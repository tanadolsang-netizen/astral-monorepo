"""Tests: sky view planetarium data."""

from __future__ import annotations

import pytest

from datetime import datetime
from src.services.sky_view import sky_view, _alt_az, _ra_dec_from_ecliptic


def test_ra_dec_equinox() -> None:
    # 0° ecliptic = 0h RA, 0° Dec
    ra, dec = _ra_dec_from_ecliptic(0.0)
    assert abs(ra) < 0.01 and abs(dec) < 0.01


def test_alt_az_polaris_north() -> None:
    # Polaris RA 2.53h=37.95°, Dec 89.26° — from Bangkok (13.75N)
    alt, az = _alt_az(37.95, 89.26, 13.75, 100.52,
                      datetime(2026, 9, 1, 18, 0))
    # Polaris altitude ≈ observer latitude (13.75° from Bangkok)
    assert 12 <= alt <= 16


def test_sky_view_structure() -> None:
    r = sky_view("2026-09-01", "22:00", 7.0, lat=13.75, lon_deg=100.52)
    assert r["system"] == "sky-view"
    assert len(r["planets"]) >= 3
    assert r["star_count"] > 10
    for s in r["stars"]:
        assert s["alt"] > 0
        assert 1 <= s["size_px"] <= 8


def test_daylight_flag() -> None:
    day = sky_view("2026-09-01", "12:00", 7.0, lat=13.75, lon_deg=100.52)
    night = sky_view("2026-09-01", "22:00", 7.0, lat=13.75, lon_deg=100.52)
    assert isinstance(day["daylight"], bool)


def test_deterministic() -> None:
    a = sky_view("2026-09-01", "21:00", 7.0, lat=13.75, lon_deg=100.52)
    b = sky_view("2026-09-01", "21:00", 7.0, lat=13.75, lon_deg=100.52)
    assert a["planets"] == b["planets"]
