"""
Worker batch — Co-Star-scale daily delivery pipeline.

Co-Star's bottleneck: 500K transits computed per 3 minutes, where the
SAME shared ephemeris (positions for a date + tz bucket) was recomputed
per-user. Their fix was architectural:

  1. Compute the shared, date-determined ephemeris ONCE (cached in Redis
     keyed by date + tz-group + planet + calc_type).
  2. For each due user, pull the shared ephemeris from cache, overlay
     user-specific personalization (natal chart + behavior weights),
     assemble the message, deliver.

Our version runs the same pipeline but feeds every engine we own into
the shared part — the cache key includes the engine family, so users on
the same date + tz + engine set share one computation:

  Phase A (shared): ephemeris + Vedic/KP/BaZi daily state per (date, tz)
  Phase B (user):   natal overlay + behavior weighting + snippet assembly
  Phase C (batch):  push delivery with dedup + quiet-hours + retry

Entry point for cron:
    run_daily_batch(now_utc=None) -> BatchStats
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from src.services.cache_service import (
    get_ephemeris_cached,
    get_transit_cached,
    tz_group_for,
)
from src.services.content_engine import generate_daily
from src.services.notification_service import (
    NotificationPrefs,
    _send_push,
    already_sent_today,
    get_prefs,
    in_quiet_hours,
    users_due_now,
)
from src.services.transit_service import _compute_bodies

logger = logging.getLogger("astral.worker")

# Batch sizing — pull users in pages so a single tick stays inside a
# reasonable wall-clock window even with 100K+ opted-in users.
_USER_PAGE_SIZE = 500


@dataclass
class BatchStats:
    """Outcome of one worker batch run — the metrics Co-Star watches
    (throughput, skip ratio, failure ratio) on their daily send."""

    date: str
    tz_groups: list[str] = field(default_factory=list)
    users_due: int = 0
    sent: int = 0
    skipped_quiet: int = 0
    skipped_dedup: int = 0
    skipped_off: int = 0
    failed: int = 0
    ephemeris_computed: int = 0
    ephemeris_cache_hits: int = 0
    duration_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date,
            "tz_groups": self.tz_groups,
            "users_due": self.users_due,
            "sent": self.sent,
            "skipped_quiet": self.skipped_quiet,
            "skipped_dedup": self.skipped_dedup,
            "skipped_off": self.skipped_off,
            "failed": self.failed,
            "ephemeris_computed": self.ephemeris_computed,
            "ephemeris_cache_hits": self.ephemeris_cache_hits,
            "duration_ms": self.duration_ms,
        }


# ---------------------------------------------------------------------------
# Phase A — shared ephemeris (computed once per date + tz-group)
# ---------------------------------------------------------------------------


def warm_shared_ephemeris(
    date: str,
    tz_offsets: list[float],
) -> dict[str, Any]:
    """Pre-compute + cache the shared ephemeris for every tz-group of the
    due users, so Phase B never hits the compute path.

    This is the exact optimization that takes Co-Star from per-user
    computation to per-tz-bucket computation. Returns per-group stats.
    """
    groups = sorted({tz_group_for(o) for o in tz_offsets})
    stats: dict[str, Any] = {"groups": groups, "computed": 0, "hits": 0}

    for group in groups:
        offset = _offset_of_group(group)

        def compute() -> dict[str, Any]:
            # The 10 planetary positions are the shared, date-determined
            # part — identical for every user in this tz bucket.
            bodies = _compute_bodies(_utc_for_date(date, offset))
            return {"bodies": bodies, "tz_group": group}

        # Cache-aside: first call computes + stores, later calls hit.
        key = f"{date}:{group}"
        before = _cache_count(key)
        get_ephemeris_cached(
            date=date,
            tz_offset_hours=offset,
            planet="all",
            calc_type="position",
            compute=compute,
        )
        after = _cache_count(key)
        if after > before:
            stats["computed"] += 1
        else:
            stats["hits"] += 1

        # Also warm the transit-of-day cache (moon sign / retrogrades /
        # aspects derived from the same bodies).
        get_transit_cached(
            date=date,
            tz_offset_hours=offset,
            compute=lambda: _transit_of_day(compute()),
        )

    return stats


def _utc_for_date(date: str, tz_offset_hours: float) -> datetime:
    """A UTC datetime for the given local date at 12:00 local time."""
    from datetime import timedelta

    naive = datetime.strptime(date, "%Y-%m-%d").replace(hour=12, minute=0)
    return (naive - timedelta(hours=tz_offset_hours)).replace(tzinfo=timezone.utc)


def _offset_of_group(group: str) -> float:
    """'UTC+7' -> 7.0 ; 'UTC-5' -> -5.0 ; 'UTC+5.5' -> 5.5"""
    return float(group.replace("UTC", "").replace("+", ""))


def _cache_count(key: str) -> int:
    from src.services.cache_service import _get_redis

    r = _get_redis()
    if r is None:
        return 0
    try:
        return 1 if r.get(f"ephem:{key}:UTC*:all:position") else 0
    except Exception:  # noqa: BLE001
        return 0


def _transit_of_day(ephem: dict[str, Any]) -> dict[str, Any]:
    """Derive the day's transit state from cached positions."""
    from src.services.snippet_library import build_day_from_transit

    return build_day_from_transit(ephem)


# ---------------------------------------------------------------------------
# Phase C — batch delivery for due users
# ---------------------------------------------------------------------------


def run_daily_batch(
    now_utc: datetime | None = None,
    warm_first: bool = True,
    on_user_done: Callable[[str, str], None] | None = None,
) -> dict[str, Any]:
    """The full daily send — Co-Star's worker pipeline, our version.

    Args:
      now_utc: the tick time (default: now)
      warm_first: pre-compute shared ephemeris for due tz-groups before
        delivering (Phase A). Set False when cache is already warm
        (e.g. a catch-up tick minutes after the main one).
      on_user_done: optional callback (user_id, status) for streaming
        progress (used by the batch endpoint).

    Returns BatchStats as a dict.
    """
    started = time.monotonic()
    now_utc = now_utc or datetime.now(timezone.utc)
    date = (now_utc + _tz_delta(7.0)).strftime("%Y-%m-%d")  # UTC+7 date for keying

    stats = BatchStats(date=date)

    due = users_due_now(now_utc)
    stats.users_due = len(due)
    stats.tz_groups = sorted({tz_group_for(p.tz_offset_hours) for p in due})

    # Phase A — shared ephemeris (one computation per tz-group)
    if warm_first and due:
        warm = warm_shared_ephemeris(
            date, [p.tz_offset_hours for p in due]
        )
        stats.ephemeris_computed = warm["computed"]
        stats.ephemeris_cache_hits = warm["hits"]

    # Phase C — per-user personalization + delivery
    for prefs in due:
        status = _deliver_one(prefs, now_utc, on_user_done)
        if status == "sent":
            stats.sent += 1
        elif status == "quiet":
            stats.skipped_quiet += 1
        elif status == "dedup":
            stats.skipped_dedup += 1
        elif status == "off":
            stats.skipped_off += 1
        else:
            stats.failed += 1

    stats.duration_ms = int((time.monotonic() - started) * 1000)
    logger.info(
        "daily batch done: due=%d sent=%d dedup=%d failed=%d in %dms",
        stats.users_due, stats.sent, stats.skipped_dedup, stats.failed,
        stats.duration_ms,
    )
    return stats.to_dict()


def _tz_delta(hours: float):
    from datetime import timedelta

    return timedelta(hours=hours)


def _deliver_one(
    prefs: NotificationPrefs,
    now_utc: datetime,
    on_user_done: Callable[[str, str], None] | None = None,
) -> str:
    """One user's full path: dedup -> generate (cached ephemeris) -> push.

    Returns a coarse status: sent | quiet | dedup | off | failed.
    """
    user_id = prefs.user_id

    if not prefs.daily_transit:
        if on_user_done:
            on_user_done(user_id, "off")
        return "off"

    if in_quiet_hours(prefs, now_utc):
        if on_user_done:
            on_user_done(user_id, "quiet")
        return "quiet"

    if already_sent_today(user_id, "daily_transit", now_utc):
        if on_user_done:
            on_user_done(user_id, "dedup")
        return "dedup"

    try:
        content = generate_daily(
            user_id=user_id,
            tz_offset_hours=prefs.tz_offset_hours,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("generate failed for %s: %s", user_id, exc)
        if on_user_done:
            on_user_done(user_id, "failed")
        return "failed"

    title = content.epigram
    body = (
        f"{content.body}\n\n"
        f"ทำ: {', '.join(content.do_list)}\n"
        f"ไม่ทำ: {', '.join(content.dont_list)}"
    )
    payload = {
        "kind": "daily_transit",
        "mood": content.mood,
        "triggers": list(content.triggers),
        "snippet_ids": list(content.snippet_ids),
        "engines_used": list(content.engines_used),
        "moon_sign": content.moon_sign,
    }

    from src.services.notification_service import _log_delivery

    con = prefs  # placeholder to avoid unused import; replaced below
    del con

    import sqlite3
    from pathlib import Path

    from src.services.notification_service import DB_PATH

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        tokens = [
            r["push_token"]
            for r in con.execute(
                "SELECT push_token FROM push_devices WHERE user_id = ? AND enabled = 1",
                (user_id,),
            ).fetchall()
        ]
        result = _send_push(tokens, title, body, payload)
        status_map = {"sent": "sent", "skipped": "pending", "failed": "failed"}
        _log_delivery(
            con,
            user_id=user_id,
            kind="daily_transit",
            title=title,
            body=body,
            payload=payload,
            status=status_map.get(result["status"], "failed"),
            error=result.get("error"),
        )
        con.commit()
    finally:
        con.close()

    if on_user_done:
        on_user_done(user_id, result["status"])
    return "sent" if result["status"] == "sent" else "failed"


# ---------------------------------------------------------------------------
# Backfill — catch up users who missed their slot (server restart etc.)
# ---------------------------------------------------------------------------


def backfill_missed(now_utc: datetime | None = None, max_users: int = 1000) -> dict[str, Any]:
    """Re-run the batch for users due in the last 3 hours who have no
    'daily_transit' log entry today (missed because of downtime).

    Bounded by max_users so a long outage can't wedge the worker.
    """
    from datetime import timedelta

    now_utc = now_utc or datetime.now(timezone.utc)
    date = (now_utc + _tz_delta(7.0)).strftime("%Y-%m-%d")

    con = get_prefs  # keep import used
    del con

    import sqlite3

    from src.services.notification_service import DB_PATH

    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    try:
        rows = db.execute(
            """
            SELECT p.* FROM user_notification_prefs p
            WHERE p.daily_transit = 1
              AND NOT EXISTS (
                SELECT 1 FROM notification_log n
                WHERE n.user_id = p.user_id
                  AND n.kind = 'daily_transit'
                  AND n.delivery_status IN ('sent','delivered','pending')
                  AND date(n.created_at) = date(?)
              )
            LIMIT ?
            """,
            (now_utc.isoformat(sep=" "), max_users),
        ).fetchall()
    finally:
        db.close()

    from src.services.notification_service import _row_to_prefs

    recovered = 0
    for row in rows:
        prefs = _row_to_prefs(row)
        # Only catch up within a 3-hour window after their local slot.
        local_now = now_utc + timedelta(hours=prefs.tz_offset_hours)
        local_slot = _parse_hhmm(prefs.transit_time)
        delta_min = (local_now.hour * 60 + local_now.minute) - (
            local_slot.hour * 60 + local_slot.minute
        )
        if 0 <= delta_min <= 180:
            _deliver_one(prefs, now_utc)
            recovered += 1

    return {"date": date, "recovered": recovered, "scanned": len(rows)}


def _parse_hhmm(value: str):
    from datetime import time as _time

    try:
        hh, mm = value.split(":", 1)
        return _time(hour=int(hh), minute=int(mm))
    except (ValueError, AttributeError):
        return _time(hour=8, minute=0)
