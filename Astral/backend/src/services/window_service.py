"""Favourable / cautionary time windows for a natal chart.

Scans transit-to-natal aspects across a date range and scores each sampled
slot, so a client can answer "when this week is a good time to X" instead
of only "what is aspecting me right now" (transit_service.compute_now).

The Moon moves ~13 deg/day, so a daily sample smears its aspects together;
sampling several times a day keeps them distinguishable, which is the whole
point of a window.
"""

from datetime import date as date_type, datetime, time as time_type, timedelta

from src.services.aspects import compute_cross_aspects
from src.services.chart_service import compute_chart

# Aspects are read as supportive or tense in the classical scheme. Conjunction
# is deliberately absent: it intensifies whatever it touches rather than
# carrying a valence of its own, so it is scored via the body it hits.
_HARMONIOUS = {"trine", "sextile"}
_TENSE = {"square", "opposition"}

# Benefics and malefics, plus the luminaries. A conjunction inherits the
# nature of the transiting body it involves.
_BODY_TONE = {
    "Venus": 1.0, "Jupiter": 1.0, "Sun": 0.5, "Moon": 0.5, "Mercury": 0.3,
    "Mars": -0.7, "Saturn": -0.8, "Uranus": -0.4, "Neptune": -0.3, "Pluto": -0.6,
}

# The Moon is fast, so its aspects describe the texture of an afternoon
# rather than a season; weight it below the slower bodies whose aspects mark
# out genuinely distinct periods.
_TRANSIT_WEIGHT = {
    "Moon": 0.6, "Sun": 1.0, "Mercury": 0.8, "Venus": 1.0, "Mars": 1.0,
    "Jupiter": 1.3, "Saturn": 1.3, "Uranus": 1.0, "Neptune": 0.8, "Pluto": 1.2,
}

# Natal points that describe the person most directly.
_NATAL_WEIGHT = {
    "Sun": 1.3, "Moon": 1.3, "ASC": 1.3, "Venus": 1.0, "Mars": 1.0,
    "Mercury": 1.0, "Jupiter": 0.8, "Saturn": 0.8,
    "Uranus": 0.5, "Neptune": 0.5, "Pluto": 0.5,
}

_MAX_ORB = 3.0
_SLOT_HOURS = [6, 12, 20]
_SLOT_LABEL = {6: "เช้า", 12: "กลางวัน", 20: "ค่ำ"}

_BKK = (13.7563, 100.5018)


def _score_aspect(aspect: dict) -> float:
    """Signed strength of one transit-to-natal aspect.

    Tight aspects count for more than wide ones, so orb tapers the score
    linearly to zero at _MAX_ORB.
    """
    orb = aspect["orb"]
    if orb > _MAX_ORB:
        return 0.0
    closeness = 1.0 - (orb / _MAX_ORB)

    kind = aspect["aspect"]
    transit_body = aspect["body_b"]
    natal_body = aspect["body_a"]

    if kind in _HARMONIOUS:
        valence = 1.0
    elif kind in _TENSE:
        valence = -1.0
    else:  # conjunction: takes its tone from the transiting body
        valence = _BODY_TONE.get(transit_body, 0.0)

    weight = (_TRANSIT_WEIGHT.get(transit_body, 0.8)
              * _NATAL_WEIGHT.get(natal_body, 0.8))
    return valence * closeness * weight


def _classify(score: float) -> str:
    if score >= 1.5:
        return "favourable"
    if score <= -1.5:
        return "caution"
    return "neutral"


def compute_windows(
    natal: dict,
    start: date_type,
    days: int = 7,
    tz_offset_hours: float = 7.0,
    lat: float = _BKK[0],
    lon: float = _BKK[1],
    system: str = "tropical",
) -> dict:
    if days < 1 or days > 31:
        raise ValueError("days must be between 1 and 31")

    slots = []
    for offset in range(days):
        day = start + timedelta(days=offset)
        for hour in _SLOT_HOURS:
            transit = compute_chart(
                name="transit",
                date=day,
                time=time_type(hour, 0),
                tz_offset_hours=tz_offset_hours,
                lat=lat,
                lon=lon,
                system=system,
            )
            aspects = [a for a in compute_cross_aspects(natal, transit)
                       if a["orb"] <= _MAX_ORB]
            score = sum(_score_aspect(a) for a in aspects)

            top = sorted(aspects, key=lambda a: abs(_score_aspect(a)), reverse=True)[:3]
            slots.append({
                "date": day.isoformat(),
                "hour": hour,
                "label": _SLOT_LABEL[hour],
                "score": round(score, 2),
                "rating": _classify(score),
                "drivers": [
                    {
                        "transit": a["body_b"],
                        "aspect": a["aspect"],
                        "natal": a["body_a"],
                        "orb": a["orb"],
                    }
                    for a in top
                ],
            })

    ranked = sorted(slots, key=lambda s: s["score"], reverse=True)
    return {
        "start": start.isoformat(),
        "days": days,
        "slots": slots,
        "best": ranked[:3],
        "worst": [s for s in ranked[-3:] if s["score"] < 0][::-1],
    }


def find_shared_windows(windows_a: dict, windows_b: dict) -> list[dict]:
    """Slots that score well for two people at once.

    Two charts rarely peak on the same aspect, so the combined score is what
    matters here, with a floor on each side to rule out a slot that is only
    good on average because one person is having a great day and the other a
    bad one.
    """
    by_key_b = {(s["date"], s["hour"]): s for s in windows_b["slots"]}
    shared = []
    for slot in windows_a["slots"]:
        other = by_key_b.get((slot["date"], slot["hour"]))
        if other is None:
            continue
        if slot["score"] <= 0 or other["score"] <= 0:
            continue
        shared.append({
            "date": slot["date"],
            "hour": slot["hour"],
            "label": slot["label"],
            "score_a": slot["score"],
            "score_b": other["score"],
            "combined": round(slot["score"] + other["score"], 2),
        })
    return sorted(shared, key=lambda s: s["combined"], reverse=True)
