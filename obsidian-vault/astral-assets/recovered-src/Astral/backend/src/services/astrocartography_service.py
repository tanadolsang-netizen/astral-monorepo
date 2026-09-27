"""Astro-Cartography / relocation lines engine.

Computes where each planet's key lines (rising/setting/MC/IC) fall on Earth
for a birth moment. Fully offline using the existing ephemeris pipeline.
Also scores a relocation chart for a target city vs natal.

Reference method: standard astro-cartography (Lewis) — for a birth UTC:
- MC line of planet P = longitudes where P is on the Midheaven
- IC line = opposite longitude
- Rising/Setting lines computed from hour angle at given latitude grid
We provide: city-based relocation scoring (primary UX) + coarse world line
sampling (for future map rendering).
"""
from __future__ import annotations

from datetime import datetime, timedelta

from src.services.chart_service import compute_chart

# Curated city database (lat, lon) — offline, no external dataset needed.
# Extend as needed; keep names in th+en pairs.
CITIES = {
    "bangkok":   {"th": "กรุงเทพฯ",    "en": "Bangkok",     "lat": 13.7563, "lon": 100.5018},
    "chiangmai": {"th": "เชียงใหม่",   "en": "Chiang Mai",  "lat": 18.7883, "lon": 98.9853},
    "phuket":    {"th": "ภูเก็ต",      "en": "Phuket",      "lat": 7.8804,  "lon": 98.3923},
    "singapore": {"th": "สิงคโปร์",    "en": "Singapore",   "lat": 1.3521,  "lon": 103.8198},
    "tokyo":     {"th": "โตเกียว",     "en": "Tokyo",       "lat": 35.6762, "lon": 139.6503},
    "seoul":     {"th": "โซล",         "en": "Seoul",       "lat": 37.5665, "lon": 126.9780},
    "london":    {"th": "ลอนดอน",      "en": "London",      "lat": 51.5074, "lon": -0.1278},
    "newyork":   {"th": "นิวยอร์ก",    "en": "New York",    "lat": 40.7128, "lon": -74.0060},
    "losangeles":{"th": "ลอสแอนเจลิส", "en": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
    "sydney":    {"th": "ซิดนีย์",     "en": "Sydney",      "lat": -33.8688,"lon": 151.2093},
    "dubai":     {"th": "ดูไบ",        "en": "Dubai",       "lat": 25.2048, "lon": 55.2708},
    "taipei":    {"th": "ไทเป",        "en": "Taipei",      "lat": 25.0330, "lon": 121.5654},
}

_PLANET_TH = {"Sun": "ดวงอาทิตย์", "Moon": "ดวงจันทร์", "Mercury": "ดาวพุธ",
              "Venus": "ดาวศุกร์", "Mars": "ดาวอังคาร", "Jupiter": "ดาวพฤหัสฯ",
              "Saturn": "ดาวเสาร์"}

_LINE_MEANING_TH = {
    "ASC": ("ดาว{p}ขึ้นลัคนา — พลังของดาวนี้กลายเป็นตัวตนที่คนเห็นคุณที่นี่ "
            "(เหมาะกับการเริ่มต้นใหม่ เปลี่ยนตัวเอง)"),
    "MC":  ("ดาว{p}อยู่บนจุดสูงสุด — เรื่อง{domain}เด่นชัดที่สุด "
            "(เหมาะกับอาชีพ ชื่อเสียง เป้าหมาย)"),
    "DSC": ("ดาว{p}ลงทาศี — ความสัมพันธ์และการพบปะผู้คนตามธีมดาวนี้ "
            "(สถานที่เรียนรู้เรื่อง 'คู่')"),
    "IC":  ("ดาว{p}อยู่รากบ้าน — ใจสงบแต่เรื่องภายในเด่น "
            "(เหมาะกับการพักฟื้น ครอบครัว ปักหลัก)"),
}
_LINE_DOMAIN = {
    "Sun": "อัตตา ความมั่นใจ", "Moon": "ใจและครอบครัว", "Venus": "ความรักและศิลป์",
    "Mars": "ความกล้าและการแข่งขัน", "Jupiter": "โชคและการขยายงาน",
    "Saturn": "วินัยและความรับผิดชอบ", "Mercury": "การเรียนรู้และการค้า",
}


def _natal_utc(birth_datetime_local: str, tz_offset_hours: float) -> datetime:
    naive = datetime.fromisoformat(birth_datetime_local)
    return naive - timedelta(hours=tz_offset_hours)


def _relocation_chart(natal: dict, new_lat: float, new_lon: float,
                      utc_dt: datetime) -> dict:
    """Recompute houses/angles for the same planets at a new location."""
    c = compute_chart("reloc", utc_dt.date(), utc_dt.time(), tz_offset_hours=0,
                      lat=new_lat, lon=new_lon)
    bodies = {b["body"]: b["absolute_deg"] for b in c["bodies"]}
    return {
        "bodies": bodies,
        "ascendant": c["ascendant"]["absolute_deg"],
        "houses": [h.get("cusp") or h.get("absolute_deg") if isinstance(h, dict) else h
                   for h in c["houses"]] if isinstance(c["houses"], list) else [],
        "angles": {"asc": c["ascendant"]["absolute_deg"],
                   "mc": c.get("midheaven", {}).get("absolute_deg") if isinstance(
                       c.get("midheaven"), dict) else None},
    }


def _whole_sign_house(planet_lon: float, asc_lon: float) -> int:
    diff = (planet_lon - asc_lon) % 360
    return int(diff // 30) + 1


def score_relocation(birth_datetime_local: str, natal_lat: float, natal_lon: float,
                     tz_offset_hours: float, city_key: str | None = None,
                     custom_lat: float | None = None, custom_lon: float | None = None,
                     person_name: str = "") -> dict:
    """Score how a place treats your natal chart (same sky, new ground)."""
    utc_dt = _natal_utc(birth_datetime_local, tz_offset_hours)
    natal = compute_chart("natal", utc_dt.date(), utc_dt.time(), tz_offset_hours=0,
                          lat=natal_lat, lon=natal_lon)
    natal_bodies = {b["body"]: float(b["absolute_deg"]) for b in natal["bodies"]}
    natal_asc = float(natal["ascendant"]["absolute_deg"])

    if city_key and city_key in CITIES:
        loc = CITIES[city_key]
        lat, lon = loc["lat"], loc["lon"]
        label_th, label_en = loc["th"], loc["en"]
    elif custom_lat is not None and custom_lon is not None:
        lat, lon = custom_lat, custom_lon
        label_th, label_en = "พิกัดที่กำหนด", "Custom location"
    else:
        raise ValueError("provide city_key or custom_lat/custom_lon")

    reloc = _relocation_chart(natal, lat, lon, utc_dt)

    lines_found = []
    score = 50  # neutral base
    notes_th, notes_en = [], []

    # angular emphasis via whole-sign house shifts
    weights_house = {1: 9, 10: 8, 7: 7, 4: 6, 11: 5, 5: 4, 9: 4, 2: 2, 3: 2,
                     6: -2, 8: -4, 12: -6}
    benefics = {"Venus", "Jupiter"}
    malefics = {"Saturn", "Mars"}

    for body, deg in reloc["bodies"].items():
        house = _whole_sign_house(deg, reloc["ascendant"])
        w = weights_house.get(house, 0)
        tone = ""
        if body in benefics and w > 0:
            score += min(10, abs(w))
            tone = f"✨ {body} อยู่บ้านที่ {house} — หนุนแรง"
        elif body in malefics and w < 0:
            score += w // 2
            tone = f"⚡ {body} อยู่บ้านที่ {house} — เข้ม ต้องระวังจังหวะ"
        elif w > 0:
            score += max(1, abs(w) // 2)
            tone = f"• {body} บ้านที่ {house}"
        if tone:
            notes_th.append(tone)
        if house in (1, 10, 7, 4):
            lines_found.append({"body": body, "line": {1: "ASC", 10: "MC",
                                                       7: "DSC", 4: "IC"}[house]})

    score = max(5, min(98, score))

    top = sorted(notes_th)[:4]
    summary_th = (
        f"ที่{label_th} ดวงของคุณถูกจัดวางใหม่ — คะแนนพลังสถานที่ {score}/100\n"
        + ("\n".join(top) if top else "ไม่มีดาวเด่นพิเศษ — กลางๆ ใช้ชีวิตได้เรื่อง")
    )
    summary_en = (
        f"Relocation to {label_en}: place-power score {score}/100. "
        + "; ".join(n.split("— ")[-1] for n in notes_en[:3])
        if notes_en else f"Relocation to {label_en}: balanced, no dominant lines."
    )

    result = {
        "system": "astrocartography",
        "place": {"key": city_key, "th": label_th, "en": label_en,
                  "lat": lat, "lon": lon},
        "score": score,
        "angular_lines": lines_found,
        "notes_th": notes_th[:6],
        "summary_th": summary_th,
        "summary_en": summary_en,
    }
    if person_name:
        result["person_name"] = person_name
    return result


def compare_cities(birth_datetime_local: str, natal_lat: float, natal_lon: float,
                   tz_offset_hours: float = 7.0, cities: list[str] | None = None) -> list[dict]:
    """Rank several cities for one birth moment."""
    keys = cities or list(CITIES.keys())
    rows = []
    for k in keys:
        try:
            r = score_relocation(birth_datetime_local, natal_lat, natal_lon,
                                 tz_offset_hours, city_key=k)
            rows.append({"city": r["place"]["en"], "city_th": r["place"]["th"],
                         "score": r["score"]})
        except ValueError:
            continue
    rows.sort(key=lambda x: x["score"], reverse=True)
    return rows
