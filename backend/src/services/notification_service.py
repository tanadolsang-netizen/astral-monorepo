"""
Notification service — Co-Star-style daily transit push.

Persists user prefs + device tokens + delivery log in the local SQLite
cache. The scheduler walks all opted-in users in their own transit time
(after quiet-hours), generates the daily message from the real transit
engine, and records the delivery outcome.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any

from src.services.transit_service import compute_now

logger = logging.getLogger("astral.notifications")

DB_PATH = Path(__file__).resolve().parents[2] / "astral.db"

# Platform push senders (Expo push in production; noop locally)
_EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


@dataclass
class NotificationPrefs:
    user_id: str
    daily_transit: bool = True
    transit_time: str = "08:00"
    tz_offset_hours: float = 7.0
    weekly_reading: bool = True
    compatibility_alerts: bool = True
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None


def _connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise RuntimeError(f"Local cache DB not found: {DB_PATH}")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def _row_to_prefs(row: sqlite3.Row) -> NotificationPrefs:
    return NotificationPrefs(
        user_id=row["user_id"],
        daily_transit=bool(row["daily_transit"]),
        transit_time=row["transit_time"],
        tz_offset_hours=row["tz_offset_hours"],
        weekly_reading=bool(row["weekly_reading"]),
        compatibility_alerts=bool(row["compatibility_alerts"]),
        quiet_hours_start=row["quiet_hours_start"],
        quiet_hours_end=row["quiet_hours_end"],
    )


# ---------------------------------------------------------------------------
# Message composition — real transit data, not static text
# ---------------------------------------------------------------------------

_ZODIAC_TH = {
    "Aries": "เมษ", "Taurus": "พฤษภ", "Gemini": "เมถุน", "Cancer": "กรกฎ",
    "Leo": "สิงห์", "Virgo": "กันย์", "Libra": "ตุลย์", "Scorpio": "พิจิก",
    "Sagittarius": "ธนู", "Capricorn": "มังกร", "Aquarius": "กุมภ์", "Pisces": "มีน",
}

# Short, plain-Thai descriptors per body — the "mood" of the day.
_BODY_TONE_TH = {
    "Sun": "จุดเด่นของตัวคุณ",
    "Moon": "อารมณ์และความรู้สึก",
    "Mercury": "การสื่อสารและความคิด",
    "Venus": "ความรักและความสัมพันธ์",
    "Mars": "พลังและการลงมือ",
    "Jupiter": "โชคลาภและโอกาส",
    "Saturn": "บทเรียนและวินัย",
}


def _compose_daily_message(transit: dict[str, Any]) -> tuple[str, str]:
    """Turn real transit positions into a Thai push headline + body."""
    bodies = {b["body"]: b for b in transit.get("bodies", [])}
    moon = bodies.get("Moon")
    venus = bodies.get("Venus")
    mars = bodies.get("Mars")

    if moon:
        moon_sign_th = _ZODIAC_TH.get(moon["sign"], moon["sign"])
        headline = f"วันนี้พระจันทร์ทรง {moon_sign_th}"
    else:
        headline = "วันนี้ดาราเคลื่อนไหว"

    parts = []
    if venus:
        v_sign = _ZODIAC_TH.get(venus["sign"], venus["sign"])
        tone = _BODY_TONE_TH["Venus"]
        parts.append(f"ดาวศุกร์ {tone} กำลังเดินทางผ่าน {v_sign}")
    if mars:
        m_sign = _ZODIAC_TH.get(mars["sign"], mars["sign"])
        tone = _BODY_TONE_TH["Mars"]
        parts.append(f"ดาวอังคาร {tone} มาถึง {m_sign}")
    if moon:
        tone = _BODY_TONE_TH["Moon"]
        parts.append(f"พระจันทร์ส่อง {tone}ของคุณวันนี้")

    body = " • ".join(parts) if parts else "เปิดแอปเพื่ออ่านดวงวันนี้ของคุณ"
    return headline, body


# ---------------------------------------------------------------------------
# Preferences
# ---------------------------------------------------------------------------

def get_prefs(user_id: str) -> NotificationPrefs:
    con = _connect()
    row = con.execute(
        "SELECT * FROM user_notification_prefs WHERE user_id = ?", (user_id,)
    ).fetchone()
    con.close()
    if row is None:
        return NotificationPrefs(user_id=user_id)
    return _row_to_prefs(row)


def save_prefs(prefs: NotificationPrefs) -> NotificationPrefs:
    con = _connect()
    con.execute(
        """
        INSERT INTO user_notification_prefs
          (user_id, daily_transit, transit_time, tz_offset_hours,
           weekly_reading, compatibility_alerts,
           quiet_hours_start, quiet_hours_end)
        VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(user_id) DO UPDATE SET
          daily_transit = excluded.daily_transit,
          transit_time = excluded.transit_time,
          tz_offset_hours = excluded.tz_offset_hours,
          weekly_reading = excluded.weekly_reading,
          compatibility_alerts = excluded.compatibility_alerts,
          quiet_hours_start = excluded.quiet_hours_start,
          quiet_hours_end = excluded.quiet_hours_end,
          updated_at = datetime('now')
        """,
        (
            prefs.user_id,
            int(prefs.daily_transit),
            prefs.transit_time,
            float(prefs.tz_offset_hours),
            int(prefs.weekly_reading),
            int(prefs.compatibility_alerts),
            prefs.quiet_hours_start,
            prefs.quiet_hours_end,
        ),
    )
    con.commit()
    con.close()
    return get_prefs(prefs.user_id)


# ---------------------------------------------------------------------------
# Device tokens
# ---------------------------------------------------------------------------

def register_device(user_id: str, platform: str, push_token: str) -> dict[str, Any]:
    if platform not in ("ios", "android", "web"):
        raise ValueError(f"unsupported platform: {platform}")
    con = _connect()
    con.execute(
        """
        INSERT INTO push_devices (user_id, platform, push_token, enabled)
        VALUES (?,?,?,1)
        ON CONFLICT(push_token) DO UPDATE SET
          user_id = excluded.user_id,
          platform = excluded.platform,
          enabled = 1,
          last_seen = datetime('now')
        """,
        (user_id, platform, push_token),
    )
    con.commit()
    con.close()
    return {"status": "registered", "platform": platform}


def unregister_device(user_id: str, push_token: str) -> dict[str, Any]:
    con = _connect()
    cur = con.execute(
        "UPDATE push_devices SET enabled = 0 WHERE user_id = ? AND push_token = ?",
        (user_id, push_token),
    )
    con.commit()
    con.close()
    return {"status": "unregistered", "rows": cur.rowcount}


def list_devices(user_id: str) -> list[dict[str, Any]]:
    con = _connect()
    rows = con.execute(
        "SELECT platform, push_token, enabled, last_seen FROM push_devices "
        "WHERE user_id = ? ORDER BY id",
        (user_id,),
    ).fetchall()
    con.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Scheduling helpers
# ---------------------------------------------------------------------------

def _parse_hhmm(value: str) -> time:
    try:
        hh, mm = value.split(":", 1)
        return time(hour=int(hh), minute=int(mm))
    except (ValueError, AttributeError):
        return time(hour=8, minute=0)


def in_quiet_hours(prefs: NotificationPrefs, now_utc: datetime) -> bool:
    """True when `now_utc` (as local time via tz offset) falls inside quiet hours."""
    if not prefs.quiet_hours_start or not prefs.quiet_hours_end:
        return False
    local = now_utc + timedelta(hours=prefs.tz_offset_hours)
    start = _parse_hhmm(prefs.quiet_hours_start)
    end = _parse_hhmm(prefs.quiet_hours_end)
    if start <= end:
        return start <= local.time() < end
    # wraps midnight (e.g. 22:00 -> 06:00)
    return local.time() >= start or local.time() < end


def users_due_now(now_utc: datetime) -> list[NotificationPrefs]:
    """Users whose local time matches their transit_time window (5-min slot)."""
    con = _connect()
    rows = con.execute(
        "SELECT * FROM user_notification_prefs WHERE daily_transit = 1"
    ).fetchall()
    con.close()
    due: list[NotificationPrefs] = []
    for row in rows:
        prefs = _row_to_prefs(row)
        if in_quiet_hours(prefs, now_utc):
            continue
        local = now_utc + timedelta(hours=prefs.tz_offset_hours)
        t = _parse_hhmm(prefs.transit_time)
        delta = (local.time().hour * 60 + local.time().minute) - (t.hour * 60 + t.minute)
        if 0 <= delta <= 5:
            due.append(prefs)
    return due


def already_sent_today(user_id: str, kind: str, now_utc: datetime) -> bool:
    """True once a notification for this user+kind has been created today.

    'pending' counts as sent: the message was composed (and the user may
    have no device yet) — re-running would re-spam the log without value.
    """
    con = _connect()
    row = con.execute(
        """
        SELECT 1 FROM notification_log
        WHERE user_id = ? AND kind = ?
          AND delivery_status IN ('sent', 'delivered', 'pending')
          AND date(created_at) = date(?)
        LIMIT 1
        """,
        (user_id, kind, now_utc.isoformat(sep=" ")),
    ).fetchone()
    con.close()
    return row is not None


# ---------------------------------------------------------------------------
# Delivery
# ---------------------------------------------------------------------------

def _send_push(tokens: list[str], title: str, body: str, payload: dict) -> dict[str, Any]:
    """Send via Expo push service. Returns per-ticket status.

    Local/dev (no tokens) degrades to a logged noop so the scheduler stays
    testable without network calls.
    """
    if not tokens:
        return {"status": "skipped", "reason": "no_devices"}

    import httpx

    messages = [
        {"to": tok, "title": title, "body": body, "data": payload, "sound": "default"}
        for tok in tokens
    ]
    try:
        resp = httpx.post(_EXPO_PUSH_URL, json=messages, timeout=15)
        resp.raise_for_status()
        return {"status": "sent", "response": resp.json()}
    except Exception as exc:  # noqa: BLE001 - record and continue
        logger.warning("push send failed: %s", exc)
        return {"status": "failed", "error": str(exc)}


def _log_delivery(
    con: sqlite3.Connection,
    *,
    user_id: str,
    kind: str,
    title: str,
    body: str,
    payload: dict,
    status: str,
    error: str | None = None,
) -> None:
    con.execute(
        """
        INSERT INTO notification_log
          (user_id, kind, title, body, payload, sent_at, delivery_status, error_message)
        VALUES (?,?,?,?,?,datetime('now'),?,?)
        """,
        (user_id, kind, title, body, json.dumps(payload, ensure_ascii=False), status, error),
    )


def send_daily_transit(
    user_id: str,
    now_utc: datetime | None = None,
    content_override: tuple[str, str, dict] | None = None,
) -> dict[str, Any]:
    """Generate today's transit message and deliver to the user's devices.

    content_override: optional (headline, body, payload) tuple. When provided
    (by content_engine.generate_for_scheduler), skips the built-in
    _compose_daily_message and uses the snippet-library assembled reading
    instead. payload carries triggers/snippet_ids/engines_used for analytics.
    """
    now_utc = now_utc or datetime.now(timezone.utc)
    prefs = get_prefs(user_id)
    if not prefs.daily_transit:
        return {"status": "skipped", "reason": "daily_transit_off"}
    if in_quiet_hours(prefs, now_utc):
        return {"status": "skipped", "reason": "quiet_hours"}
    if already_sent_today(user_id, "daily_transit", now_utc):
        return {"status": "skipped", "reason": "already_sent"}

    if content_override is not None:
        headline, body, payload = content_override
    else:
        # 1. compute the real transit of the day (engine, not static text).
        #    Bangkok default — every user has a lat/lon in profiles; fall back safely.
        try:
            transit = compute_now(lat=13.8591, lon=100.5217, tz_offset_hours=prefs.tz_offset_hours)
        except Exception as exc:  # noqa: BLE001
            logger.error("transit compute failed for %s: %s", user_id, exc)
            return {"status": "failed", "reason": "transit_engine_error", "error": str(exc)}

        headline, body = _compose_daily_message(transit)
        payload = transit

    # 2. collect enabled device tokens
    con = _connect()
    tokens = [
        r["push_token"]
        for r in con.execute(
            "SELECT push_token FROM push_devices WHERE user_id = ? AND enabled = 1",
            (user_id,),
        ).fetchall()
    ]

    # 3. deliver
    push_result = _send_push(tokens, headline, body, payload)

    # 4. log the outcome (always, even when no devices -> 'skipped')
    status_map = {"sent": "sent", "skipped": "pending", "failed": "failed"}
    _log_delivery(
        con,
        user_id=user_id,
        kind="daily_transit",
        title=headline,
        body=body,
        payload=payload,
        status=status_map.get(push_result["status"], "failed"),
        error=push_result.get("error"),
    )
    con.commit()
    con.close()
    return {"status": push_result["status"], "headline": headline}


def run_scheduler(now_utc: datetime | None = None) -> dict[str, Any]:
    """One scheduler tick: send to everyone due in this 5-minute window."""
    now_utc = now_utc or datetime.now(timezone.utc)
    due = users_due_now(now_utc)
    results = []
    for prefs in due:
        results.append({"user_id": prefs.user_id, **send_daily_transit(prefs.user_id, now_utc)})
    logger.info("scheduler tick: %d due, %d sent", len(due),
                sum(1 for r in results if r.get("status") == "sent"))
    return {"checked": len(due), "results": results}
