"""
Tests for worker batch + content router — Co-Star-scale infrastructure.

Covered:
  - Phase A: shared ephemeris warming (per tz-group)
  - Phase C: per-user delivery with dedup + quiet hours
  - Backfill: catch-up after downtime
  - BatchStats accounting
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from src.services.notification_service import (
    NotificationPrefs,
    get_prefs,
    register_device,
    save_prefs,
    unregister_device,
    DB_PATH,
)
from src.services.worker_batch import (
    BatchStats,
    _deliver_one,
    _offset_of_group,
    _parse_hhmm,
    _transit_of_day,
    _utc_for_date,
    backfill_missed,
    run_daily_batch,
    warm_shared_ephemeris,
)
from src.services.cache_service import tz_group_for


@pytest.fixture()
def clean_users():
    """Ensure a clean slate for worker test users."""
    import sqlite3

    def _clean():
        con = sqlite3.connect(DB_PATH)
        for uid in ("wtest_a", "wtest_b", "wtest_c"):
            con.execute("DELETE FROM user_notification_prefs WHERE user_id = ?", (uid,))
            con.execute("DELETE FROM push_devices WHERE user_id = ?", (uid,))
            con.execute("DELETE FROM notification_log WHERE user_id = ?", (uid,))
        con.commit()
        con.close()

    _clean()
    yield
    _clean()


def _slot_now(tz_offset: float = 7.0) -> str:
    """Current local HH:MM for the given tz offset — makes a user 'due'."""
    local = datetime.now(timezone.utc) + timedelta(hours=tz_offset)
    return f"{local.hour:02d}:{local.minute:02d}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def test_offset_of_group():
    assert _offset_of_group("UTC+7") == 7.0
    assert _offset_of_group("UTC-5") == -5.0


def test_parse_hhmm_default():
    assert _parse_hhmm("08:30").hour == 8
    assert _parse_hhmm("garbage").hour == 8  # fallback


def test_utc_for_date_is_tz_aware():
    dt = _utc_for_date("2026-10-10", 7.0)
    assert dt.tzinfo is not None  # skyfield needs tz-aware


def test_tz_group_for_bucketing():
    assert tz_group_for(7.0) == "UTC+7"
    assert tz_group_for(-5.0) == "UTC-5"


# ---------------------------------------------------------------------------
# Phase A — shared ephemeris warming
# ---------------------------------------------------------------------------


def test_warm_shared_ephemeris_single_group():
    stats = warm_shared_ephemeris("2026-10-10", [7.0, 7.0, 7.0])
    assert stats["groups"] == ["UTC+7"]  # deduped


def test_warm_shared_ephemeris_multi_group():
    stats = warm_shared_ephemeris("2026-10-10", [7.0, -5.0, 7.0])
    assert set(stats["groups"]) == {"UTC-5", "UTC+7"}


def test_transit_of_day_derives_moon():
    from src.services.transit_service import _compute_bodies

    ephem = {"bodies": _compute_bodies(datetime.now(timezone.utc))}
    day = _transit_of_day(ephem)
    assert "moon_sign" in day
    assert day["moon_sign"]  # non-empty sign name


# ---------------------------------------------------------------------------
# Phase C — batch delivery
# ---------------------------------------------------------------------------


def test_run_daily_batch_empty(clean_users):
    """No users due -> zero counts, no crash."""
    stats = run_daily_batch(datetime.now(timezone.utc), warm_first=False)
    assert stats["users_due"] == 0
    assert stats["sent"] == 0


def test_run_daily_batch_sends_due_users(clean_users):
    now = datetime.now(timezone.utc)
    slot = _slot_now()
    for uid in ("wtest_a", "wtest_b"):
        save_prefs(NotificationPrefs(
            user_id=uid, daily_transit=True,
            transit_time=slot, tz_offset_hours=7.0,
        ))
        register_device(uid, "ios", f"ExpoToken_{uid}")

    stats = run_daily_batch(now, warm_first=True)
    assert stats["users_due"] >= 2
    assert stats["sent"] >= 2
    assert stats["tz_groups"] == ["UTC+7"]


def test_batch_dedupes_second_run(clean_users):
    """Second batch run the same day sends nothing (dedup)."""
    now = datetime.now(timezone.utc)
    slot = _slot_now()
    save_prefs(NotificationPrefs(
        user_id="wtest_a", daily_transit=True,
        transit_time=slot, tz_offset_hours=7.0,
    ))
    register_device("wtest_a", "ios", "ExpoToken_wtest_a")

    first = run_daily_batch(now, warm_first=False)
    assert first["sent"] >= 1

    second = run_daily_batch(now, warm_first=False)
    assert second["skipped_dedup"] >= 1
    assert second["sent"] == 0


def test_batch_skips_off_users_via_deliver(clean_users):
    """daily_transit=False -> 'off' (users_due_now already filters these
    out at the SQL level, so the batch never sees them — but the guard
    in _deliver_one keeps the path safe when called directly)."""
    prefs = NotificationPrefs(user_id="wtest_a", daily_transit=False)
    assert _deliver_one(prefs, datetime.now(timezone.utc)) == "off"


def test_batch_skips_quiet_hours_via_deliver(clean_users):
    """Quiet hours covering 'now' -> 'quiet'."""
    now = datetime.now(timezone.utc)
    local = now + timedelta(hours=7)
    quiet_start = f"{local.hour:02d}:00"
    quiet_end = f"{(local.hour + 1) % 24:02d}:00"
    prefs = NotificationPrefs(
        user_id="wtest_a", daily_transit=True,
        transit_time=_slot_now(), tz_offset_hours=7.0,
        quiet_hours_start=quiet_start, quiet_hours_end=quiet_end,
    )
    register_device("wtest_a", "ios", "ExpoToken_wtest_a")
    assert _deliver_one(prefs, now) == "quiet"


# ---------------------------------------------------------------------------
# Single-user delivery path
# ---------------------------------------------------------------------------


def test_deliver_one_off(clean_users):
    prefs = NotificationPrefs(user_id="wtest_a", daily_transit=False)
    assert _deliver_one(prefs, datetime.now(timezone.utc)) == "off"


def test_deliver_one_dedup(clean_users):
    now = datetime.now(timezone.utc)
    prefs = NotificationPrefs(
        user_id="wtest_a", daily_transit=True,
        transit_time=_slot_now(), tz_offset_hours=7.0,
    )
    register_device("wtest_a", "ios", "ExpoToken_wtest_a")
    _deliver_one(prefs, now)
    # Second call same day -> dedup
    assert _deliver_one(prefs, now) == "dedup"


# ---------------------------------------------------------------------------
# Backfill
# ---------------------------------------------------------------------------


def test_backfill_finds_nothing_when_all_sent(clean_users):
    """After a successful batch, backfill recovers 0 users."""
    now = datetime.now(timezone.utc)
    slot = _slot_now()
    save_prefs(NotificationPrefs(
        user_id="wtest_a", daily_transit=True,
        transit_time=slot, tz_offset_hours=7.0,
    ))
    register_device("wtest_a", "ios", "ExpoToken_wtest_a")
    run_daily_batch(now, warm_first=False)

    result = backfill_missed(now, max_users=10)
    assert result["recovered"] == 0


def test_backfill_recovers_unsent(clean_users):
    """A user whose slot passed but has no log entry today is recovered."""
    now = datetime.now(timezone.utc)
    local = now + timedelta(hours=7)
    # Slot 30 minutes ago — within the 3h catch-up window.
    past = local - timedelta(minutes=30)
    slot = f"{past.hour:02d}:{past.minute:02d}"
    save_prefs(NotificationPrefs(
        user_id="wtest_a", daily_transit=True,
        transit_time=slot, tz_offset_hours=7.0,
    ))
    register_device("wtest_a", "ios", "ExpoToken_wtest_a")

    result = backfill_missed(now, max_users=10)
    assert result["recovered"] == 1


# ---------------------------------------------------------------------------
# BatchStats
# ---------------------------------------------------------------------------


def test_batch_stats_to_dict():
    stats = BatchStats(date="2026-10-10", sent=5, users_due=7)
    d = stats.to_dict()
    assert d["date"] == "2026-10-10"
    assert d["sent"] == 5
    assert d["users_due"] == 7
