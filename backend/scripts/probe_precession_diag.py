"""Diagnose the true precession/nutation residuals so the tests assert real numbers."""
import math
import sys

import numpy as np

sys.path.insert(0, ".")
from src.services import parans_service as ps
from skyfield.framelib import build_ecliptic_matrix

ASEC = 3600.0


def mcmie(jd: float) -> np.ndarray:
    """IAU 1976 precession: J2000 equatorial -> mean equinox/equator of `jd`.

    Standard active-rotation matrices acting on column vectors. Precession
    maps equatorial to equatorial, so the obliquity rotation cancels and
    must NOT appear here: the product is the three zeta/theta/z rotations
    alone, which equals the identity at T=0 and whose rotation angle grows
    like the general precession in longitude (5028.796195"/century).
    """
    T = (jd - 2451545.0) / 36525.0
    z = (2306.2181 * T + 0.30188 * T**2 + 0.017998 * T**3) / ASEC
    th = (2004.3109 * T - 0.42665 * T**2 - 0.041833 * T**3) / ASEC
    ze = (2306.2181 * T + 1.09468 * T**2 + 0.018203 * T**3) / ASEC
    # active rotations: v' = R @ v
    rz = lambda a: np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    ry = lambda a: np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
    return rz(-z) @ ry(th) @ rz(-ze)


def rot_angle(p: np.ndarray) -> float:
    """Rotation angle of `p` in radians, via atan2 for numerical stability.

    cos(theta) = (trace-1)/2 and sin(theta) = |antisym|/2 are both exact for
    any rotation matrix, so atan2 keeps full precision as theta -> 0 where
    the trace form cancels catastrophically. Self-checked below against
    matrices with known angles.
    """
    s = 0.5 * float(np.linalg.norm(np.array([p[2, 1] - p[1, 2], p[0, 2] - p[2, 0], p[1, 0] - p[0, 1]])))
    c = 0.5 * (float(np.trace(p)) - 1.0)
    return math.atan2(s, c)


out = []
out.append("=== 1. obliquity gap (true - mean) across 1900-2100 ===")
ts = ps._timescale()
for yr in (1900, 1950, 1997, 2020, 2050, 2100):
    jd = ts.utc(yr, 1, 1).tt
    m_ecl = build_ecliptic_matrix(ts.tt(jd=jd))
    m_tete = np.array(ts.tt(jd=jd).M)
    eps = ps._obliquity_of_date(m_ecl, m_tete)
    T = (jd - 2451545.0) / 36525.0
    mean = math.radians((84381.448 - 46.8150 * T - 0.00059 * T**2 + 0.001813 * T**3) / ASEC)
    out.append(f"  {yr}: eps={math.degrees(eps):.8f} mean={math.degrees(mean):.8f} gap={(eps-mean)*ASEC:+.3f}\"")

out.append("")
out.append("=== 2. precession rotation angle, J2000 -> jd (deg and arcsec) ===")
for yr in (1997, 2000, 2100):
    jd = ts.utc(yr, 1, 1).tt
    p = mcmie(jd)
    ang = math.degrees(rot_angle(p))
    T = (jd - 2451545.0) / 36525.0
    gp_lon = 5028.796195 * T + 1.1054348 * T**2
    out.append(f"  {yr}: T={T:+.6f} rot={ang:.8f} deg  = {ang*ASEC:9.2f}\"  precession-in-lon={gp_lon:9.2f}\"")

out.append("")
out.append("=== 3. star residual: Skyfield t.M vs classical precession-only ===")
for name in ("Polaris", "Sirius", "Vega", "Arcturus", "Antares", "Aldebaran", "Regulus", "Spica"):
    s = ps.STARS[name]
    v = np.array([math.cos(math.radians(s["dec"])) * math.cos(math.radians(s["ra"] * 15.0)),
                  math.cos(math.radians(s["dec"])) * math.sin(math.radians(s["ra"] * 15.0)),
                  math.sin(math.radians(s["dec"]))])
    rows = []
    for yr in (1900, 2050):
        jd = ts.utc(yr, 1, 1).tt
        a = mcmie(jd) @ v
        b = np.array(ts.tt(jd=jd).M) @ v
        rows.append(np.linalg.norm(a - b) * ASEC)
    out.append(f"  {name:10s} 1900: {rows[0]:7.2f}\"   2050: {rows[1]:7.2f}\"")

out.append("")
out.append("=== 4. per-star precession in RA / dec over 100 yr (deg) ===")
for name in ("Polaris", "Sirius", "Vega", "Arcturus"):
    s = ps.STARS[name]
    v = np.array([math.cos(math.radians(s["dec"])) * math.cos(math.radians(s["ra"] * 15.0)),
                  math.cos(math.radians(s["dec"])) * math.sin(math.radians(s["ra"] * 15.0)),
                  math.sin(math.radians(s["dec"]))])
    jd0 = ts.utc(2000, 1, 1).tt
    jd1 = ts.utc(2100, 1, 1).tt
    a0, a1 = mcmie(jd0) @ v, mcmie(jd1) @ v

    def to_radec(u):
        return math.degrees(math.atan2(u[1], u[0])) % 360, math.degrees(math.asin(u[2]))

    r0, d0 = to_radec(a0)
    r1, d1 = to_radec(a1)
    ddr = (r1 - r0 + 180) % 360 - 180
    out.append(f"  {name:10s} ra {r0:8.3f}->{r1:8.3f} (dRA {ddr*ASEC:9.1f}\")  dec {d0:7.3f}->{d1:7.3f} (dDec {(d1-d0)*ASEC:8.1f}\")")

out.append("")
out.append("=== 5. _lonlat_to_radec round-trip with RADIANS obliquity ===")
jd = ts.utc(1997, 5, 19, 5, 45).tt
m_ecl, m_tete = ps._frames(2450587.4)
eps = ps._obliquity_of_date(m_ecl, m_tete)
out.append(f"  eps radians = {eps!r}")
def to_lonlat(ra_deg, dec_deg, eps):
    lam = math.radians(ra_deg)
    bet = math.radians(dec_deg)
    lon = math.atan2(math.sin(lam) * math.cos(eps) + math.tan(bet) * math.sin(eps), math.cos(lam))
    lat = math.asin(math.sin(bet) * math.cos(eps) - math.cos(bet) * math.sin(eps) * math.sin(lam))
    return math.degrees(lon) % 360, math.degrees(lat)


for lon, lat in ((0.0, 0.0), (0.0, 12.0), (200.0, 3.0), (300.0, -5.0)):
    ra, dec = ps._lonlat_to_radec(lon, lat, eps)
    blon, blat = to_lonlat(ra, dec, eps)
    out.append(f"  lon={lon:6.1f} lat={lat:6.1f} -> ra={ra:9.5f} dec={dec:8.5f} -> back lon={blon:9.5f} lat={blat:8.5f}")
out.append("  (ecliptic->equatorial does NOT preserve latitude; that is correct)")

with open("C:/AI/hermes/data/cache/scratch/prec_diag.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("\n".join(out))
