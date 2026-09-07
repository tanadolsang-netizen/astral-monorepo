#!/usr/bin/env python3
"""Verify vault astrology computations: D9 navamsha, Chara Karaka, Vimshottari.
Test case: born 19 May 1997, 05:45 ICT, Chonburi (13.36N, 100.98E).
Sidereal (Lahiri) positions from the vault natal chart note.
"""
import math

# Sidereal Lahiri positions (from vault natal-chart-19-may-1997.md)
SIDEREAL = {
    'Sun':     (1,  4.37),   # sign index 1 = Taurus (0=Aries)
    'Moon':    (5, 23.69),   # Virgo
    'Mercury': (0,  9.70),   # Aries
    'Venus':   (1, 16.47),   # Taurus
    'Mars':    (4, 25.64),   # Leo
    'Jupiter': (9, 27.53),   # Capricorn
    'Saturn':  (11, 22.40),  # Pisces
    'Rahu':    (5,  2.07),   # Virgo
    'Ketu':    (11, 2.07),   # Pisces
}
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio',
         'Sagittarius','Capricorn','Aquarius','Pisces']

# ---- 1. Navamsha D9 (Parashari: element-based counting) ----
# navamsa within sign: each 3°20'. Counting start sign by element:
# movable (Aries,Cancer,Libra,Capricorn) start from themselves; fixed from 9th; dual from 5th.
def navamsa_sign(sign_idx, deg):
    part = int(deg // (30/9))  # 0..8
    if sign_idx % 3 == 0:      # movable: Aries=0, Cancer=3, Libra=6, Capricorn=9
        start = sign_idx
    elif sign_idx % 3 == 1:    # fixed
        start = (sign_idx + 8) % 12
    else:                      # dual
        start = (sign_idx + 4) % 12
    return (start + part) % 12, part + 1

print("=== NAVAMSHA D9 (Parashari element method) ===")
for body, (si, deg) in SIDEREAL.items():
    d9, part = navamsa_sign(si, deg)
    varg = " ** VARGOTTAMA **" if d9 == si else ""
    print(f"{body:8s} D1 {SIGNS[si]:11s} {deg:5.2f}° navamsa#{part} -> D9 {SIGNS[d9]:11s}{varg}")

# ---- 2. Chara Karaka (7-karaka, degree within sign, highest=AK) ----
print("\n=== CHARA KARAKA (7 scheme, no Rahu/Ketu) ===")
seven = {k: v[1] for k, v in SIDEREAL.items() if k not in ('Rahu','Ketu')}
rank = sorted(seven.items(), key=lambda x: -x[1])
names = ['AK (Atmakaraka/soul)','AmK (career)','BK (siblings/courage)','MK (mother/home)',
         'PuK (children/creativity)','GK (obstacles/relatives)','DK (Darakaraka/SPOUSE)']
for (body, deg), nm in zip(rank, names):
    print(f"{nm:28s} = {body:8s} {deg:5.2f}°")

# ---- 3. Nakshatra & Vimshottari ----
NAKS = ['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya',
        'Ashlesha','Magha','P.Phalguni','U.Phalguni','Hasta','Chitra','Swati','Vishakha',
        'Anuradha','Jyeshtha','Mula','P.Ashadha','U.Ashadha','Shravana','Dhanishta',
        'Shatabhisha','P.Bhadrapada','U.Bhadrapada','Revati']
LORDS = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
DASHA_YEARS = {'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,
               'Jupiter':16,'Saturn':19,'Mercury':17}

def nakshatra_of(sid_lon):
    span = 360/27  # 13.3333°
    idx = int(sid_lon // span)
    frac_into = (sid_lon - idx*span) / span
    pada = int(((sid_lon - idx*span) % span) / (span/4)) + 1
    return idx, frac_into, pada

moon_lon = 5*30 + 23.69  # = 173.69
idx, frac, pada = nakshatra_of(moon_lon)
print(f"\n=== NAKSHATRA / VIMSHOTTARI ===")
print(f"Moon sidereal lon = {moon_lon}° -> nakshatra #{idx+1} {NAKS[idx]}, pada {pada}, "
      f"{frac*100:.1f}% elapsed")
lord = LORDS[idx % 9]
print(f"Dasha lord of {NAKS[idx]} = {lord} ({DASHA_YEARS[lord]} yrs)")

# balance of first dasha
balance = (1 - frac) * DASHA_YEARS[lord]
print(f"Balance of {lord} MD at birth = {balance:.2f} years")

# birth 1997.38 (19 May 1997 ≈ 1997 + 139/365 ≈ 1997.381)
BIRTH = 1997.381
# sequence starting from lord
order = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
i0 = order.index(lord)
t = BIRTH + balance
seq = []
# first partial MD
seq.append((lord, BIRTH, t, 'partial (balance)'))
for k in range(1, 9):
    L = order[(i0 + k) % 9]
    seq.append((L, t, t + DASHA_YEARS[L], f'{DASHA_YEARS[L]}y'))
    t += DASHA_YEARS[L]
def fmt(y):
    yr = int(y); d = y - yr
    # approximate month/day
    m = int(d*12)+1; day = int((d*12 % 1)*30)+1
    return f"{yr}-{m:02d}-{day:02d}"
print("\nMahadasha sequence:")
for L, a, b, note in seq:
    flag = " <== NOW (Aug 2026)" if a <= 2026.64 < b else ""
    print(f"  {L:8s} {fmt(a)} -> {fmt(b)}   ({note}){flag}")

# Antardashas within Jupiter MD if current
for L, a, b, note in seq:
    if a <= 2026.64 < b:
        print(f"\nAntardashas within {L} MD:")
        j0 = order.index(L)
        ta = a
        for k in range(9):
            AD = order[(j0 + k) % 9]
            dur = DASHA_YEARS[L] * DASHA_YEARS[AD] / 120
            tb = ta + dur
            flag = " <== NOW" if ta <= 2026.64 < tb else ""
            print(f"  {L}-{AD:8s} {fmt(ta)} -> {fmt(tb)}{flag}")
            ta = tb
        break
