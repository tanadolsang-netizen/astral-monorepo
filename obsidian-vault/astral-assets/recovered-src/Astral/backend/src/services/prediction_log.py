"""Timestamped prediction + follow-up log (anti-confirmation-bias registry).

P2+P3 blueprint:
- pre_register() records a claim BEFORE its expected event, rejecting any
  retroactive registration (created_at must be earlier than expected_event).
- confirm() / refute() finalize a verdict with evidence and a mechanism_tag
  classifying WHY it hit or missed (genuine / self_fulfilling / confirmation /
  coincidence) so survivorship-bias and Barnum effects stay visible.
"""
from __future__ import annotations

import hashlib
import uuid
from datetime import date, datetime, timezone
from typing import Any, Optional

from src.db.prediction_log_store import (
    append_record,
    get_record,
    load_records,
    save_records,
)

VALID_VERDICTS = ("pending", "confirmed", "refuted")
VALID_MECHANISMS = ("genuine", "self_fulfilling", "confirmation", "coincidence")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _to_dt(value: Any) -> Optional[datetime]:
    """Best-effort parse of a date / datetime / iso-string into a tz-aware datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    if isinstance(value, str):
        s = value.strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(s)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def compute_chart_fingerprint(chart: Any) -> str:
    """Deterministic hash of a chart's identity (not of the reading text).

    Accepts a ChartResponse-like object or dict with bodies / ascendant.
    """
    if hasattr(chart, "model_dump"):
        try:
            chart = chart.model_dump()
        except Exception:
            pass

    if isinstance(chart, dict):
        system = chart.get("system", "")
        dt_utc = chart.get("datetime_utc", "")
        bodies = chart.get("bodies", []) or []
        asc = chart.get("ascendant", {}) or {}
        parts = [str(system), str(dt_utc)]
        for b in bodies:
            if isinstance(b, dict):
                parts.append(f"{b.get('body')}:{b.get('absolute_deg')}")
            else:
                parts.append(str(b))
        if isinstance(asc, dict):
            parts.append(f"ASC:{asc.get('sign')}:{asc.get('absolute_deg')}")
        ident = "|".join(parts)
    else:
        ident = repr(chart)
    return hashlib.sha256(ident.encode("utf-8")).hexdigest()[:16]


def pre_register(
    chart: Any,
    claim_text: str,
    expected_event: Any,
    *,
    created_at: Optional[datetime] = None,
) -> dict[str, Any]:
    """Register a prediction BEFORE the event occurs.

    Rejects retroactive registration: created_at must be strictly earlier
    than expected_event (otherwise confirmation bias / post-hoc fitting).
    """
    created = created_at or _utcnow()
    created = created if created.tzinfo else created.replace(tzinfo=timezone.utc)
    expected = _to_dt(expected_event)
    if expected is None:
        raise ValueError(
            "expected_event must be a parseable date/datetime/iso-string"
        )
    if created >= expected:
        raise ValueError(
            "RETROACTIVE REGISTRATION REJECTED: created_at "
            f"({created.isoformat()}) is not earlier than expected_event "
            f"({expected.isoformat()}). Predictions must be pre-registered."
        )

    record = {
        "prediction_id": uuid.uuid4().hex,
        "chart_fingerprint": compute_chart_fingerprint(chart),
        "created_at": created.isoformat(),
        "claim_text": claim_text,
        "expected_event": expected.isoformat(),
        "follow_ups": [],
        "verdict": "pending",
        "mechanism_tag": None,
        "evidence_url": None,
    }
    append_record(record)
    return record


def _update(prediction_id: str, changes: dict[str, Any]) -> dict[str, Any]:
    records = load_records()
    for rec in records:
        if rec.get("prediction_id") == prediction_id:
            rec.update(changes)
            save_records(records)
            return rec
    raise KeyError(f"prediction_id not found: {prediction_id}")


def confirm(
    prediction_id: str,
    evidence_url: str,
    mechanism_tag: str,
    *,
    when: Optional[datetime] = None,
) -> dict[str, Any]:
    """Finalize a prediction as confirmed with evidence + mechanism classification."""
    if mechanism_tag not in VALID_MECHANISMS:
        raise ValueError(f"mechanism_tag must be one of {VALID_MECHANISMS}")
    return _update(
        prediction_id,
        {
            "verdict": "confirmed",
            "evidence_url": evidence_url,
            "mechanism_tag": mechanism_tag,
            "resolved_at": (when or _utcnow()).isoformat(),
        },
    )


def refute(
    prediction_id: str,
    evidence_url: str,
    mechanism_tag: str,
    *,
    when: Optional[datetime] = None,
) -> dict[str, Any]:
    """Finalize a prediction as refuted with evidence + mechanism classification."""
    if mechanism_tag not in VALID_MECHANISMS:
        raise ValueError(f"mechanism_tag must be one of {VALID_MECHANISMS}")
    return _update(
        prediction_id,
        {
            "verdict": "refuted",
            "evidence_url": evidence_url,
            "mechanism_tag": mechanism_tag,
            "resolved_at": (when or _utcnow()).isoformat(),
        },
    )


def add_follow_up(
    prediction_id: str, note: str, *, when: Optional[datetime] = None
) -> dict[str, Any]:
    """Append a timestamped follow-up note to a prediction."""
    records = load_records()
    for rec in records:
        if rec.get("prediction_id") == prediction_id:
            rec.setdefault("follow_ups", [])
            rec["follow_ups"].append(
                {"at": (when or _utcnow()).isoformat(), "note": note}
            )
            save_records(records)
            return rec
    raise KeyError(f"prediction_id not found: {prediction_id}")


def get_prediction(prediction_id: str) -> Optional[dict[str, Any]]:
    """Fetch a single prediction by id."""
    return get_record(prediction_id)
