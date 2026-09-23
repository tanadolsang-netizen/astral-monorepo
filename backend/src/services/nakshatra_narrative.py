"""
Nakshatra Narrative Service — generates Vedic Nakshatra readings.
"""
from __future__ import annotations
from .narrative_engine import generate_nakshatra_narrative
from .kb_loader import get_nakshatra_meanings


def generate_nakshatra_reading(nakshatra_data: dict, lang: str = "th") -> dict:
    """Generate a Nakshatra reading."""
    return generate_nakshatra_narrative(nakshatra_data, lang)


def generate_moon_nakshatra_reading(nakshatra_data: dict, lang: str = "th") -> dict:
    """Generate Moon Nakshatra-specific reading."""
    kb = get_nakshatra_meanings()
    moon_nak = nakshatra_data.get("moon", {})
    meaning = kb.get(moon_nak.get("name", ""), {})
    
    if lang == "th":
        return {
            "moon_nakshatra": f"จันทร์ในนักษัตร {meaning.get('th', '?')} — ปกครองโดย {meaning.get('ruler_th', '?')}",
        }
    else:
        return {
            "moon_nakshatra": f"Moon in Nakshatra {meaning.get('th', '?')} — ruled by {meaning.get('ruler', '?')}",
        }
