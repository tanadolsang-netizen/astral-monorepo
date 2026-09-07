#!/usr/bin/env python3
"""Daily transit scan for Owner & Mai, Aug 22-29 2026.
Transit planets vs natal charts (sidereal/Lahiri, same pipeline as natal_chart.py).
Prints: Moon sign/house per day, sign ingresses in the window, and tight
transit-to-natal aspects (orb <= 2.5 deg) to personal points.
"""
import math
from datetime import datetime, timezone, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from natal_chart import compute_chart, local_to_utc, BODIES

OWNER = dict(date="1997-05-19", time="05:45", tz=7.0, lat=13.36, lon=100.98, name="Owner")
MAI   = dict(date="2001-08-18", time="22:32", tz=7.0, lat=13.86, lon=100.52, name="Mai")

SIGNS_TH = ['เมษ','พฤษภ','เมถุน','กรกฎ','สิงห์','กันย์','ตุลย์','พิจิก','ธนู','มังกร','กุมภ์','มีน']

def sgn(lon): return int(lon // 30), lon % 30
def fmt(sid):
    i, d = sgn(sid)
    return f"{SIGNS_TH[i]} {d:.1f}°"

def whouse(sid_point, sid_asc):
    return (int(sgn(sid_point)[0] - sgn(sid_asc)[0]) % 12) + 1

def angdiff(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)

ASPECTS = {0:'conj', 60:'sextile', 90:'square', 120:'trine', 180:'opp'}

owner_natal = compute_chart(local_to_utc(**{k: OWNER[k] for k in ('date','time')}) if False else local_to_utc(OWNER['date'], OWNER['time'], OWNER['tz']), OWNER['lat'], OWNER['lon'])
mai_natal   = compute_chart(local_to_utc(MAI['date'], MAI['time'], MAI['tz']), MAI['lat'], MAI['lon'])

PERSONAL = ['Sun','Moon','Mercury','Venus','Mars','ASC']
MOVERS = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto']
NODES_SID = {'Rahu': None}  # computed below from mean node approx

def mean_node_sid(dt_utc):
    # Mean lunar node, approximate formula (good to ~0.3 deg): Omega = 125.0445 - 0.05295*d
    epoch = datetime(2000,1,1,12, tzinfo=timezone.utc)
    d = (dt_utc - epoch).total_seconds() / 86400.0
    omega_trop = (125.04452 - 0.0529538 * d) % 360
    year_frac = dt_utc.year + dt_utc.timetuple().tm_yday / 365.25
    ayan = 23.68 + (year_frac - 1997) * (50.29 / 3600)
    return (omega_trop - ayan) % 360

for person, natal in ((OWNER, owner_natal), (MAI, mai_natal)):
    asc_sid = natal['ASC']['sid']
    print(f"\n================ {person['name']} (natal ASC {fmt(asc_sid)}) ================")
    prev_signs = {}
    for day in range(22, 30):
        dt_local = datetime(2026, 8, day, 12, 0, tzinfo=timezone(timedelta(hours=7)))
        dt_utc = dt_local.astimezone(timezone.utc)
        tr = compute_chart(dt_utc, person['lat'], person['lon'])
        wd = ['จันทร์','อังคาร','พุธ','พฤหัส','ศุกร์','เสาร์','อาทิตย์'][dt_local.weekday()]
        moon_i, _ = sgn(tr['Moon']['sid'])
        print(f"\n-- {dt_local.strftime('%d %b')} ({wd}) --")
        print(f"   Moon: {fmt(tr['Moon']['sid'])} -> เรือน {whouse(tr['Moon']['sid'], asc_sid)} (นับ whole-sign)")
        hits = []
        for tp in MOVERS:
            trop_now = tr[tp]['trop'] if tp != 'Rahu' else mean_node_sid(dt_utc) + tr['_ayanamsa']
            sid_now = tr[tp]['sid'] if tp != 'Rahu' else mean_node_sid(dt_utc)
            # ingress check vs previous day handled by comparing signs across days later
            for np_ in PERSONAL:
                ndeg = natal[np_]['sid']
                diff = angdiff(sid_now % 360, ndeg)
                for adeg, aname in ASPECTS.items():
                    orb = abs(diff - adeg)
                    if orb <= 2.5:
                        hits.append((orb, tp, aname, np_, fmt(sid_now), fmt(ndeg)))
        hits.sort()
        for orb, tp, aname, np_, tpos, npos in hits[:8]:
            print(f"   {tp:<8} {aname:<8} กำเนิด-{np_:<8} orb {orb:.2f}°   (transit {tpos} vs natal {npos})")
        if not hits:
            print("   (ไม่มีมุมแน่น orb<=2.5° กับจุดส่วนตัวในวันนี้)")
    # weekly summary of sign changes
    print("\n   [ingress check]")
    for tp in ['Mercury','Venus','Mars']:
        signs_seen = []
        for day in range(22, 30):
            dt_utc = datetime(2026, 8, day, 12, 0, tzinfo=timezone(timedelta(hours=7))).astimezone(timezone.utc)
            tr = compute_chart(dt_utc, person['lat'], person['lon'])
            i, _ = sgn(tr[tp]['sid'])
            if not signs_seen or signs_seen[-1][0] != i:
                signs_seen.append((i, SIGNS_TH[i], day))
        desc = " → ".join(f"{s}({d}/8)" for _, s, d in signs_seen)
        print(f"   {tp}: {desc}")
