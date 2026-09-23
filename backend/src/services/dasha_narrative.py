"""
Dasha Narrative Service — generates Vedic Dasha readings.
"""
from __future__ import annotations
from .narrative_engine import generate_dasha_narrative
from .kb_loader import get_dasha_meanings


def generate_dasha_reading(dasha_data: dict, lang: str = "th") -> dict:
    """Generate a Dasha reading."""
    return generate_dasha_narrative(dasha_data, lang)


def generate_antardasha_reading(dasha_data: dict, mahadasha: str, antardasha: str, lang: str = "th") -> dict:
    """Generate Antardasha-specific reading."""
    kb = get_dasha_meanings()
    md = kb.get(mahadasha, {})
    ad = kb.get(antardasha, {})
    
    if lang == "th":
        return {
            "mahadasha": f"มหาฑาชา {md.get('th', mahadasha)} ({md.get('period_years', '?')} ปี)",
            "antardasha": f"อันตราฑาชา {ad.get('th', antardasha)}",
        }
    else:
        return {
            "mahadasha": f"Mahadasha {md.get('th', mahadasha)} ({md.get('period_years', '?')} years)",
            "antardasha": f"Antardasha {ad.get('th', antardasha)}",
        }
