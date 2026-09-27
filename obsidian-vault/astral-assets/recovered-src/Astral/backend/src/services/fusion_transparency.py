"""Fusion transparency — auditable evidence for fuse_daily verdicts.

Wraps the existing fusion_engine without refactoring it: replays the same
per-domain scoring with full evidence exposure and theoretical-max
normalization so every score is explainable.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

from src.services.chart_service import compute_chart
from src.services.fusion_engine import (
    DOMAINS, compute_transit_hits, sidereal_moon_lon,
    vimshottari_now, bazi_year_pillars, thai_day_context, fuse_daily,
)


def _norm(raw: float, max_possible: float) -> int:
    """Theoretical-max normalization → 0-100 integer."""
    if max_possible <= 0:
        return 50
    return round(max(0.0, min(100.0, raw / max_possible * 100)))


def compute_fusion_evidence(natal: dict, *, lat: float, lon: float,
                            tz_offset_hours: float = 7.0,
                            now_utc: datetime | None = None) -> dict:
    """Replay fusion scoring exposing per-engine evidence."""
    now_utc = now_utc or datetime.now(timezone.utc)
    now_local_tz = timezone(timedelta(hours=tz_offset_hours))
    now_local = now_utc.astimezone(now_local_tz)

    chart_trop = compute_chart(
        name=natal["name"], date=natal["date"], time=natal["time"],
        tz_offset_hours=tz_offset_hours, lat=lat, lon=lon, system="tropical")
    hits = compute_transit_hits(chart_trop, now_utc)

    dt_utc_birth = datetime.combine(natal["date"], natal["time"],
                                    tzinfo=timezone.utc) - timedelta(hours=tz_offset_hours)
    moon_sid_birth = sidereal_moon_lon(dt_utc_birth)
    yf_birth = dt_utc_birth.year + dt_utc_birth.timetuple().tm_yday / 365.2425
    yf_now = now_utc.year + now_utc.timetuple().tm_yday / 365.2425
    dasha = vimshottari_now(moon_sid_birth, yf_birth, yf_now)

    # per-domain evidence: mirror fuse_daily scoring exactly, but expose parts
    evidence = []
    for dom, spec in DOMAINS.items():
        dom_hits = [h for h in hits if dom in h["domains"]]
        raw = sum((10 if h["polarity"] != "structuring" else -6)
                  * (1 - h["orb_deg"] / 6) * (h["weight"] / 9)
                  for h in dom_hits[:4])
        dasha_bonus = 0
        if dasha["mahadasha"]["lord"] in ("Jupiter", "Venus"):
            dasha_bonus = 4
        elif dasha["mahadasha"]["lord"] == "Saturn":
            dasha_bonus = -3
        fired = [
            {"transit": f"{h['transit_body']} {h['aspect']} {h['natal_point']}",
             "orb_deg": h["orb_deg"], "polarity": h["polarity"]}
            for h in dom_hits[:4]
        ]
        if dasha_bonus:
            fired.append({"transit": f"dasha lord {dasha['mahadasha']['lord']}",
                          "orb_deg": 0, "polarity":
                          "supportive" if dasha_bonus > 0 else "structuring"})
        # theoretical max: 4 hits × +10 each + dasha bonus cap 4
        score_clamped = max(5, min(95, round(50 + raw + dasha_bonus)))
        max_possible = 40 + 4
        evidence.append({
            "domain": dom,
            "label_th": spec.get("th", dom),
            "label_en": spec.get("en", dom),
            "score_raw": round(50 + raw + dasha_bonus, 2),
            "score_clamped": score_clamped,
            "normalized": _norm(score_clamped, 95),
            "max_possible_normalized_base": 50 + max_possible,
            "hits_count": len(dom_hits),
            "fired_reasons": fired,
            "weight_used": [h["weight"] for h in dom_hits[:4]],
        })

    overall_raw = sum(e["score_raw"] for e in evidence) / len(evidence) \
        if evidence else 50

    return {
        "system": "fusion-transparency",
        "as_of": now_utc.isoformat(),
        "engines_fired": sorted({r["transit"].split()[0]
                                 for e in evidence for r in e["fired_reasons"]}),
        "dasha_lord": dasha["mahadasha"]["lord"],
        "domains": evidence,
        "overall_normalized": _norm(overall_raw, 94),
        "method_note_en": ("Scores are normalized against a fixed theoretical "
                           "maximum (4 strongest hits × weight + dasha bonus), "
                           "so readings are comparable across days."),
        "method_note_th": ("คะแนน normalize กับค่าสูงสุดตายตัว "
                           "(4 transit แรงสุด + โบนัสดาชา) "
                           "ทำให้เทียบวันต่อวันได้ยุติธรรม"),
    }
