"""Varshaphal / Tajika (Solar Return) — engine spec C:/AI/research-astrology/16.

The annual chart is cast at the exact moment the transiting Sun returns to
its NATAL longitude in the requested frame (Lahiri sidereal by default —
spec 16 is a Vedic module). The return instant itself is solved numerically
by ``returns_service.compute_solar_return`` (coarse scan + bisection,
~1-second precision) — no closed form exists against a general ephemeris.

Deterministic v1 rules implemented here (spec 16 §1):
- Varsha lagna  : ascendant of the solar-return chart.
- Muntha        : progressed ascendant — the natal ASC ADVANCED one sign
                  (30°) per completed year, i.e. muntha = natal_ASC + age×30°
                  mod 360. (Spec 16 writes "advanced by year count" for the
                  engine rule; its prose also floats a minus-sign variant —
                  we pin the forward/advance convention and say so.)
- Year Lord     : strongest planet among {varsha-lagna lord, muntha lord,
                  10th-house lord from the varsha lagna}, scored by dignity
                  (exaltation/domicile), angular house placement, and a
                  combustion penalty near the SR Sun. Ties resolve in that
                  candidate order.
- Tajika aspects: whole-sign conj / opp (1/7), trine (3/11), square (4/10),
                  sextile (5/9).
- Sahams        : key Tajika lots cast from the SR chart (Fortune/Spirit/
                  Eros/Courage formulas as coded below).

Regression anchor (spec 16 §4): owner natal sidereal Sun ≈ Taurus 4.37° →
the 2026 return lands ≈ 14 May 2026; consecutive returns drift < 1 day/year.
"""

from __future__ import annotations

from datetime import date as date_type, time as time_type

from src.services.returns_service import compute_solar_return
from src.services.chart_service import SIGNS

# Classical domicile rulers by 0-based SIGNS index.
RULERS_BY_SIGN_IDX = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun",
    5: "Mercury", 6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn",
    10: "Saturn", 11: "Jupiter",
}

_EXALTATION_IDX = {"Sun": 0, "Moon": 1, "Mercury": 5, "Venus": 11, "Mars": 9, "Jupiter": 3, "Saturn": 6}
_DOMICILE_IDX = {"Sun": [4], "Moon": [3], "Mercury": [2, 5], "Venus": [1, 6],
                 "Mars": [0, 7], "Jupiter": [8, 11], "Saturn": [9, 10]}
_ANGULAR_HOUSES = {1, 4, 7, 10}
_COMBUSTION_ORB_DEG = 8.0


def _sign_index(sign: str) -> int:
    """0-based index into SIGNS, tolerating Thai-prefixed labels."""
    try:
        return SIGNS.index(sign)
    except ValueError:
        for i, s in enumerate(SIGNS):
            if sign in s or s in sign:
                return i
    raise ValueError(f"unknown sign label: {sign!r}")


def _to_sign(lon_deg: float) -> tuple[str, float]:
    idx = int(lon_deg // 30) % 12
    return SIGNS[idx], lon_deg % 30


def _muntha(natal_asc_lon: float, age_years: int) -> dict:
    """Natal ASC advanced 30° per completed year (forward convention, see docstring)."""
    lon = (natal_asc_lon + 30.0 * age_years) % 360.0
    sign, deg = _to_sign(lon)
    natal_idx = int(natal_asc_lon // 30) % 12
    muntha_idx = int(lon // 30) % 12
    # Whole-sign house counted from the natal lagna.
    house_from_natal_lagna = ((muntha_idx - natal_idx) % 12) + 1
    return {
        "longitude": round(lon, 4),
        "sign": sign,
        "degree_in_sign": round(deg, 2),
        "lord": RULERS_BY_SIGN_IDX[muntha_idx],
        "house_from_natal_lagna": house_from_natal_lagna,
        "convention": "natal ASC + age×30° (advance)",
    }


def _house_of(body_lon: float, asc_lon: float) -> int:
    return ((int(body_lon // 30) - int(asc_lon // 30)) % 12) + 1


def _strength(chart: dict, planet: str) -> float:
    """Simple deterministic strength score for a Year-Lord candidate."""
    bodies = {b["body"]: b for b in chart.get("bodies", [])}
    body = bodies.get(planet)
    if not body:
        return float("-inf")
    score = 0.0
    sign_idx = _sign_index(body["sign"])
    if _EXALTATION_IDX.get(planet) == sign_idx:
        score += 2.0
    elif sign_idx in _DOMICILE_IDX.get(planet, []):
        score += 1.5
    asc_lon = chart["ascendant"]["absolute_deg"]
    if _house_of(body["absolute_deg"], asc_lon) in _ANGULAR_HOUSES:
        score += 1.0
    sun = bodies.get("Sun")
    if sun and abs((body["absolute_deg"] - sun["absolute_deg"] + 180) % 360 - 180) <= _COMBUSTION_ORB_DEG:
        score -= 1.0
    return score


def _year_lord(sr_chart: dict, muntha_lord: str) -> dict:
    """Strongest of {lagna lord, muntha lord, 10th lord} — spec 16 §1 v1 rule."""
    asc_idx = int(sr_chart["ascendant"]["absolute_deg"] // 30) % 12
    tenth_sign_idx = (asc_idx + 9) % 12  # whole-sign 10th house
    candidates = [
        ("lagna lord", RULERS_BY_SIGN_IDX[asc_idx]),
        ("muntha lord", muntha_lord),
        ("tenth lord", RULERS_BY_SIGN_IDX[tenth_sign_idx]),
    ]
    scored = [
        {"role": role, "planet": planet, "score": round(_strength(sr_chart, planet), 2)}
        for role, planet in candidates
    ]
    best = max(scored, key=lambda s: s["score"])  # max() keeps first on ties → candidate order
    return {
        "planet": best["planet"],
        "basis": f"strongest of [{', '.join(r for r, _ in candidates)}] by dignity/house/combustion",
        "score": best["score"],
        "candidates": scored,
    }


def _tajika_aspects(chart: dict) -> list[dict]:
    """Tajika whole-sign aspects: same-sign conj, 1/7, 3/11, 4/10, 5/9."""
    points = chart.get("bodies", []) + ([chart["ascendant"]] if chart.get("ascendant") else [])

    aspects = []
    for i, p1 in enumerate(points):
        for p2 in points[i + 1:]:
            diff = (_sign_index(p2["sign"]) - _sign_index(p1["sign"])) % 12

            aspect_name = None
            if diff == 0:
                aspect_name = "conjunction"
            elif diff == 6:
                aspect_name = "opposition"
            elif diff in (2, 10):   # 3/11 signs = trine
                aspect_name = "trine"
            elif diff in (3, 9):    # 4/10 signs = square
                aspect_name = "square"
            elif diff in (4, 8):    # 5/9 signs = sextile
                aspect_name = "sextile"

            if aspect_name:
                aspects.append({
                    "body_a": p1["body"],
                    "body_b": p2["body"],
                    "sign_a": p1["sign"],
                    "sign_b": p2["sign"],
                    "aspect": aspect_name,
                })
    aspects.sort(key=lambda a: a["body_a"])
    return aspects


def _sahams(varshaphal_chart: dict) -> dict:
    """Key Tajika lots cast wholly inside the SR chart."""
    bodies_v = {b["body"]: b["absolute_deg"] for b in varshaphal_chart.get("bodies", [])}
    asc_v = varshaphal_chart.get("ascendant", {}).get("absolute_deg", 0)

    def part(formula: str) -> float:
        vars_ = {
            "ASC": asc_v,
            "Sun": bodies_v.get("Sun", 0),
            "Moon": bodies_v.get("Moon", 0),
            "Mercury": bodies_v.get("Mercury", 0),
            "Venus": bodies_v.get("Venus", 0),
            "Mars": bodies_v.get("Mars", 0),
            "Jupiter": bodies_v.get("Jupiter", 0),
            "Saturn": bodies_v.get("Saturn", 0),
        }
        terms = formula.split(" - ")
        value = sum(vars_[t.strip()] for t in terms[0].split(" + "))
        for t in terms[1:]:
            value -= vars_[t.strip()]
        return value % 360

    out = {}
    for name, formula in [
        ("Punya", "ASC + Jupiter - Sun"),       # fortune (day formula, spec 16 §2)
        ("Spirit", "ASC + Sun - Moon"),
        ("Vivaha", "ASC + Venus - Moon"),       # marriage [formula flagged VERIFY in spec]
        ("Courage", "ASC + Mars - Saturn"),
    ]:
        lon = part(formula)
        sign, deg = _to_sign(lon)
        out[name] = {"sign": sign, "degree": round(deg, 2), "absolute_deg": round(lon, 2)}
    return out


def compute_varshaphal(
    name: str,
    birth_date: date_type,
    birth_time: time_type,
    target_year: int,
    tz_offset_hours: float = 7.0,
    lat: float = 13.8591,
    lon: float = 100.5217,
    system: str = "sidereal",
) -> dict:
    """Varshaphal for `target_year`: return instant + lagna/Muntha/Year Lord."""
    sr = compute_solar_return(
        name=name,
        birth_date=birth_date,
        birth_time=birth_time,
        target_year=target_year,
        tz_offset_hours=tz_offset_hours,
        lat=lat,
        lon=lon,
        system=system,
    )

    varshaphal_chart = sr["chart"]
    natal_chart = sr["natal"]

    asc = varshaphal_chart["ascendant"]
    asc_idx = int(asc["absolute_deg"] // 30) % 12
    varsha_lagna = {
        "sign": asc["sign"],
        "degree": asc["degree"],
        "lord": RULERS_BY_SIGN_IDX[asc_idx],
    }

    age_years = target_year - birth_date.year
    muntha = _muntha(natal_chart["ascendant"]["absolute_deg"], age_years)

    tajika = _tajika_aspects(varshaphal_chart)
    sahams = _sahams(varshaphal_chart)

    return {
        "target_year": target_year,
        "return_datetime_utc": sr["return_datetime_utc"],
        "system": system,
        "varsha_lagna": varsha_lagna,
        "muntha": muntha,
        "year_lord": _year_lord(varshaphal_chart, muntha["lord"]),
        "tajika_aspects": tajika,
        "sahams": sahams,
        "chart": varshaphal_chart,
    }
