"""Cosmobiology service layer — engine spec 15 (Ebertin COSI conventions).

Sits on top of ``src/services/grand/cosmobiology.py`` (which owns the
wrap-safe shortest-arc midpoint math, the C(n,2) tree and direct/indirect
hit-testing). This module adds what the spec requires beyond raw geometry:

1. **20 core pair principles** (§2) — Ebertin principal-principle one-liners,
   EN + TH, attached to every picture whose pair matches.
2. **Transit activation** (§2 timing rule): a mover reaching ≤1° of any natal
   midpoint axis on the 90° dial (conj OR square OR opposition — dial-equivalent)
   FIRES the pair's principle during its window; ≤2° is approaching/leaving
   tail. Soft aspects never count. Per-day output capped at 2 lines sorted by
   orb then planet speed (§5 anti-overload rule).
3. **Composite heart** (§4): composite Sun/Moon midpoint of two charts joins
   the daily scan target list.

Frame rule: TROPICAL ONLY (cosmobiology is Western; spec header ⚠️).
Degradation: fewer than two valid longitudes ⇒ no tree; missing birth time ⇒
angle contacts dropped automatically by the underlying tree builder.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from src.services.chart_service import SIGNS
from src.services.grand.cosmobiology import (
    CONFIRM_ORB,
    SCAN_ORB,
    angdiff,
    compute_cosmobiology,
    format_sign,
    midpoint,
)

# ---------------------------------------------------------------------------
# §2 — 20 core combinations (principal principle, EN + TH)
# ---------------------------------------------------------------------------

PRINCIPLES: dict[frozenset, dict] = {
    frozenset(("Sun", "Moon")): {
        "en": "Vitality–emotion axis: body and soul act as one",
        "th": "แกนชีพจร–จิตใจ: กายกับใจเป็นหนึ่ง",
    },
    frozenset(("Sun", "Venus")): {
        "en": "Love of life; self shines through joy",
        "th": "รักชีวิต: ตัวตนเปล่งประกายผ่านความสุข",
    },
    frozenset(("Venus", "Mars")): {
        "en": "Passion; raw attraction",
        "th": "ความหลงใหล: แรงดึงดูดดิบ",
    },
    frozenset(("Sun", "Saturn")): {
        "en": "Endurance vs obstacle; self built by discipline",
        "th": "อดทนสู้อุปสรรค: วินัยหล่อหลอมตัวตน",
    },
    frozenset(("Jupiter", "Saturn")): {
        "en": "Expansion meets its limit; growth needs frame",
        "th": "ขยายพบขอบเขต: เติบโตต้องมีกรอบ",
    },
    frozenset(("Mars", "Saturn")): {
        "en": "Discipline vs frustration; strength under compression",
        "th": "วินัย–คับขัน: แรงถูกบีบ ต้องบริหาร",
    },
    frozenset(("Uranus", "Pluto")): {
        "en": "Force of change; upheaval that rebuilds from root",
        "th": "แรงเปลี่ยนผ่านรุนแรง: ปฏิวัติจากราก",
    },
    frozenset(("Moon", "Venus")): {
        "en": "Affection; warmth, comfort-seeking",
        "th": "ความเอ็นดู: ใจอ่อนโยน แสวงหาความสบาย",
    },
    frozenset(("Mercury", "Uranus")): {
        "en": "Quick insight; lightning intuition",
        "th": "สติปัญญาไว: มโนทัศน์ฉับพลัน",
    },
    frozenset(("Venus", "Saturn")): {
        "en": "Loyalty tested; love proven over time and duty",
        "th": "ความภักดีถูกทดสอบ: รักผ่านเวลาและภาระ",
    },
    frozenset(("Mars", "Pluto")): {
        "en": "Drive-power; unstoppable force",
        "th": "แรงขับมหาศาล: ลงมือแล้วไม่หยุด",
    },
    frozenset(("Jupiter", "Pluto")): {
        "en": "Big power; game-scale ambition",
        "th": "อำนาจใหญ่: ฟางสุดท้ายระดับเปลี่ยนเกม",
    },
    frozenset(("Sun", "Jupiter")): {
        "en": "Success–growth; optimism, health expanding",
        "th": "สำเร็จ–เติบโต: โชคและสุขภาพขยายตัว",
    },
    frozenset(("Moon", "Saturn")): {
        "en": "Solemn feeling; disciplined, lonely depth",
        "th": "ใจจริงจังเก็บเงียบ: อารมณ์มีวินัย/เหงาลึก",
    },
    frozenset(("Venus", "Neptune")): {
        "en": "Romance and idealization; love as dream — watch projection",
        "th": "โรแมนซ์เลือนราง: รักแบบฝัน — ระวังมองเกินจริง",
    },
    frozenset(("Mars", "Uranus")): {
        "en": "Sudden action; fast, decisive, accident-prone",
        "th": "ลงมือฉับพลัน: เร็วและเด็ดขาด ระวังหน้ามือ",
    },
    frozenset(("Saturn", "Pluto")): {
        "en": "Endurance through crisis; pressure that rebuilds",
        "th": "ทนผ่านวิกฤต: กดดันลึกเพื่อสร้างใหม่",
    },
    frozenset(("Mercury", "Saturn")): {
        "en": "Serious mind; deep structured thinking",
        "th": "ความคิดจริงจัง: คิดลึก ช้าแต่แน่",
    },
    frozenset(("Moon", "Mars")): {
        "en": "Emotional drive; feelings push action",
        "th": "อารมณ์ขับเคลื่อน: ใจร้อน ลงมือตามใจ",
    },
    frozenset(("Venus", "Pluto")): {
        "en": "Fascination; magnetic, consuming attraction",
        "th": "เสน่ห์เหนี่ยวรั้ง: ดึงดูดแบบหลงใหลลึก",
    },
}


def principle_of(pair_names: list[str] | tuple[str, str]) -> dict | None:
    """Principal principle for an unordered pair, or None if not in COSI-20."""
    return PRINCIPLES.get(frozenset(pair_names))


def annotate_pictures(cosmobio_result: dict) -> dict:
    """Attach EN/TH principal principles to a grand.cosmobiology payload."""
    pictures = cosmobio_result.get("pictures") or []
    annotated = 0
    for pic in pictures:
        pr = principle_of(pic.get("pair") or [])
        if pr:
            pic["principle_en"] = pr["en"]
            pic["principle_th"] = pr["th"]
            annotated += 1
    out = dict(cosmobio_result)
    out["pictures"] = pictures
    out["confirmed_pictures"] = [
        p for p in pictures if p.get("confirmed")
    ]
    out["principles_annotated"] = annotated
    return out


def cosmobiology_with_principles(
    natal_chart: dict,
    scan_orb: float = SCAN_ORB,
    confirm_orb: float = CONFIRM_ORB,
) -> dict:
    """One-call entry point: full midpoint tree + COSI-20 annotations."""
    result = compute_cosmobiology(natal_chart, scan_orb, confirm_orb)
    result = annotate_pictures(result)

    sm = result.get("sun_moon_midpoint")
    if sm:
        pr = PRINCIPLES[frozenset(("Sun", "Moon"))]
        sm = {**sm, "principle_en": pr["en"], "principle_th": pr["th"]}
    result["sun_moon_midpoint"] = sm
    return result


# ---------------------------------------------------------------------------
# §2 transit activation — hard contacts only, on the 90° dial
# ---------------------------------------------------------------------------

MOVERS: dict[str, str] = {
    # label → skyfield body key (de421.bsp carries all of these)
    "Moon": "moon",
    "Sun": "sun",
    "Mercury": "mercury",
    "Venus": "venus",
    "Mars": "mars",
    "Jupiter": "jupiter barycenter",
    "Saturn": "saturn barycenter",
}

WINDOW_DAYS = {  # §2 window length by mover (label only; scan uses dates given)
    "Moon": 1, "Sun": 3, "Mercury": 4, "Venus": 4,
    "Mars": 10, "Jupiter": 45, "Saturn": 75,
}

MAX_LINES_PER_DAY = 2


def ecliptic_lon(body_key: str, dt_utc: datetime) -> float:
    from src.services.ephemeris import earth, eph, ts

    _, lon, _ = earth.at(ts.from_datetime(dt_utc)).observe(eph[body_key]).ecliptic_latlon()
    return lon.degrees % 360.0


def _dial_sep(lon_c: float, axis_direct: float) -> float:
    """Separation on the 90° dial — conj/square/opp are all 'same dial spot'."""
    x = abs((lon_c % 90.0) - (axis_direct % 90.0))
    return min(x, 90.0 - x)


def _hard_aspect_name(lon_c: float, axis_direct: float) -> str:
    s = abs(lon_c - axis_direct) % 360.0
    s = min(s, 360.0 - s)
    step = round(s / 90.0) * 90 % 360
    return {0: "conjunction", 90: "square", 180: "opposition"}[step]


def midpoint_axes(natal_chart: dict) -> list[dict]:
    """All C(n,2) axes from the natal chart via the shared wrap-safe math."""
    pts = [(b["body"], float(b["absolute_deg"])) for b in natal_chart.get("bodies", [])]
    if natal_chart.get("ascendant"):
        pts.append(("ASC", float(natal_chart["ascendant"]["absolute_deg"])))
    if natal_chart.get("midheaven"):
        pts.append(("MC", float(natal_chart["midheaven"]["absolute_deg"])))
    axes = []
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            na, la = pts[i]
            nb, lb = pts[j]
            direct = midpoint(la, lb)
            axes.append({
                "pair": [na, nb], "direct_deg": direct,
                **format_sign(direct), "principle": principle_of([na, nb]),
            })
    return axes


def _activation_line_th(act: dict) -> str:
    sign_lbl = act["axis_sign"]
    return (
        f"{act['mover']} {_aspect_th(act['aspect'])} จุดกึ่งกลาง "
        f"{act['pair'][0]}/{act['pair'][1]} กำเนิด ({sign_lbl} {act['axis_degree']}°) — "
        f"{act['principle_th']} (orb {act['orb_deg']}°)"
    )


def _activation_line_en(act: dict) -> str:
    return (
        f"{act['mover']} {act['aspect']} natal {act['pair'][0]}/{act['pair'][1]} "
        f"midpoint ({act['axis_sign']} {act['axis_degree']}°) — "
        f"{act['principle_en']} fires (orb {act['orb_deg']}°)"
    )


_ASPECT_TH = {"conjunction": "☌", "square": "□", "opposition": "☍"}


def _aspect_th(name: str) -> str:
    return _ASPECT_TH.get(name, name)


def scan_activations(
    natal_chart: dict,
    start_utc: datetime,
    end_utc: datetime,
    step_days: int = 1,
    fire_orb: float = 1.0,
    approach_orb: float = 2.0,
    extra_targets: list[dict] | None = None,
    movers: tuple[str, ...] | None = None,
) -> list[dict]:
    """Daily hard-contact scan of movers against natal midpoint axes.

    ``extra_targets`` adds named axes (e.g. the composite heart) in the same
    shape as ``midpoint_axes`` entries. Returns activations sorted by date,
    then orb, then mover speed (fastest first); max 2 per day.
    """
    if end_utc.tzinfo is None or start_utc.tzinfo is None:
        raise ValueError("start_utc/end_utc must be timezone-aware")
    axes = midpoint_axes(natal_chart) + [t for t in (extra_targets or [])]
    movers = movers or ("Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn")

    activations: list[dict] = []
    t = start_utc
    while t <= end_utc:
        day_rows: list[dict] = []
        for mname in movers:
            key = MOVERS[mname]
            lon_now = ecliptic_lon(key, t)
            speed = (
                (ecliptic_lon(key, t + timedelta(hours=12))
                 - ecliptic_lon(key, t - timedelta(hours=12))) % 360.0
            )
            if speed > 180.0:
                speed -= 360.0  # wrap
            for ax in axes:
                orb = _dial_sep(lon_now, ax["direct_deg"])
                if orb > approach_orb:
                    continue
                aspect = _hard_aspect_name(lon_now, ax["direct_deg"])
                pr = ax.get("principle") or {}
                day_rows.append({
                    "date": t.date().isoformat(),
                    "mover": mname,
                    "speed_lon_deg_per_day": round(speed, 4),
                    "aspect": aspect,
                    "pair": ax["pair"],
                    "axis_direct_deg": round(ax["direct_deg"], 2),
                    "axis_sign": ax.get("sign"),
                    "axis_degree": ax.get("degree_in_sign"),
                    "orb_deg": round(orb, 2),
                    "fired": orb <= fire_orb,
                    "tier": "fire" if orb <= fire_orb else "approaching",
                    "window_note": f"~±{WINDOW_DAYS[mname]}d window ({mname})",
                    "principle_en": pr.get("en", ""),
                    "principle_th": pr.get("th", ""),
                })
        fired = [r for r in day_rows if r["fired"]]
        tail = [r for r in day_rows if not r["fired"]]
        fired.sort(key=lambda r: (r["orb_deg"], -abs(r["speed_lon_deg_per_day"])))
        tail.sort(key=lambda r: (r["orb_deg"], -abs(r["speed_lon_deg_per_day"])))
        for r in (fired + tail)[:MAX_LINES_PER_DAY]:
            r["line_th"] = _activation_line_th(r)
            r["line_en"] = _activation_line_en(r)
            activations.append(r)
        t += timedelta(days=step_days)
    return activations


# ---------------------------------------------------------------------------
# §4 composite heart — relationship Sun/Moon midpoint
# ---------------------------------------------------------------------------

def composite_sun_moon_midpoint(chart_a: dict, chart_b: dict) -> dict | None:
    """Composite Sun/Moon 'heart' midpoint of two charts (spec 15 §4).

    Composite Sun = mid(SunA, SunB), composite Moon = mid(MoonA, MoonB),
    heart = mid(composite Sun, composite Moon). Regression anchor:
    mid(101.90, 168.1667) = 135.0333 = Leo 15°02′.
    """
    def _lon(chart: dict, name: str) -> float | None:
        b = next((x for x in chart.get("bodies", []) if x["body"] == name), None)
        return float(b["absolute_deg"]) if b else None

    sun_a, sun_b = _lon(chart_a, "Sun"), _lon(chart_b, "Sun")
    moon_a, moon_b = _lon(chart_a, "Moon"), _lon(chart_b, "Moon")
    if None in (sun_a, sun_b, moon_a, moon_b):
        return None
    comp_sun = midpoint(sun_a, sun_b)
    comp_moon = midpoint(moon_a, moon_b)
    heart = midpoint(comp_sun, comp_moon)
    return {
        "composite_sun_deg": round(comp_sun, 4),
        "composite_moon_deg": round(comp_moon, 4),
        "heart_deg": round(heart, 4),
        **format_sign(heart),
        "note": "commitment-window trigger: hard contact (≤1°) to this degree opens a decision window",
    }
