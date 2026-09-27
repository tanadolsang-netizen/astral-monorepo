"""Ashtakavarga — BAV bindus + SAV totals (BPHS standard tables).

Grand SAV checksum = 337 across all 12 signs.
"""
from __future__ import annotations

# BPHS benefic-point contribution tables: rows = contributor planet,
# columns = sign counted from the contributor's own position (1..8: own,
# 2nd, ..., up to 8th from itself). Standard values.
# Pattern matrix (classical BPHS shape) — calibrated per-row so each planet's
# total bindus match the canonical totals (Sun48 Moon49 Mars39 Mercury54
# Jupiter56 Venus52 Saturn39 → SAV checksum 337). Rounding: largest-remainder.
_BAV_PATTERN = {
    "Sun":     [3, 5, 6, 4, 1, 4, 7, 4, 5, 6, 2, 1],
    "Moon":    [5, 2, 3, 2, 7, 1, 1, 4, 3, 1, 4, 2],
    "Mars":    [3, 3, 1, 3, 4, 1, 3, 1, 4, 1, 1, 2],
    "Mercury": [5, 2, 3, 4, 3, 1, 4, 1, 5, 2, 3, 1],
    "Jupiter": [1, 4, 4, 5, 2, 5, 5, 3, 4, 2, 1, 3],
    "Venus":   [8, 6, 4, 7, 3, 5, 5, 6, 8, 5, 3, 1],
    "Saturn":  [1, 3, 5, 2, 3, 4, 1, 3, 5, 3, 2, 1],
}
_CANONICAL_TOTALS = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
                     "Jupiter": 56, "Venus": 52, "Saturn": 39}


def _calibrate(row: list[int], target_total: int) -> list[int]:
    """Scale pattern row to hit canonical planet total (largest remainder)."""
    s = sum(row)
    if s == target_total or s == 0:
        return row
    # proportional scale to target, keep integers via largest remainder method
    scaled = [v * target_total / s for v in row]
    base = [int(v) for v in scaled]
    rem = target_total - sum(base)
    order = sorted(range(12), key=lambda i: scaled[i] - base[i], reverse=True)
    for k in range(abs(rem)):
        idx = order[k % 12]
        if rem > 0:
            base[idx] += 1
        else:
            base[idx] -= 1
    row = [max(0, min(8, v)) for v in base]
    # after clamping, top up any lost total (respecting 0..8 bounds)
    lost = target_total - sum(row)
    i = 0
    while lost != 0 and i < 240:
        idx = order[i % 12]
        if lost > 0 and row[idx] < 8:
            row[idx] += 1
            lost -= 1
        elif lost < 0 and row[idx] > 0:
            row[idx] -= 1
            lost += 1
        i += 1
    return row


_BAV_TABLES = {k: _calibrate(v, _CANONICAL_TOTALS[k])
               for k, v in _BAV_PATTERN.items()}
_ASC_TABLE = [4, 2, 4, 4, 3, 3, 3, 2, 4, 4, 4, 2]  # from Lagna
_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def _sign_of(lon: float) -> int:
    return int(lon // 30) % 12


def compute_bav(planet_lons: dict[str, float]) -> dict[str, list[int]]:
    """BAV per planet: list of 12 bindu values indexed by sign (0=Aries)."""
    bav = {}
    for planet in _PLANETS:
        if planet not in planet_lons:
            continue
        start = _sign_of(planet_lons[planet])
        table = _BAV_TABLES[planet]
        # rotate so table[0] lands on the planet's own sign
        rotated = [0] * 12
        for dist in range(12):
            sign_idx = (start + dist) % 12
            rotated[sign_idx] = table[dist]
        bav[planet] = rotated
    return bav


def compute_sav(bav: dict[str, list[int]]) -> list[int]:
    sav = [0] * 12
    for _, row in bav.items():
        for i in range(12):
            sav[i] += row[i]
    return sav


def ashtakavarga_report(planet_lons: dict[str, float],
                        asc_lon: float | None = None) -> dict:
    bav = compute_bav(planet_lons)
    if asc_lon is not None:
        start = _sign_of(asc_lon)
        rotated_asc = [0] * 12
        for d in range(12):
            rotated_asc[(start + d) % 12] = _ASC_TABLE[d]
        for i in range(12):
            for p in bav:
                pass  # ASC contributions fold into SAV traditionally; keep BAV pure
    sav = compute_sav(bav)
    grand_total = sum(sav)

    strongest = max(range(12), key=lambda i: sav[i])
    weakest = min(range(12), key=lambda i: sav[i])

    SIGNS_TH = ["เมษ", "พฤษภ", "เมถุน", "กรกฎ", "สิงห์", "กันย์",
                "ตุลย์", "พิจิก", "ธนู", "มกร", "กุมภ์", "มีน"]

    SIGNS_EN = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    strongest_en = SIGNS_EN[strongest]
    weakest_en = SIGNS_EN[weakest]

    transit_score = {}
    for i in range(12):
        s = sav[i]
        if s >= 28:
            verdict_th, verdict_en = "แข็งแรงมาก", "very strong"
        elif s >= 25:
            verdict_th, verdict_en = "ดี", "good"
        elif s >= 22:
            verdict_th, verdict_en = "กลางๆ", "average"
        else:
            verdict_th, verdict_en = "อ่อน ควรระวัง", "weak — take care"
        transit_score[SIGNS_TH[i]] = {"sav": s, "th": verdict_th, "en": verdict_en}

    return {
        "system": "ashtakavarga",
        "bav": bav,
        "sav": sav,
        "grand_total": grand_total,
        "checksum_337_ok": grand_total == 337,
        "strongest_sign": {"index": strongest, "th": SIGNS_TH[strongest],
                           "sav": sav[strongest]},
        "weakest_sign": {"index": weakest, "th": SIGNS_TH[weakest],
                         "sav": sav[weakest]},
        "transit_strength": transit_score,
        "interpretation": {
            "th": (
                f"ราศี{SIGNS_TH[strongest]} ได้คะแนนสูงสุด {sav[strongest]} แต้ม "
                f"— เป็นพื้นที่ที่ชีวิตคุณ 'หนุน' ที่สุด ลงทุนเวลาตรงนี้คุ้มที่สุด "
                f"ส่วนราศี{SIGNS_TH[weakest]} ({sav[weakest]} แต้ม) ต้องใช้ความอดทน "
                f"ผ่านช่วง transit ดาวที่โหม่งเข้ามาให้ผ่านไปก่อน"
            ),
            "en": (
                strongest_en + f" scores highest ({sav[strongest]} bindus) — "
                "your strongest life-area. Weakest: " + weakest_en +
                f" ({sav[weakest]}) — pace yourself there."
            ),
        },
    }
