"""Premium astrology PDF v2 — Regency × Victorian with Greek mythology art.

Layout fixes over v1:
- Single hairline frame (no double outline stacking)
- No fixed-position elements colliding with content
- Cover art plate (Met Museum CC0 painting) in a gilded frame
- Clean section cards without inset box-shadow stacking
- Footer inline at document end (not fixed overlay)
Art: Titian / Batoni / Canova from The Met Open Access (public domain).
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import datetime

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT_DIR = os.path.join(_REPO, "assets", "fonts")
ART_DIR = os.path.join(_REPO, "assets", "art")

_ZODIAC = [
    ("Aries", "เมษ", "♈"), ("Taurus", "พฤษภ", "♉"), ("Gemini", "เมถุน", "♊"),
    ("Cancer", "กรกฎ", "♋"), ("Leo", "สิงห์", "♌"), ("Virgo", "กันย์", "♍"),
    ("Libra", "ตุลย์", "♎"), ("Scorpio", "พิจิก", "♏"), ("Sagittarius", "ธนู", "♐"),
    ("Capricorn", "มกร", "♑"), ("Aquarius", "กุมภ์", "♒"), ("Pisces", "มีน", "♓"),
]

_GOLD = "#9a7b34"
_GOLD_SOFT = "rgba(154,123,52,.40)"
_INK = "#3b3324"
_IVORY = "#f6f0e2"


def _data_uri(path: str) -> str:
    with open(path, "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()


_SEARCH_TERMS = {
    # zodiac / planet -> museum query (falls back gracefully)
    "venus": ["Venus goddess painting"], "taurus": ["Venus goddess painting"],
    "libra": ["Venus goddess painting"],
    "mars": ["Mars god war painting"], "aries": ["Mars god war painting"],
    "scorpio": ["Venus goddess painting"],
    "moon": ["Diana moon goddess"], "cancer": ["Diana moon goddess"],
    "sun": ["Apollo sun god painting"], "leo": ["Apollo sun god painting"],
    "mercury": ["Mercury Hermes painting"], "gemini": ["Mercury Hermes painting"],
    "jupiter": ["Jupiter Zeus painting"], "sagittarius": ["Jupiter Zeus painting"],
    "saturn": ["Saturn Cronus painting"], "capricorn": ["Saturn Cronus painting"],
    "uranus": ["Aurora dawn goddess"], "aquarius": ["Ganymede Zeus eagle"],
    "neptune": ["Neptune Poseidon painting"], "pisces": ["Cupid Psyche myth"],
}


def _met_search(query: str) -> tuple[str, str] | None:
    """Live search The Met Open Access; returns (local_path, caption) or None."""
    try:
        import urllib.request, urllib.parse
        s = json.load(urllib.request.urlopen(urllib.request.Request(
            f"https://collectionapi.metmuseum.org/public/collection/v1/search?"
            f"q={urllib.parse.quote(query)}&hasImages=true",
            headers={"User-Agent": "Mozilla/5.0"}), timeout=20))
        for oid in (s.get("objectIDs") or [])[:10]:
            try:
                o = json.load(urllib.request.urlopen(urllib.request.Request(
                    f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}",
                    headers={"User-Agent": "Mozilla/5.0"}), timeout=20))
            except Exception:
                continue
            if not o.get("isPublicDomain") or not o.get("primaryImage"):
                continue
            title = (o.get("title") or "")
            if query.split()[0].lower() not in title.lower():
                continue
            data = urllib.request.urlopen(urllib.request.Request(
                o["primaryImage"], headers={"User-Agent": "Mozilla/5.0"}),
                timeout=90).read()
            slug = query.lower().replace(" ", "-")[:24]
            path = os.path.join(ART_DIR, f"{slug}.jpg")
            with open(path, "wb") as f:
                f.write(data)
            artist = o.get("artistDisplayName") or "Unknown"
            return path, f"{title} — {artist}"
    except Exception:
        return None
    return None


def _pick_cover_art(theme_hint: str = "") -> tuple[str, str] | None:
    """Choose bundled art by hint; else search the Met live; else any bundle."""
    hint = theme_hint.lower()
    # 1) try exact bundled matches first
    mapping = {
        "venus": "venus_mars", "taurus": "venus_mars", "libra": "venus_mars",
        "psyche": "cupid_psyche", "cupid": "cupid_psyche", "pisces": "cupid_psyche",
        "diana": "diana", "moon": "diana", "cancer": "diana",
        "mars": "venus_mars", "aries": "venus_mars",
    }
    key = None
    for k, v in mapping.items():
        if k in hint:
            key = v
            break
    available = _available_art()
    if key and key in available:
        path = os.path.join(ART_DIR, f"{key}.jpg")
        captions = {
            "venus_mars": "Venus and the Lute Player — Titian",
            "diana": "Diana and Cupid — Pompeo Batoni",
            "cupid_psyche": "Cupid and Psyche — Antonio Canova",
        }
        return _data_uri(path), captions[key]

    # 2) live Met search keyed off planet/zodiac terms in the hint
    for term_key, queries in _SEARCH_TERMS.items():
        if term_key in hint:
            for q in queries:
                got = _met_search(q)
                if got:
                    return _data_uri(got[0]), got[1]

    # 3) any bundled art
    if available:
        path = os.path.join(ART_DIR, f"{available[0]}.jpg")
        return _data_uri(path), "The Metropolitan Museum of Art · Open Access"
    return None
    captions = {
        "venus_mars": "Venus and the Lute Player — Titian",
        "diana": "Diana and Cupid — Pompeo Batoni",
        "cupid_psyche": "Cupid and Psyche — Antonio Canova",
    }
    return _data_uri(path), captions.get(key, "The Metropolitan Museum of Art")


def _available_art() -> list[str]:
    if not os.path.isdir(ART_DIR):
        return []
    return [f[:-4] for f in os.listdir(ART_DIR)
            if f.endswith(".jpg") and f[:-4] != "met-picks"]


def _wheel_svg() -> str:
    import math
    spokes = []
    for i in range(12):
        a0 = i * 30 - 90
        a1 = a0 + 30
        x0, y0 = 100 + 92 * math.cos(math.radians(a0)), 100 + 92 * math.sin(math.radians(a0))
        x1, y1 = 100 + 92 * math.cos(math.radians(a1)), 100 + 92 * math.sin(math.radians(a1))
        xi, yi = 100 + 58 * math.cos(math.radians(a0 + 15)), 100 + 58 * math.sin(math.radians(a0 + 15))
        sym = _ZODIAC[i][2]
        spokes.append(
            f'<path d="M100,100 L{x0:.1f},{y0:.1f} A92,92 0 0,1 {x1:.1f},{y1:.1f} Z" '
            f'fill="rgba(154,123,52,{0.03 + (i % 2) * 0.02})" stroke="{_GOLD_SOFT}" stroke-width=".55"/>'
            f'<text x="{xi:.1f}" y="{yi:.1f}" font-size="12.5" fill="{_GOLD}" '
            f'text-anchor="middle" dominant-baseline="central">{sym}</text>'
        )
    return (
        '<svg viewBox="0 0 200 200" class="wheel">'
        f'<circle cx="100" cy="100" r="97" fill="none" stroke="{_GOLD}" stroke-width="1"/>'
        f'<circle cx="100" cy="100" r="58" fill="#fbf7ec" stroke="{_GOLD}" stroke-width=".7"/>'
        + "".join(spokes) +
        '<text x="100" y="96" text-anchor="middle" fill="#9a7b34" font-size="8.5" letter-spacing="3">ASTRAL</text>'
        '<text x="100" y="108" text-anchor="middle" fill="#8a774e" font-size="5" letter-spacing="1.5">COSMIC REPORT</text>'
        "</svg>"
    )




def _constellation_svg(name: str, points: list[tuple[float, float]],
                       links: list[tuple[int, int]], w: int = 160) -> str:
    """Draw a named constellation as connected gold stars."""
    scale = w / 100.0
    pts = [(x * scale * 0.62 + 12, y * scale * 0.62 + 10) for x, y in points]
    lines = "".join(
        f'<line x1="{pts[a][0]:.1f}" y1="{pts[a][1]:.1f}" x2="{pts[b][0]:.1f}" y2="{pts[b][1]:.1f}" '
        f'stroke="rgba(154,123,52,.55)" stroke-width=".8"/>'
        for a, b in links if a < len(pts) and b < len(pts)
    )
    stars = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{2.2 - i*0.08:.2f}" fill="#9a7b34"/>'
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{4.5 - i*0.15:.2f}" fill="rgba(201,168,76,.25)"/>'
        for i, (x, y) in enumerate(pts)
    )
    label = (
        f'<text x="{w*0.62/2+12:.0f}" y="{max(y for _, y in pts)+14:.0f}" text-anchor="middle" '
        f'font-size="7.5" letter-spacing="2.5" fill="#8a774e" font-style="italic">{name}</text>'
    )
    return (f'<svg viewBox="0 0 {w*0.75+24:.0f} {max(y for _, y in pts)*scale+28:.0f}" class="constellation">'
            + lines + stars + label + "</svg>")


def _constellations_row() -> str:
    """Three famous love/myth constellations side by side."""
    orion = _constellation_svg("ORION", [
        (50, 8), (44, 30), (56, 32), (40, 52), (60, 54), (46, 78), (64, 80)],
        [(0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6), (1, 2), (3, 4)])
    lyra = _constellation_svg("LYRA", [
        (50, 15), (38, 38), (62, 36), (42, 62), (58, 60), (50, 85)],
        [(0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 5)])
    gemini = _constellation_svg("GEMINI", [
        (30, 10), (70, 14), (26, 38), (74, 40), (34, 64), (66, 66), (48, 88)],
        [(0, 2), (1, 3), (2, 4), (3, 5), (4, 6), (5, 6), (0, 6), (1, 6)])
    return ('<div class="const-row">' + orion + lyra + gemini + "</div>")


def _moon_phases() -> str:
    """Eight phases of the moon in gold line art."""
    phases = []
    n = 8
    for i in range(n):
        # simple illuminated disc progression via two overlapping circles
        illum = i / (n - 1)
        cx = 20 + i * 22
        phases.append(
            f'<g transform="translate({cx},0)">'
            f'<circle cx="9" cy="9" r="8" fill="none" stroke="#9a7b34" stroke-width=".9"/>'
            f'<path d="M9,1 A{abs(8*(1-2*illum)) if illum != .5 else 0:.1f},8 0 0,{1 if illum < .5 else 0} 9,17 '
            f'A8,8 0 0,{"0" if illum < .5 else "1"} 9,1 Z" fill="rgba(154,123,52,.45)"/>'
            f"</g>"
        )
    label = '<text x="98" y="34" text-anchor="middle" font-size="7" letter-spacing="2.5" fill="#8a774e" font-style="italic">LUNAR CYCLE</text>'
    return f'<svg viewBox="-10 -4 216 42" class="moons">{"".join(phases)}{label}</svg>'


def _stars_field(seed: int = 7) -> str:
    """Deterministic scattered stars for the page background."""
    import random
    rng = random.Random(seed)
    dots = []
    for _ in range(120):
        x, y = rng.uniform(2, 98), rng.uniform(1, 99)
        s = rng.choice([0.8, 1.0, 1.3, 1.8])
        o = rng.choice([.18, .28, .4])
        dots.append(f'<circle cx="{x:.1f}%" cy="{y:.1f}%" r="{s}" fill="rgba(154,123,52,{o})"/>')
    return f'<svg class="starfield" preserveAspectRatio="none">{"".join(dots)}</svg>'







_ASPECT_DEFS = [(0, "conj"), (60, "sextile"), (90, "square"), (120, "trine"), (180, "opp")]
_ORBS = {"conj": 8, "sextile": 5, "square": 7, "trine": 8, "opp": 8}
_ASPECT_COLOR = {"conj": "#b08d3e", "sextile": "#5e8c61", "square": "#a63b40",
                 "trine": "#5e8c61", "opp": "#a63b40"}
_PLANET_GLYPH = {"Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
                 "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "ASC": "AC"}
_SIGN_START = {"Aries": 0, "Taurus": 30, "Gemini": 60, "Cancer": 90,
               "Leo": 120, "Virgo": 150, "Libra": 180, "Scorpio": 210,
               "Sagittarius": 240, "Capricorn": 270, "Aquarius": 300, "Pisces": 330}


def _deg_to_xy(deg: float, radius: float, cx: float = 100, cy: float = 100):
    import math
    # astrological: 0° Aries at left (9 o'clock), counterclockwise
    rad = math.radians(180 - deg)
    return cx + radius * math.cos(rad), cy - radius * math.sin(rad)


def biwheel_svg(chart_a: dict, chart_b: dict,
                name_a: str = "A", name_b: str = "B") -> str:
    """Dual-ring wheel: A planets inner ring, B planets outer, aspect lines."""
    import math
    parts = [
        '<svg viewBox="0 0 200 200" class="biwheel">',
        '<circle cx="100" cy="100" r="97" fill="#fdfaf2" stroke="#9a7b34" stroke-width="1"/>',
        '<circle cx="100" cy="100" r="80" fill="none" stroke="rgba(154,123,52,.45)" stroke-width=".6"/>',
        '<circle cx="100" cy="100" r="56" fill="none" stroke="rgba(154,123,52,.45)" stroke-width=".6"/>',
        '<circle cx="100" cy="100" r="34" fill="#fffdf6" stroke="rgba(154,123,52,.3)" stroke-width=".5"/>',
    ]
    # sign ticks
    for i in range(12):
        d = i * 30
        x0, y0 = _deg_to_xy(d, 97); x1, y1 = _deg_to_xy(d, 80)
        parts.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
                     f'stroke="#9a7b34" stroke-width=".8"/>')
        mx, my = _deg_to_xy(d + 15, 88.5)
        glyph = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"][i]
        parts.append(f'<text x="{mx:.1f}" y="{my:.1f}" font-size="6.5" fill="#9a7b34" '
                     f'text-anchor="middle" dominant-baseline="central">{glyph}</text>')
    # aspect lines (center zone)
    bodies_a = {b["body"]: b["absolute_deg"] for b in chart_a.get("bodies", []) if "absolute_deg" in b}
    bodies_b = {b["body"]: b["absolute_deg"] for b in chart_b.get("bodies", []) if "absolute_deg" in b}
    for pa, da in bodies_a.items():
        for pb, db in bodies_b.items():
            diff = abs(da - db) % 360
            if diff > 180:
                diff = 360 - diff
            for target, kind in _ASPECT_DEFS:
                if abs(diff - target) <= _ORBS[kind]:
                    x0, y0 = _deg_to_xy(da, 54)
                    x1, y1 = _deg_to_xy(db, 56)
                    dash = ' stroke-dasharray="1.5,1.5"' if kind == "conj" else ""
                    parts.append(
                        f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
                        f'stroke="{_ASPECT_COLOR[kind]}" stroke-width=".55" '
                        f'opacity=".75"{dash}/>'
                    )
                    break
    # A planets inner
    for name, deg in bodies_a.items():
        x, y = _deg_to_xy(deg, 68)
        g = _PLANET_GLYPH.get(name, "•")
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.6" fill="#f6efdd" '
                     f'stroke="#9a7b34" stroke-width=".5"/>')
        parts.append(f'<text x="{x:.1f}" y="{y+.3:.1f}" font-size="5.2" fill="#5a4a28" '
                     f'text-anchor="middle" dominant-baseline="central">{g}</text>')
    # B planets outer
    for name, deg in bodies_b.items():
        x, y = _deg_to_xy(deg, 69)
        x2, y2 = _deg_to_xy(deg, 86)
        g = _PLANET_GLYPH.get(name, "•")
        parts.append(f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="4.9" fill="#fdf6e8" '
                     f'stroke="#a05252" stroke-width=".55"/>')
        parts.append(f'<text x="{x2:.1f}" y="{y2+.3:.1f}" font-size="5.4" fill="#6b3030" '
                     f'text-anchor="middle" dominant-baseline="central">{g}</text>')
    # legend
    parts.append(f'<text x="100" y="12" text-anchor="middle" font-size="5" fill="#6b3030">{name_b} ○</text>')
    parts.append(f'<text x="100" y="191" text-anchor="middle" font-size="5" fill="#5a4a28">{name_a} ●</text>')
    parts.append("</svg>")
    return "".join(parts)


def _frame_svg_uri() -> str:
    """A4-proportioned double gold frame as encoded SVG background."""
    # A4 ratio 210:297 -> viewBox scales; preserveAspectRatio=none stretches ok
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2100 2970" '
        'preserveAspectRatio="none">'
        '<rect x="18" y="18" width="2064" height="2934" fill="none" '
        f'stroke="{_GOLD}" stroke-width="2.4"/>'
        '<rect x="30" y="30" width="2040" height="2910" fill="none" '
        f'stroke="{_GOLD_SOFT}" stroke-width="1.2"/>'
        "</svg>"
    )
    import urllib.parse
    return urllib.parse.quote(svg)



def build_html(sections: list[dict], person_name: str = "", lang: str = "th",
               theme_hint: str = "", biwheel: str = "",
               section_art: dict[int, str] | None = None,
               raw_section: str = "", raw_title: str = "") -> str:
    now = datetime.datetime.now().strftime("%d/%m/%Y")
    name = person_name or ("ผู้รับการพยากรณ์" if lang == "th" else "Querent")
    t_title = "รายงานดวงชะตา" if lang == "th" else "Astrology Report"
    t_sub = ("เอกสารพยากรณ์ส่วนบุคคล · " + now) if lang == "th" else \
            ("A private reading · " + now)

    art = _pick_cover_art(theme_hint or " ".join(s["title"] for s in sections))
    art_html = ""
    art_credit = ""
    if art:
        uri, caption = art
        art_html = (
            '<div class="art-plate"><img src="' + uri + '" alt="mythology art"/>'
            '<div class="art-frame"></div></div>'
        )
        art_credit = f'<div class="credit">{caption} · The Met Open Access</div>'

    section_art = section_art or {}
    raw_block = ""
    if raw_section:
        raw_block = ('<section class="card" style="break-before:auto">'
                     '<h2><span class="num">✦</span>' + raw_title +
                     '</h2><div class="body">' + raw_section + "</div></section>")

    body_sections = []
    for idx, sec in enumerate(sections, start=1):
        lines_html = "\n".join(f"<p>{l}</p>" for l in sec.get("lines", []))
        art_html = ""
        art_path = section_art.get(idx)
        if art_path and os.path.exists(art_path):
            cap = os.path.splitext(os.path.basename(art_path))[0].replace("-", " ")
            art_html = ('<div class="card-art"><img src="' + _data_uri(art_path) +
                        '" alt=""/><div class="credit">' + cap.title() +
                        ' · The Met Open Access</div></div>')
        body_sections.append(f"""
      <section class="card">
        <h2><span class="num">{idx:02d}</span>{sec['title']}</h2>
        {art_html}
        <div class="body">{lines_html}</div>
      </section>""")

    wheel = _wheel_svg()
    constellations = _constellations_row()
    moons = _moon_phases()
    stars = _stars_field()
    frame_svg = _frame_svg_uri()
    biwheel_block = (
        '<div class="biwheel-wrap">' + biwheel + "</div>"
        if biwheel else ""
    )
    return f"""<!DOCTYPE html>
<html lang="{lang}"><head><meta charset="utf-8">
<style>
@font-face {{ font-family:'Sarabun'; src:url('file:///{FONT_DIR.replace(chr(92), '/')}/Sarabun-Regular.ttf'); font-weight:400; }}
@font-face {{ font-family:'Sarabun'; src:url('file:///{FONT_DIR.replace(chr(92), '/')}/Sarabun-Bold.ttf'); font-weight:700; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:210mm; min-height:297mm; }}
body {{
  font-family:'Sarabun',Georgia,serif; color:{_INK};
  background:{_IVORY};
}}
/* ── frame as page background: identical on every printed page ── */
html {{ height:100%; }}
body {{
  /* double gold frame drawn purely as background layers — cannot shift */
  background:
    linear-gradient({_IVORY}, {_IVORY}) padding-box,           /* ivory fill   */
    url("data:image/svg+xml,{frame_svg}") no-repeat center/100% 100% border-box;
}}
@page {{ size:A4; margin:11mm 11mm 12mm; }}
.page {{ position:relative; }}

/* ── cover ── */
.cover {{ text-align:center; }}
.kicker {{ letter-spacing:.4em; font-size:9px; color:#8a774e; text-transform:uppercase; }}
h1 {{ font-size:30pt; font-weight:700; margin:4mm 0 1mm; color:#2e2818; letter-spacing:.03em; }}
.gold-text {{ background:linear-gradient(105deg,#8a6d25,#c9a84c 45%,#7a5f22);
  -webkit-background-clip:text; background-clip:text; color:transparent; }}
.sub {{ color:#6d5f43; font-size:10pt; letter-spacing:.12em; font-style:italic; }}
.epigraph {{ margin-top:2.5mm; font-size:9.5pt; color:#9a7b34; font-style:italic;
  opacity:.85; letter-spacing:.04em; }}

/* ── art plate ── */
.art-plate {{ position:relative; width:118mm; margin:8mm auto 2mm; }}
.art-plate img {{ width:100%; display:block; border-radius:1mm; }}
.art-frame {{ position:absolute; inset:-3.2mm; border:1px solid {_GOLD};
  border-radius:1.5mm; pointer-events:none; }}
.credit {{ font-size:7.5pt; color:#8a774e; font-style:italic; margin-bottom:6mm; }}

.wheel-wrap {{ display:flex; justify-content:center; margin:2mm 0 6mm; }}
.wheel {{ width:62mm; height:62mm; }}

.name-chip {{ display:inline-block; padding:2.5mm 9mm;
  border:1px solid {_GOLD_SOFT}; border-radius:999px; font-size:12pt;
  color:#4a3f28; letter-spacing:.06em; background:#fdfaf1; }}
.rule {{ height:0; width:52%; margin:7mm auto; border-top:1px solid {_GOLD_SOFT};
  position:relative; }}
.rule::after {{ content:"✦"; position:absolute; left:50%; top:-7.5px;
  transform:translateX(-50%); color:{_GOLD}; background:{_IVORY}; padding:0 3.5mm; }}

/* ── section cards: flat ivory panels, thin gold left rule ── */
.card {{ background:#fbf7ec; border-left:2.5px solid {_GOLD};
  border-top:1px solid rgba(154,123,52,.18); border-right:1px solid rgba(154,123,52,.18);
  border-bottom:1px solid rgba(154,123,52,.18);
  border-radius:0 2mm 2mm 0; padding:6.5mm 7.5mm 6mm; margin-bottom:5mm;
  break-inside:avoid; page-break-inside:avoid; }}
.card h2 {{ font-size:13.5pt; color:#33291a; margin-bottom:4.5mm;
  display:flex; align-items:center; gap:4mm; padding-bottom:2.5mm;
  border-bottom:1px solid rgba(154,123,52,.15); }}
.card h2 .num {{ color:{_GOLD}; font-style:italic; font-size:14pt; }}
.body p {{ font-size:10.8pt; line-height:1.78; margin-bottom:2.8mm; color:#443a26; text-align:justify; }}
.body b {{ color:#33291a; font-weight:700; }}
.body p i.story, .body p.story {{ display:block; font-style:normal; color:#5a4a28;
  background:rgba(154,123,52,.07); border-left:2px solid rgba(154,123,52,.45);
  padding:2.5mm 3.5mm; border-radius:0 1.5mm 1.5mm 0; margin-bottom:3mm;
  font-size:10.2pt; line-height:1.85; }}

.seal-row {{ text-align:center; margin:3mm 0 1mm;
  break-inside:avoid; page-break-inside:avoid; }}
.seal {{ display:inline-flex; width:17mm; height:17mm; border-radius:50%;
  background:radial-gradient(circle at 35% 32%, #a63b40, #7c2328 60%, #5f181d);
  box-shadow:0 2px 8px rgba(60,10,12,.35), inset 0 0 0 1.6px rgba(255,235,220,.18);
  align-items:center; justify-content:center; color:#f4dfc8;
  font-size:11pt; font-weight:700; letter-spacing:.08em; }}

/* ── bi-wheel ── */
.biwheel-wrap {{ display:flex; justify-content:center; margin:4mm 0 2mm; }}
.biwheel {{ width:118mm; height:118mm;
  filter:drop-shadow(0 3px 14px rgba(90,60,20,.18)); }}

/* ── in-card artwork ── */
.card-art {{ margin:1mm 0 4mm; }}
.card-art img {{ width:100%; max-height:78mm; object-fit:cover;
  border-radius:1.5mm; display:block;
  box-shadow:0 2px 10px rgba(90,60,20,.15); }}
.card-art .credit {{ font-size:7pt; color:#8a774e; font-style:italic; margin-top:1.5mm; }}

/* ── personal tarot cards ── */
.trow-head {{ font-size:12.5pt; font-weight:700; color:#33291a;
  margin:9mm 0 5mm; padding:2.5mm 4mm;
  background:linear-gradient(90deg, rgba(154,123,52,.14), transparent);
  border-left:3px solid #9a7b34; letter-spacing:.04em;
  break-after:avoid; page-break-after:avoid; }}
/* first player header needs less top gap (comes right after section title) */
.trow-head:first-of-type {{ margin-top:2mm; }}
.trow {{ display:flex; gap:5mm; margin-bottom:4mm; }}
.trow {{ align-items:flex-start; }}
.tcard {{ flex:1; background:#fffdf6; border:1px solid rgba(154,123,52,.25);
  border-radius:2mm; padding:3mm 3.5mm 3.5mm;
  break-inside:avoid; page-break-inside:avoid; }}
.tcard-img img {{ width:100%; border-radius:1.5mm; display:block;
  box-shadow:0 2px 8px rgba(90,60,20,.18); }}
.tcard-pos {{ font-size:8pt; color:#8a774e; letter-spacing:.14em; text-transform:uppercase;
  margin-top:2.5mm; }}
.tcard-name {{ font-size:11pt; font-weight:700; color:#33291a; margin:1mm 0 1.5mm; }}
.rev {{ color:#a05252; font-size:9pt; }}
.tcard-beat {{ font-size:9pt; color:#7a6234; font-style:italic; margin-bottom:1.5mm; }}
.tcard-story {{ font-size:8.8pt; line-height:1.75; color:#5a4a28;
  background:rgba(154,123,52,.06); border-left:2px solid rgba(154,123,52,.4);
  padding:2mm 2.5mm; border-radius:0 1.2mm 1.2mm 0; margin-bottom:1.5mm;
  font-style:normal; }}
.tcard-mean {{ font-size:9.3pt; line-height:1.65; color:#55492f; }}

/* ── fairy-tale flourishes ── */
.starfield {{ position:absolute; inset:0; width:100%; height:100%;
  pointer-events:none; z-index:0; opacity:.55; }}
.page > * {{ position:relative; z-index:1; }}

.const-row {{ display:flex; justify-content:center; gap:6mm; margin:2mm 0 4mm; }}
.constellation {{ width:44mm; }}
.moons {{ width:120mm; margin:0 auto 2mm; display:block; }}

.footer {{ text-align:center; margin-top:1.5mm; color:#8a774e; font-size:8pt;
  letter-spacing:.28em; text-transform:uppercase;
  break-inside:avoid; page-break-inside:avoid; }}
</style></head><body>
{stars}
<div class="page">
  <header class="cover">
    <div class="kicker">Astral · Society of Cosmic Sciences</div>
    <h1><span class="gold-text">{t_title}</span></h1>
    <div class="sub">{t_sub}</div>
    <div class="epigraph">"สองดวงชะตาที่พบกัน คือดาวสองดวงที่เขียนนิทานร่วมกัน"</div>

    {art_html}
    {art_credit}

    <div class="rule"></div>
    <div class="wheel-wrap">{wheel}</div>
    <div class="name-chip">{name}</div>
    {biwheel_block}
    <div class="rule"></div>
    {constellations}
    {moons}
  </header>

  <div style="height:8mm"></div>
  {''.join(body_sections)}
  {raw_block}

  <div class="seal-row"><div class="seal">A</div></div>
  <div class="footer">Astral · Est. MMXXVI · โหราศาสตร์ครบวงจร</div>
</div>
</body></html>"""


def render_pdf(sections: list[dict], out_path: str,
               person_name: str = "", lang: str = "th",
               theme_hint: str = "", biwheel: str = "",
               section_art: dict[int, str] | None = None,
               raw_section: str = "", raw_title: str = "") -> str:
    html = build_html(sections, person_name, lang, theme_hint,
                      biwheel=biwheel, section_art=section_art,
                      raw_section=raw_section, raw_title=raw_title)
    tmp_html = out_path.replace(".pdf", ".html")
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(html)

    # Linux CI: playwright chromium if present, else fall through to Windows paths
    linux_candidates = [
        os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux/chrome"),
        "/usr/bin/google-chrome", "/usr/bin/chromium-browser", "/usr/bin/chromium",
    ]
    import glob as _glob
    for pat in [c for c in linux_candidates if "*" in c]:
        hits = sorted(_glob.glob(pat))
        if hits:
            chrome_candidates_linux = hits[-1]
            break
    else:
        chrome_candidates_linux = next((c for c in linux_candidates if os.path.exists(c)), None)

    chrome_candidates = [
        *( [chrome_candidates_linux] if chrome_candidates_linux else [] ),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    chrome = next((c for c in chrome_candidates if os.path.exists(c)), None)
    if not chrome:
        raise RuntimeError("Chrome/Edge not found for PDF rendering")

    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--no-pdf-header-footer", "--print-to-pdf=" + os.path.abspath(out_path),
           "file:///" + os.path.abspath(tmp_html).replace("\\", "/")]
    r = subprocess.run(cmd, capture_output=True, timeout=120)
    if not os.path.exists(out_path) or os.path.getsize(out_path) < 5000:
        raise RuntimeError(f"PDF render failed: {r.stderr.decode(errors='ignore')[:300]}")
    os.remove(tmp_html)
    return out_path
