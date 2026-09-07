"""Vedic endpoints — rashi, nakshatra, sidereal chart."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.services.vedic_service import compute_vedic
from src.services.chart_service import compute_dual_chart

router = APIRouter()


class BirthData(BaseModel):
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    time: str = Field(pattern=r"^\d{2}:\d{2}$")
    lat: float = Field(default=13.7565, ge=-90, le=90)
    lon: float = Field(default=100.5018, ge=-180, le=180)
    tz_offset_hours: float = Field(default=7.0, ge=-12, le=14)


class VedicRequest(BaseModel):
    name: str = Field(default="", max_length=120)
    birth: BirthData


@router.get("/health")
def vedic_health() -> dict:
    return {"ok": True, "engine": "vedic", "ayanamsa": "Lahiri-approx"}


@router.post("/chart")
def vedic_chart(req: VedicRequest) -> dict:
    return compute_vedic(
        f"{req.birth.date}T{req.birth.time}",
        lat=req.birth.lat,
        lon=req.birth.lon,
        tz_offset_hours=req.birth.tz_offset_hours,
        person_name=req.name,
    )


@router.post("/chart-dual")
def vedic_chart_dual(req: VedicRequest) -> dict:
    vedic = compute_vedic(
        f"{req.birth.date}T{req.birth.time}",
        lat=req.birth.lat,
        lon=req.birth.lon,
        tz_offset_hours=req.birth.tz_offset_hours,
        person_name=req.name,
    )
    dual = compute_dual_chart(
        name=req.name or "Dual",
        date=req.birth.date,
        time=req.birth.time,
        tz_offset_hours=req.birth.tz_offset_hours,
        lat=req.birth.lat,
        lon=req.birth.lon,
    )
    return {
        "vedic": vedic,
        "tropical": dual["tropical"],
        "sidereal": dual["sidereal"],
        "caveat": CAVEAT,
    }
