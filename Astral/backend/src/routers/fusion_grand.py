"""GET /v1/fusion/grand/{name} — Universe Phase 2 extended grand-fusion payload.

Query:
    lang   : th | en (default th) — selects the reading-line language
    years  : comma-separated target years for the Varshaphal/annual layers
             (default: current + next calendar year)
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from src.services.grand.grand_fusion import compute_grand_fusion

router = APIRouter(prefix="/v1/fusion", tags=["fusion-grand"])


@router.get("/grand/{name}")
async def grand_fusion(
    name: str,
    lang: str = Query("th", pattern="^(th|en)$"),
    years: str | None = Query(None, description="comma-separated years, e.g. 2026,2027"),
):
    year_list: list[int] | None = None
    if years:
        try:
            year_list = [int(y.strip()) for y in years.split(",") if y.strip()]
        except ValueError:
            year_list = None
    return compute_grand_fusion(name, lang=lang, years=year_list)
