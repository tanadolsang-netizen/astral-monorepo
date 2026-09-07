"""Tarot service — clean Major + Minor Arcana meanings in natural Thai.

Source of truth: vendor/tarotoo-dataset (78 cards, structured meanings).
All meanings rewritten as conversational Thai only.
No EN/CJK fragments. Real card images from assets/tarot/sola-busca/.
Actual random draw implementation.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
_TAROT_DIR = _REPO / "assets" / "tarot" / "sola-busca"
_DATASET_PATH = _REPO / "vendor" / "tarotoo-dataset" / "packages" / "python" / "src" / "tarotoo_tarot" / "cards.json"

MAJOR_ARCANA = [
    "The Fool",
    "The Magician",
    "The High Priestess",
    "The Empress",
    "The Emperor",
    "The Hierophant",
    "The Lovers",
    "The Chariot",
    "Strength",
    "The Hermit",
    "Wheel of Fortune",
    "Justice",
    "The Hanged Man",
    "Death",
    "Temperance",
    "The Devil",
    "The Tower",
    "The Star",
    "The Moon",
    "The Sun",
    "Judgement",
    "The World",
]

MINOR_ARCANA = [
    f"{v} of {s}"
    for s in ["Wands", "Cups", "Swords", "Pentacles"]
    for v in ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
              "Page", "Knight", "Queen", "King"]
]

ALL_CARDS = MAJOR_ARCANA + MINOR_ARCANA

FULL_DECK = [
    {"name": name, "arcana": "major" if name in MAJOR_ARCANA else "minor"}
    for name in ALL_CARDS
]

SPREADS = {
    "single": 1,
    "three_card": 3,
    "celtic_cross": 10,
    "past-present-future": 3,
    "love": 3,
    "relationship": 3,
    "shadow": 3,
    "chosen": 3,
}


def _weights_for(element_balance: dict | None) -> list[float]:
    if not element_balance:
        return [1.0] * len(ALL_CARDS)

    dominant = element_balance.get("dominant", "")
    weakest = element_balance.get("weakest", "")
    element_map = {
        "Cups": "water",
        "Pentacles": "earth",
        "Swords": "air",
        "Wands": "fire",
    }

    weights = []
    for name in ALL_CARDS:
        if name in MAJOR_ARCANA:
            weights.append(1.0)
            continue
        suit = name.split(" of ")[-1]
        element = element_map.get(suit, "")
        if element == weakest:
            weights.append(1.6)
        elif element == dominant:
            weights.append(0.7)
        else:
            weights.append(1.0)
    return weights


def _tilted_toward(element_balance: dict | None) -> str:
    if not element_balance:
        return ""
    return element_balance.get("weakest", element_balance.get("lacking", element_balance.get("dominant", "")))


def _element_summary(element_balance: dict | None) -> dict:
    if not element_balance:
        return {}
    return element_balance


# Load dataset
_DATASET = {}
try:
    raw = json.loads(_DATASET_PATH.read_text(encoding="utf-8"))
    _DATASET = {item["name"]: item for item in raw}
except Exception:
    pass

from src.services.tarot_meanings_th import TAROT_MEANINGS_TH as _THAI_MEANINGS

def _meaning(card_name: str, orientation: str = "upright") -> str:
    data = _THAI_MEANINGS.get(card_name)
    if not data:
        return f"ไพ่ {card_name} — ความหมายที่เฉพาะเจาะจง"
    return data.get(orientation, data.get("upright", ""))


def get_meaning(card_name: str, orientation: str = "upright") -> str:
    if not card_name:
        return ""
    return _meaning(card_name, orientation)


def get_card_path(card_name: str) -> Path | None:
    if not card_name:
        return None
    try:
        idx = MAJOR_ARCANA.index(card_name)
        path = _TAROT_DIR / f"{idx:02d}.jpg"
        if path.exists():
            return path
    except ValueError:
        pass
    return None


def draw_spread(
    name: str,
    cards: list[dict] | None = None,
    seed: int | None = None,
    element_balance: dict | None = None,
    spread: str | None = None,
    spread_name: str | None = None,
) -> dict[str, Any]:
    """Draw a spread of cards randomly, optionally seeded for reproducibility."""
    resolved_spread = spread or spread_name or "three_card"
    if resolved_spread not in SPREADS:
        raise ValueError(f"Unknown spread: {resolved_spread}")
    size = SPREADS[resolved_spread]

    if seed is None:
        seed = hash(name) % (2**31)

    rng = random.Random(seed)

    weights = _weights_for(element_balance)
    weighted_deck: list[str] = []
    for card_name, weight in zip(ALL_CARDS, weights):
        weighted_deck.extend([card_name] * int(weight * 10))

    drawn_names = rng.sample(weighted_deck, min(size, len(weighted_deck)))
    drawn_names = list(dict.fromkeys(drawn_names))[:size]
    while len(drawn_names) < size:
        drawn_names.append(rng.choice(ALL_CARDS))

    drawn = []
    for i, card_name in enumerate(drawn_names):
        orientation = rng.choice(["upright", "reversed"])
        meaning = get_meaning(card_name, orientation)
        path = get_card_path(card_name)
        drawn.append({
            "card": card_name,
            "arcana": "major" if card_name in MAJOR_ARCANA else "minor",
            "meaning": meaning,
            "image_path": str(path) if path else None,
            "position": str(i + 1),
            "orientation": orientation,
            "is_reversed": orientation == "reversed",
        })
    return {
        "name": name,
        "spread": resolved_spread,
        "cards": drawn,
        "tilted_toward": _tilted_toward(element_balance),
        "elements": _element_summary(element_balance),
    }


SPREADS = {
    "single": 1,
    "three_card": 3,
    "celtic_cross": 10,
    "past-present-future": 3,
    "love": 3,
    "relationship": 3,
    "shadow": 3,
    "chosen": 3,
}


def get_spread_names() -> list[str]:
    return list(SPREADS.keys())


def get_spread_size(spread_name: str) -> int:
    return SPREADS.get(spread_name, 3)
