"""
Fixed Star Narrative Service — generates fixed star readings.
"""
from __future__ import annotations
from .narrative_engine import generate_fixed_star_narrative
from .kb_loader import get_fixed_star_meanings


def generate_fixed_star_reading(fixed_star_data: dict, lang: str = "th") -> dict:
    """Generate a fixed star reading."""
    return generate_fixed_star_narrative(fixed_star_data, lang)


def generate_sabian_reading(sabian_data: dict, lang: str = "th") -> dict:
    """Generate Sabian symbol reading."""
    if lang == "th":
        return {
            "sun": sabian_data.get("sun", {}).get("phrase_th", ""),
            "moon": sabian_data.get("moon", {}).get("phrase_th", ""),
            "asc": sabian_data.get("asc", {}).get("phrase_th", ""),
        }
    else:
        return {
            "sun": sabian_data.get("sun", {}).get("phrase_en", ""),
            "moon": sabian_data.get("moon", {}).get("phrase_en", ""),
            "asc": sabian_data.get("asc", {}).get("phrase_en", ""),
        }
