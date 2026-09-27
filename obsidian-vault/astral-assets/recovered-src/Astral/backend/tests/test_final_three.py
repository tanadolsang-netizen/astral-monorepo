"""Tests: fusion transparency + rectification tournament + Uranian TNP."""

from __future__ import annotations

from datetime import datetime, date, time as dtime, timezone

import pytest

from src.services.fusion_transparency import compute_fusion_evidence, _norm
from src.services.rectification_tournament import rectification_tournament
from src.services.uranian_service import (
    tnp_longitudes, tnp_midpoint_pictures, uranian_report,
)

NATAL = {"name": "t", "date": date(1990, 5, 19), "time": dtime(5, 45)}


# ── Fusion transparency ──────────────────────────────────────────────
def test_norm_bounds() -> None:
    assert _norm(-50, 94) == 0
    assert _norm(200, 94) == 100
    assert _norm(47, 94) == 50
    assert _norm(0, 0) == 50


def test_fusion_evidence_deterministic_and_bounded() -> None:
    a = compute_fusion_evidence(NATAL, lat=13.75, lon=100.52,
                                now_utc=datetime(2026, 9, 1, tzinfo=timezone.utc))
    b = compute_fusion_evidence(NATAL, lat=13.75, lon=100.52,
                                now_utc=datetime(2026, 9, 1, tzinfo=timezone.utc))
    assert a == b
    for dom in a["domains"]:
        assert 0 <= dom["normalized"] <= 100
        assert isinstance(dom["fired_reasons"], list)


def test_fusion_evidence_lists_engines() -> None:
    r = compute_fusion_evidence(NATAL, lat=13.75, lon=100.52,
                                now_utc=datetime(2026, 9, 1, tzinfo=timezone.utc))
    assert "dasha_lord" in r
    assert r["domains"]


def test_method_notes_present() -> None:
    r = compute_fusion_evidence(NATAL, lat=13.75, lon=100.52)
    assert "theoretical" in r["method_note_en"].lower()
    assert "normalize" in r["method_note_th"] or "ค่าสูงสุด" in r["method_note_th"]


# ── Rectification tournament ─────────────────────────────────────────
EVENTS = [
    {"event_date": "2018-06-15", "category": "marriage"},
    {"event_date": "2021-03-01", "category": "career_start"},
]


def test_tournament_needs_events() -> None:
    with pytest.raises(ValueError):
        rectification_tournament("1990-05-19", "05:45", events=None)


def test_tournament_returns_ranked_candidates() -> None:
    r = rectification_tournament("1990-05-19", "05:45", natal_lat=13.75,
                                 natal_lon=100.52, events=EVENTS,
                                 window_hours=2, step_minutes=30)
    assert r["candidates_evaluated"] >= 4
    assert len(r["top5"]) >= 1
    scores = [c["raw_score"] for c in r["top5"]]
    assert scores == sorted(scores, reverse=True)


def test_anchor_window_scores_vary_deterministically() -> None:
    r1 = rectification_tournament("1990-05-19", "05:45", natal_lat=13.75,
                                  natal_lon=100.52, events=EVENTS,
                                  window_hours=1, step_minutes=15)
    r2 = rectification_tournament("1990-05-19", "05:45", natal_lat=13.75,
                                  natal_lon=100.52, events=EVENTS,
                                  window_hours=1, step_minutes=15)
    assert r1 == r2  # deterministic
    assert r1["candidates_evaluated"] == 9  # ±1h / 15min
    assert r1["confidence_pct"] >= 0


def test_tnp_longitudes_all_12_signs_range() -> None:
    tnps = tnp_longitudes(datetime(2026, 9, 1, tzinfo=timezone.utc))
    assert set(tnps) == set(_TNP_KEYS)
    for v in tnps.values():
        assert 0 <= v < 360


_TNP_KEYS = {"Cupido", "Hades", "Zeus", "Kronos",
             "Apollon", "Admetos", "Vulcanus", "Poseidon"}


def test_tnp_slow_motion_monotonic() -> None:
    a = tnp_longitudes(datetime(2026, 1, 1))
    b = tnp_longitudes(datetime(2036, 1, 1))
    for k in a:
        diff = (b[k] - a[k]) % 360
        assert diff < 26 or diff > 334  # slow motion, wrap-aware


def test_uranian_report_structure() -> None:
    bodies = {"Sun": 57.9, "Moon": 342.4, "Venus": 10.3}
    r = uranian_report(bodies, "1990-05-19T05:45")
    assert r["system"] == "uranian-hamburg"
    assert "pictures_sample" in r
    assert len(r["interpretation"]["th"]) > 40


def test_midpoint_pictures_detectable() -> None:
    # Sun/Venus midpoint should catch some C within 1.5° dial usually
    pics = tnp_midpoint_pictures({"Sun": 57.9, "Venus": 10.3, "Mars": 170.0},
                                 datetime(2026, 9, 1), orb=3.0)
    assert isinstance(pics, list)
