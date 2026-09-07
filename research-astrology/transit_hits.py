#!/usr/bin/env python3
"""Find EXACT dates major transits hit the natal chart (19 May 1997).
Uses JPL DE421 via skyfield — same as the vault's own tooling."""
import math
from skyfield.api import load

ts = load.timescale()
eph = load(r'C:\Users\ADMIN\Documents\Obsidian Vault\de421.bsp')
earth = eph['earth']

BODIES = {
    'Sun': 'sun', 'Moon': 'moon', 'Mercury': 'mercury', 'Venus': 'venus',
    'Mars': 'mars', 'Jupiter': 'jupiter barycenter', 'Saturn': 'saturn barycenter',
    'Uranus': 'uranus barycenter', 'Neptune': 'neptune barycenter',
}

def lon_of(name, t):
    astrom = earth.at(t).observe(eph[BODIES[name]])
    lat, lng, _ = astrom.ecliptic_latlon(epoch='date')
    return lng.degrees % 360

def ayanamsa(year_frac):
    return 23.68 + (year_frac - 1997) * (50.29 / 3600)

# scan daily from Aug 2026 to Dec 2028
from datetime import datetime, timedelta, timezone
start = datetime(2026, 8, 22, tzinfo=timezone.utc)
days = [(start + timedelta(days=i)) for i in range(0, 860)]

# precompute longitudes daily for slow movers
print("scanning...", flush=True)
lons = {b: [] for b in ['Jupiter', 'Saturn', 'Uranus', 'Neptune']}
times = []
for d in days:
    t = ts.from_datetime(d)
    times.append(d)
    for b in lons:
        lons[b].append(lon_of(b, t))

def find_crossings(body, target, tol_days=1):
    """exact-ish dates where body's ecliptic longitude crosses target (deg),
       handling retrograde multiple passes"""
    arr = lons[body]
    hits = []
    prev_diff = None
    for i in range(1, len(arr)):
        diff = (arr[i] - target + 180) % 360 - 180
        if prev_diff is not None and prev_diff * diff < 0:
            # linear interpolation within the day-step
            frac = abs(prev_diff) / (abs(prev_diff) + abs(diff))
            hit = times[i-1] + (times[i] - times[i-1]) * frac
            hits.append(hit)
        prev_diff = diff
    return hits

NATAL = {
    'Saturn_trop': 16.08 + 0,        # Aries 16.08 -> abs 16.08
    'Mars_trop':   150 + 19.32,      # Virgo 19.32
    'Mars_sid_tropical_equiv': None, # computed below
}
# natal sidereal Mars abs sidereal lon = 4*30+25.64=145.64; tropical equiv adds ayanamsa at birth 23.68 => 169.32? 
# BUT transit comparison uses CURRENT ayanamsa: tropical_lon(t) - ayanamsa(t) = sidereal_lon(t)
# So we want sidereal_lon_jupiter(t) == 145.64  => tropical_lon == 145.64 + ayanamsa(t)
def jupiter_hits_natal_sid_mars():
    hits = []
    prev = None
    for i, d in enumerate(times):
        ay = ayanamsa(d.year + d.timetuple().tm_yday / 365.25)
        target = 145.64 + ay
        cur = lons['Jupiter'][i]
        diff = (cur - target + 180) % 360 - 180
        if prev is not None and prev[1] * diff < 0:
            frac = abs(prev[1]) / (abs(prev[1]) + abs(diff))
            hits.append(times[i-1] + (times[i] - times[i-1]) * frac)
        prev = (d, diff)
    return hits

print("\n=== Saturn conj natal Saturn (tropical Aries 16.08°) ===")
for h in find_crossings('Saturn', NATAL['Saturn_trop']):
    print("  ", h.strftime('%Y-%m-%d'))

print("\n=== Saturn conj natal Descendant axis (Scorpio 25.96 / Taurus 25.96) ===")
for tgt, nm in [(205.96, 'Asc Scorpio 25.96'), (25.96, 'Desc Taurus 25.96')]:
    for h in find_crossings('Saturn', tgt):
        print(f"   [{nm}]", h.strftime('%Y-%m-%d'))

print("\n=== Jupiter conj natal Mars (tropical Virgo 19.32°) ===")
for h in find_crossings('Jupiter', NATAL['Mars_trop']):
    print("  ", h.strftime('%Y-%m-%d'))

print("\n=== Jupiter conj natal Mars (SIDEREAL Leo 25.64°, ayanamsa-adjusted) ===")
for h in jupiter_hits_natal_sid_mars():
    print("  ", h.strftime('%Y-%m-%d'))

print("\n=== Jupiter conj natal Sun (Taurus 28.05° = 58.05°) ===")
for h in find_crossings('Jupiter', 58.05):
    print("  ", h.strftime('%Y-%m-%d'))

print("\n=== Jupiter opposite natal MC / conj natal IC (MC Aqua 16.43 -> IC Leo 16.43 = 136.43°) ===")
for h in find_crossings('Jupiter', 136.43):
    print("  ", h.strftime('%Y-%m-%d'))

print("\n=== Uranus trine natal Jupiter (Jupiter Aqua 21.21 = 321.21; trine from Gemini 21.21 = 81.21 or Sag 21.21 = 261.21) ===")
for h in find_crossings('Uranus', 81.21):
    print("   [Gemini 21.21 trine]", h.strftime('%Y-%m-%d'))

print("\n=== Neptune conj natal Sun? (58.05) — far future check window only ===")
for h in find_crossings('Neptune', 58.05):
    print("  ", h.strftime('%Y-%m-%d'))
