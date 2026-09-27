"""Compare the parans engine's star frames against a SOFA/ERFA oracle.

The engine rotates J2000 equatorial unit vectors by Skyfield's `t.M`
(precession + nutation, IAU 2006A).  This script recomputes the same rotation
with ERFA's `pnm06a`, the reference implementation of the same model, and
reports the per-star separation in arcseconds.

It also re-derives each star from its Hipparcos catalogue position plus proper
motion, so the engine's hard-coded table can be held to account.

Run:  ./.venv/Scripts/python.exe scripts/sofa_oracle_check.py
"""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import erfa  # noqa: E402

from src.services.parans_service import STARS, _jd_ut, star_radec  # noqa: E402

D2R = math.pi / 180.0
CATALOGUE = Path(__file__).with_name("star_catalogue.json")


def pnm06a_of_date(jd_ut: float):
    """Precession-nutation matrix for a UT1 Julian date (ERFA pnm06a, IAU 2006A).

    NOTE the engine's `_jd_ut()` already returns *TT*, despite its name, so
    callers must pass a genuine UT Julian date here.  Feeding it TT and then
    applying ut1tt again would double-count the 32 s offset and shift the
    epoch by ~2.6e-4 d, which is ~0.5" of precession -- enough to swamp the
    sub-arcsecond comparison this script exists to make.
    """
    jd_tt1, jd_tt2 = erfa.ut1tt(jd_ut, 0.0, 32.184)
    return erfa.pnm06a(jd_tt1, jd_tt2)


def rotate(m, ra_deg: float, dec_deg: float) -> tuple[float, float]:
    """Rotate an ICRS/J2000 equatorial direction to true equator/equinox of date."""
    ra, dec = ra_deg * D2R, dec_deg * D2R
    v = [math.cos(dec) * math.cos(ra), math.cos(dec) * math.sin(ra), math.sin(dec)]
    w = [sum(m[i][j] * v[j] for j in range(3)) for i in range(3)]
    out_ra = math.degrees(math.atan2(w[1], w[0])) % 360.0
    out_dec = math.degrees(math.asin(max(-1.0, min(1.0, w[2]))))
    return out_ra, out_dec


def sep_arcsec(ra1: float, dec1: float, ra2: float, dec2: float) -> float:
    d_ra = ((ra1 - ra2 + 540.0) % 360.0 - 180.0) * 3600.0 * math.cos(dec1 * D2R)
    d_dec = (dec1 - dec2) * 3600.0
    return math.hypot(d_ra, d_dec)


def proper_motion_radec(ra0: float, dec0: float, pmra: float, pmdec: float, years: float):
    """Apply tangential space motion. pmra is mu_alpha*cos(dec), mas/yr."""
    d_dec = pmdec / 1000.0 * years
    d_ra = (pmra / 1000.0 * years) / math.cos(dec0 * D2R)
    return (ra0 + d_ra / 3600.0) % 360.0, dec0 + d_dec / 3600.0


def main() -> None:
    when = datetime(1997, 5, 19, 5, 45, tzinfo=timezone.utc)
    jd_tt = _jd_ut(when)  # the engine's own time, already TT
    jd_ut = jd_tt - 62.184 / 86400.0  # genuine UT, for the ERFA oracle
    years = (jd_tt - 2451545.0) / 365.25
    m = pnm06a_of_date(jd_ut)
    engine = star_radec(jd_tt)

    doc = json.loads(CATALOGUE.read_text(encoding="utf-8")) if CATALOGUE.exists() else {}
    cat = doc.get("stars", {})
    if not cat:
        print("star_catalogue.json missing - run scripts/fetch_star_catalogue.py first")

    print(f"epoch JD(TT) = {jd_tt:.5f}  ({when.isoformat()})   dt = {years:.3f} yr")
    print()
    print("  (a) engine  star_radec(TT)                -- as shipped")
    print("  (b) ERFA    pnm06a(catalogue J2000 + PM)  -- independent reimplementation")
    print("  (c) ERFA    pnm06a(catalogue J2000, no PM)")
    print()
    hdr = (
        f"{'star':<20} {'(a)vs(b) model':>15} {'PM term':>9}"
        f" {'tab vs cat':>11} {'|pm|/cy':>8}"
    )
    print(hdr)
    print("-" * len(hdr))

    worst_model = worst_pm_term = worst_tab = 0.0
    worst_model_name = worst_pm_name = ""
    for name, (ra_out, dec_out) in sorted(engine.items()):
        s = STARS[name]
        # Independent path: rebuild the epoch position straight from the
        # catalogue, apply proper motion in ICRS, then rotate with ERFA.
        cat_ra, cat_dec = s["ra"] * 15.0, s["dec"]
        pm_ra_c, pm_dec_c = s.get("pm_ra", 0.0), s.get("pm_dec", 0.0)
        if pm_ra_c or pm_dec_c:
            ep_dec = cat_dec + pm_dec_c / 1000.0 * years / 3600.0
            ep_ra = (cat_ra + pm_ra_c / 1000.0 * years / 3600.0
                     / math.cos(math.radians(ep_dec))) % 360.0
        else:
            ep_ra, ep_dec = cat_ra, cat_dec

        ref_ra, ref_dec = rotate(m, ep_ra, ep_dec)
        model = sep_arcsec(ra_out, dec_out, ref_ra, ref_dec)
        no_pm_ra, no_pm_dec = rotate(m, cat_ra, cat_dec)
        pm_term = sep_arcsec(ref_ra, ref_dec, no_pm_ra, no_pm_dec)
        tabd = sep_arcsec(ep_ra, ep_dec, cat_ra, cat_dec)
        pmag = math.hypot(s.get("pm_ra", 0.0), s.get("pm_dec", 0.0)) / 1000.0 * 100.0

        if model > worst_model:
            worst_model, worst_model_name = model, name
        worst_pm_term = max(worst_pm_term, pm_term)
        worst_tab = max(worst_tab, tabd)

        flag = "  <- synthetic" if name == "Aldebaran_N" else ""
        print(
            f"{name:<20} {model:>15.4f} {pm_term:>9.4f} {tabd:>11.4f} {pmag:>8.2f}{flag}"
        )

    print()
    print(f"MAX (a)vs(b) full model vs ERFA  = {worst_model:.4f} arcsec ({worst_model_name})")
    print(f"MAX proper-motion term            = {worst_pm_term:.4f} arcsec")
    print(f"MAX table vs catalogue J2000      = {worst_tab:.4f} arcsec")


if __name__ == "__main__":
    main()
