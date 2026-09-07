"""Muhurta (electional) endpoints — เลือกวันมงคล."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.services.muhurta_service import find_windows, _ACTIONS

router = APIRouter()


class MuhurtaRequest(BaseModel):
    action: str = Field(pattern="^(marriage|business|contract|travel|moving)$")
    start_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    days: int = Field(default=60, ge=7, le=180)
    lat: float = Field(default=13.7565, ge=-90, le=90)
    lon: float = Field(default=100.5018, ge=-180, le=180)
    tz_offset_hours: float = Field(default=7.0, ge=-12, le=14)
    top_n: int = Field(default=3, ge=1, le=5)


@router.get("/actions")
def list_actions() -> dict:
    return {
        "actions": [
            {"id": k, "th": v["th"], "en": v["en"]}
            for k, v in _ACTIONS.items()
        ]
    }


@router.post("/find")
def find(req: MuhurtaRequest) -> dict:
    try:
        return find_windows(
            action=req.action,
            start_date=req.start_date,
            days=req.days,
            lat=req.lat,
            lon=req.lon,
            tz_offset_hours=req.tz_offset_hours,
            top_n=req.top_n,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
