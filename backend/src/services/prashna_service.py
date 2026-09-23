"""Vedic Prashna (horary) + Tajika aspects — question-answering verdicts."""

from __future__ import annotations

from datetime import datetime

from src.services.chart_service import compute_chart
from src.services.vedic_service import _sidereal, _ayanamsa

SIGNS_TH = ["เมษ", "พฤษภ", "เมถุน", "กรกฎ", "สิงห์", "กันย์",
            "ตุลย์", "พิจิก", "ธนู", "มกร", "กุมภ์", "มีน"]

# Tajika orbs by aspect (tighter than Western)
_TAJIKA_ORBS = {"conjunction": 8, "sextile": 4, "square": 5,
                "trine": 6, "opposition": 6}
_ASPECT_ANGLE = {"conjunction": 0, "sextile": 60, "square": 90,
                 "trine": 120, "opposition": 180}

LORD_OF_SIGN = {0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun",
                5: "Mercury", 6: "Venus", 7: "Mars", 8: "Jupiter",
                9: "Saturn", 10: "Saturn", 11: "Jupiter"}

# question category → (house asked about, house of querent)
CATEGORY_HOUSES = {
    "lost_object": (2, 1),
    "marriage_timing": (7, 1),
    "job_offer": (10, 1),
    "illness_recovery": (1, 6),   # recovery = querent(1) stronger than 6th
    "travel_safe": (9, 1),
    "money_gain": (11, 2),
}


def _tajika_aspect(a: float, b: float) -> str | None:
    d = abs(a - b) % 360
    if d > 180:
        d = 360 - d
    for name, angle in _ASPECT_ANGLE.items():
        if abs(d - angle) <= _TAJIKA_ORBS[name]:
            return name
    return None


def _is_applying(lon_a: float, speed_a: float, lon_b: float,
                 speed_b: float) -> bool:
    """Simplified applying test: faster body approaches exact aspect."""
    sep = abs((lon_a - lon_b) % 360)
    if sep > 180:
        sep = 360 - sep
    rel_speed = speed_a - speed_b
    # approaching if the separation is shrinking
    return rel_speed < 0 if sep < 180 else rel_speed > 0


def compute_prashna(question_date_iso: str, question_time_hhmm: str,
                    lat: float, lon: float, tz_offset_hours: float,
                    category: str, question_text: str = "") -> dict:
    if category not in CATEGORY_HOUSES:
        raise ValueError(f"unknown category: {category}")

    d = datetime.fromisoformat(f"{question_date_iso}T{question_time_hhmm}:00")
    utc_dt = d - __import__("datetime").timedelta(hours=tz_offset_hours)

    chart = compute_chart("prashna", utc_dt.date(), utc_dt.time(),
                          tz_offset_hours=0, lat=lat, lon=lon)
    bodies = {b["body"]: b for b in chart["bodies"]}
    lons = {k: float(v["absolute_deg"]) for k, v in bodies.items()}
    asc_sid = _sidereal(float(chart["ascendant"]["absolute_deg"]), utc_dt)
    asc_idx = int(asc_sid // 30) % 12

    asked_house_num, querent_house_num = CATEGORY_HOUSES[category]
    asked_sign_idx = (asc_idx + asked_house_num - 1) % 12
    lord_name = LORD_OF_SIGN[asked_sign_idx]
    lord_lon = lons.get(lord_name)
    moon_lon_sid = _sidereal(lons["Moon"], utc_dt)
    moon_sign_idx = int(moon_lon_sid // 30) % 12

    # significator aspect check (lord of asked house vs Moon — classical)
    asp = _tajika_aspect(lord_lon, moon_lon_sid + asc_idx * 0) \
        if lord_lon else None

    # applying/separating via relative motion to Moon (~13°/day)
    lord_speed = -0.05  # placeholder slow motion; Moon dominates
    ithasala = asp and _is_applying(lord_lon, lord_speed,
                                    moon_lon_sid + asc_idx * 0, 13.2)

    verdict_positive = bool(ithasala) or (asp in ("trine", "sextile"))

    timing_th = ("ภายใน 3-7 วัน" if verdict_positive and moon_sign_idx in (0, 3, 6, 9)
                 else "ภายใน 2-4 สัปดาห์" if verdict_positive
                 else "ยังไม่ถึงจังหวะ — ลองใหม่หลังดวงจันทร์ขึ้นบวก")
    verdict_th = "มีแนวโน้มสำเร็จ" if verdict_positive else "ยังไม่ชัดเจน"
    verdict_en = "favors success" if verdict_positive else "unclear for now"

    th_narrative = (
        f'คำถามเรื่อง "{category}" — ลัคนาปราชญ์ขึ้นราศี{SIGNS_TH[asc_idx]} '
        f'ผู้ถูกถามอยู่ที่บ้านที่ {asked_house_num} มี{lord_name}เป็นเจ้าบ้าน '
        f'ดวงจันทร์โคจรราศี{SIGNS_TH[moon_sign_idx]}. '
        + (f'พบ <b>Ithasala</b> (มุมกำลังประสาน) ระหว่างเจ้าบ้านกับดวงจันทร์ '
           f'— {verdict_th}, {timing_th}' if ithasala
           else f'มุมสัมพันธ์: {asp or "ไม่มี aspect ใน orb"} — {verdict_th}')
    )
    en_narrative = (
        f"Horary ascendant {asc_idx+1}; significator {lord_name}; "
        f"Moon in sign {moon_sign_idx+1}. Aspect: {asp or 'none'}. "
        f"Ithasala: {'yes' if ithasala else 'no'} → {verdict_en}."
    )

    return {
        "system": "prashna-tajika",
        "category": category,
        "question": question_text,
        "verdict_th": verdict_th,
        "verdict_en": verdict_en,
        "timing_th": timing_th,
        "aspect": asp,
        "ithasala": bool(ithasala),
        "interpretation": {"th": th_narrative, "en": en_narrative},
    }
