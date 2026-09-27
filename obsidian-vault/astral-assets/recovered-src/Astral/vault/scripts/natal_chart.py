#!/usr/bin/env python3
"""Natal chart calculator — tropical + Thai sidereal (Lahiri) + Ascendant.

Uses real astronomy (JPL DE421 via skyfield); reproduces the Astra app's numbers.
Also importable: `from natal_chart import compute_chart`.

Usage:
  python3 natal_chart.py --date 2001-08-18 --time 22:32 --tz 7 \
      --lat 13.8591 --lon 100.5217 --name Mai

Defaults: tz=7 (Thailand), lat/lon = Nonthaburi. Birth time is LOCAL; --tz is the
offset from UTC in hours.
"""
import argparse
import math
from datetime import datetime, timezone, timedelta
from skyfield.api import load

SIGNS = ['เมษ(Aries)', 'พฤษภ(Taurus)', 'เมถุน(Gemini)', 'กรกฎ(Cancer)',
         'สิงห์(Leo)', 'กันย์(Virgo)', 'ตุลย์(Libra)', 'พิจิก(Scorpio)',
         'ธนู(Sagittarius)', 'มังกร(Capricorn)', 'กุมภ์(Aquarius)', 'มีน(Pisces)']

BODIES = {
    'Sun': 'sun', 'Moon': 'moon', 'Mercury': 'mercury', 'Venus': 'venus',
    'Mars': 'mars', 'Jupiter': 'jupiter barycenter', 'Saturn': 'saturn barycenter',
    'Uranus': 'uranus barycenter', 'Neptune': 'neptune barycenter', 'Pluto': 'pluto barycenter',
}

OBLIQUITY = math.radians(23.4392911)  # ponytail: fixed mean obliquity, fine for 1900-2100


def to_sign(lon):
    return SIGNS[int(lon // 30)], lon % 30


def lahiri_ayanamsa(year_frac):
    # Lahiri approx anchored at 1997; ~50.29"/yr precession. Matches the vault's other scripts.
    return 23.68 + (year_frac - 1997) * (50.29 / 3600)


def compute_chart(dt_utc, lat_deg, lon_deg):
    """Return dict: body/ASC -> {'trop': deg, 'sid': deg}. dt_utc must be tz-aware UTC."""
    ts = load.timescale()
    eph = load('de421.bsp')
    earth = eph['earth']
    t = ts.from_datetime(dt_utc)

    year_frac = dt_utc.year + dt_utc.timetuple().tm_yday / 365.25
    ayan = lahiri_ayanamsa(year_frac)

    chart = {'_ayanamsa': ayan}
    for name, key in BODIES.items():
        astro = earth.at(t).observe(eph[key])
        _, lon_e, _ = astro.ecliptic_latlon()
        trop = lon_e.degrees % 360
        chart[name] = {'trop': trop, 'sid': (trop - ayan) % 360}

    # Ascendant from Local Sidereal Time
    lst = (t.gmst * 15 + lon_deg) % 360
    ramc = math.radians(lst)
    phi = math.radians(lat_deg)
    asc = math.degrees(math.atan2(
        math.cos(ramc),
        -(math.sin(ramc) * math.cos(OBLIQUITY) + math.tan(phi) * math.sin(OBLIQUITY))
    )) % 360
    chart['ASC'] = {'trop': asc, 'sid': (asc - ayan) % 360}
    return chart


def local_to_utc(date_str, time_str, tz_hours):
    dt_local = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    return dt_local.replace(tzinfo=timezone(timedelta(hours=tz_hours))).astimezone(timezone.utc)


def print_chart(chart, name):
    print(f"=== {name} — natal chart ===")
    print(f"Ayanamsa (Lahiri approx): {chart['_ayanamsa']:.3f}")
    print("%-9s %-22s %-22s" % ("Body", "Tropical", "Sidereal(Thai)"))
    order = list(BODIES) + ['ASC']
    for b in order:
        ts_, td_ = to_sign(chart[b]['trop'])
        ss_, sd_ = to_sign(chart[b]['sid'])
        print("%-9s %-13s %6.2f   %-13s %6.2f" %
              (b, ts_.split('(')[0], td_, ss_.split('(')[0], sd_))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Natal chart (tropical + Thai sidereal + Ascendant)")
    p.add_argument("--date", required=True, help="birth date YYYY-MM-DD")
    p.add_argument("--time", required=True, help="birth time HH:MM (local)")
    p.add_argument("--tz", type=float, default=7.0, help="UTC offset hours (default 7 = Thailand)")
    p.add_argument("--lat", type=float, default=13.8591, help="latitude (default Nonthaburi)")
    p.add_argument("--lon", type=float, default=100.5217, help="longitude (default Nonthaburi)")
    p.add_argument("--name", default="Subject")
    a = p.parse_args()
    dt_utc = local_to_utc(a.date, a.time, a.tz)
    print(f"(local {a.date} {a.time} tz{a.tz:+g} -> {dt_utc.isoformat()})")
    print_chart(compute_chart(dt_utc, a.lat, a.lon), a.name)
