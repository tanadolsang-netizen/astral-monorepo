"""Tests: Maha Taksa + เลขสังวาลย์ + Jaimini + Prashna."""

from __future__ import annotations

import pytest

from src.services.mahataksa_service import (
    compute_mahataksa, lucky_numbers, STRENGTHS, CYCLE, _taksa_sequence,
)
from src.services.jaimini_service import (
    chara_karakas, atmakaraka, arudha_padas, karakamsa, chara_dasha,
    compute_jaimini,
)
from src.services.prashna_service import compute_prashna


# ── Maha Taksa ───────────────────────────────────────────────────────
def test_strengths_sum_108() -> None:
    assert CYCLE == 108
    assert sum(STRENGTHS.values()) == 108


def test_weekday_start_lord_anchor() -> None:
    # 1990-05-19 was a Saturday → start lord Saturn
    r = compute_mahataksa("1990-05-19", "2026-08-25")
    assert r["start_lord"] == "Saturn"
    assert r["birth_weekday_th"] == "เสาร์"


def test_deterministic_progression() -> None:
    a = compute_mahataksa("1990-05-19", "2026-08-25")
    b = compute_mahataksa("1990-05-19", "2026-08-25")
    assert a["current"] == b["current"]
    assert len(a["interpretation"]["th"]) > 60


def test_taksa_sequence_rotation() -> None:
    seq = _taksa_sequence("Saturn")
    assert seq[0] == "Saturn" and len(seq) == 8
    assert set(seq) == set(STRENGTHS.keys())


def test_chomangkala_numerology() -> None:
    r = lucky_numbers("สมชาย", "19/05")
    assert r["name_total"] > 0
    assert 1 <= r["luck_number"] <= 9
    assert r["meaning"]


# ── Jaimini ──────────────────────────────────────────────────────────
def test_karaka_ordering_desc() -> None:
    lons = {"Sun": 58.5, "Moon": 197.2, "Mars": 169.9,
            "Mercury": 70.1, "Jupiter": 100.4, "Venus": 10.3, "Saturn": 280.7}
    ks = chara_karakas(lons)
    degs = [k["deg_in_sign"] for k in ks]
    assert degs == sorted(degs, reverse=True)
    assert ks[0]["karaka"] == "AK"


def test_atmakaraka_highest_degree() -> None:
    lons = {"Sun": 58.5, "Moon": 197.2, "Mars": 169.9}  # Mars 169.9→28.9 in-sign? no: 169.9%30=19.9; Moon 17.2; Sun 28.5 → AK=Sun
    ak = atmakaraka(lons)
    assert ak["planet"] == "Sun"


def test_arudha_reflection_rules() -> None:
    # lord 7 signs away (same as 7th) → exception: arudha = 4th from house
    out = arudha_padas({}, {"1": 6})   # house1(Aries), lord in Libra(idx6)
    assert out["A1"]["sign_en"] == "Capricorn"  # same-sign exception → 10th from it


def test_chara_dasha_direction() -> None:
    d_odd = chara_dasha(0, years_per_sign=2, max_periods=3)  # Aries odd-footed → forward
    d_even = chara_dasha(1, years_per_sign=2, max_periods=3)  # Taurus even → reverse
    assert [p["sign_en"] for p in d_odd] == ["Aries", "Taurus", "Gemini"]
    assert [p["sign_en"] for p in d_even] == ["Taurus", "Aries", "Pisces"]


def test_compute_jaimini_full() -> None:
    lons = {"Sun": 58.5, "Moon": 197.2, "Mars": 169.9, "Mercury": 70.1,
            "Jupiter": 100.4, "Venus": 10.3, "Saturn": 280.7}
    r = compute_jaimini(lons, asc_lon_sidereal=30.0, person_name="t")
    assert r["atmakaraka"]["planet"]
    assert len(r["interpretation"]["th"]) > 80


# ── Prashna ──────────────────────────────────────────────────────────
def test_prashna_structure() -> None:
    r = compute_prashna("2026-09-01", "10:30", lat=13.75, lon=100.52,
                        tz_offset_hours=7, category="job_offer",
                        question_text="จะได้งานไหม")
    assert r["verdict_th"] in ("มีแนวโน้มสำเร็จ", "ยังไม่ชัดเจน")
    assert r["aspect"] is not None or r["ithasala"] is False
    assert "prashna" in r["interpretation"]["en"] or len(r["interpretation"]["en"]) > 40


def test_prashna_unknown_category_raises() -> None:
    with pytest.raises(ValueError):
        compute_prashna("2026-09-01", "10:30", 13.75, 100.52, 7,
                        category="lottery_numbers")


def test_prashna_categories_covered() -> None:
    from src.services.prashna_service import CATEGORY_HOUSES
    assert {"marriage_timing", "job_offer", "lost_object",
            "illness_recovery"} <= set(CATEGORY_HOUSES)
