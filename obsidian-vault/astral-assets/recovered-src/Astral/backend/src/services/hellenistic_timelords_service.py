"""Hellenistic time-lord systems — Zodiacal Releasing, Annual Profections, Firdaria.

Valens-method ZR + standard profections + classical Firdaria sequence.
All pure date arithmetic on the natal chart; offline deterministic.
"""
from __future__ import annotations

from datetime import datetime, timedelta

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_TH = ["เมษ", "พฤษภ", "เมถุน", "กรกฎ", "สิงห์", "กันย์",
           "ตุลย์", "พิจิก", "ธนู", "มกร", "กุมภ์", "มีน"]
# Valens periods (years)
SIGN_YEARS = {"Cancer": 45, "Leo": 30, "Virgo": 40, "Gemini": 40,
              "Libra": 30, "Scorpio": 30, "Sagittarius": 12, "Pisces": 12,
              "Capricorn": 27, "Aquarius": 27, "Aries": 8, "Taurus": 8}
SIGN_RULER = {"Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
              "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
              "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
              "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"}
RULER_TH = {"Sun": "ดวงอาทิตย์", "Moon": "ดวงจันทร์", "Mercury": "ดาวพุธ",
            "Venus": "ดาวศุกร์", "Mars": "ดาวอังคาร", "Jupiter": "ดาวพฤหัสฯ",
            "Saturn": "ดาวเสาร์"}


def _sign_index(lon: float) -> int:
    return int(lon // 30) % 12


def zodiacal_releasing(lot_lon: float, birth_date: datetime,
                       max_years: float = 120.0) -> dict:
    """ZR L1 from a lot longitude (Spirit for career/fortune for body)."""
    start_idx = _sign_index(lot_lon)
    chapters = []
    age = 0.0
    idx = start_idx
    chapter_no = 1
    while age < max_years:
        sign = SIGNS[idx]
        years = float(SIGN_YEARS[sign])
        end_age = min(age + years, max_years)
        # loosing of the bond: when sub-period reaches the 7th sign from L1
        is_lob = ((idx - start_idx) % 12) == 6
        chapters.append({
            "n": chapter_no, "sign_en": sign, "sign_th": SIGN_TH[idx],
            "lord": SIGN_RULER[sign], "lord_th": RULER_TH[SIGN_RULER[sign]],
            "age_from": round(age, 2), "age_to": round(end_age, 2),
            "years": round(end_age - age, 2),
            "loosing_of_bond": bool(is_lob) and chapter_no > 1,
        })
        age = end_age
        idx = (idx + 1) % 12
        chapter_no += 1
    return {
        "lot_sign_en": SIGNS[start_idx], "lot_sign_th": SIGN_TH[start_idx],
        "chapters": chapters,
        "peaks": [c for c in chapters if c["loosing_of_bond"]],
    }


def annual_profections(age: int, asc_lon: float) -> dict:
    """Age-based annual profection from rising sign."""
    house = (age % 12) + 1
    sign_idx = (_sign_index(asc_lon) + age % 12) % 12
    return {
        "age": age, "house": house, "sign_en": SIGNS[sign_idx],
        "sign_th": SIGN_TH[sign_idx], "lord": SIGN_RULER[SIGNS[sign_idx]],
        "lord_th": RULER_TH[SIGN_RULER[SIGNS[sign_idx]]],
        "theme_en": {
            1: "self & identity", 2: "money & values", 3: "communication",
            4: "home & family", 5: "creativity & romance", 6: "health & work",
            7: "partnership", 8: "transformation", 9: "travel & study",
            10: "career peak", 11: "friends & gains", 12: "rest & release",
        }[house],
    }


_FIRDARIA_DAY = [("Sun", 6), ("Venus", 8), ("Mercury", 13), ("Moon", 9),
                 ("Saturn", 11), ("Jupiter", 12), ("Mars", 7),
                 ("North Node", 3), ("South Node", 2)]
_FIRDARIA_NIGHT = [("Moon", 9), ("Saturn", 11), ("Jupiter", 12), ("Mars", 7),
                   ("Sun", 5), ("Venus", 10), ("Mercury", 13),
                   ("North Node", 3), ("South Node", 2)]


def firdaria(birth_date: datetime, is_day_chart: bool,
             max_years: float = 75.0) -> dict:
    seq = _FIRDARIA_DAY if is_day_chart else _FIRDARIA_NIGHT
    periods = []
    age = 0.0
    total = sum(y for _, y in seq)
    scale = max_years / total
    for lord, yrs in seq:
        span = yrs * scale
        end = min(age + span, max_years)
        if age >= max_years:
            break
        periods.append({"lord": lord, "lord_th": RULER_TH.get(
            lord, "โหนดเหนือ" if lord == "North Node" else "โหนดใต้"),
            "age_from": round(age, 1), "age_to": round(end, 1)})
        age = end
    return {"sequence": "day" if is_day_chart else "night", "periods": periods}


def compute_timelords(natal_asc_lon: float, lot_of_spirit_lon: float,
                      lot_of_fortune_lon: float, birth_iso_local: str,
                      tz_offset_hours: float = 7.0,
                      query_age: int | None = None) -> dict:
    birth_dt = datetime.fromisoformat(birth_iso_local)
    zr_spirit = zodiacal_releasing(lot_of_spirit_lon, birth_dt)
    zr_fortune = zodiacal_releasing(lot_of_fortune_lon, birth_dt)
    prof = annual_profections(query_age if query_age is not None else 35,
                              natal_asc_lon)
    # day/night: Sun below horizon (houses 1-6 whole-sign from ASC) = night
    result = {
        "system": "hellenistic-timelords",
        "zr_spirit": zr_spirit,
        "zr_fortune": {"chapters": zr_fortune["chapters"][:8]},
        "profection_current": prof,
        "firdaria": firdaria(birth_dt, is_day_chart=True),
    }
    current_zr = next((c for c in zr_spirit["chapters"]
                       if c["age_from"] <= (query_age or 0) <= c["age_to"]),
                      zr_spirit["chapters"][0])
    lob_note = ""
    if current_zr.get("loosing_of_bond"):
        lob_note = " — ช่วงนี้คือ <b>loosing of the bond</b> จุดหักเหสำคัญของชีวิต!"
    result["interpretation"] = {
        "th": (
            f"ปีอายุ {prof['age']} ของคุณคือปีบ้านที่ {prof['house']} "
            f"(ราศี{prof['sign_th']} ผู้คุมคือ{prof['lord_th']}) — "
            f"ธีม: {prof['theme_en']}. ระยะ ZR ปัจจุบันอยู่ภายใต้ราศี"
            f"{current_zr['sign_th']} ผู้คุม{current_zr['lord_th']} "
            f"({current_zr['age_from']:.0f}-{current_zr['age_to']:.0f} ปี)"
            f"{lob_note}. Firdaria วันแบบคลาสสิกเริ่มจากดวงอาทิตย์สำหรับดวงกลางวัน"
        ),
        "en": (
            f"Age {prof['age']} profection: house {prof['house']} "
            f"({prof['sign_en']}, lord {prof['lord']}) — theme: {prof['theme_en']}. "
            f"Current ZR chapter: {current_zr['sign_en']} under "
            f"{current_zr['lord']} ({current_zr['age_from']:.0f}-"
            f"{current_zr['age_to']:.0f})"
            + (" — this is a LOOSING OF THE BOND period, a major turning point!"
               if current_zr.get("loosing_of_bond") else "")
        ),
    }
    return result
