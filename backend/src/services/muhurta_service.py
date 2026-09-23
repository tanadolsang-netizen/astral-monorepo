"""Electional / Muhurta engine — เลือกวันมงคล (spec 17).

Deterministic search over the existing chart engine:
coarse hourly scan → fine per-minute scan on candidates → ranked windows
with reason bullets, th/en interpretive text.

Scoring follows research-astrology/17-electional-muhurta-engine-spec.md §2-3.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from src.services.chart_service import compute_chart

# classical benefics/malefics (Lilly tradition)
_BENEFICS = {"Venus", "Jupiter"}
_MALEFICS = {"Saturn", "Mars"}
_ANGLES_HOUSES = {1, 4, 7, 10}

# action profiles: which planet must be dignified/direct + extra bias text
_ACTIONS = {
    "marriage": {
        "th": "งานมงคลสมรส/หมั้น", "en": "marriage or engagement",
        "priority": "Venus", "avoid_rx": ["Venus"], "waxing_moon_bonus": True,
    },
    "business": {
        "th": "เปิดกิจการ/ปล่อยผลงาน", "en": "business launch",
        "priority": "Jupiter", "avoid_rx": ["Mercury"], "waxing_moon_bonus": True,
    },
    "contract": {
        "th": "เซ็นสัญญา", "en": "contract signing",
        "priority": "Mercury", "avoid_rx": ["Mercury"], "waxing_moon_bonus": False,
    },
    "travel": {
        "th": "เดินทางไกล", "en": "travel",
        "priority": "Jupiter", "avoid_rx": [], "waxing_moon_bonus": True,
        "no_malefic_asc": True,
    },
    "moving": {
        "th": "ย้ายบ้าน", "en": "moving house",
        "priority": "Moon", "avoid_rx": [], "waxing_moon_bonus": True,
    },
}

_MERCURY_RX_APPROX_WINDOWS = [
    # 2026 Mercury retrograde periods (approx, from ephemeris tables)
    ("2026-02-25", "2026-03-20"),
    ("2026-06-29", "2026-07-23"),
    ("2026-10-24", "2026-11-13"),
]


def _is_mercury_rx(dt: datetime | str) -> bool:
    if isinstance(dt, str):
        s = dt.strip()
        if s.endswith("+00:00+00:00"):
            s = s[:-6]
        elif s.endswith("Z"):
            s = s[:-1]
        dt = datetime.fromisoformat(s).replace(tzinfo=None)
    for a, b in _MERCURY_RX_APPROX_WINDOWS:
        if datetime.fromisoformat(a) <= dt <= datetime.fromisoformat(b):
            return True
    return False


def _moon_waxing(chart: dict) -> bool:
    bodies = {p["body"]: p["absolute_deg"] for p in chart["bodies"]}
    sep = (bodies["Moon"] - bodies["Sun"]) % 360.0
    return sep < 180.0


def _via_combusta(chart: dict) -> bool:
    moon = next(p["absolute_deg"] for p in chart["bodies"] if p["body"] == "Moon")
    return 195.0 <= moon <= 225.0  # 15 Libra – 15 Scorpio


def score_chart(chart: dict, action: str) -> tuple[int, list[str], list[str]]:
    """Return (score, reasons_th, reasons_en)."""
    bodies = {p["body"]: p for p in chart["bodies"]}
    asc = chart["ascendant"]["absolute_deg"]
    score = 0
    why_th: list[str] = []
    why_en: list[str] = []
    profile = _ACTIONS[action]

    # Asc ruler dignity is complex; approximate with priority-planet dignity
    prio = bodies.get(profile["priority"])
    if prio and prio["dignity"]["domicile"]:
        score += 10
        why_th.append(f"ดาว{profile['priority']}อยู่ในราศีตนเอง (+10)")
        why_en.append(f"{profile['priority']} in domicile (+10)")
    elif prio and prio["dignity"]["exaltation"]:
        score += 8
        why_th.append(f"ดาว{profile['priority']}อยู่ในราศีเอกซาลเตชัน (+8)")
        why_en.append(f"{profile['priority']} exalted (+8)")

    waxing = _moon_waxing(chart)
    if waxing:
        score += 8 if profile.get("waxing_moon_bonus") else 4
        why_th.append("ดวงจันทร์ข้างขึ้น (+8)" if profile.get("waxing_moon_bonus")
                      else "ดวงจันทร์ข้างขึ้น (+4)")
        why_en.append("waxing Moon (+8)" if profile.get("waxing_moon_bonus")
                      else "waxing Moon (+4)")

    if _via_combusta(chart):
        score -= 6
        why_th.append("จันทร์อยู่ Via Combusta (−6)")
        why_en.append("Moon via combusta (−6)")

    for name in _BENEFICS:
        b = bodies.get(name)
        if b and b["house"] in _ANGLES_HOUSES:
            score += 7
            why_th.append(f"ดาว{name}อยู่บนจตุรัส (บ้าน {b['house']}) (+7)")
            why_en.append(f"{name} angular in house {b['house']} (+7)")

    for name in _MALEFICS:
        m = bodies.get(name)
        if not m:
            continue
        near_asc = abs((m["absolute_deg"] - asc + 180) % 360 - 180) <= 8
        if near_asc:
            score -= 12
            why_th.append(f"ดาว{name}ขึ้นบนลัคนา (−12)")
            why_en.append(f"{name} rising on Ascendant (−12)")

    if profile["priority"] == "Mercury" and _is_mercury_rx(chart["datetime_utc"]):
        score -= 15
        why_th.append("ดาวพุธย้อนรอย (−15) ไม่เหมาะเซ็นสัญญา")
        why_en.append("Mercury retrograde (−15), poor for contracts")

    return score, why_th, why_en


def find_windows(
    action: str,
    start_date: str,
    days: int = 60,
    lat: float = 13.7565,
    lon: float = 100.5018,
    tz_offset_hours: float = 7.0,
    top_n: int = 3,
    threshold: int = 12,
) -> dict:
    """Search [start_date, start_date+days) for best local-time windows."""
    if action not in _ACTIONS:
        raise ValueError(f"unknown action: {action}")

    start = datetime.fromisoformat(start_date)
    end = start + timedelta(days=days)

    def local_chart(dt_local: datetime) -> dict:
        utc_dt = dt_local - timedelta(hours=tz_offset_hours)
        return compute_chart("muhurta", utc_dt.date(), utc_dt.time(),
                             lat=lat, lon=lon)

    # coarse pass: every 3 hours at 10:00-18:00 local window
    candidates: list[tuple[int, datetime]] = []
    t = start.replace(hour=9, minute=0, second=0, microsecond=0)
    step = timedelta(hours=3)
    while t < end:
        if 9 <= t.hour <= 18:
            c = local_chart(t)
            s, _, _ = score_chart(c, action)
            if s >= threshold - 6:  # loose pre-filter
                candidates.append((s, t))
        t += step

    # fine pass: per-hour around each candidate peak, keep best hour
    refined: list[dict] = []
    seen_days: set[str] = set()
    for s0, t0 in sorted(candidates, reverse=True):
        day_key = t0.date().isoformat()
        if day_key in seen_days:
            continue  # one window per day keeps results spread out
        seen_days.add(day_key)
        best = None
        for h in range(8, 19):
            tt = t0.replace(hour=h, minute=30)
            c = local_chart(tt)
            s, th, en = score_chart(c, action)
            if best is None or s > best["score"]:
                best = {"score": s, "when_local": tt.isoformat(timespec="minutes"),
                        "reasons_th": th, "reasons_en": en}
        if best["score"] >= threshold:
            refined.append(best)
        if len(refined) >= top_n:
            break

    refined.sort(key=lambda w: w["score"], reverse=True)
    profile = _ACTIONS[action]
    return {
        "action": action,
        "action_th": profile["th"],
        "action_en": profile["en"],
        "searched_from": start.date().isoformat(),
        "searched_days": days,
        "windows": refined,
        "summary_th": _summary_th(action, profile, refined),
        "summary_en": _summary_en(profile, refined),
    }


def _summary_th(action: str, profile: dict, windows: list[dict]) -> str:
    if not windows:
        return (
            f"ช่วง {profile['th']} ใน {profile['en']} ไม่มีช่วงเวลาที่ดาวหนุนเต็มที่"
            f"ในห้วงวันที่ค้นหา — ลองขยายช่วงเวลา หรือเลื่อนไปเดือนถัดไปดีกว่า "
            f"โดยเฉพาะถ้าหลุมดาวพุธย้อนรอยตรงกับงานของคุณ"
        )
    top = windows[0]
    when = datetime.fromisoformat(top["when_local"])
    thai_date = when.strftime("%d/%m/%Y เวลา %H:%M น.")
    lines = [
        f"ช่วงมงคลสำหรับ{profile['th']}: วันที่ {thai_date} — คะแนนดาว {top['score']} แต้ม",
    ]
    if top["reasons_th"]:
        lines.append(f"เหตุผล: {' · '.join(top['reasons_th'][:3])}")
    if len(windows) > 1:
        alt = ", ".join(datetime.fromisoformat(w['when_local']).strftime('%d/%m') for w in windows[1:])
        lines.append(f"(วันสำรองที่ดี: {alt})")
    return "\n".join(lines)


def _summary_en(profile: dict, windows: list[dict]) -> str:
    if not windows:
        return (f"No strongly supported window found for {profile['en']} in the "
                "searched range — widen the range or push past the next "
                "Mercury retrograde.")
    top = windows[0]
    when = datetime.fromisoformat(top["when_local"])
    return (
        f"Best window for {profile['en']}: {when.strftime('%d %b %Y, %H:%M')} — "
        f"score {top['score']}. "
        + "; ".join(top["reasons_en"][:3])
    )
