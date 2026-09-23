"""Spec 03 §2 synastry scoring — six dimensions 0-100 from real cross-aspects.

Weighted table (spec 03 §2, sums to 100):

    Venus-Mars 14 · Sun-Moon 12 · Sun-Venus 10 · Moon-Venus 10 ·
    Venus-Saturn 9 · Moon-Mars 8 · Sun-Saturn 7 · Jupiter contacts 8 ·
    outer-contacts 6 · house-overlay(7th) 10 · nodal 6

score_pair = W[kind] x harmonic x (1 - orb/max_orb)   [linear decay]

max_orb comes from spec 01 §1 per planet; a pair uses the stricter (min)
of its two bodies.  The spec's linear decay carries no harmonic term, so an
exact opposition would outscore nothing-but-squares equally with conjunctions;
the engine therefore multiplies by HARMONIC (conj 1.0 / trine 0.9 / sextile 0.7 /
square 0.35 / opposition 0.25) so bonds outrank frictions at equal orb.
Documented deviation #2: spec omits Mercury from the table while listing the
communication dimension — Mercury contacts use weight 10 (personal partner)
or 6 (Saturn/Jupiter partner); ASC contacts score half their partner's kind.
Each dimension normalizes against its nominal capacity, clamped to 100.

Karmic pull (spec 03 §4): nodal contact = any body of either side conj/opposed
to the OTHER side's mean node within 5 deg.  Mean node via Meeus' polynomial
(reproduces the verified M NN Virgo 25.75 for 1997-05-19).  With no nodal
contact the engine falls back to the DK cross-check (spec 02 section 6):
Darakaraka = lowest sidereal degree-within-sign among Sun..Saturn; a luminary
DK meeting a Sun-conj-Moon partner signature confirms the archetype
(regression case: DK(M)=Sun <-> Mai double-Leo).
"""

from __future__ import annotations

from datetime import datetime

from src.services.aspects import ASPECTS, ORBS, _angular_sep
from src.services.chart_service import SIGNS, SIGNS_TH_DISPLAY, lahiri_ayanamsa

# Build lookup that maps both English and Thai(English) → index
_SIGN_INDEX = {}
for i, s in enumerate(SIGNS):
    _SIGN_INDEX[s] = i
for i, s in enumerate(SIGNS_TH_DISPLAY):
    _SIGN_INDEX[s] = i

# spec 01 §1
MAX_ORB = {
    "Sun": 8, "Moon": 8, "Mercury": 6, "Venus": 6, "Mars": 6,
    "Jupiter": 6, "Saturn": 6, "Uranus": 4, "Neptune": 4, "Pluto": 4,
    "ASC": 6,
}

# spec 03 §2
W = {
    "Venus-Mars": 14,
    "Sun-Moon": 12,
    "Sun-Venus": 10,
    "Moon-Venus": 10,
    "Venus-Saturn": 9,
    "Moon-Mars": 8,
    "Sun-Saturn": 7,
    "Jupiter contacts": 8,
    "outer-contacts": 6,
    "house-overlay(7th)": 10,
    "nodal": 6,
}

HARMONIC = {
    "conjunction": 1.0,
    "trine": 0.9,
    "sextile": 0.7,
    "square": 0.35,
    "opposition": 0.25,
}

DIMENSIONS = (
    "chemistry",
    "emotional_bond",
    "stability",
    "communication",
    "growth",
    "karmic_pull",
)

# Nominal capacities used to normalize each dimension to 0-100.
CAPACITY = {
    "chemistry": 24,        # Venus-Mars 14 + Sun-Venus 10 (+ overlay 10 -> 34 total possible, see below)
    "emotional_bond": 30,   # Sun-Moon 12 + Moon-Venus 10 + Moon-Mars 8
    "stability": 16,        # Venus-Saturn 9 + Sun-Saturn 7
    "communication": 20,    # engine extension: Mercury contacts (see module docstring)
    "growth": 14,           # Jupiter 8 + outer 6
    "karmic_pull": 6,       # nodal 6
}
OVERLAY_BONUS_MUTUAL = 10   # spec 03 §1: mutual 7th-house ASC overlay = "คู่แท้"
OVERLAY_BONUS_SINGLE = 5
KARMIC_DK_RAW = 3.6         # 60/100 of capacity when DK archetype confirmed
KARMIC_NONE_RAW = 0.9       # floor 15/100

_CLASSICAL = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn")
_OUTER = ("Uranus", "Neptune", "Pluto")

_PAIR_KIND = {
    frozenset(("Venus", "Mars")): "Venus-Mars",
    frozenset(("Sun", "Moon")): "Sun-Moon",
    frozenset(("Sun", "Venus")): "Sun-Venus",
    frozenset(("Moon", "Venus")): "Moon-Venus",
    frozenset(("Venus", "Saturn")): "Venus-Saturn",
    frozenset(("Moon", "Mars")): "Moon-Mars",
    frozenset(("Sun", "Saturn")): "Sun-Saturn",
}

# Where each weighted kind lands dimensionally.
_KIND_DIMENSION = {
    "Venus-Mars": "chemistry",
    "Sun-Venus": "chemistry",
    "Sun-Moon": "emotional_bond",
    "Moon-Venus": "emotional_bond",
    "Moon-Mars": "emotional_bond",
    "Venus-Saturn": "stability",
    "Sun-Saturn": "stability",
    "Jupiter contacts": "growth",
    "outer-contacts": "growth",
}

_PERSONAL = ("Sun", "Moon", "Venus", "Mars")

# Documented deviation #3: same-body cross contacts. A partner-to-partner
# Sun-conj-Sun (shared identity — the signature of same-birthday/close-age
# couples) is a real bond the spec table never names, yet the identical-chart
# case is exactly that pattern. Same-body conjunction/trine/sextile score
# under the planet's natural dimension; same-body squares/oppositions stay
# unscored so frictions keep coming from the spec's named kinds only.
_SAME_BODY_DIMENSION = {
    "Sun": "emotional_bond", "Moon": "emotional_bond",
    "Mercury": "communication", "Venus": "chemistry", "Mars": "chemistry",
    "Jupiter": "growth", "Saturn": "stability",
}
_SAME_BODY_WEIGHT = {
    "Sun": 10.0, "Moon": 10.0, "Mercury": 8.0,
    "Venus": 8.0, "Mars": 8.0, "Jupiter": 6.0, "Saturn": 6.0,
}  # outer planets default to growth @ 3.0


def _points(chart: dict) -> list[dict]:
    """Bodies plus the Ascendant (when present) as scorable points."""
    pts = list(chart.get("bodies", []))
    asc = chart.get("ascendant")
    if asc:
        pts = pts + [asc]
    return [p for p in pts if p.get("absolute_deg") is not None]


def _classify(body_a: str, body_b: str) -> tuple[str | None, str | None, float]:
    """Return (kind, dimension, weight) for an ordered A/B point pair."""
    if body_a == body_b:
        # Same-body resonance (deviation #3): Sun-Sun, Moon-Moon, ...
        return (
            f"{body_a}-resonance",
            _SAME_BODY_DIMENSION.get(body_a, "growth"),
            _SAME_BODY_WEIGHT.get(body_a, 3.0),
        )
    if body_a == "ASC" or body_b == "ASC":
        other = body_b if body_a == "ASC" else body_a
        if other == "ASC":
            return None, None, 0.0
        if other in _PERSONAL:
            base = {
                "Sun": W["Sun-Moon"], "Moon": W["Moon-Venus"],
                "Venus": W["Sun-Venus"], "Mars": W["Venus-Mars"],
            }[other] / 2
            dim = "chemistry" if other in ("Venus", "Mars") else "emotional_bond"
            return f"ASC-{other}", dim, base
        if other == "Mercury":
            return "ASC-Mercury", "communication", 5.0
        if other in ("Saturn", "Jupiter"):
            return f"ASC-{other}", "stability" if other == "Saturn" else "growth", \
                (W["Sun-Saturn"] / 2 if other == "Saturn" else W["Jupiter contacts"] / 2)
        return f"ASC-{other}", "growth", W["outer-contacts"] / 2

    fs = frozenset((body_a, body_b))
    if fs in _PAIR_KIND:
        kind = _PAIR_KIND[fs]
        return kind, _KIND_DIMENSION[kind], float(W[kind])
    if "Mercury" in fs:
        rest = fs - {"Mercury"}
        if not rest:  # Mercury-Mercury: not a weighted kind in the spec table
            return None, None, 0.0
        other = next(iter(rest))
        if other in _PERSONAL:
            return "Mercury contacts", "communication", 10.0
        if other in ("Saturn", "Jupiter"):
            return "Mercury contacts", "communication", 6.0
        return None, None, 0.0
    if "Jupiter" in fs:
        return "Jupiter contacts", "growth", float(W["Jupiter contacts"])
    if fs & set(_OUTER):
        return "outer-contacts", "growth", float(W["outer-contacts"])
    return None, None, 0.0


def _weighted_contacts(chart_a: dict, chart_b: dict) -> list[dict]:
    """Cross-aspects between augmented point sets, scored per spec 03 §2."""
    name_a, name_b = chart_a.get("name", "A"), chart_b.get("name", "B")
    results = []
    for pa in _points(chart_a):
        for pb in _points(chart_b):
            sep = _angular_sep(pa["absolute_deg"], pb["absolute_deg"])
            for aspect_name, angle in ASPECTS.items():
                orb = abs(sep - angle)
                if orb > ORBS[aspect_name]:
                    continue
                kind, dim, weight = _classify(pa["body"], pb["body"])
                if kind is None:
                    break
                if pa["body"] == pb["body"] and aspect_name not in (
                    "conjunction", "trine", "sextile",
                ):
                    break  # same-body hard aspects are unscored (deviation #3)
                max_orb = min(MAX_ORB.get(pa["body"], 6), MAX_ORB.get(pb["body"], 6))
                score = weight * HARMONIC[aspect_name] * (1 - orb / max_orb)
                results.append({
                    "pair": f"{name_a} {pa['body']} {aspect_name} {name_b} {pb['body']}",
                    "a_point": pa["body"],
                    "b_point": pb["body"],
                    "aspect": aspect_name,
                    "sign_a": pa.get("sign"),
                    "sign_b": pb.get("sign"),
                    "orb": round(float(orb), 2),
                    "kind": kind,
                    "dimension": dim,
                    "score": round(float(score), 3),
                    "applying": bool(pa.get("applying", False)),
                })
                break
    results.sort(key=lambda r: (-r["score"], r["orb"]))
    return results


def _parse_utc(chart: dict) -> datetime | None:
    raw = chart.get("datetime_utc")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(str(raw).replace("+00:00Z", "+00:00").rstrip("Z"))
    except ValueError:
        return None


def mean_north_node(jd_ut: float) -> float:
    """Mean ascending lunar node, ecliptic longitude in degrees (Meeus ch.47)."""
    t = (jd_ut - 2451545.0) / 36525.0
    omega = (
        125.0445479
        - 1934.1362891 * t
        + 0.0020754 * t * t
        + t * t * t / 467441.0
        - t * t * t / 60616000.0
    )
    return omega % 360


def _jd_from_chart(chart: dict) -> float | None:
    dt = _parse_utc(chart)
    if dt is None:
        return None
    if dt.tzinfo is not None:
        from datetime import timezone
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt.toordinal() + 1721424.5 + (dt.hour + dt.minute / 60 + dt.second / 3600) / 24.0


def north_node_deg(chart: dict) -> float | None:
    jd = _jd_from_chart(chart)
    return mean_north_node(jd) if jd is not None else None


def darakaraka(chart: dict) -> dict | None:
    """Spec 02 §6 Jaimini 7-scheme DK: lowest sidereal degree-in-sign, Sun..Saturn."""
    dt = _parse_utc(chart)
    if dt is None:
        return None
    year_frac = dt.year + (dt.timetuple().tm_yday / 365.2425)
    ayanamsa = 0.0 if chart.get("system") == "sidereal" else lahiri_ayanamsa(year_frac)
    best = None
    for b in chart.get("bodies", []):
        if b["body"] not in _CLASSICAL:
            continue
        deg_in_sign = ((b["absolute_deg"] - ayanamsa) % 360) % 30
        if best is None or deg_in_sign < best["degree_in_sign"]:
            best = {
                "planet": b["body"],
                "degree_in_sign": round(float(deg_in_sign), 2),
                "scheme": "jaimini-7",
            }
    return best


def _nodal_contacts(chart_a: dict, chart_b: dict) -> list[dict]:
    """Spec 03 §4: body conj/opp partner's mean node within 5 deg."""
    node_a = north_node_deg(chart_a)
    node_b = north_node_deg(chart_b)
    if node_a is None or node_b is None:
        return []
    contacts = []
    for side, node in (("a_on_b", node_b), ("b_on_a", node_a)):
        src, dst = (chart_a, "b") if side == "a_on_b" else (chart_b, "a")
        for p in _points(src):
            sep = _angular_sep(p["absolute_deg"], node)
            orb = min(sep, 180.0 - sep)
            if orb <= 5.0:
                contacts.append({
                    "side": side,
                    "point": p["body"],
                    "node_of": dst,
                    "aspect": "conjunction" if sep <= 90 else "opposition",
                    "orb": round(orb, 2),
                    "score": round(W["nodal"] * (1 - orb / 5.0), 3),
                })
    contacts.sort(key=lambda c: c["orb"])
    return contacts


def _sun_moon_sep(chart: dict) -> float | None:
    bmap = {b["body"]: b for b in chart.get("bodies", [])}
    if "Sun" not in bmap or "Moon" not in bmap:
        return None
    return _angular_sep(bmap["Sun"]["absolute_deg"], bmap["Moon"]["absolute_deg"])


def _dk_cross_check(chart_a: dict, chart_b: dict) -> dict:
    """Luminary-DK vs partner Sun-conj-Moon archetype (spec 02 §6 / 03 §4)."""
    checks = {}
    for label, src, dst in (("a_to_b", chart_a, chart_b), ("b_to_a", chart_b, chart_a)):
        dk = darakaraka(src)
        sep = _sun_moon_sep(dst)
        hit = bool(dk and dk["planet"] in ("Sun", "Moon") and sep is not None and sep <= ORBS["conjunction"])
        checks[label] = {"dk": dk, "partner_sun_moon_orb": None if sep is None else round(sep, 2), "hit": hit}
    hit_any = checks["a_to_b"]["hit"] or checks["b_to_a"]["hit"]
    return {"checks": checks, "hit": hit_any}


def house_overlay(chart_a: dict, chart_b: dict) -> dict:
    """Whole-sign 7th-house ASC overlay (spec 03 §1: พฤษภ↔พิจิก = mutual)."""
    def asc_idx(chart: dict) -> int | None:
        asc = chart.get("ascendant")
        if not asc:
            return None
        return _SIGN_INDEX.get(asc["sign"])

    ia, ib = asc_idx(chart_a), asc_idx(chart_b)
    if ia is None or ib is None:
        return {"mutual_7th_asc": False, "a_asc_in_b_dsc_sign": False, "b_asc_in_a_dsc_sign": False, "eligible": False}
    a_in_b = ia == (ib + 6) % 12
    b_in_a = ib == (ia + 6) % 12
    return {
        "mutual_7th_asc": bool(a_in_b and b_in_a),
        "a_asc_in_b_dsc_sign": bool(a_in_b),
        "b_asc_in_a_dsc_sign": bool(b_in_a),
        "eligible": True,
    }


def compute_synastry_profile(chart_a: dict, chart_b: dict) -> dict:
    """Full spec 03 profile: 6 dimensions 0-100 + top_bonds + frictions + karmic layer."""
    contacts = _weighted_contacts(chart_a, chart_b)

    raw = {d: 0.0 for d in DIMENSIONS}
    for c in contacts:
        if c["dimension"]:
            raw[c["dimension"]] += c["score"]

    # House overlay (7th) feeds chemistry per spec 03 §1/§2.
    overlay = house_overlay(chart_a, chart_b)
    overlay_raw = OVERLAY_BONUS_MUTUAL if overlay["mutual_7th_asc"] else (
        OVERLAY_BONUS_SINGLE if (overlay["a_asc_in_b_dsc_sign"] or overlay["b_asc_in_a_dsc_sign"]) else 0.0
    )
    raw["chemistry"] += overlay_raw
    chemistry_cap = CAPACITY["chemistry"] + W["house-overlay(7th)"]

    # Karmic pull: nodal contacts first, DK cross-check fallback (spec 03 §4).
    nodal = _nodal_contacts(chart_a, chart_b)
    nodal_raw = min(sum(c["score"] for c in nodal), W["nodal"])
    dk = None
    if nodal:
        method = "nodal_contact"
        karmic_raw = nodal_raw
    else:
        dk = _dk_cross_check(chart_a, chart_b)
        if dk["hit"]:
            method = "dk_cross_check"
            karmic_raw = KARMIC_DK_RAW
        else:
            method = "none"
            karmic_raw = KARMIC_NONE_RAW
    raw["karmic_pull"] = karmic_raw

    caps = dict(CAPACITY)
    caps["chemistry"] = chemistry_cap
    dims = {
        d: int(max(0, min(100, round(raw[d] / caps[d] * 100))))
        for d in DIMENSIONS
    }

    harmonious = [c for c in contacts if c["aspect"] in ("conjunction", "trine", "sextile")]
    tense = [c for c in contacts if c["aspect"] in ("square", "opposition")]

    overall = round(sum(dims.values()) / len(DIMENSIONS))

    note_parts = " · ".join(f"{d} {dims[d]}" for d in DIMENSIONS)
    note = (
        f"คะแนนความสัมพันธ์: {overall}/100 — {note_parts} "
        f"(บอนด์แรงสุด: {harmonious[0]['pair']} orb {harmonious[0]['orb']}° "
        f"เมื่อมี contact; วิธีชั้นกรรม: {method})"
        if harmonious else
        f"คะแนนความสัมพันธ์: {overall}/100 — {note_parts}"
    )

    return {
        "dimensions": dims,
        "overall": overall,
        "top_bonds": harmonious[:5],
        "frictions": sorted(tense, key=lambda c: c["orb"])[:5],
        "karmic": {
            "method": method,
            "nodal_contacts": nodal,
            "node_a_deg": None if north_node_deg(chart_a) is None else round(north_node_deg(chart_a), 2),
            "node_b_deg": None if north_node_deg(chart_b) is None else round(north_node_deg(chart_b), 2),
            "dk_cross_check": dk,
            "dk_a": darakaraka(chart_a),
            "dk_b": darakaraka(chart_b),
        },
        "house_overlay": overlay,
        "weights_version": "spec03-section2+mercury-ext",
        "note": note,
    }
