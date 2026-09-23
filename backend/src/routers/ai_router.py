"""AI Narrative Router — per-reading narrative + direct LLM chat."""
from __future__ import annotations

import logging
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from src.services.ai_generator import generate_full_reading
from src.services.chart_service import compute_chart, ChartValidationError
from src.services.feedback_service import feedback_service
from src.services.event_service import event_service
from src.services.user_service import user_pref_service
from src.services.llm_client import get_llm_client

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


class DirectChatRequest(BaseModel):
    system: str = ""
    message: str
    max_tokens: int = 4096
    temperature: float = 0.7


class DirectChatResponse(BaseModel):
    reply: str
    model: str


@router.post("/reading")
async def generate_reading(data: BirthData, user_id: str = "", lang: str = Query("th")):
    """Generate full narrative reading."""
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
    try:
        return feedback_service.submit_feedback(
            reading_id=data.reading_id, user_id=data.user_id,
            rating=data.rating, comment=data.comment, section=data.section,
        )
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error("Feedback submission failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Feedback submission failed") from e


@router.get("/feedback/stats")
async def feedback_stats(user_id: str = ""):
    try:
        return feedback_service.get_feedback_stats(user_id)
    except Exception as e:
        logger.error("Feedback stats failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get feedback stats") from e


@router.post("/event")
async def record_event(data: EventData):
    try:
        return event_service.record_event(
            user_id=data.user_id, event_date=data.event_date,
            category=data.category, description=data.description,
            significance=data.significance, related_transit=data.related_transit,
        )
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error("Event recording failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Event recording failed") from e


@router.get("/events/{user_id}")
async def get_events(user_id: str, category: str = ""):
    try:
        return event_service.get_events(user_id, category)
    except Exception as e:
        logger.error("Get events failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get events") from e


@router.get("/correlations/{user_id}")
async def get_correlations(user_id: str):
    try:
        return event_service.find_transit_event_correlations(user_id)
    except Exception as e:
        logger.error("Get correlations failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get correlations") from e


@router.get("/preferences/{user_id}")
async def get_preferences(user_id: str):
    try:
        return user_pref_service.get_preferences(user_id)
    except Exception as e:
        logger.error("Get preferences failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get preferences") from e


@router.post("/chat")
async def direct_chat(req: DirectChatRequest) -> DirectChatResponse:
    """Direct LLM chat via unified client."""
    try:
        client = get_llm_client()
        reply = client.chat(
            system=req.system,
            user=req.message,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
        )
        return DirectChatResponse(reply=reply, model=client.model)
    except Exception as e:
        logger.error("Direct chat failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"LLM chat failed: {e}") from e


@router.get("/health")
async def ai_health() -> dict:
    """Check LLM connectivity."""
    try:
        client = get_llm_client()
        return client.health_check()
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/health/llm")
async def llm_health() -> dict:
    """Detailed LLM health check including model info and connectivity test."""
    try:
        client = get_llm_client()
        health = client.health_check()
        return {
            "ok": health.get("ok", False),
            "model": client.model,
            "base_url": client._base_url,
            "provider": "ollama",
            "status": "online" if health.get("ok") else "offline",
            "health_details": health,
        }
    except Exception as e:
        return {
            "ok": False,
            "status": "error",
            "model": None,
            "base_url": None,
            "provider": "ollama",
            "error": str(e),
        }
