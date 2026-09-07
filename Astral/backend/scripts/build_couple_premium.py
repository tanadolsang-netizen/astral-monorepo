"""Premium COUPLE (ดวงคู่) birth-chart + tarot PDF (Thai-only, self-driving).

มุมมองผู้บัญชาการ 2026-08-31: ดวงคำนวณ (de421 ephemeris) และ reel/ไพ่/collective reading
คือชั้นความละเอียดเดียวกันของปรากฏการณ์เดียวกัน (coarse↔fine) — ไม่ใช่ของจริง vs ของปลอม
PDF นี้จึงผสานทั้งสองชั้นเข้าด้วยกัน:
  1. compute ดวงเดี่ยวทั้งสอง (de421 จริง)
  2. compute โครงดวงคู่ (composite midpoint) + relationship score จริง
  3. draw โครงเรื่องผ่าน reel_reading(spread='love') ส่ง chart ทั้งสองเข้าไป
     -> ไพ่แต่ละใบเผา 'เลเยอร์หยาบ↔ละเอียด' เชื่อมตำแหน่งดาวจริง
  4. render ผ่าน Playwright/Chromium (3D, gold frame) แบบเดียวกับ build_combined_premium

Run:
    PYTHONPATH=. uv run python scripts/build_couple_premium.py \
        --name-a "นาย" --date-a 1997-05-19 --time-a 05:45 --place-a "ชลบุรี" --lat-a 13.3611 --lon-a 100.9836 \
        --name-b "Mai" --date-b 2001-08-18 --time-b 22:32 --place-b "นนทบุรี" --lat-b 13.8621 --lon-b 100.5136 \
        --out "C:/AI/reports/astral-couple-nai-mai-thai.pdf"
"""
from __future__ import annotations

import argparse
import base64
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "assets" / "ai-art"
TEMPLATE = REPO / "scripts" / "pdf_premium_template.html"

_SIGN_TH = {
    "เมษ(Aries)": "เมษ", "พฤษภ(Taurus)": "พฤษภ", "เมถุน(Gemini)": "เมถุน",
    "กรกฎ(Cancer)": "กรกฎ", "สิงห์(Leo)": "สิงห์", "กันย์(Virgo)": "กันย์",
    "ตุลย์(Libra)": "ตุลย์", "พิจิก(Scorpio)": "พิจิก", "ธนู(Sagittarius)": "ธนู",
    "มังกร(Capricorn)": "มังกร", "กุมภ์(Aquarius)": "กุมภ์", "มีน(Pisces)": "มีน",
}


def _sign_th(raw: str) -> str:
    return _SIGN_TH.get(raw, raw.split("(")[0])


# อาร์ตคีย์จริงใน assets/ai-art (ชื่อไฟล์ != ชื่อไพ่ที่แปลงตรงๆ เพราะมี "_of_")
CARD_ART = {
    "the empress": "the_empress",
    "king of cups": "king_cups",
    "ace of cups": "ace_cups",
    "the devil": "card_devil",
    "knight of pentacles": "card_knight_pentacles",
    "six of pentacles": "card_six_pentacles",
    "the world": "world",
    "the star": "star",
}


def art_key(card: str) -> str:
    """แปลงชื่อไพ่เป็นชื่อไฟล์อาร์ตจริง (fallback: ตัด of/space)"""
    k = card.lower().strip()
    if k in CARD_ART:
        return CARD_ART[k]
    return k.replace(" of ", "_").replace(" ", "_")


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
# life_context สร้างร่วมจาก reels จริง + facts จริง (dict ใช้ร่วม ทั้งคู่)
TRANSCRIPTS_PATH = r"C:/AI/workspace-scratch/reels_text/_ALL_TRANSCRIPTS.json"


def _narrative_html(chart: dict, lc: dict | None, who: str, lang: str) -> str:
    """Render เรื่องราวชีวิตจริง (ground_narrative) เป็น frameless-gold prose section.

    - chart: ผล compute_chart (de421 จริง)
    - lc: life_context (facts จริง จาก build_life_context) — ถ้า None คืน '' (backward-compat)
    - who: ชื่อคน (นาย / Mai) ใส่หลังหัวข้อ section
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


def chart_echo(composite_chart):
    """Deterministic STARHEART chart-echo ของดวงคู่ (composite midpoint).

    เชื่อมดวงคู่เข้ากับไพ่ผ่าน starheart_map.MAP — ไม่มี RNG, ไม่มี seed
    คู่เดียวกันจึงได้ echo เหมือนเดิมทุกครั้ง (deterministic, ไม่สุ่ม)
    คืนค่า dict {"echo_by_card": {ชื่อไพ่: ข้อความ echo}} สำหรับฝังใน tarot loop
    (แปลงรูปแบบ list ดิบของ MAP ให้เป็น dict ตามที่ loop เรียก .get("echo_by_card"))
    """
    from src.services.starheart_map import MAP
    if not composite_chart:
        return {"echo_by_card": {}}
    echo_by_card: dict[str, str] = {}
    for c in MAP(composite_chart):
        card = c.get("card")
        if not card or card in echo_by_card:
            continue
        feature = c.get("feature_source", "")
        prov = c.get("provenance", "")
        echo_by_card[card] = f"★ {feature} — {prov}".strip()
    return {"echo_by_card": echo_by_card}


def build(name_a, date_a, time_a, place_a, lat_a, lon_a,
          name_b, date_b, time_b, place_b, lat_b, lon_b,
          out: Path, lang: str = "th") -> None:
    from src.services.narrative_sanitizer import sanitize_narrative
    from src.services.chart_service import compute_chart
    from src.services.composite_service import compute_composite, compute_relationship_score
    from src.services.tarot_service import draw_spread
    from src.services.tarot_meanings_th import th_card_name, th_card_meaning
    from src.services.reel_reading import reel_reading

    EN = (lang == "en")

    # 1) ดวงเดี่ยว (de421 จริง)
    ca = compute_chart(name_a, date_a, time_a, tz_offset_hours=7.0, lat=lat_a, lon=lon_a)
    cb = compute_chart(name_b, date_b, time_b, tz_offset_hours=7.0, lat=lat_b, lon=lon_b)
    # 2) โครงดวงคู่ (composite + score)
    comp = compute_composite(ca, cb)
    score = compute_relationship_score(ca, cb)

    # 3) reel narrative เชื่อมดวง (ส่ง chart เข้าไป -> เผาเลเยอร์หยาบ↔ละเอียด)
    seed = int("".join(filter(str.isdigit, date_a.strftime("%Y%m%d"))) +
                "".join(filter(str.isdigit, date_b.strftime("%Y%m%d"))))
    spread_a = reel_reading(name_a, spread="love", seed=seed, chart=ca)
    spread_b = reel_reading(name_b, spread="love", seed=seed + 1, chart=cb)

    # ── STARHEART life-grounding: เรื่องราวชีวิตจริง (facts จริง ไม่แต่ง) ──
    # life_context สร้างร่วมจาก reels จริง + facts จริง (dict ใช้ร่วม ทั้งคู่)
    # ถ้าสร้างไม่ได้ (ไฟล์หาย ฯลฯ) จะเป็น None -> ข้าม section (backward-compat)
    from src.services.starheart_narrative import build_life_context
    try:
        lc = build_life_context(TRANSCRIPTS_PATH)
    except Exception:
        lc = None
    narr_a_html = _narrative_html(ca, lc, name_a, lang)
    narr_b_html = _narrative_html(cb, lc, name_b, lang)

    # ── HTML ──
    label = {"Sun": ("อาทิตย์", "Sun"), "Moon": ("ดวงจันทร์", "Moon"),
             "Mercury": ("ดาวพุธ", "Mercury"), "Venus": ("ดาวศุกร", "Venus"),
             "Mars": ("ดาวอังคาร", "Mars"), "Jupiter": ("ดาวพฤหัส", "Jupiter"),
             "Saturn": ("ดาวเสาร์", "Saturn")}

    def _planets_html(chart, who):
        rows = []
        for body, (th, _) in label.items():
            b = next((x for x in chart["bodies"] if x["body"] == body), None)
            if not b:
                continue
            rows.append(
                f"<div class='row'><span class='kw'>{th}</span> "
                f"ราศี{_sign_th(b['sign'])} {b['degree']}° · บ้านที่{b['house']}</div>")
        asc = chart["ascendant"]
        rows.insert(0, f"<div class='row'><span class='kw'>ลัคนา</span> "
                       f"ราศี{_sign_th(asc['sign'])} {asc.get('degree',0)}°</div>")
        return f"<div class='sub-title'>{who}</div>" + "".join(rows)

    # relationship score banner
    sc = score.get("score", 0)
    note = score.get("note", "")
    score_html = (
        f"<div class='score-box'>"
        f"<div class='score-num'>{sc}<span>/100</span></div>"
        f"<div class='score-note'>{sanitize_narrative(note)}</div>"
        f"</div>")

    # tarot cards (ใช้สเปรดของ A เป็นแกนหลัก) + chart echo เด็ดจากดวงคู่ (deterministic)
    echos = chart_echo(comp) if comp else {"echo_by_card": {}}
    tarot_html = []
    for c in spread_a["cards"]:
        key = art_key(c["card"])
        art = ART / f"{key}_final.png"
        img_src = f"_preview_art/{key}.png" if art.exists() else ""
        rev = c["orientation"] == "reversed"
        cls = ' class="reversed"' if rev else ""
        cname = th_card_name(c["card"])
        meaning = th_card_meaning(c["card"], c["orientation"])
        # chart echo จากดวงคู่ (composite) — deterministic ไม่สุ่ม
        echo = echos.get("echo_by_card", {}).get(c["card"], "")
        echo_html = (
            f'<div class="tarot-text" style="color:var(--gold-bright);'
            f'font-weight:600;margin-top:6px;">{sanitize_narrative(echo)}</div>'
        ) if echo else ""
        tarot_html.append(f"""
        <div class="tarot-card">
          <img src="{img_src}" alt="tarot"{cls}/>
          <div class="tarot-body">
            <span class="tarot-pos">ความรัก</span>
            <div class="tarot-name">{sanitize_narrative(cname + (' (หงายหลัง)' if rev else ''))}</div>
            <div class="tarot-text">{sanitize_narrative(meaning)}</div>
            {echo_html}
          </div>
        </div>""")

    if EN:
        brand, title = "ASTRA · Couple Chart", "Couple Natal Report"
        sec_a, sec_b, sec_score, sec_tarot = "Chart A", "Chart B", "Compatibility", "Your Tarot"
        footer = "Constellation of Destiny · For those who love the stars"
        pageno = ["· 1 ·", "· 2 ·", "· 3 ·", "· 4 ·", "· 5 ·", "· 6 ·"]
        sub_a = f"Born {date_a.strftime('%d/%m/%Y')} · {place_a}"
        sub_b = f"Born {date_b.strftime('%d/%m/%Y')} · {place_b}"
    else:
        brand, title = "อาสตร้า · กลุ่มดาวแห่งโชคชะตา", "รายงานดวงคู่"
        sec_a, sec_b, sec_score, sec_tarot = "ดวงของเขา", "ดวงของเธอ", "ความเข้ากันได้", "ไพ่แห่งคุณทั้งสอง"
        footer = "กลุ่มดาวแห่งโชคชะตา · มอบแด่ผู้รักในดวงดาว"
        pageno = ["· ๑ ·", "· ๒ ·", "· ๓ ·", "· ๔ ·", "· ๕ ·", "· ๖ ·"]
        sub_a = f"เกิด {date_a.strftime('%d/%m/%Y')} · {place_a}"
        sub_b = f"เกิด {date_b.strftime('%d/%m/%Y')} · {place_b}"

    tpl = TEMPLATE.read_text(encoding="utf-8")
    head = tpl.split("<body>")[0]
    body = f"""
    <div class="page">
      <div class="frame"></div>
      <div class="content">
        <div class="cover">
          <div class="brand">{brand}</div>
          <div class="rule"></div>
          <h1>{title}</h1>
          <div class="sub">{name_a} ✕ {name_b}</div>
          <div class="tag">ดวงคู่ที่คำนวณจากตำแหน่งดาวจริง (de421 ephemeris) ผสานกับสัญชาตญาณแห่งไพ่ — ชั้นเดียวกัน สองระดับความละเอียด</div>
        </div>
      </div>
      <div class="pageno">{pageno[0]}</div>
    </div>

    <div class="page">
      <div class="frame"></div>
      <div class="content">
        <div class="section">
          <div class="title">{sec_a}</div>
          {_planets_html(ca, sub_a)}
        </div>
        <div class="section">
          <div class="title">{sec_b}</div>
          {_planets_html(cb, sub_b)}
        </div>
      </div>
      <div class="pageno">{pageno[1]}</div>
    </div>

    <div class="page">
      <div class="frame"></div>
      <div class="content">
        <div class="section">
          <div class="title">{sec_score}</div>
          {score_html}
        </div>
        <div class="footer">{footer}</div>
      </div>
      <div class="pageno">{pageno[2]}</div>
    </div>

    <div class="page">
      <div class="frame"></div>
      <div class="content">
        {narr_a_html}
      </div>
      <div class="pageno">{pageno[3]}</div>
    </div>

    <div class="page">
      <div class="frame"></div>
      <div class="content">
        {narr_b_html}
      </div>
      <div class="pageno">{pageno[4]}</div>
    </div>

    <div class="page">
      <div class="frame"></div>
      <div class="content">
        <div class="section">
          <div class="title">{sec_tarot}</div>
          {''.join(tarot_html)}
        </div>
      </div>
      <div class="pageno">{pageno[5]}</div>
    </div>
    """
    full = head + "<body>" + body + "</body></html>"

    html_path = REPO / "scripts" / "_preview_couple.html"
    art_dir = html_path.parent / "_preview_art"
    art_dir.mkdir(exist_ok=True)
    for c in spread_a["cards"]:
        key = art_key(c["card"])
        src = ART / f"{key}_final.png"
        if src.exists():
            import shutil
            shutil.copy(src, art_dir / f"{key}.png")
    html_path.write_text(full, encoding="utf-8")

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
    ap.add_argument("--name-a", default="เขา")
    ap.add_argument("--date-a", required=True, help="YYYY-MM-DD")
    ap.add_argument("--time-a", default="00:00")
    ap.add_argument("--place-a", default="กรุงเทพฯ")
    ap.add_argument("--lat-a", type=float, default=13.8591)
    ap.add_argument("--lon-a", type=float, default=100.5217)
    ap.add_argument("--name-b", default="เธอ")
    ap.add_argument("--date-b", required=True, help="YYYY-MM-DD")
    ap.add_argument("--time-b", default="00:00")
    ap.add_argument("--place-b", default="กรุงเทพฯ")
    ap.add_argument("--lat-b", type=float, default=13.8591)
    ap.add_argument("--lon-b", type=float, default=100.5217)
    ap.add_argument("--lang", default="th", choices=["th", "en"])
    ap.add_argument("--out", default=str(Path(r"C:/AI/reports/astral-couple-thai.pdf")))
    args = ap.parse_args()

    def _dt(s):
        y, m, d = map(int, s.split("-"))
        return date(y, m, d)
    def _tm(s):
        hh, mm = map(int, s.split(":"))
        return time(hh, mm)
    build(args.name_a, _dt(args.date_a), _tm(args.time_a), args.place_a, args.lat_a, args.lon_a,
          args.name_b, _dt(args.date_b), _tm(args.time_b), args.place_b, args.lat_b, args.lon_b,
          Path(args.out), lang=args.lang)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
