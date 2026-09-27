"""Whole-chart accuracy: project vs Swiss Ephemeris.

Swiss Ephemeris is the reference for every planetary and lunar position. The
project runs Skyfield + DE421. Both are JPL integrals, so they should agree
closely; this measures the real residual instead of trusting the claim.

Run: ./.venv/Scripts/python.exe scripts/accuracy_report.py
"""

from __future__ import annotations

import math
import sys
from datetime import date, datetime, time, timezone

import swisseph as swe

sys.path.insert(0, "C:/AI/backend")

from src.services.ayanamsa import ayanamsa_for  # noqa: E402
from src.services.ephemeris import OBLIQUITY  # noqa: E402

SWE_CODE = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
    "True Node": swe.TRUE_NODE,
    "Chiron": swe.CHIRON,
    "Lilith": swe.OSCU_APOG,
}

# Models the project reports
MODELS = {
    "Sun": ("Sun", "geometric"),
    "Moon": ("Moon", "geometric"),
    "Mercury": ("Mercury", "geometric"),
    "Venus": ("Venus", "geometric"),
    "Mars": ("Mars", "geometric"),
    "Jupiter": ("Jupiter", "geometric"),
    "Saturn": ("Saturn", "geometric"),
    "Uranus": ("Uranus", "geometric"),
    "Neptune": ("Neptune", "geometric"),
    "Pluto": ("Pluto", "geometric"),
    "True Node": ("MeanNode", "mean"),
    "Chiron": ("Chiron", "geometric"),
    "Lilith": ("Lilith", "apogee"),
}

PROFILE = {
    "name": "M (Nai) 1997-05-19 05:45 ICT Chonburi",
    "dt_utc": datetime(1997, 5, 18, 22, 45, tzinfo=timezone.utc),
    "local_date": date(1997, 5, 19),
    "local_time": time(5, 45),
    "lat": 13.12,
    "lon": 100.88,
}


def swiss_apparent_lon(jd_ut: float) -> dict[str, float]:
    out: dict[str, float] = {}
    for label, code in SWE_CODE.items():
        r = swe.calc_ut(jd_ut, code, swe.FLG_SWIEPH | swe.FLG_SPEED)
        if r is None or r[0] is None:
            continue
        if swe.getswe_tname() is None:
            pass
        out[label] = float(r[0][0])
    # caller passes flag
    return out


def norm_diff(a: float, b: float) -> float:
    """Signed shortest angular difference a-b in degrees, in (-180, 180]."""
    d = (a - b) % 360.0
    if d > 180.0:
        d -= 360.0
    return d


def main() -> int:
    from src.services.chart_service import compute_chart
    from src.services.ephemeris import ts

    dt = PROFILE["dt_utc"]
    jd = ts.from_datetime(dt).tt
    ayan = ayanamsa_for("lahiri", dt)

    chart = compute_chart(
        name="M",
        date=PROFILE["local_date"],
        time=PROFILE["local_time"],
        lat=PROFILE["lat"],
        lon=PROFILE["lon"],
        tz_offset_hours=7.0,
        system="tropical",
    )
    project = {b["body"]: b["absolute_deg"] for b in chart.get("bodies", [])}

    jd_ut = swe.julday(dt.year, dt.month, dt.day,
                      dt.hour + dt.minute / 60.0, swe.GREG_CAL)

    print("=" * 74)
    print(f"ACCURACY REPORT  {PROFILE['name']}")
    print(f"JD(TT) = {jd:.6f}   Lahiri ayanamsa = {ayan:.6f} deg")
    print("=" * 74)
    print(f"{'body':<11}{'project':>11}{'swiss':>11}{'diff':>11}{'arcsec':>12}{'arcmin':>10}")
    print("-" * 74)

    rows = []
    for label, code in SWE_CODE.items():
        if label not in project:
            continue
        r = swe.calc_ut(jd_ut, code, swe.FLG_SWIEPH | swe.FLG_SPEED)
        if r is None or r[0] is None:
            continue
        ref = float(r[0][0])
        got = float(project[label])
        d = norm_diff(got, ref)
        rows.append((label, got, ref, d))
        flag = "  <-- " if abs(d) > 1.0 / 60.0 else ""
        print(f"{label:<11}{got:11.5f}{ref:11.5f}{d:+11.5f}"
              f"{d * 3600:+12.2f}{d * 60:+10.3f}{flag}")

    print("-" * 74)
    if rows:
        worst = max(rows, key=lambda x: abs(x[3]))
        mean = sum(abs(r[3]) for r in rows) / len(rows)
        print(f"  bodies compared : {len(rows)}")
        print(f"  mean abs error  : {mean * 3600:.3f} arcsec  ({mean * 60:.4f} arcmin)")
        print(f"  WORST           : {worst[0]} {worst[3] * 3600:+.2f} arcsec "
              f"({worst[3] * 60:+.3f} arcmin)")
        print(f"  mean obliquity  : {math.degrees(OBLIQUITY):.6f} deg "
              f"(J2000 IAU 1980 = 23.4392911)")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
