"""Regression tests for parans star precession.

The original implementation converted J2000 equatorial coordinates with a
single constant obliquity and a linear `lon - (year-2000)*50.29/3600` shift.
That formula moved in the wrong direction and was accurate only near J2000:

    epoch    old error      now
    1900     -167.4 arcmin  < 0.001 arcsec
    2100     +167.3 arcmin  < 0.001 arcsec

The reference is Skyfield's own `build_ecliptic_matrix` (IAU 2006 precession
plus true obliquity and nutation), so these tests assert the project and
Skyfield agree, not that we match a hand-derived number.
"""
import math
from datetime import datetime, timezone

import pytest

from src.services.parans_service import (
    STAR_TH,
    STARS,
    _jd_ut,
    _star_epoch_radec,
    brady_parans,
    star_positions,
)

from skyfield.api import load

skyfield = pytest.importorskip("skyfield")

EPOCHS = [
    (1900, 1, 1, 0),
    (1950, 6, 15, 12),
    (1997, 5, 18, 22),
    (2016, 1, 1, 0),
    (2100, 1, 1, 0),
]

# Precession is sub-arcsecond, so anything under a milliarcsecond means the
# two implementations are running the same matrix.
TOL_ARCSEC = 0.001


@pytest.fixture(scope="module")
def ts():
    return load.timescale()


def _reference_lon(ts, star, y, mo, d, h):
    """Ecliptic longitude via Skyfield, with proper motion applied in ICRS.

    The proper-motion step is re-implemented here rather than imported from
    the engine, so this stays a real cross-check of the engine's propagation
    rather than a tautology. The matrix is still Skyfield's, which is why the
    module is a consistency check and not an accuracy one.
    """
    from skyfield.framelib import build_ecliptic_matrix

    m = build_ecliptic_matrix(ts.utc(y, mo, d, h))
    ra_deg = star["ra"] * 15.0
    dec_deg = star["dec"]
    # Same Julian-date arithmetic the engine uses, so the residual measures
    # the propagation and not a difference in how the interval was measured.
    jd_tt = ts.utc(y, mo, d, h).tt
    years = (jd_tt - 2451545.0) / 365.25
    dec_deg += star.get("pm_dec", 0.0) / 1000.0 * years / 3600.0
    # pm_ra is mu_alpha*cos(dec), so the RA increment needs the cos undone.
    ra_deg += star.get("pm_ra", 0.0) / 1000.0 * years / 3600.0 / math.cos(
        math.radians(dec_deg)
    )
    ra = math.radians(ra_deg % 360.0)
    dec = math.radians(dec_deg)
    v = (math.cos(dec) * math.cos(ra), math.cos(dec) * math.sin(ra), math.sin(dec))
    o = [sum(m[i][j] * v[j] for j in range(3)) for i in range(3)]
    return math.degrees(math.atan2(o[1], o[0])) % 360.0


def test_matches_skyfield_at_every_epoch(ts):
    worst = 0.0
    worst_where = None
    for y, mo, d, h in EPOCHS:
        jd = _jd_ut(datetime(y, mo, d, h, tzinfo=timezone.utc))
        got = star_positions(jd)
        for name, star in STARS.items():
            diff = abs(got[name] - _reference_lon(ts, star, y, mo, d, h)) * 3600.0
            if diff > worst:
                worst, worst_where = diff, (name, y)
    assert worst < TOL_ARCSEC, f"worst {worst:.4f} arcsec at {worst_where}"


def test_proper_motion_moves_stars_the_right_amount():
    """Guard that proper motion is applied at all, and with the right sign.

    Measured on `_star_epoch_radec` rather than `star_positions`, because a
    century of ecliptic longitude is dominated by ~5037" of precession and
    would bury the term under test. Arcturus drifts 227.9" per century, so
    over a century every star must move by a positive amount that is no
    larger than the catalogue's own |pm|. This also pins the tangential RA
    term: pm_ra is mu_alpha*cos(dec), so dropping the 1/cos(dec) shows up
    immediately at the pole, where cos(dec) is 0.013 (Polaris).
    """
    t0 = _jd_ut(datetime(2000, 1, 1, tzinfo=timezone.utc))
    t1 = _jd_ut(datetime(2100, 1, 1, tzinfo=timezone.utc))
    for name, star in STARS.items():
        ra0, dec0 = _star_epoch_radec(name, t0)
        ra1, dec1 = _star_epoch_radec(name, t1)
        moved = math.hypot(
            ((ra1 - ra0 + 540.0) % 360.0 - 180.0) * math.cos(math.radians(dec0)),
            dec1 - dec0,
        ) * 3600.0
        expected = math.hypot(star.get("pm_ra", 0.0), star.get("pm_dec", 0.0)) / 10.0
        assert moved == pytest.approx(expected, rel=0.01), (
            f"{name} moved {moved:.2f}\" in a century, catalogue says {expected:.2f}\""
        )


def test_precession_direction_is_positive():
    """Guard the exact sign bug: ecliptic longitude must INCREASE with date.

    Precession is retrograde in RA, which makes tropical ecliptic longitude of
    a fixed star grow by ~50.3 arcsec/yr. The old code subtracted, which is why
    every pre-J2000 chart was off by up to 2.8 degrees.
    """
    early = star_positions(_jd_ut(datetime(1900, 1, 1, tzinfo=timezone.utc)))
    late = star_positions(_jd_ut(datetime(2100, 1, 1, tzinfo=timezone.utc)))
    for name in STARS:
        assert late[name] > early[name], f"{name} precessed the wrong way"


def test_precession_rate_is_about_50_3_arcsec_per_year():
    """A century of precession should be ~1.397 deg, not ~0 or ~2.8 deg."""
    early = star_positions(_jd_ut(datetime(1900, 1, 1, tzinfo=timezone.utc)))
    late = star_positions(_jd_ut(datetime(2000, 1, 1, tzinfo=timezone.utc)))
    shifts = [late[n] - early[n] for n in STARS]
    mean = sum(shifts) / len(shifts)
    assert 1.30 < mean < 1.50, f"mean century shift {mean:.4f} deg"


def test_jd_ut_round_trips_known_instant():
    """1997-05-18 22:45 UTC is JD_UT 2450587.447916667; _jd_ut returns TT.

    The UTC JD is cross-checked against the Gregorian JDN formula, which is
    independent of Skyfield: JDN 2450587 minus 0.5 plus 22.75/24. The function
    then adds the TT-UTC offset, 62.184 s here. IERS leap seconds put it at
    62 s on that date, so the two agree to well under a second.
    """
    jd_utc = 2450587.447916667
    jd_tt = _jd_ut(datetime(1997, 5, 18, 22, 45, tzinfo=timezone.utc))
    assert 61.5 < (jd_tt - jd_utc) * 86400.0 < 63.0, "TT-UTC offset wrong"


def test_jd_ut_treats_naive_as_utc():
    aware = _jd_ut(datetime(1997, 5, 18, 22, 45, tzinfo=timezone.utc))
    naive = _jd_ut(datetime(1997, 5, 18, 22, 45))
    assert aware == pytest.approx(naive, abs=1e-9)


def test_known_star_longitudes_of_date():
    """Tropical anchors: Sirius ~14 deg Taurus, Vega ~15 deg Capricorn."""
    jd = _jd_ut(datetime(1997, 5, 18, 22, 45, tzinfo=timezone.utc))
    pos = star_positions(jd)
    assert 103.0 < pos["Sirius"] < 105.0, pos["Sirius"]
    assert 284.0 < pos["Vega"] < 286.0, pos["Vega"]


def test_longitudes_stay_in_range_for_every_epoch():
    for y, mo, d, h in EPOCHS:
        for name, lon in star_positions(
            _jd_ut(datetime(y, mo, d, h, tzinfo=timezone.utc))
        ).items():
            assert 0.0 <= lon < 360.0, f"{name} at {y}: {lon}"


def test_cache_returns_consistent_values():
    jd = _jd_ut(datetime(1997, 5, 18, 22, 45, tzinfo=timezone.utc))
    assert star_positions(jd) == star_positions(jd)


def test_thai_star_names_are_not_truncated_to_first_character():
    """Regression: `th_name[0]` rendered only the first character.

    อัลเดบารัน was displayed as "ดาวอ". A 180-minute orb makes the match
    deterministic, so this exercises the real formatting path rather than
    re-implementing the f-string.
    """
    result = brady_parans("1997-05-19", "05:45", 7, 13.7, 101.1, orb_minutes=180)
    parans = result["parans"]
    assert parans, "expected parans at a 180-minute orb"

    thai_names = {th for th, _ in STAR_TH.values()}
    for p in parans:
        star = p["star"]
        expected = STAR_TH.get(star, (star,))[0]
        # A one-character star name is the bug; the full name must appear.
        assert len(expected) == 1 or expected in p["th"], (star, p["th"])
        assert f"ดาว{expected} " in p["th"] or p["th"].endswith(f"ดาว{expected} มุม{p['planet_angle']}"), (star, p["th"])

    # Spot-check a name that is in STAR_TH, so the assertion above is real.
    aldebaran = [p for p in parans if p["star"] == "Aldebaran"]
    assert aldebaran, "expected Aldebaran in the 180-minute result"
    assert "ดาวอัลเดบารัน" in aldebaran[0]["th"], aldebaran[0]["th"]


def test_thai_names_cover_the_known_star_table():
    """Every STAR_TH entry must be a real name, not a stray character."""
    for key, (th, _meaning) in STAR_TH.items():
        assert len(th) >= 2, f"{key} -> {th!r} looks truncated"
        assert " " not in th.strip() or len(th) > 2, f"{key} -> {th!r}"
    assert STAR_TH["Aldebaran"][0] == "อัลเดบารัน"
    assert STAR_TH["Vega"][0] == "เวกา"


# --- POA criterion ---------------------------------------------------------
#
# A paran is one angle circle held in common by both bodies. The original
# code compared the *angle between the two bodies and the angle* instead of
# comparing where each body sits on the shared angle circle, so it only ever
# matched bodies that were already on top of each other. The reference probe
# is scripts/probe_poa_criterion.py.

CHONBURI = ("1997-05-19", "05:45", 7, 13.7, 101.1)


def test_sun_alcyone_asc_is_a_poa_paran():
    """The reference case from probe_poa_criterion.py.

    Sun and Alcyone sit ~7 min apart from the ASC but only 0.69 min apart
    *from each other* on the angle circle -- a real paran that the exact-angle
    gate returned nothing for.
    """
    result = brady_parans(*CHONBURI, orb_minutes=2)
    pairs = {(p["planet"], p["star"], p["planet_angle"]) for p in result["parans"]}
    assert ("Sun", "Alcyone (Pleiades)", "ASC") in pairs, sorted(pairs)


def test_poa_orb_widens_the_result_set_monotonically():
    """More orb must never find fewer parans."""
    counts = [len(brady_parans(*CHONBURI, orb_minutes=orb)["parans"])
              for orb in (2, 8, 30)]
    assert counts == sorted(counts), counts
    assert counts[0] < counts[2], counts


def test_paran_separation_never_exceeds_the_orb():
    for orb in (2, 8, 30):
        for p in brady_parans(*CHONBURI, orb_minutes=orb)["parans"]:
            assert p["separation_minutes"] <= orb, p


def test_a_body_is_never_paired_to_a_different_angle():
    """ASC/DSC use different angles but the same circle.

    Both members of a pair must cite the same angle, otherwise the
    comparison is between two unrelated reference circles.
    """
    for orb in (2, 8, 30):
        for p in brady_parans(*CHONBURI, orb_minutes=orb)["parans"]:
            assert p["planet_angle"] == p["star_angle"], p


def test_results_are_sorted_tightest_separation_first():
    seps = [p["separation_minutes"] for p in brady_parans(*CHONBURI)["parans"]]
    assert seps == sorted(seps), seps


def test_synthetic_star_never_reaches_chart_output():
    """Aldebaran_N has no astrometry, so it cannot appear in a chart.

    It sits 35" from the real Aldebaran, so leaving it in produced a
    near-duplicate paran a couple of arcminutes away.
    """
    assert "Aldebaran_N" in STARS, "kept in STARS as a documented default"
    for orb in (4, 60, 180):
        names = {p["star"] for p in brady_parans(*CHONBURI, orb_minutes=orb)["parans"]}
        assert not any(n.endswith("_N") for n in names), sorted(names)


def test_thai_planet_names_are_used():
    for p in brady_parans(*CHONBURI, orb_minutes=30)["parans"]:
        assert not p["th"].startswith(p["planet"] + " "), p


def test_engine_is_chart_specific_not_hardcoded():
    """Two charts, far apart in space and time, must not agree."""
    other = brady_parans("1971-01-03", "09:15", 5, -12.0, 77.0, orb_minutes=4)
    mine = brady_parans(*CHONBURI, orb_minutes=4)
    assert {p["star"] for p in other["parans"]} != {p["star"] for p in mine["parans"]}
    # ...and a location shift alone must change the answer, or the lat/lon
    # arguments are being ignored.
    elsewhere = brady_parans("1997-05-19", "05:45", 7, -33.9, 151.2, orb_minutes=4)
    assert elsewhere["parans"] != mine["parans"]
