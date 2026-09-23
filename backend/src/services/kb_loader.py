"""
Knowledge base loader — reads JSON files from knowledge/ directory.
"""
from pathlib import Path
import json

_KB_DIR = Path(__file__).resolve().parent / "knowledge"

def _load(name: str) -> dict:
    path = _KB_DIR / f"{name}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def get_sign_traits() -> dict:
    return _load("sign_traits")

def get_aspect_meanings() -> dict:
    return _load("aspect_meanings")

def get_house_placements() -> dict:
    return _load("house_placements")

def get_dignity_meanings() -> dict:
    return _load("dignity_meanings")

def get_transit_aspects() -> dict:
    return _load("transit_aspects")

def get_synastry_aspects() -> dict:
    return _load("synastry_aspects")

def get_nakshatra_meanings() -> dict:
    return _load("nakshatra_meanings")

def get_dasha_meanings() -> dict:
    return _load("dasha_meanings")

def get_yoga_meanings() -> dict:
    return _load("yoga_meanings")

def get_arabic_parts_meanings() -> dict:
    return _load("arabic_parts_meanings")

def get_ziwei_meanings() -> dict:
    return _load("ziwei_meanings")

def get_varshaphal_meanings() -> dict:
    return _load("varshaphal_meanings")

def get_fixed_star_meanings() -> dict:
    return _load("fixed_star_meanings")

def get_asteroid_meanings() -> dict:
    return _load("asteroid_meanings")

def get_thai_idioms() -> dict:
    return _load("thai_idioms")

def get_transit_th_templates() -> dict:
    return _load("transit_th_templates")

def get_synastry_th_templates() -> dict:
    return _load("synastry_th_templates")

def get_depth_psychology() -> dict:
    return _load("depth_psychology")

def get_complexes() -> dict:
    return _load("complexes")
