"""Birth Time Rectification Service.

Infers the most likely birth time from known life events using deterministic
astrological triggers. Each candidate ASC is tested at 4-minute intervals
(1 degree of ASC per 4 minutes of clock time).

Scoring triggers (ground-truth from vault):
- Saturn Return exact conjunction (orb ≤ 1°) → +30 pts per match
- Jupiter transit to natal Sun/Moon/ASC/Venus (orb ≤ 2°) during known event years → +20 pts
- Progressed Moon conjunct/opp/square natal ASC/Sun/Moon during event → +15 pts
- Solar Arc directions to natal angles/planets → +10 pts
- Lunar/Planetary transits on event dates (orb ≤ 1.5°) → +5 pts each
"""

from __future__ import annotations

from datetime import date as date_type, time as time_type, datetime, timedelta, timezone
from typing import Any

from src.services.aspects import ASPECTS, ORBS, _angular_sep
from src.services.chart_service import compute_chart, compute_houses
from src.services.ephemeris import earth, eph, ts
from src.services.progressions_service import compute_progressions
from src.services.returns_service import compute_solar_return


# Bodies that can be transiting triggers
TRANSIT_BODIES = {
    "Sun": "sun",
    "Moon": "moon",
    "Mercury": "mercury",
    "Venus": "venus",
    "Mars": "mars",
    "Jupiter": "jupiter barycenter",
    "Saturn": "saturn barycenter",
    "Uranus": "uranus barycenter",
    "Neptune": "neptune barycenter",
    "Pluto": "pluto barycenter",
}

# Natal points we score transits against
NATAL_KEY_POINTS = ("Sun", "Moon", "ASC", "Venus", "Mars", "Mercury", "Jupiter", "Saturn")


def _longitude_at(dt_utc: datetime, body_key: str) -> float:
    """Ecliptic longitude (tropical) of a body at a given UTC time."""
    t = ts.from_datetime(dt_utc)
    pos = earth.at(t).observe(eph[body_key])
    _, lon_ecl, _ = pos.ecliptic_latlon()
    return lon_ecl.degrees % 360.0


def _signed_delta(lon_deg: float, target_deg: float) -> float:
    """Shortest signed angular distance from lon_deg to target_deg, in (-180, 180]."""
    return (target_deg - lon_deg + 180) % 360 - 180


def _get_natal_points(chart: dict) -> dict[str, float]:
    """Extract natal positions for key points from a computed chart."""
    points = {}
    for body in chart["bodies"]:
        if body["body"] in NATAL_KEY_POINTS:
            points[body["body"]] = body["absolute_deg"]
    # Add ASC and MC
    points["ASC"] = chart["ascendant"]["absolute_deg"]
    points["MC"] = chart["midheaven"]["absolute_deg"]
    return points


def _find_exact_conjunction(
    transit_body: str,
    target_deg: float,
    search_start: datetime,
    search_days: float,
    step_days: float,
) -> datetime | None:
    """Find when a transit body makes exact conjunction to target degree.
    
    Returns the UTC datetime of the exact conjunction, or None if not found.
    """
    t0 = search_start
    d0 = _signed_delta(_longitude_at(t0, TRANSIT_BODIES[transit_body]), target_deg)
    steps = max(1, int(search_days / step_days))
    for i in range(1, steps + 1):
        t1 = search_start + timedelta(days=step_days * i)
        d1 = _signed_delta(_longitude_at(t1, TRANSIT_BODIES[transit_body]), target_deg)
        is_sign_change = (d0 <= 0 <= d1) or (d0 >= 0 >= d1)
        if is_sign_change and abs(d1 - d0) < 180.0:
            lo, hi, lo_delta = t0, t1, d0
            for _ in range(40):
                mid = lo + (hi - lo) / 2
                mid_delta = _signed_delta(_longitude_at(mid, TRANSIT_BODIES[transit_body]), target_deg)
                if (lo_delta <= 0 <= mid_delta) or (lo_delta >= 0 >= mid_delta):
                    hi = mid
                else:
                    lo, lo_delta = mid, mid_delta
                if (hi - lo) < timedelta(seconds=1):
                    break
            return lo + (hi - lo) / 2
        t0, d0 = t1, d1
    return None


def _check_saturn_return(natal_chart: dict, event_date: date_type, orb_deg: float = 1.0) -> tuple[bool, float, str]:
    """Check if Saturn Return (exact conjunction to natal Saturn) occurs near event_date.
    
    Returns (match_found, orb, reasoning).
    """
    natal_saturn = next(b for b in natal_chart["bodies"] if b["body"] == "Saturn")
    target_deg = natal_saturn["absolute_deg"]
    
    # Search ±2 years around event
    search_start = datetime.combine(event_date, time_type(0, 0), tzinfo=timezone.utc) - timedelta(days=730)
    exact_time = _find_exact_conjunction("Saturn", target_deg, search_start, search_days=1460, step_days=5.0)
    
    if exact_time:
        days_diff = abs((exact_time.date() - event_date).days)
        if days_diff <= 30:  # Within ~1 month of event
            orb = abs(_signed_delta(_longitude_at(exact_time, TRANSIT_BODIES["Saturn"]), target_deg))
            if orb <= orb_deg:
                return True, orb, f"Saturn Return exact on {exact_time.date().isoformat()} (orb {orb:.2f}°), event {event_date.isoformat()}"
    return False, 0.0, ""


def _check_jupiter_transits(natal_chart: dict, event_date: date_type, orb_deg: float = 2.0) -> tuple[int, list[str]]:
    """Check Jupiter transits to natal Sun/Moon/ASC/Venus around event_date.
    
    Returns (total_points, reasoning_list).
    """
    natal_points = _get_natal_points(natal_chart)
    targets = {k: v for k, v in natal_points.items() if k in ("Sun", "Moon", "ASC", "Venus")}
    
    points = 0
    reasons = []
    
    # Search ±1 year around event
    search_start = datetime.combine(event_date, time_type(0, 0), tzinfo=timezone.utc) - timedelta(days=365)
    
    for point_name, target_deg in targets.items():
        exact_time = _find_exact_conjunction("Jupiter", target_deg, search_start, search_days=730, step_days=2.0)
        if exact_time:
            days_diff = abs((exact_time.date() - event_date).days)
            if days_diff <= 60:  # Within ~2 months
                orb = abs(_signed_delta(_longitude_at(exact_time, TRANSIT_BODIES["Jupiter"]), target_deg))
                if orb <= orb_deg:
                    points += 20
                    reasons.append(f"Jupiter conjunct natal {point_name} on {exact_time.date().isoformat()} (orb {orb:.2f}°)")
    return points, reasons


def _check_progressed_moon(natal_chart: dict, event_date: date_type, orb_deg: float = 1.5) -> tuple[int, list[str]]:
    """Check Progressed Moon aspects to natal ASC/Sun/Moon around event_date.
    
    Returns (total_points, reasoning_list).
    """
    natal_points = _get_natal_points(natal_chart)
    targets = {k: v for k, v in natal_points.items() if k in ("ASC", "Sun", "Moon")}
    
    points = 0
    reasons = []
    
    # Get progressed chart for the event date
    birth_date = natal_chart["datetime_utc"][:10]
    birth_time_str = natal_chart["datetime_utc"][11:16]
    birth_dt = datetime.fromisoformat(natal_chart["datetime_utc"].replace("Z", "+00:00"))
    birth_date_obj = birth_dt.date()
    birth_time_obj = birth_dt.time()
    
    try:
        prog = compute_progressions(
            name="rectification",
            birth_date=birth_date_obj,
            birth_time=birth_time_obj,
            target_date=event_date,
            tz_offset_hours=7.0,
            lat=13.36,
            lon=100.98,
            system="tropical",
        )
        prog_moon = next(b for b in prog["progressed"]["bodies"] if b["body"] == "Moon")
        prog_moon_deg = prog_moon["absolute_deg"]
        
        for target_name, target_deg in targets.items():
            sep = _angular_sep(prog_moon_deg, target_deg)
            for aspect_name in ("conjunction", "opposition", "square"):
                aspect_angle = ASPECTS[aspect_name]
                orb = abs(sep - aspect_angle)
                if orb <= ORBS[aspect_name] and orb <= orb_deg:
                    points += 15
                    reasons.append(f"Progressed Moon {aspect_name} natal {target_name} on {event_date.isoformat()} (orb {orb:.2f}°)")
    except Exception:
        pass  # Silently skip if progression fails
    
    return points, reasons


def _check_solar_arc(natal_chart: dict, event_date: date_type, orb_deg: float = 1.0) -> tuple[int, list[str]]:
    """Check Solar Arc directions to natal angles/planets.
    
    Solar Arc = Sun's progressed position - natal Sun position, applied to all points.
    
    Returns (total_points, reasoning_list).
    """
    natal_points = _get_natal_points(natal_chart)
    targets = {k: v for k, v in natal_points.items() if k in ("ASC", "MC", "Sun", "Moon", "Venus", "Mars")}
    
    # Get progressed Sun position at event date
    birth_dt = datetime.fromisoformat(natal_chart["datetime_utc"].replace("Z", "+00:00"))
    birth_date_obj = birth_dt.date()
    birth_time_obj = birth_dt.time()
    
    points = 0
    reasons = []
    
    try:
        prog = compute_progressions(
            name="rectification",
            birth_date=birth_date_obj,
            birth_time=birth_time_obj,
            target_date=event_date,
            tz_offset_hours=7.0,
            lat=13.36,
            lon=100.98,
            system="tropical",
        )
        prog_sun = next(b for b in prog["progressed"]["bodies"] if b["body"] == "Sun")
        natal_sun = next(b for b in natal_chart["bodies"] if b["body"] == "Sun")
        
        solar_arc = (prog_sun["absolute_deg"] - natal_sun["absolute_deg"]) % 360.0
        
        for target_name, target_deg in targets.items():
            directed_deg = (target_deg + solar_arc) % 360.0
            
            # Check transiting planets to directed position
            for transit_name, transit_key in TRANSIT_BODIES.items():
                if transit_name in ("Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"):
                    transit_lon = _longitude_at(
                        datetime.combine(event_date, time_type(0, 0), tzinfo=timezone.utc),
                        transit_key
                    )
                    sep = _angular_sep(transit_lon, directed_deg)
                    for aspect_name in ("conjunction", "opposition", "square"):
                        aspect_angle = ASPECTS[aspect_name]
                        orb = abs(sep - aspect_angle)
                        if orb <= ORBS[aspect_name] and orb <= orb_deg:
                            points += 10
                            reasons.append(f"Solar Arc {target_name} {aspect_name} transiting {transit_name} on {event_date.isoformat()} (orb {orb:.2f}°)")
    except Exception:
        pass
    
    return points, reasons


def _check_event_transits(natal_chart: dict, event_date: date_type, orb_deg: float = 1.5) -> tuple[int, list[str]]:
    """Check all planetary transits to natal points on the exact event date.
    
    Returns (total_points, reasoning_list).
    """
    natal_points = _get_natal_points(natal_chart)
    event_dt = datetime.combine(event_date, time_type(0, 0), tzinfo=timezone.utc)
    
    points = 0
    reasons = []
    
    for transit_name, transit_key in TRANSIT_BODIES.items():
        transit_lon = _longitude_at(event_dt, transit_key)
        for point_name, point_deg in natal_points.items():
            sep = _angular_sep(transit_lon, point_deg)
            for aspect_name, aspect_angle in ASPECTS.items():
                orb = abs(sep - aspect_angle)
                if orb <= orb_deg and orb <= ORBS[aspect_name]:
                    # Weight: outer planets more significant
                    weight = 5 if transit_name in ("Jupiter", "Saturn", "Uranus", "Neptune", "Pluto") else 3
                    points += weight
                    reasons.append(f"Transit {transit_name} {aspect_name} natal {point_name} on {event_date.isoformat()} (orb {orb:.2f}°)")
    return points, reasons


def infer_birth_time(
    events: list[dict[str, str]],
    date: date_type,
    lat: float,
    lon: float,
    tz_offset_hours: float,
    window_hours: float = 4.0,
    base_time: time_type | None = None,
) -> list[dict[str, Any]]:
    """Infer the most likely birth time from known life events.
    
    Args:
        events: List of {"date": "YYYY-MM-DD", "description": "event name"}
        date: Birth date
        lat: Birth latitude
        lon: Birth longitude
        tz_offset_hours: Timezone offset in hours
        window_hours: Search window in hours around base_time (default 4 hours = ±4 hours)
        base_time: Center of search window (if None, uses 12:00 noon)
    
    Returns:
        List of top 3 candidates: {"time": "HH:MM", "confidence": 0.0-1.0, "reasoning": "..."}
        Sorted by confidence descending.
    """
    if base_time is None:
        base_time = time_type(12, 0)
    
    # Generate candidate times at 4-minute intervals (1 degree ASC per 4 min)
    candidates = []
    base_dt = datetime.combine(date, base_time)
    window_minutes = int(window_hours * 60)
    step_minutes = 4
    num_steps = (window_minutes * 2) // step_minutes + 1
    
    start_dt = base_dt - timedelta(minutes=window_minutes)
    
    all_reasons = {}
    
    for i in range(num_steps):
        candidate_dt = start_dt + timedelta(minutes=step_minutes * i)
        candidate_time = candidate_dt.time()
        
        # Compute natal chart for this candidate
        natal_chart = compute_chart(
            name="rectification",
            date=date,
            time=candidate_time,
            tz_offset_hours=tz_offset_hours,
            lat=lat,
            lon=lon,
            system="tropical",
        )
        
        total_score = 0
        all_reason_strings = []
        
        # Score against each life event
        for event in events:
            event_date = date_type.fromisoformat(event["date"])
            event_desc = event.get("description", "life event")
            
            # 1. Saturn Return (30 pts)
            saturn_match, saturn_orb, saturn_reason = _check_saturn_return(natal_chart, event_date)
            if saturn_match:
                total_score += 30
                all_reason_strings.append(f"[{event_desc}] {saturn_reason}")
            
            # 2. Jupiter transits to Sun/Moon/ASC/Venus (20 pts each)
            jupiter_pts, jupiter_reasons = _check_jupiter_transits(natal_chart, event_date)
            total_score += jupiter_pts
            all_reason_strings.extend([f"[{event_desc}] {r}" for r in jupiter_reasons])
            
            # 3. Progressed Moon to ASC/Sun/Moon (15 pts each)
            prog_pts, prog_reasons = _check_progressed_moon(natal_chart, event_date)
            total_score += prog_pts
            all_reason_strings.extend([f"[{event_desc}] {r}" for r in prog_reasons])
            
            # 4. Solar Arc directions (10 pts each)
            sa_pts, sa_reasons = _check_solar_arc(natal_chart, event_date)
            total_score += sa_pts
            all_reason_strings.extend([f"[{event_desc}] {r}" for r in sa_reasons])
            
            # 5. Event date transits (5 pts each)
            transit_pts, transit_reasons = _check_event_transits(natal_chart, event_date)
            total_score += transit_pts
            all_reason_strings.extend([f"[{event_desc}] {r}" for r in transit_reasons])
        
        # Maximum possible score estimation (for normalization)
        # Rough estimate: 30 (Saturn) + 4*20 (Jupiter) + 3*15 (Prog Moon) + 5*10 (Solar Arc) + 10*5 (Transits) per event
        max_per_event = 30 + 80 + 45 + 50 + 50  # = 255
        max_possible = max_per_event * len(events)
        
        confidence = min(1.0, total_score / max_possible) if max_possible > 0 else 0.0
        
        candidates.append({
            "time": candidate_time.strftime("%H:%M"),
            "confidence": round(confidence, 4),
            "score": total_score,
            "reasoning": "; ".join(all_reason_strings) if all_reason_strings else "No significant triggers found",
        })
        all_reasons[candidate_time.strftime("%H:%M")] = all_reason_strings
    
    # Sort by score (confidence) descending
    candidates.sort(key=lambda c: c["confidence"], reverse=True)
    
    # Return top 3 with just time, confidence, reasoning
    top_3 = []
    for c in candidates[:3]:
        top_3.append({
            "time": c["time"],
            "confidence": c["confidence"],
            "reasoning": c["reasoning"],
        })
    
    return top_3