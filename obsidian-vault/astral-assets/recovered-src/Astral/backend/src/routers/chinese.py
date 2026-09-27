"""Chinese astrology endpoints: BaZi Four Pillars, zodiac animal, Wu Xing."""

from datetime import date as _date, time as _time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.services.caveat import CAVEAT
from src.services.chinese_service import compute_bazi, get_zodiac, compute_element_analysis

router = APIRouter()


class BaZiRequest(BaseModel):
    date: str = Field(..., description="วันเกิด YYYY-MM-DD")
    time: str = Field(..., description="เวลาเกิด HH:MM:SS")


class ZodiacRequest(BaseModel):
    year: int = Field(..., ge=1900, le=2100, description="ปีเกิด (คริสต์ศักราช)")


class ElementRequest(BaseModel):
    date: str = Field(..., description="วันเกิด YYYY-MM-DD")
    time: str = Field(..., description="เวลาเกิด HH:MM:SS")


@router.post("/bazi")
async def bazi(req: BaZiRequest):
    """คำนวณดวง八字 (BaZi) — เสาหลักทั้งสี่"""
    try:
        bd = _date.fromisoformat(req.date)
        bt = _time.fromisoformat(req.time)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"รูปแบบวันเวลาไม่ถูกต้อง: {exc}") from exc

    result = compute_bazi(bd, bt)
    return {**result, "caveat": CAVEAT}


@router.post("/zodiac")
async def zodiac(req: ZodiacRequest):
    """นักษัตรจีน — สัตว์ประจำปีเกิด"""
    result = get_zodiac(req.year)
    return {**result, "caveat": CAVEAT}


@router.post("/element")
async def element(req: ElementRequest):
    """ธาตุทั้งห้า (Wu Xing) — การวิเคราะห์ธาตุในดวงชะตา"""
    try:
        bd = _date.fromisoformat(req.date)
        bt = _time.fromisoformat(req.time)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"รูปแบบวันเวลาไม่ถูกต้อง: {exc}") from exc

    result = compute_element_analysis(bd, bt)
    return {**result, "caveat": CAVEAT}
