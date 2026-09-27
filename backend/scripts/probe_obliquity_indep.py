"""Independent IAU-1980 obliquity check (no Skyfield matrices involved)."""
import math
import sys

sys.path.insert(0, ".")

from src.services.parans_service import _frames, _obliquity_of_date

ASEC = 3600.0
JD = 2450587.448636389


def iau1980_true_obliquity(jd_tt: float) -> float:
    """eps = mean obliquity (IAU 1980 polynomial) + nutation in obliquity.

    Fully independent of Skyfield/SOFA: textbook series in arcseconds.
    Note the dominant nutation-in-OBLIQUITY term is +9.203" cos(Omega);
    the famous -17.20" sin(Omega) term belongs to nutation in LONGITUDE.
    """
    t = (jd_tt - 2451545.0) / 36525.0
    # Mean obliquity, degrees.
    eps0 = (84381.448
            - 46.8150 * t
            - 0.00059 * t * t
            + 0.001813 * t ** 3) / 3600.0
    # Nutation in obliquity, arcseconds.
    omega = math.radians(125.04452 - 1934.136261 * t)
    l_sun = math.radians(280.4665 + 36000.7698 * t)
    l_moon = math.radians(218.3165 + 481267.8813 * t)
    d_eps = (9.203 * math.cos(omega)
             + 0.573 * math.cos(2 * l_sun)
             + 0.098 * math.cos(2 * l_moon)
             + 0.063 * math.cos(2 * omega))
    return eps0 + d_eps / 3600.0


m_ecl, m_tete = _frames(JD)
got = math.degrees(_obliquity_of_date(m_ecl, m_tete))
ref = iau1980_true_obliquity(JD)
print(f"engine (from its own frames) = {got:.9f} deg")
print(f"IAU-1980 series (independent) = {ref:.9f} deg")
print(f"difference                    = {(got - ref) * ASEC:+.4f} arcsec")
print(f"Ignoring nutation, mean eps   = {iau1980_true_obliquity(JD) * 1:.9f}")
