"""Language gate — purity policy for Thai-only text.

 upgraded to a soft threshold so the suite can grow with the meanings.
"""
from __future__ import annotations

import re
import pytest

from src.services.tarot_service import _THAI_MEANINGS
from src.services.tarot_meanings_th import TAROT_MEANINGS_TH

# Characters we never want inside Thai strings
_BANNED_RE = re.compile(
    r"[\u3000-\u9FFF"   # CJK
    r"\uAC00-\uD7AF"    # Hangul
    r"\u0400-\u04FF"    # Cyrillic
    r"\u0080-\u00FF"    # Latin-1 supplement
    r"]"
)

# Known safe Thai fragments/prefixes that may appear before dataset text
_SAFE_PREFIXES = ("ไพ่", "เรื่อง", "→")


def _purity(text: str) -> float:
    if not text.strip():
        return 1.0
    chars = list(text)
    banned = sum(1 for ch in chars if _BANNED_RE.search(ch) is not None)
    return 1.0 - banned / len(chars)


def _failures_for(text: str, label: str) -> list[str]:
    hits = _BANNED_RE.findall(text)
    return [f"{label}: {ch!r}" for ch in hits]


@pytest.mark.parametrize("card_name,meaning_map", list(_THAI_MEANINGS.items()))
def test_inline_meanings_threshold(card_name, meaning_map):
    for orientation, text in meaning_map.items():
        p = _purity(text)
        label = f"_THAI_MEANINGS[{card_name!r}][{orientation!r}]"
        assert p >= 1.0, _failures_for(text, label) + [f"purity={p:.2f}"]


@pytest.mark.parametrize("card_name,meaning_map", list(TAROT_MEANINGS_TH.items()))
def test_module_meanings_threshold(card_name, meaning_map):
    for orientation, text in meaning_map.items():
        p = _purity(text)
        label = f"TAROT_MEANINGS_TH[{card_name!r}][{orientation!r}]"
        assert p >= 1.0, _failures_for(text, label) + [f"purity={p:.2f}"]


def test_all_78_cards_present_in_module():
    assert len(TAROT_MEANINGS_TH) == 78, f"Expected 78 cards, got {len(TAROT_MEANINGS_TH)}"
    for card_name in _THAI_MEANINGS:
        assert card_name in TAROT_MEANINGS_TH, f"Missing card in module: {card_name!r}"
