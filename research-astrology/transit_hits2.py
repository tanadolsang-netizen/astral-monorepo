#!/usr/bin/env python3
"""Round 2: Jupiter/Saturn hits on Mai's chart + remaining key points."""
from skyfield.api import load
from datetime import datetime, timedelta, timezone

ts = load.timescale()
eph = load(r'C:\Users\ADMIN\Documents\Obsidian Vault\de421.bsp')
earth = eph['earth']
BODIES = {'Sun':'sun','Moon':'moon','Mercury':'mercury','Venus':'venus','Mars':'mars',
          'Jupiter':'jupiter barycenter','Saturn':'saturn barycenter'}

def lon_of(name, t):
    lat, lng, _ = earth.at(t).observe(eph[BODIES[name]]).ecliptic_latlon(epoch='date')
    return lng.degrees % 360

start = datetime(2026, 8, 22, tzinfo=timezone.utc)
days = [start + timedelta(days=i) for i in range(0, 900)]
lons = {b: [] for b in ['Jupiter', 'Saturn']}
for d in days:
    t = ts.from_datetime(d)
    for b in lons:
        lons[b].append(lon_of(b, t))

def crossings(body, target, label):
    arr = lons[body]; prev=None; out=[]
    for i in range(1, len(arr)):
        diff = (arr[i]-target+180)%360-180
        if prev is not None and prev[1]*diff<0:
            frac = abs(prev[1])/(abs(prev[1])+abs(diff))
            out.append(days[i-1]+(days[i]-days[i-1])*frac)
        prev=(i,diff)
    print(f"{body} -> {label}")
    for h in out: print("   ", h.strftime('%Y-%m-%d'))

print("=== MAI side (tropical) ===")
crossings('Jupiter', 108.95+1, 'conj Mai Venus Cancer 19.90 (109.90)')
crossings('Jupiter', 138.95, 'conj Mai Moon Leo 18.95')
crossings('Jupiter', 145.74, 'conj Mai Sun Leo 25.74')
crossings('Jupiter', 163.59, 'conj Mai Saturn Gemini 13.59? NO - that is 73.59; skip')
print()
crossings('Jupiter', 197.37, 'conj M Moon Libra 17.37')
crossings('Jupiter', 190.15+30, 'conj M Venus Gemini 10.15 (70.15) — wrong window check')
print()
# fix: M Venus Gemini abs = 60+10.15=70.15 (Jupiter passed pre-window); Mai Saturn Gem 13.59 = 73.59
crossings('Jupiter', 73.59, '(already passed? verify) conj Mai Saturn 73.59')
crossings('Saturn', 73.59, 'Saturn conj Mai Saturn Gemini 13.59')
crossings('Saturn', 70.15, 'Saturn conj M Venus Gemini 10.15')
crossings('Saturn', 58.05, 'Saturn conj M Sun Taurus 28.05 (!!)')
crossings('Saturn', 55+3.38, 'Saturn conj M Mercury Taurus 3.38 (33.38)')
