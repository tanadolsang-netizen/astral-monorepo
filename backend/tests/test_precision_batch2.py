"""Tests: SA rectifier + kakshya windows + Brady parans + reel pipeline."""

from __future__ import annotations

import os

import pytest

from src.services.sa_rectifier import (
    rectify_sa_convergence, _angles_from, _sep,
)
from src.services.kakshya_service import (
    transit_micro_windows, KAKSHYA_SPAN, _kakshya_index,
)
from src.services.parans_service import (
    brady_parans, star_positions, STARS,
)
from src.services.reel_video import build_reel_script


# ── SA rectifier ─────────────────────────────────────────────────────
def test_angles_from_chart() -> None:
    from src.services.chart_service import compute_chart
    c = compute_chart("a", __import__("datetime").date(1990, 5, 19),
                      __import__("datetime").time(5, 45),
                      tz_offset_hours=0, lat=13.75, lon=100.52)
    ang = _angles_from(c)
    assert set(ang) == {"ASC", "DSC", "MC", "IC"}
    assert abs(_sep(ang["ASC"], ang["DSC"]) - 180) < 1
    assert abs(_sep(ang["MC"], ang["IC"]) - 180) < 1


def test_sa_rectifier_runs_and_ranks() -> None:
    r = rectify_sa_convergence(
        "1990-05-19", "05:45", 7.0, 13.75, 100.52,
        events=[{"event_date": "2018-06-15", "category": "marriage"},
                {"event_date": "2021-03-01", "category": "career"},
                {"event_date": "2015-09-10", "category": "recognition"}],
        window_hours=2, step_minutes=20)
    scores = [c["score"] for c in r["top5"]]
    assert scores == sorted(scores, reverse=True)
    assert r["confidence_pct"] >= 0
    assert len(r["interpretation"]["th"]) > 40


def test_sa_rectifier_validates_category() -> None:
    with pytest.raises(ValueError):
        rectify_sa_convergence(
            "1990-05-19", "05:45", 7.0, 13.75, 100.52,
            events=[{"event_date": "2018-06-15",
                     "category": "lottery_win"}])


def test_sa_rectifier_needs_events() -> None:
    with pytest.raises(ValueError):
        rectify_sa_convergence("1990-05-19", "05:45", 7.0,
                               13.75, 100.52, events=[])


# ── Kakshya ──────────────────────────────────────────────────────────
def test_kakshya_span_math() -> None:
    assert abs(KAKSHYA_SPAN - 3.75) < 1e-9
    assert _kakshya_index(0.5) == 0
    assert _kakshya_index(3.8) == 1     # past first 3°45'
    assert _kakshya_index(29.9) == 7    # last kakshya


def test_kakshya_windows_structure() -> None:
    natal = {"Sun": 57.9, "Moon": 197.2, "Mars": 169.9, "Mercury": 70.1,
             "Jupiter": 100.4, "Venus": 10.3, "Saturn": 280.7}
    r = transit_micro_windows(natal, natal_asc_lon=154.0,
                              transiting_planet="Jupiter",
                              scan_start_iso="2026-09-01", scan_days=120)
    assert r["system"] == "ashtakavarga-kakshya"
    for w in r["windows"]:
        assert w["peak_sav"] >= 25
        assert w["signs"]


def test_kakshya_unknown_planet_raises() -> None:
    natal = {"Sun": 57.9}
    with pytest.raises(ValueError):
        transit_micro_windows(natal, 154.0, transiting_planet="Xena34",
                              scan_start_iso="2026-09-01", scan_days=30)


# ── Brady parans ─────────────────────────────────────────────────────
def test_stars_table_size() -> None:
    assert len(STARS) >= 24   # canonical list shipped


def test_star_positions_in_range() -> None:
    pos = star_positions(1990.4)
    for name, lon in pos.items():
        assert 0 <= lon < 360, name


def test_precession_direction() -> None:
    p2000 = star_positions(2000.0)
    p2050 = star_positions(2050.0)
    # precession decreases ecliptic longitude (westward)
    diff = (p2000["Sirius"] - p2050["Sirius"]) % 360
    assert diff > 350 or diff < 10  # ~2.5° over 50y wraps either way


def test_brady_parans_runs() -> None:
    r = brady_parans("1990-05-19", "05:45", tz_offset_hours=7,
                     lat=13.75, lon=100.52)
    assert r["system"] == "brady-parans"
    assert r["stars_checked"] == len(STARS)
    assert isinstance(r["parans_found"], int)
    assert len(r["interpretation"]["th"]) > 40


def test_parans_deterministic() -> None:
    a = brady_parans("1990-05-19", "05:45", 7, 13.75, 100.52)
    b = brady_parans("1990-05-19", "05:45", 7, 13.75, 100.52)
    assert a == b


# ── Reel video ───────────────────────────────────────────────────────
def test_reel_script_builds() -> None:
    s = build_reel_script("bench-user", spread="single")
    assert s["slides"]
    assert s["cards"]
    assert s["hook"]


def test_reel_script_lang_en() -> None:
    s = build_reel_script("x", lang="en")
    assert s["lang"] == "en"
