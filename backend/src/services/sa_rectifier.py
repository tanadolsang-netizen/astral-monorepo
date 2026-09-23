"""Solar-arc-to-angle convergence rectifier.

Principle (research #3): solar arc advances ~1°/yr; a 4-minute birth-time
error shifts the angles ~1°, which shifts every SA contact by ~1 year.
Score candidate birth times by whether SA planets hit the angles on dated
events. >=3 convergent events => minute-level precision.

Best cost/precision ratio in Western rectification. Pure orchestration
over chart_service + existing solar_arc math.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from src.services.chart_service import compute_chart

# event category -> angle it should activate + planets allowed as promissors
_EVENT_ANGLE = {
    "career": ("MC", ("Sun", "Jupiter", "Saturn", "Mars")),
    "marriage": ("DSC", ("Venus", "Jupiter", "Sun")),
    "home_move": ("IC", ("Moon", "Saturn")),
    "relocation": ("IC", ("Moon", "Mercury")),
    "recognition": ("MC", ("Sun", "Jupiter")),
    "loss_grief": ("IC", ("Saturn", "Pluto")),
}
_ORB_YEARS = 1.0  # SA contact within ±1 year of the event


def _angles_from(chart: dict) -> dict[str, float]:
    """ASC/DSC/MC/IC longitudes for a chart dict."""
    asc = float(chart["ascendant"]["absolute_deg"])
    h = chart.get("houses") or {}
    cusps = h.get("cusps", []) if isinstance(h, dict) else []
    mc = None
    for c in cusps:
        if c.get("house") == 10:
            mc = float(c["absolute_deg"])
            break
    if mc is None:
        # fallback: MC ≈ ASC + 90 in whole-sign-ish approximation
        mc = (asc + 90) % 360
    return {"ASC": asc, "DSC": (asc + 180) % 360,
            "MC": mc, "IC": (mc + 180) % 360}


def _sep(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def _sa_arc_degrees(natal_sun: float, birth_utc: datetime,
                    target_age_years: float) -> float:
    """Actual solar arc: Sun moved between birth and birth+age_days."""
    prog_dt = birth_utc + timedelta(days=365.2422 * target_age_years)
    prog = compute_chart("prog", prog_dt.date(), prog_dt.time(),
                         tz_offset_hours=0,
                         lat=0.0, lon=0.0)  # Sun longitude lat/lon-independent
    prog_sun = next(float(b["absolute_deg"]) for b in prog["bodies"]
                    if b["body"] == "Sun")
    return (prog_sun - natal_sun) % 360


def rectify_sa_convergence(birth_date_iso: str, stated_time_local: str,
                           tz_offset_hours: float, natal_lat: float,
                           natal_lon: float,
                           events: list[dict],
                           window_hours: int = 4,
                           step_minutes: int = 5,
                           person_name: str = "") -> dict:
    """Rank candidate times by SA→angle convergence across dated events.

    events: [{"event_date": "YYYY-MM-DD", "category": "..."}]
    """
    if not events:
        raise ValueError("at least one dated event required")
    for ev in events:
        if ev["category"] not in _EVENT_ANGLE:
            raise ValueError(f"unknown category {ev['category']}; "
                             f"use {list(_EVENT_ANGLE)}")

    stated = datetime.fromisoformat(f"{birth_date_iso}T{stated_time_local}:00")
    start = stated - timedelta(hours=window_hours)

    natal_cache = {}

    def natal_for(t_naive_utc: datetime) -> tuple[dict, dict]:
        key = t_naive_utc.strftime("%Y%m%d%H%M")
        if key not in natal_cache:
            c = compute_chart("cand", t_naive_utc.date(), t_naive_utc.time(),
                              tz_offset_hours=0, lat=natal_lat, lon=natal_lon)
            bodies = {b["body"]: float(b["absolute_deg"])
                      for b in c["bodies"]}
            natal_cache[key] = (bodies, _angles_from(c))
        return natal_cache[key]

    candidates = []
    t = start
    while t <= stated + timedelta(hours=window_hours):
        t_utc = t - timedelta(hours=tz_offset_hours)
        bodies, angles = natal_for(t_utc)
        natal_sun = bodies["Sun"]
        age0 = 30.0  # anchor age not needed — we score per-event ages

        score = 0.0
        hits_detail = []
        for ev in events:
            angle_name, promissors = _EVENT_ANGLE[ev["category"]]
            ev_date = datetime.fromisoformat(ev["event_date"]).replace(
                hour=12)
            ev_years = (ev_date - stated.replace(
                tzinfo=None)).total_seconds() / (86400 * 365.2425)
            if ev_years <= 1:
                continue
            try:
                arc = _sa_arc_degrees(natal_sun, t_utc, ev_years)
            except Exception:
                continue
            best_orb = min(_sep((bodies[p] + arc) % 360, angles[angle_name])
                           for p in promissors if p in bodies)
            tightness = max(0.0, 1 - best_orb / 1.0)  # 1° orb
            score += tightness
            hits_detail.append({"event": ev["event_date"],
                                "category": ev["category"],
                                "angle": angle_name,
                                "orb_deg": round(best_orb, 2),
                                "tightness": round(tightness, 3)})
        candidates.append({
            "time_local": t.strftime("%H:%M"),
            "score": round(score, 4),
            "hits": sorted(hits_detail, key=lambda x: x["orb_deg"])[:3],
        })
        t += timedelta(minutes=step_minutes)

    ranked = sorted(candidates, key=lambda c: c["score"], reverse=True)
    max_possible = len(events)  # every event perfectly tight
    confidence = round(min(100.0, ranked[0]["score"] / max(max_possible, 1)
                           * 100), 1) if ranked else 0.0

    th = (
        f'จากเหตุการณ์จริง {len(events)} เรื่อง — เวลาเกิดที่โซลาร์อาร์ค '
        f'"พาดับถึง" มุมชะตาพร้อมกันมากที่สุดคือ **{ranked[0]["time_local"] if ranked else "-"}** '
        f'(คะแนน {ranked[0]["score"] if ranked else 0:.2f}/{max_possible}) '
        f'ความมั่นใจ ~{confidence}%'
        if ranked else "ไม่มีข้อมูล"
    )
    en = (f"SA→angle convergence over {len(events)} events: best candidate "
          f"{ranked[0]['time_local'] if ranked else '-'} "
          f"(confidence {confidence}%).")

    return {
        "system": "solar-arc-convergence-rectifier",
        "candidates_evaluated": len(candidates),
        "best_time_th": ranked[0]["time_local"] if ranked else None,
        "best_hits": ranked[0]["hits"] if ranked else [],
        "confidence_pct": confidence,
        "top5": ranked[:5],
        "interpretation": {"th": th, "en": en},
        **({"person_name": person_name} if person_name else {}),
    }
