BEGIN TRANSACTION;
CREATE TABLE charts (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  name TEXT NOT NULL,
  date TEXT NOT NULL,
  time TEXT NOT NULL,
  tz_offset_hours REAL NOT NULL,
  lat REAL NOT NULL,
  lon REAL NOT NULL,
  system TEXT DEFAULT 'tropical',
  payload TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE memory (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  target TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE profiles (
  id TEXT PRIMARY KEY,
  email TEXT,
  full_name TEXT,
  tz TEXT DEFAULT 'Asia/Bangkok',
  lat REAL DEFAULT 13.8591,
  lon REAL DEFAULT 100.5217,
  chart_system TEXT DEFAULT 'tropical',
  created_at TEXT DEFAULT (datetime('now'))
);
INSERT INTO "profiles" VALUES('00000000-0000-0000-0000-000000000001','dev@example.com','Dev User','Asia/Bangkok',13.8591,100.5217,'tropical','2026-08-27 04:53:29');
CREATE TABLE research_corpus (
  id TEXT PRIMARY KEY,
  category TEXT NOT NULL,
  name TEXT NOT NULL,
  data TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  timestamp TEXT DEFAULT (datetime('now'))
);
COMMIT;
