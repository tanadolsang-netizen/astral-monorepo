"""Solar Arc + Tertiary Progressions — timing depth pass."""

from __future__ import annotations

from datetime import datetime, timedelta

from src.services.chart_service import compute_chart

NAIBOD = 360.0 / 365.2422 * 0.9856  # ~0.9856°/day mean solar arc per year


def _chart_at(name: str, dt_utc: datetime, lat: float, lon: float) -> dict:
    c = compute_chart(name, dt_utc.date(), dt_utc.time(),
                      tz_offset_hours=0, lat=lat, lon=lon)
    return {b["body"]: float(b["absolute_deg"]) for b in c["bodies"]}


def solar_arc_progressions(birth_iso_local: str, natal_lat: float,
                           natal_lon: float, tz_offset_hours: float = 7.0,
                           target_age_years: float | None = None,
                           target_date_iso: str | None = None) -> dict:
    birth_local = datetime.fromisoformat(birth_iso_local)
    birth_utc = birth_local - timedelta(hours=tz_offset_hours)

    natal = _chart_at("natal", birth_utc, natal_lat, natal_lon)

    # target moment
    if target_date_iso:
        tgt_local = datetime.fromisoformat(target_date_iso)
    else:
        tgt_local = birth_local + timedelta(days=365.2422 *
                                            (target_age_years or 30.0))
    age_years = (tgt_local - birth_local).days / 365.2422
    tgt_utc = tgt_local - timedelta(hours=tz_offset_hours)

    # progressed Sun position (day-per-year): chart at birth + age_days as days
    prog_dt = birth_utc + timedelta(days=age_years)  # 1 day = 1 year
    prog_sun_chart = _chart_at("prog", prog_dt, natal_lat, natal_lon)

    # solar arc = prog sun - natal sun; apply to every body/angle uniformly
    import math
    natal_sun = natal["Sun"]
    prog_sun = prog_sun_chart["Sun"]
    arc = (prog_sun - natal_sun) % 360

    progressed = {}
    for name, lon in natal.items():
        progressed[name] = (lon + arc) % 360

    # tertiary: lunar-month-per-year → moon advances ~13°/year of life
    tertiary_moon = (natal.get("Moon", 0) + age_years * 13.176) % 360

    aspects_to_natal = []
    for name, plon in progressed.items():
        for nb, nlon in natal.items():
            d = abs(plon - nlon) % 360
            if d > 180:
                d = 360 - d
            if abs(d - 120) <= 3:
                aspects_to_natal.append(f"✨ {name} trine natal {nb}")
            elif abs(d - 90) <= 3:
                aspects_to_natal.append(f"⚡ {name} square natal {nb}")
            elif abs(d) <= 3:
                aspects_to_natal.append(f"🔥 {name} conjunct natal {nb}")

    return {
        "system": "solar-arc-tertiary",
        "target": {"age_years": round(age_years, 2),
                   "date": tgt_local.date().isoformat()},
        "solar_arc_degrees": round(arc, 4),
        "progressed_positions": {k: round(v, 3) for k, v in progressed.items()},
        "tertiary_moon_longitude": round(tertiary_moon, 3),
        "aspects_to_natal": aspects_to_natal[:10],
        "interpretation": {
            "th": (
                f"ณ อายุ {age_years:.1f} ปี โซลาร์อาร์คเดินมาแล้ว {arc:.1f}° "
                f"— ทุกดวงถูกเลื่อนพร้อมกัน จึงเห็น 'บทใหม่ของชีวิต' ชัดเจน "
                f"จันทร์เตอร์ชัยรีอยู่ที่ {tertiary_moon:.0f}° คืออารมณ์ระยะสั้นที่กำลังเปลี่ยนผ่าน"
            ),
            "en": (
                f"At age {age_years:.1f}: solar arc {arc:.1f}° applied to all "
                f"points; tertiary Moon at {tertiary_moon:.0f}° marks the "
                f"short-term emotional shift."
            ),
        },
    }
