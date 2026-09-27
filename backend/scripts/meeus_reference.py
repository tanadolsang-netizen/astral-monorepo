"""Standalone Meeus/IAU reference: no rotation-matrix conventions to get wrong.

No rotation-matrix conventions to get wrong, so nothing here can silently
inherit a transpose/product-order bug from the engine.

  * Precession  -> Meeus ch.21, formulas 21.4/21.5. Start epoch is J2000, so
                  t == dt == T and the full form collapses to the cubic.
  * Nutation in obliquity -> Meeus ch.22, formula 22.3 (principal terms).
  * Mean obliquity       -> Meeus ch.22, formula 22.2 (IAU 1980).

Compared against the engine's star_radec() (precession only, obliquity-free)
and star_positions() (full equatorial -> ecliptic longitude path).

Caveat: stars are fixed J2000 positions (no proper motion), which is exactly
what the engine's own STARS table holds.
"""
import math

ASEC = 3600.0
J2000 = 2451545.0


def julian_centuries(jd: float) -> float:
    return (jd - J2000) / 36525.0


def mean_obliquity_deg(jd: float) -> float:
    """Meeus 22.2, IAU 1980 mean obliquity of the ecliptic, degrees."""
    t = julian_centuries(jd)
    return (84381.448 - 46.8150 * t - 0.00059 * t**2 + 0.001813 * t**3) / ASEC


def nutation_arcsec(jd: float) -> tuple:
    """Meeus 22 low-precision nutation. Returns (dpsi, deps) in arcseconds.

    Abbreviated series; quoted accuracy ~0.5" in dpsi, ~0.1" in deps. That is
    an order of magnitude below the 17" nutation amplitude it exists to model,
    which is all this reference needs: the point is to reproduce the leading
    term so an engine that DOES apply nutation is not falsely flagged.
    """
    t = julian_centuries(jd)
    omega = math.radians(125.04452 - 1934.136261 * t + 0.0020708 * t**2)
    l = math.radians(280.4665 + 36000.7698 * t)
    l_prime = math.radians(218.3165 + 481267.8813 * t)

    dpsi = (
        -17.20 * math.sin(omega)
        - 1.32 * math.sin(2 * l)
        - 0.23 * math.sin(2 * l_prime)
        + 0.21 * math.sin(2 * omega)
    )
    deps = (
        9.20 * math.cos(omega)
        + 0.57 * math.cos(2 * l)
        + 0.10 * math.cos(2 * l_prime)
        - 0.09 * math.cos(2 * omega)
    )
    return dpsi, deps


def true_obliquity_deg(jd: float) -> float:
    """Meeus 22.3: mean obliquity + nutation in obliquity. Degrees."""
    _, deps = nutation_arcsec(jd)
    return mean_obliquity_deg(jd) + deps / ASEC


def nutate_ra_dec(ra_deg: float, dec_deg: float, jd: float) -> tuple:
    """Mean equinox of date -> true equinox of date. Returns degrees.

    Implemented as the standard linearised nutation matrix (Explanatory
    Supplement / IAU 1980) acting on the mean-of-date unit vector:

        x' =  x - dpsi*cos(e)*y - dpsi*sin(e)*z
        y' =  y + dpsi*cos(e)*x - deps*z
        z' =  z + dpsi*sin(e)*x + deps*y

    The matrix form is used deliberately over the compact scalar apparent-place
    formulas: with dpsi = deps = 0 it is the exact identity, which
    test_nutation_is_identity asserts. A wrong scalar form fails that check,
    a wrong matrix cannot.
    """
    dpsi, deps = nutation_arcsec(jd)
    eps = math.radians(mean_obliquity_deg(jd))
    dpsi_r, deps_r = math.radians(dpsi / 3600.0), math.radians(deps / 3600.0)
    dpce, dpse = dpsi_r * math.cos(eps), dpsi_r * math.sin(eps)

    a, d = math.radians(ra_deg), math.radians(dec_deg)
    cd = math.cos(d)
    x, y, z = cd * math.cos(a), cd * math.sin(a), math.sin(d)

    xp = x - dpce * y - dpse * z
    yp = y + dpce * x - deps_r * z
    zp = z + dpse * x + deps_r * y

    ra = math.degrees(math.atan2(yp, xp)) % 360.0
    dec = math.degrees(math.asin(max(-1.0, min(1.0, zp))))
    return ra, dec


def test_nutation_is_identity() -> int:
    """With zero nutation the transform must be the identity. Returns failures.

    This is the guard that catches a malformed apparent-place formula. It
    monkeypatches nutation_arcsec, so it must run before any real comparison.
    """
    global nutation_arcsec
    real = nutation_arcsec
    nutation_arcsec = lambda jd: (0.0, 0.0)
    failures = 0
    try:
        for ra in (0.0, 37.5, 122.25, 271.0, 359.9):
            for dec in (-60.0, -12.3, 0.0, 27.4, 54.0):
                r, d = nutate_ra_dec(ra, dec, 2451545.0)
                if abs(sep(r, ra)) > 1e-9 or abs(d - dec) > 1e-9:
                    failures += 1
    finally:
        nutation_arcsec = real
    return failures


def precession_angles(t: float) -> tuple:
    """Meeus 21.4/21.5 with t == dt == T (J2000 start). Returns degrees."""
    zeta = (2306.2181 * t + 0.30188 * t**2 + 0.017998 * t**3) / ASEC
    z = (2306.2181 * t + 1.09468 * t**2 + 0.018203 * t**3) / ASEC
    theta = (2004.3109 * t - 0.42665 * t**2 - 0.041833 * t**3) / ASEC
    return zeta, z, theta


def precess_ra_dec(ra_deg: float, dec_deg: float, jd: float) -> tuple:
    """J2000 equatorial -> mean equinox/equator of `jd`. Returns degrees."""
    t = julian_centuries(jd)
    zeta, z, theta = precession_angles(t)

    # zeta/z/theta are already DEGREES here; converting them again is a bug.
    a = math.radians(ra_deg + zeta)
    d = math.radians(dec_deg)
    ad, cd = math.cos(d), math.sin(d)
    ct, st = math.cos(math.radians(theta)), math.sin(math.radians(theta))

    A = ad * math.sin(a)
    B = ct * ad * math.cos(a) - st * cd
    C = st * ad * math.cos(a) + ct * cd

    ra = math.degrees(math.atan2(A, B)) + z
    dec = math.degrees(math.asin(max(-1.0, min(1.0, C))))
    return ra % 360.0, dec


def radec_to_ecl_lon(ra_deg: float, dec_deg: float, eps_deg: float) -> float:
    ra, dec, eps = math.radians(ra_deg), math.radians(dec_deg), math.radians(eps_deg)
    num = math.sin(ra) * math.cos(eps) + math.tan(dec) * math.sin(eps)
    return math.degrees(math.atan2(num, math.cos(ra))) % 360.0


def ref_ecl_lon(ra_j2000, dec_j2000, jd, true_eps=True):
    ra, dec = precess_ra_dec(ra_j2000, dec_j2000, jd)
    eps = true_obliquity_deg(jd) if true_eps else mean_obliquity_deg(jd)
    return radec_to_ecl_lon(ra, dec, eps)


def sep(a: float, b: float) -> float:
    """Signed separation a - b, wrapped to (-180, 180]."""
    return ((a - b + 180.0) % 360.0) - 180.0


def jd_from_year(year: int) -> float:
    """Julian Day of Jan 1.0 (00:00 TT) in `year`, proleptic Gregorian.

    Self-tested in tests/test_parans_frames.py against three independent
    anchors: J2000.0, the J1900.0 standard epoch, and the engine's own
    verified birth-date JD.
    """
    if year <= 1582:
        raise ValueError("Gregorian calendar assumed; year must be > 1582")
    a = 1                                    # January: a = floor((14-1)/12)
    y = year + 4800 - a
    m = 1 + 12 * a - 3                       # January -> m = 10
    day = 1
    jdn = (day + (153 * m + 2) // 5 + 365 * y + y // 4
           - y // 100 + y // 400 - 32045)
    return jdn - 0.5                         # JD 0.0 is noon; want midnight


def ecliptic_longitude_deg(ra_deg: float, dec_deg: float, eps_deg: float) -> float:
    """Equatorial of date -> ecliptic longitude of date, degrees."""
    return radec_to_ecl_lon(ra_deg, dec_deg, eps_deg)


def ecliptic_latitude_deg(ra_deg: float, dec_deg: float, eps_deg: float) -> float:
    """Equatorial of date -> ecliptic latitude of date, degrees."""
    ra, dec, eps = math.radians(ra_deg), math.radians(dec_deg), math.radians(eps_deg)
    s = (math.sin(dec) * math.cos(eps)
         - math.cos(dec) * math.sin(eps) * math.sin(ra))
    return math.degrees(math.asin(max(-1.0, min(1.0, s))))
