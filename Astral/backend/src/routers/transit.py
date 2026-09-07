from datetime import date as date_type, time as time_type

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.services.caveat import CAVEAT
from src.services.chart_service import compute_chart, compute_dual_chart
from src.services.transit_service import compute_now, compute_dual_now
from src.services.window_service import compute_windows, find_shared_windows

router = APIRouter()


@router.get("/now")
async def transit_now(lat: float = 13.8591, lon: float = 100.5217, tz: float = 7.0):
    return {**compute_now(lat=lat, lon=lon, tz_offset_hours=tz), "caveat": CAVEAT}


@router.get("/now-dual")
async def transit_now_dual(lat: float = 13.8591, lon: float = 100.5217, tz: float = 7.0):
    return {**compute_dual_now(lat=lat, lon=lon, tz_offset_hours=tz), "caveat": CAVEAT}


class NatalInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    date: date_type
    time: time_type
    tz_offset_hours: float = Field(default=7.0, ge=-12, le=14)
    lat: float = Field(default=13.8591, ge=-90, le=90)
    lon: float = Field(default=100.5217, ge=-180, le=180)
    system: str = Field(default="tropical", pattern="^(tropical|sidereal)$")
    dual: bool = Field(default=False)


class WindowRequest(BaseModel):
    natal: NatalInput
    start: date_type
    days: int = Field(default=7, ge=1, le=31)


class SharedWindowRequest(BaseModel):
    natal_a: NatalInput
    natal_b: NatalInput
    start: date_type
    days: int = Field(default=7, ge=1, le=31)


def _chart_from(natal: NatalInput) -> dict:
    if natal.dual:
        return compute_dual_chart(
            name=natal.name,
            date=natal.date,
            time=natal.time,
            tz_offset_hours=natal.tz_offset_hours,
            lat=natal.lat,
            lon=natal.lon,
        )
    return compute_chart(
        name=natal.name,
        date=natal.date,
        time=natal.time,
        tz_offset_hours=natal.tz_offset_hours,
        lat=natal.lat,
        lon=natal.lon,
        system=natal.system,
    )


@router.post("/windows")
async def transit_windows(req: WindowRequest):
    chart = _chart_from(req.natal)
    try:
        windows = compute_windows(
            natal=chart,
            start=req.start,
            days=req.days,
            tz_offset_hours=req.natal.tz_offset_hours,
            system=req.natal.system,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"name": req.natal.name, **windows, "caveat": CAVEAT}


@router.post("/windows/shared")
async def transit_windows_shared(req: SharedWindowRequest):
    try:
        wa = compute_windows(
            natal=_chart_from(req.natal_a), start=req.start, days=req.days,
            tz_offset_hours=req.natal_a.tz_offset_hours, system=req.natal_a.system,
        )
        wb = compute_windows(
            natal=_chart_from(req.natal_b), start=req.start, days=req.days,
            tz_offset_hours=req.natal_b.tz_offset_hours, system=req.natal_b.system,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "name_a": req.natal_a.name,
        "name_b": req.natal_b.name,
        "start": req.start.isoformat(),
        "days": req.days,
        "shared": find_shared_windows(wa, wb)[:5],
        "caveat": CAVEAT,
    }
