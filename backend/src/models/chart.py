from pydantic import BaseModel, Field
from datetime import date, time
from typing import Optional


class ChartRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    date: date
    time: time
    tz_offset_hours: float = Field(default=7.0, ge=-12, le=14)
    lat: float = Field(default=13.8591, ge=-90, le=90)
    lon: float = Field(default=100.5217, ge=-180, le=180)
    system: str = Field(default="tropical", pattern="^(tropical|sidereal)$")
    dual: bool = Field(default=False)


class BodyPosition(BaseModel):
    body: str
    sign: str
    degree: float
    absolute_deg: float


class ChartResponse(BaseModel):
    name: str
    datetime_utc: str
    system: str
    bodies: list[BodyPosition]
    ascendant: BodyPosition
