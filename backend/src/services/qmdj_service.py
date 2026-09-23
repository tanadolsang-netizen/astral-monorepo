"""Qi Men Dun Jia 奇門遁甲 — hour-based destiny plate (simplified classical).

Deterministic structure: solar-term dun rotation, 9 palaces with
Star + Door + God + Heaven/Earth stems. Simplified but consistent
plate rules documented in-code.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from src.services.bazi_service import jdn

# Heavenly stems in QMDJ order
STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
STEMS_TH = ["เจี๋ย", "อี้", "ปิ่ง", "ติง", "อู่", "จี๋", "เกิง", "ซิน", "เหริน", "กุย"]

NINE_STARS = ["天蓬", "天芮", "天沖", "天輔", "天禽", "天心", "天柱", "任", "英"]
NINE_STARS_TH = ["เทียนเพิง", "เทียนุย", "เทียนชง", "เทียนฝู", "เทียนฉิน",
                 "เทียนซิน", "เทียนจู", "เหริน", "อิง"]
EIGHT_DOORS = ["休門", "生門", "傷門", "杜門", "景門", "死門", "驚門", "開門"]
EIGHT_DOORS_TH = ["ดูซิว (พัก)", "โช่วมง (เกิด/ลาภ)", "ซางมง (บาดเจ็บ)",
                  "ตู้มง (ปิดกั้น)", "จิ่งมง (แสงสว่าง)", "สื่อมง (จบสิ้น)",
                  "จิงมง (ตกใจ)", "ไคมง (เปิด/สำเร็จ)"]
EIGHT_GODS = ["值符", "騰蛇", "太陰", "六合", "白虎", "玄武", "九地", "九天"]
EIGHT_GODS_TH = ["จื้อฟู (ผู้นำ)", "เถิงเสวย (ความฝัน)", "ไท่อิน (ลับๆ)",
                 "ลิ่วเหอ (คู่)", "ไป่หู (ดุร้าย)", "เสวนอู่ (ลวง)",
                 "จิ่วตี้ (มั่นคง)", "จิ่วเทียน (สูงส่ง)"]

# Solar terms approx start days (month, day) for dun switching
_SOLAR_TERMS = [(2, 4), (3, 6), (4, 5), (5, 6), (6, 6), (7, 7),
                (8, 8), (9, 8), (10, 8), (11, 7), (12, 7), (1, 6)]


def _solar_term_index(dt: datetime) -> int:
    """0-23 term index (Yang dun terms are even indices after winter solstice)."""
    m, day = dt.month, dt.day
    # find which term window we're in
    boundaries = sorted([(m2 * 100 + d2, i)
                         for i, (m2, d2) in enumerate(_SOLAR_TERMS)])
    key = m * 100 + day
    current = 0
    for bkey, idx in boundaries:
        if key >= bkey:
            current = idx
    return current


def _day_ganzhi_index(dt: datetime) -> tuple[int, int]:
    """(stem_idx, branch_idx) of the JDN-based day pillar."""
    day_jdn = jdn(dt.year, dt.month, dt.day)
    stem = day_jdn % 10
    branch = (day_jdn + 10) % 12
    return stem, branch


def _hour_ganzhi(dt: datetime, day_stem: int) -> tuple[int, int]:
    hour_branch = ((dt.hour + 1) // 2) % 12
    hour_stem = (day_stem % 5) * 2 + hour_branch % 10 - hour_branch
    hour_stem = (day_stem * 2 + hour_branch) % 10
    return hour_stem % 10, hour_branch


def _dun_number(dt: datetime, day_stem: int) -> int:
    """Upper/middle/lower yuan dun number 1..9."""
    is_yang = dt.month in (12, 1, 2, 3, 4) or (dt.month == 5 and dt.day < 6)
    base = (day_stem % 9) + 1
    return base if is_yang else (10 - base)


def _rotate(seq: list, offset: int) -> list:
    n = len(seq)
    return [seq[(i - offset) % n] for i in range(n)]


def compute_qmdj(question_dt_local: datetime, tz_offset_hours: float = 7.0,
                 intent: str = "career") -> dict:
    utc = question_dt_local - timedelta(hours=tz_offset_hours)
    day_stem, day_branch = _day_ganzhi_index(utc)
    hour_stem, hour_branch = _hour_ganzhi(question_dt_local, day_stem)

    dun = _dun_number(utc, day_stem)
    yang = utc.month not in (6, 7, 8, 9, 10)

    # plate: rotate stars/doors/gods/stems by dun+hour offset
    offset = (dun * 2 + hour_branch) % 9
    palaces = []
    star_rot = _rotate(NINE_STARS, offset)
    door_rot = _rotate(EIGHT_DOORS, (offset + hour_branch) % 8)
    god_rot = _rotate(EIGHT_GODS, (offset + hour_stem) % 8)
    heaven_stems = _rotate(STEMS, offset)
    earth_stems = _rotate(STEMS, (offset + dun) % 10)

    palace_names_th = ["坎1(北)", "坤2(西南)", "震3(東)", "巽4(東南)", "中5",
                       "乾6(西北)", "兌7(西)", "艮8(東北)", "離9(南)"]
    directions_th = ["ทิศเหนือ", "ทิศตะวันตกเฉียงใต้", "ทิศตะวันออก",
                     "ทิศตะวันออกเฉียงใต้", "ศูนย์กลาง", "ทิศตะวันตกเฉียงเหนือ",
                     "ทิศตะวันตก", "ทิศตะวันออกเฉียงเหนือ", "ทิศใต้"]

    for i in range(9):
        palaces.append({
            "palace": i + 1, "direction_th": directions_th[i],
            "star": NINE_STARS_TH[i], "star_cn": star_rot[i],
            "door": EIGHT_DOORS_TH[i % 8], "door_cn": door_rot[i % 8],
            "god": EIGHT_GODS_TH[i % 8], "god_cn": god_rot[i % 8],
            "heaven_stem": heaven_stems[i], "earth_stem": earth_stems[i],
        })

    INTENT_DOOR = {
        "career": "ไคมง (เปิด/สำเร็จ)", "wealth": "โช่วมง (เกิด/ลาภ)",
        "love": "ลิ่วเหอ (คู่)", "travel": "休門 (พัก)",
    }
    target_door = INTENT_DOOR.get(intent, "ไคมง (เปิด/สำเร็จ)")
    best = next((p for p in palaces if p["door"] == target_door), palaces[0])

    th = (
        f"ดวงปี่เหมินดุนเจี๋ย เวลา{question_dt_local.strftime('%H:%M')} "
        f"ดุนที่ {dun} ({'หยาง' if yang else 'หยิ่น'}ดุน) — "
        f"สำหรับเรื่อง{intent}: ประตู{best['door']} ณ {best['direction_th']} "
        f"เทพ{best['god']} คุ้มครอง — เสริมการกระทำได้"
    )
    en = (
        f"QMDJ chart at {question_dt_local.strftime('%H:%M')}, dun #{dun}. "
        f"For '{intent}': favorable gate at palace {best['palace']} "
        f"({best['direction_th']})."
    )

    return {"system": "qimen-dunjia", "dun": dun, "yang_dun": yang,
            "intent": intent, "best_palace": best, "palaces": palaces,
            "interpretation": {"th": th, "en": en}}
