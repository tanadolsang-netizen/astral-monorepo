"""Single source of truth for ayanamsa (sidereal zodiac offset).

WHY THIS MODULE EXISTS
----------------------
The project previously had THREE different ayanamsa implementations that
disagreed with each other and with Swiss Ephemeris by up to 487 arcsec
(8.1 arcminutes) — enough to move a planet across a whole sign boundary:

  chart_service.lahiri_ayanamsa()  J2000 anchor 23.68  → -487.0 arcsec error
  vedic_service._ayanamsa()        J2000 anchor 23.85  →  -25.6 arcsec error
  kp_service.kp_ayanamsa()         Lahiri - 6'        →  -25.9 arcsec error

The root cause: all three used a *linear* drift model (50.29"/yr) with a
hand-guessed anchor. Real ayanamsas follow the true precession of the equinox,
which is not linear.

WHAT THIS DOES
--------------
Primary:  Swiss Ephemeris (pyswisseph) via set_sid_mode + get_ayanamsa_ut.
          This is the reference standard — the same value JH, Astro.com and
          every serious Vedic package report. Verified against published
          anchor values: Lahiri at J2000 = 23°51'25" (23.857092°), matching
          Swiss exactly, vs our old 23.7219°.

Fallback: 4th-order polynomial in Julian centuries, least-squares fitted
          against Swiss over 1500-2300 CE at 5-year steps. Reproduces Swiss
          to <= 0.0001 arcsec over that whole 800-year span, so the fallback
          is not a degraded path — it is numerically indistinguishable.

VERIFIED (see scripts/precision_audit.py):
  Lahiri   J2000  23.857092°  = 23°51'25.5"  ✓ matches published tables
  KP       J2000  23.760240°  = Lahiri - 5'49" ✓ matches KP literature
  Raman    J2000  22.410791°
  FB       J2000  24.740300°
  Deluce   J2000  27.815753°

Thread safety: swe.set_sid_mode() mutates C-global state, so all Swiss calls
are serialised behind _SWISS_LOCK.
"""

from __future__ import annotations

import math
import threading
from datetime import datetime, timezone
from typing import Callable

import swisseph as swe

__all__ = [
    "SUPPORTED",
    "DEFAULT",
    "ayanamsa",
    "ayanamsa_for",
    "is_supported",
    "SOURCE",
]

DEFAULT = "lahiri"

# Polynomial coefficients, descending order in T (Julian centuries from J2000),
# fitted against swisseph.get_ayanamsa_ut over 1500-2300 CE.
_FITS: dict[str, tuple[float, float, float, float, float]] = {
    "lahiri":        (-5.987e-09, 4.306e-09, 0.000307104466, 1.396887952877, 23.857092347830),
    "raman":         (-5.975e-09, 4.188e-09, 0.000307071021, 1.396888072983, 22.410791034447),
    "fagan_bradley": (-5.986e-09, 4.293e-09, 0.000307100774, 1.396887967268, 24.740299988556),
    "krishnamurti":  (-5.975e-09, 4.188e-09, 0.000307071021, 1.396888072983, 23.760240034447),
    "deluce":        (-5.547e-09, 7.953e-09, 0.000305909060, 1.396878335920, 27.815752796276),
}

_SWISS_MODES: dict[str, int] = {
    "lahiri": swe.SIDM_LAHIRI,
    "raman": swe.SIDM_RAMAN,
    "fagan_bradley": swe.SIDM_FAGAN_BRADLEY,
    "krishnamurti": swe.SIDM_KRISHNAMURTI,
    "deluce": swe.SIDM_DELUCE,
}

SUPPORTED: tuple[str, ...] = tuple(_FITS)

# Remembers which sidereal mode is currently set in Swiss global state, so we
# only call set_sid_mode when the mode actually changes (it is not cheap).
_MODE_LOCK = threading.Lock()
_current_mode: int | None = None
_SWISS_LOCK = threading.RLock()


def is_supported(name: str) -> bool:
    return (name or "").strip().lower() in _FITS


def _jd_from_datetime(dt: datetime) -> float:
    """Julian Day (UT) from an aware or naive datetime. Naive is treated as UT."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)
    hour = (
        dt.hour
        + (dt.minute + (dt.second + dt.microsecond / 1e6) / 60.0) / 60.0
    )
    return swe.julday(dt.year, dt.month, dt.day, hour, swe.GREG_CAL)


def _polynomial(name: str, jd_ut: float) -> float:
    c4, c3, c2, c1, c0 = _FITS[name]
    t = (jd_ut - 2451545.0) / 36525.0
    return c0 + t * (c1 + t * (c2 + t * (c3 + t * c4)))


def _swiss(name: str, jd_ut: float) -> float | None:
    """Swiss Ephemeris ayanamsa. None means 'Swiss unavailable, use fallback'."""
    global _current_mode
    mode = _SWISS_MODES[name]
    try:
        with _SWISS_LOCK:
            with _MODE_LOCK:
                if _current_mode != mode:
                    swe.set_sid_mode(mode, 0.0, 0.0)
                    _current_mode = mode
            return float(swe.get_ayanamsa_ut(jd_ut))
    except Exception:  # pragma: no cover - Swiss must never break a chart
        return None


def ayanamsa_for(name: str, dt_utc: datetime) -> float:
    """Ayanamsa in degrees for a named mode. Unknown modes raise ValueError."""
    key = (name or DEFAULT).strip().lower()
    if key not in _FITS:
        raise ValueError(
            f"unsupported ayanamsa {name!r}; choose one of {', '.join(SUPPORTED)}"
        )
    jd = _jd_from_datetime(dt_utc)
    value = _swiss(key, jd)
    if value is None:
        value = _polynomial(key, jd)
    # Guard the physically meaningful range; a bad clock or tz would show up here.
    if not 15.0 <= value <= 35.0:
        return _polynomial(key, jd)
    return value


def ayanamsa(dt_utc: datetime) -> float:
    """Ayanamsa in degrees using the default (Lahiri) mode."""
    return ayanamsa_for(DEFAULT, dt_utc)


def sidereal_longitude(lon_tropical: float, dt_utc: datetime, ayanamsa_name: str = DEFAULT) -> float:
    """Convert a tropical longitude to sidereal. THE single conversion path."""
    return (lon_tropical - ayanamsa_for(ayanamsa_name, dt_utc)) % 360.0


def to_sidereal(longitude: float, dt_utc: datetime, ayanamsa_name: str = DEFAULT) -> float:
    return sidereal_longitude(longitude, dt_utc, ayanamsa_name)


def source() -> str:
    """Report which path is live, for the accuracy endpoint and tests."""
    probe = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    jd = _jd_from_datetime(probe)
    return "swiss_ephemeris" if _swiss(DEFAULT, jd) is not None else "polynomial_fallback"
