"""Zi Wei Dou Shu (紫微斗數) — minimal REAL computation via ``lunar-python``.

Scope pinned to what lunar-python supports deterministically (Universe Phase
2 mission order — explicitly NO full 14-star chart):

1. True lunar calendar conversion (solar → lunar month/day/year ganzhi,
   leap-month aware) via ``Solar.fromYmdHms(...).getLunar()``.
2. Life Palace 命宮 & Body Palace 身宮 from lunar month + hour branch
   (spec C:/AI/research-astrology/05 §1, counting Yin 寅=0):
       life_palace = ((lunar_month − 1) + (12 − hour_branch)) mod 12
       body_palace = ((lunar_month − 1) +  hour_branch     ) mod 12
   Test case (owner 1997-05-19 05:45 ICT): lunar month 4, hour 卯(3)
   → life = (3+9)%12 = 0 → 寅 ; body = (3+3)%12 = 6 → 申.
3. Life-Palace heavenly stem via the 五虎遁 rule (year stem fixes the stem
   of 寅; the palace stem advances from there).
4. Sui Po 歲破 (Year Breaker) + flow-year palace 流年 for requested years:
   the year branch comes from lunar-python; Sui Po is the branch opposite
   Tai Sui (2026 丙午 → 子/Rat, 2027 丁未 → 丑/Ox).

The old scaffold's fabricated star placements / brightness tables were
removed — this module never invents stars it cannot derive.
"""

from __future__ import annotations

from datetime import date as date_type, time as time_type

from lunar_python import Solar

# Earthly Branches in canonical order (index used for hour/zhi lookups).
ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ZHI_ANIMAL = {
    "子": "Rat", "丑": "Ox", "寅": "Tiger", "卯": "Rabbit",
    "辰": "Dragon", "巳": "Snake", "午": "Horse", "未": "Goat",
    "申": "Monkey", "酉": "Rooster", "戌": "Dog", "亥": "Pig",
}
STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# Palaces laid out from Yin 寅=0 (spec 05 §1 counting base): index → branch.
_FROM_YIN = [ZHI[(2 + i) % 12] for i in range(12)]

# 12 Palaces, canonical order away from the Life Palace (counterclockwise /
# reverse-zodiacal placement on the chart wheel).
PALACE_NAMES_CN = ["命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
                   "遷移宮", "奴僕宮", "官祿宮", "田宅宮", "福德宮", "父母宮"]
PALACE_NAMES_EN = ["Life", "Siblings", "Spouse", "Children", "Wealth", "Health",
                   "Travel", "Friends", "Career", "Property", "Mental/Virtue", "Parents"]

_STEM_IDX = {s: i for i, s in enumerate(STEMS)}
_ZHI_IDX = {z: i for i, z in enumerate(ZHI)}


def _yin_stem_for_year(year_stem: str) -> str:
    """五虎遁: first-day stem of 寅 for a given year stem.

    甲己→丙, 乙庚→戊, 丙辛→庚, 丁壬→壬, 戊癸→甲.
    """
    y = _STEM_IDX[year_stem[0]]
    return STEMS[(y % 5) * 2 + 2]


def _lunar_parts(birth_date: date_type, birth_time: time_type) -> dict:
    solar = Solar.fromYmdHms(
        birth_date.year, birth_date.month, birth_date.day,
        birth_time.hour, birth_time.minute, birth_time.second,
    )
    lunar = solar.getLunar()
    raw_month = lunar.getMonth()
    return {
        "year_ganzhi": lunar.getYearInGanZhi(),
        "month": abs(raw_month),
        "day": lunar.getDay(),
        "is_leap_month": raw_month < 0,
        "hour_zhi": lunar.getTimeZhi(),
        "hour_branch_idx": _ZHI_IDX[lunar.getTimeZhi()],
        "year_stem": lunar.getYearInGanZhi()[0],
    }


def compute_life_body_palaces(birth_date: date_type, birth_time: time_type) -> dict:
    """Real Life/Body Palace derivation from lunar month + hour branch."""
    lp = _lunar_parts(birth_date, birth_time)
    hb = lp["hour_branch_idx"]
    m = lp["month"] - 1

    life_idx = (m + (12 - hb)) % 12          # spec 05 §1, Yin 寅=0
    body_idx = (m + hb) % 12

    life_branch = _FROM_YIN[life_idx]
    body_branch = _FROM_YIN[body_idx]

    # 五虎遁 stems: 寅 gets the year-derived stem, advancing one stem per
    # branch step from 寅 (only the 6 branches 寅..丑 reachable here map
    # forward through the cycle).
    yin_stem = _yin_stem_for_year(lp["year_stem"])
    yin_s, life_off = _STEM_IDX[yin_stem], (_ZHI_IDX[life_branch] - 2) % 12
    life_stem = STEMS[(yin_s + life_off) % 10]
    body_off = (_ZHI_IDX[body_branch] - 2) % 12
    body_stem = STEMS[(yin_s + body_off) % 10]

    return {
        "lunar": lp,
        "life_palace": {
            "branch": life_branch,
            "animal": ZHI_ANIMAL[life_branch],
            "stem": life_stem,
            "pillar": f"{life_stem}{life_branch}",
            "count_from_yin": life_idx,
        },
        "body_palace": {
            "branch": body_branch,
            "animal": ZHI_ANIMAL[body_branch],
            "stem": body_stem,
            "pillar": f"{body_stem}{body_branch}",
            "count_from_yin": body_idx,
        },
    }


def palace_wheel(life_branch: str) -> list[dict]:
    """The 12 palaces placed reverse-zodiacally starting from the Life Palace."""
    start = _ZHI_IDX[life_branch]
    return [
        {
            "name_cn": PALACE_NAMES_CN[i],
            "name_en": PALACE_NAMES_EN[i],
            "branch": ZHI[(start - i) % 12],
            "animal": ZHI_ANIMAL[ZHI[(start - i) % 12]],
        }
        for i in range(12)
    ]


def year_info(year: int) -> dict:
    """Ganzhi / Tai-Sui branch / Sui Po 歲破 / flow-year palace for `year`.

    Sampled safely inside the year (June) so the Lichun vs Lunar-New-Year
    boundary question never matters. Sui Po = branch opposite Tai Sui —
    the direction/branch "broken" that year.
    """
    gz = Solar.fromYmd(year, 6, 1).getLunar().getYearInGanZhi()
    year_branch = gz[1]
    idx = _ZHI_IDX[year_branch]
    sui_po_branch = ZHI[(idx + 6) % 12]
    return {
        "year": year,
        "ganzhi": gz,
        "tai_sui_branch": year_branch,
        "flow_year_palace_branch": year_branch,
        "sui_po_branch": sui_po_branch,
        "sui_po_animal": ZHI_ANIMAL[sui_po_branch],
        "note": "歲破 = branch clashing Tai Sui; avoid major groundbreaking/moves on its sector in folk practice",
    }


def compute_ziwei(
    birth_date: date_type,
    birth_time: time_type,
    annual_years: list[int] | None = None,
) -> dict:
    """Main entry point: lunar conversion + Life/Body palaces (+ optional annual layer)."""
    base = compute_life_body_palaces(birth_date, birth_time)

    result = {
        "status": "ok",
        "scope_note": (
            "minimal real computation — lunar calendar, Life/Body Palace, "
            "Sui Po; no 14-main-star chart (out of phase-2 scope)"
        ),
        "lunar": base["lunar"],
        "life_palace": base["life_palace"],
        "body_palace": base["body_palace"],
        "palace_wheel": palace_wheel(base["life_palace"]["branch"]),
        "annual": {},
    }
    for y in annual_years or []:
        result["annual"][str(y)] = year_info(y)
    return result


def ziwei_summary(zw: dict) -> dict:
    """Compact highlights for grand-fusion composition."""
    life, body = zw["life_palace"], zw["body_palace"]
    key = {}
    for p in zw.get("palace_wheel", []):
        if p["name_en"] in ("Life", "Career", "Wealth", "Spouse"):
            key[p["name_en"]] = p["branch"]
    return {
        "life_pillar": life["pillar"],
        "body_branch": body["branch"],
        "key_palaces": key,
        "annual": {y: v["ganzhi"] for y, v in zw.get("annual", {}).items()},
    }
