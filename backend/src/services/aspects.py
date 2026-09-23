"""Cross-aspect calculation between two computed charts."""

ASPECTS: dict[str, float] = {
    "conjunction": 0.0,
    "sextile": 60.0,
    "square": 90.0,
    "trine": 120.0,
    "opposition": 180.0,
}

# Traditional orb allowances by aspect type (degrees). Spaced narrowly enough
# relative to the gaps between aspect angles (60/90/120/180) that a given body
# pair's separation can only fall inside one aspect's window at a time.
ORBS: dict[str, float] = {
    "conjunction": 8.0,
    "opposition": 8.0,
    "trine": 8.0,
    "square": 7.0,
    "sextile": 6.0,
}

# Approximate mean daily motion (deg/day). Synastry compares two fixed birth
# moments rather than live transits, so "applying" here is a heuristic: it
# projects each body forward along its typical direction of travel and checks
# whether the aspect would tighten, not a real-time transit calculation.
MEAN_DAILY_MOTION: dict[str, float] = {
    "Sun": 0.9856,
    "Moon": 13.176,
    "Mercury": 1.383,
    "Venus": 1.2,
    "Mars": 0.524,
    "Jupiter": 0.083,
    "Saturn": 0.034,
    "Uranus": 0.012,
    "Neptune": 0.006,
    "Pluto": 0.004,
}


def _angular_sep(a: float, b: float) -> float:
    diff = abs(a - b) % 360
    return diff if diff <= 180 else 360 - diff


def _is_applying(body_a: dict, body_b: dict, aspect_angle: float, sep: float) -> bool:
    eps_days = 1.0
    motion_a = MEAN_DAILY_MOTION.get(body_a["body"], 0.5)
    motion_b = MEAN_DAILY_MOTION.get(body_b["body"], 0.5)
    future_a = (body_a["absolute_deg"] + motion_a * eps_days) % 360
    future_b = (body_b["absolute_deg"] + motion_b * eps_days) % 360
    future_sep = _angular_sep(future_a, future_b)
    # bool(...): the inputs are numpy.float64 (from Skyfield), whose
    # comparisons yield numpy.bool_ — not JSON-serializable by FastAPI.
    return bool(abs(future_sep - aspect_angle) < abs(sep - aspect_angle))


def compute_cross_aspects(chart_a: dict, chart_b: dict) -> list[dict]:
    results = []
    for body_a in chart_a["bodies"]:
        for body_b in chart_b["bodies"]:
            sep = _angular_sep(body_a["absolute_deg"], body_b["absolute_deg"])
            for aspect_name, aspect_angle in ASPECTS.items():
                orb = abs(sep - aspect_angle)
                if orb <= ORBS[aspect_name]:
                    results.append({
                        "body_a": body_a["body"],
                        "body_b": body_b["body"],
                        "aspect": aspect_name,
                        "orb": round(orb, 2),
                        "applying": _is_applying(body_a, body_b, aspect_angle, sep),
                    })
                    break
    results.sort(key=lambda r: r["orb"])
    return results
