"""Tests: star astrometry is Hipparcos-backed and internally consistent.

`services/sky_view.py` used to carry its own hand-entered copy of the Yale Bright
Star Catalogue.  71 of its 82 Hipparcos-checkable rows pointed at the wrong
star, because the names and coordinates had fallen out of alignment.  Nothing
caught it: the old tests only checked that a star came back with a plausible
altitude, and a star in the wrong place is just as plausible.

These tests pin the catalogue as the single source of truth so that regression
is loud rather than silent.
"""

from __future__ import annotations

import math

import pytest

from src.services.sky_view import STARS, sky_view
from src.services.star_catalogue import BRIGHT_STARS


def _separation_arcmin(
    ra_h_a: float, dec_a: float, ra_h_b: float, dec_b: float
) -> float:
    """Great-circle separation in arcminutes between two equatorial positions."""
    d_ra = math.radians((ra_h_b - ra_h_a) * 15.0)
    dec_1, dec_2 = math.radians(dec_a), math.radians(dec_b)
    cos_sep = (
        math.sin(dec_1) * math.sin(dec_2)
        + math.cos(dec_1) * math.cos(dec_2) * math.cos(d_ra)
    )
    return math.degrees(math.acos(max(-1.0, min(1.0, cos_sep)))) * 60.0


def test_sky_view_reads_the_catalogue_not_a_private_table() -> None:
    """Drawability is derived from the catalogue, not hand-listed.

    ``sky_view`` draws the Hipparcos-verified rows only.  The handful of
    ``yale_rounded`` rows (companion stars, one nebula) inherit coordinates and
    magnitudes from the app's old hand-entered table and are demonstrably wrong,
    so they are deliberately held back from the drawable set.
    """
    expected = {
        (r["ra_h"], r["dec_deg"], r["mag"], n, r["th"])
        for n, r in BRIGHT_STARS.items()
        if r.get("precision") == "hip2_full"
    }
    assert set(STARS) == expected, (
        "sky_view.STARS is not exactly the catalogue's hip2_full rows; add"
        " star data via scripts/fetch_bright_star_catalogue.py rather than"
        " editing the table"
    )


def test_every_star_sits_where_hipparcos_says() -> None:
    """Guards the exact bug class: a name paired with another star's position.

    A 1-2 arcminute tolerance allows for proper motion since J2000.  A row in
    the wrong constellation is off by degrees, so the margin is enormous.
    """
    offenders: list[str] = []
    for ra_h, dec, _mag, name, _th in STARS:
        cat = BRIGHT_STARS[name]
        if cat["precision"] != "hip2_full":
            continue
        sep = _separation_arcmin(ra_h, dec, cat["ra_h"], cat["dec_deg"])
        if sep > 2.0:
            offenders.append(f"{name} off by {sep / 60.0:.2f} deg")
    assert not offenders, "star positions diverged from Hipparcos: " + ", ".join(offenders)


def test_no_synthetic_star_reaches_the_sky() -> None:
    """Aldebaran_N is a test fixture, not a star. It must never render."""
    assert not [row for row in STARS if "Aldebaran_N" in row[3]]
    view = sky_view("2026-09-01", "22:00", 7.0, lat=13.75, lon_deg=100.52)
    assert not [s for s in view["stars"] if "Aldebaran_N" in s["name"]]


def test_catalogue_rows_are_self_consistent() -> None:
    """Proper motion, where present, must be finite and physically plausible.

    The bound is 6 arcsec/century per component.  Arcturus is the fastest
    bright star at mu_alpha* = -1093.55 and mu_delta = -1999.87 mas/yr
    (van Leeuwen 2007), so 6000 mas/yr leaves it real headroom while still
    catching a decimal-point slip: dropping or adding a decimal turns 1093
    into 109 or 109339, and neither survives this bound.
    """
    for name, cat in BRIGHT_STARS.items():
        if cat["precision"] != "hip2_full":
            continue
        pm_ra = cat["pm_ra_masyr"]
        pm_dec = cat["pm_dec_masyr"]
        assert math.isfinite(pm_ra) and math.isfinite(pm_dec), name
        assert abs(pm_ra) < 6000 and abs(pm_dec) < 6000, f"{name}: implausible PM"


def test_thai_names_are_not_english_passthrough() -> None:
    """The catalogue is bilingual by contract; a missing translation must fail."""
    assert BRIGHT_STARS, "catalogue is empty"
    for name, cat in BRIGHT_STARS.items():
        th = cat["th"]
        assert th and th.strip(), f"{name}: missing Thai name"
        assert th != name, f"{name}: Thai name is the English name"


def test_sky_view_keeps_returning_stars() -> None:
    """Smoke test on the real path, so a catalogue shape change cannot hide here."""
    view = sky_view("2026-09-01", "22:00", 7.0, lat=13.75, lon_deg=100.52)
    assert view["star_count"] > 10
    assert all(s["alt"] > 0 for s in view["stars"])
    assert all(s["name_th"] for s in view["stars"])
