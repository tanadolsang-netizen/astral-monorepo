"""Persistent JSON store for timestamped prediction logs.

Simple, dependency-free JSON file at:
    C:/AI/NEW-AI-REBORN/data/prediction_log.json

Provides load/store functions used by src.services.prediction_log.
"""
from __future__ import annotations

import json
import os
import threading
from typing import Any, Optional

# Default location: <repo>/data/prediction_log.json
DEFAULT_STORE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "prediction_log.json",
)

_lock = threading.RLock()


def store_path() -> str:
    """Absolute path of the JSON store on disk."""
    return DEFAULT_STORE_PATH


def _ensure_parent(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)


def load_records(path: Optional[str] = None) -> list[dict[str, Any]]:
    """Load all prediction records; returns [] if the file is missing/corrupt."""
    p = path or DEFAULT_STORE_PATH
    if not os.path.exists(p):
        return []
    with _lock:
        with open(p, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                return []
    if not isinstance(data, list):
        return []
    return data


def save_records(records: list[dict[str, Any]], path: Optional[str] = None) -> None:
    """Atomically write all records to disk (pretty, UTF-8)."""
    p = path or DEFAULT_STORE_PATH
    _ensure_parent(p)
    tmp = p + ".tmp"
    with _lock:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        os.replace(tmp, p)


def append_record(record: dict[str, Any], path: Optional[str] = None) -> None:
    """Append a single record to the store."""
    records = load_records(path)
    records.append(record)
    save_records(records, path)


def get_record(prediction_id: str, path: Optional[str] = None) -> Optional[dict[str, Any]]:
    """Fetch one record by prediction_id, or None."""
    for rec in load_records(path):
        if rec.get("prediction_id") == prediction_id:
            return rec
    return None
