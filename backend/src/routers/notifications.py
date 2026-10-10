"""
Notification router — persists user prefs + device tokens + delivery log.

Endpoints:
  GET  /v1/notifications/preferences
  PUT  /v1/notifications/preferences
  POST /v1/notifications/devices       (register push token)
  DELETE /v1/notifications/devices/{push_token}
  GET  /v1/notifications/devices
  POST /v1/notifications/send-daily    (manual trigger for one user)
  POST /v1/notifications/scheduler     (one scheduler tick — cron)
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from src.services.notification_service import (
    NotificationPrefs,
    get_prefs,
    list_devices,
    register_device,
    run_scheduler,
    save_prefs,
    send_daily_transit,
    unregister_device,
)

router = APIRouter()


class PreferencesIn(BaseModel):
    daily_transit: bool = True
    transit_time: str = "08:00"
    tz_offset_hours: float = 7.0
    weekly_reading: bool = True
    compatibility_alerts: bool = True
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None


class DeviceIn(BaseModel):
    platform: str  # ios | android | web
    push_token: str


def _user_id_from_auth(authorization: str) -> str:
    """Extract user_id from Bearer token.

    In production this decodes the JWT via Supabase; locally we accept any
    non-empty token and use it as the user_id so the flow is testable.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Empty token")
    return token


# ---------------------------------------------------------------------------
# Preferences
# ---------------------------------------------------------------------------

@router.get("/preferences")
async def read_preferences(authorization: str = Header(default="")) -> dict:
    user_id = _user_id_from_auth(authorization)
    prefs = get_prefs(user_id)
    return {
        "user_id": prefs.user_id,
        "daily_transit": prefs.daily_transit,
        "transit_time": prefs.transit_time,
        "tz_offset_hours": prefs.tz_offset_hours,
        "weekly_reading": prefs.weekly_reading,
        "compatibility_alerts": prefs.compatibility_alerts,
        "quiet_hours_start": prefs.quiet_hours_start,
        "quiet_hours_end": prefs.quiet_hours_end,
    }


@router.put("/preferences")
async def update_preferences(
    prefs: PreferencesIn, authorization: str = Header(default="")
) -> dict:
    user_id = _user_id_from_auth(authorization)
    saved = save_prefs(
        NotificationPrefs(
            user_id=user_id,
            daily_transit=prefs.daily_transit,
            transit_time=prefs.transit_time,
            tz_offset_hours=prefs.tz_offset_hours,
            weekly_reading=prefs.weekly_reading,
            compatibility_alerts=prefs.compatibility_alerts,
            quiet_hours_start=prefs.quiet_hours_start,
            quiet_hours_end=prefs.quiet_hours_end,
        )
    )
    return {
        "status": "saved",
        "prefs": {
            "daily_transit": saved.daily_transit,
            "transit_time": saved.transit_time,
            "tz_offset_hours": saved.tz_offset_hours,
            "weekly_reading": saved.weekly_reading,
            "compatibility_alerts": saved.compatibility_alerts,
            "quiet_hours_start": saved.quiet_hours_start,
            "quiet_hours_end": saved.quiet_hours_end,
        },
    }


# ---------------------------------------------------------------------------
# Device tokens
# ---------------------------------------------------------------------------

@router.post("/devices")
async def add_device(
    device: DeviceIn, authorization: str = Header(default="")
) -> dict:
    user_id = _user_id_from_auth(authorization)
    try:
        return register_device(user_id, device.platform, device.push_token)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/devices/{push_token}")
async def remove_device(
    push_token: str, authorization: str = Header(default="")
) -> dict:
    user_id = _user_id_from_auth(authorization)
    return unregister_device(user_id, push_token)


@router.get("/devices")
async def get_devices(authorization: str = Header(default="")) -> dict:
    user_id = _user_id_from_auth(authorization)
    return {"devices": list_devices(user_id)}


# ---------------------------------------------------------------------------
# Delivery
# ---------------------------------------------------------------------------

@router.post("/send-daily")
async def trigger_daily(authorization: str = Header(default="")) -> dict:
    user_id = _user_id_from_auth(authorization)
    return send_daily_transit(user_id, datetime.now(timezone.utc))


@router.post("/scheduler")
async def scheduler_tick() -> dict:
    """Called by cron every 5 minutes. Sends to everyone due in this window."""
    return run_scheduler(datetime.now(timezone.utc))
