"""AI Narrative Router — สร้าง narrative ต่อบุคคลจริง + feedback + events."""

import logging
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.services.ai_generator import generate_full_reading
from src.services.chart_service import compute_chart, ChartValidationError
from src.services.feedback_service import feedback_service
from src.services.event_service import event_service
from src.services.user_service import user_pref_service

logger = logging.getLogger("astral.ai-router")
router = APIRouter(prefix="/v1/ai", tags=["ai-narrative"])


class BirthData(BaseModel):
    name: str
    date: str
    time: str
    tz_offset_hours: float = 7.0
    lat: float = 13.8591
    lon: float = 100.5217
    system: str = "tropical"


class FeedbackData(BaseModel):
    reading_id: str
    user_id: str
    rating: int
    comment: str = ""
    section: str = ""


class EventData(BaseModel):
    user_id: str
    event_date: str
    category: str
    description: str
    significance: int = 3
    related_transit: str = ""


@router.post("/reading")
async def generate_reading(data: BirthData, user_id: str = "", lang: str = Query("th")):
    """สร้าง narrative เต็มรูปแบบต่อบุคคล"""
    try:
        chart = compute_chart(
            name=data.name, date=data.date, time=data.time,
            tz_offset_hours=data.tz_offset_hours, lat=data.lat, lon=data.lon,
            system=data.system,
        )
        reading = generate_full_reading(chart, user_id, lang)
        return reading
    except ChartValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error("AI reading generation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Reading generation failed") from e


@router.post("/feedback")
async def submit_feedback(data: FeedbackData):
    """บันทึก feedback"""
    try:
        return feedback_service.submit_feedback(
            reading_id=data.reading_id,
            user_id=data.user_id,
            rating=data.rating,
            comment=data.comment,
            section=data.section,
        )
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error("Feedback submission failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Feedback submission failed") from e


@router.get("/feedback/stats")
async def feedback_stats(user_id: str = ""):
    """ดูสถิติ feedback"""
    try:
        return feedback_service.get_feedback_stats(user_id)
    except Exception as e:
        logger.error("Feedback stats failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get feedback stats") from e


@router.post("/event")
async def record_event(data: EventData):
    """บันทึกเหตุการณ์ชีวิต"""
    try:
        return event_service.record_event(
            user_id=data.user_id,
            event_date=data.event_date,
            category=data.category,
            description=data.description,
            significance=data.significance,
            related_transit=data.related_transit,
        )
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error("Event recording failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Event recording failed") from e


@router.get("/events/{user_id}")
async def get_events(user_id: str, category: str = ""):
    """ดูเหตุการณ์ทั้งหมด"""
    try:
        return event_service.get_events(user_id, category)
    except Exception as e:
        logger.error("Get events failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get events") from e


@router.get("/correlations/{user_id}")
async def get_correlations(user_id: str):
    """หาความสัมพันธ์ระหว่าง transit กับเหตุการณ์"""
    try:
        return event_service.find_transit_event_correlations(user_id)
    except Exception as e:
        logger.error("Get correlations failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get correlations") from e


@router.get("/preferences/{user_id}")
async def get_preferences(user_id: str):
    """ดู preferences"""
    try:
        return user_pref_service.get_preferences(user_id)
    except Exception as e:
        logger.error("Get preferences failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get preferences") from e
