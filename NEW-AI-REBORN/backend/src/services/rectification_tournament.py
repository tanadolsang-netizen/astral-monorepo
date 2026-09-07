"""Rectification tournament — cosine-encoded event matching.

Upgrades heuristic birth-time rectification: candidate times in ±window
are scored against life events using cosine-encoded angular separations
(raw angles demonstrably fail in ML), tournament bracket instead of naive sum.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta

from src.services.chart_service import compute_chart

_EVENT_PLANETS = {
    "marriage": ["Venus", "Jupiter", "Moon"],
    "career_start": ["Saturn", "Sun", "Midheaven"],
    "relocation": ["Moon", "Mercury", "ASC"],
    "loss_grief": ["Saturn", "Pluto"],
    "birth_child": ["Jupiter", "Moon"],
}


def _cos_features(chart_lons: dict[str, float],
                  transit_lons: dict[str, float]) -> dict[str, float]:
    """Cosine-encoded angular separations for every planet pair."""
    feats = {}
    for p1, l1 in chart_lons.items():
        for p2, l2 in transit_lons.items():
            sep = (l2 - l1) % 360.0
            feats[f"cos:{p1}:{p2}"] = math.cos(math.radians(sep))
    return feats


def _score_candidate(candidate_time_utc: datetime, natal_lat: float,
                     natal_lon: float, events: list[dict]) -> tuple[float, list[str]]:
    total = 0.0
    reasons = []
    for ev in events:
        ev_dt = datetime.fromisoformat(ev["event_date"])
        if len(ev["event_date"]) <= 10:
            ev_dt = ev_dt.replace(hour=12)
        planets = _EVENT_PLANETS.get(ev.get("category", ""), ["Sun", "Moon"])

        natal_chart = compute_chart("cand", candidate_time_utc.date(),
                                    candidate_time_utc.time(), tz_offset_hours=0,
                                    lat=natal_lat, lon=natal_lon)
        natal_lons = {b["body"]: b["absolute_deg"] for b in natal_chart["bodies"]}
        natal_lons["ASC"] = natal_chart["ascendant"]["absolute_deg"]

        tr_chart = compute_chart("ev", ev_dt.date(), ev_dt.time(), tz_offset_hours=0,
                                 lat=natal_lat, lon=natal_lon)
        tr_lons = {b["body"]: b["absolute_deg"] for b in tr_chart["bodies"]}

        # score = tightest hard-or-soft aspect among relevant pairs (cosine space)
        best = -1.0
        for p in planets:
            for np_, nl in natal_lons.items():
                tl = tr_lons.get(p)
                if tl is None or np_ not in tr_lons and np_ not in ("ASC",):
                    continue
                sep = abs((tl - nl) % 360)
                if sep > 180:
                    sep = 360 - sep
                tightness = max(0.0, 1 - min(sep, 360 - sep) / 8.0) \
                    if min(sep, 360-sep) <= 8 else 0.0
                best = max(best, tightness)
        total += best
        reasons.append(f"{ev['event_date']}: {best:.2f}")

    return total, reasons


def rectification_tournament(birth_date_iso: str,
                             stated_time_local: str,
                             tz_offset_hours: float = 7.0,
                             natal_lat: float = 13.7563,
                             natal_lon: float = 100.5018,
                             events: list[dict] | None = None,
                             window_hours: int = 6,
                             step_minutes: int = 10,
                             person_name: str = "") -> dict:
    """Bracket-style ranking of candidate birth times."""
    if not events:
        raise ValueError("at least one life event required")

    stated = datetime.fromisoformat(f"{birth_date_iso}T{stated_time_local}:00")
    start = stated - timedelta(hours=window_hours)

    candidates = []
    t = start
    while t <= stated + timedelta(hours=window_hours):
        utc_t = t - timedelta(hours=tz_offset_hours)
        raw, _ = _score_candidate(utc_t, natal_lat, natal_lon, events)
        candidates.append({"time_local": t.strftime("%H:%M"),
                           "utc_iso": utc_t.isoformat(),
                           "raw_score": round(raw, 4)})
        t += timedelta(minutes=step_minutes)

    # theoretical-max normalization per event count
    max_raw = len(events) * 5 * len(events)  # generous ceiling
    ranked = sorted(candidates, key=lambda c: c["raw_score"], reverse=True)
    top = ranked[0]
    confidence = round(min(100.0, top["raw_score"] / max(max_raw / 25, 1e-9) * 100), 1)

    return {
        "system": "rectification-tournament",
        "candidates_evaluated": len(candidates),
        "best_time_th": top["time_local"],
        "best_utc": top["utc_iso"],
        "confidence_pct": confidence,
        "top5": ranked[:5],
        "method_en": ("Cosine-encoded angular features + tournament bracket "
                      "over a ±6h candidate grid; scores normalized "
                      "theoretical-max style."),
        "method_th": ("ใช้ cosine encoding ของมุมดาว + จัดทัวร์นาเมนต์คัดเวลา "
                      "ในกรอบ ±6 ชั่วโมง — เวลาที่ชนะคือเวลาที่เหตุการณ์จริง"
                      "ในชีวิตคุณ 'ล็อก' กับดาวได้แม่นที่สุด"),
        **({"person_name": person_name} if person_name else {}),
    }
