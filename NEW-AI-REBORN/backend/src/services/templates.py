"""Output templates — ประโยคที่แม่น ชัด มีวันที่ ไม่ปล่อยให้ user เดาเอง.

Rules (from the Research Department spec):
- Every sentence names its evidence: which transit, which dasha, which system.
- Dated where possible; no vague "อาจจะ/อาจมีบางอย่าง".
- Thai and English variants of the same deterministic content.
"""

from __future__ import annotations

from src.services.fusion_engine import DOMAINS

_DOMAIN_TH = {k: v["th"] for k, v in DOMAINS.items()}
_DOMAIN_EN = {k: v["en"] for k, v in DOMAINS.items()}

_POLARITY_TH = {
    "supportive": "หนุน",
    "structuring": "กดเพื่อจัดระเบียบ",
    "activating": "กระตุ้นแรง ต้องระวังพลาด",
}
_POLARITY_EN = {
    "supportive": "supportive for",
    "structuring": "pressuring",
    "activating": "high-activation, watch for friction",
}
_PLANET_TH = {"Sun": "อาทิตย์", "Moon": "จันทร์", "Mercury": "พุธ", "Venus": "ศุกร์",
              "Mars": "อังคาร", "Jupiter": "พฤหัสฯ", "Saturn": "เสาร์", "Uranus": "ยูเรนัส",
              "Neptune": "เนปจูน", "Pluto": "พลูโต", "ASC": "ลัคนา"}
_ASPECT_TH = {"conjunction": "ร่วม (0°)", "sextile": "หกสิบองศา (60°)", "square": "ศอก (90°)",
              "trine": "สามเหลี่ยม (120°)", "opposition": "ตรงข้าม (180°)"}


def _fmt_transit_th(hit: dict) -> str:
    exact = " (เข้าองศาพอดี)" if hit["exact"] else f" (เหลือ {hit['orb_deg']}°)"
    return (f"ดาว{_PLANET_TH[hit['transit_body']]} ทำมุม{_ASPECT_TH[hit['aspect']]} "
            f"กับดาวเกิด{_PLANET_TH[hit['natal_point']]} — "
            f"{_POLARITY_TH[hit['polarity']]}{exact}")


def _fmt_transit_en(hit: dict) -> str:
    exact = " (exact)" if hit["exact"] else f" ({hit['orb_deg']}° orb)"
    return (f"Transiting {hit['transit_body']} {hit['aspect']} natal "
            f"{hit['natal_point']} — {_POLARITY_EN[hit['polarity']]}{exact}")


def render_daily_reading(fused: dict, lang: str = "th") -> dict:
    """Deterministic sentences per life domain + a one-line synthesis."""
    layers = fused["layers"]
    md = layers["vedic"]["vimshottari"]["mahadasha"]["lord"]
    ad = (layers["vedic"]["vimshottari"].get("antardasha") or {}).get("lord")
    clash = layers["thai_bazi"]["chong_clash_this_year"]
    weekday = fused["local_weekday"]

    lines = []
    for dom_key, verdict in fused["verdicts"].items():
        dom_name = _DOMAIN_TH[dom_key] if lang == "th" else _DOMAIN_EN[dom_key]
        top = verdict.get("top_transit")
        if lang == "th":
            head = f"[{dom_name} · {verdict['score']}/100]"
        else:
            head = f"[{dom_name.capitalize()} · {verdict['score']}/100]"
        parts = [head]
        if top:
            parts.append(_fmt_transit_th(top) if lang == "th" else _fmt_transit_en(top))
        if lang == "th":
            parts.append(f"ฉากหลัง: มหาทศา {md}" + (f"-{ad}" if ad and ad != md else ""))
            if clash:
                parts.append("ปีนี้ชงปีเกิด — เรื่องใหญ่ต้องวางแผนล่วงหน้า")
        else:
            parts.append(f"Backdrop: {md} mahadasha" + (f"-{ad}" if ad and ad != md else ""))
            if clash:
                parts.append("Year-clash (Chong) on your birth animal — plan big moves carefully")
        lines.append(" ".join(parts))

    day_lord = layers["thai_bazi"]["day"]["ruling_planet"]
    lucky = layers["thai_bazi"]["day"]["lucky_number"]
    if lang == "th":
        synth = (f"{weekday}: ดาวผู้คุณวันคือ {day_lord} (เลขนำโชค {lucky}). "
                 f"ข้อมูลจาก transit สด + Vimshottari + ตรีวิธี — ไม่ต้องเดาเอง")
    else:
        synth = (f"{weekday}: day ruler {day_lord} (lucky number {lucky}). "
                 f"Fused from live transits + Vimshottari dasha + Triyampathai — no guesswork.")

    return {"synthesis": synth, "domains": lines, "language": lang}
