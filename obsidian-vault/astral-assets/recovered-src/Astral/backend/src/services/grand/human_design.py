"""Human Design — engine spec C:/AI/research-astrology/06.

Phase 4.5 unlock (2026-08-23) — Profile layer:

- Gate/line lookup from the verified 64-gate Rave Mandala wheel
  (``hd_gate_wheel.json``: order source-pinned against 5 sources, anchor
  302.0° ecliptic = Gate 41 start, 5.625°/gate, 0.9375°/line; Gate 33
  restored at index 33). The order is embedded below as a fallback so the
  module still works if the data file is missing.
- Design moment: the Sun sits 88° of solar arc before its natal position
  (≈ 89.3 mean-solar days), solved iteratively on the skyfield ephemeris.

Phase 4.7 unlock (2026-08-23) — Type + Inner Authority REAL:

- Full 26-activation pipeline (ATLAS ``hd_channels_centers.json``, commit
  b5ac4d0; 36-channel / 64-gate→9-center tables pinned against geneticmatrix,
  humdes.com and humandesign-api): Personality activations (Sun, Earth =
  Sun+180°, Moon, True North/South Node, Mercury…Pluto) from the natal
  tropical chart, plus the same 13 bodies re-computed at the design moment.
- FRAME NOTE: the Rave Mandala lives in the ecliptic OF-DATE tropical frame.
  chart_service/skyfield longitudes are J2000-referenced (a uniform
  precession-since-2000 skew: ~0.75° for a 1946 birth) — enough to flip
  gate/line boundaries on historical charts. Activations and the Personality/
  Design Sun therefore come from pyswisseph (of-date) when importable;
  skyfield remains as fallback (design-moment solving is frame-independent,
  so the solved instant is unaffected either way).
- Validated end-to-end against the dataset's published validation vector
  (Donald Trump, 1946-06-14 10:54 EDT Queens): all 26 gate.line labels,
  channels 6-59/17-62/21-45/35-36, defined centers Ajna/Heart/Sacral/
  SolarPlexus/Throat, Type = Manifesting Generator, Authority = Emotional,
  Profile 1/3 reproduce exactly (totalhumandesign + geneticmatrix +
  humandesignsystem.co consensus; ATLAS our_pipeline_result_2026_08_23).
- A channel DEFINES when BOTH endpoint gates are activated somewhere in the
  Personality ∪ Design union; defined centers are the centers touched by
  completed channels; Type follows the table's rule set (Reflector /
  Generator / Manifesting Generator / Manifestor / Projector with
  motor-to-Throat connectivity walked through completed channels).
- Authority follows the jovianarchive/Ra ordering recorded in the dataset:
  Emotional > Sacral > Splenic > Ego/Heart > Self-Projected (Projectors) >
  Mental/Environmental > Lunar (Reflectors).
- Lunar nodes: TRUE node = Meeus ch. 47 mean ascending node polynomial plus
  the principal periodic terms of the Chapront lunar series (the standard
  truncated true-node expansion, arcminute-class); South node = North+180°.
  All four published Trump node gate.lines (45.5/26.5/12.4/11.4) reproduce.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

REASON = "unavailable: needs a natal tropical chart (with Sun) to emit a profile"

# Swiss Ephemeris optional import — used for ecliptic-OF-DATE longitudes.
# skyfield's ``ecliptic_latlon()`` is J2000-referenced: for 1946 births it
# runs ~0.75° ahead of the of-date frame every HD calculator uses (measured,
# uniform across all bodies ≈ general precession since 2000.0). The HD
# Rave Mandala lives in the of-date tropical frame (anchor 02 Aquarius), so
# activations/profile are computed with pyswisseph when importable and fall
# back to the skyfield path (small historical-date skew, documented) when not.
try:  # pragma: no cover - depends on interpreter/wheel availability
    import swisseph as _swe
except Exception:  # pragma: no cover
    _swe = None
else:
    try:
        _SWE_EPHE_DIR = Path(__file__).resolve().parents[3] / "ephe"
        if _SWE_EPHE_DIR.is_dir():
            _swe.set_ephe_path(str(_SWE_EPHE_DIR))
    except Exception:  # pragma: no cover
        pass

# Verified Rave Mandala order (hd_gate_wheel.json, 2026-08-23) — embedded
# fallback so gate/line lookup never dies with a missing data file.
_WHEEL_ORDER_FALLBACK = [
    41, 19, 13, 49, 30, 55, 37, 63, 22, 36, 25, 17, 21, 51, 42, 3,
    27, 24, 2, 23, 8, 20, 16, 35, 45, 12, 15, 52, 39, 53, 62, 56,
    31, 33, 7, 4, 29, 59, 40, 64, 47, 6, 46, 18, 48, 57, 32, 50,
    28, 44, 1, 43, 14, 34, 9, 5, 26, 11, 10, 58, 38, 54, 61, 60,
]
_WHEEL_START_DEG = 302.0
_GATE_SPAN = 360.0 / 64  # 5.625°
_LINE_SPAN = _GATE_SPAN / 6  # 0.9375°
_DESIGN_ARC_DEG = 88.0

_ANCHOR_CANDIDATES = (
    Path("C:/AI/research-astrology/data/hd_gate_wheel.json"),
    Path(__file__).resolve().parents[3] / "data" / "hd_gate_wheel.json",
)

# --- Embedded from ATLAS hd_channels_centers.json (commit b5ac4d0) ---
# 64 gates -> 9 centers (geneticmatrix / humdes / humandesign-api agree).
_GATE_CENTER: dict[int, str] = {
    1: "G", 2: "G", 3: "Sacral", 4: "Ajna", 5: "Sacral", 6: "SolarPlexus",
    7: "G", 8: "Throat", 9: "Sacral", 10: "G", 11: "Ajna", 12: "Throat",
    13: "G", 14: "Sacral", 15: "G", 16: "Throat", 17: "Ajna", 18: "Spleen",
    19: "Root", 20: "Throat", 21: "Heart", 22: "SolarPlexus", 23: "Throat",
    24: "Ajna", 25: "G", 26: "Heart", 27: "Sacral", 28: "Spleen", 29: "Sacral",
    30: "SolarPlexus", 31: "Throat", 32: "Spleen", 33: "Throat", 34: "Sacral",
    35: "Throat", 36: "SolarPlexus", 37: "SolarPlexus", 38: "Root",
    39: "Root", 40: "Heart", 41: "Root", 42: "Sacral", 43: "Ajna",
    44: "Spleen", 45: "Throat", 46: "G", 47: "Ajna", 48: "Spleen",
    49: "SolarPlexus", 50: "Spleen", 51: "Heart", 52: "Root", 53: "Root",
    54: "Root", 55: "SolarPlexus", 56: "Throat", 57: "Spleen", 58: "Root",
    59: "Sacral", 60: "Root", 61: "Head", 62: "Throat", 63: "Head", 64: "Head",
}
# The 36 definition channels: both gates active (anywhere in P∪D) ⇒ defined.
_CHANNELS: tuple[dict, ...] = (
    {"gates": (1, 8), "name": "Inspiration", "centers": ("G", "Throat")},
    {"gates": (2, 14), "name": "The Beat", "centers": ("G", "Sacral")},
    {"gates": (3, 60), "name": "Mutation", "centers": ("Sacral", "Root")},
    {"gates": (4, 63), "name": "Logic", "centers": ("Ajna", "Head")},
    {"gates": (5, 15), "name": "Rhythm", "centers": ("Sacral", "G")},
    {"gates": (6, 59), "name": "Mating", "centers": ("SolarPlexus", "Sacral")},
    {"gates": (7, 31), "name": "The Alpha", "centers": ("G", "Throat")},
    {"gates": (9, 52), "name": "Concentration", "centers": ("Sacral", "Root")},
    {"gates": (10, 20), "name": "Awakening", "centers": ("G", "Throat")},
    {"gates": (10, 34), "name": "Exploration", "centers": ("G", "Sacral")},
    {"gates": (10, 57), "name": "Perfected Form", "centers": ("G", "Spleen")},
    {"gates": (11, 56), "name": "Curiosity", "centers": ("Ajna", "Throat")},
    {"gates": (12, 22), "name": "Openness", "centers": ("Throat", "SolarPlexus")},
    {"gates": (13, 33), "name": "The Prodigal", "centers": ("G", "Throat")},
    {"gates": (16, 48), "name": "Talent/Wavelength", "centers": ("Throat", "Spleen")},
    {"gates": (17, 62), "name": "Acceptance", "centers": ("Ajna", "Throat")},
    {"gates": (18, 58), "name": "Judgment", "centers": ("Spleen", "Root")},
    {"gates": (19, 49), "name": "Synthesis/Sensitivity", "centers": ("Root", "SolarPlexus")},
    {"gates": (20, 34), "name": "Charisma", "centers": ("Throat", "Sacral")},
    {"gates": (20, 57), "name": "Brainwave", "centers": ("Throat", "Spleen")},
    {"gates": (21, 45), "name": "Money/Materialism", "centers": ("Heart", "Throat")},
    {"gates": (23, 43), "name": "Structuring", "centers": ("Throat", "Ajna")},
    {"gates": (24, 61), "name": "Awareness", "centers": ("Ajna", "Head")},
    {"gates": (25, 51), "name": "Initiation", "centers": ("G", "Heart")},
    {"gates": (26, 44), "name": "Surrender", "centers": ("Heart", "Spleen")},
    {"gates": (27, 50), "name": "Preservation", "centers": ("Sacral", "Spleen")},
    {"gates": (28, 38), "name": "Struggle", "centers": ("Spleen", "Root")},
    {"gates": (29, 46), "name": "Discovery", "centers": ("Sacral", "G")},
    {"gates": (30, 41), "name": "Recognition/Desire", "centers": ("SolarPlexus", "Root")},
    {"gates": (32, 54), "name": "Transformation", "centers": ("Spleen", "Root")},
    {"gates": (34, 57), "name": "Power", "centers": ("Sacral", "Spleen")},
    {"gates": (35, 36), "name": "Transitoriness", "centers": ("Throat", "SolarPlexus")},
    {"gates": (37, 40), "name": "Community/Bargain", "centers": ("SolarPlexus", "Heart")},
    {"gates": (39, 55), "name": "Emoting", "centers": ("Root", "SolarPlexus")},
    {"gates": (42, 53), "name": "Maturation", "centers": ("Sacral", "Root")},
    {"gates": (47, 64), "name": "Abstraction", "centers": ("Ajna", "Head")},
)

_MOTOR_CENTERS = frozenset({"Sacral", "SolarPlexus", "Heart", "Root"})
_ABOVE_THROAT = frozenset({"Head", "Ajna", "Throat"})

_AUTH_EMOTIONAL = "Emotional (Solar Plexus)"
_AUTH_SACRAL = "Sacral"
_AUTH_SPLENIC = "Splenic"
_AUTH_EGO = "Ego / Heart"
_AUTH_SELF_PROJECTED = "Self-Projected"
_AUTH_MENTAL = "Mental / Environmental (no inner authority)"
_AUTH_LUNAR = "Lunar"


def _load_wheel() -> dict:
    """Verified wheel file if reachable, else the embedded fallback order."""
    for path in _ANCHOR_CANDIDATES:
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            order = data.get("order")
            if isinstance(order, list) and len(order) == 64:
                return {"order": [int(g) for g in order], "source_file": str(path)}
        except (OSError, ValueError):
            continue
    return {"order": list(_WHEEL_ORDER_FALLBACK), "source_file": "embedded_fallback"}


def lon_to_gate_line(longitude: float, order: list[int] | None = None) -> tuple[int, int]:
    """Ecliptic longitude → (gate, line) on the Rave Mandala wheel.

    slot = floor(((lon − 302) mod 360) / 5.625); gate = order[slot];
    line = floor((((lon − 302) mod 360) mod 5.625) / 0.9375) + 1.
    """
    order = order or _WHEEL_ORDER_FALLBACK
    rel = (longitude - _WHEEL_START_DEG) % 360.0
    slot = int(rel // _GATE_SPAN)
    slot = min(slot, 63)  # guard float edge (rel == 359.9999…)
    gate = order[slot]
    line = int((rel % _GATE_SPAN) // _LINE_SPAN) + 1
    return gate, min(line, 6)


# ---------------------------------------------------------------------------
# Lunar nodes — TRUE node (HD charts use the true node)
# ---------------------------------------------------------------------------

def _jd_ut_from_datetime(dt_utc: datetime) -> float:
    """Julian Day (UT) from an aware datetime (ΔT ignored: sub-arcminute here)."""
    dt_utc = dt_utc.astimezone(timezone.utc)
    return (dt_utc - datetime(2000, 1, 1, 12, tzinfo=timezone.utc)).total_seconds() / 86400.0 + 2451545.0


def true_north_node(jd_ut: float) -> float:
    """True ascending lunar node, ecliptic longitude in degrees.

    Mean node polynomial (Meeus, Astronomical Algorithms ch. 47.7) plus the
    principal periodic terms of the Chapront lunar series — the standard
    truncated true-node expansion used by almanac-grade astro software.
    South node is always North + 180°.
    """
    t = (jd_ut - 2451545.0) / 36525.0
    omega = (
        125.0445479
        - 1934.1362891 * t
        + 0.0020754 * t * t
        + t * t * t / 467441.0
        - t * t * t * t / 60616000.0
    )
    d = 297.8501921 + 445267.1114034 * t - 0.0018819 * t * t + t ** 3 / 545868.0
    m_sun = 357.5291092 + 35999.0502909 * t - 0.0001536 * t * t
    m_moon = 134.9633964 + 477198.8675055 * t + 0.0087414 * t * t + t ** 3 / 69699.0
    f = 93.2720950 + 483202.0175233 * t - 0.0036539 * t * t - t ** 3 / 3526000.0

    def s(x: float) -> float:
        return math.sin(math.radians(x))

    omega += (
        -1.4979 * s(2 * (d - f))
        - 0.1500 * s(m_sun)
        - 0.1226 * s(2 * d)
        + 0.1176 * s(2 * f)
        - 0.0801 * s(2 * (m_moon - f))
    )
    return omega % 360.0


_SWE_PLANETS = (("Sun", 0), ("Moon", 1), ("Mercury", 2), ("Venus", 3), ("Mars", 4),
                ("Jupiter", 5), ("Saturn", 6), ("Uranus", 7), ("Neptune", 8), ("Pluto", 9))


def _sun_longitude_utc(dt_utc: datetime) -> float:
    """Apparent geocentric ecliptic-of-date longitude of the Sun (tropical).

    Swiss Ephemeris when available; skyfield fallback (J2000-referenced
    ecliptic — frame-consistent for the −88° design-arc difference).
    """
    if _swe is not None:
        jd = _jd_ut_from_datetime(dt_utc)
        return _swe.calc_ut(jd, 0, _swe.FLG_SWIEPH)[0][0] % 360.0
    return _sun_longitude_skyfield(dt_utc)


def _sun_longitude_skyfield(dt_utc: datetime) -> float:
    from src.services.ephemeris import earth, eph, ts

    t = ts.from_datetime(dt_utc)
    pos = earth.at(t).observe(eph["sun"])
    return pos.ecliptic_latlon()[1].degrees % 360.0


def _body_longitudes_utc(dt_utc: datetime) -> dict[str, float]:
    """Apparent geocentric ecliptic-of-date longitudes of Sun..Pluto."""
    if _swe is not None:
        jd = _jd_ut_from_datetime(dt_utc)
        out: dict[str, float] = {}
        for name, pid in _SWE_PLANETS:
            out[name] = _swe.calc_ut(jd, pid, _swe.FLG_SWIEPH)[0][0] % 360.0
        return out
    # skyfield fallback (J2000-referenced ecliptic; small skew on historical dates)
    from src.services.chart_service import BODIES
    from src.services.ephemeris import earth, eph, ts

    t = ts.from_datetime(dt_utc)
    out = {}
    for name, key in BODIES.items():
        pos = earth.at(t).observe(eph[key])
        out[name] = pos.ecliptic_latlon()[1].degrees % 360.0
    return out


_ACTIVATION_BODIES = (
    "Sun", "Earth", "Moon", "North Node", "South Node", "Mercury", "Venus",
    "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
)


def activations_at(dt_utc: datetime, sun_longitude: float | None = None) -> dict[str, dict]:
    """The 13 HD activation points at one instant → {'Body': {lon,gate,line}}.

    Earth = Sun + 180°. Nodes come from the true-node series. ``sun_longitude``
    lets callers pin the Sun (used for the design moment where the solved
    value is already available).
    """
    lons = _body_longitudes_utc(dt_utc)
    if sun_longitude is not None:
        lons["Sun"] = sun_longitude % 360.0
    jd = _jd_ut_from_datetime(dt_utc)
    nn = true_north_node(jd)
    lons["North Node"] = nn
    lons["South Node"] = (nn + 180.0) % 360.0
    lons["Earth"] = (lons["Sun"] + 180.0) % 360.0

    order = _load_wheel()["order"]
    out: dict[str, dict] = {}
    for body in _ACTIVATION_BODIES:
        lon = lons[body] % 360.0
        gate, line = lon_to_gate_line(lon, order)
        out[body] = {
            "longitude_tropical": round(lon, 4),
            "gate": gate,
            "line": line,
            "label": f"{gate}.{line}",
        }
    return out


# ---------------------------------------------------------------------------
# Channels → centers → Type / Authority (pure rules, unit-testable)
# ---------------------------------------------------------------------------

def activated_gates(longitudes) -> set[int]:
    """Set of gates hit by an iterable of tropical longitudes."""
    order = _load_wheel()["order"]
    return {lon_to_gate_line(float(lon), order)[0] for lon in longitudes}


def completed_channels(gates: set[int]) -> list[dict]:
    """Channels whose BOTH endpoint gates appear in ``gates`` (sorted)."""
    done = [ch for ch in _CHANNELS if ch["gates"][0] in gates and ch["gates"][1] in gates]
    return sorted(done, key=lambda c: c["gates"])


def defined_centers_of(channels_done: list[dict]) -> set[str]:
    """Centers touched by at least one completed channel."""
    centers: set[str] = set()
    for ch in channels_done:
        centers.update(ch["centers"])
    return centers


def motor_throat_connected(defined: set[str], channels_done: list[dict]) -> bool:
    """Is ANY motor center connected to the Throat through completed channels?

    BFS over completed channels as edges (each edge joins its two centers;
    both endpoints are defined by construction).
    """
    if "Throat" not in defined or not (_MOTOR_CENTERS & defined):
        return False
    adj: dict[str, set[str]] = {}
    for ch in channels_done:
        a, b = ch["centers"]
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    seen = {"Throat"}
    frontier = ["Throat"]
    while frontier:
        nxt: list[str] = []
        for c in frontier:
            if c in _MOTOR_CENTERS:
                return True
            for nb in adj.get(c, ()):  # noqa: B007
                if nb not in seen:
                    seen.add(nb)
                    nxt.append(nb)
        frontier = nxt
    return False


def classify_type(defined: set[str], channels_done: list[dict]) -> str:
    """Type per hd_channels_centers.json type_rules."""
    if not defined:
        return "Reflector"
    link = motor_throat_connected(defined, channels_done)
    if "Sacral" in defined:
        return "Manifesting Generator" if link else "Generator"
    if link:
        return "Manifestor"
    return "Projector"


def inner_authority(defined: set[str], hd_type: str) -> str:
    """Inner Authority per the jovianarchive/Ra hierarchy in the dataset."""
    if not defined:
        return _AUTH_LUNAR
    if "SolarPlexus" in defined:
        return _AUTH_EMOTIONAL  # always overrides all others
    if "Sacral" in defined:
        return _AUTH_SACRAL
    if "Spleen" in defined:
        return _AUTH_SPLENIC
    if "Heart" in defined:
        return _AUTH_EGO
    if "G" in defined and hd_type == "Projector":
        return _AUTH_SELF_PROJECTED
    # Only centers above/at the Throat can remain here: any defined Root,
    # Spleen, Sacral, SolarPlexus, Heart or G center would have matched above
    # (Root cannot define without one of its partner centers).
    return _AUTH_MENTAL


def type_and_authority_from_gates(gates: set[int]) -> dict:
    """Full Type/Authority/Definition from an activated-gate set (P∪D union)."""
    channels_done = completed_channels(gates)
    defined = defined_centers_of(channels_done)
    hd_type = classify_type(defined, channels_done)
    authority = inner_authority(defined, hd_type)
    return {
        "type": hd_type,
        "authority": authority,
        "defined_centers": sorted(defined),
        "defined_channels": [f"{a}-{b}" for a, b in (c["gates"] for c in channels_done)],
        "defined_channels_detail": [
            {
                "gates": f"{c['gates'][0]}-{c['gates'][1]}",
                "name": c["name"],
                "centers": list(c["centers"]),
            }
            for c in channels_done
        ],
        "motor_throat_connected": motor_throat_connected(defined, channels_done),
    }


# ---------------------------------------------------------------------------
# Design-moment solver (Phase 4.5; Sun source now Swiss-Ephemeris-first)
# ---------------------------------------------------------------------------

def find_design_moment(natal_sun_lon: float, birth_utc: datetime) -> dict:
    """Solve transit Sun = (natal Sun − 88°) mod 360 for the instant ≈89.3 d
    before birth. Coarse 0.25-day scan over [birth−100 d, birth−80 d] to
    bracket the crossing (solar longitude is monotonic), then bisection to
    sub-second precision on the signed angular difference.
    """
    target = (natal_sun_lon - _DESIGN_ARC_DEG) % 360.0

    def diff(t: datetime) -> float:
        d = (_sun_longitude_utc(t) - target + 180.0) % 360.0 - 180.0
        return d  # negative before the crossing, positive after (Sun moves +)

    lo = birth_utc - timedelta(days=100)
    hi = birth_utc - timedelta(days=80)
    step = timedelta(days=0.25)

    prev_d = diff(lo)
    bracket = None
    t = lo
    while t < hi:
        nxt = t + step
        d = diff(nxt)
        if prev_d <= 0.0 <= d:
            bracket = (t, nxt)
            break
        prev_d, t = d, nxt
    if bracket is None:  # pragma: no cover — solar motion cannot skip 0.25°
        return {"status": "unavailable", "reason": "design_moment_bracket_not_found"}

    a, b = bracket
    for _ in range(60):  # 20 d / 2^60 — converges far below 1 s
        mid = a + (b - a) / 2
        if diff(mid) < 0.0:
            a = mid
        else:
            b = mid
    moment = a + (b - a) / 2
    return {
        "status": "ok",
        "moment_utc": moment,
        "target_sun_lon": round(target, 6),
        "sun_lon_at_moment": round(_sun_longitude_utc(moment), 6),
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def compute_human_design(natal_chart: dict | None = None, *_args, **_kwargs) -> dict:
    """Full Human Design: Profile + Type + Authority + Definition.

    ``natal_chart`` is a ``chart_service.compute_chart(system="tropical")``
    payload. Pipeline: 26 activations (13 Personality from the natal chart +
    13 Design at the −88° solar-arc moment) → gates → 36-channel table →
    defined centers → Type rules → Authority hierarchy. Graceful under all
    missing-input paths.
    """
    if not isinstance(natal_chart, dict):
        return {"status": "unavailable", "reason": "missing_natal_chart"}

    sun = next(
        (b for b in natal_chart.get("bodies", []) if b.get("body") == "Sun"), None
    )
    if sun is None or sun.get("absolute_deg") is None:
        return {"status": "unavailable", "reason": "missing_natal_sun_longitude"}

    # Birth instant in UTC. chart_service serialises as
    # isoformat() + "Z" → "...+00:00Z"; strip a trailing Z before parsing.
    birth_iso = natal_chart.get("datetime_utc")
    try:
        s = str(birth_iso).strip()
        if s.endswith("Z"):
            s = s[:-1]
        birth_utc = datetime.fromisoformat(s)
        if birth_utc.tzinfo is None:
            birth_utc = birth_utc.replace(tzinfo=timezone.utc)
    except ValueError:
        return {"status": "unavailable", "reason": "invalid_natal_datetime_utc"}

    wheel = _load_wheel()
    order = wheel["order"]

    # Personality Sun in ecliptic-OF-DATE frame (the Rave Mandala frame).
    # chart_service longitudes are skyfield J2000-referenced; pyswisseph gives
    # the of-date value HD calculators use. Fall back to the chart value.
    sun_source = "natal_chart(skyfield)"
    natal_sun_lon = float(sun["absolute_deg"])
    if _swe is not None:
        try:
            natal_sun_lon = _sun_longitude_utc(birth_utc)
            sun_source = "swisseph(of-date)"
        except Exception:
            pass
    p_gate, p_line = lon_to_gate_line(natal_sun_lon, order)

    design = find_design_moment(natal_sun_lon, birth_utc)
    if design.get("status") != "ok":
        return {
            "status": "unavailable",
            "reason": f"design_moment_unsolved:{design.get('reason')}",
        }

    moment = design["moment_utc"]
    d_gate, d_line = lon_to_gate_line(design["sun_lon_at_moment"], order)

    # ---- Phase 4.7: 26 activations → Type / Authority ----
    try:
        p_act = activations_at(birth_utc, sun_longitude=natal_sun_lon)
        d_act = activations_at(moment, sun_longitude=design["sun_lon_at_moment"])
    except Exception as exc:  # ephemeris unavailable → degrade honestly
        return {"status": "unavailable", "reason": f"activation_ephemeris_failed:{exc}"}

    gates_union: set[int] = {v["gate"] for v in p_act.values()}
    gates_union |= {v["gate"] for v in d_act.values()}
    ta = type_and_authority_from_gates(gates_union)

    profile = {
        "p_sun": f"{p_gate}.{p_line}",
        "d_sun": f"{d_gate}.{d_line}",
        "profile_name": f"{p_line}/{d_line}",
    }
    return {
        "status": "ok",
        "system": "Human Design — Rave Mandala gate/line + Type/Authority (36-channel table)",
        "wheel": {
            "source_file": wheel["source_file"],
            "anchor": f"Gate {order[0]} starts {_WHEEL_START_DEG}° ecliptic",
            "deg_per_gate": _GATE_SPAN,
            "deg_per_line": round(_LINE_SPAN, 6),
        },
        "channels_source": "hd_channels_centers.json (commit b5ac4d0; embedded)",
        "sun_longitude_source": sun_source,
        "personality": {
            "gate": p_gate,
            "line": p_line,
            "label": profile["p_sun"],
            "sun_longitude_tropical": round(natal_sun_lon, 4),
            "activations": p_act,
        },
        "design": {
            "gate": d_gate,
            "line": d_line,
            "label": profile["d_sun"],
            "sun_longitude_tropical": design["sun_lon_at_moment"],
            "moment_utc": moment.isoformat(),
            "arc_days_before_birth": round(
                (birth_utc - moment).total_seconds() / 86400.0, 4
            ),
            "solar_arc_deg": _DESIGN_ARC_DEG,
            "activations": d_act,
        },
        "profile": profile,
        "type": ta["type"],
        "authority": ta["authority"],
        "defined_centers": ta["defined_centers"],
        "defined_channels": ta["defined_channels"],
        "defined_channels_detail": ta["defined_channels_detail"],
        "activated_gates": sorted(gates_union),
        "motor_throat_connected": ta["motor_throat_connected"],
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }
