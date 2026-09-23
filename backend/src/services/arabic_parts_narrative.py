"""
Arabic Parts Narrative Service — generates Arabic Parts readings.
"""
from __future__ import annotations
from .narrative_engine import generate_arabic_parts_narrative
from .kb_loader import get_arabic_parts_meanings


def generate_arabic_parts_reading(parts_data: dict, lang: str = "th") -> dict:
    """Generate an Arabic Parts reading."""
    return generate_arabic_parts_narrative(parts_data, lang)


def generate_part_of_fortune_reading(parts_data: dict, lang: str = "th") -> dict:
    """Generate Part of Fortune-specific reading."""
    kb = get_arabic_parts_meanings()
    pof = kb.get("Part of Fortune", {})
    
    if lang == "th":
        return {
            "part_of_fortune": f"อาภรณ์ — {pof.get('formula', '')} → {pof.get('meaning_th', '')}",
        }
    else:
        return {
            "part_of_fortune": f"Part of Fortune — {pof.get('formula', '')} → {pof.get('meaning_en', '')}",
        }
