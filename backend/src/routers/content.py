"""
Content router — Co-Star-style home feed + worker batch control.

Endpoints:
  GET  /v1/content/daily      — today's reading for the caller (home screen)
  POST /v1/content/refresh    — regenerate (respects daily dedup)
  GET  /v1/content/stats      — cache + batch stats (ops/debug)
  POST /v1/worker/daily       — one daily batch tick (cron)
  POST /v1/worker/backfill    — catch up missed users (ops)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from src.integrations.supabase_client import get_current_user, User
from src.services.content_engine import generate_daily
from src.services.notification_service import (
    already_sent_today,
    get_prefs,
)

logger = logging.getLogger("astral.content_router")

router = APIRouter()


async def _user_id_from_auth(
    authorization: str = Header(default=""),
) -> str:
    """Resolve the authenticated user id from a Bearer token.

    Uses the shared Supabase auth (single source of truth) — no longer
    treats the raw token as the user_id.
    """
    try:
        user: User = await get_current_user(authorization)
        return user.id
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=401, detail="Unauthorized") from exc


# ---------------------------------------------------------------------------
# Home feed
# ---------------------------------------------------------------------------


@router.get("/daily")
async def get_daily(authorization: str = Header(default="")) -> dict[str, Any]:
    """Today's reading — what Co-Star shows when you open the app.

    Runs the full pipeline (transit -> triggers -> snippet assembly ->
    behavior weighting -> mood modulation) but WITHOUT sending a push.
    Returns the reading + metadata (which engines fired, mood, triggers).
    """
    user_id = await _user_id_from_auth(authorization)
    prefs = get_prefs(user_id)
    content = generate_daily(
        user_id=user_id,
        tz_offset_hours=prefs.tz_offset_hours,
    )
    return {
        "user_id": user_id,
        "reading": content.to_dict(),
        "already_delivered": already_sent_today(
            user_id, "daily_transit", datetime.now(timezone.utc)
        ),
    }


@router.post("/refresh")
async def refresh_daily(authorization: str = Header(default="")) -> dict[str, Any]:
    """Regenerate today's reading (user pulled to refresh).

    Co-Star regenerates on pull-to-refresh; we do the same but keep the
    daily dedup for PUSH delivery (the feed can change, the push can't).
    """
    user_id = await _user_id_from_auth(authorization)
    prefs = get_prefs(user_id)
    content = generate_daily(
        user_id=user_id,
        tz_offset_hours=prefs.tz_offset_hours,
    )
    return {"user_id": user_id, "reading": content.to_dict()}


@router.get("/stats")
async def content_stats() -> dict[str, Any]:
    """Ops endpoint — cache health + snippet library stats."""
    from src.services.cache_service import cache_stats
    from src.services.snippet_library import library_stats

    return {
        "cache": cache_stats(),
        "snippets": library_stats(),
    }


# ---------------------------------------------------------------------------
# Worker batch control (cron / ops)
# ---------------------------------------------------------------------------


class BatchParams(BaseModel):
    warm_first: bool = True


@router.post("/worker/daily")
async def worker_daily(params: BatchParams | None = None) -> dict[str, Any]:
    """One daily batch tick — the cron entry point.

    Phase A: warm shared ephemeris (per tz-group, cached in Redis)
    Phase C: per-user personalization + push delivery
    """
    from src.services.worker_batch import run_daily_batch

    warm = params.warm_first if params else True
    return run_daily_batch(datetime.now(timezone.utc), warm_first=warm)


@router.post("/worker/backfill")
async def worker_backfill(max_users: int = 1000) -> dict[str, Any]:
    """Catch-up send for users who missed their slot (downtime recovery)."""
    from src.services.worker_batch import backfill_missed

    return backfill_missed(datetime.now(timezone.utc), max_users=max_users)
