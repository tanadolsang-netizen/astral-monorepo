"""Horary astrology: the chart is cast for the moment the question is
asked, not for the querent's birth. Reuses compute_chart() wholesale — the
only new thing is that "now" is the event time.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.services.caveat import CAVEAT
from src.services.chart_service import compute_chart, compute_dual_chart
from src.services.element_service import compute_element_balance

router = APIRouter()


class HoraryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    tz_offset_hours: float = Field(default=7.0, ge=-12, le=14)
    lat: float = Field(default=13.8591, ge=-90, le=90)
    lon: float = Field(default=100.5217, ge=-180, le=180)
    system: str = Field(default="tropical", pattern="^(tropical|sidereal)$")
    dual: bool = Field(default=False)


@router.post("/ask")
async def ask(req: HoraryRequest):
    try:
        tz = timezone(timedelta(hours=req.tz_offset_hours))
        now = datetime.now(tz)

        chart = compute_chart(
            name=req.question[:120],
            date=now.date(),
            time=now.time().replace(microsecond=0),
            tz_offset_hours=req.tz_offset_hours,
            lat=req.lat,
            lon=req.lon,
            system=req.system,
        )

        moon = next((b for b in chart["bodies"] if b["body"] == "Moon"), None)

        return {
            "question": req.question,
            "asked_at_local": now.isoformat(timespec="seconds"),
            "chart": chart,
            "ascendant": chart["ascendant"],
            "moon": moon,
            "elements": compute_element_balance(chart),
            "caveat": CAVEAT,
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Computation failed: {exc}") from exc


@router.post("/ask-dual")
async def ask_dual(req: HoraryRequest):
    try:
        tz = timezone(timedelta(hours=req.tz_offset_hours))
        now = datetime.now(tz)

        dual = compute_dual_chart(
            name=req.question[:120],
            date=now.date(),
            time=now.time().replace(microsecond=0),
            tz_offset_hours=req.tz_offset_hours,
            lat=req.lat,
            lon=req.lon,
        )

        moon_tropical = next((b for b in dual["tropical"]["bodies"] if b["body"] == "Moon"), None)
        moon_sidereal = next((b for b in dual["sidereal"]["bodies"] if b["body"] == "Moon"), None)

        return {
            "question": req.question,
            "asked_at_local": now.isoformat(timespec="seconds"),
            "tropical": {
                **dual["tropical"],
                "elements": compute_element_balance(dual["tropical"]),
                "moon": moon_tropical,
            },
            "sidereal": {
                **dual["sidereal"],
                "elements": compute_element_balance(dual["sidereal"]),
                "moon": moon_sidereal,
            },
            "caveat": CAVEAT,
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Computation failed: {exc}") from exc
