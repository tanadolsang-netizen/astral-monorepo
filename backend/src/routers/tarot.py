from fastapi import APIRouter, HTTPException

from src.models.tarot import TarotDrawRequest, TarotDrawResponse
from src.services.caveat import CAVEAT
from src.services.chart_service import compute_chart, ChartValidationError
from src.services.element_service import compute_element_balance
from src.services.tarot_service import draw_spread
from src.services.reel_reading import reel_reading
from src.services.tarot_images import card_image_url, deck_completeness

router = APIRouter()


@router.get("/deck")
def deck_status() -> dict:
    return deck_completeness()


@router.post("/draw", response_model=TarotDrawResponse)
async def draw(req: TarotDrawRequest):
    balance = None
    if req.birth is not None:
        try:
            chart = compute_chart(
                name=req.name,
                date=req.birth.date,
                time=req.birth.time,
                tz_offset_hours=req.birth.tz_offset_hours,
                lat=req.birth.lat,
                lon=req.birth.lon,
                system=req.birth.system,
            )
            balance = compute_element_balance(chart)
        except ChartValidationError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e

    try:
        result = reel_reading(
            name=req.name,
            spread=req.spread,
            seed=req.seed,
            element_balance=balance,
        )
        result["narrative"] = {
            k: result["narrative"][k]
            for k in ([req.lang, "en", "th"] if req.lang == "th" else [req.lang, "th", "en"])
            if k in result.get("narrative", {})
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    for c in result["cards"]:
        c["image_url"] = card_image_url(c["card"])
    result["deck"] = deck_completeness()

    return {**result, "elements": balance, "caveat": CAVEAT}
