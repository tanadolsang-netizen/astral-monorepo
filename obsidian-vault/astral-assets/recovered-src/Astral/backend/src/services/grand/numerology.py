"""Western Numerology — engine spec C:/AI/research-astrology/11.

Deterministic digit-reduction module. v1 convention (QA 2026-08-23 note a):
master numbers 11/22/33 are PRESERVED at any intermediate reduction step.
A bare mod-9 shortcut agrees only when no intermediate master appears and
must not be substituted blindly.

Ground truth (M, DOB 1997-05-19): raw digit sum 41 → Life Path 5 ·
Birth Day 19→10→1 · Personal Year 2026 = 7 · Personal Year 2027 = 8.

Expression / Soul Urge / Personality need the optional birth name; without
it the name-numbers block degrades to ``birth_name_not_provided`` by design
(spec: engine runs only if provided) — never fabricated.

Degradation contract: missing date → ``missing_birth_date``; unparsable
date → ``invalid_birth_date``; module never raises, never invents numbers.
"""

from __future__ import annotations

from datetime import date as date_type

_MASTERS = {11, 22, 33}

# Pythagorean letter table (spec §1): A J S=1 · B K T=2 · C L U=3 · D M V=4
# E N W=5 · F O X=6 · G P Y=7 · H Q Z=8 · I R=9
_PYTHAGOREAN: dict[str, int] = {}
for _letters, _val in (
    ("AJS", 1), ("BKT", 2), ("CLU", 3), ("DMV", 4), ("ENW", 5),
    ("FOX", 6), ("GPY", 7), ("HQZ", 8), ("IR", 9),
):
    for _ch in _letters:
        _PYTHAGOREAN[_ch] = _val

_VOWELS = set("AEIOU")

# Meaning matrix, condensed TH/EN per number (spec §2).
MEANINGS: dict[int, dict[str, str]] = {
    1: {"core_en": "pioneer/initiator", "core_th": "ผู้บุกเบิก"},
    2: {"core_en": "diplomat/partner", "core_th": "นักการทูต/คู่หู"},
    3: {"core_en": "expressor/creator", "core_th": "ผู้สื่อสาร/ผู้สร้าง"},
    4: {"core_en": "builder/systems", "core_th": "นักสร้าง/ระบบ"},
    5: {"core_en": "freedom/senses", "core_th": "เสรีภาพ/ประสาทสัมผัส"},
    6: {"core_en": "caretaker/aesthetic", "core_th": "ผู้ดูแล/ศิลป์"},
    7: {"core_en": "analyst/mystic", "core_th": "นักวิเคราะห์/ลี้ลับ"},
    8: {"core_en": "executive/power", "core_th": "ผู้บริหาร/อำนาจ"},
    9: {"core_en": "humanitarian/closer", "core_th": "มนุษยธรรม/ปิดจบ"},
    11: {"core_en": "intuitive channel", "core_th": "ช่องทางสัญชาตญาณ (master)"},
    22: {"core_en": "master builder", "core_th": "สถาปนิกใหญ่ (master)"},
    33: {"core_en": "master teacher", "core_th": "ครูใหญ่ (master)"},
}


def _digit_sum(n: int) -> int:
    return sum(int(d) for d in str(n))


def reduce_number(n: int) -> int:
    """Digit-reduce preserving masters 11/22/33 at any intermediate step."""
    while n > 9 and n not in _MASTERS:
        n = _digit_sum(n)
    return n


def life_path_number(birth_date: date_type) -> tuple[int, int]:
    """(raw digit sum of YYYYMMDD, reduced Life Path)."""
    raw = _digit_sum(birth_date.year * 10000 + birth_date.month * 100 + birth_date.day)
    return raw, reduce_number(raw)


def birth_day_number(birth_date: date_type) -> int:
    return reduce_number(birth_date.day)


def personal_year_number(birth_date: date_type, year: int) -> int:
    """reduce(reduced(day) + month + digits(current year)) — QA note (a)."""
    return reduce_number(
        birth_day_number(birth_date)
        + reduce_number(birth_date.month)
        + reduce_number(_digit_sum(year))
    )


def _name_numbers(birth_name: str | None) -> dict:
    if not birth_name or not str(birth_name).strip():
        return {"status": "unavailable", "reason": "birth_name_not_provided"}
    letters = [ch.upper() for ch in str(birth_name) if ch.isalpha()]
    if not letters:
        return {"status": "unavailable", "reason": "birth_name_not_provided"}
    values = [_PYTHAGOREAN[ch] for ch in letters]
    total = sum(values)
    vowels = sum(v for ch, v in zip(letters, values) if ch in _VOWELS)
    return {
        "status": "ok",
        "expression": reduce_number(total),
        "soul_urge": reduce_number(vowels),
        "personality": reduce_number(total - vowels),
        "convention": "v1 master-preserving reduction",
    }


def _meaning(number: int) -> dict[str, str]:
    row = MEANINGS.get(number, {})
    return {
        "core_en": row.get("core_en", ""),
        "core_th": row.get("core_th", ""),
    }


def compute_numerology(
    birth_date: date_type | str | None,
    birth_name: str | None = None,
    years: list[int] | None = None,
) -> dict:
    """Life Path + Birth Day + Personal Years (+ optional name numbers).

    Deterministic; never raises. Missing/invalid inputs degrade per spec §QA-c.
    """
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

    from datetime import datetime, timezone

    targets = sorted(set(years)) if years else None

    lp_raw, lp_num = life_path_number(bd)
    bday = birth_day_number(bd)

    py_block: dict[str, dict] = {}
    if targets is None:
        now_year = datetime.now(timezone.utc).year
        targets = [now_year, now_year + 1]
    for y in targets:
        n = personal_year_number(bd, y)
        py_block[str(y)] = {"number": n, **_meaning(n)}

    return {
        "status": "ok",
        "system": "western_numerology_v1",
        "convention_note": (
            "digit-sum with masters 11/22/33 preserved at any intermediate "
            "step (mod-9 shortcut only agrees when no intermediate master)"
        ),
        "life_path": {"number": lp_num, "raw_digit_sum": lp_raw, **_meaning(lp_num)},
        "birth_day": {"number": bday, **_meaning(bday)},
        "personal_year": py_block,
        "name_numbers": _name_numbers(birth_name),
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }
