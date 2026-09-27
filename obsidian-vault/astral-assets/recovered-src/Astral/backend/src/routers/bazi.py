from datetime import date as date_type, time as time_type

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.services.bazi_service import four_pillars, yearly_relations
from src.services.caveat import CAVEAT

router = APIRouter()


class BirthInput(BaseModel):
    name: str = Field(default="", max_length=120)
    date: date_type
    time: time_type = Field(default="12:00")
    tz_offset_hours: float = Field(default=7.0, ge=-12, le=14)


class YearlyRequest(BaseModel):
    birth: BirthInput
    years: list[int] = Field(default_factory=list, min_length=1, max_length=60)


def _pillars_payload(birth: BirthInput) -> dict:
    try:
        result = four_pillars(birth.date, birth.time)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "input": {
            "name": birth.name,
            "date": birth.date.isoformat(),
            "time": birth.time.isoformat(),
            "tz_offset_hours": birth.tz_offset_hours,
        },
        **result,
        "note": (
            "เดือนแบบ fixed-date solar term (ความเชื่อมั่น MEDIUM) — "
            "เสาปี/วัน/ชั่วโมงเป็นสูตร JDN ตรง (HIGH)"
        ),
        "caveat": CAVEAT,
    }


@router.get("/pillars")
async def pillars_get(
    date: date_type = Query(..., alias="date"),
    time: time_type = Query("12:00", alias="time"),
    tz_offset_hours: float = Query(7.0, alias="tz_offset_hours", ge=-12, le=14),
    name: str = Query("", alias="name"),
):
    return _pillars_payload(BirthInput(name=name, date=date, time=time, tz_offset_hours=tz_offset_hours))


@router.post("/pillars")
async def pillars_post(birth: BirthInput):
    return _pillars_payload(birth)


@router.get("/yearly")
async def yearly_get(
    birth_date: date_type = Query(..., alias="birth_date"),
    birth_time: time_type = Query("12:00", alias="birth_time"),
    tz_offset_hours: float = Query(7.0, alias="tz_offset_hours", ge=-12, le=14),
    years: str = Query("2026,2027", alias="years", description="Comma-separated target years"),
):
    try:
        year_list = sorted({int(y) for y in years.split(",") if y.strip()})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="years must be comma-separated integers") from exc
    if not year_list:
        raise HTTPException(status_code=400, detail="at least one year required")
    return {
        **yearly_relations(birth_date, year_list),
        "caveat": CAVEAT,
    }


@router.post("/yearly")
async def yearly_post(req: YearlyRequest):
    return {
        **yearly_relations(req.birth.date, sorted(set(req.years))),
        "caveat": CAVEAT,
    }
