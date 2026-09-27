"""KP sub-lord engine — Placidus cusps + Vimshottari-proportion sub-lords
with KP (Newcomb) ayanamsa. The canonical serious-practitioner rectification/
event-filter system.

Sub-lord chain: sign lord -> star (nakshatra) lord -> sub-lord, where the sub
division splits each nakshatra proportionally by Vimshottari years.
"""
from __future__ import annotations

import math
from datetime import datetime

from src.services.chart_service import compute_chart

# Vimshottari dasha years (also the sub-division proportions)
_VIM_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
              "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
_VIM_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
              "Jupiter", "Saturn", "Mercury"]
_NAKSHATRA_SPAN = 360 / 27  # 13°20'

# Ashwini starts at 0° with Ketu; order cycles through _VIM_ORDER
NAKSHATRA_LORDS = [_VIM_ORDER[i % 9] for i in range(27)]

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]


def kp_ayanamsa(dt_utc: datetime) -> float:
    """KP-Newcomb ayanamsa ≈ Lahiri − 6′.

    Lahiri linear approx: 23°51'11\" at J2000 + 50.29"/yr.
    Good to ±1′ across 1900-2100 — sufficient for sub-lord work with flags.
    """
    j2000 = datetime(2000, 1, 1, 12)
    dt_naive = dt_utc.replace(tzinfo=None) if dt_utc.tzinfo else dt_utc
    years = (dt_naive - j2000).total_seconds() / (365.2422 * 86400)
    lahiri = 23.853055 + years * (50.29 / 3600)
    return lahiri - (6.0 / 60)


def sidereal(lon_tropical: float, dt_utc: datetime) -> float:
    return (lon_tropical - kp_ayanamsa(dt_utc)) % 360


def star_and_sub(sid_lon: float) -> dict:
    """Return star (nakshatra) lord and sub-lord for a sidereal longitude."""
    sid_lon %= 360
    nak_idx = int(sid_lon // _NAKSHATRA_SPAN)
    within = sid_lon - nak_idx * _NAKSHATRA_SPAN

    star_lord = NAKSHATRA_LORDS[nak_idx]
    # sub-lords: start from star lord, cycle _VIM_ORDER, proportional spans
    start_i = _VIM_ORDER.index(star_lord)
    pos = 0.0
    sub_lord, sub_span_frac = None, None
    for k in range(9):
        lord = _VIM_ORDER[(start_i + k) % 9]
        span = _NAKSHATRA_SPAN * (_VIM_YEARS[lord] / 120.0)
        if pos <= within < pos + span:
            sub_lord = lord
            sub_span_frac = (within - pos) / span
            break
        pos += span
    return {
        "nakshatra": nak_idx + 1,
        "star_lord": star_lord,
        "sub_lord": sub_lord,
        "position_in_sub": round(sub_span_frac or 0, 4),
    }


def cuspal_sub_lords(chart_trop: dict, dt_utc: datetime) -> list[dict]:
    """KP cusp table: house, cusp longitude (sidereal), sign/star/sub lords."""
    hdata = chart_trop.get("houses") or {}
    cusps_in = hdata.get("cusps", []) if isinstance(hdata, dict) else hdata
    out = []
    for h in list(cusps_in)[:12]:
        cusp_trop = h["absolute_deg"] if isinstance(h, dict) else h
        sid = sidereal(float(cusp_trop), dt_utc)
        i = h.get("house", len(out) + 1) if isinstance(h, dict) else len(out) + 1
        ss = star_and_sub(sid)
        sign_idx = int(sid // 30)
        out.append({
            "house": int(i),
            "cusp_sidereal": round(sid, 4),
            "sign": SIGNS[sign_idx],
            "sign_lord": SIGN_RULER[SIGNS[sign_idx]],
            **ss,
        })
    return out


from src.services.hellenistic_timelords_service import SIGN_RULER  # noqa: E402


def planet_kp_table(chart_trop: dict, dt_utc: datetime) -> list[dict]:
    bodies = chart_trop.get("bodies") or []
    rows = []
    for b in bodies:
        sid = sidereal(float(b["absolute_deg"]), dt_utc)
        ss = star_and_sub(sid)
        rows.append({"body": b["body"], "sidereal": round(sid, 3), **ss})
    return rows


def kp_event_filter(chart_trop: dict, dt_utc: datetime, category: str) -> dict:
    """Event allowed only if house cusp sub-lord's significators include the
    event houses. Simplified significator rule: cusp sub-lord must occupy OR
    star-rule one of the event houses (occupant/star-lord of that house)."""
    EVENT_HOUSES = {
        "marriage": (2, 7, 11),
        "job": (2, 6, 10),
        "career": (2, 6, 10),
        "children": (2, 5, 11),
        "money": (2, 11),
        "travel": (3, 9, 12),
    }
    if category not in EVENT_HOUSES:
        raise ValueError(f"category must be in {list(EVENT_HOUSES)}")
    want = set(EVENT_HOUSES[category])

    cusps = cuspal_sub_lords(chart_trop, dt_utc)
    planets = {p["body"]: p for p in planet_kp_table(chart_trop, dt_utc)}

    # house occupants: planets whose sidereal falls in that house's sign-span
    # (simplified whole-sign occupancy relative to each cusp)
    def house_of(lon: float) -> int:
        best = 1
        for c in cusps:
            if lon >= c["cusp_sidereal"] - 1e-9:
                best = max(best, c["house"])
        return best

    results = []
    for c in cusps:
        if c["house"] not in want:
            continue
        sub = c["sub_lord"]
        prow = planets.get(sub)
        occupied_house = house_of(prow["sidereal"]) if prow else None
        star_of = prow["star_lord"] if prow else None
        signifies = False
        how = []
        if occupied_house in want:
            signifies = True
            how.append(f"sub-lord {sub} occupies H{occupied_house}")
        # strong rule: sub-lord is STAR LORD of a planet sitting in target houses
        for pb, pr in planets.items():
            hh = house_of(pr["sidereal"])
            if hh in want and pr["star_lord"] == sub:
                signifies = True
                how.append(f"{pb} in H{hh} has star-lord {sub}")
        results.append({
            "house": c["house"],
            "cusp_sub_lord": sub,
            "signifies_event": signifies,
            "how": how[:3],
        })

    allowed = all(r["signifies_event"] for r in results) if results else False
    return {
        "system": "kp-event-filter",
        "category": category,
        "event_houses": sorted(want),
        "cusps": results,
        "event_allowed_by_kp": allowed,
        "interpretation": {
            "th": (
                f"ระบบ KP: เหตุการณ์ '{category}' "
                + ("ผ่านเกณฑ์ sub-lord ครบทุกบ้าน — ช่วงนี้อนุญาต"
                   if allowed else
                   "ยังไม่ผ่านเกณฑ์ sub-lord ทุกบ้าน — ควรเลื่อนจังหวะ")
            ),
            "en": (f"KP filter for '{category}': "
                   f"{'PASSED' if allowed else 'NOT PASSED'} on all event houses."),
        },
    }
