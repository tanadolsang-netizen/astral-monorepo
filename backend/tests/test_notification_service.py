"""Tests for the notification service + router (push delivery, prefs, log)."""

from datetime import datetime, timezone

import pytest

from src.services import notification_service as ns


@pytest.fixture(autouse=True)
def clean_tables():
    con = ns._connect()
    con.execute("DELETE FROM notification_log")
    con.execute("DELETE FROM push_devices")
    con.execute("DELETE FROM user_notification_prefs")
    con.commit()
    con.close()
    yield
    con = ns._connect()
    con.execute("DELETE FROM notification_log")
    con.execute("DELETE FROM push_devices")
    con.execute("DELETE FROM user_notification_prefs")
    con.commit()
    con.close()


UID = "notif-test-user"


# --- preferences -----------------------------------------------------------

def test_prefs_default_when_unset():
    prefs = ns.get_prefs(UID)
    assert prefs.user_id == UID
    assert prefs.daily_transit is True
    assert prefs.transit_time == "08:00"
    assert prefs.tz_offset_hours == 7.0


def test_prefs_roundtrip():
    ns.save_prefs(
        ns.NotificationPrefs(
            user_id=UID, transit_time="07:30", tz_offset_hours=-5.0, daily_transit=False
        )
    )
    got = ns.get_prefs(UID)
    assert got.transit_time == "07:30"
    assert got.tz_offset_hours == -5.0
    assert got.daily_transit is False


def test_prefs_update_overwrites():
    ns.save_prefs(ns.NotificationPrefs(user_id=UID, transit_time="06:00"))
    ns.save_prefs(ns.NotificationPrefs(user_id=UID, transit_time="09:15"))
    assert ns.get_prefs(UID).transit_time == "09:15"


# --- devices ---------------------------------------------------------------

def test_register_device_persists():
    ns.register_device(UID, "ios", "tok-1")
    devices = ns.list_devices(UID)
    assert len(devices) == 1
    assert devices[0]["platform"] == "ios"
    assert devices[0]["enabled"] == 1


def test_register_device_rejects_bad_platform():
    with pytest.raises(ValueError):
        ns.register_device(UID, "windows-phone", "tok-x")


def test_unregister_device_soft_disables():
    ns.register_device(UID, "android", "tok-2")
    result = ns.unregister_device(UID, "tok-2")
    assert result["rows"] == 1
    assert ns.list_devices(UID)[0]["enabled"] == 0


def test_reregister_device_flips_enabled_back():
    ns.register_device(UID, "web", "tok-3")
    ns.unregister_device(UID, "tok-3")
    ns.register_device(UID, "web", "tok-3")
    assert ns.list_devices(UID)[0]["enabled"] == 1


# --- quiet hours -----------------------------------------------------------

def test_quiet_hours_simple_range():
    prefs = ns.NotificationPrefs(user_id=UID, tz_offset_hours=7,
                                 quiet_hours_start="22:00", quiet_hours_end="06:00")
    # 16:00 UTC = 23:00 local -> inside
    assert ns.in_quiet_hours(prefs, datetime(2026, 10, 10, 16, 0, tzinfo=timezone.utc))
    # 09:00 UTC = 16:00 local -> outside
    assert not ns.in_quiet_hours(prefs, datetime(2026, 10, 10, 9, 0, tzinfo=timezone.utc))


def test_quiet_hours_disabled_when_unset():
    prefs = ns.NotificationPrefs(user_id=UID)
    assert not ns.in_quiet_hours(prefs, datetime(2026, 10, 10, 23, 0, tzinfo=timezone.utc))


def test_quiet_hours_early_morning_inside_wrapped_range():
    prefs = ns.NotificationPrefs(user_id=UID, tz_offset_hours=7,
                                 quiet_hours_start="22:00", quiet_hours_end="06:00")
    # 23:30 UTC = 06:30 local -> outside; 21:00 UTC = 04:00 local -> inside
    assert ns.in_quiet_hours(prefs, datetime(2026, 10, 10, 21, 0, tzinfo=timezone.utc))
    assert not ns.in_quiet_hours(prefs, datetime(2026, 10, 10, 23, 30, tzinfo=timezone.utc))


# --- scheduling ------------------------------------------------------------

def test_users_due_now_window():
    ns.save_prefs(ns.NotificationPrefs(user_id=UID, transit_time="08:00", tz_offset_hours=7))
    due = ns.users_due_now(datetime(2026, 10, 11, 1, 2, tzinfo=timezone.utc))  # 08:02 local
    assert [p.user_id for p in due] == [UID]
    not_due = ns.users_due_now(datetime(2026, 10, 11, 20, 0, tzinfo=timezone.utc))
    assert not_due == []


def test_users_due_now_respects_daily_off():
    ns.save_prefs(ns.NotificationPrefs(user_id=UID, transit_time="08:00",
                                       tz_offset_hours=7, daily_transit=False))
    assert ns.users_due_now(datetime(2026, 10, 11, 1, 2, tzinfo=timezone.utc)) == []


def test_users_due_now_skips_quiet_hours():
    ns.save_prefs(ns.NotificationPrefs(user_id=UID, transit_time="05:00", tz_offset_hours=7,
                                       quiet_hours_start="22:00", quiet_hours_end="06:00"))
    # 05:00 local falls inside 22:00-06:00 quiet window -> not due
    assert ns.users_due_now(datetime(2026, 10, 10, 22, 1, tzinfo=timezone.utc)) == []


# --- delivery --------------------------------------------------------------

def test_send_daily_transit_persists_log():
    ns.save_prefs(ns.NotificationPrefs(user_id=UID))
    ns.register_device(UID, "ios", "exp-token-xyz")
    result = ns.send_daily_transit(UID, datetime.now(timezone.utc))
    assert result["status"] in ("sent", "failed")  # failed only if network down
    assert result["headline"]  # Thai headline from real transit engine

    con = ns._connect()
    row = con.execute(
        "SELECT kind, title, body, delivery_status FROM notification_log "
        "WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (UID,),
    ).fetchone()
    con.close()
    assert row["kind"] == "daily_transit"
    assert row["title"] == result["headline"]
    assert row["delivery_status"] in ("sent", "failed")


def test_send_daily_transit_dedupes_same_day():
    ns.save_prefs(ns.NotificationPrefs(user_id=UID))
    now = datetime.now(timezone.utc)
    ns.send_daily_transit(UID, now)
    second = ns.send_daily_transit(UID, now)
    assert second == {"status": "skipped", "reason": "already_sent"}


def test_send_daily_transit_skipped_when_off():
    ns.save_prefs(ns.NotificationPrefs(user_id=UID, daily_transit=False))
    result = ns.send_daily_transit(UID, datetime.now(timezone.utc))
    assert result["status"] == "skipped"
    assert result["reason"] == "daily_transit_off"


def test_send_daily_transit_no_device_logs_pending():
    ns.save_prefs(ns.NotificationPrefs(user_id=UID))
    result = ns.send_daily_transit(UID, datetime.now(timezone.utc))
    assert result["status"] == "skipped"  # no devices registered
    con = ns._connect()
    row = con.execute(
        "SELECT delivery_status FROM notification_log WHERE user_id = ?", (UID,)
    ).fetchone()
    con.close()
    assert row["delivery_status"] == "pending"
