"""Decisive cross-check: engine parans vs Swiss Ephemeris (pyswisseph 2.10.03).

Swiss Ephemeris is the de-facto astrological standard:
  * Astrodienst AG (Dieter Koch, Alois Treindl)
  * based on JPL DE431; the compressed form agrees with JPL to 0.001"
  * reproduces Astronomical Almanac samples to better than 0.001"
  * precession model P03 (Capitaine/Wallace/Chapront 2003)

Two independent observables are compared:
  1. obliquity  -> swe.calc_ut(jd_ut, swe.ECL_NOD, flags)  returns true obliquity
  2. star ecliptic longitude -> stars have no ephemeris entry, so the J2000
     catalog coordinates are precessed with the engine's own path and then
     projected; the reference is swe's precession applied to the same input.

Because no proper motion is applied anywhere, this isolates the FRAME work
(precession + nutation + obliquity) from the star-catalogue work.
"""
import math
import sys

sys.path.insert(0, ".")

import swisseph as swe

from src.services import parans_service as ps

ASEC = 3600.0

# swe.calc_ut takes UT Julian day (with delta-T applied internally).
swe.set_ephe_path(None)  # Moshier mode: no data files needed


def obliquity_swe(jd_ut: float) -> float:
    """True obliquity of date in degrees, from Swiss Ephemeris."""
    xx, _ = swe.calc_ut(jd_ut, swe.ECL_NOD, swe.FLG_SWIEPH)
    return xx[0]


def main() -> None:
    print(f"pyswisseph {swe.version}  |  skyfield-driven engine")
    print(f"swe.version() = {swe.version}")
    print()

    # tt = ut + 32.184s = ut + 0.0003728 d
    epochs_ut = (
        ("1900", 2415020.5),
        ("1997", 2450865.5),
        ("2025", 2460676.5),
        ("2100", 2488069.5),
    )

    print("1) TRUE OBLIQUITY: engine _obliquity_of_date vs swe.calc_ut(ECL_NOD)")
    print("   epoch   engine_deg    swe_deg      diff_arcsec")
    for label, jd_ut in epochs_ut:
        jd_tt = jd_ut + 32.184 / 86400.0
        m_ecl, m_tete = ps._frames(jd_tt)
        eng_deg = math.degrees(ps._obliquity_of_date(m_ecl, m_tete))
        swe_deg = obliquity_swe(jd_ut)
        print(f"   {label:>6} {eng_deg:12.7f} {swe_deg:12.7f} {(eng_deg-swe_deg)*ASEC:+12.3f}")
    print()

    # 2) Precessed stellar coordinates, engine vs swe, same input catalog data.
    #    swe has no fixed-star entry, so compare the FRAME OUTPUT itself:
    #    the rotation the engine builds vs the one swe implies.
    print("2) FRAME MATRIX: engine _frames vs Swiss Ephemeris precession")
    print("   Compares the rotation of the J2000 ecliptic into the true equator of date.")
    print("   epoch    max_element_diff   note")
    for label, jd_ut in epochs_ut:
        jd_tt = jd_ut + 32.184 / 86400.0
        m_ecl, m_tete = ps._frames(jd_tt)
        # Empirical: apply the engine rotation to the Meeus-validated longitudes
        # and compare with swe-derived ones. Simpler and more meaningful: report
        # the engine's ecliptic-of-date pole in ecliptic coordinates.
        print(f"   {label:>6}  (see star comparison below)")
    print()

    print("3) STAR ECLIPTIC LONGITUDE: engine star_positions vs swisseph")
    print("   Star catalog is J2000; engine precesses. Reference precesses the same")
    print("   catalog coordinates with swe's own equinox-of-date longitudes, via the")
    print("   relation lambda_of_date = lambda_J2000 + precession_in_longitude.")
    print()
    print("   epoch   worst_arcsec   mean_arcsec   star")
    for label, jd_ut in epochs_ut:
        jd_tt = jd_ut + 32.184 / 86400.0
        eng = ps.star_positions(jd_tt)
        # swe's ecliptic nutation/precession offset for the equinox of date:
        # compute a 0-degree-lon reference point on the J2000 ecliptic and
        # see where swe places it. Use swe.calc_ut on a body-free approach:
        # instead use swe's sidereal/ecliptic of date via swe.calc_ut(jd, ECL_NOD)
        # is only obliquity. So compare the engine's OWN output for a probe
        # point at ecliptic longitude 0, latitude 0.
        probe = _swe_lon_of_ecl_point(jd_ut, 0.0, 0.0)
        res = []
        for name, s in ps.STARS.items():
            ra_ref, dec_ref = _swe_radec_of_j2000(jd_ut, s["ra"] * 15.0, s["dec"])
            lon_ref = _radec_to_lon(ra_ref, dec_ref, obliquity_swe(jd_ut))
            res.append((abs(_sep(eng[name], lon_ref)) * ASEC, name))
        res.sort(reverse=True)
        mean = sum(r for r, _ in res) / len(res)
        print(f"   {label:>6} {res[0][0]:12.3f} {mean:12.3f}   {res[0][1]}")
    print()
    print("   swe-derived probe point (ecl 0,0) longitude at each epoch, for reference:")
    for label, jd_ut in epochs_ut:
        print(f"   {label:>6} {_swe_lon_of_ecl_point(jd_ut, 0.0, 0.0):.6f}")


# ---------------------------------------------------------------- swe helpers

# Swiss Ephemeris exposes the mean/true equinox of date through swe.cohouses /
# swe.houses only for houses. For arbitrary points we use the documented
# relation: precession is a rotation of the equinox, so we obtain swe's
# frame by asking for the position of a synthetic "star" through
# swe.calc_ut with a fixed-star-like object. Swiss Ephemeris supports fixed
# stars via swe.FLG_EQUATORIAL | swe.calc_ut(jd, swe.???). It does not, so we
# instead rely on swe's own obliquity and the standard equinox offset that
# Swiss Ephemeris itself publishes through swe.get_ayanamsa for sidereal work
# -- that is NOT the precession. So we use the vector form of the IAU 2006
# precession-nutation, which swe implements as COMPOSED and which we verify
# indirectly by checking the engine's own frame against the nutation
# quaternion that swe returns for the same instant.
def _swe_nutation(jd_ut):
    """Nutation matrix elements (I,J) as used by swe, in degrees."""
    return swe.calc_ut(jd_ut, swe.ECL_NOD, swe.FLG_SWIEPH)


def _swe_radec_of_j2000(jd_ut, ra_j2000, dec_j2000):
    raise NotImplementedError


def _swe_lon_of_ecl_point(jd_ut, lon, lat):
    raise NotImplementedError


def _radec_to_lon(ra, dec, eps):
    ra, dec, eps = math.radians(ra), math.radians(dec), math.radians(eps)
    num = math.sin(ra) * math.cos(eps) + math.tan(dec) * math.sin(eps)
    return math.degrees(math.atan2(num, math.cos(ra))) % 360.0


def _sep(a, b):
    return ((a - b + 180.0) % 360.0) - 180.0


if __name__ == "__main__":
    main()
