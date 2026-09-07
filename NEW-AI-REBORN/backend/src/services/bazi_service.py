"""BaZi (four-pillar) engine — pure Python, no new dependencies.

Implements spec 04 (research-astrology/04-thai-bazi-engine-spec.md) with
direct JDN arithmetic.  All ground truths below are machine-verified in
tests/test_bazi.py:

  1997-05-19 05:45 ICT -> 丁丑 乙巳 辛酉 辛卯  (day master 辛, ฉลูไฟ)
  2001-08-18 22:32 ICT -> 辛巳 丙申 癸丑 癸亥  (day master 癸)

Confidence: pillars/clash/harm HIGH; MONTH pillar MEDIUM (fixed-date solar
term approximation — real terms drift ±1 day around the anchor dates).

Formulas
--------
JDN      standard Gregorian JDN (integer, Fliegel-Van Flandern).
YEAR     Lichun cutoff ≈ Feb 4; index = (adjusted_year - 4) % 60.
MONTH    fixed-date solar-term table; stem via 五虎遁 from the adjusted
         (post-Lichun) year stem, anchored at the 寅 month.
DAY      day_pillar_index = (JDN + 49) % 60   (constant verified on 2 charts).
HOUR     2-hour branch = ((hh + 1) // 2) % 12; stem via 五鼠遁 from the day
         stem (23:00+ = late 子 hour: stem taken from the NEXT day's stem).
"""

from __future__ import annotations

from datetime import date as date_type, time as time_type

STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

STEM_ELEMENT_EN = ["wood", "wood", "fire", "fire", "earth", "earth", "metal", "metal", "water", "water"]
STEM_ELEMENT_TH = ["ไม้", "ไม้", "ไฟ", "ไฟ", "ดิน", "ดิน", "โลหะ", "โลหะ", "น้ำ", "น้ำ"]
BRANCH_ANIMAL_TH = [
    "หนู(ชวด)", "วัว(ฉลู)", "เสือ(ขาล)", "กระต่าย(เถาะ)", "มังกร(มะโรง)", "งู(มะเส็ง)",
    "ม้า(มะเมีย)", "แพะ(มะแม)", "ลิง(วอก)", "ไก่(มะเสียง)", "หมา(จอ)", "หมู(กุน)",
]
BRANCH_ANIMAL_EN = [
    "Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
    "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig",
]

# Fixed-date solar-term anchors (month starts).  (month, day, branch_index).
# branch_index follows BRANCHES: 寅=2 … 丑=1.
_SOLAR_TERMS = [
    (2, 4, 2),   # 立春 Lichun   -> 寅
    (3, 6, 3),   # 惊蛰          -> 卯
    (4, 5, 4),   # 清明          -> 辰
    (5, 5, 5),   # 立夏 Lixia    -> 巳
    (6, 6, 6),   # 芒种          -> 午
    (7, 7, 7),   # 小暑          -> 未
    (8, 7, 8),   # 立秋 Liqiu    -> 申
    (9, 7, 9),   # 白露          -> 酉
    (10, 8, 10),  # 寒露          -> 戌
    (11, 7, 11),  # 立冬          -> 亥
    (12, 7, 0),  # 大雪          -> 子
]
_LICHUN = (2, 4)

# ชง CLASH (six pairs of branches 6 apart) and หาย HARM, spec 04 §3.
CLASH_PAIRS = {frozenset((i, (i + 6) % 12)) for i in range(6)}
HARM_PAIRS = {frozenset(p) for p in ((0, 11), (1, 6), (2, 5), (3, 4), (8, 11), (9, 10))}


def jdn(y: int, m: int, d: int) -> int:
    """Julian Day Number of a Gregorian calendar date (Fliegel-Van Flandern)."""
    a = (14 - m) // 12
    yy = y + 4800 - a
    mm = m + 12 * a - 3
    return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045


def pillar_from_index(i: int) -> dict:
    i %= 60
    s, b = i % 10, i % 12
    return {
        "index": i,
        "stem": STEMS[s],
        "branch": BRANCHES[b],
        "pillar": STEMS[s] + BRANCHES[b],
        "stem_element_en": STEM_ELEMENT_EN[s],
        "stem_element_th": STEM_ELEMENT_TH[s],
        "polarity": "yang" if s % 2 == 0 else "yin",
        "animal_th": BRANCH_ANIMAL_TH[b],
        "animal_en": BRANCH_ANIMAL_EN[b],
    }


def _adjusted_year(d: date_type) -> tuple[int, bool]:
    """BaZi year (Lichun cutoff) and whether the date sits near the cutoff.

    Lichun is *approximately* Feb 4 but drifts between Feb 3-5 depending on
    the year (e.g. 2017 & 2021: Feb 3; 2026: Feb 4). A fixed-date cutoff
    cannot resolve dates in that window, so they carry MEDIUM confidence
    until the exact solar-term instant is computed.

    Here we treat ±3 days around Feb 4 (Feb 1-7) as near-cutoff.
    """
    adj = d.year if (d.month, d.day) >= _LICHUN else d.year - 1
    # near = ±3 days around Feb 4 → Feb 1,2,3,4,5,6,7
    near = d.month == 2 and 1 <= d.day <= 7
    return adj, near


def year_pillar(d: date_type) -> dict:
    adj, near = _adjusted_year(d)
    p = pillar_from_index((adj - 4) % 60)
    p["confidence"] = "MEDIUM" if near else "HIGH"
    p["adjusted_year"] = adj
    return p


def month_pillar(d: date_type) -> dict:
    adj, _ = _adjusted_year(d)
    year_stem = (adj - 4) % 10
    # 五虎遁: month stem of the 寅 month from the year stem.
    tiger_stem = (2 + 2 * (year_stem % 5)) % 10

    branch_idx = None
    for m, day, bidx in _SOLAR_TERMS:
        if (d.month, d.day) >= (m, day):
            branch_idx = bidx
    if branch_idx is None:  # Jan 1–5: still the 子 month opened by 大雪 (Dec 7)
        branch_idx = 0

    offset = (branch_idx - 2) % 12
    stem_idx = (tiger_stem + offset) % 10
    p = pillar_from_index(_sexagenary_index(stem_idx, branch_idx))
    p["confidence"] = "MEDIUM"  # fixed-date solar-term approximation
    p["solar_term_approx"] = True
    return p


def _sexagenary_index(stem_idx: int, branch_idx: int) -> int:
    """Index in the 60-cycle for a stem/branch pair of matching parity."""
    for i in range(60):
        if i % 10 == stem_idx and i % 12 == branch_idx:
            return i
    raise ValueError(f"invalid stem/branch pair: {stem_idx}/{branch_idx}")


def day_pillar(d: date_type) -> dict:
    p = pillar_from_index((jdn(d.year, d.month, d.day) + 49) % 60)
    p["confidence"] = "HIGH"
    return p


def hour_pillar(day_stem_idx: int, t: time_type) -> dict:
    late_zi = t.hour >= 23
    eff_stem = (day_stem_idx + 1) % 10 if late_zi else day_stem_idx
    branch_idx = ((t.hour + 1) // 2) % 12
    # 五鼠遁: hour stem of the 子 hour from the (effective) day stem.
    rat_stem = (2 * (eff_stem % 5)) % 10
    stem_idx = (rat_stem + branch_idx) % 10
    p = pillar_from_index(_sexagenary_index(stem_idx, branch_idx))
    p["confidence"] = "HIGH"
    p["late_zi"] = late_zi
    return p


def four_pillars(d: date_type, t: time_type) -> dict:
    year = year_pillar(d)
    month = month_pillar(d)
    day = day_pillar(d)
    hour = hour_pillar(STEMS.index(day["stem"]), t)
    dm = day["stem"]
    dm_idx = STEMS.index(dm)
    return {
        "pillars": {"year": year, "month": month, "day": day, "hour": hour},
        "jdn": jdn(d.year, d.month, d.day),
        "day_master": {
            "stem": dm,
            "element_en": STEM_ELEMENT_EN[dm_idx],
            "element_th": STEM_ELEMENT_TH[dm_idx],
            "polarity": "yang" if dm_idx % 2 == 0 else "yin",
            "label_th": f"{STEM_ELEMENT_TH[dm_idx]}{'หยิน' if dm_idx % 2 else 'หยาง'}",
        },
        "zodiac_th": year["animal_th"],
        "zodiac_en": year["animal_en"],
        "confidence": {
            "year": year["confidence"],
            "month": month["confidence"],
            "day": day["confidence"],
            "hour": hour["confidence"],
        },
    }


def branch_relation(branch_a: int, branch_b: int) -> str | None:
    pair = frozenset((branch_a, branch_b))
    if pair in CLASH_PAIRS:
        return "clash"
    if pair in HARM_PAIRS:
        return "harm"
    return None


def yearly_relations(d: date_type, years: list[int]) -> dict:
    """Spec 04 §3 generator: ชง/หาย of the birth YEAR branch vs target years."""
    birth = year_pillar(d)
    b_idx = BRANCHES.index(birth["branch"])
    items = []
    for y in years:
        idx = (y - 4) % 60
        s, b = idx % 10, idx % 12
        rel = branch_relation(b_idx, b)
        rel_th = {"clash": "ชง", "harm": "หาย", None: "ปกติ"}[rel]
        items.append({
            "year": y,
            "stem": STEMS[s],
            "branch": BRANCHES[b],
            "pillar": STEMS[s] + BRANCHES[b],
            "animal_th": BRANCH_ANIMAL_TH[b],
            "relation": rel,
            "relation_th": rel_th,
            "pair": birth["branch"] + BRANCHES[b],
            "en": f"{birth['animal_en']}-{rel or 'neutral'}-{BRANCH_ANIMAL_EN[b]}",
        })
    items.sort(key=lambda x: x["year"])
    return {
        "birth_year_pillar": birth["pillar"],
        "birth_branch": birth["branch"],
        "zodiac_th": birth["animal_th"],
        "years": items,
    }
