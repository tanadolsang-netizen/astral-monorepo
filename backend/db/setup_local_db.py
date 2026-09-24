"""Local SQLite cache + migration runner for Astral backend."""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "astral.db"
MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
SCHEMA_FILE = MIGRATIONS_DIR / "001_initial_schema.sql"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def _table_names(cur: sqlite3.Cursor) -> set[str]:
    return {row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}


def migrate() -> None:
    """Apply migrations in order if not already applied."""
    con = _connect()
    cur = con.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS migrations (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          applied_at TEXT DEFAULT (datetime('now'))
        );
        """
    )

    applied = {
        row[0]
        for row in cur.execute("SELECT name FROM migrations").fetchall()
    }

    sql_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    applied_now = 0
    for sql_file in sql_files:
        name = sql_file.name
        if name in applied:
            continue
        sql = sql_file.read_text(encoding="utf-8")
        cur.executescript(sql)
        cur.execute("INSERT INTO migrations(name) VALUES(?)", (name,))
        applied_now += 1
        print(f"migrated: {name}")

    con.commit()
    con.close()
    print(f"migrations applied this run: {applied_now}")


def seed() -> None:
    """Seed local cache with baseline data."""
    con = _connect()
    cur = con.cursor()

    seeds_dir = Path(__file__).resolve().parent / "seeds"
    sql_files = sorted(seeds_dir.glob("*.sql"))
    if not sql_files:
        print("no seeds")
        return
    for sql_file in sql_files:
        sql = sql_file.read_text(encoding="utf-8")
        cur.executescript(sql)
        print(f"seeded: {sql_file.name}")
    con.commit()
    con.close()


def backup(out_path: str | Path | None = None) -> Path:
    """Create timestamped SQLite backup."""
    out_path = Path(out_path or Path(__file__).resolve().parent.parent / "db/backups")
    out_path.mkdir(parents=True, exist_ok=True)
    backup_file = out_path / f"astral-{Path(__file__).stem}.db"
    con = _connect()
    bkp = sqlite3.connect(backup_file)
    con.backup(bkp)
    bkp.close()
    con.close()
    print(f"backup: {backup_file}")
    return backup_file


if __name__ == "__main__":
    migrate()
    seed()
    backup()
