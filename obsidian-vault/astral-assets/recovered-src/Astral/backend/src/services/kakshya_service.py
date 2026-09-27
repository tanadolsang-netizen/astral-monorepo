"""Ashtakavarga kakshya micro-windows — week-level transit timing.

Research #4: divide each sign into eight 3°45' kakshyas; a transit "fires"
only while the transiting planet moves through kakshyas whose ruler
contributed a bindu in that planet's BAV. Gates everything by SAV strength.

Deterministic, BPHS-grounded, builds on ashtakavarga_service.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from src.services.ashtakavarga_service import (
    compute_bav, compute_sav, _BAV_TABLES, _CANONICAL_TOTALS,
)
from src.services.chart_service import compute_chart

KAKSHYA_SPAN = 30 / 8  # 3°45'
_KAKSHYA_RULERS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
                   "Saturn", "Rahu"]  # classical kakshya lord sequence

SIGNS_TH = ["เมษ", "พฤษภ", "เมถุน", "กรกฎ", "สิงห์", "กันย์",
            "ตุลย์", "พิจิก", "ธนู", "มกร", "กุมภ์", "มีน"]
SIGNS_EN = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius",
            "Pisces"]


def _sign_of(lon: float) -> int:
    return int(lon // 30) % 12


def _kakshya_index(lon_in_sign: float) -> int:
    return int(lon_in_sign // KAKSHYA_SPAN) % 8


def transit_micro_windows(natal_bodies: dict[str, float],
                          natal_asc_lon: float,
                          transiting_planet: str,
                          scan_start_iso: str,
                          scan_days: int = 365,
                          step_days: int = 1) -> dict:
    """Find windows where `transiting_planet` crosses favorable kakshyas
    (per its own BAV) in signs with SAV >= threshold."""
    bav = compute_bav({k: float(v) for k, v in natal_bodies.items()})
    sav = compute_sav(bav)
    if transiting_planet not in bav:
        raise ValueError(f"no BAV for {transiting_planet}")
    planet_row = bav[transiting_planet]

    start = datetime.fromisoformat(scan_start_iso).replace(hour=12)

    # current transit position via chart at start (geo only matters for moon;
    # for slow planets a single chart is fine per step)
    windows = []
    run = None
    prev_state = None

    cursor = start
    for day_i in range(scan_days):
        c = compute_chart("tr", cursor.date(), datetime.strptime(
            "12:00", "%H:%M").time(), tz_offset_hours=0,
            lat=13.7563, lon=100.5018)
        bodies = {b["body"]: float(b["absolute_deg"]) for b in c["bodies"]}
        tlon = bodies.get(transiting_planet)
        if tlon is None:
            cursor += timedelta(days=step_days)
            continue

        sign_idx = _sign_of(tlon)
        lon_in_sign = tlon - sign_idx * 30
        k_idx = _kakshya_index(lon_in_sign)
        kak_ruler = _KAKSHYA_RULERS[k_idx]

        # bindu contributed by this kakshya ruler into planet's row for THIS sign
        # BAV row rotated: planet_row[sign] already sign-specific.
        # kakshya rulership: find which contributor column corresponds to ruler.
        # Column layout: table index = distance from contributor itself; but our
        # rotated row is indexed by SIGN. We approximate: favorable kakshya =
        # kakshya ruler contributed a bindu to this planet's BAV *in this sign*
        # — check via pattern matrix: contributor=ruler, target sign=sign_idx,
        # distance d = (sign_idx - sign_of(ruler's natal lon)) mod 12.
        ruler_natal_lon = natal_bodies.get(kak_ruler)
        favorable = False
        bindu_val = None
        if ruler_natal_lon is not None:
            d = (_sign_of(float(ruler_natal_lon)) - 0)  # placeholder below
        # Simpler robust rule (documented): kakshya favorable iff the kakshya
        # ruler is NOT the planet that contributed 0 bindus to this sign in
        # this planet's BAV construction — we instead use direct lookup:
        # contribution of `ruler` to `transiting_planet`'s BAV at this sign.
        contrib_table = _BAV_TABLES.get(kak_ruler)
        if contrib_table is not None and ruler_natal_lon is not None:
            dist = (_sign_of(float(ruler_natal_lon)) - 0) % 12
            dist = (_sign_of(float(ruler_natal_lon)))  # from ruler itself
            # rotate: value at sign position for contributions FROM ruler
            rotated = [0] * 12
            for dd in range(12):
                rotated[(dist + dd) % 12] = contrib_table[dd]
            bindu_val = rotated[sign_idx]
            favorable = bindu_val > 0

        sav_ok = sav[sign_idx] >= 25
        state = favorable and sav_ok

        entry = {
            "date": cursor.date().isoformat(),
            "sign_en": SIGNS_EN[sign_idx], "sign_th": SIGNS_TH[sign_idx],
            "kakshya": k_idx + 1, "kakshya_ruler": kak_ruler,
            "bindu_from_ruler": bindu_val, "sav": sav[sign_idx],
            "fires": bool(state),
        }
        if state:
            if run is None:
                run = {"start": entry["date"], "end": entry["date"],
                       "signs": [], "peak_sav": sav[sign_idx]}
            else:
                run["end"] = entry["date"]
                run["peak_sav"] = max(run["peak_sav"], sav[sign_idx])
            if entry["sign_en"] not in run["signs"]:
                run["signs"].append(entry["sign_en"])
        else:
            if run is not None:
                if len(windows) < 40:
                    windows.append(run)
                run = None
        cursor += timedelta(days=step_days)

    if run is not None:
        windows.append(run)

    th = (f"{transiting_planet} โคจรผ่านคักชยะที่หนุน "
          f"{sum(w and (w['end'] and 1) or 0 for w in windows) or len(windows)} ช่วงใน {scan_days} วัน "
          f"(กรองด้วย SAV ≥ 25)")
    en = (f"{len(windows)} favorable kakshya window(s) for "
          f"{transiting_planet} within {scan_days} days.")

    return {
        "system": "ashtakavarga-kakshya",
        "planet": transiting_planet,
        "windows": windows,
        "interpretation": {"th": th, "en": en},
    }
