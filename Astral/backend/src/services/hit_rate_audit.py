"""Hit-rate audit — honest accuracy accounting with NO survivorship bias.

hit_rate = confirmed / total, where total INCLUDES refuted and still-pending
predictions (so we never silently drop misses). Reports are broken down by
mechanism_tag so genuine vs self_fulfilling vs coincidence effects stay visible.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.services.prediction_log import VALID_MECHANISMS


def _verdict(rec: dict[str, Any]) -> str:
    return rec.get("verdict", "pending")


def hit_rate(
    records: list[dict[str, Any]], *, resolved_only: bool = False
) -> dict[str, Any]:
    """Overall hit rate. By default total includes ALL records (no bias)."""
    total = len(records)
    confirmed = sum(1 for r in records if _verdict(r) == "confirmed")
    refuted = sum(1 for r in records if _verdict(r) == "refuted")
    pending = sum(1 for r in records if _verdict(r) == "pending")

    denom = (confirmed + refuted) if resolved_only else total
    rate = (confirmed / denom) if denom else 0.0

    return {
        "total": total,
        "confirmed": confirmed,
        "refuted": refuted,
        "pending": pending,
        "denominator": denom,
        "resolved_only": resolved_only,
        "hit_rate": round(rate, 4),
        "survivorship_safe": not resolved_only,
    }


def audit_by_mechanism(
    records: list[dict[str, Any]], *, resolved_only: bool = False
) -> dict[str, Any]:
    """Breakdown of hit rate per mechanism_tag (genuine / self_fulfilling / ...)."""
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    untagged: list[dict[str, Any]] = []
    for r in records:
        tag = r.get("mechanism_tag")
        if tag in VALID_MECHANISMS:
            buckets[tag].append(r)
        else:
            untagged.append(r)

    breakdown: dict[str, Any] = {}
    for tag in VALID_MECHANISMS:
        grp = buckets.get(tag, [])
        confirmed = sum(1 for r in grp if _verdict(r) == "confirmed")
        refuted = sum(1 for r in grp if _verdict(r) == "refuted")
        pending = sum(1 for r in grp if _verdict(r) == "pending")
        total = len(grp)
        denom = (confirmed + refuted) if resolved_only else total
        rate = (confirmed / denom) if denom else 0.0
        breakdown[tag] = {
            "total": total,
            "confirmed": confirmed,
            "refuted": refuted,
            "pending": pending,
            "hit_rate": round(rate, 4),
        }

    return {
        "by_mechanism": breakdown,
        "untagged": {
            "total": len(untagged),
            "confirmed": sum(1 for r in untagged if _verdict(r) == "confirmed"),
            "refuted": sum(1 for r in untagged if _verdict(r) == "refuted"),
            "pending": sum(1 for r in untagged if _verdict(r) == "pending"),
        },
    }


def generate_report(
    records: list[dict[str, Any]], *, resolved_only: bool = False
) -> dict[str, Any]:
    """Full audit report: overall hit rate + per-mechanism breakdown."""
    return {
        "overall": hit_rate(records, resolved_only=resolved_only),
        "by_mechanism": audit_by_mechanism(records, resolved_only=resolved_only),
        "resolved_only": resolved_only,
    }
