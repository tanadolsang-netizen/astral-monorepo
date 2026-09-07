"""Elemental balance of a chart.

The four classical elements are the one vocabulary shared by every branch
already in raw/astrology/ and by the tarot suits in raw/tarot/, so this is
the join key between the two halves of the app: a chart's element weights
can be compared against a spread's suit distribution.

Sign -> element is identical in tropical and sidereal; only which sign a
body falls in differs, so this works unchanged for both systems.
"""

ELEMENTS = ["fire", "earth", "air", "water"]

# Keyed on the Thai(English) sign labels produced by chart_service.SIGNS.
SIGN_ELEMENT: dict[str, str] = {
    "เมษ(Aries)": "fire",
    "สิงห์(Leo)": "fire",
    "ธนู(Sagittarius)": "fire",
    "พฤษภ(Taurus)": "earth",
    "กันย์(Virgo)": "earth",
    "มังกร(Capricorn)": "earth",
    "เมถุน(Gemini)": "air",
    "ตุลย์(Libra)": "air",
    "กุมภ์(Aquarius)": "air",
    "กรกฎ(Cancer)": "water",
    "พิจิก(Scorpio)": "water",
    "มีน(Pisces)": "water",
}

# The luminaries and the rising sign describe the person; the outer planets
# sit in one sign for years at a time and describe a whole cohort, so they
# are down-weighted rather than counted equally.
BODY_WEIGHT: dict[str, float] = {
    "ASC": 3.0,
    "Sun": 3.0,
    "Moon": 3.0,
    "Mercury": 2.0,
    "Venus": 2.0,
    "Mars": 2.0,
    "Jupiter": 1.0,
    "Saturn": 1.0,
    "Uranus": 0.5,
    "Neptune": 0.5,
    "Pluto": 0.5,
}

TAROT_SUIT = {"fire": "Wands", "earth": "Pentacles", "air": "Swords", "water": "Cups"}

_DOMAIN = {
    "fire": "แรงผลักดัน การลงมือทำ ความกล้า",
    "earth": "ความมั่นคง ความอดทน การทำจริงเป็นระบบ",
    "air": "ความคิด การสื่อสาร การเชื่อมโยงผู้คน",
    "water": "อารมณ์ ความสัมพันธ์ สัญชาตญาณ",
}


def compute_element_balance(chart: dict) -> dict:
    """Weighted element distribution for a chart from compute_chart()."""
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
            f"ธาตุเด่นคือ{dominant} ({_DOMAIN[dominant]}) "
            f"ส่วนธาตุที่บางที่สุดคือ{lacking} ({_DOMAIN[lacking]}) "
            f"— ไพ่ชุด {TAROT_SUIT[lacking]} ที่เปิดได้จึงมักพูดถึงด้านที่ยังต้องพัฒนา"
        ),
    }
