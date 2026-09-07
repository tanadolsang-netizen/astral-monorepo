"""Read/append proxy for Hermes Agent's local memory store.

Hermes (D:\\AI\\AOS\\hermes) keeps its own memory as two flat files —
memories/MEMORY.md and memories/USER.md — with entries separated by the
literal delimiter "\n\u00a7\n" (see hermes-agent/tools/memory_tool.py). This
module re-implements that same file format and locking convention so
astral-backend can read/append entries without importing hermes-agent's
package directly (it isn't installed as a dependency, and its code path is
owned by a separate project).

Concurrent-write safety mirrors MemoryStore in hermes-agent: an exclusive
lock on a "<file>.lock" sibling, a full re-read of current entries once the
lock is held (so a write from a live Hermes agent isn't clobbered), then an
atomic replace (temp file + os.replace) rather than truncate-then-write.
"""

import contextlib
import os
import sqlite3
from pathlib import Path
from typing import Optional

from src.models.memory import MemoryEntry, MemorySummary, MemoryTarget

try:
    import msvcrt
except ImportError:  # not on Windows
    msvcrt = None
try:
    import fcntl
except ImportError:  # on Windows
    fcntl = None

DELIMITER = "\n\u00a7\n"

_DEFAULT_ROOT = Path(r"D:\AI\AOS\hermes")
HERMES_ROOT = Path(os.getenv("HERMES_MEMORY_ROOT") or _DEFAULT_ROOT).resolve()
MEMORY_DIR = HERMES_ROOT / "memories"
STATE_DB = Path(os.getenv("HERMES_STATE_DB") or (HERMES_ROOT / "state.db")).resolve()

_FILENAMES: dict[MemoryTarget, str] = {"memory": "MEMORY.md", "user": "USER.md"}


def _target_path(target: MemoryTarget) -> Path:
    return MEMORY_DIR / _FILENAMES[target]


def _parse_entries(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(DELIMITER) if part.strip()]


def _atomic_write_text(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


@contextlib.contextmanager
def _file_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "a+b") as fh:
        if msvcrt is not None:
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_LOCK, 1)
        elif fcntl is not None:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if msvcrt is not None:
                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
            elif fcntl is not None:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def read_entries(target: MemoryTarget) -> list[MemoryEntry]:
    path = _target_path(target)
    if not path.exists():
        return []
    raw = path.read_text(encoding="utf-8")
    return [MemoryEntry(index=i, content=c) for i, c in enumerate(_parse_entries(raw))]


def read_summary() -> MemorySummary:
    memory_path = _target_path("memory")
    user_path = _target_path("user")
    return MemorySummary(
        memory_bytes=memory_path.stat().st_size if memory_path.exists() else 0,
        memory_entries=len(read_entries("memory")),
        user_bytes=user_path.stat().st_size if user_path.exists() else 0,
        user_entries=len(read_entries("user")),
    )


def append_entry(target: MemoryTarget, content: str) -> MemoryEntry:
    content = content.strip()
    if not content:
        raise ValueError("content must not be empty")

    path = _target_path(target)
    lock_path = path.with_name(path.name + ".lock")
    with _file_lock(lock_path):
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        entries = _parse_entries(current)
        entries.append(content)
        _atomic_write_text(path, DELIMITER.join(entries))
        new_index = len(entries) - 1

    return MemoryEntry(index=new_index, content=content)


def search_sessions(query: str, limit: int = 20) -> list[dict]:
    """Best-effort read-only full-text search over Hermes chat history.

    Opens state.db in SQLite's URI ro mode, which refuses to create the file
    and refuses writes, and returns immediately rather than blocking a live
    Hermes agent that holds the write lock.
    """
    if not STATE_DB.exists():
        return []

    uri = f"file:{STATE_DB.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=2.0)
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            """
            SELECT messages.id, messages.session_id, messages.role,
                   messages.content, messages.timestamp
            FROM messages_fts
            JOIN messages ON messages.id = messages_fts.rowid
            WHERE messages_fts MATCH ? AND messages.active = 1
            ORDER BY messages.timestamp DESC
            LIMIT ?
            """,
            (query, limit),
        )
        return [dict(row) for row in cur.fetchall()]
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()
