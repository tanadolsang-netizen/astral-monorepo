"""
Redis cache layer — Co-Star-style shared ephemeris state.

Co-Star's scale bottleneck: 500K transits per 3 minutes, where the SAME
transit (shared, date-based) was recomputed per-user. The fix is to split
shared ephemeris state (cache this, keyed by date+tz-group+planet) from
user-specific personalization (compute per-user, in the worker).

This module owns the shared side:
  - get_ephemeris_cached(): cache-aside lookup on compute of planetary
    positions for a given date (the expensive shared part).
  - get_transit_cached(): same for transit aspects of the day.
  - invalidate_date(): drop stale cache entries when ephemeris data is
    corrected (e.g. after an ephemeris fix deployment).

Local/dev: degrades gracefully to no-cache (returns compute() result) when
Redis is unavailable, so the backend always works without Redis.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Callable, TypeVar

logger = logging.getLogger("astral.cache")

T = TypeVar("T")

REDIS_URL = os.getenv("REDIS_URL", "")

# Cache key schema (matches Co-Star's documented pattern):
#   ephem:{date}:{tz_group}:{planet}:{calculation_type}
_KEY_PREFIX = "ephem"

# TTLs — ephemeris is deterministic for a given date, so long TTL is safe.
EPHEMERIS_TTL_SECONDS = 24 * 3600   # positions for a past/today date
TRANSIT_TTL_SECONDS = 3600          # transits of the current day

_redis_client = None
_redis_checked = False


def _get_redis():
    """Lazy singleton. Returns None (and logs once) when Redis is absent."""
    global _redis_client, _redis_checked
    if _redis_checked:
        return _redis_client
    _redis_checked = True
    if not REDIS_URL:
        logger.info("REDIS_URL not set — running without cache")
        _redis_client = None
        return None
    try:
        import redis

        _redis_client = redis.Redis.from_url(
            REDIS_URL, decode_responses=True, socket_timeout=2, socket_connect_timeout=2
        )
        _redis_client.ping()
        logger.info("Redis cache connected: %s", REDIS_URL.split("@")[-1])
    except Exception as exc:  # noqa: BLE001
        logger.warning("Redis unavailable (%s) — running without cache", exc)
        _redis_client = None
    return _redis_client


def cache_key(date: str, tz_group: str, planet: str, calc_type: str) -> str:
    """Build the shared-state cache key.

    tz_group: bucketed timezone (e.g. 'UTC+7') so users in the same offset
    share one entry. planet: 'all' or 'Moon'/'Venus'/... calc_type:
    'position' | 'transit' | 'aspects'.
    """
    return f"{_KEY_PREFIX}:{date}:{tz_group}:{planet}:{calc_type}"


def tz_group_for(tz_offset_hours: float) -> str:
    """Bucket a timezone offset to whole hours (same offset shares cache)."""
    return f"UTC{int(round(tz_offset_hours)):+d}"


# ---------------------------------------------------------------------------
# Cache-aside helpers
# ---------------------------------------------------------------------------

def get_or_compute(
    key: str,
    compute: Callable[[], T],
    ttl: int = EPHEMERIS_TTL_SECONDS,
) -> T:
    """Cache-aside: return cached value if present, else compute + store.

    Works without Redis (compute-only) so callers never branch.
    """
    r = _get_redis()
    if r is not None:
        try:
            cached = r.get(key)
            if cached is not None:
                try:
                    return json.loads(cached)
                except (json.JSONDecodeError, TypeError):
                    pass  # corrupt entry -> recompute
        except Exception as exc:  # noqa: BLE001
            logger.warning("redis get failed for %s: %s", key, exc)

    value = compute()

    if r is not None:
        try:
            r.setex(key, ttl, json.dumps(value, ensure_ascii=False, default=str))
        except Exception as exc:  # noqa: BLE001
            logger.warning("redis set failed for %s: %s", key, exc)
    return value


def get_ephemeris_cached(
    date: str,
    tz_offset_hours: float,
    planet: str,
    calc_type: str,
    compute: Callable[[], Any],
) -> Any:
    """Cached ephemeris for a shared (date, tz-group, planet, calc_type)."""
    key = cache_key(date, tz_group_for(tz_offset_hours), planet, calc_type)
    return get_or_compute(key, compute, EPHEMERIS_TTL_SECONDS)


def get_transit_cached(
    date: str,
    tz_offset_hours: float,
    compute: Callable[[], Any],
) -> Any:
    """Cached transit-of-the-day for a shared (date, tz-group)."""
    key = cache_key(date, tz_group_for(tz_offset_hours), "all", "transit")
    return get_or_compute(key, compute, TRANSIT_TTL_SECONDS)


def invalidate_date(date: str) -> int:
    """Drop all cache entries for a date (after an ephemeris correction)."""
    r = _get_redis()
    if r is None:
        return 0
    try:
        keys = list(r.scan_iter(f"{_KEY_PREFIX}:{date}:*", count=200))
        if keys:
            return r.delete(*keys)
        return 0
    except Exception as exc:  # noqa: BLE001
        logger.warning("redis invalidate failed for %s: %s", date, exc)
        return 0


def cache_stats() -> dict[str, Any]:
    """Health/debug info: connected + hit counts."""
    r = _get_redis()
    if r is None:
        return {"connected": False}
    try:
        info = r.info("stats")
        return {
            "connected": True,
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
        }
    except Exception as exc:  # noqa: BLE001
        return {"connected": False, "error": str(exc)}
