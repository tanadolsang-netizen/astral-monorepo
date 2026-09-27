"""Shared narrative sanitizer — strips CJK/Cyrillic/Greek artifacts and empty-token noise.

Used as a final safety net after the TH/EN builders so no garbled or
wrong-script leftovers ever reach the rendered PDF.
"""

from __future__ import annotations

import re

# Scripts that never belong in a TH or EN narrative — leftover LLM artifacts.
_STRAY_SCRIPTS = re.compile(
    "["
    "一-鿿"  # CJK unified ideographs
    "぀-ヿ"  # hiragana / katakana
    "가-힣"  # hangul
    "Ѐ-ӿ"  # cyrillic
    "Ͱ-Ͽ"  # greek
    "]"
)

# Known garbled/mixed-in tokens seen from earlier generations.
_ARTIFACT_WORDS = [
    "Axami", "Kps", "oportun", " Kritikal", "wajik indian",
    "cuatro palos", "etalon", "rutin", "cross-reference",
]

_FULLWIDTH_PARENS = str.maketrans({"（": "(", "）": ")"})


def sanitize_narrative(text: str, lang: str = "th") -> str:
    """Strip stray scripts, known artifacts, and empty-token noise from a narrative string."""
    if not text:
        return text
    text = _STRAY_SCRIPTS.sub("", text)
    for art in _ARTIFACT_WORDS:
        text = text.replace(art, "")
    text = text.translate(_FULLWIDTH_PARENS)
    text = re.sub(r"\(\s*\)", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return text.strip()
