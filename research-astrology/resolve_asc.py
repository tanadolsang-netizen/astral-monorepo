#!/usr/bin/env python3
"""Resolve the Ascendant dispute: Scorpio 25.96 vs Taurus 25.96?
Compute ASC/MC from first principles (LST + obliquity + latitude).
Test both birth charts."""
import math

def jd_from_utc(y, mo, d, h, mi):
    # Julian Day (UT)
    if mo <= 2:
        y -= 1; mo += 12
    A = y // 100; B = A // 4
    return int(365.25*(y+4716)) + int(30.6001*(mo+1)) + d + B - 1524.5 + (h+mi/60)/24

def gmst_deg(jd):
    T = (jd - 2451545.0)/36525
    g = 280.46061837 + 360.98564736629*(jd-2451545.0) + 0.000387933*T*T - T*T*T/38710000
    return g % 360

def asc_mc(jd, lat, lon_east):
    lst = (gmst_deg(jd) + lon_east) % 360          # RAMC deg
    eps = math.radians(23.4393)
    phi = math.radians(lat)
    ramc = math.radians(lst)
    # MC ecliptic longitude
    mc = math.degrees(math.atan2(math.sin(ramc), math.cos(ramc)*math.cos(eps))) % 360
    # ASC
    y = -math.cos(ramc)
    x = math.sin(ramc)*math.cos(eps) + math.tan(phi)*math.sin(eps)
    asc = math.degrees(math.atan2(y, x)) % 360
    return asc, mc, lst

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sag','Cap','Aqu','Pisces']
def fmt(l):
    s = int(l//30); return f"{SIGNS[s]} {l%30:.2f}"

# --- Owner: 19 May 1997 05:45 ICT = 1997-05-18 22:45 UTC, Chonburi ---
jd = jd_from_utc(1997,5,18,22,45)
asc, mc, lst = asc_mc(jd, 13.36, 100.98)
print("OWNER 19 May 1997 05:45 ICT Chonburi:")
print("  LST =", round(lst,3), "deg")
print("  ASC =", fmt(asc))
print("  MC  =", fmt(mc))
# check sun position approx (should rise ~2h later? no—sunrise soon): sun ecl lon mid-May=58
print("  (Sun ~ Taurus 28 => sunrise when ASC reaches ~58)")
# what time does ASC hit Sun's longitude (~57.8)? scan minutes:
for mins in range(-120, 61, 10):
    jd2 = jd + mins/1440
    a, m, _ = asc_mc(jd2, 13.36, 100.98)
    print(f"   {mins:+4d} min -> ASC {fmt(a)}")

print()
# --- Mai: 18 Aug 2001 22:32 ICT = 15:32 UTC, Nonthaburi ---
jdm = jd_from_utc(2001,8,18,15,32)
am, mm, l2 = asc_mc(jdm, 13.86, 100.52)
print("MAI 18 Aug 2001 22:32 ICT Nonthaburi:")
print("  ASC =", fmt(am))
print("  MC  =", fmt(mm))
