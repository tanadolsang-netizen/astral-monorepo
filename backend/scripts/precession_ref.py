"""Meeus (Astronomical Algorithms ch.21) precession in coordinates + rates.

No matrix conventions to get wrong: at T=0 this is the identity by
construction, and its rates are pinned to the authoritative IAU 1976
constants (general precession in longitude 5028.796195"/century,
precession in RA m = 3.07496 s/yr, in dec n = 1.33621 s/yr).
"""
import math

ASEC = 3600.0

# IAU 1976 general precession constants (Meeus 21.2 / 21.4)
P_LON_PER_CENTURY = 5028.796195          # arcsec / Julian century
M_PER_YEAR = 3.07496 * 15.0             # s/yr -> arcsec/yr
N_PER_YEAR = 1.33621 * 15.0


def precession_angles(jd: float) -> tuple[float, float, float]:
    T = (jd - 2451545.0) / 36525.0
    zeta = (2306.2181 * T + 0.30188 * T**2 + 0.017998 * T**3) / ASEC
    z = (2306.2181 * T + 1.09468 * T**2 + 0.018203 * T**3) / ASEC
    theta = (2004.3109 * T - 0.42665 * T**2 - 0.041833 * T**3) / ASEC
    return zeta, z, theta


def precess_ra_dec(ra_deg: float, dec_deg: float, jd: float) -> tuple[float, float]:
    """J2000 equatorial -> mean equinox/equator of `jd` (Meeus 21.5)."""
    zeta, z, theta = precession_angles(jd)
    a0, d0 = math.radians(ra_deg), math.radians(dec_deg)
    cz, sz = math.cos(zeta), math.sin(zeta)
    ct, st = math.cos(theta), math.sin(theta)
    cd, sd = math.cos(d0), math.sin(d0)
    A = cd * math.sin(a0 + zeta)
    B = ct * cd * math.cos(a0 + zeta) - st * sd
    C = st * cd * math.cos(a0 + zeta) + ct * sd
    return (math.degrees(math.atan2(A, B)) + z) % 360.0, math.degrees(math.asin(C))


def predicted_rate(ra_deg: float, dec_deg: float) -> tuple[float, float]:
    """dRA/dt, dDec/dt in arcsec/yr from the IAU 1976 m/n first-order rates.

    Meeus 21.6:  dRA = m + n sin(a) tan(d);  dDec = n cos(a)
    """
    a, d = math.radians(ra_deg), math.radians(dec_deg)
    return M_PER_YEAR + N_PER_YEAR * math.sin(a) * math.tan(d), N_PER_YEAR * math.cos(a)
