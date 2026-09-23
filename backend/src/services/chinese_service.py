"""สี่เสา (BaZi) + ธาตุทั้งห้า + นักษัตร

คำนวณเสาปี เดือน วัน และชั่วโมง จากวัน-เวลาเกิด
โดยใช้ระบบหกสิบปี ไม่ต้องพึ่งดาวพระเคราะห์ — คำนวณจากปฏิทินล้วนๆ

ทุกอย่างเป็นภาษาไทย ไม่มีตัวอักษรจีน
"""

from datetime import date as _date, time as _time, datetime as _dt

# ── ฟ้าつもり (十天干 · ทั้งสิบ) ──────────────────────────────────

HEAVENLY_STEMS: list[dict] = [
    {"index": 0,  "thai": "กั่ว", "name": "Gia",  "polarity": "yang", "element": "wood",
     "thai_element": "ไม้หยาง"},
    {"index": 1,  "thai": "หยี",  "name": "Yi",   "polarity": "yin",  "element": "wood",
     "thai_element": "ไม้หยิน"},
    {"index": 2,  "thai": "เปง",  "name": "Bing", "polarity": "yang", "element": "fire",
     "thai_element": "ไฟหยาง"},
    {"index": 3,  "thai": "เดง",  "name": "Ding", "polarity": "yin",  "element": "fire",
     "thai_element": "ไฟหยิน"},
    {"index": 4,  "thai": "บุ๋ง", "name": "Wu",   "polarity": "yang", "element": "earth",
     "thai_element": "ดินหยาง"},
    {"index": 5,  "thai": "กี",   "name": "Ji",   "polarity": "yin",  "element": "earth",
     "thai_element": "ดินหยิน"},
    {"index": 6,  "thai": "เกง",  "name": "Geng", "polarity": "yang", "element": "metal",
     "thai_element": "โลหะหยาง"},
    {"index": 7,  "thai": "ซิม",  "name": "Xin",  "polarity": "yin",  "element": "metal",
     "thai_element": "โลหะหยิน"},
    {"index": 8,  "thai": "เดง",  "name": "Ren",  "polarity": "yang", "element": "water",
     "thai_element": "น้ำหยาง"},
    {"index": 9,  "thai": "กุ้ย", "name": "Gui",  "polarity": "yin",  "element": "water",
     "thai_element": "น้ำหยิน"},
]

# ── ดินเสมอ (ทั้งสิบสอง) ───────────────────────────────────────

EARTHLY_BRANCHES: list[dict] = [
    {"index": 0,  "thai": "ชวด",    "animal": "ชวด",   "animal_en": "Rat",    "element": "water",
     "thai_element": "น้ำ"},
    {"index": 1,  "thai": "ฉลู",    "animal": "ฉลู",   "animal_en": "Ox",     "element": "earth",
     "thai_element": "ดิน"},
    {"index": 2,  "thai": "ขาล",    "animal": "ขาล",   "animal_en": "Tiger",  "element": "wood",
     "thai_element": "ไม้"},
    {"index": 3,  "thai": "เถาะ",   "animal": "เถาะ",  "animal_en": "Rabbit", "element": "wood",
     "thai_element": "ไม้"},
    {"index": 4,  "thai": "มะโรง", "animal": "มะโรง", "animal_en": "Dragon", "element": "earth",
     "thai_element": "ดิน"},
    {"index": 5,  "thai": "มะเส็ง", "animal": "มะเส็ง", "animal_en": "Snake",  "element": "fire",
     "thai_element": "ไฟ"},
    {"index": 6,  "thai": "มะเมีย", "animal": "มะเมีย", "animal_en": "Horse",  "element": "fire",
     "thai_element": "ไฟ"},
    {"index": 7,  "thai": "มะแม",   "animal": "มะแม",  "animal_en": "Goat",   "element": "earth",
     "thai_element": "ดิน"},
    {"index": 8,  "thai": "วอก",    "animal": "วอก",   "animal_en": "Monkey", "element": "metal",
     "thai_element": "โลหะ"},
    {"index": 9,  "thai": "ระกา",   "animal": "ระกา",  "animal_en": "Rooster","element": "metal",
     "thai_element": "โลหะ"},
    {"index": 10, "thai": "จอ",     "animal": "จอ",    "animal_en": "Dog",    "element": "earth",
     "thai_element": "ดิน"},
    {"index": 11, "thai": "กุน",    "animal": "กุน",   "animal_en": "Pig",    "element": "water",
     "thai_element": "น้ำ"},
]

WU_XING: dict[str, dict] = {
    "wood":  {"thai": "ไม้",  "color": "เขียว",
              "season": "ฤดูใบไม้ผลิ", "nature": "การเจริญเติบโต ความคิดสร้างสรรค์"},
    "fire":  {"thai": "ไฟ",   "color": "แดง",
              "season": "ฤดูร้อน",   "nature": "พลังงาน ความหลงใหล การแสดงออก"},
    "earth": {"thai": "ดิน",  "color": "เหลือง",
              "season": "ฤดูเก็บเกี่ยว", "nature": "ความมั่นคง ความน่าเชื่อถือ การเลี้ยงดู"},
    "metal": {"thai": "โลหะ", "color": "ขาว",
              "season": "ฤดูใบไม้ร่วง", "nature": "ความแข็งแกร่ง ความยุติธรรม ความชัดเจน"},
    "water": {"thai": "น้ำ",  "color": "ดำ",
              "season": "ฤดูหนาว",   "nature": "ความลึกซึ้ง สติปัญญา ความยืดหยุ่น"},
}

ELEMENT_NAMES: list[str] = ["wood", "fire", "earth", "metal", "water"]

_DOMAIN: dict[str, str] = {
    "wood":  "การเจริญเติบโต ความคิดสร้างสรรค์",
    "fire":  "พลังงาน ความหลงใหล การแสดงออก",
    "earth": "ความมั่นคง ความน่าเชื่อถือ การเลี้ยงดู",
    "metal": "ความแข็งแกร่ง ความยุติธรรม ความชัดเจน",
    "water": "ความลึกซึ้ง สติปัญญา ความยืดหยุ่น",
}

# ── จุดอ้างอิงของระบบหกสิบปี ──────────────────────────────────────
# วันกั่วชวด (ดัชนี 0) ตรงกับ JDN 2445730
_JDN_REF = 2445730
_OFFSET_1984 = 0


# ── ฟังก์ชันช่วย ─────────────────────────────────────────────────

def _jdn(d: _date) -> int:
    """เลขจูเลียนเดย์ (เที่ยงวัน) จากวันที่เกรกอเรียน"""
    y, m, d_ = d.year, d.month, d.day
    if m <= 2:
        y -= 1
        m += 12
    A = y // 100
    B = 2 - A + A // 4
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d_ + B - 1524


def _year_pillar(d: _date) -> int:
    """ดัชนีหกสิบปีของเสาปี (เปลี่ยนตรงวันตรุษ ≈ 4 กุมภาพันธ์)"""
    year = d.year
    if d.month < 2 or (d.month == 2 and d.day < 4):
        year -= 1
    return (year - 1984) % 60


def _month_pillar(d: _date) -> int:
    """ดัชนีหกสิบปีของเสาเดือน

    ใช้ระบบเดือนตามจุดเปลี่ยนฤดู: เดือน 1 (ขาล) เริ่ม ≈ 4 กุมภาพันธ์
    ฟ้าปีของเดือน 1 คำนวณจากฟ้าปีของปี ตามกฎ กั่วกี → เปงขาล
    """
    year = d.year
    if d.month < 2 or (d.month == 2 and d.day < 4):
        year -= 1

    year_stem = (year - 4) % 10
    # ฟ้าปีของเดือน 1 = (2 × ฟ้าปีปี + 2) mod 10
    month1_stem = (2 * year_stem + 2) % 10

    # แผนที่วันที่เกรกอเรียน → จำนวนเดือนจีน (0-11) ตามจุดเปลี่ยนฤดู
    # แต่ละแถว: (เดือนเกรกอเรียน, วัน, จำนวนเดือนจีน)
    # เดือน 1 (ขาล) เริ่มตรงวันลี่ชุน ≈ 4 กุมภาพันธ์
    boundaries = [
        (2, 4, 0),   # 4 ก.พ.+ → เดือน 1  ขาล
        (3, 5, 1),   # 5 มี.ค.+ → เดือน 2  เถาะ
        (4, 4, 2),   # 4 เม.ย.+ → เดือน 3  มะโรง
        (5, 5, 3),   # 5 พ.ค.+ → เดือน 4  มะเส็ง
        (6, 5, 4),   # 5 มิ.ย.+ → เดือน 5  มะเมีย
        (7, 6, 5),   # 6 ก.ค.+ → เดือน 6  มะแม
        (8, 7, 6),   # 7 ส.ค.+ → เดือน 7  วอก
        (9, 7, 7),   # 7 ก.ย.+ → เดือน 8  ระกา
        (10, 8, 8),  # 8 ต.ค.+ → เดือน 9  จอ
        (11, 7, 9),  # 7 พ.ย.+ → เดือน 10 กุน
        (12, 6, 10), # 6 ธ.ค.+ → เดือน 11 ชวด
        (1, 6, 11),  # 6 ม.ค.+ → เดือน 12 ฉลู
    ]

    offset = 11  # ก่อน 4 ก.พ. → เดือน 12 ของปีก่อน
    for bm, bd, month_offset in boundaries:
        if d.month == bm and d.day >= bd:
            offset = month_offset
            break
        elif d.month == bm and d.day < bd:
            break

    # หาดัชนีหกสิบปีของเดือน 1: i mod 10 == month1_stem, i mod 12 == 2
    month1_idx = next(
        i for i in range(60) if i % 10 == month1_stem and i % 12 == 2
    )
    return (month1_idx + offset) % 60


def _day_pillar(d: _date) -> int:
    """ดัชนีหกสิบปีของเสาวัน (เที่ยงวัน ตามเลขจูเลียน)"""
    return (_jdn(d) - _JDN_REF + _OFFSET_1984) % 60


def _hour_pillar(day_stem_idx: int, t: _time) -> int:
    """ดัชนีหกสิบปีของเสาชั่วโมง

    ระบบยาม: 23:00-00:59 = ยามที่ 0,
    01:00-02:59 = ยามที่ 1 ฯลฯ
    ฟ้าปีแรกของยามในวันหนึ่ง = (2 × ฟ้าปีวัน + 2) mod 10
    """
    h = t.hour
    hour_idx = (h + 1) % 24 // 2  # 23→0, 0→0, 1→1, …, 23→11
    hour_stem_start = (2 * day_stem_idx + 2) % 10
    stem = (hour_stem_start + hour_idx) % 10
    branch = hour_idx % 12
    return (stem * 12 + branch) % 60


def _pillar_label(idx: int) -> dict:
    """สร้างข้อมูลเสาหนึ่งจากดัชนีหกสิบปี"""
    stem_idx = idx % 10
    branch_idx = idx % 12
    stem = HEAVENLY_STEMS[stem_idx]
    branch = EARTHLY_BRANCHES[branch_idx]
    return {
        "sexagenary_index": idx,
        "stem": stem,
        "branch": branch,
        "label_th": f"{stem['thai']}{branch['thai']}",
        "label_en": f"{stem['name']}-{branch['animal_en']}",
    }


# ── API สาธารณะ ──────────────────────────────────────────────────

def compute_bazi(d: _date, t: _time) -> dict:
    """คำนวณสี่เสา (BaZi) และถ่วงน้ำหนักธาตุทั้งห้า"""
    year_idx = _year_pillar(d)
    month_idx = _month_pillar(d)
    day_idx = _day_pillar(d)
    day_stem_idx = day_idx % 10
    hour_idx = _hour_pillar(day_stem_idx, t)

    pillars = {
        "year":  _pillar_label(year_idx),
        "month": _pillar_label(month_idx),
        "day":   _pillar_label(day_idx),
        "hour":  _pillar_label(hour_idx),
    }

    # ── ถ่วงน้ำหนักธาตุ ────────────────────────────────────────
    counts: dict[str, int] = {e: 0 for e in ELEMENT_NAMES}
    yin_yang: dict[str, int] = {"yang": 0, "yin": 0}

    # ฟ้าปี (4 เสา × 1 ฟ้าปีแต่ละอัน)
    for key in ("year", "month", "day", "hour"):
        stem = pillars[key]["stem"]
        counts[stem["element"]] += 1
        yin_yang[stem["polarity"]] += 1

    # ดินเสมอ (4 เสา × 1 ตัว)
    for key in ("year", "month", "day", "hour"):
        branch = pillars[key]["branch"]
        counts[branch["element"]] += 1
        # หยิน/หยางของดินเสมอ: คู่ = หยาง, คี่ = หยิน
        branch_polarity = "yang" if branch["index"] % 2 == 0 else "yin"
        yin_yang[branch_polarity] += 1

    total = sum(counts.values()) or 1
    percent = {e: round(counts[e] / total * 100, 1) for e in ELEMENT_NAMES}
    ranked = sorted(ELEMENT_NAMES, key=lambda e: counts[e], reverse=True)
    dominant, lacking = ranked[0], ranked[-1]

    day_master = pillars["day"]["stem"]

    note = (
        f"ธาตุเด่นในดวง {day_master['thai']}{pillars['day']['branch']['thai']} "
        f"คือ {WU_XING[dominant]['thai']} "
        f"({dominant} — {_DOMAIN[dominant]}) "
        f"ส่วนธาตุที่ขาดแคลนคือ {WU_XING[lacking]['thai']} "
        f"({lacking} — {_DOMAIN[lacking]})"
    )

    return {
        "pillars": pillars,
        "element_balance": {
            "counts": counts,
            "percent": percent,
            "dominant": dominant,
            "lacking": lacking,
        },
        "yin_yang_balance": yin_yang,
        "day_master": {
            "stem": day_master,
            "note": (
                f"วันเกิดของคุณคือ {day_master['thai']}{pillars['day']['branch']['thai']} "
                f"ซึ่งมีธาตุ{day_master['thai_element']}"
            ),
        },
        "note": note,
    }


def get_zodiac(year: int) -> dict:
    """หานักษัตรประจำปีเกิด

    ใช้ระบบง่ายๆ แบบเดียวกับหน้าเว็บ: วัฏจักร 12 ปี มังกร = ปี 2024
    """
    animal_idx = (year - 4) % 12
    animal = EARTHLY_BRANCHES[animal_idx]
    buddhist_year = year + 543

    lucky_elements = {
        "wood": ["water", "wood"],   "fire": ["wood", "fire"],
        "earth": ["fire", "earth"],  "metal": ["earth", "metal"],
        "water": ["metal", "water"],
    }

    return {
        "animal_th": animal["animal"],
        "animal_en": animal["animal_en"],
        "animal_thai_name": animal["thai"],
        "element": animal["element"],
        "thai_element": animal["thai_element"],
        "year": year,
        "buddhist_year": buddhist_year,
        "lucky_elements": lucky_elements.get(animal["element"], []),
        "note": (
            f"ปี{animal['animal']} ({animal['animal_en']}) "
            f"ธาตุ{animal['thai_element']} — "
            f"{buddhist_year} พ.ศ."
        ),
    }


def compute_element_analysis(d: _date, t: _time) -> dict:
    """วิเคราะห์ธาตุทั้งห้า จากรายละเอียดสี่เสา"""
    bazi = compute_bazi(d, t)
    eb = bazi["element_balance"]

    breakdown: dict[str, dict] = {}
    for el in ELEMENT_NAMES:
        wu = WU_XING[el]
        breakdown[el] = {
            "thai": wu["thai"],
            "count": eb["counts"][el],
            "percent": eb["percent"][el],
            "color": wu["color"],
            "season": wu["season"],
            "nature": wu["nature"],
        }

    return {
        "breakdown": breakdown,
        "dominant": eb["dominant"],
        "lacking": eb["lacking"],
        "yin_yang_balance": bazi["yin_yang_balance"],
        "day_master": bazi["day_master"],
        "note": (
            f"ธาตุทั้ง 5 ในดวงชะตาของคุณ: "
            f"เด่นคือ {WU_XING[eb['dominant']]['thai']} "
            f"({_DOMAIN[eb['dominant']]}) "
            f"ขาดคือ {WU_XING[eb['lacking']]['thai']} "
            f"({_DOMAIN[eb['lacking']]})"
        ),
    }
