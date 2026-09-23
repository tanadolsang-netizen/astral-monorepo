"""
Varshaphal (Annual) Narrative Service — generates yearly readings.
"""
from __future__ import annotations
from .narrative_engine import generate_varshaphal_narrative
from .kb_loader import get_varshaphal_meanings


def generate_annual_reading(varshaphal_data: dict, lang: str = "th") -> dict:
    """Generate an annual Varshaphal reading."""
    return generate_varshaphal_narrative(varshaphal_data, lang)


def generate_monthly_focus(varshaphal_data: dict, month: int, lang: str = "th") -> dict:
    """Generate monthly focus from Varshaphal data."""
    kb = get_varshaphal_meanings()
    muntha = varshaphal_data.get("muntha", {})
    
    if lang == "th":
        return {
            "month": month,
            "focus": f"เดือนนี้โฟกัสที่ {muntha.get('sign', '?')}",
            "advice": "ระวังเรื่องการเงินและสุขภาพ",
        }
    else:
        return {
            "month": month,
            "focus": f"This month focuses on {muntha.get('sign', '?')}",
            "advice": "Be cautious with finances and health",
        }
