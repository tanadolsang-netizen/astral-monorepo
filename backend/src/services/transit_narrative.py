"""
Transit Narrative Service — generates real-time transit readings per user.
"""
from __future__ import annotations
from typing import Optional
from datetime import datetime, timedelta
from .narrative_engine import generate_transit_natal_narrative
from .chart_service import compute_chart
from .kb_loader import get_transit_aspects


def get_current_transit_chart(lat: float, lon: float, tz_offset: float = 7.0) -> dict:
    """Compute current transit chart for a location."""
    now = datetime.utcnow()
    # Convert to local then UTC for chart computation
    from datetime import timezone
    dt_utc = now.replace(tzinfo=timezone.utc)
    return compute_chart(
        name="Transit",
        date=dt_utc.date(),
        time=dt_utc.time(),
        tz_offset_hours=tz_offset,
        lat=lat,
        lon=lon,
        system="tropical",
    )


def generate_daily_reading(natal_chart: dict, lat: float, lon: float, lang: str = "th") -> dict:
    """Generate a daily transit reading for a user.
    
    Args:
        natal_chart: user's natal chart
        lat: current latitude
        lon: current longitude
        lang: "th" or "en"
    
    Returns:
        dict with keys: date, active_transits, themes, advice
    """
    transit_chart = get_current_transit_chart(lat, lon)
    return generate_transit_natal_narrative(natal_chart, transit_chart, lang)


def generate_weekly_forecast(natal_chart: dict, lat: float, lon: float, lang: str = "th") -> list:
    """Generate a 7-day forecast."""
    forecasts = []
    today = datetime.utcnow().date()
    
    for day_offset in range(7):
        target_date = today + timedelta(days=day_offset)
        # Compute transit for that day
        transit_chart = compute_chart(
            name=f"Transit-{target_date}",
            date=target_date,
            time=datetime.min.time(),
            tz_offset_hours=7.0,
            lat=lat,
            lon=lon,
            system="tropical",
        )
        reading = generate_transit_natal_narrative(natal_chart, transit_chart, lang)
        reading["date"] = target_date.isoformat()
        forecasts.append(reading)
    
    return forecasts
