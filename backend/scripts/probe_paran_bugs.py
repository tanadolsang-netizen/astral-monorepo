"""Measure the two fatal bugs in brady_parans (2026-09-27).

BUG 1: RAMC is set to the MC *ecliptic longitude* instead of the right
       ascension of the local meridian. These differ by up to ~2.5 deg,
       i.e. ~10 minutes of clock time, against a 2-minute orb.
BUG 2: ecliptic latitude is discarded, both for the planets (chart
       provides "latitude") and for the fixed stars, which are round-
       tripped ecliptic-lon -> RA/Dec assuming beta = 0.
"""
import datetime
import math
import sys

sys.path.insert(0, r"C:/AI/backend")

from src.services.parans_service import (  # noqa: E402
    OBLIQUITY,
    STARS,
    _ecliptic_matrix,
    _jd_ut,
    star_positions,
)

JD_TT = _jd_ut(datetime.datetime(1997, 5, 18, 22, 45, tzinfo=datetime.timezone.utc))


def ra_from_lon(lam_deg: float) -> float:
    lam = math.radians(lam_deg)
    return math.degrees(math.atan2(math.sin(lam) * math.cos(OBLIQUITY), math.cos(lam))) % 360


def dec_from_lon(lam_deg: float) -> float:
    lam = math.radians(lam_deg)
    return math.degrees(math.asin(math.sin(lam) * math.sin(OBLIQUITY)))


print("BUG 1  RAMC vs MC ecliptic longitude")
print(f"{'MC lon':>10} {'true RAMC':>11} {'error deg':>10} {'err minutes':>12} {'x orb(2m)':>10}")
for lam in (0.0, 45.0, 90.0, 180.0, 270.0, 316.3229):
    true_ramc = ra_from_lon(lam)
    err = (lam - true_ramc + 180) % 360 - 180
    print(f"{lam:10.4f} {true_ramc:11.4f} {err:+10.4f} {abs(err) * 4:12.2f} {abs(err) * 4 / 2:10.1f}")

print()
print("BUG 2  fixed stars: engine's beta=0 round-trip vs true J2000 RA/Dec")
lons = star_positions(JD_TT)
print(f"{'star':<11}{'eng RA':>9}{'true RA':>9}{'dRA':>8}{'eng Dec':>9}{'true Dec':>10}{'dDec':>9}")
for name in ("Sirius", "Vega", "Arcturus", "Antares", "Aldebaran", "Spica"):
    s = STARS[name]
    true_ra, true_dec = s["ra"] * 15.0, s["dec"]
    eng_ra, eng_dec = ra_from_lon(lons[name]), dec_from_lon(lons[name])
    d_ra = (eng_ra - true_ra + 180) % 360 - 180
    print(
        f"{name:<11}{eng_ra:9.3f}{true_ra:9.3f}{d_ra:+8.2f}"
        f"{eng_dec:9.3f}{true_dec:10.3f}{eng_dec - true_dec:+9.2f}"
    )

print()
print("BUG 3  planets: ecliptic latitude the chart already provides")
from src.services.chart_service import compute_chart  # noqa: E402

ch = compute_chart(
    "parans",
    datetime.date(1997, 5, 18),
    datetime.time(22, 45),
    tz_offset_hours=0.0,
    lat=13.12,
    lon=100.88,
)
print(f"{'body':<9}{'lon':>9}{'lat':>9}{'RA (beta=0)':>13}{'RA (true)':>11}{'dRA deg':>9}")
for b in ch["bodies"]:
    if b["body"] in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        lam, beta = math.radians(b["absolute_deg"]), math.radians(b.get("latitude") or 0.0)
        ra_fake = math.degrees(math.atan2(math.sin(lam) * math.cos(OBLIQUITY), math.cos(lam))) % 360
        ra_true = math.degrees(
            math.atan2(
                math.sin(lam) * math.cos(beta) * math.cos(OBLIQUITY)
                - math.cos(lam) * math.sin(beta),
                math.cos(beta) * math.cos(lam),
            )
        ) % 360
        d = (ra_fake - ra_true + 180) % 360 - 180
        print(f"{b['body']:<9}{b['absolute_deg']:9.3f}{b.get('latitude') or 0:9.3f}{ra_fake:13.3f}{ra_true:11.3f}{d:+9.2f}")

print()
print("BUG 4  round-trip: does the ecliptic matrix preserve the star position?")
m = _ecliptic_matrix(JD_TT)
print(f"  matrix[0] = {m[0]}")
print(f"  matrix[1] = {m[1]}")
print(f"  matrix[2] = {m[2]}")
