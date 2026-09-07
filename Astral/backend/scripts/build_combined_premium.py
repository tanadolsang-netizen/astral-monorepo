"""Premium combined birth-chart + tarot PDF (Thai-only, self-driving).

Generates a 100% Thai, premium 3D-style PDF for ANY birth data:
  1. compute the real natal chart (ephemeris de421.bsp)
  2. derive personality + planetary-position narrative from the chart
  3. draw a deterministic 3-card tarot spread seeded by the birth date
  4. ensure AI art exists for each drawn card (draw missing ones via ComfyUI)
  5. render via Playwright/Chromium (full browser engine -> real 3D, gold frames)

Run:
    PYTHONPATH=. uv run python scripts/build_combined_premium.py \
        --name "นาย" --date 1997-05-19 --time 05:45 --place "ชลบุรี" \
        --lat 13.3611 --lon 100.9836 --out "C:/AI/reports/astral-natal-nai-thai.pdf"

If --date/--time are omitted it falls back to the demo chart (04041996).
"""
from __future__ import annotations

import argparse
import base64
import subprocess
import sys
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "assets" / "ai-art"
TEMPLATE = REPO / "scripts" / "pdf_premium_template.html"

# Thai sign names
_SIGN_TH = {
    "เมษ(Aries)": "เมษ", "พฤษภ(Taurus)": "พฤษภ", "เมถุน(Gemini)": "เมถุน",
    "กรกฎ(Cancer)": "กรกฎ", "สิงห์(Leo)": "สิงห์", "กันย์(Virgo)": "กันย์",
    "ตุลย์(Libra)": "ตุลย์", "พิจิก(Scorpio)": "พิจิก", "ธนู(Sagittarius)": "ธนู",
    "มังกร(Capricorn)": "มังกร", "กุมภ์(Aquarius)": "กุมภ์", "มีน(Pisces)": "มีน",
}


def _sign_th(raw: str) -> str:
    return _SIGN_TH.get(raw, raw.split("(")[0])


# Card -> art key (must match assets/ai-art/<key>_final.png)
def _art_key(card_name: str) -> str:
    return {
        "The Devil": "devil", "Six of Pentacles": "six",
        "Knight of Pentacles": "knight", "The World": "world",
        "The Star": "star",
    }.get(card_name, card_name.lower().replace(" ", "_").replace(" of ", "_"))


def b64(p: Path, max_kb: int = 1600) -> str:
    data = p.read_bytes()
    if len(data) > max_kb * 1024:
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(data)).convert("RGB")
            img.thumbnail((900, 1300))
            buf = io.BytesIO()
            img.save(buf, format="PNG", optimize=True)
            data = buf.getvalue()
        except Exception:
            pass
    return "data:image/png;base64," + base64.b64encode(data).decode()


def kw(text: str) -> str:
    _KW = ["อาทิตย์", "ดวงจันทร์", "ดาวพุธ", "ดาวศุกร", "ดาวอังคาร", "ดาวพฤหัส",
           "ดาวเสาร์", "ลัคนา", "ราศีเมษ", "ราศีตุลย์", "ราศีกรกฎ", "ราศีพฤษภ",
           "เมษ", "ตุลย์", "กรกฎ", "พฤษภ", "บ้านที่"]
    for k in _KW:
        if k in text:
            text = text.replace(k, f'<span class="kw">{k}</span>')
    return text


# STARHEART life-grounding: เรื่องราวชีวิตจริง (จาก starheart_narrative.ground_narrative)
# life_context สร้างร่วมจาก reels จริง + facts จริง
TRANSCRIPTS_PATH = r"C:/AI/workspace-scratch/reels_text/_ALL_TRANSCRIPTS.json"


def _narrative_html(chart: dict, lc: dict | None, who: str, lang: str) -> str:
    """Render เรื่องราวชีวิตจริง (ground_narrative) เป็น frameless-gold prose section.

    - chart: ผล compute_chart (de421 จริง)
    - lc: life_context (facts จริง จาก build_life_context) — ถ้า None คืน '' (backward-compat)
    - who: ชื่อคน ใส่หลังหัวข้อ section
    - lang: 'th' | 'en'
    ไม่แต่งเรื่องใหม่: ข้อความทั้งหมดมาจาก ground_narrative (facts จริง + MAP)
    """
    if lc is None:
        return ""
    from src.services.starheart_narrative import ground_narrative
    from src.services.narrative_sanitizer import sanitize_narrative
    text = ground_narrative(chart, lc, lang=lang)
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    body = "".join(f"<p>{kw(sanitize_narrative(p))}</p>" for p in paras)
    if lang == "en":
        title = "Your Real-Life Story"
    else:
        title = "เรื่องราวชีวิตจริง"
    who_label = f" · {who}" if who else ""
    return (
        f'<div class="life-narrative">'
        f'<div class="title">{title}{who_label}</div>'
        f'{body}'
        f'</div>'
    )


def ensure_art(cards: list[dict]) -> None:
    """Generate missing AI art for drawn cards via ComfyUI if not present."""
    from src.services.tarot_meanings_th import th_card_name
    needed = {}
    for c in cards:
        key = _art_key(c["card"])
        if not (ART / f"{key}_final.png").exists():
            needed[key] = c["card"]
    if not needed:
        return
    print(f"[art] missing {len(needed)} image(s): {', '.join(needed)} -> drawing...")
    # build prompt per card from comfy_prompts mapping (majors only; reuse devil-style)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "cp", REPO / "scripts" / "comfy_prompts.py")
    cp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cp)
    argv = ["scripts/gen_ai_art.py"]
    seed = 19970519
    for key, card in needed.items():
        pr = getattr(cp, f"PROMPT_{key.upper()}", None)
        ng = getattr(cp, f"NEG_{key.upper()}", None)
        if not pr:
            continue
        argv += ["--key", key, "--prompt", pr, "--neg", ng]
    if len(argv) <= 1:
        return
    try:
        subprocess.run([sys.executable, *argv], cwd=str(REPO),
                       env={**__import__("os").environ, "PYTHONPATH": "."},
                       check=True)
    except Exception as e:
        print(f"[art] warn: could not draw art: {e}")


def build(name: str, birth_date: date, birth_time: time, place: str,
          lat: float, lon: float, out: Path, lang: str = "th") -> None:
    from src.services.narrative_sanitizer import sanitize_narrative
    from src.services.chart_service import compute_chart
    from src.services.tarot_service import draw_spread
    from src.services.tarot_meanings_th import th_card_name, th_card_meaning
    from src.services.tarot_meanings_en import TAROT_MEANINGS_EN
    from src.services.reel_reading import reel_reading

    EN = (lang == "en")

    # 1) chart
    chart = compute_chart(name, birth_date, birth_time,
                          tz_offset_hours=7.0, lat=lat, lon=lon)
    asc = chart["ascendant"]
    asc_sign = _sign_th(asc["sign"])
    bodies = {b["body"]: b for b in chart["bodies"]}
    sun = bodies.get("Sun")
    moon = bodies.get("Moon")

    # bilingual labels
    label = {
        "Sun": ("อาทิตย์", "Sun"), "Moon": ("ดวงจันทร์", "Moon"),
        "Mercury": ("ดาวพุธ", "Mercury"), "Venus": ("ดาวศุกร", "Venus"),
        "Mars": ("ดาวอังคาร", "Mars"), "Jupiter": ("ดาวพฤหัส", "Jupiter"),
        "Saturn": ("ดาวเสาร์", "Saturn"),
    }
    pos_th = {1: "อดีต", 2: "ปัจจุบัน", 3: "อนาคต"}
    pos_en = {1: "Past", 2: "Present", 3: "Future"}

    # 2) full bilingual chart narrative (deep, precise, long, merged)
    from src.services.chart_narrative_full import chart_narrative
    chart_prose = chart_narrative(name, chart, lang=lang)
    # split merged prose into real paragraphs (block separated by blank lines)
    _paras = [p.strip() for p in chart_prose.split("\n\n") if p.strip()]
    personality_html = "".join(
        f"<p>{kw(sanitize_narrative(p))}</p>" for p in _paras)
    positions_html = ""  # merged into the single prose block above

    # 3) tarot (deterministic seed from birth date) — bilingual via reel_reading
    seed = int("".join(filter(str.isdigit, birth_date.strftime("%Y%m%d"))))
    spread = reel_reading(name, seed=seed, spread="three_card")
    cards = spread["cards"]

    # ── STARHEART life-grounding: เรื่องราวชีวิตจริง (facts จริง ไม่แต่ง) ──
    from src.services.starheart_narrative import build_life_context
    try:
        lc = build_life_context(TRANSCRIPTS_PATH)
    except Exception:
        lc = None
    narr_html = _narrative_html(chart, lc, name, lang)

    ensure_art(cards)

    tarot_html = []
    for c in cards:
        key = _art_key(c["card"])
        rev = c["orientation"] == "reversed"
        art = ART / f"{key}_final.png"
        img_src = f"_preview_art/{key}.png" if art.exists() else ""
        cls = ' class="reversed"' if rev else ""
        if EN:
            orient = "Reversed" if rev else "Upright"
            cname = c["card"]
            meaning = TAROT_MEANINGS_EN.get(c["card"], {}).get(
                "reversed" if rev else "upright", "")
            pos_label = pos_en.get(int(c["position"]), c["position"])
        else:
            orient = "หงายหลัง" if rev else "ตั้งตรง"
            cname = th_card_name(c["card"])
            meaning = th_card_meaning(c["card"], c["orientation"])
            pos_label = pos_th.get(int(c["position"]), c["position"])
        tarot_html.append(f"""
        <div class="tarot-card">
          <img src="{img_src}" alt="tarot"{cls}/>
          <div class="tarot-body">
            <span class="tarot-pos">{pos_label}</span>
            <div class="tarot-name">{sanitize_narrative(cname + (f' ({orient})' if rev else ''))}</div>
            <div class="tarot-text">{sanitize_narrative(meaning)}</div>
          </div>
        </div>""")

    date_str = birth_date.strftime("%d/%m/%Y")
    # 4) assemble HTML (bilingual cover/titles)
    if EN:
        brand = "ASTRA · Constellation of Destiny"
        title = "Natal Chart Report"
        tag = "Deep dive into personality and planetary positions, woven with a tarot spread of past, present, and future"
        sec_personality = "Your Natal Chart"
        sec_tarot = "Your Tarot Cards"
        footer = "Constellation of Destiny · For those who love the stars"
        pageno = ["· 1 ·", "· 2 ·", "· 3 ·", "· 4 ·"]
        sub_line = f"Born {date_str} · {place}"
    else:
        brand = "อาสตร้า · กลุ่มดาวแห่งโชคชะตา"
        title = "รายงานดวงชะตา"
        tag = "เจาะลึกบุคลิกภาพและตำแหน่งดาว ผสานไพ่ทาโรต์แห่งอดีต ปัจจุบัน และอนาคต"
        sec_personality = "ดวงชะตาของคุณ"
        sec_tarot = "ไพ่ทาโรต์แห่งคุณ"
        footer = "กลุ่มดาวแห่งโชคชะตา · มอบแด่ผู้รักในดวงดาว"
        pageno = ["· ๑ ·", "· ๒ ·", "· ๓ ·", "· ๔ ·"]
        sub_line = f"เกิด {date_str} · {place}"
    tpl = TEMPLATE.read_text(encoding="utf-8")
    head = tpl.split("<body>")[0]
    cover_img = ART / "cover_helios.png"
    cover_src = "_preview_art/cover.png" if cover_img.exists() else ""
    body = f"""
    <div class="page">
      <div class="frame"></div>
      <div class="content">
        <div class="cover">
          <div class="brand">{brand}</div>
          <div class="rule"></div>
          <h1>{title}</h1>
          <div class="sub">{sub_line}</div>
          <div class="tag">{tag}</div>
          <img class="hero" src="{cover_src}" alt="cover art"/>
        </div>
      </div>
      <div class="pageno">{pageno[0]}</div>
    </div>

    <div class="page">
      <div class="frame"></div>
      <div class="content">
        <div class="section">
          <div class="title">{sec_personality}</div>
          {personality_html}
          {positions_html}
        </div>
      </div>
      <div class="pageno">{pageno[1]}</div>
    </div>

    <div class="page">
      <div class="frame"></div>
      <div class="content">
        {narr_html}
      </div>
      <div class="pageno">{pageno[2]}</div>
    </div>

    <div class="page">
      <div class="frame"></div>
      <div class="content">
        <div class="section">
          <div class="title">{sec_tarot}</div>
          {''.join(tarot_html)}
        </div>
        <div class="footer">{footer}</div>
      </div>
      <div class="pageno">{pageno[3]}</div>
    </div>
    """
    full = head + "<body>" + body + "</body></html>"

    html_path = REPO / "scripts" / "_preview_premium.html"
    art_dir = html_path.parent / "_preview_art"
    art_dir.mkdir(exist_ok=True)
    if cover_img.exists():
        import shutil
        shutil.copy(cover_img, art_dir / "cover.png")
    for c in cards:
        key = _art_key(c["card"])
        src = ART / f"{key}_final.png"
        if src.exists():
            import shutil
            shutil.copy(src, art_dir / f"{key}.png")
    html_path.write_text(full, encoding="utf-8")

    # 5) render with Chromium
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.as_uri(), wait_until="load")
        page.wait_for_timeout(3000)
        page.pdf(path=str(out), format="A4", print_background=True,
                 margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        browser.close()
    print(f"WROTE {out} ({out.stat().st_size} bytes)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="ผู้รักในดวงดาว")
    ap.add_argument("--date", default=None, help="YYYY-MM-DD")
    ap.add_argument("--time", default="05:45", help="HH:MM")
    ap.add_argument("--place", default="กรุงเทพฯ")
    ap.add_argument("--lat", type=float, default=13.8591)
    ap.add_argument("--lon", type=float, default=100.5217)
    ap.add_argument("--lang", default="th", choices=["th", "en"])
    ap.add_argument("--out", default=str(Path(r"C:/AI/reports/astral-natal-thai.pdf")))
    args = ap.parse_args()

    if args.date:
        y, m, d = map(int, args.date.split("-"))
        bd = date(y, m, d)
        hh, mm = map(int, args.time.split(":"))
        bt = time(hh, mm)
    else:
        bd = date(1996, 4, 4)
        bt = time(0, 0)
    build(args.name, bd, bt, args.place, args.lat, args.lon,
          Path(args.out), lang=args.lang)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
