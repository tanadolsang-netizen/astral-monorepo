"""Measure what the production parans frame omits, against Swiss Ephemeris.

The production engine builds ICRF -> true-equator/equinox-of-date with
Skyfield's ``build_ecliptic_matrix`` / ``t.M`` (IAU 2006 precession, true
obliquity, nutation) but feeds it a J2000 mean-position catalogue that carries
no proper motion, and it never applies annual aberration. This probe quantifies
both omissions rather than asserting a bound.

Swiss Ephemeris is the reference, not a shared code path -- pyswisseph calls
Astrodienst's C library, and the star catalogue is Moshier/Abramov/Koch data
distributed as ``sefstars.txt``. No part of the production stack is reused.

Why the equatorial frame
    A paran is a horizon/meridian event, so it is reckoned in right ascension
    (see the Bowser "Aspects in Mundo" note in ``star_radec``). Ecliptic
    longitude is the wrong metric, and mixing the two frames is what produced
    the spurious ~1.39 deg/century "proper motion" in an earlier run of this
    probe -- that value is the general precession in longitude, not a star's
    motion.

Why position differencing
    ``fixstar_ut`` returns 0.0 in all three speed fields even with
    ``FLG_SPEED``, so per-star motion is recovered by differencing positions.

Swiss flag decomposition (always with FLG_EQUATORIAL)
    FLG_NOABERR                      nutation + proper motion  (no aberration)
    FLG_NOABERR | FLG_NONUT          proper motion only
    neither                          nutation + aberration + proper motion

Usage
    python scripts/probe_omitted_terms.py
"""
from __future__ import annotations

import math
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import swisseph as swe  # noqa: E402

from src.services import parans_service as ps  # noqa: E402

EPHE_DIR = os.environ.get("ASTRAL_EPHE", r"C:/AI/hermes/data/cache/scratch/eph")
OWNER_BIRTH = datetime(1997, 5, 18, 22, 45, tzinfo=timezone.utc)  # 19 May 05:45 ICT

# Swiss catalogue naming differs for a few production keys.
SWISS_NAME = {
    "Alcyone (Pleiades)": "Alcyone",
    "Aldebaran_N": "Aldebaran",
}

SIDEREAL_RATE = 15.04107  # deg/hr, RA of a fixed star on the meridian
WINDOW_MIN = 2.0          # production paran window


def swiss_radec(name: str, jd_ut: float, flags: int) -> tuple[float, float]:
    """(RA, Dec) of date in degrees from Swiss Ephemeris.

    ``fixstar_ut`` with ``FLG_EQUATORIAL`` returns (RA, Dec, dist, 0, 0, 0);
    the three trailing speed fields are always zero, so only the first two
    are returned here.
    """
    xx = swe.fixstar_ut(SWISS_NAME.get(name, name), jd_ut,
                        flags | swe.FLG_EQUATORIAL)[0]
    return xx[0] % 360.0, xx[1]


def vec(ra_deg: float, dec_deg: float) -> tuple[float, float, float]:
    a, d = math.radians(ra_deg), math.radians(dec_deg)
    return math.cos(d) * math.cos(a), math.cos(d) * math.sin(a), math.sin(d)


def sep_arcsec(r1: tuple[float, float], r2: tuple[float, float]) -> float:
    """Great-circle separation in arcsec -- well conditioned near the poles,
    unlike subtracting right ascensions."""
    u, v = vec(*r1), vec(*r2)
    dot = max(-1.0, min(1.0, sum(a * b for a, b in zip(u, v))))
    return math.degrees(math.acos(dot)) * 3600.0


def dra_arcsec(r1: tuple[float, float], r2: tuple[float, float]) -> float:
    """Signed right-ascension difference in arcsec (scaled by cos dec)."""
    u, v = vec(*r1), vec(*r2)
    return math.degrees(math.atan2(v[1], v[0]) - math.atan2(u[1], u[0])) * 3600.0


def to_minutes(arcsec_value: float) -> float:
    """Position error -> minutes of meridian-contact time."""
    return arcsec_value / (SIDEREAL_RATE * 3600.0) * 60.0


def main() -> int:
    path = os.path.join(EPHE_DIR, "sefstars.txt")
    if not os.path.isfile(path):
        print(f"sefstars.txt missing under {EPHE_DIR}")
        print("curl -L -o sefstars.txt https://raw.githubusercontent.com/aloistr/"
              "swisseph/master/ephe/sefstars.txt")
        return 2
    swe.set_ephe_path(EPHE_DIR)

    base = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL
    no_aber = base | swe.FLG_NOABERR
    pm_only = no_aber | swe.FLG_NONUT

    jd = ps._jd_ut(OWNER_BIRTH)
    jd_100 = ps._jd_ut(OWNER_BIRTH.replace(year=OWNER_BIRTH.year + 100))
    print(f"Swiss Ephemeris {swe.version}")
    print(f"epoch JD(TT) {jd:.6f}   ({OWNER_BIRTH.isoformat()} = 19 May 05:45 ICT)")
    print(f"100-yr span JD {jd_100:.6f} -- same calendar date, so annual")
    print("aberration largely cancels in the differencing below")
    print()

    eng = ps.star_radec(jd)
    eng_100 = ps.star_radec(jd_100)

    # --- 1. proper motion isolated over 100 years -----------------------
    print("=" * 76)
    print("1. PROPER MOTION, isolated over a 100-year same-date span")
    print("   change(Swiss, no aberration) minus change(production)")
    print("=" * 76)
    q = '"'
    print(f"{'star':<20} {'dRA ' + q + '/cy':>12} {'dDec ' + q + '/cy':>12} "
          f"{'great ' + q + '/cy':>12}")
    pm_rows = []
    for name in ps.STARS:
        try:
            s0 = swiss_radec(name, jd, no_aber)
            s1 = swiss_radec(name, jd_100, no_aber)
        except Exception as exc:
            pm_rows.append((name, None, f"skipped: {exc}"))
            continue
        dra = dra_arcsec(s0, s1) - dra_arcsec(eng[name], eng_100[name])
        ddec = (s1[1] - s0[1]) - (eng_100[name][1] - eng[name][1])
        # Magnitude of the vector difference between the two 100-year motion
        # vectors: |(s1-s0) - (e1-e0)|. Differencing separations or taking a
        # dot product of the differences instead would cancel (or reintroduce)
        # the ~5000" precession term and destroy the proper-motion signal.
        e0, e1 = vec(*eng[name]), vec(*eng_100[name])
        s0v, s1v = vec(*s0), vec(*s1)
        diff = [(a - b) - (c - d) for a, b, c, d in zip(s0v, s1v, e0, e1)]
        tang = math.hypot(*diff) * 206264.80624709636
        pm_rows.append((name, (dra, ddec, tang), None))

    worst = (0.0, "", 0.0)
    for name, val, err in pm_rows:
        if err:
            print(f"{name:<20} {'--':>12} {'--':>12}  {err}")
            continue
        dra, ddec, tang = val
        tot = math.hypot(dra, ddec)
        flag = "  <- near-pole: dRA singular, trust total" if abs(eng[name][1]) > 55 else ""
        print(f"{name:<20} {dra:12.3f} {ddec:12.3f} {tang:12.3f}{flag}")
        if abs(eng[name][1]) <= 55 and abs(tang) > abs(worst[0]):
            worst = (tang, name, dra)
    print()
    print(f"largest proper motion (dec <= 55 deg only, great-circle): "
          f"{worst[0]:.2f} arcsec/century  ({worst[1]}, dRA {worst[2]:+.2f})")
    print("docstring currently claims a bound of ~0.2 arcsec/century")
    print()

    # --- 2. term decomposition at the owner's birth epoch ----------------
    print("=" * 76)
    print("2. TERM DECOMPOSITION at the birth epoch")
    print("   production minus Swiss, arcsec of angular offset")
    print("=" * 76)
    print(f"{'star':<20} {'PM only':>10} {'PM+nut':>10} {'+aberr':>10} "
          f"{'min':>9} {'%window':>9}")
    rows = []
    for name in ps.STARS:
        if any(r[0] == name and r[2] for r in pm_rows):
            continue
        e = eng[name]
        d_pm = sep_arcsec(e, swiss_radec(name, jd, pm_only))
        d_nut = sep_arcsec(e, swiss_radec(name, jd, no_aber))
        d_all = sep_arcsec(e, swiss_radec(name, jd, base))
        rows.append((name, d_pm, d_nut, d_all))
    for name, d_pm, d_nut, d_all in sorted(rows, key=lambda r: -r[3]):
        mins = to_minutes(d_all)
        print(f"{name:<20} {d_pm:10.3f} {d_nut:10.3f} {d_all:10.3f} "
              f"{mins:9.3f} {mins / WINDOW_MIN * 100:8.1f}%")
    print()
    mx = max(r[3] for r in rows)
    mm = to_minutes(mx)
    print(f"worst star residual : {mx:.2f}\"  =  {mm:.2f} min of meridian motion")
    print(f"production window   : {WINDOW_MIN:.2f} min")
    verdict = ("EXCEEDS" if mm > WINDOW_MIN else
               "COMPARABLE TO" if mm > WINDOW_MIN / 2 else "well below")
    print(f"=> omitted proper motion + aberration are {verdict} the window "
          f"({mm / WINDOW_MIN * 100:.0f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
