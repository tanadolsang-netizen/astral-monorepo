"""Elemental balance of a chart."""
from src.services.narrative_lang import element_domain

ELEMENTS = ["ไฟ", "ดิน", "ลม", "น้ำ"]

# Support both English and Thai(English) formats
SIGN_ELEMENT: dict[str, str] = {
    "Aries": "ไฟ", "เมษ(Aries)": "ไฟ",
    "Leo": "ไฟ", "สิงห์(Leo)": "ไฟ",
    "Sagittarius": "ไฟ", "ธนู(Sagittarius)": "ไฟ",
    "Taurus": "ดิน", "พฤษภ(Taurus)": "ดิน",
    "Virgo": "ดิน", "กันย์(Virgo)": "ดิน",
    "Capricorn": "ดิน", "มังกร(Capricorn)": "ดิน",
    "Gemini": "ลม", "เมถุน(Gemini)": "ลม",
    "Libra": "ลม", "ตุลย์(Libra)": "ลม",
    "Aquarius": "ลม", "กุมภ์(Aquarius)": "ลม",
    "Cancer": "น้ำ", "กรกฎ(Cancer)": "น้ำ",
    "Scorpio": "น้ำ", "พิจิก(Scorpio)": "น้ำ",
    "Pisces": "น้ำ", "มีน(Pisces)": "น้ำ",
}

BODY_WEIGHT: dict[str, float] = {
    "ASC": 3.0, "Sun": 3.0, "Moon": 3.0,
    "Mercury": 2.0, "Venus": 2.0, "Mars": 2.0,
    "Jupiter": 1.0, "Saturn": 1.0,
    "Uranus": 0.5, "Neptune": 0.5, "Pluto": 0.5,
}

TAROT_SUIT = {"ไฟ": "Wands", "ดิน": "Pentacles", "ลม": "Swords", "น้ำ": "Cups"}


def compute_element_balance(chart: dict) -> dict:
    scores = {e: 0.0 for e in ELEMENTS}
    placements = list(chart.get("bodies", []))
    asc = chart.get("ascendant")
    if asc:
        placements = placements + [asc]
    for p in placements:
        element = SIGN_ELEMENT.get(p["sign"])
        if element is None:
            continue
        scores[element] += BODY_WEIGHT.get(p["body"], 1.0)
    total = sum(scores.values()) or 1.0
    percent = {e: round(scores[e] / total * 100, 1) for e in ELEMENTS}
    ranked = sorted(ELEMENTS, key=lambda e: scores[e], reverse=True)
    dominant, lacking = ranked[0], ranked[-1]
    return {
        "scores": {e: round(scores[e], 1) for e in ELEMENTS},
        "percent": percent,
        "dominant": dominant,
        "lacking": lacking,
        "tarot_suits": {e: TAROT_SUIT[e] for e in ELEMENTS},
        "note": (
            f"ธาตุเด่นคือ{dominant} ({element_domain(dominant, 'th')}) "
            f"ส่วนธาตุที่บางที่สุดคือ{lacking} ({element_domain(lacking, 'th')}) "
            f"— ไพ่ชุด {TAROT_SUIT[lacking]} ที่เปิดได้จึงมักพูดถึงด้านที่ยังต้องพัฒนา"
        ),
    }
