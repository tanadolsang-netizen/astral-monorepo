#!/usr/bin/env python3
"""weekly_digest.py — 7-day ahead digest for Owner & Mai (deterministic, Thai, <=30 lines).

Reuses daily_brief.py internals (same skyfield+DE421 pipeline, Lahiri ayanamsa,
transit_hits orb<=2.5, snapshot 06:00 ICT).

Usage:
    python weekly_digest.py [YYYY-MM-DD] [--json]
Deterministic: same date -> identical bytes.
"""
import sys, json
from datetime import datetime, timedelta, timezone

from daily_brief import (OWNER, MAI, compute_chart, local_to_utc,
                         transit_hits, DAY_LORD)

DAY_NAMES = ["จันทร์", "อังคาร", "พุธ", "พฤหัสฯ", "ศุกร์", "เสาร์", "อาทิตย์"]
PEOPLE = (("Owner", OWNER), ("Mai", MAI))


def day_snapshot(day_local):
    snap_local = day_local.replace(hour=6, minute=0, tzinfo=timezone(timedelta(hours=7)))
    return snap_local.astimezone(timezone.utc)


def main():
    as_json = "--json" in sys.argv[1:]
    positionals = [a for a in sys.argv[1:] if not a.startswith("--")]
    if positionals:
        base = datetime.strptime(positionals[0], "%Y-%m-%d")
    else:
        base = datetime.now(timezone(timedelta(hours=7))).replace(
            hour=6, minute=0, second=0, microsecond=0)

    natal = {name: compute_chart(local_to_utc(p["date"], p["time"], p["tz"]),
                                 p["lat"], p["lon"]) for name, p in PEOPLE}

    days = []
    for i in range(7):
        d = base + timedelta(days=i)
        wd = d.weekday()
        snap_utc = day_snapshot(d)
        people_out = {}
        for name, p in PEOPLE:
            tr = compute_chart(snap_utc, p["lat"], p["lon"])
            tr["_dt"] = snap_utc
            hits = transit_hits(tr, natal[name])[:2]
            people_out[name] = [
                {"txt": f"{tp} {aname} {point}", "orb": orb}
                for (orb, _mi, _ad, _pi, tp, aname, point) in hits
            ]
        tightest = min((a["orb"] for po in people_out.values() for a in po), default=99.99)
        days.append({"date": d, "wd": wd, "people": people_out, "tight": tightest})

    best = sorted(range(7), key=lambda i: days[i]["tight"])[:3]
    shared = best[0]

    if as_json:
        print(json.dumps({
            "date": base.strftime("%Y-%m-%d"),
            "days": [{"date": days[i]["date"].strftime("%Y-%m-%d"),
                      "weekday_th": DAY_NAMES[days[i]["wd"]],
                      "day_lord_th": DAY_LORD[days[i]["wd"]][0],
                      "lucky_number": DAY_LORD[days[i]["wd"]][1],
                      "people": days[i]["people"]} for i in range(7)],
            "best_days": [days[i]["date"].strftime("%Y-%m-%d") for i in best],
            "shared_best": days[shared]["date"].strftime("%Y-%m-%d"),
        }, ensure_ascii=False, indent=2))
        return

    lines = [f"[Weekly Digest · {base.strftime('%Y-%m-%d')} +6 วัน · snapshot 06:00 ICT · sidereal Lahiri]"]
    for i in range(7):
        dd = days[i]
        lines.append(f"— {dd['date'].strftime('%d.%m')} ({DAY_NAMES[dd['wd']]}) —")
        for name, aspects in dd["people"].items():
            short = "Owner" and "M" if name == "Owner" else "Mai"
            for a in aspects:
                lines.append(f"{short}: {a['txt']} orb {a['orb']}")
    lines.append("★ BEST DAYS:")
    for i in best:
        dd = days[i]
        lines.append(f"  {dd['date'].strftime('%d.%m')} ({DAY_NAMES[dd['wd']]}) — orb แคบสุด {dd['tight']}")
    lines.append(f"★ SHARED BEST: {days[shared]['date'].strftime('%d.%m')} ({DAY_NAMES[days[shared]['wd']]})")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
