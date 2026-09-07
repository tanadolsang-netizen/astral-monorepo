"""
Vedic Yoga Narrative Service — generates yoga readings.
"""
from __future__ import annotations
from .narrative_engine import generate_yoga_narrative
from .kb_loader import get_yoga_meanings


def generate_yoga_reading(yoga_data: dict, lang: str = "th") -> dict:
    """Generate a Vedic Yoga reading."""
    return generate_yoga_narrative(yoga_data, lang)


def generate_raja_yoga_reading(yoga_data: dict, lang: str = "th") -> dict:
    """Generate Raja Yoga-specific reading."""
    kb = get_yoga_meanings()
    raja = kb.get("Raja Yoga", {})
    
    if lang == "th":
        return {
            "raja_yoga": f"ราชาโยคะ — {raja.get('condition', '')} → {raja.get('meaning_th', '')}",
        }
    else:
        return {
            "raja_yoga": f"Raja Yoga — {raja.get('condition', '')} → {raja.get('meaning_en', '')}",
        }
