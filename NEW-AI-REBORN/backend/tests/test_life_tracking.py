"""Tests: life tracking payload."""

from __future__ import annotations

from datetime import datetime, timezone

from src.services.life_tracking import (
    life_tracking_payload, _whole_sign_house,
)


def test_whole_sign_house() -> None:
    assert _whole_sign_house(0.0, 0.0) == 1
    assert _whole_sign_house(65.0, 30.0) == 2   # Gemini vs Taurus ASC
    assert _whole_sign_house(355.0, 350.0) == 1


def test_payload_structure_and_markers() -> None:
    r = life_tracking_payload(
        "Mark", "1990-05-19", "05:45", 7.0, 13.75, 100.52,
        now_utc=datetime(2026, 8, 26, tzinfo=timezone.utc))
    assert r["system"] == "life-tracking"
    assert "asc_lon" in r["natal"]
    assert len(r["transit_markers"]) >= 8
    for m in r["transit_markers"]:
        assert 1 <= m["natal_house"] <= 12


def test_dasha_and_profection_present() -> None:
    r = life_tracking_payload(
        "M", "1997-08-18", "22:32", 7.0, 13.86, 100.52)
    assert r["dasha"]["mahadasha_lord"]
    p = r["profection"]
    assert p["age"] >= 20 and 1 <= p["house"] <= 12


def test_interpretation_th_en() -> None:
    r = life_tracking_payload(
        "t", "1990-05-19", "05:45", 7.0, 13.75, 100.52)
    assert "บ้านที่" in r["interpretation"]["th"]
    assert "H" in r["interpretation"]["en"]
