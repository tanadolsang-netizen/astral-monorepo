-- Notification + user preferences schema
-- Co-Star-style: push delivery, user timezone-aware scheduling, prediction log

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS user_notification_prefs (
  user_id TEXT PRIMARY KEY,
  daily_transit INTEGER NOT NULL DEFAULT 1,
  transit_time TEXT NOT NULL DEFAULT '08:00',
  tz_offset_hours REAL NOT NULL DEFAULT 7.0,
  weekly_reading INTEGER NOT NULL DEFAULT 1,
  compatibility_alerts INTEGER NOT NULL DEFAULT 1,
  quiet_hours_start TEXT,
  quiet_hours_end TEXT,
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS push_devices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  platform TEXT NOT NULL CHECK (platform IN ('ios', 'android', 'web')),
  push_token TEXT NOT NULL UNIQUE,
  enabled INTEGER NOT NULL DEFAULT 1,
  last_seen TEXT DEFAULT (datetime('now')),
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS notification_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  kind TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT,
  payload TEXT,
  scheduled_for TEXT,
  sent_at TEXT,
  delivery_status TEXT NOT NULL DEFAULT 'pending'
    CHECK (delivery_status IN ('pending', 'sent', 'delivered', 'failed', 'skipped_quiet_hours')),
  error_message TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_notif_log_user_created
  ON notification_log(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_notif_log_pending
  ON notification_log(delivery_status, scheduled_for);

CREATE INDEX IF NOT EXISTS idx_push_devices_user
  ON push_devices(user_id, enabled);

CREATE INDEX IF NOT EXISTS idx_notif_prefs_active
  ON user_notification_prefs(daily_transit, transit_time);

COMMIT;
