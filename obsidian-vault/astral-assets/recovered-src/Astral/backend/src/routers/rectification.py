"""Birth Time Rectification API Router.

POST /v1/rectify — infer birth time from life events.
"""

from datetime import date as date_type, time as time_type

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.services.rectification import infer_birth_time

router = APIRouter()


class LifeEvent(BaseModel):
    date: date_type
    description: str = Field(default="life event", max_length=200)


class RectifyRequest(BaseModel):
    date: date_type
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    tz_offset_hours: float = Field(..., ge=-12, le=14)
    events: list[LifeEvent] = Field(..., min_length=1)
    window_hours: float = Field(default=4.0, ge=0.5, le=12.0)
    base_time: time_type | None = Field(default=None, description="Center of search window (default 12:00)")


class RectifyCandidate(BaseModel):
    time: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


class RectifyResponse(BaseModel):
    candidates: list[RectifyCandidate]


@router.post("/rectify", response_model=RectifyResponse)
async def rectify_birth_time(req: RectifyRequest):
    """Infer the most likely birth time from known life events.
    
    Tests candidate birth times at 4-minute intervals (1° ASC per 4 min)
    within the search window around base_time (default ±4 hours from noon).
    
    Scores each candidate against provided life events using astrological triggers:
    - Saturn Return exact conjunction (orb ≤ 1°) → +30 pts
    - Jupiter transit to natal Sun/Moon/ASC/Venus (orb ≤ 2°) → +20 pts
    - Progressed Moon conjunct/opp/square natal ASC/Sun/Moon → +15 pts
    - Solar Arc directions to natal angles/planets → +10 pts
    - Lunar/Planetary transits on event dates (orb ≤ 1.5°) → +5 pts each
    
    Returns top 3 candidates sorted by confidence (normalized score).
    """
    try:
        # Convert Pydantic models to plain dicts
        events = [{"date": e.date.isoformat(), "description": e.description} for e in req.events]
        
        base_time = req.base_time
        if base_time is None:
            base_time = time_type(12, 0)
        
        candidates = infer_birth_time(
            events=events,
            date=req.date,
            lat=req.lat,
            lon=req.lon,
            tz_offset_hours=req.tz_offset_hours,
            window_hours=req.window_hours,
            base_time=base_time,
        )
        
        return {"candidates": candidates}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Rectification failed: {exc}") from exc