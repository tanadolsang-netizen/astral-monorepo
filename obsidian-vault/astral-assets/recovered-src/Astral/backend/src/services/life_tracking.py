"""Life tracking layer — natal overlay + transit markers + life timeline
on the real-sky view. Combines birth chart, current transits, and timing
engines (triple activation / profections) into one sky-anchored payload.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

from src.services.chart_service import compute_chart
from src.services.fusion_engine import sidereal_moon_lon, vimshottari_now
from src.services.hellenistic_timelords_service import annual_profections


def _whole_sign_house(planet_lon: float, asc_lon: float) -> int:
    return int(((planet_lon - asc_lon) % 360) // 30) + 1


def _natal_overlay(birth_utc: datetime, lat: float, lon_deg: float,
                   tz_offset_hours: float) -> dict:
    """Natal planets with house placement — drawn as fixed markers."""
    c = compute_chart("natal", birth_utc.date(), birth_utc.time(),
                      tz_offset_hours=0, lat=lat, lon=lon_deg)
    asc = float(c["ascendant"]["absolute_deg"])
    planets = {}
    for b in c["bodies"]:
        lon = float(b["absolute_deg"])
        planets[b["body"]] = {
            "lon": round(lon, 3),
            "house": _whole_sign_house(lon, asc),
            "sign": b.get("sign", ""),
        }
    return {"asc_lon": round(asc, 3), "planets": planets}


def _transit_markers(chart_now: dict, natal: dict,
                     now_utc: datetime) -> list[dict]:
    """For each transiting planet: which natal house it's in + aspect to natal."""
    asc_natal = natal["asc_lon"]
    markers = []
    for b in chart_now["bodies"]:
        name = b["body"]
        lon = float(b["absolute_deg"])
        house = _whole_sign_house(lon, asc_natal)

        # closest major aspect to same natal planet
        aspects = []
        for nb_name, ndata in natal["planets"].items():
            d = abs(lon - ndata["lon"]) % 360
            if d > 180:
                d = 360 - d
            label, orb_ok = None, False
            if d <= 6:
                label, orb_ok = "conjunction", True
            elif abs(d - 120) <= 5:
                label, orb_ok = "trine", abs(d - 120) <= 4
            elif abs(d - 90) <= 5:
                label, orb_ok = "square", abs(d - 90) <= 3
            elif abs(d - 60) <= 4:
                label, orb_ok = "sextile", True
            elif abs(d - 180) <= 5:
                label, orb_ok = "opposition", abs(d - 180) <= 4
            if label and orb_ok and nb_name != name:
                aspects.append(f"{name} {label} natal {nb_name}")
        markers.append({
            "planet": name,
            "natal_house": house,
            "aspects": aspects[:3],
        })
    return markers


def _dasha_summary(moon_sid_birth: float, birth_dt_aware: datetime,
                   now_dt_aware: datetime) -> dict:
    yf_b = birth_dt_aware.year + birth_dt_aware.timetuple().tm_yday / 365.2425
    yf_n = now_dt_aware.year + now_dt_aware.timetuple().tm_yday / 365.2425
    d = vimshottari_now(moon_sid_birth, yf_b, yf_n)
    md = d.get("mahadasha") or {}
    ad = d.get("antardasha") or {}
    return {"mahadasha_lord": md.get("lord"),
            "mahadasha_end": md.get("end_year"),
            "antardasha_lord": ad.get("lord")}


def _profection_now(birth_utc_naive: datetime, now_naive: datetime,
                    asc_lon: float) -> dict:
    age = int((now_naive - birth_utc_naive).days / 365.2425)
    p = annual_profections(age, asc_lon)
    return {"age": age, **p}


def life_tracking_payload(natal_name: str, birth_date_iso: str,
                          birth_time_hhmm: str, tz_offset_hours: float,
                          lat: float, lon_deg: float,
                          now_utc: datetime | None = None) -> dict:
    """Everything the frontend needs to draw life-tracking on the sky."""
    now_utc = now_utc or datetime.now(timezone.utc)
    now_naive = now_utc.replace(tzinfo=None)

    birth_local = datetime.fromisoformat(
        f"{birth_date_iso}T{birth_time_hhmm}:00")
    birth_utc = birth_local - timedelta(hours=tz_offset_hours)

    # natal (sidereal-flavored via tropical chart; houses whole-sign)
    natal = _natal_overlay(birth_utc, lat, lon_deg, tz_offset_hours)
    asc_lon = natal["asc_lon"]

    # current sky
    sky_now = compute_chart("now", now_naive.date(), now_naive.time(),
                            tz_offset_hours=0, lat=lat, lon=lon_deg)

    markers = _transit_markers(sky_now, natal, now_utc)

    moon_sid_birth = sidereal_moon_lon(
        birth_utc.replace(tzinfo=timezone.utc))
    dasha = _dasha_summary(moon_sid_birth,
                           birth_utc.replace(tzinfo=timezone.utc),
                           now_utc)
    prof = _profection_now(birth_utc, now_naive, asc_lon)

    th_lines = [
        f'ตอนนี้ดาวเคราะห์แต่ละดวงกำลังโคจรผ่านบ้านในชะตาคุณ:',
    ]
    for m in markers:
        if m["aspects"]:
            th_lines.append(f"• {m['planet']} → บ้านที่ {m['natal_house']}"
                            f" ({'; '.join(m['aspects'])})")
    th_lines.append(f"ปีนักษัตรราษฎร์: อายุ {prof['age']} ปี "
                    f"— profection บ้าน {prof['house']} "
                    f"(ผู้คุม {prof['lord_th']})")
    th_lines.append(f"Dasha: {dasha['mahadasha_lord']} MD / "
                    f"{dasha['antardasha_lord']} AD")

    en_lines = [
        f"Transits through your natal houses:",
    ]
    for m in markers:
        en_lines.append(f"• {m['planet']} → H{m['natal_house']}"
                        + (f" ({'; '.join(m['aspects'])})"
                           if m["aspects"] else ""))

    return {
        "system": "life-tracking",
        "natal": natal,
        "transit_markers": markers,
        "dasha": dasha,
        "profection": prof,
        "interpretation": {"th": "\n".join(th_lines),
                           "en": "\n".join(en_lines)},
    }
