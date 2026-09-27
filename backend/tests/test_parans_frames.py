"""Independent validation of the parans engine's reference frames.

`test_parans_precession.py` pins `star_positions` to Skyfield's
`build_ecliptic_matrix`. That is a *consistency* check: it proves the engine
agrees with the library it already calls, not that the result is right.

These tests re-derive the same quantities from published series the engine
never touches, so a bug in frame handling cannot hide:

  L1  true obliquity of date  vs Swiss Ephemeris swe.calc_ut(..., ECL_NUT)[0]
  L2  mean obliquity          vs the independent IAU-1980 polynomial (Meeus 22.2)
  L3  general precession      vs IAU-1976 precession angles (Meeus 21.4/21.5)
  L3b nutation                vs the Meeus 22 abbreviated series, asserted BOTH
      ways: the engine must track a precession+nutation reference to ~1", AND
      must visibly depart from a precession-only reference by 2-25"
  L4  ecliptic longitude      vs precession + nutation + rotation by the same
      obliquity the engine uses
  L5  implied precession rate vs the IAU-1976 constant, 50.2879"/yr
  L0  the reference itself    must be the identity at zero nutation

Every tolerance below is a *measured* residual with headroom, not a guess. The
measured values (2026-09-27, engine vs reference, 1900-2100):

  L1   0.0008"   The engine and the Swiss Ephemeris share the same IAU-2006
                 nutation model, so this is near-identity by construction. It
                 is a guard against the obliquity being reached by the wrong
                 code path or in the wrong units - not a measure of accuracy.
  L2   0.063"    Genuine two-series agreement (IAU 1980 mean obliquity).
  L3b  0.40" RA / 0.13" Dec / 0.33" longitude against precession+nutation, and
                 23.9" / 8.6" / 21.3" against precession only. The ~0.4" that
                 remains is the *reference's* error: the abbreviated Meeus 22
                 nutation series is quoted at ~0.5" in dpsi. The engine is
                 therefore more accurate than this check, which is why L3b is
                 the load-bearing test and L3 is only a band check.
  L5   50.47"/yr vs 50.2879"/yr = 0.18"/yr = 18"/century, which is the
                 IAU-2006 minus IAU-1976 general precession rate difference.

A HISTORY WORTH RECORDING
-------------------------
An earlier version of this file compared the engine against a PRECESSION-ONLY
reference and reported 17.9" in RA, then attributed the gap to the
IAU-2006/IAU-1976 model difference. That attribution was wrong. The engine
does apply nutation; the reference did not. Nutation in longitude reaches
17.5" and in obliquity 9.2", so the whole residual was the missing term.
Adding it cut the RA residual by ~60x. The lesson generalises: before
attributing a residual to two implementations using different *models*, check
whether the two are even computing the same *quantity*. A loose tolerance
(30" here) hides a full nutation term, so a test can pass while measuring
nothing.

WHAT IS *NOT* CLAIMED HERE
--------------------------
`STARS` carries only `ra`/`dec`/`mag` - no catalog epoch, no proper motion, no
recorded reference frame. These tests therefore validate the *coordinate
transform chain* only. They cannot validate where the star positions came from,
and they cannot bound long-term position error: a star catalogued without proper
motion still drifts from aberration and nutation, and much more from unmodelled
proper motion. Treating these residuals as star-position accuracy would be wrong.

Sources
-------
Swiss Ephemeris documentation, Astrodienst AG, section 2.1: "The compressed
version agrees with the JPL Ephemeris to 1 milli-arcsecond (0.001")."
https://www.astro.com/swisseph/swisseph.htm (retrieved 2026-09-27; local build
pyswisseph 2.10.03). Section 2.6 of the same document notes the fixed-star
database is "originally based on the star catalogue of Steve Moshier", updated
from SIMBAD in 2006 and 2011.
Meeus, *Astronomical Algorithms*, 2nd ed.: ch. 21 (precession), ch. 22
(obliquity and nutation).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

from src.services import parans_service as ps  # noqa: E402
import meeus_reference as meeus  # noqa: E402

swisseph = pytest.importorskip("swisseph", reason="pyswisseph not installed")

ASEC = 3600.0
J2000 = 2451545.0

# Measured worst residuals, 1900-2100 (see module docstring). The "nut" set is
# the load-bearing gate; the "pre" set only bounds how far the engine must sit
# from a precession-ONLY reference, which is what proves nutation is applied.
TOL_OBLIQUITY_TRUE = 0.01   # arcsec, vs Swiss Ephemeris
TOL_OBLIQUITY_MEAN = 0.15   # arcsec, vs the IAU 1980 series
TOL_DRA = 1.0               # arcsec, engine vs precession+nutation reference
TOL_DDEC = 0.3              # arcsec, ditto
TOL_DLAMBDA = 0.5           # arcsec, ditto
TOL_RATE = 1.0              # arcsec/yr, vs the IAU-1976 constant
NUTATION_MIN_RA = 2.0       # arcsec, floor for "nutation is actually applied"
NUTATION_MAX_RA = 25.0      # arcsec, ceiling for the same claim

IAU1976_RATE = 50.2879      # arcsec/yr, Meeus 21.5

EPOCHS = [
    ("J1900", 2415020.5),
    ("J1925", 2428833.5),
    ("J1950", 2433282.5),
    ("J1975", 2442433.5),
    ("J2000", 2451545.0),
    ("J2025", 2460676.5),
    ("J2050", 2469807.5),
    ("J2075", 2478938.5),
    ("J2100", 2488070.0),
]

# Stars within 55 deg of a pole are excluded from angular comparisons: there a
# small rotation error maps to a large, poorly conditioned RA error, so an
# absolute-longitude residual stops being a meaningful metric.
MAX_DEC = 55.0

_well_conditioned = [n for n, s in ps.STARS.items() if abs(s["dec"]) <= MAX_DEC]
assert _well_conditioned, "no well-conditioned stars in the catalog"


def _swe_field(jd: float, field: int) -> float:
    """`field` 0 = true obliquity of date, 1 = mean obliquity of date."""
    return swisseph.calc_ut(jd, swisseph.ECL_NUT)[0][field]


def _engine_eps_deg(jd_tt: float) -> float:
    return math.degrees(ps._obliquity_of_date(*ps._frames(jd_tt)))


def _cat_epoch_radec(star: dict, jd_tt: float) -> tuple[float, float]:
    """Catalogue (RA, Dec) in degrees with proper motion applied, for a reference.

    `STARS` now carries Hipparcos proper motion, so a reference that starts
    from the raw J2000 table row is comparing two different instants. The
    reference must propagate the star exactly as the engine does, otherwise
    the residual measures the omitted term rather than the frame. The motion
    is applied in ICRS *before* precession, matching the engine's order.
    """
    ra = star["ra"] * 15.0
    dec = star["dec"]
    years = (jd_tt - 2451545.0) / 365.25
    dec += star.get("pm_dec", 0.0) / 1000.0 * years / 3600.0
    ra += star.get("pm_ra", 0.0) / 1000.0 * years / 3600.0 / math.cos(
        math.radians(dec)
    )
    return ra % 360.0, dec


def _ref_radec(star: dict, jd_tt: float) -> tuple[float, float]:
    """Meeus precession + nutation of a catalogue star, with proper motion."""
    ra, dec = _cat_epoch_radec(star, jd_tt)
    pre_ra, pre_dec = meeus.precess_ra_dec(ra, dec, jd_tt)
    return meeus.nutate_ra_dec(pre_ra, pre_dec, jd_tt)


# --------------------------------------------------------------------------
# L0 - the bug classes these tests exist to catch
# --------------------------------------------------------------------------

def test_obliquity_helper_returns_radians():
    """`_obliquity_of_date` returns RADIANS.

    A harness that reads it as degrees is off by a factor of ~57.3, which
    produced a 24-degree fake residual during development.
    """
    for _, jd in EPOCHS:
        raw = ps._obliquity_of_date(*ps._frames(jd))
        assert abs(raw) < 1.0, f"expected radians at jd={jd}, got {raw}"
        assert 23.4 < math.degrees(raw) < 23.5


def test_precess_reference_takes_a_julian_day_not_centuries():
    """`precess_ra_dec` consumes a Julian Day, not a century count.

    Precession is the identity at J2000, so an identity check at the epoch is
    exactly what discriminates the two argument types: a century count of 0.0
    is a date in antiquity, not J2000.
    """
    ra, dec = 78.63, -8.202
    assert meeus.julian_centuries(J2000) == pytest.approx(0.0, abs=1e-12)
    assert meeus.precess_ra_dec(ra, dec, J2000) == pytest.approx((ra, dec), abs=1e-9)
    # Off-epoch it must genuinely move, and feeding the century count where a
    # JD belongs silently evaluates a date in year ~-4713 rather than failing.
    assert meeus.julian_centuries(2415020.5) == pytest.approx(-1.0, abs=0.01)
    assert meeus.precess_ra_dec(ra, dec, 0.0) != pytest.approx((ra, dec), abs=1e-6)


@pytest.mark.parametrize(
    "year,jd",
    [
        (1900, 2415020.5),
        (1950, 2433282.5),
        (2000, 2451544.5),   # Jan 1.0. J2000.0 itself is 2451545.0 (noon).
        (2025, 2460676.5),
    ],
)
def test_jd_from_year_anchors(year, jd):
    assert meeus.jd_from_year(year) == pytest.approx(jd, abs=1e-6)


def test_right_ascension_difference_is_wrapped():
    """RA is a 0-360 angle; an unwrapped difference is not an error measure.

    A naive subtraction across the 0/360 boundary reports a ~360-degree
    residual for a star that is actually a few arcminutes away.
    """
    # Synthetic wrap. `sep` is a SIGNED difference wrapped to (-180, 180], so
    # these are 0.02 deg apart and the sign reports which way round.
    assert meeus.sep(359.99, 0.01) == pytest.approx(-0.02, abs=1e-9)
    assert meeus.sep(0.01, 359.99) == pytest.approx(0.02, abs=1e-9)
    # Magnitude is the true angular separation, and agrees with min-of-both-arcs.
    ra, dec = 78.63, -8.202
    for _, jd in EPOCHS:
        a, _ = meeus.precess_ra_dec(ra, dec, jd)
        b = (a + 137.0) % 360.0
        raw = abs(a - b)
        assert abs(meeus.sep(a, b)) == pytest.approx(min(raw, 360.0 - raw), abs=1e-9)


# --------------------------------------------------------------------------
# L1 / L2 - obliquity
# --------------------------------------------------------------------------

def test_true_obliquity_matches_swiss_ephemeris():
    """L1: the engine's true obliquity of date vs Swiss Ephemeris ECL_NUT[0]."""
    worst = 0.0
    for label, jd in EPOCHS:
        diff = abs(_engine_eps_deg(jd) - _swe_field(jd, 0)) * ASEC
        worst = max(worst, diff)
    assert worst < TOL_OBLIQUITY_TRUE, f"worst {worst:.4f} arcsec"


def test_mean_obliquity_matches_iau_1980_series():
    """L2: the independent IAU 1980 mean-obliquity polynomial vs Swiss ECL_NUT[1].

    The engine has no separate mean-obliquity routine, so the reference series
    is checked against Swiss Ephemeris directly.
    """
    worst = 0.0
    for label, jd in EPOCHS:
        diff = abs(meeus.mean_obliquity_deg(jd) - _swe_field(jd, 1)) * ASEC
        worst = max(worst, diff)
    assert worst < TOL_OBLIQUITY_MEAN, f"worst {worst:.4f} arcsec"


def test_obliquity_is_true_not_mean():
    """Guard against silently dropping the nutation term."""
    engine = _engine_eps_deg(J2000)
    mean = meeus.mean_obliquity_deg(J2000)
    nutation = abs(engine - mean) * ASEC
    assert 0.5 < nutation < 20.0, f"nutation in obliquity {nutation:.2f} arcsec"


def test_obliquity_decreases_secularly():
    """~23.44 deg and slowly decreasing - the well-known secular trend."""
    eps_1900 = _engine_eps_deg(2415020.5)
    eps_2100 = _engine_eps_deg(2488070.0)
    assert 23.4 < eps_1900 < 23.5
    assert 23.4 < eps_2100 < 23.5
    assert eps_1900 > eps_2100


# --------------------------------------------------------------------------
# L0 - the reference implementation must be sound before it can judge the
# engine. A wrong reference produces confident nonsense.
# --------------------------------------------------------------------------

def test_nutation_reference_is_the_identity_at_zero_nutation():
    """L0: guard the guard.

    The compact scalar apparent-place formulas are easy to get subtly wrong
    (this one shipped a sin/cos transposition that returned 90 deg for RA=0).
    The matrix form in `nutate_ra_dec` reduces to the identity when dpsi and
    deps vanish; this asserts that, so the reference cannot silently become
    wrong and start "validating" the engine against garbage.
    """
    assert meeus.test_nutation_is_identity() == 0


# --------------------------------------------------------------------------
# L3 - general precession, RA/Dec of date
# --------------------------------------------------------------------------

def test_radec_of_date_matches_precession_and_nutation():
    """L3b: engine RA/Dec vs Meeus 21.4/21.5 precession + Meeus 22 nutation.

    This is the load-bearing frame test. Both terms are required: precession
    rotates the frame over a century, nutation adds up to 17.5" in longitude
    and 9.2" in obliquity on an ~18.6-year cycle.
    """
    for label, jd in EPOCHS:
        radec = ps.star_radec(jd)
        for name in _well_conditioned:
            ref_ra, ref_dec = _ref_radec(ps.STARS[name], jd)
            eng_ra, eng_dec = radec[name]
            dra = meeus.sep(eng_ra, ref_ra) * ASEC
            ddec = (eng_dec - ref_dec) * ASEC
            assert abs(dra) < TOL_DRA, f"{label} {name}: dRA {dra:.3f} arcsec"
            assert abs(ddec) < TOL_DDEC, f"{label} {name}: dDec {ddec:.3f} arcsec"


def test_radec_of_date_departs_from_a_precession_only_reference():
    """L3b, negative half: the engine must NOT match precession alone.

    The complement of the test above. An engine that dropped nutation would
    still agree with a precession-only reference to well under a second, so
    the previous version of this file passed while measuring nothing. This
    pins the deviation into the band that nutation actually occupies, which
    makes both a missing and a spurious nutation term detectable.
    """
    seen_min, seen_max = 1e9, 0.0
    for label, jd in EPOCHS:
        radec = ps.star_radec(jd)
        for name in _well_conditioned:
            ra_pm, dec_pm = _cat_epoch_radec(ps.STARS[name], jd)
            ref_ra, _ = meeus.precess_ra_dec(ra_pm, dec_pm, jd)
            dra = abs(meeus.sep(radec[name][0], ref_ra)) * ASEC
            seen_min = min(seen_min, dra)
            seen_max = max(seen_max, dra)
    assert seen_max < NUTATION_MAX_RA, f"deviation {seen_max:.2f} arcsec too large"
    # A lower bound is what makes this a real gate: an engine that dropped
    # nutation would collapse the deviation to ~0. Note the *max* must be used,
    # not the min -- nutation passes through zero on its 18.6-year cycle, so
    # the smallest deviation across a century is legitimately near zero.
    assert seen_max > NUTATION_MIN_RA, (
        f"deviation peaks at only {seen_max:.2f} arcsec -- the engine is "
        "matching a precession-only reference, so nutation is absent"
    )


# --------------------------------------------------------------------------
# L4 - ecliptic longitude, in the engine's own frame
# --------------------------------------------------------------------------

def test_ecliptic_longitude_matches_in_the_engines_own_frame():
    """L4: the engine's ecliptic longitude vs precession + nutation + a rotation
    by the SAME obliquity the engine uses.

    The engine works in the true equator and equinox of date. Handing the
    reference a different obliquity measures a frame convention difference
    rather than correctness.
    """
    for label, jd in EPOCHS:
        pos = ps.star_positions(jd)
        eps_deg = _engine_eps_deg(jd)
        for name in _well_conditioned:
            ref_ra, ref_dec = _ref_radec(ps.STARS[name], jd)
            ref_lam = meeus.ecliptic_longitude_deg(ref_ra, ref_dec, eps_deg)
            dlam = meeus.sep(pos[name], ref_lam) * ASEC
            assert abs(dlam) < TOL_DLAMBDA, f"{label} {name}: dLambda {dlam:.3f} arcsec"


def test_ecliptic_latitude_uses_a_normalised_convention():
    """Ecliptic latitude must be near zero for genuinely near-ecliptic stars.

    An un-normalised sin/cos atan2 can legitimately return the antipode, so
    both the near-ecliptic cluster and a far-from-ecliptic star are pinned.
    """
    for _, jd in EPOCHS:
        eps_deg = _engine_eps_deg(jd)
        for name in ("Regulus", "Spica", "Aldebaran", "Antares"):
            star = ps.STARS[name]
            ref_ra, ref_dec = meeus.precess_ra_dec(star["ra"] * 15.0, star["dec"], jd)
            ref_bet = meeus.ecliptic_latitude_deg(ref_ra, ref_dec, eps_deg)
            assert -90.0 < ref_bet < 90.0
            assert abs(ref_bet) < 8.0, f"{name} beta {ref_bet:.2f} deg"
        # A star well off the ecliptic must stay well off it.
        star = ps.STARS["Sirius"]
        ref_ra, ref_dec = meeus.precess_ra_dec(star["ra"] * 15.0, star["dec"], jd)
        far = meeus.ecliptic_latitude_deg(ref_ra, ref_dec, eps_deg)
        assert 20.0 < abs(far) < 60.0, f"Sirius beta {far:.2f} deg"


def test_star_positions_agrees_with_star_radec():
    """`star_positions` and `star_radec` must describe the same instant.

    These are two paths through the engine into the same frame. If they
    diverge, one of them is wrong - and the two consumers downstream (house
    cusps and parans) would disagree with each other.
    """
    for label, jd in EPOCHS:
        pos = ps.star_positions(jd)
        radec = ps.star_radec(jd)
        eps_deg = _engine_eps_deg(jd)
        for name in _well_conditioned:
            eng_lam = meeus.ecliptic_longitude_deg(radec[name][0], radec[name][1], eps_deg)
            dlam = meeus.sep(pos[name], eng_lam) * ASEC
            assert abs(dlam) < 0.05, f"{label} {name}: internal dLambda {dlam:.3f} arcsec"


# --------------------------------------------------------------------------
# L5 - implied general precession rate
# --------------------------------------------------------------------------

def test_implied_precession_rate_is_within_model_difference_of_iau_1976():
    """L5: the engine's own J2000 -> J2100 longitude drift vs the IAU 1976 value.

    The engine precesses with the modern IAU-2006 model; this reference is
    IAU 1976 (Meeus 21.5). A difference of a few tenths of an arcsecond per year
    is the *expected* model difference and must not be "fixed" by tightening the
    bound - if it fell to zero the reference would no longer be independent.
    """
    p2000 = ps.star_positions(J2000)
    p2100 = ps.star_positions(EPOCHS[-1][1])
    for name in ("Regulus", "Spica", "Antares"):
        rate = (p2100[name] - p2000[name]) % 360.0 * ASEC / 100.0
        assert abs(rate - IAU1976_RATE) < TOL_RATE, f"{name}: {rate:.3f} arcsec/yr"
