"""Cosmobiology / Midpoint tree — engine spec C:/AI/research-astrology/15.

Ebertin COSI conventions (QA 2026-08-23 canonical form):
- Stable sorted point order; every unordered pair i<j → C(n,2) midpoints.
- Direct midpoint, shortest arc, wrap-safe:
  ``d = (b − a) % 360; direct = (a + d/2) % 360 if d ≤ 180
  else (a + d/2 − 180) % 360``; indirect = (direct + 180) % 360.
  Never average naively across 0° Aries (Jupiter/Saturn wrap regression:
  direct ≈ 348.65°).
- Contact test always checks BOTH sides: ``hit(c) ⇔ angdiff(c, direct) ≤ orb
  or angdiff(c, indirect) ≤ orb``.
- Orbs: working tier ≤ 2° (scan), tight tier ≤ 1° (confirmed picture /
  transit fire) — never widened to manufacture hits.
- Frame rule: TROPICAL ONLY. Hit tests compare longitudes in one frame;
  this engine is fed the tropical natal chart by grand_fusion.

Ground truth reproduced from the live chart service (M, 1997-05-19 05:45
ICT Chonburi): Sun/Moon midpoint 127.71° (Leo 7°43′) and the four §3 natal
pictures Ve/Ma=Ne (indirect ~0.18°) · Su/Ve=Pl (indirect ~0.34°) ·
Ve/Ju=Sa (direct ~0.40°) · Su/Mo=Ur (indirect ~0.98°) — QA prints the same
pictures at 0.19/0.35/0.40/0.99 from rounded inputs.

Degradation: < 2 valid longitudes ⇒ no tree (empty hits + reason); missing
birth time ⇒ ASC/MC absent ⇒ angle contacts dropped with flag, planet-only
scan continues.
"""

from __future__ import annotations

from datetime import datetime, timezone

from src.services.chart_service import SIGNS

SCAN_ORB = 2.0    # working tier: build/scan the tree
CONFIRM_ORB = 1.0  # tight tier: confirmed picture / transit fires


def angdiff(a: float, b: float) -> float:
    """Smallest absolute angular distance between two longitudes."""
    x = abs(a - b) % 360
    return min(x, 360 - x)


def midpoint(a: float, b: float) -> float:
    """Direct shortest-arc midpoint, wrap-safe (canonical form)."""
    a %= 360
    b %= 360
    d = (b - a) % 360
    direct = (a + d / 2) % 360 if d <= 180 else (a + d / 2 - 180) % 360
    return direct


def indirect_of(direct: float) -> float:
    return (direct + 180) % 360


def hit(c: float, m: float, orb: float) -> tuple[bool, str | None]:
    """Is point c on midpoint axis m? Returns (hit, side)."""
    if angdiff(c, m) <= orb:
        return True, "direct"
    if angdiff(c, indirect_of(m)) <= orb:
        return True, "indirect"
    return False, None


def format_sign(lon: float) -> dict:
    lon %= 360
    idx = int(lon // 30)
    deg = lon % 30
    return {"sign": SIGNS[idx], "degree_in_sign": round(deg, 2)}


def _points(natal_chart: dict) -> tuple[list[tuple[str, float]], bool]:
    """Sorted stable (name, longitude) points + whether angles were present."""
    pts = [(b["body"], float(b["absolute_deg"])) for b in natal_chart.get("bodies", [])]
    asc = natal_chart.get("ascendant")
    mc = natal_chart.get("midheaven")
    if asc:
        pts.append(("ASC", float(asc["absolute_deg"])))
    if mc:
        pts.append(("MC", float(mc["absolute_deg"])))
    return pts, bool(asc and mc)


def compute_cosmobiology(
    natal_chart: dict,
    scan_orb: float = SCAN_ORB,
    confirm_orb: float = CONFIRM_ORB,
) -> dict:
    """Full midpoint tree over every unordered pair i<j, with pictures."""
    points, has_angles = _points(natal_chart)

    base: dict = {
        "status": "ok",
        "system": "cosmobiology_ebertin_v1",
        "frame": "tropical-only",
        "orbs": {
            "scan_deg": scan_orb,
            "confirm_deg": confirm_orb,
            "convention": "COSI norms — never widened to manufacture hits",
        },
        "angles": "included" if has_angles else "skipped(no birth time)",
    }

    if len(points) < 2:
        base.update({
            "status": "unavailable",
            "reason": "insufficient_points(<2 valid longitudes)",
            "midpoints": [],
            "pictures": [],
            "confirmed_pictures": [],
            "computed_at": datetime.now(timezone.utc).isoformat(),
        })
        return base

    lons = {name: lon for name, lon in points}
    midpoints: list[dict] = []
    pictures: list[dict] = []

    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            name_a, lon_a = points[i]
            name_b, lon_b = points[j]
            direct = midpoint(lon_a, lon_b)
            entry = {
                "pair": [name_a, name_b],
                "direct_deg": round(direct, 4),
                "indirect_deg": round(indirect_of(direct), 4),
                **{f"direct_{k}": v for k, v in format_sign(direct).items()},
                "hits": [],
            }
            for name_c, lon_c in points:
                if name_c in (name_a, name_b):
                    continue  # endpoints never contact their own midpoint axis
                is_hit, side = hit(lon_c, direct, scan_orb)
                if is_hit:
                    orb = angdiff(
                        lon_c,
                        direct if side == "direct" else indirect_of(direct),
                    )
                    entry["hits"].append({
                        "point": name_c,
                        "side": side,
                        "orb_deg": round(orb, 4),
                        "confirmed": orb <= confirm_orb,
                    })
                    pictures.append({
                        "picture": f"{name_a}/{name_b}={name_c}",
                        "pair": [name_a, name_b],
                        "contact": name_c,
                        "side": side,
                        "midpoint_deg": round(direct, 4),
                        **{f"midpoint_{k}": v for k, v in format_sign(direct).items()},
                        "orb_deg": round(orb, 4),
                        "confirmed": orb <= confirm_orb,
                    })
            midpoints.append(entry)

    pictures.sort(key=lambda p: p["orb_deg"])
    sun_moon = next(
        (m for m in midpoints if m["pair"] == ["Sun", "Moon"]), None,
    )

    base.update({
        "point_count": len(points),
        "pair_count": len(midpoints),
        "points_used": [name for name, _ in points],
        "sun_moon_midpoint": (
            {
                "direct_deg": round(sun_moon["direct_deg"], 4),
                "indirect_deg": round(sun_moon["indirect_deg"], 4),
                **format_sign(sun_moon["direct_deg"]),
            }
            if sun_moon else None
        ),
        "midpoints": midpoints,
        "picture_count": len(pictures),
        "pictures": pictures,
        "confirmed_pictures": [p for p in pictures if p["confirmed"]],
        "timing_note": (
            "transit hard contacts 0/90/180 within 1° of an axis fire the "
            "pair's principal principle (COSI timing convention)"
        ),
        "computed_at": datetime.now(timezone.utc).isoformat(),
    })
    return base
