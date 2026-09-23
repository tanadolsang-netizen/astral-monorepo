"""Vedic astrology endpoints: chart computation and dasha periods."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.services.caveat import CAVEAT
from src.services.vedic_service import compute_vedic_chart, compute_dasha_periods

router = APIRouter()


class VedicChartRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    date: str = Field(..., description="Birth date YYYY-MM-DD")
    time: str = Field(..., description="Birth time HH:MM:SS")
    tz_offset_hours: float = Field(default=7.0, ge=-12, le=14)
    lat: float = Field(default=13.8591, ge=-90, le=90)
    lon: float = Field(default=100.5217, ge=-180, le=180)
    ayanamsa: str = Field(default="lahiri", pattern="^(lahiri|raman|fagan_bradley|krishnamurti)$")


class DashaRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    date: str = Field(..., description="Birth date YYYY-MM-DD")
    time: str = Field(..., description="Birth time HH:MM:SS")
    tz_offset_hours: float = Field(default=7.0, ge=-12, le=14)
    lat: float = Field(default=13.8591, ge=-90, le=90)
    lon: float = Field(default=100.5217, ge=-180, le=180)
    ayanamsa: str = Field(default="lahiri", pattern="^(lahiri|raman|fagan_bradley|krishnamurti)$")


@router.post("/chart")
async def vedic_chart(req: VedicChartRequest):
    from datetime import date as date_type, time as time_type

    try:
        birth_date = date_type.fromisoformat(req.date)
        birth_time = time_type.fromisoformat(req.time)

        result = compute_vedic_chart(
            name=req.name,
            birth_date=birth_date,
            birth_time=birth_time,
            tz_offset_hours=req.tz_offset_hours,
            lat=req.lat,
            lon=req.lon,
            ayanamsa=req.ayanamsa,
        )
        return {**result, "caveat": CAVEAT}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid date/time format: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Computation failed: {exc}") from exc


@router.post("/chart-dual")
async def vedic_chart_dual(req: VedicChartRequest):
    from datetime import date as date_type, time as time_type

    try:
        birth_date = date_type.fromisoformat(req.date)
        birth_time = time_type.fromisoformat(req.time)

        lahiri = compute_vedic_chart(
            name=req.name,
            birth_date=birth_date,
            birth_time=birth_time,
            tz_offset_hours=req.tz_offset_hours,
            lat=req.lat,
            lon=req.lon,
            ayanamsa="lahiri",
        )
        krishnamurti = compute_vedic_chart(
            name=req.name,
            birth_date=birth_date,
            birth_time=birth_time,
            tz_offset_hours=req.tz_offset_hours,
            lat=req.lat,
            lon=req.lon,
            ayanamsa="krishnamurti",
        )
        return {**lahiri, "krishnamurti": krishnamurti, "caveat": CAVEAT}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid date/time format: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Computation failed: {exc}") from exc


@router.post("/dasha")
async def dasha_periods(req: DashaRequest):
    from datetime import date as date_type, time as time_type

    try:
        birth_date = date_type.fromisoformat(req.date)
        birth_time = time_type.fromisoformat(req.time)

        result = compute_dasha_periods(
            name=req.name,
            birth_date=birth_date,
            birth_time=birth_time,
            tz_offset_hours=req.tz_offset_hours,
            lat=req.lat,
            lon=req.lon,
            ayanamsa=req.ayanamsa,
        )
        return {**result, "caveat": CAVEAT}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid date/time format: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Computation failed: {exc}") from exc
