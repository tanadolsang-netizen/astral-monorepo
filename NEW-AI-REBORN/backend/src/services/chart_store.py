"""Persistence for computed charts.

public.charts already exists in supabase/schema.sql (with RLS scoping rows
to their owner); this module is the missing read/write path to it. The
dashboard stub previously claimed no such table existed — it did.

Every function raises RuntimeError when Supabase is not configured so
callers can degrade gracefully in local dev rather than 500.
"""

from datetime import date as date_type, time as time_type

from src.integrations import supabase_client

_TABLE = "charts"


def _client():
    client = getattr(supabase_client, "_supabase", None)
    if client is None:
        raise RuntimeError("Supabase not initialized")
    return client


def save_chart(
    user_id: str,
    name: str,
    date: date_type,
    time: time_type,
    tz_offset_hours: float,
    lat: float,
    lon: float,
    system: str,
    payload: dict,
) -> dict:
    row = {
        "user_id": user_id,
        "name": name,
        "date": date.isoformat(),
        "time": time.isoformat(),
        "tz_offset_hours": tz_offset_hours,
        "lat": lat,
        "lon": lon,
        "system": system,
        "payload": payload,
    }
    res = _client().table(_TABLE).insert(row).execute()
    return (res.data or [row])[0]


def list_recent(user_id: str, limit: int = 5) -> list[dict]:
    limit = max(0, min(limit, 50))
    if limit == 0:
        return []
    res = (
        _client()
        .table(_TABLE)
        .select("id,name,date,time,system,created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data or []
