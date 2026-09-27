"""Is the parans criterion wrong, or is ±2 min just rare?

The engine gates on BOTH bodies being within orb_minutes of the SAME angle
simultaneously. Brady's method requires the two bodies' POSITIONS ON THAT
ANGLE (POA) to coincide -- i.e. |p_sep_signed - s_sep_signed| small -- which
does NOT require either body to be sitting on the angle at the birth instant.

The two criteria select different pairings. Measure the distribution.
"""
import datetime
import math
import sys

sys.path.insert(0, r"C:/AI/backend")

from src.services.chart_service import compute_chart  # noqa: E402
from src.services.parans_service import (  # noqa: E402
    _angle_lst,
    _frames,
    _jd_ut,
    _lonlat_to_radec,
    _obliquity_of_date,
    _rise_hour_angle,
    star_radec,
)

BIRTH_UTC = datetime.datetime(1997, 5, 18, 22, 45, tzinfo=datetime.timezone.utc)
LAT, LON = 13.7, 101.1

jd = _jd_ut(BIRTH_UTC)
m_ecl, m_tete = _frames(jd)
eps = _obliquity_of_date(m_ecl, m_tete)

chart = compute_chart("parans", BIRTH_UTC.date(), BIRTH_UTC.time(),
                      tz_offset_hours=0, lat=LAT, lon=LON)
bodies = {b["body"]: (float(b["absolute_deg"]), float(b.get("latitude", 0.0)))
          for b in chart["bodies"]}
angles = {"ASC": chart["ascendant"]["absolute_deg"]}
for c in (chart.get("houses") or {}).get("cusps", []):
    if c.get("house") == 10:
        angles["MC"] = float(c["absolute_deg"])
angles.setdefault("MC", (angles["ASC"] + 90) % 360)
angles["DSC"] = (angles["ASC"] + 180) % 360
angles["IC"] = (angles["MC"] + 180) % 360

ramc = _angle_lst(angles["MC"], eps)
stars = star_radec(jd)


def signed_minutes(ra_deg: float, dec_deg: float, angle: str):
    """Signed POA offset in minutes of clock time (+ = past the angle)."""
    h = (ramc - ra_deg) % 360
    if angle == "MC":
        target = 0.0
    elif angle == "IC":
        target = 180.0
    else:
        h_rise = _rise_hour_angle(LAT, dec_deg)
        if h_rise is None:
            return None
        target = -h_rise if angle == "ASC" else h_rise
    d = (h - target + 180) % 360 - 180
    return d * (24 * 60) / 360.0


PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
rows = []
for pname in PLANETS:
    if pname not in bodies:
        continue
    pra, pdec = _lonlat_to_radec(bodies[pname][0], bodies[pname][1], eps)
    for sname, (sra, sdec) in stars.items():
        for ang in ("ASC", "MC", "DSC", "IC"):
            p = signed_minutes(pra, pdec, ang)
            s = signed_minutes(sra, sdec, ang)
            if p is None or s is None:
                continue
            rows.append((abs(p - s), max(abs(p), abs(s)), pname, sname, ang, p, s))

rows.sort()
print(f"candidate pairs: {len(rows)}")
print()
print("--- 15 tightest by TRUE POA difference |p_sep - s_sep| ---")
print(f"{'POA diff':>9}{'max|sep|':>9}  {'planet':<8}{'star':<11}{'ang':<5}{'p_sep':>8}{'s_sep':>8}")
for poa, mx, pn, sn, ang, p, s in rows[:15]:
    flag = "  <-- current engine MISSES this" if mx > 2.0 else ""
    print(f"{poa:9.2f}{mx:9.2f}  {pn:<8}{sn:<11}{ang:<5}{p:+8.2f}{s:+8.2f}{flag}")

for orb in (0.5, 1, 2, 3, 4, 6, 8, 10, 15, 20, 30):
    by_poa = sum(1 for r in rows if r[0] <= orb)
    by_engine = sum(1 for r in rows if r[1] <= orb)
    print(f"orb={orb:>5} min  ->  POA-equality: {by_poa:>3}   current engine: {by_engine:>3}")

near = [r for r in rows if r[0] <= 8]
print(f"\npairs with POA diff <= 8 min: {len(near)}")
print(f"  ... of those, current engine would catch: {sum(1 for r in near if r[1] <= 2)}")
