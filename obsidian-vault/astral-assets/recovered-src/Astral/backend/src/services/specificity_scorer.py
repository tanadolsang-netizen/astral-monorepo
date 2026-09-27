"""Specificity scorer — blocks Barnum / generic claims from being rendered.

A prediction claim must be SPECIFIC to be auditable (falsifiable). This module
scores a claim_text from 0.0 (vague / Barnum) to 1.0 (concrete, falsifiable).
Callers should enforce a minimum before rendering a claim.
"""
from __future__ import annotations

import re
from typing import Optional

# Generic / Barnum phrases that apply to almost anyone (strong penalty).
_GENERIC_PHRASES = [
    "คุณจะเจอเรื่องดี",
    "เรื่องดี",
    "โชคดี",
    "สิ่งดีๆ",
    "สิ่งดี ๆ",
    "good things",
    "something good",
    "good luck",
    "better days",
    "changes are coming",
    "things will improve",
    "you will meet someone",
    "opportunity will come",
    "a surprise awaits",
    "your luck will change",
    "everything happens for a reason",
    "the universe has a plan",
    "positive energy",
    "you may experience",
    "soon you will",
    "in the near future",
    "ช่วงนี้มีเรื่องดี",
    "เร็วๆ นี้",
]

# Concrete markers that increase specificity / falsifiability.
_NUMERIC_RE = re.compile(r"\b\d{1,4}\b")
_DATE_RE = re.compile(
    r"\b(\d{1,2}[/\-.]\d{1,2}([/\-.]\d{2,4})?|\d{4}-\d{2}-\d{2}|"
    r"\d{1,2}\s*(ม\.ค\.|ก\.พ\.|มี\.ค\.|เม\.ย\.|พ\.ค\.|มิ\.ย\.|ก\.ค\.|ส\.ค\.|ก\.ย\.|ต\.ค\.|พ\.ย\.|ธ\.ค\.|"
    r"jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*)\b",
    re.IGNORECASE,
)
_TIME_RE = re.compile(r"\b\d{1,2}[:.]\d{2}\b|\b\d{1,2}\s*(am|pm|น\.|โมง|นาฬิกา)\b", re.IGNORECASE)
_MONEY_RE = re.compile(r"[฿$€£]\s*\d|\b\d+\s*(บาท|baht|usd|eur|dollars?)\b", re.IGNORECASE)
_PERCENT_RE = re.compile(r"\b\d{1,3}\s*%")
_NAMED_ENTITY_RE = re.compile(r"\b([A-Z][a-z]{2,}(?:\s[A-Z][a-z]+){0,3})\b")
_TOKEN_RE = re.compile(r"[\w\u0E00-\u0E7F]+", re.UNICODE)

SPECIFICITY_MINIMUM = 0.35


def specificity_score(claim_text: str) -> float:
    """Return a 0.0..1.0 specificity score for a claim."""
    if not claim_text or not claim_text.strip():
        return 0.0

    text = claim_text.strip()
    lowered = text.lower()
    tokens = _TOKEN_RE.findall(text)
    n_tokens = max(len(tokens), 1)

    score = 0.0

    # Penalty: generic Barnum phrases (each match subtracts strongly).
    generic_hits = sum(1 for phrase in _GENERIC_PHRASES if phrase in lowered)
    if generic_hits:
        score -= 0.35 * generic_hits

    # Boost: concrete numeric specificity.
    if _DATE_RE.search(text):
        score += 0.30
    if _TIME_RE.search(text):
        score += 0.15
    numeric_count = len(_NUMERIC_RE.findall(text))
    if numeric_count:
        score += min(0.20, 0.05 * numeric_count)
    if _MONEY_RE.search(text):
        score += 0.15
    if _PERCENT_RE.search(text):
        score += 0.15

    # Boost: named entities (people, places, companies).
    named = _NAMED_ENTITY_RE.findall(text)
    if named:
        score += min(0.20, 0.07 * len(named))

    # Boost: moderate length indicates detail (too short = vague).
    if n_tokens >= 6:
        score += 0.10

    return max(0.0, min(1.0, score))


def is_specific_enough(
    claim_text: str, min_score: float = SPECIFICITY_MINIMUM
) -> bool:
    """True when the claim meets the minimum specificity threshold."""
    return specificity_score(claim_text) >= min_score


def enforce_minimum(
    claim_text: str, min_score: float = SPECIFICITY_MINIMUM
) -> float:
    """Raise if the claim is too vague to render; otherwise return its score."""
    score = specificity_score(claim_text)
    if score < min_score:
        raise ValueError(
            f"CLAIM REJECTED: specificity {score:.2f} < minimum {min_score:.2f}. "
            "Claim is too generic/Barnum to be auditable. Make it concrete "
            "(add dates, times, names, amounts)."
        )
    return score
