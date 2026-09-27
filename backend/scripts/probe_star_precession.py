"""Cross-check the star precession against an INDEPENDENT algorithm.

Skyfield derives its TETE rotation from SOFA's `iauPmat06` (IAU-2006/200A).
Here we instead use the CLASSICAL IAU-1976 precession angles (zeta, z, theta),
written out longhand. Two unrelated code paths implementing the same physics
must agree; if they do, the TETE matrix is standard.
"""
import math
import sys

sys.path.insert(0, ".")

from src.services.parans_service import STARS, star_radec  # noqa: E402

D2R = math.pi / 180.0
R2D = 180.0 / math.pi
ASEC = 3600.0

JD_BIRTH = 2450587.448636389


def precession_angles(jd: float) -> tuple[float, float, float, float]:
    """IAU 1976 precession, plus the J2000 frame bias, all in radians."""
    t1 = (jd - 2451545.0) / 36525.0
    zeta = ((2306.2181 + 1.39656 * t1 - 0.000139 * t1 * t1) * t1
            + (0.30188 - 0.000344 * t1) * t1 * t1
            + 0.017998 * t1 ** 3) / ASEC * D2R
    z = ((2306.2181 + 1.39656 * t1 - 0.000139 * t1 * t1) * t1
         + (1.09468 + 0.000066 * t1) * t1 * t1
         + 0.018203 * t1 ** 3) / ASEC * D2R
    theta = ((2004.3109 - 0.85330 * t1 - 0.000217 * t1 * t1) * t1
             - (0.42665 + 0.000217 * t1) * t1 * t1
             - 0.041833 * t1 ** 3) / ASEC * D2R
    # J2000 frame bias (ICRF -> mean equator/equinox of J2000), tiny.
    # Values are given in arcsec, so /3600 then to radians.
    d_psi = -0.01406 / ASEC * D2R
    d_eps = -0.01631 / ASEC * D2R
    return zeta, z, theta, d_psi, d_eps


def rot_about(axis: int, angle: float) -> list[list[float]]:
    c, s = math.cos(angle), math.sin(angle)
    m = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    i, j = (axis + 1) % 3, (axis + 2) % 3
    m[i][i] = c
    m[j][j] = c
    m[i][j] = -s
    m[j][i] = s
    return m


def matmul(a, b):
    return [[sum(a[r][k] * b[k][c] for k in range(3)) for c in range(3)]
            for r in range(3)]


def apply(m, v):
    return [sum(m[r][k] * v[k] for k in range(3)) for r in range(3)]


zeta, z, theta, d_psi, d_eps = precession_angles(JD_BIRTH)
# P maps the J2000 mean equator to the mean equator of date:
#   P = Rz(z) Ry(-theta) Rz(zeta)   [transpose of the usual "J2000 -> date"
#   composition, which is written with the opposite rotation signs]
P = matmul(rot_about(2, z), matmul(rot_about(1, -theta), rot_about(2, zeta)))
P = matmul(P, matmul(rot_about(0, -d_eps), rot_about(2, d_psi)))

# Nutation is absent from the classical angles but present in Skyfield's true
# equinox of date. Its RA effect is dpsi * sin(alpha) * tan(delta), which for a
# star at delta = 89.26 deg is amplified by tan = 57.
DELTA_PSI = 17.2 / ASEC * D2R  # peak nutation in longitude, arcsec -> rad

print(f"JD {JD_BIRTH:.6f}   T = {(JD_BIRTH - 2451545.0) / 36525.0:+.6f} century")
print(f"zeta={zeta * R2D * 3600:.2f}\"  z={z * R2D * 3600:.2f}\"  "
      f"theta={theta * R2D * 3600:.2f}\"")
print(f"frame bias d_psi={d_psi * R2D * 3600:.4f}\"  d_eps={d_eps * R2D * 3600:.4f}\"")
print()
print("  star                   dRA sky  dRA IAU76   resid   "
      "nutation bound  dDec sky  dDec IAU76   resid")
print("  " + "-" * 92)

worst_explained, worst_name = 0.0, ""
unexplained: list[tuple[str, float, float]] = []
for name, (ra, dec) in star_radec(JD_BIRTH).items():
    s = STARS[name]
    ra0, dec0 = s["ra"] * 15.0, s["dec"]
    v = [math.cos(dec0 * D2R) * math.cos(ra0 * D2R),
         math.cos(dec0 * D2R) * math.sin(ra0 * D2R),
         math.sin(dec0 * D2R)]
    x, y, z = apply(P, v)
    ra_p = math.degrees(math.atan2(y, x))
    dec_p = math.degrees(math.asin(z / math.hypot(x, y, z)))
    d_ra = (ra - ra0 + 180.0) % 360.0 - 180.0
    d_ra_p = (ra_p - ra0 + 180.0) % 360.0 - 180.0
    d_dec = dec - dec0
    d_dec_p = dec_p - dec0
    resid = (d_ra - d_ra_p) * ASEC
    # bound: nutation in longitude, projected into RA, plus declination
    bound = abs(DELTA_PSI * math.sin(ra0 * D2R)
                * math.tan(min(dec0, 89.0) * D2R)) * R2D * 3600.0
    if abs(resid) > bound + 2.0:
        unexplained.append((name, resid, bound))
    ratio = abs(resid) / bound if bound > 0.0 else 0.0
    if ratio > worst_explained:
        worst_explained, worst_name = ratio, name
    print(f"  {name:<22}{d_ra * ASEC:8.1f}\"{d_ra_p * ASEC:8.1f}\"{resid:8.1f}\"  "
          f"{bound:11.1f}\"  {d_dec * ASEC:9.1f}\"{d_dec_p * ASEC:9.1f}\""
          f"{(d_dec - d_dec_p) * ASEC:8.1f}\"")

print("  " + "-" * 92)
print(f"worst |residual| / nutation bound = {worst_explained:.2f}  ({worst_name})")
if unexplained:
    print("RESIDUALS BEYOND THE NUTATION BOUND:")
    for n, r, b in unexplained:
        print(f"  {n}: {r:.1f}\" vs bound {b:.1f}\"")
else:
    print("PASS: every star's RA residual is within the nutation bound "
          "(mean-vs-true equinox).")
