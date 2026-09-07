"""
Ziwei Narrative Service — generates Ziwei Dou Shu readings.
"""
from __future__ import annotations
from .narrative_engine import generate_ziwei_narrative
from .kb_loader import get_ziwei_meanings


def generate_ziwei_reading(ziwei_data: dict, lang: str = "th") -> dict:
    """Generate a Ziwei Dou Shu reading."""
    return generate_ziwei_narrative(ziwei_data, lang)


def generate_palace_focus(ziwei_data: dict, palace_name: str, lang: str = "th") -> dict:
    """Generate focus on a specific palace."""
    kb = get_ziwei_meanings()
    meaning = kb.get(palace_name, {})
    
    if lang == "th":
        return {
            "palace": palace_name,
            "focus": meaning.get("th", palace_name),
            "advice": f"ดูแลเรื่อง{meaning.get('th', palace_name)}ให้ดี",
        }
    else:
        return {
            "palace": palace_name,
            "focus": meaning.get("meaning_en", palace_name),
            "advice": f"Take care of {palace_name} matters",
        }
