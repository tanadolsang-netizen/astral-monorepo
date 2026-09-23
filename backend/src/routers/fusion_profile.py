"""Profile Store — save a birth profile once, reuse it everywhere.

Storage: JSON file per profile under HERMES_MEMORY_ROOT/profiles/ (same root
the hermes_memory_service uses, so deployment stays single-config).
"""

import json
import logging
import os
import re
import threading
from datetime import date as date_type, time as time_type
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.services.fusion_engine import fuse_daily
from src.services.templates import render_daily_reading

logger = logging.getLogger("astral.fusion-profile")
router = APIRouter()

_LOCK = threading.Lock()


def _profiles_dir() -> Path:
    # Default lives inside the repo (.data/) — the hermes_memory_service's
    # D:\ default assumes a drive this machine doesn't have.
    root = os.getenv("HERMES_MEMORY_ROOT")
    d = (Path(root) / "profiles") if root else (Path(__file__).resolve().parents[2] / ".data" / "profiles")
    d.mkdir(parents=True, exist_ok=True)
    return d


def _slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not s:
        raise HTTPException(status_code=400, detail="name has no usable characters")
    return s[:60]


def _profile_path(name: str) -> Path:
    return _profiles_dir() / f"{_slug(name)}.json"


def _load_profile(name: str) -> dict:
    p = _profile_path(name)
    if not p.exists():
        raise HTTPException(
            status_code=404,
            detail=f"profile '{name}' not found — POST /v1/fusion/profile first",
        )
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise HTTPException(status_code=500, detail=f"corrupt profile file: {exc}")


class ProfileInput(BaseModel):
    date: date_type
    time: time_type
    tz_offset_hours: float = Field(default=7.0, ge=-12, le=14)
    lat: float = Field(default=13.8591, ge=-90, le=90)
    lon: float = Field(default=100.5217, ge=-180, le=180)


@router.put("/profile/{name}")
async def upsert_profile(name: str, profile: ProfileInput):
    """Create or update a birth profile. Idempotent."""
    try:
        data = profile.model_dump(mode="json")
        data["name"] = name
        path = _profile_path(name)
        with _LOCK:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"saved": True, "name": name}
    except HTTPException:
        raise
    except (OSError, ValueError) as e:
        logger.error("Profile save failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save profile: {e}") from e


@router.get("/profile/{name}")
async def get_profile(name: str):
    return {"name": name, **_load_profile(name)}


@router.post("/today/by-name/{name}")
async def fusion_today_by_name(name: str, lang: str = "th", payload: dict | None = None):
    """Today's fused reading using the stored profile — no birth data in the request.

    Optional JSON body: {"on": "YYYY-MM-DD"} pins a specific date instead of today.
    """
    try:
        prof = _load_profile(name)
        natal = {
            "name": name,
            "date": date_type.fromisoformat(prof["date"]),
            "time": time_type.fromisoformat(prof["time"]),
        }
        on = (payload or {}).get("on")
        now_utc = None
        if on:
            # Pin the reading to a specific local date (00:00 UTC anchor is fine:
            # fuse_daily only reads the local calendar day from this timestamp).
            from datetime import datetime as _dt, timezone as _tz
            now_utc = _dt.fromisoformat(f"{on}T04:00:00+00:00")
        result = fuse_daily(natal, lat=prof["lat"], lon=prof["lon"],
                            tz_offset_hours=prof["tz_offset_hours"], now_utc=now_utc)
        result["reading"] = render_daily_reading(result, lang=lang)
        return result
    except HTTPException:
        raise
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid profile data: {e}") from e
    except Exception as e:
        logger.error("Fusion today by name failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Fusion computation failed") from e
