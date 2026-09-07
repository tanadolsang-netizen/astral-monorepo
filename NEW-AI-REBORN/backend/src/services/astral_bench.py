"""Astral-Bench — evaluate LLM interpretation against engine-computed facts.

Inspired by arXiv 2510.23337 (BaZi character-simulation benchmark):
the LLM must NOT contradict computed placements, and should reference
a minimum number of them. Deterministic scoring; offline.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from src.services.chart_service import compute_chart

_SIGNS_EN = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]


@dataclass
class BenchCase:
    name: str
    date: str          # YYYY-MM-DD
    time: str          # HH:MM
    lat: float
    lon: float
    tz: float = 7.0


def ground_truth(case: BenchCase) -> dict:
    """Facts the LLM must not contradict."""
    from datetime import datetime as _dt, timedelta as _td
    local = _dt.fromisoformat(f"{case.date}T{case.time}:00")
    utc = local - _td(hours=case.tz)
    c = compute_chart("bench", utc.date(), utc.time(), tz_offset_hours=0,
                      lat=case.lat, lon=case.lon)
    bodies = {b["body"]: b for b in c["bodies"]}
    sun = bodies["Sun"]
    moon = bodies["Moon"]
    asc = c["ascendant"]

    def sign_of(abs_deg: float) -> str:
        return _SIGNS_EN[int(abs_deg // 30) % 12]

    return {
        "sun_sign": sign_of(float(sun["absolute_deg"])),
        "moon_sign": sign_of(float(moon["absolute_deg"])),
        "asc_sign": sign_of(float(asc["absolute_deg"])),
        "sun_degree": round(float(sun["absolute_deg"]) % 30, 1),
        "moon_degree": round(float(moon["absolute_deg"]) % 30, 1),
        "planets": {b: sign_of(float(v["absolute_deg"]))
                    for b, v in bodies.items()},
    }


def score_interpretation(truth: dict, text: str) -> dict:
    """Score an LLM reading against ground truth. 0-100.

    Penalties:
      - contradicts a placement mentioned with a wrong sign  (-20 each)
    Rewards:
      - correctly references Sun/Moon/ASC signs             (+15 each)
      - references >=4 planets correctly                    (+10)
      - uses specific degrees                               (+5)
      - mentions houses or nakshatra                        (+5)
    """
    text_l = text.lower()
    checks = []
    total = 50.0

    def mentioned(planet_key: str) -> bool:
        names = {"sun": ["sun", "ดวงอาทิตย์", "อาทิตย์"],
                 "moon": ["moon", "จันทร์", "ดวงจันทร์"],
                 "asc": ["ascendant", "rising", "ลัคนา", "asc"]}
        return any(k in text_l for k in names[planet_key])

    for key in ("sun", "moon", "asc"):
        truth_sign = truth[f"{key}_sign"].lower()
        if not mentioned(key):
            checks.append({"check": f"{key} referenced", "ok": None})
            continue
        # find sign words near mention; contradiction = different zodiac word present
        signs_present = [s for s in _SIGNS_EN if s.lower() in text_l]
        thai_zodiac = {"เมษ": "aries", "พฤษภ": "taurus", "เมถุน": "gemini",
                       "กรกฎ": "cancer", "สิงห์": "leo", "กันย์": "virgo",
                       "ตุลย์": "libra", "พิจิก": "scorpio", "ธนู": "sagittarius",
                       "มกร": "capricorn", "กุมภ์": "aquarius", "มีน": "pisces"}
        for th, en in thai_zodiac.items():
            if th in text:
                signs_present.append(en)
        signs_present = set(signs_present)
        correct = truth_sign in signs_present and len(signs_present & (
            {truth[f"sun_sign"].lower(), truth[f"moon_sign"].lower(),
             truth["asc_sign"].lower()} - {truth_sign})) == 0
        # simpler: ok if true sign appears; contradiction if another of the big-3 signs appears instead
        if truth_sign in text_l or any(
                t in text for t in [k for k, v in thai_zodiac.items()
                                    if v == truth_sign]):
            total += 15
            checks.append({"check": f"{key}={truth_sign} correct", "ok": True})
        else:
            other_big3 = ({truth["sun_sign"], truth["moon_sign"],
                           truth["asc_sign"]} - {truth_sign.capitalize()})
            if any(o.lower() in text_l for o in other_big3):
                total -= 20
                checks.append({"check": f"{key} CONTRADICTED", "ok": False})
            else:
                checks.append({"check": f"{key} sign not stated", "ok": None})

    planet_correct = sum(1 for p, s in truth["planets"].items()
                         if s.lower() in text_l)
    if planet_correct >= 4:
        total += 10
    checks.append({"check": f"planets correctly cited: {planet_correct}",
                   "ok": planet_correct >= 4})

    if re.search(r"\d+\.\d+°|\d+°\d+", text):
        total += 5
        checks.append({"check": "uses exact degrees", "ok": True})

    if re.search(r"house|บ้าน|นักษัตร|nakshatra", text_l):
        total += 5
        checks.append({"check": "houses/nakshatra mentioned", "ok": True})

    return {"score": max(0, min(100, round(total))), "checks": checks}


def run_bench(cases: list[BenchCase], interpret_fn=None) -> dict:
    """Run all cases through interpret_fn(truth, case)->str and score.

    Without an LLM configured, runs self-consistency mode: verifies the
    engine facts are stable across two calls (regression guard).
    """
    results = []
    for case in cases:
        gt = ground_truth(case)
        entry = {"case": case.name, "ground_truth": {
            k: v for k, v in gt.items() if k != "planets"}}
        if interpret_fn is not None:
            reading = interpret_fn(gt, case)
            entry.update(score_interpretation(gt, reading))
        else:
            # regression mode: recompute twice, assert stable
            gt2 = ground_truth(case)
            stable = gt == gt2
            entry.update({"score": 100 if stable else 0,
                          "stable_recompute": stable,
                          "checks": [{"check": "engine determinism", "ok": stable}]})
        results.append(entry)

    scores = [r["score"] for r in results]
    return {
        "system": "astral-bench",
        "cases": len(results),
        "mean_score": round(sum(scores) / max(len(scores), 1), 1),
        "results": results,
        "interpretation": {
            "th": f"Bench {len(results)} เคส — คะแนนเฉลี่ย "
                  f"{round(sum(scores)/max(len(scores),1),1)}/100",
            "en": f"Astral-Bench mean {round(sum(scores)/max(len(scores),1),1)}"
                  f"/100 over {len(results)} cases.",
        },
    }
