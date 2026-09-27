"""Decisive nutation test for the parans frame validation.

The earlier residual of ~18" in RA was measured against a PRECESSION-ONLY
reference. The engine applies precession AND nutation. Nutation in longitude
has a 17.2" amplitude, so an 18" residual is the nutation term, not a defect.

This script separates the two effects instead of guessing:

  1. Compare the engine's true obliquity to Swiss ECL_NUT[0] and to the new
     Meeus 22.3 true obliquity. If the Meeus nutation series is right, both
     agree with each other and with Swiss.
  2. Compare engine RA/Dec against (a) Meeus precession only and (b) Meeus
     precession + nutation. If (b) collapses, the engine was never wrong.

Run:  ./.venv/Scripts/python.exe scripts/probe_nutation_split.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import swisseph as swe

import meeus_reference as meeus
from src.services import parans_service as ps

swe.set_ephe_path(None)

ASEC = 3600.0
EPOCHS = [
    ("J1900", meeus.jd_from_year(1900)),
    ("J1925", meeus.jd_from_year(1925)),
    ("J1950", meeus.jd_from_year(1950)),
    ("J1975", meeus.jd_from_year(1975)),
    ("J2000", 2451545.0),
    ("J2025", meeus.jd_from_year(2025)),
    ("J2050", meeus.jd_from_year(2050)),
    ("J2075", meeus.jd_from_year(2075)),
    ("J2100", meeus.jd_from_year(2100)),
]


def engine_star(jd_ut):
    """Public engine entry point, one row per star."""
    return ps.star_radec(jd_ut)


def arcsec(a_deg, b_deg):
    return (a_deg - b_deg) * ASEC


def section_obliquity():
    print()
    print("1) TRUE OBLIQUITY: engine / Meeus 22.3 / Swiss ECL_NUT[0]")
    print("     epoch      engine\"-swiss\"   meeus\"-swiss\"")
    worst_e = worst_m = 0.0
    for label, jd in EPOCHS:
        eng = math.degrees(ps._obliquity_of_date(*ps._frames(jd)))
        swi = swe.calc_ut(jd, swe.ECL_NUT)[0][0]
        mee = meeus.true_obliquity_deg(jd)
        de, dm = arcsec(eng, swi), arcsec(mee, swi)
        worst_e, worst_m = max(worst_e, abs(de)), max(worst_m, abs(dm))
        print("     {:<8} {:>14.4f} {:>14.4f}".format(label, de, dm))
    print("   -> worst |engine - swisseph| = {:.4f} arcsec".format(worst_e))
    print("   -> worst |meeus  - swisseph| = {:.4f} arcsec".format(worst_m))
    return worst_e, worst_m


def section_radec():
    print()
    print("2) RA/Dec OF DATE: engine vs Meeus, precession-only vs precession+nutation")
    print("   skips |dec| > 55 deg (RA is ill-conditioned near the pole)")
    print("     epoch   max|dRA|\" pre   max|dDec|\" pre   max|dRA|\" +nut   max|dDec|\" +nut")

    worst = [0.0, 0.0, 0.0, 0.0]
    worst_star = ["", "", "", ""]
    for label, jd in EPOCHS:
        eng = engine_star(jd)
        wp_ra = wp_dec = wn_ra = wn_dec = 0.0
        sp_ra = sp_dec = sn_ra = sn_dec = ""
        for name, star in ps.STARS.items():
            if abs(star["dec"]) > 55.0:
                continue
            ra0, dec0 = star["ra"] * 15.0, star["dec"]
            e_ra, e_dec = eng[name]

            p_ra, p_dec = meeus.precess_ra_dec(ra0, dec0, jd)
            n_ra, n_dec = meeus.nutate_ra_dec(p_ra, p_dec, jd)

            if abs(meeus.sep(e_ra, p_ra)) > wp_ra:
                wp_ra, sp_ra = abs(meeus.sep(e_ra, p_ra)), name
            if abs(e_dec - p_dec) > wp_dec:
                wp_dec, sp_dec = abs(e_dec - p_dec), name
            if abs(meeus.sep(e_ra, n_ra)) > wn_ra:
                wn_ra, sn_ra = abs(meeus.sep(e_ra, n_ra)), name
            if abs(e_dec - n_dec) > wn_dec:
                wn_dec, sn_dec = abs(e_dec - n_dec), name

        for i, v in enumerate((wp_ra, wp_dec, wn_ra, wn_dec)):
            if v > worst[i]:
                worst[i] = v
                worst_star[i] = (sp_ra, sp_dec, sn_ra, sn_dec)[i]
        print(
            "     {:<8} {:>14.4f} {:>15.4f} {:>16.4f} {:>17.4f}".format(
                label, wp_ra * ASEC, wp_dec * ASEC, wn_ra * ASEC, wn_dec * ASEC
            )
        )

    labels = ("dRA precession only", "dDec precession only",
              "dRA precession+nut", "dDec precession+nut")
    for v, s, lab in zip(worst, worst_star, labels):
        print("   -> worst {:<22} = {:>10.4f} arcsec  ({})".format(lab, v * ASEC, s))
    return worst


def section_nutation_amplitude():
    print()
    print("3) NUTATION AMPLITUDE over the epochs (arcsec)")
    print("     epoch        dpsi        deps")
    lo_psi = hi_psi = lo_eps = hi_eps = 0.0
    for label, jd in EPOCHS:
        dpsi, deps = meeus.nutation_arcsec(jd)
        lo_psi, hi_psi = min(lo_psi, dpsi), max(hi_psi, dpsi)
        lo_eps, hi_eps = min(lo_eps, deps), max(hi_eps, deps)
        print("     {:<8} {:>10.3f} {:>11.3f}".format(label, dpsi, deps))
    print("   -> dpsi range [{:.2f}, {:.2f}], deps range [{:.2f}, {:.2f}]".format(lo_psi, hi_psi, lo_eps, hi_eps))


def main():
    print("=" * 74)
    print("parans frame validation - nutation split")
    print("pyswisseph {}".format(swe.version))
    print("engine: {}".format(ps.__file__))
    print("=" * 74)

    e_obl, m_obl = section_obliquity()
    worst = section_radec()
    section_nutation_amplitude()

    print()
    print("=" * 74)
    print("SUMMARY")
    print("  engine obliquity vs swisseph        : {:.4f} arcsec".format(e_obl))
    print("  Meeus  true obliquity vs swisseph   : {:.4f} arcsec".format(m_obl))
    print("  engine RA  vs precession-only ref   : {:.4f} arcsec".format(worst[0] * ASEC))
    print("  engine Dec vs precession-only ref   : {:.4f} arcsec".format(worst[1] * ASEC))
    print("  engine RA  vs precession+nut ref    : {:.4f} arcsec".format(worst[2] * ASEC))
    print("  engine Dec vs precession+nut ref    : {:.4f} arcsec".format(worst[3] * ASEC))
    print("=" * 74)


if __name__ == "__main__":
    main()
