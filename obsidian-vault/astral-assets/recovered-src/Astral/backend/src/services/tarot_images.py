"""Tarot card images — map card names to local deck files."""

from __future__ import annotations

import os
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
DECK_DIR = _REPO_ROOT / "assets" / "tarot" / "sola-busca"
PUBLIC_WEB_BASE = "/tarot/sola-busca"

_MAJORS = [
    "The Fool", "The Magician", "The High Priestess", "The Empress",
    "The Emperor", "The Hierophant", "The Lovers", "The Chariot",
    "Strength", "The Hermit", "Wheel of Fortune", "Justice",
    "The Hanged Man", "Death", "Temperance", "The Devil",
    "The Tower", "The Star", "The Moon", "The Sun",
    "Judgement", "The World",
]
_SUITS = ["Wands", "Cups", "Swords", "Pentacles"]
_RANKS = [
    "Ace of {s}", "Two of {s}", "Three of {s}", "Four of {s}", "Five of {s}",
    "Six of {s}", "Seven of {s}", "Eight of {s}", "Nine of {s}", "Ten of {s}",
    "Page of {s}", "Knight of {s}", "Queen of {s}", "King of {s}",
]

CARD_INDEX: dict[str, int] = {}
for i, name in enumerate(_MAJORS):
    CARD_INDEX[name] = i
n = 22
for suit in _SUITS:
    for tmpl in _RANKS:
        CARD_INDEX[tmpl.format(s=suit)] = n
        n += 1


def card_image_url(card_name: str) -> str | None:
    """Return a public web path to the card image, or None if missing."""
    idx = CARD_INDEX.get(card_name)
    if idx is None:
        return None
    fname = f"{idx:02d}.jpg"
    if (DECK_DIR / fname).exists():
        return f"{PUBLIC_WEB_BASE}/{fname}"
    return None


def deck_completeness() -> dict:
    have = sum(1 for i in range(78) if (DECK_DIR / f"{i:02d}.jpg").exists())
    return {"have": have, "total": 78, "complete": have == 78}
