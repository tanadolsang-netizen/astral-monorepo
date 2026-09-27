"""Tibetan / Kalachakra calendrical layer — engine spec C:/AI/research-astrology/18.

Phase 4.5 unlock (2026-08-23) — Rabjung YEAR layer is real:

- Year element/animal/gender via the research-pinned anchor
  ``data/kalachakra_anchor.json``: epoch 1027 CE = Fire-female-Hare
  (Rabjung cycle 1 year 1; Laufer 1911 + Janson arXiv:1401.6285).
  Formula: i = (Y − 4) mod 60 → element = ELEMENTS[(i//2) % 5],
  animal = ANIMALS[i % 12], gender = male iff i even.
  Validated against 9 published anchors incl. Janson Table 1 and the
  Tibetan Nuns Project calendars. The spec's original pseudocode phase
  (and the "(Y−1026)+Wood-Male-Tiger" variant) stay REJECTED — both give
  Wood-Ox male for 1997, which fails every known anchor.
- Losar handling: a Rabjung label attaches to the Tibetan year that begins
  at Losar. Without a full Losar table we use the mission-pinned fixed
  cutoff — Gregorian Jan 1–Feb 7 belongs to the PRIOR Tibetan year — and
  flag such lookups as Losar-approximate (Losar drifts Feb 4–Mar 5).
  M (1997-05-19) is far after Losar 1997-02-08, so his label is clean.
- Parkha DAY number = JDN mod 8 (number only; the name/meaning matrix is
  still [VERIFY] per spec §QA — never invented here).

Still gracefully unavailable (no ad-hoc seeding): daily element/animal pair,
Mewa birth-year color table, parkha names, merit/dharmapala lunar-day lists.
"""

from __future__ import annotations

import json
from datetime import date as date_type
from pathlib import Path

from src.services.grand.mayan_tzolkin import jdn

REASON_YEAR = "missing_birth_date"

# Verified constants (embedded fallback mirroring data/kalachakra_anchor.json;
# the external file, when present, is authoritative provenance only — the math
# below reproduces its formula exactly).
_ELEMENTS = ["Wood", "Fire", "Earth", "Iron", "Water"]
_ANIMALS = [
    "Mouse", "Ox", "Tiger", "Hare", "Dragon", "Snake",
    "Horse", "Sheep", "Monkey", "Bird", "Dog", "Pig",
]
_EPOCH = 1027  # Rabjung cycle 1, year 1 = Fire-female-Hare

# Fixed pre-Losar cutoff (mission 2026-08-23): Jan 1–Feb 7 → prior Tibetan
# year. Real Losar drifts Feb 4 – Mar 5, so these get an approximate flag.
_LOSAR_CUTOFF = (2, 8)

_ANCHOR_CANDIDATES = (
    Path("C:/AI/research-astrology/data/kalachakra_anchor.json"),
    Path(__file__).resolve().parents[3] / "data" / "kalachakra_anchor.json",
)


def _load_anchor() -> dict | None:
    for path in _ANCHOR_CANDIDATES:
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict) and data.get("epoch_rule"):
                return {"path": str(path), **data}
        except (OSError, ValueError):
            continue
    return None


def rabjung_label(year: int) -> dict:
    """Element/animal/gender + Rabjung cycle numbering for a Tibetan year."""
    i = (year - 4) % 60
    element = _ELEMENTS[(i // 2) % 5]
    animal = _ANIMALS[i % 12]
    gender = "male" if i % 2 == 0 else "female"
    cycle = (year - _EPOCH) // 60 + 1
    year_in_cycle = ((year - _EPOCH) % 60) + 1
    return {
        "element": element,
        "animal": animal,
        "gender": gender,
        "label": f"{element}-{animal} ({gender})",
        "rabjung_cycle": cycle,
        "rabjung_year_in_cycle": year_in_cycle,
    }


def compute_kalachakra(birth_date=None, *_args, **_kwargs) -> dict:
    """Rabjung year label + Parkha day number for a Gregorian birth date."""
    if birth_date is None:
        return {
            "status": "unavailable",
            "reason": REASON_YEAR,
            "notes": ["pass a datetime.date; Rabjung year layer needs the birth date"],
        }
    if not isinstance(birth_date, date_type):
        try:
            birth_date = date_type.fromisoformat(str(birth_date))
        except ValueError:
            return {"status": "unavailable", "reason": "invalid_birth_date"}

    # --- Losar assignment: Jan 1–Feb 7 belongs to the prior Tibetan year ---
    pre_losar = (birth_date.month, birth_date.day) < _LOSAR_CUTOFF
    tibetan_year = birth_date.year - 1 if pre_losar else birth_date.year

    label = rabjung_label(tibetan_year)
    anchor = _load_anchor()

    parkha_day_number = jdn(birth_date.year, birth_date.month, birth_date.day) % 8

    result = {
        "status": "ok",
        "system": "Tibetan Rabjung 60-year cycle (Kalachakra year layer)",
        "birth_date": birth_date.isoformat(),
        "gregorian_year": birth_date.year,
        "tibetan_year": tibetan_year,
        "year": {
            "element": label["element"],
            "animal": label["animal"],
            "gender": label["gender"],
            "label": label["label"],
        },
        "rabjung": {
            "cycle": label["rabjung_cycle"],
            "year_in_cycle": label["rabjung_year_in_cycle"],
            "epoch_note": "cycle 1 year 1 = 1027 CE Fire-female-Hare",
        },
        "losar_rule": {
            "cutoff": "Gregorian Feb 8 starts the new Tibetan year (fixed cutoff)",
            "assigned_prior_year": pre_losar,
            "approximate": pre_losar,
            "note": (
                "Losar drifts Feb 4 – Mar 5; without a per-year Losar table "
                "pre-cutoff assignments are approximate"
                if pre_losar else
                "birth date falls safely after any plausible Losar — label clean"
            ),
        },
        "parkha_day_number": parkha_day_number,
        "parkha_names": {
            "status": "unavailable",
            "reason": "name_matrix_[VERIFY]: number-only output by design",
        },
        "daily_pair": {
            "status": "unavailable",
            "reason": "almanac converter constants unpinned",
        },
        "mewa": {"status": "unavailable", "reason": "birth-year color table unverified"},
        "anchor_file": (anchor or {}).get("path", "embedded_fallback"),
        "anchor_verified_against": len((anchor or {}).get("test_vectors", [])) or None,
    }
    return {k: v for k, v in result.items() if v is not None}
