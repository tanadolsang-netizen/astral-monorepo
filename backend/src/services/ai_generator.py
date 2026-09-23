"""
AI Narrative Generator — สร้าง narrative ต่อบุคคลจริง
"""
from src.services.narrative_engine import ai_generator

def generate_full_reading(chart: dict, user_id: str = "", lang: str = "th") -> dict:
    """สร้าง narrative เต็มรูปแบบต่อบุคคล"""
    return ai_generator.generate_full_reading(chart, user_id, lang)
