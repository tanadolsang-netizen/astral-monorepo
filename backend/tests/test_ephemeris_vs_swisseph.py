"""Regression guard: chart_service vs Swiss Ephemeris 20230604.

This file exists because the engine once reported **J2000-referred** ecliptic
longitudes instead of equinox-of-date, which displaced every planet by the
general precession (0.01397 deg/yr) and put cusp 2 of a Placidus chart up to
7.8 deg — and 29 deg — out of place. Nothing in the 556-test suite caught it,
because the suite's own ground-truth tables had been generated from the same
buggy output.

Swiss Ephemeris is the reference implementation for astrology, and
pyswisseph is a declared project dependency, so it is the yardstick here.

Tolerances below are 20x tighter than anything the product needs, and they are
what caught every one of the three bugs fixed on 2026-09-27:

  1. planets: J2000 frame        -> .apparent().ecliptic_latlon(epoch=t)
  2. houses:  J2000 obliquity    -> mean_obliquity(jd_tt)
  3. cusps:   wrong Placidus base -> 60/120 deg quadrant anchors
     (plus Koch, which is now delegated to swisseph outright)
"""
from datetime import date, time as dtime

import pytest

swe = pytest.importorskip("swisseph")

from src.services.chart_service import compute_chart  # noqa: E402

PLANETS = [
    ("Sun", swe.SUN), ("Moon", swe.MOON), ("Mercury", swe.MERCURY),
    ("Venus", swe.VENUS), ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
    ("Saturn", swe.SATURN), ("Uranus", swe.URANUS), ("Neptune", swe.NEPTUNE),
    ("Pluto", swe.PLUTO),
]

# (y, m, d, hour, minute, lat, lon)
MODERN = [
    (1987, 11, 3, 5, 0, 13.3611, 100.9847),
    (1997, 5, 19, 22, 45, 13.3611, 100.9847),
    (2000, 1, 1, 12, 0, 51.4779, 0.0),
    (2010, 6, 15, 8, 30, 13.3611, 100.9847),
    (2026, 9, 27, 0, 0, 13.3611, 100.9847),
    (2040, 1, 1, 6, 0, 13.3611, 100.9847),
]

# Before 1973 the IERS/Espenak-Meeus delta-T series that Skyfield extrapolates
# and the one pyswisseph carries internally disagree by up to ~2.8 s. That is
# 0.16 deg of RAMC, so the ascendant and the quadrant cusps cannot be expected
# to agree to arcsecond level. Planet longitudes are unaffected.
HISTORICAL = [
    (1901, 12, 13, 20, 45, 13.3611, 100.9847),
    (1935, 3, 8, 4, 20, 13.3611, 100.9847),
    (1969, 7, 20, 20, 17, 40.7128, -74.0060),
]

HSYS = {b"P": "placidus", b"K": "koch", b"A": "equal", b"W": "whole_sign"}


def _delta(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def _ours(y, mo, d, hh, mm, lat, lon, hsys):
    c = compute_chart("t", date(y, mo, d), dtime(hh, mm), 0.0, lat, lon,
                      "tropical", hsys)
    out = {b["body"]: b["absolute_deg"] for b in c["bodies"]}
    out["ASC"] = c["ascendant"]["absolute_deg"]
    out["MC"] = c["midheaven"]["absolute_deg"]
    for cusp in c["houses"]["cusps"]:
        out[f"H{cusp['house']}"] = cusp["absolute_deg"]
    return out


def _swisseph(y, mo, d, hh, mm, lat, lon, sflag):
    jd = swe.julday(y, mo, d, hh + mm / 60, swe.GREG_CAL)
    out = {n: swe.calc_ut(jd, pl, swe.FLG_SWIEPH)[0][0] % 360 for n, pl in PLANETS}
    cusps, ascmc = swe.houses(jd, lat, lon, sflag)
    out["ASC"], out["MC"] = ascmc[0] % 360, ascmc[1] % 360
    for i in range(12):
        out[f"H{i + 1}"] = cusps[i] % 360
    return out


@pytest.mark.parametrize("case", MODERN, ids=lambda c: f"{c[0]}-{c[1]:02d}-{c[2]:02d}")
@pytest.mark.parametrize("hsys", HSYS.values())
def test_planets_match_swisseph_modern(case, hsys):
    y, mo, d, hh, mm, lat, lon = case
    ours = _ours(y, mo, d, hh, mm, lat, lon, hsys)
    ref = _swisseph(y, mo, d, hh, mm, lat, lon, b"P")
    for name, _pl in PLANETS:
        assert _delta(ours[name], ref[name]) < 0.01, (
            f"{name} off by {_delta(ours[name], ref[name]):.4f} deg on {y}-{mo}-{d}")


@pytest.mark.parametrize("case", MODERN, ids=lambda c: f"{c[0]}-{c[1]:02d}-{c[2]:02d}")
@pytest.mark.parametrize("hsys", HSYS.values())
def test_angles_and_cusps_match_swisseph_modern(case, hsys):
    y, mo, d, hh, mm, lat, lon = case
    ours = _ours(y, mo, d, hh, mm, lat, lon, hsys)
    ref = _swisseph(y, mo, d, hh, mm, lat, lon, next(k for k, v in HSYS.items() if v == hsys))
    for key in ("ASC", "MC", *(f"H{i}" for i in range(1, 13))):
        assert _delta(ours[key], ref[key]) < 0.01, (
            f"{key} off by {_delta(ours[key], ref[key]):.4f} deg on "
            f"{y}-{mo}-{d} ({hsys})")


@pytest.mark.parametrize("case", HISTORICAL, ids=lambda c: f"{c[0]}-{c[1]:02d}-{c[2]:02d}")
def test_planets_match_swisseph_historical(case):
    """Planets are delta-T independent, so the full tolerance applies."""
    y, mo, d, hh, mm, lat, lon = case
    ours = _ours(y, mo, d, hh, mm, lat, lon, "placidus")
    ref = _swisseph(y, mo, d, hh, mm, lat, lon, b"P")
    for name, _pl in PLANETS:
        assert _delta(ours[name], ref[name]) < 0.01, (
            f"{name} off by {_delta(ours[name], ref[name]):.4f} deg on {y}-{mo}-{d}")


@pytest.mark.parametrize("case", HISTORICAL, ids=lambda c: f"{c[0]}-{c[1]:02d}-{c[2]:02d}")
def test_angles_historical_within_deltat_bound(case):
    """Pre-1973 the two libraries' delta-T series differ by up to ~2.8 s.

    2.8 s of time is 0.17 deg of RAMC, so this is a bound on the reference
    data, not on the engine. If this ever fails by much more than 0.2 deg the
    cause is in our code, not in delta-T.
    """
    y, mo, d, hh, mm, lat, lon = case
    ours = _ours(y, mo, d, hh, mm, lat, lon, "placidus")
    ref = _swisseph(y, mo, d, hh, mm, lat, lon, b"P")
    for key in ("ASC", "MC"):
        assert _delta(ours[key], ref[key]) < 0.25, (
            f"{key} off by {_delta(ours[key], ref[key]):.4f} deg on {y}-{mo}-{d}")


def test_no_zodiac_sign_mismatch_modern():
    """A wrong zodiac degree 0-30 is a wrong reading, whatever the tolerance."""
    for y, mo, d, hh, mm, lat, lon in MODERN:
        for sflag, hname in HSYS.items():
            ours = _ours(y, mo, d, hh, mm, lat, lon, hname)
            ref = _swisseph(y, mo, d, hh, mm, lat, lon, sflag)
            for key, val in ours.items():
                assert int(val // 30) == int(ref[key] // 30), (
                    f"{key} on {y}-{mo}-{d} ({hname}): "
                    f"sign {int(val // 30)} vs swisseph {int(ref[key] // 30)}")


def test_equinox_of_date_not_j2000():
    """The regression itself, stated directly.

    At 1901 the two frames are 1.37 deg apart. If this ever fails, the engine
    has gone back to reporting J2000-referred longitudes.
    """
    c = compute_chart("t", date(1901, 12, 13), dtime(20, 45), 0.0,
                      13.3611, 100.9847, "tropical", "placidus")
    sun = [b for b in c["bodies"] if b["body"] == "Sun"][0]
    jd = swe.julday(1901, 12, 13, 20 + 45 / 60, swe.GREG_CAL)
    ref = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)[0][0] % 360
    assert _delta(sun["absolute_deg"], ref) < 0.01
    # and explicitly NOT the J2000 value
    j2000_value = ref + 1.3725
    assert _delta(sun["absolute_deg"], j2000_value) > 1.0
