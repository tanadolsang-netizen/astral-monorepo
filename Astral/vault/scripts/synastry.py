#!/usr/bin/env python3
"""Synastry — cross-aspects between two people's charts.

Reuses natal_chart.compute_chart. Reports the classic major aspects between every
pair of bodies, flagging the romance pairs (Venus-Mars) and luminary/Ascendant
contacts that matter most for compatibility.

Usage:
  python3 synastry.py \
    --a-name Mai   --a-date 2001-08-18 --a-time 22:32 \
    --b-name Owner --b-date 1997-05-19 --b-time 05:45

Both people default to tz=7 and Nonthaburi/Chonburi-ish coords; override per person
with --a-lat/--a-lon/--a-tz (and --b-*). Aspects use the TROPICAL zodiac.
"""
import argparse
from natal_chart import compute_chart, local_to_utc, to_sign, BODIES

# aspect name -> (exact angle, orb allowed)
ASPECTS = {
    'conjunction': (0, 8),
    'sextile': (60, 5),
    'square': (90, 6),
    'trine': (120, 6),
    'opposition': (180, 8),
}
# tighter orb + "headline" flag for the pairs that matter most romantically
ROMANCE_PAIRS = {frozenset(['Venus', 'Mars'])}
LUMINARIES = {'Sun', 'Moon', 'ASC'}


def angle_diff(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def find_aspect(lon_a, lon_b):
    sep = angle_diff(lon_a, lon_b)
    for name, (exact, orb) in ASPECTS.items():
        if abs(sep - exact) <= orb:
            return name, abs(sep - exact)
    return None, None


def synastry(chart_a, chart_b):
    """Yield (bodyA, bodyB, aspect, orb, flag) sorted by tightness."""
    rows = []
    bodies = list(BODIES) + ['ASC']
    for ba in bodies:
        for bb in bodies:
            asp, orb = find_aspect(chart_a[ba]['trop'], chart_b[bb]['trop'])
            if not asp:
                continue
            flag = ''
            if frozenset([ba, bb]) in ROMANCE_PAIRS:
                flag = '💞 romance'
            elif ba in LUMINARIES or bb in LUMINARIES:
                flag = '★ core'
            rows.append((ba, bb, asp, orb, flag))
    rows.sort(key=lambda r: r[3])  # tightest orb first
    return rows


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Synastry cross-aspects between two charts")
    for who in ('a', 'b'):
        p.add_argument(f"--{who}-name", default=who.upper())
        p.add_argument(f"--{who}-date", required=True)
        p.add_argument(f"--{who}-time", required=True)
        p.add_argument(f"--{who}-tz", type=float, default=7.0)
        p.add_argument(f"--{who}-lat", type=float, default=13.8591)
        p.add_argument(f"--{who}-lon", type=float, default=100.5217)
    args = vars(p.parse_args())

    def build(who):
        dt = local_to_utc(args[f'{who}_date'], args[f'{who}_time'], args[f'{who}_tz'])
        return compute_chart(dt, args[f'{who}_lat'], args[f'{who}_lon'])

    ca, cb = build('a'), build('b')
    na, nb = args['a_name'], args['b_name']

    print(f"=== Synastry: {na} x {nb} (tropical) ===\n")
    print("%-8s %-16s %-8s %-16s %-12s %-6s %s" %
          (na, "", nb, "", "aspect", "orb", "note"))
    for ba, bb, asp, orb, flag in synastry(ca, cb):
        sa, da = to_sign(ca[ba]['trop'])
        sb, db = to_sign(cb[bb]['trop'])
        print("%-8s %-16s %-8s %-16s %-12s %5.1f  %s" %
              (ba, f"{sa.split('(')[0]} {da:.1f}",
               bb, f"{sb.split('(')[0]} {db:.1f}", asp, orb, flag))
