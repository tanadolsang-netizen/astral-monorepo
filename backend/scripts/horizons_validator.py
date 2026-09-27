"""Independent truth check: our engine vs JPL Horizons (the gold standard).

Neither Skyfield/DE421 nor Swiss/Moshier is the arbiter here — Horizons is
JPL's own DE440 driver, so agreement with it is real evidence.

Run: ./.venv/Scripts/python.exe -m scripts.horizons_validator
"""
import json
import math
import ssl
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, time as dtime

sys.path.insert(0, ".")

from src.services.chart_service import compute_chart, lahiri_ayanamsa  # noqa: E402

API = "https://ssd.jpl.nasa.gov/api/horizons.api"
CTX = ssl.create_default_context()

# (year, month, day, hour, minute, lat, lon)
CASES = [
    (1901, 12, 13, 20, 45, 13.3611, 100.9847),
    (1935, 3, 8, 4, 20, 13.3611, 100.9847),
    (1969, 7, 20, 20, 17, 40.7128, -74.0060),
    (1987, 11, 3, 5, 0, 13.3611, 100.9847),
    (1997, 5, 19, 22, 45, 13.3611, 100.9847),
    (2001, 8, 18, 22, 32, 13.8591, 100.5217),
    (2010, 6, 15, 8, 30, 13.3611, 100.9847),
    (2026, 9, 27, 0, 0, 13.3611, 100.9847),
    (2040, 1, 1, 6, 0, 13.3611, 100.9847),
]

# Horizons COMMAND codes
TARGETS = {
    "Sun": "10", "Moon": "301", "Mercury": "199", "Venus": "299",
    "Mars": "499", "Jupiter": "599", "Saturn": "699", "Uranus": "799",
    "Neptune": "899", "Pluto": "999",
}


def sec(deg):
    return deg * 3600.0


def d360(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def horizons(command: str, y, mo, d, hh, mm) -> tuple[float, float, float] | None:
    """Return (ecliptic lon of date, lat, distance AU) from Horizons, or None."""
    ut = f"{y:04d}-{mo:02d}-{d:02d} {hh:02d}:{mm:02d}"
    params = {
        "format": "text", "COMMAND": f"'{command}'", "OBJ_DATA": "NO",
        "MAKE_EPHEM": "YES", "EPHEM_TYPE": "OBSERVER",
        "CENTER": "'500@399'",            # geocentric
        "START_TIME": f"'{ut}'", "STOP_TIME": f"'{ut}'", "STEP_SIZE": "'1 h'",
        "QUANTITIES": "'20,24'",           # 20 = observer ecliptic lon/lat, 24 = range
        "REF_SYSTEM": "'ICRF'", "CAL_TYPE": "'GREGORIAN'",
        "CAL_FORMAT": "'CAL'", "TIME_DIGITS": "'SECONDS'",
        "ANG_FORMAT": "'DEG'", "CSV_FORMAT": "'YES'",
        "EXTRA_PREC": "'YES'",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, context=CTX, timeout=60) as r:
            txt = r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"    ! network: {e}")
        return None
    if "$$SOE" not in txt:
        return None
    body = txt.split("$$SOE")[1].split("$$EOE")[0].strip()
    lines = [ln for ln in body.splitlines() if ln.strip()]
    if not lines:
        return None
    # CSV: ecliptic lon, lat, range  -> index 3,4,5 after the leading date cols
    cols = lines[0].split(",")
    try:
        return float(cols[3]), float(cols[4]), float(cols[5])
    except (IndexError, ValueError):
        return None


def main():
    print("=" * 84)
    print("JPL HORIZONS (DE440) VALIDATION — observer ecliptic of date, geocentric")
    print("=" * 84)
    print(f"{'date':<20}{'body':<10}{'ours':>12}{'Horizons':>12}{'delta':>12}{'arcsec':>10}")
    worst = {}
    for y, mo, d, hh, mm, lat, lon in CASES:
        c = compute_chart("h", date(y, mo, d), dtime(hh, mm), 0.0, lat, lon,
                          "tropical", "placidus")
        ours = {b["body"]: b["absolute_deg"] for b in c["bodies"]}
        for name, cmd in TARGETS.items():
            r = horizons(cmd, y, mo, d, hh, mm)
            if r is None:
                print(f"{y}-{mo:02d}-{d:02d}".ljust(20) + f"{name:<10}  <unavailable>")
                continue
            ref_lon = r[0] % 360
            ds = sec(d360(ours[name], ref_lon))
            worst[name] = max(worst.get(name, 0.0), ds)
            print(f"{y}-{mo:02d}-{d:02d}".ljust(20)
                  + f"{name:<10}{ours[name]:12.6f}{ref_lon:12.6f}"
                  + f"{d360(ours[name], ref_lon):12.6f}{ds:10.3f}")
        print()

    print("-" * 84)
    print(f"{'WORST':<20}" + "".join(f"{k[:8]:>10}" for k in TARGETS))
    print("arcsec".ljust(20) + "".join(f"{worst.get(k, 0):10.3f}" for k in TARGETS))
    print("-" * 84)

    # ---- Lahiri ayanamsa, checked against the published anchor values -------
    print("\nLAHIRI (CHITRAKSHI / CHITRAPAKSHA) AYANAMSA CHECK")
    print("Authoritative values (Swiss Ephemeris / Indian Govt. PANC, Vedic):")
    print("  1900 = 22°27'38\"   1950 = 23°09'32\"   2000 = 23°51'11\"")
    print("  2026 ≈ 24°12'xx\"    (= 23.85306 + 50.29\"/yr from J2000)")
    print()
    for y in (1900, 1950, 2000, 2026, 2050):
        j2000_plus = 23.85306 + (y + 0.5 - 2000.0) * 50.29 / 3600.0
        ours = lahiri_ayanamsa(y + 0.5)
        print(f"  {y}:  ours={ours:.6f} deg   "
              f"true Lahiri={j2000_plus:.6f} deg   "
              f"error={sec(ours - j2000_plus):+9.1f} arcsec "
              f"({(ours - j2000_plus) * 60:+.2f} arcmin)")

    print("\nCAUSE: chart_service.lahiri_ayanamsa() is a straight line fitted to")
    print("a wrong intercept (23.68 at year 1997 instead of 23.7955). The slope")
    print("50.29\"/yr is right; the offset is wrong by ~0.13 deg = 7.5 arcmin.")
    print("That 0.13 deg lands on EVERY sidereal body, cusp, ASC, MC and orb.")


if __name__ == "__main__":
    main()
