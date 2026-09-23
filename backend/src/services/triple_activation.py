"""Triple-activation timing rule — high-confidence event windows.

A window is HIGH CONFIDENCE only when >=3 independent layers agree:
  L1. Annual profection (house + lord of year)          [hellenistic_timelords]
  L2. Slow transit (Saturn/Jupiter/Rahu-Ketu nodes) to that lord/house
                                                        [chart transits]
  L3. Vimshottari dasha (MD/AD/PD lord signifying)      [fusion_engine]
Optionally L4: solar arc / progression cross-check.

Pure orchestration over existing engines — no new astronomy code.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

from src.services.chart_service import compute_chart
from src.services.hellenistic_timelords_service import (
    annual_profections, SIGN_RULER,
)
from src.services.fusion_engine import sidereal_moon_lon, vimshottari_now

SLOW_BODIES = ("Saturn", "Jupiter", "Rahu", "Ketu")
# houses that "signify" each other for common life events
_EVENT_HOUSE_MAP = {
    "marriage": (7, (2, 11)),
    "career": (10, (2, 6)),
    "children": (5, (2, 11)),
    "money": (2, (11,)),
    "travel": (9, (12,)),
    "health": (6, (1, 8)),
    "education": (4, (9,)),
}


def _whole_sign_house(planet_lon: float, asc_lon: float) -> int:
    return int(((planet_lon - asc_lon) % 360) // 30) + 1


def _transit_layer(chart_trop: dict, now_utc: datetime,
                   target_house: int, allied: tuple[int, ...]) -> tuple[bool, list[str]]:
    """L2: slow body transiting target or allied house."""
    bodies = {b["body"]: b["absolute_deg"] for b in chart_trop["bodies"]}
    asc = chart_trop["ascendant"]["absolute_deg"]
    hits = []
    for body in SLOW_BODIES:
        lon = bodies.get(body)
        if lon is None:
            continue
        house = _whole_sign_house(float(lon), float(asc))
        if house == target_house or house in allied:
            hits.append(f"{body}→H{house}")
    return bool(hits), hits


def _dasha_layer(moon_sid_birth_lon: float, birth_dt_utc: datetime,
                 now_utc: datetime, target_house: int,
                 allied: tuple[int, ...]) -> tuple[bool, list[str]]:
    """L3: current MD/AD/PD lords rule the target/allied houses from natal Moon."""
    yf_b = birth_dt_utc.year + birth_dt_utc.timetuple().tm_yday / 365.2425
    yf_n = now_utc.year + now_utc.timetuple().tm_yday / 365.2425
    dasha = vimshottari_now(moon_sid_birth_lon, yf_b, yf_n)

    # natal Moon whole-sign houses counted FROM MOON (Chandra lagna)
    moon_house_of_lord = {}
    # We approximate: a dasha lord 'signifies' the house if it RULES the sign
    # of the target/allied house counted from Moon's sign.
    moon_sign_idx = int(moon_sid_birth_lon // 30)
    HOUSE_LORD_BY_SIGN = {0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon",
                          4: "Sun", 5: "Mercury", 6: "Venus", 7: "Mars",
                          8: "Jupiter", 9: "Saturn", 10: "Saturn",
                          11: "Jupiter"}
    active_lords = []
    for level in ("mahadasha", "antardasha"):
        d = dasha.get(level) or {}
        if isinstance(d, dict) and d.get("lord"):
            active_lords.append(d["lord"])
    pd = dasha.get("pratyantardasha") or {}
    if isinstance(pd, dict) and pd.get("lord"):
        active_lords.append(pd["lord"])

    reasons = []
    ok = False
    for h in (target_house,) + allied:
        sign_idx = (moon_sign_idx + h - 1) % 12
        ruler = HOUSE_LORD_BY_SIGN[sign_idx]
        if ruler in active_lords:
            ok = True
            reasons.append(f"{ruler} rules H{h}-from-Moon & is active "
                           f"({'+'.join(active_lords[:2])})")
    return ok, reasons


def triple_activation_windows(natal_name: str, birth_date_iso: str,
                              birth_time_hhmm: str, tz_offset_hours: float,
                              lat: float, lon: float,
                              category: str,
                              now_utc: datetime | None = None,
                              scan_days: int = 365) -> dict:
    """Scan forward `scan_days`, emit windows where >=3 layers agree."""
    if category not in _EVENT_HOUSE_MAP:
        raise ValueError(f"category must be one of {list(_EVENT_HOUSE_MAP)}")
    target_house, allied = _EVENT_HOUSE_MAP[category]
    now_utc = now_utc or datetime.now(timezone.utc)

    birth_local = datetime.fromisoformat(f"{birth_date_iso}T{birth_time_hhmm}:00")
    birth_utc = birth_local - timedelta(hours=tz_offset_hours)

    # natal sidereal ASC for profections (tropical fine for whole-sign too;
    # profections traditionally use natal rising sign — use tropical chart)
    natal = compute_chart("natal", birth_utc.date(), birth_utc.time(),
                          tz_offset_hours=0, lat=lat, lon=lon)
    asc_lon = float(natal["ascendant"]["absolute_deg"])
    now_naive = now_utc.replace(tzinfo=None) if now_utc.tzinfo else now_utc
    birth_naive = birth_utc.replace(tzinfo=None) if birth_utc.tzinfo else birth_utc
    age_at_now = (now_naive - birth_naive).days / 365.2425

    from datetime import timezone as _tz
    birth_utc_aware = (birth_utc.replace(tzinfo=_tz.utc)
                       if birth_utc.tzinfo is None else birth_utc)
    moon_sid_birth = sidereal_moon_lon(birth_utc_aware)

    windows = []
    step = timedelta(days=1)
    cursor = now_utc
    end = now_utc + timedelta(days=scan_days)
    current_run = None

    while cursor <= end:
        day_chart = compute_chart(
            "day", cursor.date(), cursor.time().replace(minute=0),
            tz_offset_hours=0, lat=lat, lon=lon)

        # L1 profection at this date
        cursor_naive = cursor.replace(tzinfo=None) if cursor.tzinfo else cursor
        age_here = (cursor_naive - birth_naive).days / 365.2425
        prof = annual_profections(int(age_here), asc_lon)
        l1_ok = prof["house"] in (target_house,) + allied
        l1_note = f"profection H{prof['house']} ({prof['lord']})"

        # L2 slow transit
        l2_ok, l2_hits = _transit_layer(day_chart, cursor, target_house, allied)

        # L3 dasha
        cursor_aware = (cursor.replace(tzinfo=_tz.utc)
                        if cursor.tzinfo is None else cursor)
        l3_ok, l3_notes = _dasha_layer(
            moon_sid_birth, birth_utc_aware, cursor_aware,
            target_house, allied)

        layers_active = sum([l1_ok, l2_ok, l3_ok])
        confidence = {0: "none", 1: "low", 2: "medium",
                      3: "HIGH"}.get(layers_active, "low")

        entry = {
            "date": cursor.date().isoformat(),
            "confidence": confidence,
            "layers": layers_active,
            "reasons": [l1_note] + l2_hits + l3_notes if layers_active else [],
        }

        if layers_active >= 3:
            if current_run is None:
                current_run = {"start": entry["date"], "end": entry["date"],
                               "peak_layers": layers_active,
                               "sample_reasons": entry["reasons"][:5]}
            else:
                current_run["end"] = entry["date"]
                current_run["peak_layers"] = max(current_run["peak_layers"],
                                                 layers_active)
        else:
            if current_run is not None:
                if len(windows) < 40:
                    windows.append(current_run)
                current_run = None
        cursor += step

    if current_run is not None:
        windows.append(current_run)

    best = max((w["peak_layers"] for w in windows), default=0)

    th = (
        f'สำหรับเรื่อง "{category}" ใน {scan_days} วันข้างหน้า '
        f'พบหน้าต่างมั่นใจสูง {len(windows)} ช่วง'
        + (f' — แรงสุด {best}/3 layers พร้อมกัน' if windows else
           ' — ยังไม่มีช่วงที่ 3 ชั้นเห็นพ้องพร้อมกัน รอจังหวะดีกว่านี้')
    )
    en = (f"{len(windows)} high-confidence window(s) for '{category}' "
          f"in the next {scan_days} days; strongest {best}/3 layers.")

    return {
        "system": "triple-activation-timing",
        "category": category,
        "target_house": target_house,
        "allied_houses": list(allied),
        "windows": windows,
        "strongest_alignment": f"{best}/3",
        "interpretation": {"th": th, "en": en},
    }
