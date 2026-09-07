"""
Asteroid Narrative Service — generates asteroid readings.
"""
from __future__ import annotations
from .narrative_engine import generate_asteroid_narrative
from .kb_loader import get_asteroid_meanings


def generate_asteroid_reading(asteroid_data: dict, lang: str = "th") -> dict:
    """Generate an asteroid reading."""
    return generate_asteroid_narrative(asteroid_data, lang)


def generate_chiron_reading(asteroid_data: dict, lang: str = "th") -> dict:
    """Generate Chiron-specific reading."""
    kb = get_asteroid_meanings()
    chiron = asteroid_data.get("positions", {}).get("Chiron", {})
    meaning = kb.get("Chiron", {})
    
    if lang == "th":
        return {
            "chiron": f"ไครอนที่ {chiron.get('absolute_deg', 0):.1f}° — {meaning.get('th', 'บาดแผลและการรักษา')}",
        }
    else:
        return {
            "chiron": f"Chiron at {chiron.get('absolute_deg', 0):.1f}° — {meaning.get('meaning_en', 'Wounds and healing')}",
        }
