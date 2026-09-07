"""Thin SQLite cache layer for local/dev deployments.

Uses the project-local `astral.db` created under `db/` and populated by
`db/setup_local_db.py`. Supabase remains the source of truth in production;
this module only mirrors/reads when Supabase is unavailable.
"""

from __future__ import annotations

import sqlite3
from datetime import date as date_type, time as time_type
from pathlib import Path
from typing import Any

DB_PATH = Path.cwd() / "astral.db"


def _connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise RuntimeError(f"Local cache DB not found: {DB_PATH}")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def save_chart(
    *,
    user_id: str,
    name: str,
    date: date_type,
    time: time_type,
    tz_offset_hours: float,
    lat: float,
    lon: float,
    system: str = "tropical",
    payload: dict[str, Any],
) -> dict[str, Any]:
    con = _connect()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO charts(user_id, name, date, time, tz_offset_hours, lat, lon, system, payload)
        VALUES(?,?,?,?,?,?,?,?,?)
        """,
        (
            user_id,
            name,
            date.isoformat(),
            time.isoformat(),
            float(tz_offset_hours),
            float(lat),
            float(lon),
            system,
            __import__("json").dumps(payload, ensure_ascii=False),
        ),
    )
    con.commit()
    row = cur.execute("SELECT * FROM charts WHERE rowid = last_insert_rowid()").fetchone()
    con.close()
    return dict(row)


def list_recent(user_id: str, limit: int = 5) -> list[dict[str, Any]]:
    con = _connect()
    cur = con.cursor()
    rows = cur.execute(
        """
        SELECT id,name,date,time,system,created_at
        FROM charts
        WHERE user_id = ?
        ORDER BY datetime(created_at) DESC
        LIMIT ?
        """,
        (user_id, max(0, min(limit, 50))),
    ).fetchall()
    con.close()
    return [dict(r) for r in rows]


def get_chart(chart_id: str, user_id: str) -> dict[str, Any] | None:
    con = _connect()
    row = con.execute(
        "SELECT * FROM charts WHERE id = ? AND user_id = ?",
        (chart_id, user_id),
    ).fetchone()
    con.close()
    return dict(row) if row else None
