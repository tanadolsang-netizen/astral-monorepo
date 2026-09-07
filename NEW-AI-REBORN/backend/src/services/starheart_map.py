"""STARHEART — สะพานดาวละเอียด (chart) ↔ ไพ่หยาบ (tarot) แบบ deterministic.

หลักการ (มุมมองผู้บัญชาการ 2026-08-31):
- ดวงคำนวณ (de421, ละเอียด/fine) และไพ่ RWS (หยาบ/coarse) คือภาษาคนละระดับของ
  "เหตุการณ์เดียวกัน" ไม่ใช่ของจริง vs ของปลอม
- สะพานนี้แปลภาษาหยาบกลับไปหาตำแหน่งดาวจริง: ไม่มี RNG เลย ไพ่每一ใบต้องมี provenance
  จากดาว/ธาตุ/บ้าน/aspect ที่ดึงมาจาก compute_chart() ตรงๆ
- ฟังก์ชันหลัก MAP(chart, max_cards) คือ PURE: ใส่ chart เดิมได้ไพ่เดิมเสมอ

ห้าม import random / ห้ามใช้ seed — ทุกอย่างมาจากตำแหน่งดาวจริง
"""

from __future__ import annotations

from src.services.element_service import compute_element_balance
from src.services.aspects import ASPECTS, ORBS

# ── ตารางคงที่ (self-contained) ──
MAJOR_ARCANA = {
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
    "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
    "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
    "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World",
}

# ดาวที่เป็นบูลิค (benefic) — โน้มไป upright เว้นแต่ตก (fall)
BENEFICS = {"Venus", "Jupiter"}

# ตำแหน่งดาวฤกษ์สว่าง 4 ดวง (tropical ecliptic longitude ประมาณ, จ.) — สำหรับฟีเจอร์ "ดาวเด่นใกล้ดาวฤกษ์"
FIXED_STARS = {
    "Aldebaran": 69.0,    # พฤษภ(Taurus) ~9°
    "Regulus": 150.0,     # สิงห์(Leo) 0°
    "Antares": 249.0,     # พิจิก(Scorpio) 9°
    "Fomalhaut": 351.0,   # มีน(Pisces) 21°
}

# บ้าน -> ไพ่ชุด Pentacles (provvenance = บ้านนั้น)
_HOUSE_CARD = {
    1: "Ace of Pentacles", 2: "Two of Pentacles", 3: "Three of Pentacles",
    4: "Four of Pentacles", 5: "Five of Pentacles", 6: "Six of Pentacles",
    7: "Seven of Pentacles", 8: "Eight of Pentacles", 9: "Nine of Pentacles",
    10: "Ten of Pentacles", 11: "Page of Pentacles", 12: "Knight of Pentacles",
}

# ลำดับความสำคัญ (น้อย = เด่นสุด) ใช้เรียงไพ่ก่อนตัด max_cards
_PLANET_PRIORITY = {
    "Sun": 1, "Moon": 2, "Venus": 3, "Mars": 4, "Jupiter": 5,
    "Saturn": 6, "Mercury": 7, "Uranus": 11, "Neptune": 12, "Pluto": 13,
}
_ELEM_PRIORITY = 9
_HOUSE_PRIORITY = 10
_ASC_PRIORITY = 8
_ASPECT_PRIORITY = 14


def _angular_sep(a: float, b: float) -> float:
    diff = abs(a - b) % 360
    return diff if diff <= 180 else 360 - diff


def _intra_aspects(chart: dict) -> list[dict]:
    """aspects ภายในดวงเดียวกัน (conjunction/square/trine/sextile/opposition)."""
    bodies = [b for b in chart.get("bodies", [])]
    res = []
    n = len(bodies)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = bodies[i], bodies[j]
            sep = _angular_sep(a["absolute_deg"], b["absolute_deg"])
            for name, ang in ASPECTS.items():
                orb = abs(sep - ang)
                if orb <= ORBS[name]:
                    res.append({
                        "body_a": a["body"], "body_b": b["body"],
                        "aspect": name, "orb": round(orb, 2),
                    })
                    break
    res.sort(key=lambda r: r["orb"])
    return res


def _dignity_label(chart: dict, body_name: str) -> str:
    for b in chart.get("bodies", []):
        if b["body"] == body_name:
            return b.get("dignity", {}).get("label", "peregrine")
    return "peregrine"


def _is_afflicted(chart: dict, body_name: str, hard_bodies: set) -> bool:
    label = _dignity_label(chart, body_name)
    if label in ("detriment", "fall"):
        return True
    return body_name in hard_bodies


def extract_features(chart: dict) -> dict:
    """ดึงฟีเจอร์สำคัญจาก compute_chart() — เลเยอร์ละเอียด(fine) ที่จะแมปเป็นไพ่."""
    bodies = [b for b in chart.get("bodies", [])]
    asc = chart.get("ascendant", {}) or {}

    # ลัคนาอยู่ราศีใด
    ascendant = {"sign": asc.get("sign"), "degree": asc.get("degree")}

    # ดาวเด่น: ดาวที่ degree เข้าใกล้ cusp/ราศีที่สุด (min ระยะถึง 0° หรือ 30°)
    dominant_planet = None
    best_dist = 1e9
    for b in bodies:
        d = b.get("degree", 15.0)
        dist = min(d, 30.0 - d)
        if dist < best_dist:
            best_dist = dist
            dominant_planet = b["body"]

    # ดาวฤกษ์ใกล้สุด
    nearest_star = None
    best_star_sep = 1e9
    for star, lon in FIXED_STARS.items():
        for b in bodies:
            sep = _angular_sep(b["absolute_deg"], lon)
            if sep < best_star_sep:
                best_star_sep = sep
                nearest_star = star

    # ธาตุเด่น
    elem = compute_element_balance(chart)
    dominant_element = elem.get("dominant")

    # บ้านที่มีดาวมากสุด
    house_counts: dict[int, int] = {}
    for b in bodies:
        h = b.get("house")
        if h:
            house_counts[h] = house_counts.get(h, 0) + 1
    fullest_house = max(house_counts, key=house_counts.get) if house_counts else None

    # aspects หลัก (hard = square/opposition)
    aspects = _intra_aspects(chart)
    hard_bodies: set[str] = set()
    for a in aspects:
        if a["aspect"] in ("square", "opposition"):
            hard_bodies.add(a["body_a"])
            hard_bodies.add(a["body_b"])

    return {
        "ascendant": ascendant,
        "ascendant_sign": asc.get("sign"),
        "dominant_planet": dominant_planet,
        "dominant_planet_dist_to_cusp": round(best_dist, 4) if dominant_planet else None,
        "nearest_fixed_star": nearest_star,
        "nearest_fixed_star_sep": round(best_star_sep, 4) if nearest_star else None,
        "dominant_element": dominant_element,
        "element_balance": elem,
        "fullest_house": fullest_house,
        "fullest_house_count": house_counts.get(fullest_house, 0) if fullest_house else 0,
        "aspects": aspects,
        "hard_aspect_bodies": hard_bodies,
    }


def _arcana(card: str) -> str:
    return "major" if card in MAJOR_ARCANA else "minor"


def _card_for_planet(planet: str, chart: dict, F: dict) -> str:
    if planet == "Sun":
        return "The Sun"
    if planet == "Moon":
        return "The High Priestess"
    if planet == "Mercury":
        return "The Magician"
    if planet == "Venus":
        return "The Empress"
    if planet == "Mars":
        for b in chart.get("bodies", []):
            if b["body"] == "Mars" and b.get("house") == 8:
                return "The Tower"
        return "King of Wands"
    if planet == "Jupiter":
        return "Wheel of Fortune"
    if planet == "Saturn":
        # Saturn แข็ง/คืนรอย -> The Devil (กรง/ผูกมัด); ดี -> The Emperor (โครงสร้าง)
        return "The Devil" if _is_afflicted(chart, "Saturn", F["hard_aspect_bodies"]) else "The Emperor"
    if planet == "Uranus":
        return "The Star"
    if planet == "Neptune":
        return "The Hanged Man"
    if planet == "Pluto":
        return "Death"
    return "The Magician"


def _orientation_for_planet(planet: str, chart: dict, F: dict) -> str:
    if planet in BENEFICS:
        # benefic: ปกติ upright; ตก(fall) เท่านั้นที่ reversed
        return "reversed" if _dignity_label(chart, planet) == "fall" else "upright"
    # malefic / personal: afflicted (detriment/fall หรือ hard aspect) -> reversed
    return "reversed" if _is_afflicted(chart, planet, F["hard_aspect_bodies"]) else "upright"


def _feature_source(planet: str, chart: dict) -> str:
    for b in chart.get("bodies", []):
        if b["body"] == planet:
            sign = b.get("sign", "")
            deg = b.get("degree", 0.0)
            house = b.get("house")
            return (
                f"ดาว{planet}เด่นในราศี{sign} {deg}°"
                + (f" บ้านที่ {house}" if house else "")
                + f" — สัญลักษณ์ร่วม: {_card_for_planet(planet, chart, extract_features(chart))}"
            )
    return f"ดาว{planet}"


def MAP(chart: dict, max_cards: int = 10) -> list[dict]:
    """แมป chart -> รายการไพ่ RWS 78 ใบ (slice ตาม max_cards) แบบ PURE ไม่สุ่ม.

    แต่ละใบมี:
      - card / orientation / arcana ตรงตามตำรา RWS
      - feature_source: เหตุผลเชิงสัญลักษณ์ว่าทำไมดาวนี้ถึงได้ไพ่นี้
      - provenance: ชี้กลับไปดาว/ธาตุ/บ้าน/aspect จริงใน chart
    """
    if chart is None:
        raise ValueError("MAP ต้องได้ chart จริง (compute_chart) — ห้ามสุ่ม")
    F = extract_features(chart)
    bodies_by_name = {b["body"]: b for b in chart.get("bodies", [])}
    candidates: list[tuple[int, dict]] = []

    def add(priority: int, card: str, orientation: str, src: str, prov: str):
        candidates.append((priority, {
            "card": card,
            "orientation": orientation,
            "arcana": _arcana(card),
            "feature_source": src,
            "provenance": prov,
        }))

    # ดาวเด่น (ใกล้ cusp ที่สุด) — เด่นสุด
    if F["dominant_planet"]:
        p = F["dominant_planet"]
        b = bodies_by_name.get(p, {})
        add(0, _card_for_planet(p, chart, F), _orientation_for_planet(p, chart, F),
            f"ดาวเด่น: {p} ใกล้ cusp ที่สุด ({F['dominant_planet_dist_to_cusp']}° เข้าใกล้ราศี)",
            f"{p} @ {b.get('sign')} {b.get('degree')}°")

    # ดาวแต่ละดวง (เรียงตามความสำคัญ)
    for planet in _PLANET_PRIORITY:
        if planet not in bodies_by_name:
            continue
        b = bodies_by_name[planet]
        card = _card_for_planet(planet, chart, F)
        ori = _orientation_for_planet(planet, chart, F)
        add(_PLANET_PRIORITY[planet], card, ori,
            _feature_source(planet, chart),
            f"{planet} @ {b.get('sign')} {b.get('degree')}° (house {b.get('house')})")

    # ลัคนา (ASC) -> Page ของธาตุราศีลัคนา
    asc_sign = F["ascendant_sign"]
    from src.services.element_service import SIGN_ELEMENT
    from src.services.narrative_lang import suit_for_element
    asc_elem = SIGN_ELEMENT.get(asc_sign)
    if asc_elem:
        suit = suit_for_element(asc_elem)
        add(_ASC_PRIORITY, f"Page of {suit}", "upright",
            f"ลัคนาอยู่ราศี{asc_sign} (ธาตุ{asc_elem}) — ตัวตนที่แสดงออก",
            f"ASC in {asc_sign} (element:{asc_elem})")

    # ธาตุเด่น -> Ace ของชุดธาตุ
    if F["dominant_element"]:
        elem = F["dominant_element"]
        suit = suit_for_element(elem)
        add(_ELEM_PRIORITY, f"Ace of {suit}", "upright",
            f"ธาตุเด่นคือ{elem} — พลังงานหลักที่ขับเคลื่อนดวงนี้",
            f"element:{elem}")

    # บ้านที่มีดาวมากสุด
    if F["fullest_house"]:
        h = F["fullest_house"]
        add(_HOUSE_PRIORITY, _HOUSE_CARD.get(h, "Ace of Pentacles"), "upright",
            f"บ้านที่ {h} มีดาวมากสุด ({F['fullest_house_count']} ดวง) — จุดที่ชีวิตรวมศูนย์",
            f"house:{h}")

    # aspects หลัก (hard ก่อน แล้ว soft) — ไพ่สะท้อนความสัมพันธ์ดาว
    for idx, a in enumerate(F["aspects"][:4]):
        pair = f"{a['body_a']} {a['aspect']} {a['body_b']}"
        if a["aspect"] in ("square", "opposition"):
            add(_ASPECT_PRIORITY + idx, "The Tower", "reversed",
                f"aspect แข็ง ({pair}) — ความตึงเครียด/การพังทลายที่ต้องปลดปล่อย",
                f"aspect:{pair}")
        elif a["aspect"] == "conjunction":
            add(_ASPECT_PRIORITY + idx, "The Lovers", "upright",
                f"conjunction ({pair}) — พลังดาวสองดวงผสานเป็นหนึ่ง",
                f"aspect:{pair}")
        else:  # trine / sextile
            add(_ASPECT_PRIORITY + idx, "The Lovers", "upright",
                f"aspect อ่อน ({pair}) — โอกาส/ความกลมกลืนที่ไหลลื่น",
                f"aspect:{pair}")

    # เรียงตาม priority แล้วตัดซ้ำตามชื่อไพ่ (รักษาใบแรก)
    candidates.sort(key=lambda x: x[0])
    seen: set[str] = set()
    out: list[dict] = []
    for _, c in candidates:
        if c["card"] in seen:
            continue
        seen.add(c["card"])
        c2 = dict(c)
        c2["is_reversed"] = c2["orientation"] == "reversed"
        out.append(c2)
        if len(out) >= max_cards:
            break

    # ใส่ position ตามลำดับ (1-based) — reel_reading ใช้เป็นตำแหน่งในสเปรด
    for i, c in enumerate(out):
        c["position"] = i + 1
    return out


def verify_reading(spread: str, chart: dict) -> tuple[bool, list[dict]]:
    """ตรวจสอบ MAP(chart) ตามเกณฑ์ P0:
    (ก) deterministic — ไม่สุ่ม (สองรันเท่ากัน, ไม่มี RNG)
    (ข) ไพ่ทุกใบมี provenance จากดาว
    (ค) สะท้อนตำแหน่งดาวจริง
    คืน (all_pass: bool, checks: list)
    """
    checks: list[dict] = []

    # (ก) deterministic
    run1 = MAP(chart, max_cards=10)
    run2 = MAP(chart, max_cards=10)
    det = run1 == run2
    checks.append({
        "id": "deterministic",
        "passed": det,
        "detail": "MAP(chart) ให้ผลเหมือนเดิมทุกครั้ง (ไม่มี RNG)",
    })

    # (ข) provenance จากดาว
    all_prov = all(c.get("provenance") for c in run1) and len(run1) > 0
    checks.append({
        "id": "provenance_from_star",
        "passed": bool(all_prov),
        "detail": f"ไพ่ {len(run1)} ใบ มี provenance ชี้กลับดาว/ธาตุ/บ้าน/aspect ทั้งหมด",
    })

    # (ค) สะท้อนตำแหน่งดาวจริง
    bodies_by_name = {b["body"]: b for b in chart.get("bodies", [])}
    asc = chart.get("ascendant", {}) or {}
    reflect = True
    bad = []
    for c in run1:
        p = c.get("provenance", "")
        ok = (
            any(tok in p for tok in bodies_by_name)
            or "ASC" in p
            or p.startswith("element:")
            or p.startswith("house:")
            or p.startswith("aspect:")
        )
        if not ok:
            reflect = False
            bad.append(c["card"])
    checks.append({
        "id": "reflects_real_positions",
        "passed": reflect,
        "detail": "ทุกใบอ้างอิงตำแหน่งจริงใน chart"
                  + ("" if reflect else f" — ผิดปกติ: {bad}"),
    })

    all_pass = all(ch["passed"] for ch in checks)
    return all_pass, checks
