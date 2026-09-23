"""Nine Star Ki (九星気学) — engine spec C:/AI/research-astrology/13.

Year Star only is computable in v1: spec code path
``(11 - (year % 9)) % 9 or 9`` with the LiChun Feb-4 cutoff (born earlier →
use year − 1), supported domain years ≥ 1900.

⚠️ The spec §1 constant dispute stays OPEN [VERIFY]: the alternative
published convention ``(y + 7) % 9`` yields a different star (1997 → 6 vs 3).
Per QA note (a)/(c) we keep the spec's current code path, carry the flag in
the output, and NEVER silently pick a side. Month Star / Day Star offsets
are likewise unpinned → those parts degrade to ``constant_unpinned:<star>``.

Ground truth (M, born 1997-05-19, after LiChun): 1997 % 9 = 8 →
(11 − 8) % 9 = Year Star 3 · Three Blue · Wood · Zhen/East.
"""

from __future__ import annotations

from datetime import date as date_type, datetime, timezone

_LICHUN = (2, 4)

# Spec §3 meaning matrix (star → color/element/trigram-palace/core TH/EN).
STAR_TABLE: dict[int, dict[str, str]] = {
    1: {"color": "White", "element": "Water", "palace": "Kan/North",
        "core_en": "adaptable depth", "core_th": "ลึกลับ ปรับตัวเก่ง"},
    2: {"color": "Black", "element": "Earth", "palace": "Kun/Southwest",
        "core_en": "nurturing supporter", "core_th": "ผู้ดูแล อดทน"},
    3: {"color": "Blue", "element": "Wood", "palace": "Zhen/East",
        "core_en": "bold initiator", "core_th": "ทะเยอทะยาน ตรงไป"},
    4: {"color": "Green", "element": "Wood", "palace": "Xun/Southeast",
        "core_en": "networker-craftsman", "core_th": "สื่อสาร มือทอง"},
    5: {"color": "Yellow", "element": "Earth", "palace": "Center",
        "core_en": "controller-core (kingly)", "core_th": "ผู้ควบคุม พลังกลาง"},
    6: {"color": "White", "element": "Metal", "palace": "Qian/Northwest",
        "core_en": "leader-duty", "core_th": "ผู้นำ หน้าที่"},
    7: {"color": "Red", "element": "Metal", "palace": "Dui/West",
        "core_en": "joy-pleasure seeker", "core_th": "รื่นเริง ติดใจ"},
    8: {"color": "White", "element": "Earth", "palace": "Gen/Northeast",
        "core_en": "steady accumulator", "core_th": "มั่นคง สะสม"},
    9: {"color": "Purple", "element": "Fire", "palace": "Li/South",
        "core_en": "radiant-visionary", "core_th": "เปล่งประกาย สายตาคม"},
}

_NUMERAL = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
            6: "Six", 7: "Seven", 8: "Eight", 9: "Nine"}

_VERIFY_NOTE = (
    "[VERIFY] constant dispute OPEN: alternative published convention "
    "(y + 7) % 9 gives a different star — pin two known-person honke "
    "examples before hardcoding (QA 2026-08-23 note a)"
)


def year_star(year: int, month: int | None = None, day: int | None = None) -> int:
    """Spec code path with LiChun Feb-4 cutoff."""
    y = year
    if month is not None and day is not None and (month, day) < _LICHUN:
        y -= 1
    return (11 - (y % 9)) % 9 or 9


def compute_ninestar_ki(birth_date: date_type | str | None) -> dict:
    """Year Star block real; Month/Day stars degrade to unpinned constants."""
    if birth_date is None or (isinstance(birth_date, str) and not birth_date.strip()):
        return {"status": "unavailable", "reason": "missing_birth_date"}
    try:
        bd = (
            birth_date
            if isinstance(birth_date, date_type)
            else date_type.fromisoformat(str(birth_date)[:10])
        )
    except ValueError:
        return {"status": "unavailable", "reason": "invalid_birth_date"}

    if bd.year < 1900:
        return {"status": "unavailable", "reason": "year_out_of_supported_range"}

    n = year_star(bd.year, bd.month, bd.day)
    row = STAR_TABLE[n]
    return {
        "status": "ok",
        "system": "nine_star_ki_v1",
        "year_star": {
            "star": n,
            "name_en": f"{_NUMERAL[n]} {row['color']} {row['element']}",
            "name_th": f"ดาว {_NUMERAL[n]} {row['color']} ธาตุ{row['element']}",
            "color": row["color"],
            "element": row["element"],
            "palace": row["palace"],
            "core_en": row["core_en"],
            "core_th": row["core_th"],
            "lichun_cutoff": "Feb 4 (born earlier → prior year's star)",
            "verify_flag": _VERIFY_NOTE,
        },
        "month_star": {"status": "unavailable", "reason": "constant_unpinned:month"},
        "day_star": {"status": "unavailable", "reason": "constant_unpinned:day"},
        "notes": [
            "Month Star ((year_star − month_index) mod 9) and Day Star "
            "((JDN + offset) mod 9) offsets remain unpinned [VERIFY] — "
            "never silently picked (QA 2026-08-23 notes a/c)",
        ],
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }
