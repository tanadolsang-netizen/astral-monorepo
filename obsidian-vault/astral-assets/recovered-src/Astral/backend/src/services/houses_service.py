"""Whole-Sign and Equal house systems, computed from an already-built chart.

`src/services/chart_service.py` already implements Placidus and Koch (both
require iterative/time-based solving of the diurnal semi-arc) and bakes a
"house" onto every body via that machinery by default. This module adds the
two systems that do NOT require any of that: they are pure sign-arithmetic
on top of the Ascendant chart_service.py already computed, so they are kept
separate here rather than duplicating chart_service's iterative solver.

Documented limitation: only "whole_sign" and "equal" are implemented in this
module. Placidus and Koch are NOT reimplemented here — see
chart_service.compute_houses for those (they need iterative, time-of-day
dependent solving of the diurnal semi-arc, which is out of scope for this
module by design). If a caller asks this module for any other house_system
string, it raises ValueError.
"""

SIGNS = [
    "เมษ(Aries)", "พฤษภ(Taurus)", "เมถุน(Gemini)", "กรกฎ(Cancer)",
    "สิงห์(Leo)", "กันย์(Virgo)", "ตุลย์(Libra)", "พิจิก(Scorpio)",
    "ธนู(Sagittarius)", "มังกร(Capricorn)", "กุมภ์(Aquarius)", "มีน(Pisces)",
]

HOUSE_SYSTEMS = ("whole_sign", "equal")


def _to_sign(longitude_deg: float) -> tuple[str, float]:
    idx = int(longitude_deg // 30) % 12
    return SIGNS[idx], longitude_deg % 30


def compute_houses(chart: dict, system: str = "whole_sign") -> list[dict]:
    """12 house cusps for `chart` (as returned by chart_service.compute_chart).

    whole_sign: house 1 = the Ascendant's whole sign (cusp at 0deg of that
    sign, regardless of the Ascendant's exact degree); house N is the sign
    N-1 signs further around the zodiac.

    equal: house 1 cusp = the Ascendant's exact degree; every other cusp is
    the Ascendant plus 30deg * (N-1), keeping each house exactly 30deg wide
    but (unlike whole-sign) not aligned to sign boundaries.
    """
    if system not in HOUSE_SYSTEMS:
        raise ValueError(
            f"Unsupported house system: {system!r}. This service only implements "
            f"{HOUSE_SYSTEMS} (Placidus/Koch require iterative time-based solving "
            "and are handled separately in src.services.chart_service)."
        )

    asc_abs = chart["ascendant"]["absolute_deg"]

    cusps = []
    if system == "whole_sign":
        asc_sign_idx = int(asc_abs // 30) % 12
        for house_num in range(1, 13):
            sign_idx = (asc_sign_idx + house_num - 1) % 12
            cusp_deg = sign_idx * 30.0
            sign, deg = _to_sign(cusp_deg)
            cusps.append({
                "house": house_num,
                "sign": sign,
                "degree": round(deg, 4),
                "cusp_deg": round(cusp_deg, 4),
            })
    else:  # equal
        for house_num in range(1, 13):
            cusp_deg = (asc_abs + 30.0 * (house_num - 1)) % 360
            sign, deg = _to_sign(cusp_deg)
            cusps.append({
                "house": house_num,
                "sign": sign,
                "degree": round(deg, 4),
                "cusp_deg": round(cusp_deg, 4),
            })

    return cusps


def place_bodies(chart: dict, cusps: list[dict]) -> list[dict]:
    """Assign each body in chart["bodies"] to a house number from `cusps`.

    A body belongs to house N if its longitude falls in [cusp_N, cusp_N+1),
    wrapping at 360deg for house 12 -> house 1.
    """
    cusp_degs = [c["cusp_deg"] for c in sorted(cusps, key=lambda c: c["house"])]
    placements = []
    for body in chart.get("bodies", []):
        lon_deg = body["absolute_deg"] % 360
        house = 12
        for i in range(12):
            start = cusp_degs[i] % 360
            end = cusp_degs[(i + 1) % 12] % 360
            if start <= end:
                if start <= lon_deg < end:
                    house = i + 1
                    break
            else:
                if lon_deg >= start or lon_deg < end:
                    house = i + 1
                    break
        placements.append({"body": body["body"], "sign": body["sign"], "house": house})
    return placements
