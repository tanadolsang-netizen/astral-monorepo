"""Composite (midpoint) chart and relationship score.

The composite chart is a purely geometric construct: for each body shared
by two natal charts, the composite position is the circular midpoint of
the two ecliptic longitudes.  No ephemeris call is needed — the source
charts must already be computed via chart_service.compute_chart().

The relationship score is a 0-100 heuristic blending cross-aspect quality
and elemental compatibility between two charts.
"""

from src.services.chart_service import _to_sign, BODIES
from src.services.aspects import compute_cross_aspects, ASPECTS
from src.services.element_service import compute_element_balance, SIGN_ELEMENT


def circular_midpoint(lon_a: float, lon_b: float) -> float:
    """Circular midpoint of two ecliptic longitudes on a 360-degree circle.

    Returns the degree on the shorter arc halfway between *lon_a* and *lon_b*,
    wrapped into [0, 360).
    """
    diff = (lon_b - lon_a) % 360
    if diff > 180:
        diff -= 360
    return (lon_a + diff / 2) % 360


def compute_composite(chart_a: dict, chart_b: dict) -> dict:
    """Build a composite (midpoint) chart from two natal charts.

    For every planet present in both charts the composite longitude is the
    circular midpoint of the two absolute degrees.  Sign and degree-within-
    sign are derived from the composite longitude using chart_service._to_sign().

    Element balance is computed via element_service.compute_element_balance().

    Houses are omitted because a geometric composite has no time/place of
    birth and therefore no meaningful house system.
    """
    bmap_a = {b["body"]: b for b in chart_a.get("bodies", [])}
    bmap_b = {b["body"]: b for b in chart_b.get("bodies", [])}

    bodies = []
    for body_name in BODIES:
        if body_name not in bmap_a or body_name not in bmap_b:
            continue
        comp_lon = circular_midpoint(
            bmap_a[body_name]["absolute_deg"],
            bmap_b[body_name]["absolute_deg"],
        )
        sign, deg = _to_sign(comp_lon)
        bodies.append({
            "body": body_name,
            "sign": sign,
            "degree": round(deg, 4),
            "absolute_deg": round(comp_lon, 4),
        })

    composite_chart = {
        "name": f"{chart_a.get('name', 'A')} & {chart_b.get('name', 'B')}",
        "system": chart_a.get("system", "tropical"),
        "bodies": bodies,
    }
    composite_chart["elements"] = compute_element_balance(composite_chart)

    return composite_chart


# ---------------------------------------------------------------------------
# Relationship score (0-100)
# ---------------------------------------------------------------------------

_ASPECT_SCORE: dict[str, float] = {
    "conjunction": 3.0,
    "trine": 3.0,
    "sextile": 1.0,
    "square": -3.0,
    "opposition": -3.0,
}

_COMPAT: dict[tuple[str, str], float] = {
    ("fire", "air"): 1.0,  ("air", "fire"): 1.0,
    ("earth", "water"): 1.0,  ("water", "earth"): 1.0,
    ("fire", "fire"): 0.7,  ("earth", "earth"): 0.7,
    ("air", "air"): 0.7,  ("water", "water"): 0.7,
    ("fire", "earth"): 0.3,  ("earth", "fire"): 0.3,
    ("fire", "water"): 0.2,  ("water", "fire"): 0.2,
    ("air", "earth"): 0.3,  ("earth", "air"): 0.3,
    ("air", "water"): 0.3,  ("water", "air"): 0.3,
}


def _aspect_score(cross_aspects: list[dict]) -> float:
    total = 0.0
    for a in cross_aspects:
        total += _ASPECT_SCORE.get(a["aspect"], 0.0)
    return total


def _element_compatibility(elements_a: dict, elements_b: dict) -> float:
    dom_a = elements_a.get("dominant", "fire")
    dom_b = elements_b.get("dominant", "fire")
    return _COMPAT.get((dom_a, dom_b), 0.5)


def _element_variety(elements_a: dict, elements_b: dict) -> float:
    pa = elements_a.get("percent", {})
    pb = elements_b.get("percent", {})
    all_vals = list(pa.values()) + list(pb.values())
    if not all_vals:
        return 0.0
    spread = max(all_vals) - min(all_vals)
    return 1.0 if spread < 20 else 0.0


def compute_relationship_score(chart_a: dict, chart_b: dict) -> dict:
    """Compute a 0-100 relationship score from two natal charts.

    The score is a weighted blend of:
    - Cross-aspect quality (conjunctions/trines positive, squares/oppositions
      negative, sextiles mildly positive)
    - Elemental compatibility (complementary elements score higher)
    - Bonus for elemental balance and variety
    """
    cross = compute_cross_aspects(chart_a, chart_b)
    elements_a = compute_element_balance(chart_a)
    elements_b = compute_element_balance(chart_b)

    raw = (
        _aspect_score(cross)
        + 15.0 * _element_compatibility(elements_a, elements_b)
        + 5.0 * _element_variety(elements_a, elements_b)
    )
    score = int(max(0, min(100, round(raw + 50))))

    pos = sum(1 for a in cross if _ASPECT_SCORE.get(a["aspect"], 0) > 0)
    chg = sum(1 for a in cross if _ASPECT_SCORE.get(a["aspect"], 0) < 0)

    note = (
        f"คะแนนความสัมพันธ์: {score}/100 — "
        f"มี aspect เชิงบวก {pos} ด้าน, "
        f"aspect ที่ท้าทาย {chg} ด้าน, "
        f"ธาตุเด่นของ A คือ{elements_a['dominant']} "
        f"และของ B คือ{elements_b['dominant']}"
    )

    return {
        "score": score,
        "cross_aspects": cross,
        "elements_a": elements_a,
        "elements_b": elements_b,
        "note": note,
        "caveat": "เพื่อการไตร่ตรองและความบันเทิงเท่านั้น "
                   "ไม่ใช่คำแนะนำทางการแพทย์ กฎหมาย หรือการเงิน "
                   "/ For reflection and entertainment; not medical, legal, or financial advice.",
    }
