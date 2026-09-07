#!/usr/bin/env python3
"""daily_brief.py — morning brief for Owner & Mai (deterministic, Thai, stdout, <=25 lines).

Pipeline reused from C:/AI/obsidian-vault/scripts/natal_chart.py (compute_chart:
JPL DE421 via skyfield, Lahiri-approx ayanamsa, ASC from LST) and transit_week_scan.py
(aspects orb<=2.5 vs personal points Sun/Moon/Mercury/Venus/Mars/ASC, whole-sign
houses from sidereal ASC).

Snapshot: 06:00 ICT of the target day -> same output all day (deterministic).
Usage: python daily_brief.py [--json] [YYYY-MM-DD]   (default: today, Bangkok)
--json: same content as one JSON object {date, generated_for:[{name,
moon_sign, moon_house, top_aspects, day_lord, lucky_number}], shared_note}
for cron delivery; default human output is unchanged. Deterministic bytes
for the same input date.
Ephemeris loaded by absolute path: C:/AI/obsidian-vault/scripts/de421.bsp
"""
import json
import math
import sys
from datetime import datetime, timedelta, timezone

from skyfield.api import load

EPH_PATH = r"C:\AI\obsidian-vault\scripts\de421.bsp"

OWNER = dict(date="1997-05-19", time="05:45", tz=7.0, lat=13.36, lon=100.98,
             name="Owner", born="1997-05-19 ชลบุรี")
MAI = dict(date="2001-08-18", time="22:32", tz=7.0, lat=13.86, lon=100.52,
           name="Mai", born="2001-08-18 นนทบุรี")

SIGNS_TH = ["เมษ", "พฤษภ", "เมถุน", "กรกฎ", "สิงห์", "กันย์",
            "ตุลย์", "พิจิก", "ธนู", "มังกร", "กุมภ์", "มีน"]
WEEKDAYS_TH = ["จันทร์", "อังคาร", "พุธ", "พฤหัส", "ศุกร์", "เสาร์", "อาทิตย์"]
THAI_MONTHS = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
               "ก.ค.", "ส.ค.", "ต.ค.", "พ.ย.", "ธ.ค."]
# Day-lord: weekday -> (planet TH, lucky number)  Sun=1 Moon=2 Mars=3 Mercury=4
# Jupiter=5 Venus=6 Saturn=9 (Mon..Sun index)
DAY_LORD = [("ดวงจันทร์", 2), ("ดาวอังคาร", 3), ("ดาวพุธ", 4), ("ดาวพฤหัสฯ", 5),
            ("ดาวศุกร์", 6), ("ดาวเสาร์", 9), ("ดวงอาทิตย์", 1)]
PLANET_TH = {"Sun": "ดวงอาทิตย์", "Moon": "ดวงจันทร์", "Mercury": "ดาวพุธ",
             "Venus": "ดาวศุกร์", "Mars": "ดาวอังคาร", "Jupiter": "ดาวพฤหัสฯ",
             "Saturn": "ดาวเสาร์", "Uranus": "ดาวยูเรนัส", "Neptune": "ดาวเนปจูน",
             "Pluto": "ดาวพลูโต", "Rahu": "ราหู"}
POINT_TH = {"Sun": "ดวงอาทิตย์เกิด", "Moon": "ดวงจันทร์เกิด", "Mercury": "ดาวพุธเกิด",
            "Venus": "ดาวศุกร์เกิด", "Mars": "ดาวอังคารเกิด", "ASC": "ลัคนาเกิด"}
ASPECTS = [(0.0, "ร่วม"), (60.0, "เซกไทล์"), (90.0, "ฉาก"), (120.0, "ไตรโคณ"), (180.0, "ตรงข้าม")]
PERSONAL = ["Sun", "Moon", "Mercury", "Venus", "Mars", "ASC"]
MOVERS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
          "Uranus", "Neptune", "Pluto", "Rahu"]
MOVER_IDX = {p: i for i, p in enumerate(MOVERS)}
POINT_IDX = {p: i for i, p in enumerate(PERSONAL)}

BODIES = {
    "Sun": "sun", "Moon": "moon", "Mercury": "mercury", "Venus": "venus",
    "Mars": "mars", "Jupiter": "jupiter barycenter", "Saturn": "saturn barycenter",
    "Uranus": "uranus barycenter", "Neptune": "neptune barycenter", "Pluto": "pluto barycenter",
}
OBLIQUITY = math.radians(23.4392911)  # fixed mean obliquity, fine 1900-2100 (as natal_chart.py)


def lahiri_ayanamsa(year_frac):
    return 23.68 + (year_frac - 1997) * (50.29 / 3600)


def compute_chart(dt_utc, lat_deg, lon_deg):
    """Same convention as vault natal_chart.py: {'trop','sid'} per body + ASC."""
    ts = load.timescale()
    eph = load(EPH_PATH)
    earth = eph["earth"]
    t = ts.from_datetime(dt_utc)
    year_frac = dt_utc.year + dt_utc.timetuple().tm_yday / 365.25
    ayan = lahiri_ayanamsa(year_frac)
    chart = {"_ayanamsa": ayan}
    for name, key in BODIES.items():
        _, lon_e, _ = earth.at(t).observe(eph[key]).ecliptic_latlon()
        trop = lon_e.degrees % 360
        chart[name] = {"trop": trop, "sid": (trop - ayan) % 360}
    lst = (t.gmst * 15 + lon_deg) % 360
    ramc, phi = math.radians(lst), math.radians(lat_deg)
    asc = math.degrees(math.atan2(
        math.cos(ramc),
        -(math.sin(ramc) * math.cos(OBLIQUITY) + math.tan(phi) * math.sin(OBLIQUITY)),
    )) % 360
    chart["ASC"] = {"trop": asc, "sid": (asc - ayan) % 360}
    return chart


def local_to_utc(date_str, time_str, tz_hours):
    d = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    return d.replace(tzinfo=timezone(timedelta(hours=tz_hours))).astimezone(timezone.utc)


def mean_node_sid(dt_utc):
    """Mean lunar node (same approx as transit_week_scan.py, good to ~0.3 deg)."""
    epoch = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)
    d = (dt_utc - epoch).total_seconds() / 86400.0
    omega_trop = (125.04452 - 0.0529538 * d) % 360
    yf = dt_utc.year + dt_utc.timetuple().tm_yday / 365.25
    ayan = lahiri_ayanamsa(yf)
    return (omega_trop - ayan) % 360


def sgn(lon):
    return int(lon // 30), lon % 30


def whouse(sid_point, sid_asc):
    return (sgn(sid_point)[0] - sgn(sid_asc)[0]) % 12 + 1


def angdiff(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def fmt_pos(sid):
    i, d = sgn(sid)
    return f"{SIGNS_TH[i]} {d:.1f}°"


def transit_hits(tr, natal):
    """All orb<=2.5 hits, sorted deterministic: orb, mover, aspect angle, point."""
    hits = []
    for tp in MOVERS:
        sid_now = mean_node_sid(tr["_dt"]) if tp == "Rahu" else tr[tp]["sid"]
        for np_ in PERSONAL:
            diff = angdiff(sid_now % 360, natal[np_]["sid"])
            for adeg, aname in ASPECTS:
                orb = abs(diff - adeg)
                if orb <= 2.5:
                    hits.append((round(orb, 2), MOVER_IDX[tp], adeg, POINT_IDX[np_],
                                 tp, aname, np_))
    hits.sort()
    return hits


def main():
    as_json = "--json" in sys.argv[1:]
    positionals = [a for a in sys.argv[1:] if not a.startswith("--")]
    if positionals:
        day_local = datetime.strptime(positionals[0], "%Y-%m-%d")
    else:
        day_local = datetime.now(timezone(timedelta(hours=7))).replace(
            hour=6, minute=0, second=0, microsecond=0)
    snap_local = day_local.replace(hour=6, minute=0, tzinfo=timezone(timedelta(hours=7)))
    snap_utc = snap_local.astimezone(timezone.utc)
    iso = snap_local.strftime("%Y-%m-%d")
    wd_i = snap_local.weekday()

    owner_natal = compute_chart(local_to_utc(OWNER["date"], OWNER["time"], OWNER["tz"]),
                                OWNER["lat"], OWNER["lon"])
    mai_natal = compute_chart(local_to_utc(MAI["date"], MAI["time"], MAI["tz"]),
                              MAI["lat"], MAI["lon"])

    charts = {}
    for person, natal in ((OWNER, owner_natal), (MAI, mai_natal)):
        tr = compute_chart(snap_utc, person["lat"], person["lon"])
        tr["_dt"] = snap_utc
        charts[person["name"]] = (tr, natal)

    wd_th = WEEKDAYS_TH[wd_i]
    lord_th, lucky = DAY_LORD[wd_i]
    th_year = snap_local.year + 543
    generated_for = []
    if not as_json:
        print(f"[ดวงประจำวัน {iso} · วัน{wd_th} {snap_local.day} "
              f"{THAI_MONTHS[snap_local.month - 1]} {th_year} · "
              f"snapshot 06:00 ICT · sidereal Lahiri]")

    per_person_best = {}
    for person in (OWNER, MAI):
        tr, natal = charts[person["name"]]
        m_i, m_d = sgn(tr["Moon"]["sid"])
        house = whouse(tr["Moon"]["sid"], natal["ASC"]["sid"])
        hits = transit_hits(tr, natal)[:3]
        per_person_best[person["name"]] = hits
        generated_for.append({
            "name": person["name"],
            "moon_sign": SIGNS_TH[m_i],
            "moon_house": house,
            "top_aspects": [
                {"planet": PLANET_TH[tp], "aspect": aname,
                 "target": POINT_TH[np_], "orb": round(orb, 2)}
                for (orb, _oi, _ai, _pi, tp, aname, np_) in hits
            ],
            "day_lord": lord_th,
            "lucky_number": lucky,
        })
        if as_json:
            continue
        print(f"— {person['name']} (เกิด {person['born']}) —")
        print(f"ดวงจันทร์: {SIGNS_TH[m_i]} {m_d:.1f}° → เรือน {house}/12 "
              f"(whole-sign จากลัคนา {fmt_pos(natal['ASC']['sid'])})")
        if hits:
            for k, (orb, _, _, _, tp, aname, np_) in enumerate(hits, 1):
                sid_now = mean_node_sid(snap_utc) if tp == "Rahu" else tr[tp]["sid"]
                print(f"{k}) {PLANET_TH[tp]} {aname} {POINT_TH[np_]} orb {orb:.2f}° "
                      f"(transit {fmt_pos(sid_now)} vs natal {fmt_pos(natal[np_]['sid'])})")
        else:
            print(f"({iso}: ไม่มีมุม orb≤2.5° ถึงจุดส่วนตัว 6 จุด ณ 06:00 ICT)")
        print(f"ผู้คุณวัน{wd_th}: {lord_th} · เลขนำโชค {lucky}")

    shared_note = None
    shared = []
    for orb_o, _, _, _, tp_o, asp_o, pt_o in per_person_best["Owner"]:
        for orb_m, _, _, _, tp_m, asp_m, pt_m in per_person_best["Mai"]:
            if tp_o == tp_m:
                shared.append((min(orb_o, orb_m), tp_o, pt_o, orb_o, pt_m, orb_m))
    if shared:
        shared.sort()
        _, tp, pt_o, orb_o, pt_m, orb_m = shared[0]
        shared_note = (f"{PLANET_TH[tp]} แตะทั้งสองดวง — Owner:{pt_o} orb {orb_o:.2f}° "
                       f"/ Mai:{pt_m} orb {orb_m:.2f}°")
        if not as_json:
            print(f"โน้ตร่วม {iso}: {shared_note}")

    if as_json:
        print(json.dumps({"date": iso,
                          "generated_for": generated_for,
                          "shared_note": shared_note},
                         ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
