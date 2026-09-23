"""Fusion Full Reading Aggregator — รวมทุกอย่างเป็นคำตอบเดียว.

Endpoint: GET /v1/fusion/full/{name}?lang=th&partner=mai

Response shape:
{
  "person": {...fusion today verdict + profile},
  "compatibility": {...synastry dimensions if partner provided},
  "upcoming": {
    "best_days": [top3 windows],
    "shared_best": {...} if partner
  }
}"""

import logging
from datetime import date, timedelta, time as time_type
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.services.fusion_engine import fuse_daily, compute_fusion_profile
from src.services.chart_service import compute_chart, ChartValidationError
from src.services.synastry_scoring import compute_synastry_profile
from src.services.window_service import compute_windows

logger = logging.getLogger("astral.fusion-full")
router = APIRouter(prefix="/v1/fusion", tags=["fusion"])


class FullReadingResponse(BaseModel):
    person: dict
    compatibility: Optional[dict] = None
    upcoming: dict


@router.get("/full/{name}", response_model=FullReadingResponse)
async def fusion_full_reading(
    name: str,
    lang: str = Query("th", pattern="^(th|en)$"),
    partner: Optional[str] = Query(None, max_length=60),
    days_ahead: int = Query(7, ge=1, le=30),
):
    """Unified reading: today's fusion + partner synastry + upcoming windows."""
    from src.routers.fusion_profile import _load_profile

    try:
        prof = _load_profile(name)
        natal = {
            "name": name,
            "date": date.fromisoformat(prof["date"]),
            "time": time_type.fromisoformat(prof["time"]),
        }
        today = fuse_daily(natal, lat=prof["lat"], lon=prof["lon"],
                           tz_offset_hours=prof["tz_offset_hours"])
        from src.services.templates import render_daily_reading
        today["reading"] = render_daily_reading(today, lang=lang)

        profile = compute_fusion_profile(name, lang)

        # If partner given, compute synastry + shared best window
        compatibility = None
        shared_best = None
        if partner:
            prof_b = _load_profile(partner)
            natal_b = {
                "name": partner,
                "date": date.fromisoformat(prof_b["date"]),
                "time": time_type.fromisoformat(prof_b["time"]),
            }
            chart_a = compute_chart(name=natal["name"], date=natal["date"], time=natal["time"],
                                    tz_offset_hours=prof["tz_offset_hours"],
                                    lat=prof["lat"], lon=prof["lon"], system="tropical")
            chart_b = compute_chart(name=natal_b["name"], date=natal_b["date"], time=natal_b["time"],
                                    tz_offset_hours=prof_b["tz_offset_hours"],
                                    lat=prof_b["lat"], lon=prof_b["lon"], system="tropical")
            synastry = compute_synastry_profile(chart_a, chart_b)
            compatibility = {
                "dimensions": synastry["dimensions"],
                "overall": synastry["overall"],
                "top_bonds": synastry["top_bonds"][:3],
                "frictions": synastry["frictions"][:3],
                "karmic": synastry["karmic"]["method"],
            }
            # Shared best window in the lookahead
            windows = compute_windows(chart_a, start=date.today(), days=days_ahead)
            shared = [
                w for w in windows.get("slots", [])
                if partner in str(w.get("shared_with", "")) or w.get("shared_score", 0) > 0
            ]
            if shared:
                shared.sort(key=lambda s: -s.get("score", 0))
                shared_best = shared[0]

        # Upcoming windows for person
        chart_a = compute_chart(name=natal["name"], date=natal["date"], time=natal["time"],
                                tz_offset_hours=prof["tz_offset_hours"],
                                lat=prof["lat"], lon=prof["lon"], system="tropical")
        windows = compute_windows(chart_a, start=date.today(), days=days_ahead)
        best_days = windows.get("best", [])[:3]

        return {
            "person": {"today": today, "profile": profile},
            "compatibility": compatibility,
            "upcoming": {
                "best_days": best_days,
                "shared_best": shared_best,
            },
        }
    except HTTPException:
        raise
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid profile data: {e}") from e
    except ChartValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error("Fusion full reading failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Reading generation failed") from e
