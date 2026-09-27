"""Xuan Kong Flying Stars 玄空飛星 — period chart + annual overlay."""

from __future__ import annotations

LO_SHU = [5, 6, 7, 8, 9, 1, 2, 3, 4]  # palace order: center,NW,W,NE,S,N,SW,E,SE
# Standard 3x3 grid layout (row-major): SE S SW / E C W / NE N NW
GRID_PALACES = [(8,), (3,)]  # not used; we build by palace index


_LOSHU_PATH = [4, 8, 3, 7, 5, 1, 6, 0, 2]  # flight order through grid cells


def _flight_sequence(center_star: int) -> list[int]:
    """Flying-star grid: center_star at palace 5(center), then +1 each step
    along the classical Lo-Shu path. Row-major output."""
    grid = [0] * 9
    for i, cell in enumerate(_LOSHU_PATH):
        star = ((center_star - 1 + i) % 9) + 1
        grid[cell] = star
    return grid


def period_of(build_year: int) -> int:
    """Period 1-9: period 1 starts 1864, each period 20 years."""
    return ((build_year - 1864) % 180) // 20 + 1


def compute_flying_stars(build_year: int, facing_degrees: float,
                         current_year: int | None = None) -> dict:
    if not 0 <= facing_degrees < 360:
        raise ValueError("facing must be 0-359")
    period = period_of(build_year)
    year = current_year or __import__("datetime").date.today().year
    annual_period = period_of(year)

    period_grid = _flight_sequence(period)
    water_grid = _flight_sequence(10 - period)     # facing star = complement
    mountain_grid = _flight_sequence(10 - period)  # sitting star simplified
    annual_grid = _flight_sequence(annual_period)

    PALACE_TH = ["ตะวันออกเฉียงใต้", "ทิศใต้", "ตะวันตกเฉียงใต้",
                 "ทิศตะวันออก", "ศูนย์กลาง", "ทิศตะวันตก",
                 "ตะวันออกเฉียงเหนือ", "ทิศเหนือ", "ตะวันตกเฉียงเหนือ"]

    palaces = []
    for i in range(9):
        w, m, p, a = water_grid[i], mountain_grid[i], period_grid[i], annual_grid[i]
        auspicious = (w in (8, 9, 1)) or (m in (8, 9, 1))
        palaces.append({
            "palace": i + 1, "direction_th": PALACE_TH[i],
            "period_star": p, "water_star": w, "mountain_star": m,
            "annual_star": a,
            "verdict_th": "เสริมได้ — มงคล" if auspicious else "ธรรมดา/ระวัง",
        })

    best = max(palaces, key=lambda p: (p["water_star"] in (8, 9, 1),
                                       p["water_star"] + p["mountain_star"]))
    th = (
        f"บ้านสร้างปี {build_year} (ยุคที่ {period}) หันหน้า{PALACE_TH[int(facing_degrees // 45 * 3) % 9] if False else 'ตามองศา ' + str(round(facing_degrees))}° "
        f"ปีนี้ (ยุค {annual_period}) พื้นที่ดีที่สุด: {best['direction_th']} "
        f"(ดาวน้ำ {best['water_star']} ดาวเขา {best['mountain_star']})"
    )
    en = (
        f"House built {build_year} (period {period}). Best sector this year: "
        f"{best['direction_th']} with water-star {best['water_star']}."
    )
    return {
        "system": "xuan-kong-flying-stars",
        "period": period, "annual_period": annual_period,
        "grids": {"period": period_grid, "water": water_grid,
                  "mountain": mountain_grid, "annual": annual_grid},
        "palaces": palaces,
        "best_sector_th": best["direction_th"],
        "interpretation": {"th": th, "en": en},
    }
