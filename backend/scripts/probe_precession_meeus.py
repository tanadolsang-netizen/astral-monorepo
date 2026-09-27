"""Independent precession/obiquity check via Meeus (Astronomical Algorithms).

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
import sys

sys.path.insert(0, ".")

from src.services import parans_service as ps

ASEC = 3600.0
J2000 = 2451545.0


def julian_centuries(jd: float) -> float:
    return (jd - J2000) / 36525.0


def mean_obliquity_deg(jd: float) -> float:
    """Meeus 22.2, IAU 1980 mean obliquity of the ecliptic, degrees."""
    t = julian_centuries(jd)
    return (84381.448 - 46.8150 * t - 0.00059 * t**2 + 0.001813 * t**3) / ASEC


def true_obliquity_deg(jd: float) -> float:
    """Meeus 22.3, mean + principal nutation term in obliquity, degrees."""
    t = julian_centuries(jd)
    omega = math.radians(-125.04452 - 1934.136261 * t)
    l = math.radians(280.4665 + 36000.7698 * t)
    l_prime = math.radians(218.3165 + 481267.8813 * t)
    d_eps = (
        -17.20 * math.sin(omega)
        - 1.32 * math.sin(2 * l)
        - 0.23 * math.sin(2 * l_prime)
        + 0.21 * math.sin(2 * omega)
    ) / ASEC
    return mean_obliquity_deg(jd) + d_eps


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


def main() -> None:
    print("self-test: T = 0 must be identity, obliquity must match Meeus 22.2")
    print(f"  precess_ra_dec(78.63, -8.202, J2000) = {precess_ra_dec(78.63, -8.202, J2000)}")
    print(f"  mean obliquity J2000 = {mean_obliquity_deg(J2000):.6f} deg (expect 23.4392794)")
    print(f"  true obliquity J2000 = {true_obliquity_deg(J2000):.6f} deg")
    print()

    epochs = (
        ("1900", 2415020.5),
        ("1997", 2450865.5),
        ("2025", 2460676.5),
        ("2100", 2488069.5),
    )

    print("A) precession only, obliquity-free: engine star_radec vs Meeus RA/Dec of date")
    print("   epoch  worst_dRA_arcsec  worst_dDec_arcsec  star")
    for label, jd in epochs:
        eng = ps.star_radec(jd)
        w_ra, w_dec, who = 0.0, 0.0, ""
        for name, s in ps.STARS.items():
            ra_ref, dec_ref = precess_ra_dec(s["ra"] * 15.0, s["dec"], jd)
            dra = abs(sep(eng[name][0], ra_ref)) * ASEC
            ddec = abs(eng[name][1] - dec_ref) * ASEC
            if dra > w_ra:
                w_ra, who = dra, name
            w_dec = max(w_dec, ddec)
        print(f"   {label:>6} {w_ra:16.3f} {w_dec:18.3f}  {who}")
    print()

    for label_true, flag in (
        ("TRUE obliquity (matches engine)", True),
        ("MEAN obliquity (isolates nutation)", False),
    ):
        print(f"B) full path, reference uses {label_true}")
        print("   epoch   worst_arcsec   mean_arcsec  star")
        for label, jd in epochs:
            pos = ps.star_positions(jd)
            resid = []
            for name, s in ps.STARS.items():
                ref = ref_ecl_lon(s["ra"] * 15.0, s["dec"], jd, true_eps=flag)
                resid.append((abs(sep(pos[name], ref)) * ASEC, name))
            resid.sort(reverse=True)
            mean = sum(r for r, _ in resid) / len(resid)
            print(f"   {label:>6} {resid[0][0]:13.3f} {mean:12.3f}  {resid[0][1]}")
        print()

    print("C) obliquity: engine _obliquity_of_date vs Meeus")
    print("   epoch      engine     mean      true   d_mean   d_true")
    for label, jd in epochs:
        m_ecl, m_tete = ps._frames(jd)
        eng = ps._obliquity_of_date(m_ecl, m_tete) * ASEC
        mn = mean_obliquity_deg(jd) * ASEC
        tr = true_obliquity_deg(jd) * ASEC
        print(f"   {label:>6} {eng:10.3f} {mn:9.3f} {tr:9.3f} {eng-mn:+8.3f} {eng-tr:+8.3f}")


if __name__ == "__main__":
    main()
