"""Narrative API — endpoints for personalized astrology readings."""

import logging
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import date, time

from src.services.narrative_engine import (
    generate_natal_narrative,
    generate_transit_natal_narrative,
    generate_synastry_narrative,
)
from src.services.chart_service import compute_chart, ChartValidationError
from src.services.transit_narrative import generate_daily_reading, generate_weekly_forecast
from src.services.synastry_narrative import generate_synastry_reading, generate_composite_reading
from src.services.llm_client import get_llm_client

logger = logging.getLogger("astral.narrative")
router = APIRouter(prefix="/v1/narrative", tags=["narrative"])


class BirthData(BaseModel):
    name: str
    date: date
    time: time
    tz_offset_hours: float = 7.0
    lat: float = 13.8591
    lon: float = 100.5217
    system: str = "tropical"


@router.post("/natal")
async def natal_narrative(data: BirthData, lang: str = Query("th")):
    """Generate a personalized natal chart narrative."""
    try:
        chart = compute_chart(
            name=data.name,
            date=data.date,
            time=data.time,
            tz_offset_hours=data.tz_offset_hours,
            lat=data.lat,
            lon=data.lon,
            system=data.system,
        )
        return generate_natal_narrative(chart, lang)
    except ChartValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error("Natal narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.post("/transit")
async def transit_narrative(data: BirthData, lang: str = Query("th")):
    """Generate a transit-to-natal narrative."""
    try:
        natal_chart = compute_chart(
            name=data.name,
            date=data.date,
            time=data.time,
            tz_offset_hours=data.tz_offset_hours,
            lat=data.lat,
            lon=data.lon,
            system=data.system,
        )
        return generate_daily_reading(natal_chart, data.lat, data.lon, lang)
    except ChartValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error("Transit narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.post("/synastry")
async def synastry_narrative(
    a: BirthData,
    b: BirthData,
    lang: str = Query("th"),
):
    """Generate a synastry (relationship) narrative."""
    try:
        return generate_synastry_reading(
            a.name, a.date, a.time, a.tz_offset_hours, a.lat, a.lon,
            b.name, b.date, b.time, b.tz_offset_hours, b.lat, b.lon,
            lang,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error("Synastry narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.post("/composite")
async def composite_narrative(
    a: BirthData,
    b: BirthData,
    lang: str = Query("th"),
):
    """Generate a composite chart narrative."""
    try:
        return generate_composite_reading(
            a.name, a.date, a.time, a.tz_offset_hours, a.lat, a.lon,
            b.name, b.date, b.time, b.tz_offset_hours, b.lat, b.lon,
            lang,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error("Composite narrative failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Narrative generation failed") from e


@router.get("/daily/{name}")
async def daily_reading(
    name: str,
    lat: float = 13.8591,
    lon: float = 100.5217,
    lang: str = Query("th"),
):
    """Generate a daily transit reading for a stored profile."""
    from src.routers.fusion_profile import _load_profile
    try:
        prof = _load_profile(name)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail="profile not found") from e

    try:
        natal_chart = compute_chart(
            name=prof["name"],
            date=date.fromisoformat(prof["date"]),
            time=time.fromisoformat(prof["time"]),
            tz_offset_hours=prof["tz_offset_hours"],
            lat=prof["lat"],
            lon=prof["lon"],
        )
        return generate_daily_reading(natal_chart, lat, lon, lang)
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid profile data: {e}") from e
    except ChartValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error("Daily reading failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Reading generation failed") from e


@router.get("/weekly/{name}")
async def weekly_forecast(
    name: str,
    lat: float = 13.8591,
    lon: float = 100.5217,
    lang: str = Query("th"),
):
    """Generate a weekly forecast for a stored profile."""
    from src.routers.fusion_profile import _load_profile
    try:
        prof = _load_profile(name)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail="profile not found") from e

    try:
        natal_chart = compute_chart(
            name=prof["name"],
            date=date.fromisoformat(prof["date"]),
            time=time.fromisoformat(prof["time"]),
            tz_offset_hours=prof["tz_offset_hours"],
            lat=prof["lat"],
            lon=prof["lon"],
        )
        return generate_weekly_forecast(natal_chart, lat, lon, lang)
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid profile data: {e}") from e
    except ChartValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error("Weekly forecast failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Forecast generation failed") from e
