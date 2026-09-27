"""Regression guard: every ayanamsa value must match Swiss Ephemeris.

This is the ground truth for the whole sidereal layer. Before the fix the
project carried THREE different ayanamsa implementations whose worst case was
487 arcsec (8.1 minutes of arc) off Swiss, which is large enough to move a
planet across a nakshatra pada boundary and change Vimshottari dasha start
dates. These tests pin the value to Swiss, not to a previous snapshot.
"""

from datetime import datetime, timedelta, timezone

import pytest

swisseph = pytest.importorskip("swisseph")

from src.services.ayanamsa import (  # noqa: E402
    _jd_from_datetime,
    _polynomial,
    SUPPORTED,
    ayanamsa_for,
    source,
    to_sidereal,
)

SWISS_MODE = {
    "lahiri": swisseph.SIDM_LAHIRI,
    "raman": swisseph.SIDM_RAMAN,
    "fagan_bradley": swisseph.SIDM_FAGAN_BRADLEY,
    "krishnamurti": swisseph.SIDM_KRISHNAMURTI,
    "deluce": swisseph.SIDM_DELUCE,
}

EPOCHS = [
    datetime(1900, 1, 1, 12, tzinfo=timezone.utc),
    datetime(1950, 6, 15, 3, 30, tzinfo=timezone.utc),
    datetime(1997, 5, 18, 22, 45, tzinfo=timezone.utc),
    datetime(2000, 1, 1, 12, tzinfo=timezone.utc),
    datetime(2026, 9, 27, 8, 0, tzinfo=timezone.utc),
    datetime(2050, 3, 3, 18, 20, tzinfo=timezone.utc),
    datetime(2200, 11, 11, 6, 0, tzinfo=timezone.utc),
]

# Swiss itself is float-accurate; anything above this is a real regression.
TOL_ARCSEC = 1e-3


def _swiss_reference(mode_name: str, dt: datetime) -> float:
    swisseph.set_sid_mode(SWISS_MODE[mode_name], 0.0, 0.0)
    return swisseph.get_ayanamsa_ut(_jd_from_datetime(dt))


@pytest.fixture(autouse=True)
def _reset_sid_mode():
    yield
    swisseph.set_sid_mode(swisseph.SIDM_LAHIRI, 0.0, 0.0)


@pytest.mark.parametrize("mode", SUPPORTED)
@pytest.mark.parametrize("dt", EPOCHS, ids=lambda d: d.strftime("%Y-%m-%d"))
def test_ayanamsa_matches_swiss(mode, dt):
    got = ayanamsa_for(mode, dt)
    ref = _swiss_reference(mode, dt)
    assert abs(got - ref) * 3600.0 < TOL_ARCSEC, (
        f"{mode} @ {dt}: got {got:.8f} deg, swiss {ref:.8f} deg, "
        f"err {(got - ref) * 3600:.4f} arcsec"
    )


@pytest.mark.parametrize("mode", SUPPORTED)
@pytest.mark.parametrize("dt", EPOCHS, ids=lambda d: d.strftime("%Y-%m-%d"))
def test_ayanamsa_fallback_matches_swiss(mode, dt):
    """The no-swisseph fallback must be just as accurate as the live path."""
    got = _polynomial(mode, _jd_from_datetime(dt))
    ref = _swiss_reference(mode, dt)
    assert abs(got - ref) * 3600.0 < TOL_ARCSEC


def test_lahiri_j2000_published_anchor():
    """Lahiri at J2000 = 23°51'25" — the value in every published table."""
    v = ayanamsa_for("lahiri", datetime(2000, 1, 1, 12, tzinfo=timezone.utc))
    assert v == pytest.approx(23.857092, abs=1e-5)
    total_arcmin = v * 60.0
    deg = int(total_arcmin // 60)
    remaining_arcmin = total_arcmin - deg * 60
    minutes = int(remaining_arcmin)
    sec = (remaining_arcmin - minutes) * 60
    assert (deg, minutes) == (23, 51)
    assert sec == pytest.approx(25.5, abs=1.0)


def test_kp_is_lahiri_minus_5_arcmin_49():
    """KP literature: KP-Newcomb ayanamsa = Lahiri - 5'49"."""
    dt = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)
    diff_arcmin = (ayanamsa_for("lahiri", dt) - ayanamsa_for("krishnamurti", dt)) * 60.0
    assert diff_arcmin == pytest.approx(5.82, abs=0.05)


def test_chart_service_shim_matches_swiss():
    """chart_service.lahiri_ayanamsa(year_frac) shim keeps old callers exact."""
    from src.services.chart_service import lahiri_ayanamsa

    for year_frac in (1900.0, 1997.0, 2000.0, 2026.72, 2050.0):
        year = int(year_frac)
        dt = datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(
            days=(year_frac - year) * 365.2425
        )
        got = lahiri_ayanamsa(year_frac)
        ref = _swiss_reference("lahiri", dt)
        assert abs(got - ref) * 3600.0 < TOL_ARCSEC, f"shim drifted at {year_frac}"


def test_vedic_and_kp_services_agree_with_central_module():
    """No service may carry its own ayanamsa formula any more."""
    from src.services.kp_service import kp_ayanamsa
    from src.services.vedic_service import _ayanamsa

    dt = datetime(1997, 5, 18, 22, 45, tzinfo=timezone.utc)
    assert kp_ayanamsa(dt) == ayanamsa_for("krishnamurti", dt)
    assert _ayanamsa(dt, "lahiri") == ayanamsa_for("lahiri", dt)


def test_vedic_ayanamsa_param_is_honoured():
    """The API accepts raman/fagan_bradley/krishnamurti — they must take effect."""
    from src.services.vedic_service import compute_vedic

    common = {
        "birth_datetime_local": "1997-05-19T05:45",
        "lat": 13.7563,
        "lon": 100.5018,
        "tz_offset_hours": 7.0,
    }
    lahiri = compute_vedic(ayanamsa="lahiri", **common)
    raman = compute_vedic(ayanamsa="raman", **common)

    assert raman["ayanamsa_mode"] == "raman"
    assert raman["ayanamsa"] < lahiri["ayanamsa"]  # Raman < Lahiri
    dt = datetime(1997, 5, 18, 22, 45, tzinfo=timezone.utc)
    assert raman["ayanamsa"] == pytest.approx(ayanamsa_for("raman", dt), abs=1e-3)


def test_unknown_mode_raises():
    with pytest.raises(ValueError, match="unsupported ayanamsa 'ketu'"):
        ayanamsa_for("ketu", datetime(2000, 1, 1, tzinfo=timezone.utc))


def test_sidereal_conversion_roundtrip():
    dt = datetime(1997, 5, 18, 22, 45, tzinfo=timezone.utc)
    trop = 58.0139  # Sun's tropical longitude, cross-checked against Swiss
    sid = to_sidereal(trop, dt, "lahiri")
    assert sid == pytest.approx((trop - ayanamsa_for("lahiri", dt)) % 360.0)
    assert 0.0 <= sid < 360.0


def test_source_is_declared():
    assert source() in {"swiss_ephemeris", "polynomial_fallback"}
