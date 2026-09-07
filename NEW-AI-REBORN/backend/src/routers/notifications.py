from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()


class Preferences(BaseModel):
    daily_transit: bool = True
    transit_time: str = "08:00"
    tz_offset_hours: float = 7.0


@router.post("/preferences")
async def set_preferences(prefs: Preferences):
    return {"status": "saved", "prefs": prefs.model_dump()}


@router.get("/preferences")
async def get_preferences():
    return {"daily_transit": True, "transit_time": "08:00", "tz_offset_hours": 7.0}
