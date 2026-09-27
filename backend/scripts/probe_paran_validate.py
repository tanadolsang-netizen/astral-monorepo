"""Independent validation of the rebuilt paran geometry (probe, not a test).

Every check compares the engine against a path that shares no code with it:

  1. true obliquity   vs the IAU 1980 mean-obliquity series (a closed-form
                       formula the engine never evaluates) + a 9.2" nutation
                       allowance.
  2. planet RA/Dec    vs Skyfield's own `earth.at(t).observe(body).apparent()
                       .radec(epoch=t)`, i.e. the library's high-level path.
  3. star RA/Dec      vs `star_positions()`, via the ecliptic matrix, proving
                       the TETE input and the ecliptic output are one frame.
  4. rise hour angle  vs Skyfield's almanac: the Sun's real rise instant from
                       `almanac.find_risings` at a geometric 0-degree horizon,
                       with the hour angle rebuilt from `Time.gast`.

Run: PYTHONPATH=C:/AI/backend ./.venv/Scripts/python.exe scripts/probe_paran_validate.py
"""
import datetime
import math
import sys

import numpy as np

sys.path.insert(0, ".")

from skyfield import almanac  # noqa: E402
from skyfield.api import wgs84  # noqa: E402
from skyfield.timelib import Time  # noqa: E402

from src.services.ephemeris import earth, eph, ts  # noqa: E402
from src.services.parans_service import (  # noqa: E402
    STARS,
    _angle_lst,
    _frames,
    _jd_ut,
    _lonlat_to_radec,
    _obliquity_of_date,
    _rise_hour_angle,
    brady_parans,
    compute_chart,
    star_positions,
    star_radec,
)

RAD2DEG = 180.0 / math.pi
ASEC = 3600.0


def _as_times(result) -> list:
    """almanac returns a bare Time when a range contains exactly one event.

    NB: `Time.N` is Skyfield's rotation matrix, NOT a count -- use len().
    """
    if isinstance(result, Time):
        try:
            n = len(result)
        except TypeError:          # a single, scalar Time -- not an array
            return [result]
        return [result] if n == 1 else [result[i] for i in range(n)]
    return list(result)

# The subject's birth data.
DATE, TIME, TZ = "1997-05-19", "05:45", 7.0
LAT, LON = 13.3611, 100.9847

fails = []


def check(label, ok, detail):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label} -- {detail}")
    if not ok:
        fails.append(label)


_birth_local = datetime.datetime.fromisoformat(f"{DATE}T{TIME}:00")
birth_utc = _birth_local - datetime.timedelta(hours=TZ)
jd = _jd_ut(birth_utc)
t_tt = ts.tt(jd=jd)
m_ecl, m_tete = _frames(jd)
eps = _obliquity_of_date(m_ecl, m_tete)
earth = eph["earth"]

print("=" * 72)
print(f"subject: {DATE} {TIME} ICT at {LAT},{LON}  ->  JD(TT) {jd:.6f}")
print("=" * 72)

print()
print("CHECK 1 -- true obliquity of date vs the IAU 1980 mean-obliquity series")
print("-" * 72)
T = (jd - 2451545.0) / 36525.0
mean_eps_arcsec = 84381.406 - 46.836769 * T
recovered = eps * RAD2DEG * ASEC
delta = recovered - mean_eps_arcsec
print(f"  IAU 1980 low-order mean obliquity, T={T:+.6f} cent : {mean_eps_arcsec:12.4f}\"")
print(f"  engine's recovered true obliquity               : {recovered:12.4f}\"")
print(f"  difference                                        : {delta:+8.4f}\"")

# The low-order series is itself only good to a few arcsec, so the sharp test
# is Skyfield's own mean obliquity plus its own nutation-in-obliquity.
mean_exact = float(t_tt._mean_obliquity_radians) * RAD2DEG * ASEC
delta_eps = float(t_tt._nutation_angles_radians[1]) * RAD2DEG * ASEC
print(f"  Skyfield mean obliquity of date                  : {mean_exact:12.4f}\"")
print(f"  Skyfield nutation in obliquity                   : {delta_eps:+8.4f}\"")
print(f"  Skyfield true obliquity (mean + nutation)        : "
      f"{mean_exact + delta_eps:12.4f}\"")
resid = recovered - (mean_exact + delta_eps)
check("recovered obliquity == Skyfield mean + nutation (<0.01\")", abs(resid) < 0.01,
      f"residual {resid:+.5f}\"")
print(f"  (vs the low-order series the residual is {delta - delta_eps:+.4f}\", which is "
      f"the series' own truncation error, not the engine's)")

eps_1900 = _obliquity_of_date(*_frames(2415020.5)) * RAD2DEG
eps_2100 = _obliquity_of_date(*_frames(2488070.0)) * RAD2DEG
print(f"  obliquity 1900-01-01 = {eps_1900:.6f} deg")
print(f"  obliquity 2100-01-01 = {eps_2100:.6f} deg")
check("obliquity is date-dependent, not frozen",
      abs(eps_1900 - 23.4392911) * ASEC > 10.0,
      f"1900 sits {(eps_1900 - 23.4392911) * ASEC:+.1f}\" from the old J2000 constant")

print()
print("CHECK 2 -- planet RA/Dec vs Skyfield's own radec()")
print("-" * 72)
from src.services.chart_service import compute_chart  # noqa: E402
raw = compute_chart("parans", birth_utc.date(), birth_utc.time(),
                    tz_offset_hours=0, lat=LAT, lon=LON)
worst, worst_name = 0.0, ""
skipped = []
for b in raw["bodies"]:
    name = b["body"]
    try:
        body = eph[name.lower()]
    except KeyError:
        skipped.append(name)
        continue
    ra_h, dec_d, _dist = earth.at(t_tt).observe(body).apparent().radec(epoch=t_tt)
    ra_ref = ra_h.hours * 15.0
    dec_ref = dec_d.degrees
    ra_mine, dec_mine = _lonlat_to_radec(
        float(b["absolute_deg"]), float(b.get("latitude", 0.0)), eps)
    dra = (ra_mine - ra_ref) * ASEC
    ddec = (dec_mine - dec_ref) * ASEC
    d = math.hypot(dra, ddec)
    if d > worst:
        worst, worst_name = d, name
    print(f"  {name:<9} beta={float(b.get('latitude', 0.0)):+7.3f} deg   "
          f"dRA={dra:+9.2f}\"   dDec={ddec:+9.2f}\"")
check("every planet agrees with Skyfield to <1 arcmin", worst < 60.0,
      f"worst = {worst_name} at {worst:.2f}\"")
if skipped:
    print(f"  NOT CHECKED (absent from the de421 kernel): {', '.join(skipped)}")

moon = [b for b in raw["bodies"] if b["body"] == "Moon"]
if moon:
    print(f"  (the discarded ecliptic latitude of the Moon here is "
          f"{float(moon[0].get('latitude', 0.0)):+.3f} deg)")

print()
print("CHECK 3 -- the two star tables must describe the same sky")
print("-" * 72)
# build_ecliptic_matrix(t) == rot_x(-eps) @ M, and the TETE frame rotation is M
# itself, so TETE -> true ecliptic is rot_x(-eps) == m_ecl @ M^-1.
tete_to_ecl = np.asarray(m_ecl) @ np.asarray(m_tete).T
lon_ref = star_positions(jd)
worst, worst_name = 0.0, ""
residuals: list[tuple[float, str]] = []
for name, (ra, dec) in star_radec(jd).items():
    v = np.array([math.cos(math.radians(dec)) * math.cos(math.radians(ra)),
                  math.cos(math.radians(dec)) * math.sin(math.radians(ra)),
                  math.sin(math.radians(dec))])
    w = tete_to_ecl @ v
    lon = math.degrees(math.atan2(w[1], w[0])) % 360
    d = abs((lon - lon_ref[name] + 180.0) % 360 - 180.0) * ASEC
    residuals.append((d, name))
    if d > worst:
        worst, worst_name = d, name
n_stars = len(star_radec(jd))
residuals.sort()
print(f"  residuals over {n_stars} stars: min {residuals[0][0]:.3f}\" ({residuals[0][1]}), "
      f"max {residuals[-1][0]:.3f}\" ({residuals[-1][1]})")
print("  five largest: " + ", ".join(f"{n} {d:.2f}\"" for d, n in residuals[-5:]))
check(f"all {n_stars} stars round-trip < 0.01 arcsec", worst < 0.01,
      f"worst = {worst_name} at {worst:.2e}\"")

# At J2000 the TETE equinox IS the catalogue equinox, so this is a pure
# plumbing check on the table, independent of any rotation reasoning.
J2000 = 2451545.0
worst_j, worst_j_name = 0.0, ""
for name, (ra, dec) in star_radec(J2000).items():
    s = STARS[name]
    ref_ra = s["ra"] * 15.0
    d = max(abs((ra - ref_ra + 180.0) % 360 - 180.0), abs(dec - s["dec"])) * ASEC
    if d > worst_j:
        worst_j, worst_j_name = d, name
check("at J2000 the TETE coords equal the catalogue (<0.01\")", worst_j < 0.01,
      f"worst = {worst_j_name} at {worst_j:.2e}\" over {len(STARS)} stars")

print()
print("CHECK 4 -- rise hour angle vs Skyfield's almanac (geometric horizon)")
print("-" * 72)
topos = earth + wgs84.latlon(LAT, LON, elevation_m=0.0)
t_ut0 = ts.utc(1997, 5, 19, 0, 0, 0.0)
t_ut1 = ts.utc(1997, 5, 21, 0, 0, 0.0)
rises, _settings = almanac.find_risings(topos, eph["sun"], t_ut0, t_ut1,
                                        horizon_degrees=0.0)
rise_t = _as_times(rises)[0]
print(f"  next solar rise after the birth instant: {rise_t.utc_iso()} UT")
# Keep Skyfield's own Time objects: round-tripping through a JD would re-tag
# UT as TT and shift every downstream angle by ~69 s of Earth's rotation.
ra_r, dec_r, _ = earth.at(rise_t).observe(eph["sun"]).apparent().radec(epoch=rise_t)
dec_sun = dec_r.degrees
ra_sun = ra_r.hours * 15.0

lst_deg = (float(rise_t.gast) + LON / 15.0) * 15.0
ha_actual = (lst_deg - ra_sun) % 360.0
ha_engine = -_rise_hour_angle(LAT, dec_sun) % 360.0
print(f"  Sun dec at rise            : {dec_sun:+.5f} deg")
print(f"  actual hour angle at rise  : {ha_actual:.5f} deg")
print(f"  engine's target (-H_rise)  : {ha_engine:.5f} deg")
diff = abs((ha_actual - ha_engine + 180.0) % 360.0 - 180.0) * ASEC
check("engine's ASC target matches the real sunrise to <10 arcsec", diff < 10.0,
      f"{diff:.2f}\" = {diff / 15.0:.2f} s of clock time")

transits, _ = almanac.find_transits(topos, eph["sun"], t_ut0, t_ut1)
tr_t = _as_times(transits)[0]
ra_tr, _dec_tr, _ = earth.at(tr_t).observe(eph["sun"]).apparent().radec(epoch=tr_t)
lst_tr = (float(tr_t.gast) + LON / 15.0) * 15.0
ha_tr = (lst_tr - ra_tr.hours * 15.0) % 360.0
print(f"  actual hour angle at transit: {ha_tr:.6f} deg  (engine's MC target = 0)")
check("engine's MC target matches the real transit to <10 arcsec",
      min(ha_tr, 360 - ha_tr) * ASEC < 10.0, f"{min(ha_tr, 360 - ha_tr) * ASEC:.2f}\"")

print()
print("=" * 72)
print(f"RESULT: {'ALL PASS' if not fails else 'FAILURES -> ' + '; '.join(fails)}")
print("=" * 72)
sys.exit(1 if fails else 0)
