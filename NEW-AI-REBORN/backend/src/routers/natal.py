"""Natal chart endpoints."""

import logging
from fastapi import APIRouter, Header, HTTPException

logger = logging.getLogger("astral.natal")

from src.integrations.supabase_client import get_current_user
from src.models.chart import ChartRequest
from src.services import chart_store
from src.services.caveat import CAVEAT
from src.services.chart_service import compute_chart, compute_dual_chart, ChartValidationError
from src.services.element_service import compute_element_balance

router = APIRouter()


@router.post("/compute")
async def compute_natal(req: ChartRequest, authorization: str = Header(default="")):
    try:
        chart = compute_chart(
            name=req.name,
            date=req.date,
            time=req.time,
            tz_offset_hours=req.tz_offset_hours,
            lat=req.lat,
            lon=req.lon,
            system=req.system,
        )
    except ChartValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error("Natal compute failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Chart computation failed") from e

    # Persist for the dashboard when the caller is authenticated. Computing a
    # chart must not fail because storage is down or the request is anonymous,
    # so this is strictly best-effort.
    saved = False
    if authorization:
        try:
            user = await get_current_user(authorization)
            chart_store.save_chart(
                user_id=user.id, name=req.name, date=req.date, time=req.time,
                tz_offset_hours=req.tz_offset_hours, lat=req.lat, lon=req.lon,
                system=req.system, payload=chart,
            )
            saved = True
        except (ValueError, RuntimeError, Exception):
            saved = False

    return {
        **chart,
        "elements": compute_element_balance(chart),
        "saved": saved,
        "caveat": CAVEAT,
    }


@router.post("/compute-dual")
async def compute_dual(req: ChartRequest, authorization: str | None = Header(default="")):
    try:
        chart = compute_dual_chart(
            name=req.name,
            date=req.date,
            time=req.time,
            tz_offset_hours=req.tz_offset_hours,
            lat=req.lat,
            lon=req.lon,
            house_system="placidus",
        )

        elements_tropical = compute_element_balance(chart["tropical"])
        elements_sidereal = compute_element_balance(chart["sidereal"])

        return {
            **chart,
            "elements_tropical": elements_tropical,
            "elements_sidereal": elements_sidereal,
            "caveat": CAVEAT,
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error("Natal compute-dual failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Chart computation failed") from e
