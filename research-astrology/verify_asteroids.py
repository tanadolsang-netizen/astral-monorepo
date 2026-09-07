# -*- coding: utf-8 -*-
"""
verify_asteroids.py — Compute Juno/Vesta/Pallas/Ceres/Chiron/Lilith for chart M
Test case: 19 May 1997 05:45 ICT (+07:00), Chonburi 13.36N 100.98E
Engine: pyswisseph (Swiss Ephemeris) + sepl/semo/seas_18.se1 files.
Cross-check anchors from 00-MASTER-unified-engine.md:
  Sun tropical = 28.05 Taurus · ASC tropical = 25.96 Gemini (Placidus)
  Chiron ~ 26deg55 Libra Rx (vault serennu interpolation)
Usage: python verify_asteroids.py            -> chart M (default)
       python verify_asteroids.py YYYY M D HH MM tz lat lon  -> any chart
"""
import sys, json

import swisseph as swe

EPHE_PATH = r"C:/AI/research-astrology/ephe"

BODIES = [
    ("Sun", swe.SUN), ("Moon", swe.MOON), ("Mercury", swe.MERCURY),
    ("Venus", swe.VENUS), ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
    ("Saturn", swe.SATURN), ("Chiron", swe.CHIRON),
    ("MeanLilith", swe.MEAN_APOG), ("OscuLilith", swe.OSCU_APOG),
    ("Ceres", swe.CERES), ("Pallas", swe.PALLAS),
    ("Juno", swe.JUNO), ("Vesta", swe.VESTA),
]
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra",
         "Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

def fmt(lon):
    sign = SIGNS[int(lon // 30)]
    d = lon % 30
    deg, m, s = int(d), int((d % 1) * 60), round((((d * 60) % 1) * 60))
    return f"{deg:02d}\u00b0{m:02d}'{s:02d}\" {sign}"

def main():
    a = sys.argv[1:]
    if len(a) == 8:
        Y, Mo, D, H, Mi, tz, lat, lon_geo = map(float, a)
        Y, Mo, D, H, Mi = int(Y), int(Mo), int(D), int(H), int(Mi)
    else:  # default: chart M
        Y, Mo, D, H, Mi, tz, lat, lon_geo = 1997, 5, 19, 5, 45, 7.0, 13.36, 100.98

    swe.set_ephe_path(EPHE_PATH)
    jd_ut = swe.julday(Y, Mo, D, H + Mi / 60.0 - tz)
    flg = swe.FLG_SWIEPH | swe.FLG_SPEED

    print(f"UT julday = {jd_ut:.6f}")
    rows = {}
    for name, pid in BODIES:
        try:
            pos, _ = swe.calc_ut(jd_ut, pid, flg)
        except Exception as e:
            rows[name] = {"error": str(e)}
            continue
        rows[name] = {
            "abs_deg": round(pos[0], 4),
            "position": fmt(pos[0]),
            "lon_speed": round(pos[3], 5),
            "retrograde": bool(pos[3] < 0),
        }
        print(f"{name:<11} {rows[name]['position']}  {'R' if pos[3] < 0 else ' '}  "
              f"speed {pos[3]:+.4f} deg/d")

    # Placidus houses + ASC cross-check
    cusps, ascmc = swe.houses(jd_ut, lat, lon_geo, b'P')
    asc = ascmc[0]
    mc = ascmc[1]
    print(f"ASC        {fmt(asc)}  (anchor: 25\u00b058' Gemini)")
    print(f"MC         {fmt(mc)}")
    rows["_asc_abs"] = round(asc, 4)
    rows["_asc"] = fmt(asc)

    # house placement of each body (Placidus cusps 1..12)
    def house_of(lo):
        for i in range(12):
            lo_c, hi_c = cusps[i], cusps[(i + 1) % 12]
            if hi_c < lo_c:  # wrap
                if lo >= lo_c or lo < hi_c:
                    return i + 1
            elif lo_c <= lo < hi_c:
                return i + 1
        return None

    for name in [n for n, _ in BODIES]:
        if "abs_deg" in rows.get(name, {}):
            rows[name]["house_placidus"] = house_of(rows[name]["abs_deg"])
    print(json.dumps({k: v.get("house_placidus") for k, v in rows.items()
                      if isinstance(v, dict)}, indent=None))

if __name__ == "__main__":
    main()
