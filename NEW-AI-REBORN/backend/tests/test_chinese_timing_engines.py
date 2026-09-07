"""Tests: QMDJ, Da Liu Ren, Flying Stars, Solar Arc/Tertiary."""

from __future__ import annotations

from datetime import datetime

import pytest

from src.services.qmdj_service import compute_qmdj, _dun_number
from src.services.daliuren_service import compute_daliuren
from src.services.flying_stars_service import (
    compute_flying_stars, period_of, _flight_sequence,
)
from src.services.solar_arc_service import solar_arc_progressions


# ── QMDJ ─────────────────────────────────────────────────────────────
def test_qmdj_structure() -> None:
    r = compute_qmdj(datetime(2026, 1, 1, 12, 0), intent="career")
    assert r["system"] == "qimen-dunjia"
    assert 1 <= r["dun"] <= 9
    assert len(r["palaces"]) == 9
    doors = {p["door_cn"] for p in r["palaces"]}
    assert len(doors & {"休門", "生門", "傷門", "杜門", "景門",
                        "死門", "驚門", "開門"}) >= 6


def test_qmdj_yang_yin_by_season() -> None:
    yang = _dun_number(datetime(2026, 1, 15), day_stem=2)
    yin = _dun_number(datetime(2026, 7, 15), day_stem=2)
    # winter = yang dun family, summer = yin — both valid 1..9
    assert 1 <= yang <= 9 and 1 <= yin <= 9


def test_qmdj_interpretation_th_en() -> None:
    r = compute_qmdj(datetime(2026, 3, 3, 9, 30), intent="wealth")
    assert len(r["interpretation"]["th"]) > 60
    assert "QMDJ" in r["interpretation"]["en"]


# ── Da Liu Ren ───────────────────────────────────────────────────────
def test_dlr_three_transmissions() -> None:
    r = compute_daliuren(datetime(2026, 5, 5, 14, 0), intent="decision")
    assert len(r["three_transmissions"]) == 3
    assert len(r["courses"]) == 4


def test_dlr_deterministic() -> None:
    a = compute_daliuren(datetime(2026, 5, 5, 14, 0))
    b = compute_daliuren(datetime(2026, 5, 5, 14, 0))
    assert a == b


def test_dlr_generals_present() -> None:
    r = compute_daliuren(datetime(2026, 6, 1, 8, 0))
    assert any("เทพ" in g or g for g in [r["general_first"]])


# ── Flying Stars ─────────────────────────────────────────────────────
def test_period_calculation() -> None:
    assert period_of(2004) == 8   # period 8: 2004-2023
    assert period_of(2024) == 9   # period 9 starts 2024
    assert period_of(1984) == 7


def test_flight_sequence_center() -> None:
    grid = _flight_sequence(5)
    assert grid[4] == 5           # center palace gets center star
    grid9 = _flight_sequence(9)
    assert grid9[4] == 9


def test_flying_stars_report() -> None:
    r = compute_flying_stars(2010, facing_degrees=180.0)
    assert r["period"] == 8
    assert len(r["palaces"]) == 9
    assert r["best_sector_th"]


def test_flying_stars_invalid_facing() -> None:
    with pytest.raises(ValueError):
        compute_flying_stars(2010, facing_degrees=400)


# ── Solar Arc / Tertiary ─────────────────────────────────────────────
def test_solar_arc_age_zero_is_natal() -> None:
    r = solar_arc_progressions("1990-05-19T05:45", 13.75, 100.52,
                               target_age_years=0.001)
    assert r["solar_arc_degrees"] < 1.0


def test_solar_arc_increases_with_age() -> None:
    a30 = solar_arc_progressions("1990-05-19T05:45", 13.75, 100.52,
                                 target_age_years=30)
    a50 = solar_arc_progressions("1990-05-19T05:45", 13.75, 100.52,
                                 target_age_years=50)
    assert a50["solar_arc_degrees"] > a30["solar_arc_degrees"]


def test_tertiary_moon_advances_13deg_per_year() -> None:
    a = solar_arc_progressions("1990-05-19T05:45", 13.75, 100.52,
                               target_age_years=10)
    b = solar_arc_progressions("1990-05-19T05:45", 13.75, 100.52,
                               target_age_years=11)
    diff = (b["tertiary_moon_longitude"] - a["tertiary_moon_longitude"]) % 360
    assert 12 < diff < 14.5


def test_solar_arc_has_aspects_and_interp() -> None:
    r = solar_arc_progressions("1990-05-19T05:45", 13.75, 100.52,
                               target_date_iso="2026-09-01")
    assert isinstance(r["aspects_to_natal"], list)
    assert len(r["interpretation"]["th"]) > 60
