"""One-off ground-truth measurement for writing the regression tests."""
import importlib.util as ilu
import math
import sys
from datetime import datetime

sys.path.insert(0, ".")

import numpy as np
from skyfield import almanac
from skyfield.api import wgs84

from src.services import parans_service as ps
from src.services.chart_service import compute_chart
from src.services.ephemeris import earth, eph, ts
from src.services.parans_service import _frames, _obliquity_of_date, _timescale

ASEC = 3600.0
D2R = math.pi / 180.0
JD = 2450587.4486
LAT, LON = 13.3611, 100.9847
UTC = datetime(1997, 5, 18, 22, 45)

# ---------------------------------------------------------------- obliquity
t = _timescale().tt(jd=JD)
m_ecl, m_tete = _frames(JD)
eps_impl = _obliquity_of_date(m_ecl, m_tete)
t_ref = ts.utc(1997, 5, 18, 22, 45, 0.0)
t_tt = ts.tt(jd=JD)
print("=== obliquity of date ===")
print(f"  engine          = {math.degrees(eps_impl):.9f} deg")
nut = np.asarray(t_tt.nutation_matrix())
print(f"  nutation matrix = "
      f"{math.degrees(math.acos(max(-1, min(1, float(nut[1][1]))))):.9f} deg")

# ------------------------------------------------- star_radec vs IAU-1976
spec = ilu.spec_from_file_location("tpf", "tests/test_parans_frames.py")
tpf = ilu.module_from_spec(spec)
try:
    spec.loader.exec_module(tpf)
    print("=== star_radec vs classical IAU-1976 (mean equinox of date) ===")
    prod = ps.star_radec(JD)
    for nm in sorted(tpf.J2000):
        pra, pdec = prod[nm]
        cra, cdec = tpf.classical_radec(tpf.J2000[nm], JD)
        s = math.degrees(math.sin(pdec * D2R) * math.cos(cdec * D2R)
                         * math.cos((cra - pra) * D2R)
                         + math.cos(pdec * D2R) * math.sin(cdec * D2R)) * ASEC
        bound = 17.2 * abs(math.sin(cra * D2R) * math.tan(cdec * D2R)) + 9.2
        print(f"  {nm:20s} sep={s:7.3f}\"  bound={bound:7.3f}\"  "
              f"{'OK' if s <= bound else 'OVER'}")
except Exception:
    import traceback
    traceback.print_exc()

# ------------------------------------------- chart lon/lat -> Skyfield radec
print("=== chart ecliptic lon/lat -> RA/Dec vs Skyfield radec ===")
chart = compute_chart("parans", UTC.date(), UTC.time(), tz_offset_hours=0,
                      lat=LAT, lon=LON)
worst, wname = 0.0, ""
for b in chart["bodies"]:
    nm = b["body"]
    try:
        seg = eph[nm.lower()][1]
    except (KeyError, IndexError):
        print(f"  {nm:9s} SKIP (absent from de421)")
        continue
    ra_h, dec_d, _ = earth.at(t_tt).observe(seg).apparent().radec(epoch=t_tt)
    mine = ps._lonlat_to_radec(float(b["absolute_deg"]),
                               float(b.get("latitude", 0.0)), eps_impl)
    dra = (mine[0] - ra_h.hours * 15.0) * ASEC
    ddec = (mine[1] - dec_d.degrees) * ASEC
    d = math.hypot(dra, ddec)
    if d > worst:
        worst, wname = d, nm
    print(f"  {nm:9s} lon={b['absolute_deg']:9.4f}  dRA={dra:+8.2f}\"  "
          f"dDec={ddec:+8.2f}\"")
print(f"  WORST = {wname} at {worst:.3f} arcsec")

# ----------------------------------------------------- sunrise / transit
print("=== sunrise / transit (Chonburi) ===")
t0 = ts.utc(1997, 5, 18, 0, 0, 0)
t1 = ts.utc(1997, 5, 19, 0, 0, 0)
topos = earth + wgs84.latlon(LAT, LON)
rises, settings = almanac.find_risings(topos, eph["sun"], t0, t1)
ri, se = list(rises), list(settings)
print(f"  risings={len(ri)}  settings={len(se)}")
if ri:
    u = ri[0].utc
    print(f"  sunrise UTC {u.hour:02d}:{u.minute:02d}:{u.second:02d}."
          f"{u.microsecond // 1000:03d}  tt_jd={ri[0].tt.jd:.9f}")
tr, an = almanac.find_transits(topos, eph["sun"], t0, t1)
trl, anl = list(tr), list(an)
print(f"  transits={len(trl)}  antitransits={len(anl)}")
if trl:
    print(f"  transit tt_jd={trl[0].tt.jd:.9f}")

# ------------------------------------------------------------ brady_parans
print("=== brady_parans ===")
for orb in (2, 8):
    c = ps.brady_parans("1997-05-19", "05:45", 7.0, LAT, LON, orb_minutes=orb)
    print(f"  orb={orb}: found={c['parans_found']} keys={list(c)}")
    for p in c["parans"][:4]:
        print("    ", p["planet"], p["planet_angle"], p["star"],
              p["star_angle"], p["separation_minutes"])
