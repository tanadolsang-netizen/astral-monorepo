"""Independent validation of the parans frame chain.

Two INDEPENDENT references, no shared code with the production path:

  1. Swiss Ephemeris (pyswisseph 2.10.03, Astrodienst AG) -- a real
     ephemeris. Gives the true + mean obliquity of date directly.
     swe.calc_ut(jd, swe.ECL_NUT) returns the "ecliptic nutation point";
     its [0] is the true obliquity and [1] the mean obliquity of date.
     https://www.astro.com/swisseph/  https://pypi.org/project/pyswisseph/

  2. Meeus, Astronomical Algorithms 2nd ed. ch.21 (precession) and
     ch.22 (obliquity, eqs 22.2/22.3) -- closed-form series, no
     rotation-matrix conventions to get wrong, so it cannot silently
     inherit a transpose/product-order bug from the engine.

All star coordinates are read from the engine's OWN catalog (ps.STARS)
so nothing here is hand-typed or recalled from memory.

Usage:  python scripts/probe_parans_validation.py
"""

import importlib.util
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import swisseph as swe  # noqa: E402

from src.services import parans_service as ps  # noqa: E402

ASEC = 3600.0
J2000 = 2451545.0
swe.set_ephe_path(None)  # no ephemeris files: forces built-in analytic series

load = importlib.util.spec_from_file_location(
    "meeus_ref", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "meeus_reference.py"))
meeus = importlib.util.module_from_spec(load)
load.loader.exec_module(meeus)

# J1900.0 .. J2100.0 sampled every 25 years, as TT Julian dates.
EPOCHS = [(f"J{y}", meeus.jd_from_year(y)) for y in range(1900, 2101, 25)]


def engine_positions(jd_tt):
    """Engine's ecliptic longitude of date, keyed by star name."""
    return ps.star_positions(jd_tt)


def engine_radec(jd_ut):
    """Engine's public (RA, Dec) of date, keyed by star name.

    Uses the real public entry point -- NOT a round trip through the
    engine's own frames, which would be tautological.
    """
    return ps.star_radec(jd_ut)


def main():
    print(f"pyswisseph {swe.version}  |  Swiss Ephemeris (Astrodienst AG)")
    print(f"engine: {ps.__file__}\n")

    # ---------------------------------------------------------------- A
    print("A) TRUE obliquity of date: engine vs Swiss Ephemeris ECL_NUT[0]")
    print(f"   {'epoch':>7} {'engine_deg':>13} {'swisseph_deg':>13} {'diff_arcsec':>12}")
    worst_obl = 0.0
    for label, jd in EPOCHS:
        m_ecl, m_tete = ps._frames(jd)
        eng = math.degrees(ps._obliquity_of_date(m_ecl, m_tete))
        ref, _flag = swe.calc_ut(jd, swe.ECL_NUT)[0][0], None
        d = (eng - ref) * ASEC
        worst_obl = max(worst_obl, abs(d))
        print(f"   {label:>7} {eng:13.7f} {ref:13.7f} {d:12.4f}")
    print(f"   -> worst |engine - swisseph| = {worst_obl:.4f} arcsec\n")

    # ---------------------------------------------------------------- B
    print("B) MEAN obliquity of date: engine-side mean vs swisseph ECL_NUT[1]")
    print("   (engine has no separate mean-obliquity routine; this compares the")
    print("    independent Meeus 22.2 series to swisseph, closing that gap)")
    print(f"   {'epoch':>7} {'meeus_deg':>13} {'swisseph_deg':>13} {'diff_arcsec':>12}")
    worst_mean = 0.0
    for label, jd in EPOCHS:
        m = meeus.mean_obliquity_deg(jd)
        ref = swe.calc_ut(jd, swe.ECL_NUT)[0][1]
        d = (m - ref) * ASEC
        worst_mean = max(worst_mean, abs(d))
        print(f"   {label:>7} {m:13.7f} {ref:13.7f} {d:12.4f}")
    print(f"   -> worst |meeus - swisseph| = {worst_mean:.4f} arcsec\n")

    # ---------------------------------------------------------------- C
    print("C) PRECESSION: engine RA/Dec of date vs Meeus 21.4/21.5 (IAU-1976)")
    print("   skips |dec| > 55 deg (RA is ill-conditioned near the pole)")
    print("   epoch      max|dRA|\"  max|dDec|\"  max_sep\"  worst star")
    worst_dra = worst_ddec = 0.0
    for label, jd in EPOCHS:
        eng = engine_radec(jd)
        dra = dd = 0.0
        worst = ""
        for name, s in ps.STARS.items():
            if abs(s["dec"]) > 55.0:
                continue
            ra0, dec0 = s["ra"] * 15.0, s["dec"]
            mra, mdec = meeus.precess_ra_dec(ra0, dec0, jd)
            era, edec = eng[name]
            dra_here = meeus.sep(era, mra) * math.cos(math.radians(mdec))
            dd_here = edec - mdec
            if abs(dra_here) > dra:
                dra = abs(dra_here)
            if abs(dd_here) > dd:
                dd = abs(dd_here)
                worst = name
        worst_dra = max(worst_dra, dra * ASEC)
        worst_ddec = max(worst_ddec, dd * ASEC)
        print(f"   {label:>7} {dra * ASEC:11.3f} {dd * ASEC:12.3f} "
              f"{max(dra, abs(dd)) * ASEC:11.3f}  {worst}")
    print("   -> worst dRA = {:.3f}\", worst dDec = {:.3f}\"\n".format(worst_dra, worst_ddec))

    # ---------------------------------------------------------------- D
    print("D) ECLIPTIC LONGITUDE: engine vs Meeus precession + ecliptic rotation")
    print("   epoch      max|dLambda|\"  max|dBeta|\"  worst star")
    worst_lam = worst_bet = 0.0
    for label, jd in EPOCHS:
        pos = engine_positions(jd)
        radec = engine_radec(jd)
        # The engine's ecliptic longitude is referred to the TETE (true
        # equator/equinox) frame, so the reference must use the SAME
        # obliquity. Feeding the reference a different frame would measure a
        # frame convention difference, not an engine error.
        eps_deg = math.degrees(ps._obliquity_of_date(*ps._frames(jd)))
        lam = bet = 0.0
        worst = ""
        for name, s in ps.STARS.items():
            if abs(s["dec"]) > 55.0:
                continue
            ra0, dec0 = s["ra"] * 15.0, s["dec"]
            mra, mdec = meeus.precess_ra_dec(ra0, dec0, jd)
            mlam = meeus.ecliptic_longitude_deg(mra, mdec, eps_deg)
            mbet = meeus.ecliptic_latitude_deg(mra, mdec, eps_deg)
            dl = meeus.sep(pos[name], mlam) * ASEC
            # engine beta is not a public output; rotate the engine's own
            # equatorial-of-date into the same ecliptic frame (orthonormal,
            # so this is exact) and compare against the reference beta.
            _era, _edec = radec[name]
            ebet = meeus.ecliptic_latitude_deg(_era, _edec, eps_deg)
            db = (ebet - mbet) * ASEC
            if abs(dl) > lam:
                lam = abs(dl)
                worst = name
            bet = max(bet, abs(db))
        worst_lam = max(worst_lam, lam)
        worst_bet = max(worst_bet, bet)
        print(f"   {label:>7} {lam:14.3f} {bet:12.3f}  {worst}")
    print(f"   -> worst |dLambda| = {worst_lam:.3f} arcsec\n")

    # ---------------------------------------------------------------- E
    print("E) PRECESSION RATE: implied general precession in longitude")
    print("   measured from the engine itself, J2000 -> J2100")
    p2000 = engine_positions(J2000)
    p2100 = engine_positions(meeus.jd_from_year(2100))
    for name in ("Regulus", "Spica", "Antares"):
        if name in p2000:
            dl = (p2100[name] - p2000[name]) % 360.0
            print(f"   {name:9s} dLambda = {dl * ASEC:9.1f}\" over 100 yr "
                  f"= {dl * ASEC / 100.0:5.2f}\"/yr")
    print("   IAU-1976 general precession in longitude = 50.2879\"/yr (Meeus 21.5)")


if __name__ == "__main__":
    main()
