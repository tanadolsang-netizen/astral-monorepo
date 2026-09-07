"""Fusion API — one present-moment answer across all systems (TH/EN)."""

import logging
from datetime import date as date_type, time as time_type

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.services.fusion_engine import fuse_daily, DOMAINS
from src.services.templates import render_daily_reading

logger = logging.getLogger("astral.fusion")
router = APIRouter()


class FusionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    date: date_type
    time: time_type
    tz_offset_hours: float = Field(default=7.0, ge=-12, le=14)
    lat: float = Field(default=13.8591, ge=-90, le=90)
    lon: float = Field(default=100.5217, ge=-180, le=180)


@router.post("/today")
async def fusion_today(req: FusionRequest, lang: str = "th"):
    try:
        natal = {"name": req.name, "date": req.date, "time": req.time}
        result = fuse_daily(natal, lat=req.lat, lon=req.lon,
                            tz_offset_hours=req.tz_offset_hours)
        result["reading"] = render_daily_reading(result, lang=lang)
        return result
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid request data: {e}") from e
    except Exception as e:
        logger.error("Fusion today failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Fusion computation failed") from e


@router.get("/domains")
async def fusion_domains():
    return {k: v["th"] for k, v in DOMAINS.items()}
