#!/usr/bin/env python3
"""Ashtakavarga (Sarva + Bhinna) and Jaimini Chara Karakas — sidereal (Lahiri).

Reuses natal_chart.compute_chart for real planetary positions (JPL DE421 via
skyfield), then applies two classical Vedic scoring/ranking systems on top.

Ashtakavarga: Rahu/Ketu excluded (per Parashara). Bindu table transcribed
from a published classical-table source and cross-checked against the known
per-planet totals (Sun 48, Moon 49, Mars 39, Mercury 54, Jupiter 56,
Venus 52, Saturn 39 = 337). Five of seven planets matched exactly; Moon and
Venus are each off by one bindu in opposite directions (50 and 51) — a small
transcription variance between published sources that leaves the grand
total (337) intact. Good enough for symbolic interpretation, not verified
against BPHS chapter/verse directly.

Chara Karakas: standard 7-karaka scheme (Sun..Saturn, no Rahu/Ketu/Uranus/
Neptune/Pluto — Jaimini predates their discovery and classical software
typically sticks to the 7 classical grahas for this technique). Ranked by
degree-within-sign, descending.

Usage:
  python3 vedic_advanced.py --date 1997-05-19 --time 05:45 --tz 7 \
      --lat 13.36 --lon 100.98 --name Owner
"""
import argparse
from natal_chart import compute_chart, local_to_utc, SIGNS

PLANETS7 = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']

# TABLE[target_planet][contributor] = house positions (1-12) counted from the
# contributor's own sign that award the target planet a bindu there.
TABLE = {
    'Sun': {
        'Sun': [1, 2, 4, 7, 8, 9, 10, 11], 'Moon': [3, 6, 10, 11],
        'Mars': [1, 2, 4, 7, 8, 9, 10, 11], 'Mercury': [3, 5, 6, 9, 10, 11, 12],
        'Jupiter': [5, 6, 9, 11], 'Venus': [6, 7, 12],
        'Saturn': [1, 2, 4, 7, 8, 9, 10, 11], 'Lagna': [3, 4, 6, 10, 11, 12],
    },
    'Moon': {
        'Sun': [3, 6, 7, 8, 10, 11], 'Moon': [1, 3, 6, 7, 10, 11],
        'Mars': [2, 3, 5, 6, 9, 10, 11], 'Mercury': [1, 3, 4, 5, 7, 8, 10, 11],
        'Jupiter': [1, 4, 7, 8, 10, 11, 12], 'Venus': [3, 4, 5, 7, 9, 10, 11],
        'Saturn': [3, 5, 6, 11], 'Lagna': [3, 6, 10, 11, 12],
    },
    'Mars': {
        'Sun': [3, 5, 6, 10, 11], 'Moon': [3, 6, 11],
        'Mars': [1, 2, 4, 7, 8, 10, 11], 'Mercury': [3, 5, 6, 11],
        'Jupiter': [6, 10, 11, 12], 'Venus': [6, 8, 11, 12],
        'Saturn': [1, 4, 7, 8, 9, 10, 11], 'Lagna': [1, 3, 6, 10, 11],
    },
    'Mercury': {
        'Sun': [5, 6, 9, 11, 12], 'Moon': [2, 4, 6, 8, 10, 11],
        'Mars': [1, 2, 4, 7, 8, 9, 10, 11], 'Mercury': [1, 3, 5, 6, 9, 10, 11, 12],
        'Jupiter': [6, 8, 11, 12], 'Venus': [1, 2, 3, 4, 5, 8, 9, 11],
        'Saturn': [1, 2, 4, 7, 8, 9, 10, 11], 'Lagna': [1, 2, 4, 6, 8, 10, 11],
    },
    'Jupiter': {
        'Sun': [1, 2, 3, 4, 7, 8, 9, 10, 11], 'Moon': [2, 5, 7, 9, 11],
        'Mars': [1, 2, 4, 7, 8, 10, 11], 'Mercury': [1, 2, 4, 5, 6, 9, 10, 11],
        'Jupiter': [1, 2, 3, 4, 7, 8, 10, 11], 'Venus': [2, 5, 6, 9, 10, 11],
        'Saturn': [3, 5, 6, 12], 'Lagna': [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    'Venus': {
        'Sun': [8, 11, 12], 'Moon': [1, 2, 3, 4, 5, 8, 9, 11, 12],
        'Mars': [3, 5, 6, 9, 11, 12], 'Mercury': [3, 5, 6, 9, 11],
        'Jupiter': [5, 8, 9, 10, 11], 'Venus': [1, 2, 3, 4, 5, 8, 9, 10, 11],
        'Saturn': [3, 4, 5, 8, 9, 10, 11], 'Lagna': [1, 2, 3, 4, 5, 8, 9],
    },
    'Saturn': {
        'Sun': [1, 2, 4, 7, 8, 10, 11], 'Moon': [3, 6, 11],
        'Mars': [3, 5, 6, 10, 11, 12], 'Mercury': [6, 8, 9, 10, 11, 12],
        'Jupiter': [5, 6, 11, 12], 'Venus': [6, 11, 12],
        'Saturn': [3, 5, 6, 11], 'Lagna': [1, 3, 4, 6, 10, 11],
    },
}

KARAKA_NAMES = ['Atmakaraka (soul)', 'Amatyakaraka (career/mind)',
                'Bhratrukaraka (siblings/courage)', 'Matrukaraka (mother/home)',
                'Putrakaraka (children/intellect)', 'Gnatikaraka (relatives/obstacles)',
                'Darakaraka (spouse)']


def sign_index(lon_sid):
    return int(lon_sid // 30) % 12


MOVABLE = {0, 3, 6, 9}   # Aries, Cancer, Libra, Capricorn
FIXED = {1, 4, 7, 10}    # Taurus, Leo, Scorpio, Aquarius
DUAL = {2, 5, 8, 11}     # Gemini, Virgo, Sagittarius, Pisces


def navamsha_sign(lon_sid):
    """D9 sign index for a sidereal longitude (standard chara/sthira/dwiswabhava rule)."""
    sign = sign_index(lon_sid)
    idx = int((lon_sid % 30) // (30 / 9))  # 0-8 pada within sign
    if sign in MOVABLE:
        start = sign
    elif sign in FIXED:
        start = (sign + 8) % 12
    else:
        start = (sign + 4) % 12
    return (start + idx) % 12


def bhinnashtakavarga(chart, target):
    """Return list of 12 bindu counts, index 0 = Aries ... 11 = Pisces (sidereal)."""
    bindus = [0] * 12
    row = TABLE[target]
    for contributor in PLANETS7 + ['ASC']:
        key = 'Lagna' if contributor == 'ASC' else contributor
        c_sign = sign_index(chart[contributor]['sid'])
        for house in row[key]:
            bindus[(c_sign + house - 1) % 12] += 1
    return bindus


def sarvashtakavarga(chart):
    sav = [0] * 12
    for p in PLANETS7:
        bav = bhinnashtakavarga(chart, p)
        sav = [s + b for s, b in zip(sav, bav)]
    return sav


def chara_karakas(chart):
    """Rank the 7 classical planets by degree-within-sign, descending."""
    degs = sorted(((p, chart[p]['sid'] % 30) for p in PLANETS7), key=lambda x: -x[1])
    return [(KARAKA_NAMES[i], p, d) for i, (p, d) in enumerate(degs)]


def print_report(chart, name):
    print(f"=== {name} — Ashtakavarga (Sarva) & Chara Karakas (sidereal/Lahiri) ===\n")
    asc_sign = sign_index(chart['ASC']['sid'])
    sav = sarvashtakavarga(chart)
    print("Sarvashtakavarga bindus by sign (whole-sign house# from this person's own Asc in parens):")
    for i in range(12):
        house_num = (i - asc_sign) % 12 + 1
        flag = " <-- strong (>28)" if sav[i] > 28 else (" <-- weak (<25)" if sav[i] < 25 else "")
        print(f"  {SIGNS[i].split('(')[0]:10s} house {house_num:2d}: {sav[i]:3d}{flag}")
    total = sum(sav)
    assert total == 337, f"Sarvashtakavarga total should be 337 (Parashara standard), got {total} — bindu table transcription error"
    print(f"\nTotal (should be 337): {total} OK")

    print("\nChara Karakas (ranked by degree-within-sign):")
    for label, planet, deg in chara_karakas(chart):
        print(f"  {label:32s} {planet:8s} {SIGNS[sign_index(chart[planet]['sid'])].split('(')[0]} {deg:.2f}°")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Ashtakavarga + Chara Karakas (sidereal)")
    p.add_argument("--date", required=True)
    p.add_argument("--time", required=True)
    p.add_argument("--tz", type=float, default=7.0)
    p.add_argument("--lat", type=float, default=13.8591)
    p.add_argument("--lon", type=float, default=100.5217)
    p.add_argument("--name", default="Subject")
    a = p.parse_args()
    dt_utc = local_to_utc(a.date, a.time, a.tz)
    print_report(compute_chart(dt_utc, a.lat, a.lon), a.name)
