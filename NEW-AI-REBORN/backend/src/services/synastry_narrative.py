"""
Synastry Narrative Service — generates relationship readings.
"""
from __future__ import annotations
from .narrative_engine import generate_synastry_narrative
from .chart_service import compute_chart


def generate_synastry_reading(
    name_a: str, date_a, time_a, tz_a: float, lat_a: float, lon_a: float,
    name_b: str, date_b, time_b, tz_b: float, lat_b: float, lon_b: float,
    lang: str = "th",
) -> dict:
    """Generate a full synastry reading between two people."""
    chart_a = compute_chart(name_a, date_a, time_a, tz_a, lat_a, lon_a)
    chart_b = compute_chart(name_b, date_b, time_b, tz_b, lat_b, lon_b)
    return generate_synastry_narrative(chart_a, chart_b, lang)


def generate_composite_reading(
    name_a: str, date_a, time_a, tz_a: float, lat_a: float, lon_a: float,
    name_b: str, date_b, time_b, tz_b: float, lat_b: float, lon_b: float,
    lang: str = "th",
) -> dict:
    """Generate a composite chart reading."""
    chart_a = compute_chart(name_a, date_a, time_a, tz_a, lat_a, lon_a)
    chart_b = compute_chart(name_b, date_b, time_b, tz_b, lat_b, lon_b)
    
    # Composite = midpoints
    composite_bodies = []
    for ba in chart_a.get("bodies", []):
        bb = next((b for b in chart_b["bodies"] if b["body"] == ba["body"]), None)
        if bb:
            mid_deg = (ba["absolute_deg"] + bb["absolute_deg"]) / 2
            composite_bodies.append({
                "body": ba["body"],
                "absolute_deg": mid_deg,
                "sign": _deg_to_sign(mid_deg),
            })
    
    composite = {
        "name": f"{name_a} + {name_b}",
        "bodies": composite_bodies,
        "system": "tropical",
    }
    
    from .narrative_engine import generate_natal_narrative
    return generate_natal_narrative(composite, lang)


def _deg_to_sign(deg: float) -> str:
    SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    return SIGNS[int(deg // 30) % 12]
