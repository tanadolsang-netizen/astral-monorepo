from datetime import date as date_type, time as time_type
from typing import Literal, Optional

from pydantic import BaseModel, Field

SpreadName = Literal["single", "three_card", "celtic_cross"]


class TarotBirthData(BaseModel):
    """Optional natal data. When supplied, the draw is weighted toward the
    elements the chart is thin in (see tarot_service._weights_for)."""

    date: date_type
    time: time_type
    tz_offset_hours: float = Field(default=7.0, ge=-12, le=14)
    lat: float = Field(default=13.8591, ge=-90, le=90)
    lon: float = Field(default=100.5217, ge=-180, le=180)
    system: str = Field(default="tropical", pattern="^(tropical|sidereal)$")


class TarotDrawRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    spread: SpreadName = Field(default="three_card")
    seed: Optional[int] = Field(
        default=None,
        description="Optional deterministic seed (e.g. derived from name+date) "
        "so the same person/day reproduces the same draw.",
    )
    birth: Optional[TarotBirthData] = Field(
        default=None,
        description="Optional birth data; enables element-weighted drawing.",
    )
    lang: Literal["th", "en"] = Field(
        default="th",
        description="Primary language for the narrative block.",
    )


class TarotCardDraw(BaseModel):
    position: str
    card: str
    arcana: Literal["major", "minor"]
    orientation: Literal["upright", "reversed"]
    meaning: str
    image_url: Optional[str] = None


class TarotDeckStatus(BaseModel):
    have: int
    total: int
    complete: bool


class TarotDrawResponse(BaseModel):
    name: str
    spread: SpreadName
    cards: list[TarotCardDraw]
    tilted_toward: Optional[str] = None
    elements: Optional[dict] = None
    caveat: str
    narrative: Optional[dict] = None
    deck: Optional[TarotDeckStatus] = None
