"""Sky view endpoints — planetarium data."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from src.services.sky_view import sky_view

router = APIRouter()


class SkyIn(BaseModel):
    date_iso: str = "2026-09-01"
    time_hhmm: str = "21:00"
    tz_offset_hours: float = 7.0
    lat: float = 13.7563
    lon_deg: float = 100.5018
    include_stars: bool = True
    mag_limit: float = 2.5


@router.post("/view")
def sky_view_ep(r: SkyIn) -> dict:
    return sky_view(r.date_iso, r.time_hhmm, r.tz_offset_hours,
                    r.lat, r.lon_deg, r.include_stars, r.mag_limit)


class LifeIn(BaseModel):
    natal_name: str = "user"
    birth_date: str
    birth_time: str
    tz_offset_hours: float = 7.0
    lat: float = 13.7563
    lon_deg: float = 100.5018


@router.post("/life")
def life_tracking_ep(r: LifeIn) -> dict:
    from src.services.life_tracking import life_tracking_payload
    return life_tracking_payload(r.natal_name, r.birth_date,
                                 r.birth_time, r.tz_offset_hours,
                                 r.lat, r.lon_deg)
