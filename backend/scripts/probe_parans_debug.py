"""Locate the discrepancy between engine ecliptic longitude and the
Meeus IAU-1976 reference, printing raw values instead of residuals.

Meeus ch.21 (Astronomical Algorithms, 2nd ed.):
  21.4 -> J2000 alpha/delta to mean equinox/equator of date
  12.x -> equatorial to ecliptic, via mean obliquity of date
"""
import importlib.util
import sys

sys.path.insert(0, ".")

from src.services import parans_service as ps

ASEC = 3600.0
J2000 = 2451545.0

spec = importlib.util.spec_from_file_location("pm", "scripts/probe_precession_meeus.py")
pm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm)


def main():
    ts = ps._timescale()
    s = ps.STARS["Rigel"]
    ra_deg = s["ra"] * 15.0
    print(f"Rigel  ra={ra_deg:.4f} deg  dec={s['dec']:.4f} deg")
    print()
    print(f"{'label':>8} {'jd_tt':>18} {'engine':>10} {'ref':>10} {'resid_arcsec':>12}")
    for label, jd in (
        ("J2000", J2000),
        ("1900", 2415020.5),
        ("2025", 2460676.5),
        ("2100", 2488069.5),
    ):
        eng = ps.star_positions(jd)["Rigel"]
        ref = pm.ref_ecl_lon(ra_deg, s["dec"], jd)
        print(f"{label:>8} {jd:>18.4f} {eng:>10.4f} {ref:>10.4f} "
              f"{pm.sep(eng, ref) * ASEC:>12.2f}")

    print()
    print("mean obliquity of date (deg) at those epochs:")
    for label, jd in (("J2000", J2000), ("1900", 2415020.5), ("2100", 2488069.5)):
        print(f"  {label}: {pm.mean_obliquity_deg(jd):.6f}")

    print()
    print("precessed RA/Dec of Rigel (deg):")
    for label, jd in (("J2000", J2000), ("1900", 2415020.5), ("2100", 2488069.5)):
        ra, dec = pm.precess_ra_dec(ra_deg, s["dec"], jd)
        print(f"  {label}: ra={ra:.5f} dec={dec:.5f}")

    print()
    print("engine star_radec at the same epochs (degrees, if that is its unit):")
    for label, jd in (("J2000", J2000), ("1900", 2415020.5), ("2100", 2488069.5)):
        try:
            r = ps.star_radec(jd)
            print(f"  {label}: {r}")
        except Exception as exc:  # noqa: BLE001
            print(f"  {label}: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
