"""Fixed Stars + Sabian Symbols — engine spec C:/AI/research-astrology/09.

Fixed-star longitudes are TROPICAL ecliptic, epoch J2000, hardcoded from
Brady / constellations-of-words tables. Runtime precesses them to the chart
epoch with the linear rate lon(t) = lon_J2000 + (year − 2000) × 50.29″/yr
(≈ −0.25° for a 1997 birth, ≈ +0.37° for 2026) — good to a few arcminutes
over ±100 years, which is far inside the conjunction orbs used here.

Contact rule (spec 09 §1): conjunction only — no aspects to stars. This
module's default orb is 2° per the Universe-Phase-2 mission order; the spec's
stricter luminaries ≤1° / planets ≤30′ rule is available via ``orb=``.

Sabian symbols (Jones/Rudhyar): degree number = ceil(planet_deg_in_sign)
(28.05° Taurus → Taurus 29). A compact verbatim table covers the owner
chart's Sun/Moon/ASC/MC degrees; anything else falls back to the neutral
"symbol N of sign" placeholder instead of inventing a phrase.

Chiron is intentionally NOT here — asteroids.py owns it (real Swiss
Ephemeris source when seas_18.se1 is present; this module never fabricates).
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from src.services.chart_service import SIGNS

# --------------------------------------------------------------------------
# Fixed stars — J2000 tropical ecliptic longitudes.
# Royal stars first (Aldebaran ~9.8 Gem, Regulus ~29.8 Leo, Antares ~9.7 Sag,
# Fomalhaut ~3.8 Pis), then notable contacts from spec 09.
# Gienah J2000 value carries the spec's own [VERIFY] flag; treat as secondary.
# --------------------------------------------------------------------------

FIXED_STARS: list[dict] = [
    {
        "name": "Aldebaran", "lon_j2000": 69.783, "mag": 0.85, "royal": True,
        "watcher": "East",
        "meaning_en": "Royal star of integrity and courage; success through honor, revocation if corrupted.",
        "meaning_th": "ดาวหลวงแห่งความซื่อตรงและความกล้าหาญ — สำเร็จเมื่อรักษามาตรฐาน ถ้าโกงจะถูกทวงคืนเร็ว",
    },
    {
        "name": "Regulus", "lon_j2000": 149.833, "mag": 1.35, "royal": True,
        "watcher": "North",
        "meaning_en": "Royal star of leadership; reward lasts while revenge is renounced.",
        "meaning_th": "ดาวหลวงแห่งผู้นำ — อำนาจยั่งยืนขอให้ปล่อยวางการแก้แค้น",
    },
    {
        "name": "Antares", "lon_j2000": 279.767, "mag": 0.96, "royal": True,
        "watcher": "West",
        "meaning_en": "Royal star of passion and transformation; intensity, danger of obsession.",
        "meaning_th": "ดาวหลวงแห่งตัณหาและการเปลี่ยนผ่าน — เข้มข้น ระวังหมกมุ่นจนทำลายตัวเอง",
    },
    {
        "name": "Fomalhaut", "lon_j2000": 333.867, "mag": 1.16, "royal": True,
        "watcher": "South",
        "meaning_en": "Royal star of charisma and spiritual ideals; fame through idealism.",
        "meaning_th": "ดาวหลวงแห่งเสน่ห์และอุดมคติ — ชื่อเสียงผ่านความฝันที่บริสุทธิ์",
    },
    {
        "name": "Gienah", "lon_j2000": 197.100, "mag": 2.59, "royal": False,
        "watcher": None,
        "meaning_en": "The Raven (γ Corvus): sharp instinct for people; beware exaggeration when emotional.",
        "meaning_th": "นกเรเวน — สัญชาตญาณอ่านคนเก่ง ฉลาดส่งสาร ระวังเล่าเกินจริงเวลาอารมณ์พลิก",
    },
    {
        "name": "Alcyone", "lon_j2000": 59.967, "mag": 2.87, "royal": False,
        "zone": "Pleiades cluster spans ~28 Tau–0 Gem — treat wide hits as zone-only.",
        "meaning_en": "Brightest Pleiad: mysticism, sorrow that refines, collective feminine themes.",
        "meaning_th": "เอลไซโอนแห่งลูกไก่ — เสพย์สัมผัสเหนือธรรมชาติ ความศรัทธา ความเศร้าที่ขัดเกลาจิต",
    },
    {
        "name": "Sirius", "lon_j2000": 183.130, "mag": -1.46, "royal": False,
        "watcher": None,
        "meaning_en": "Brightest star in the sky: fame, honor, spiritual power.",
        "meaning_th": "ดาวที่สว่างที่สุด — ชื่อเสียง เกียรติภูมิ พลังทางจิตวิญญาณ",
    },
    {
        "name": "Spica", "lon_j2000": 225.583, "mag": 0.98, "royal": False,
        "watcher": None,
        "meaning_en": "The sheaf of wheat: talent, brilliance, protection.",
        "meaning_th": "รวงข้าว — ความเก่งกาจ ความสว่างไสว คุ้มครองให้รอด",
    },
]

# Precession rate: 50.29 arcsec/year = 0.01397 deg/year from J2000.
PRECESSION_RATE = 50.29 / 3600.0


def star_longitude_at(when: datetime, lon_j2000: float) -> float:
    """Tropical longitude of a star at `when` (linear precession from J2000)."""
    dt = when if when.tzinfo else when.replace(tzinfo=timezone.utc)
    year_frac = dt.year + (dt.timetuple().tm_yday - 1 + dt.hour / 24) / 365.2425
    return (lon_j2000 + (year_frac - 2000.0) * PRECESSION_RATE) % 360.0


def _stars_at(when: datetime) -> list[dict]:
    out = []
    for s in FIXED_STARS:
        row = dict(s)
        row["longitude"] = round(star_longitude_at(when, s["lon_j2000"]), 4)
        row["precessed_from_j2000_deg"] = round(row["longitude"] - s["lon_j2000"], 4)
        out.append(row)
    return out


def _angular_sep(a: float, b: float) -> float:
    diff = abs(a - b) % 360.0
    return diff if diff <= 180 else 360 - diff


def _natal_points(natal_chart: dict) -> list[dict]:
    points = [
        {"body": b["body"], "longitude": b["absolute_deg"]}
        for b in natal_chart.get("bodies", [])
    ]
    asc = natal_chart.get("ascendant")
    if asc:
        points.append({"body": "ASC", "longitude": asc["absolute_deg"]})
    mc = natal_chart.get("midheaven")
    if mc:
        points.append({"body": "MC", "longitude": mc["absolute_deg"]})
    return points


def find_fixed_star_conjunctions(
    natal_chart: dict,
    when: datetime | None = None,
    orb: float = 2.0,
) -> list[dict]:
    """Conjunctions between natal planets/angles and fixed stars.

    Stars are precessed to the NATAL epoch by default (that is when the
    contact was made); pass an explicit `when` to evaluate another moment.
    """
    when = when or _natal_epoch(natal_chart)
    stars = {s["name"]: s for s in _stars_at(when)}

    contacts = []
    for pt in _natal_points(natal_chart):
        for name, star in stars.items():
            sep = _angular_sep(pt["longitude"], star["longitude"])
            if sep <= orb:
                idx = int(star["longitude"] // 30) % 12
                contacts.append({
                    "star": name,
                    "royal": star["royal"],
                    "star_longitude_tropical": star["longitude"],
                    "star_sign": SIGNS[idx],
                    "natal_point": pt["body"],
                    "natal_longitude": round(pt["longitude"], 4),
                    "orb_deg": round(sep, 4),
                    "magnitude": star["mag"],
                    "meaning_en": star["meaning_en"],
                    "meaning_th": star["meaning_th"],
                    **({"zone_note": star["zone"]} if star.get("zone") else {}),
                })
    contacts.sort(key=lambda c: c["orb_deg"])
    return contacts


def _natal_epoch(natal_chart: dict) -> datetime:
    raw = natal_chart.get("datetime_utc") or ""
    try:
        stamp = str(raw).rstrip("Z")
        return datetime.fromisoformat(stamp).replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime.now(timezone.utc)


# --------------------------------------------------------------------------
# Sabian symbols (Jones/Rudhyar). Compact verbatim table for the owner-chart
# points; everything else falls back to "symbol N of sign" (no invention).
# Key: (SIGNS index 0=Aries..11=Pisces, degree number 1..30 where N = ceil(deg)).
# --------------------------------------------------------------------------

SABIAN_TABLE: dict[tuple[int, int], tuple[str, str]] = {
    # Owner Sun — Taurus 28.05° → Taurus 29
    (1, 29): (
        "Two cobblers working at a table",
        "ช่างทำรองเท้าสองคนกำลังทำงานที่โต๊ะเดียวกัน — ความชำนาญผ่านการฝีมือช่าง ทำงานเป็นทีมเงียบๆ คุณค่ามาจากความละเอียด",
    ),
    # Owner Moon — Libra 17.37° → Libra 18
    (6, 18): (
        "Two men placed under arrest",
        "ชายสองคนถูกจับกุม — บทเรียนอารมณ์: ผลจากการฝ่าฝืนกติกาสังคม/ความยุติธรรม ต้องรับผิดร่วมกัน ใคร่ครวญเรื่องขอบเขต",
    ),
    # Owner ASC — Taurus ~25.9° → Taurus 26
    (1, 26): (
        "A Spanish gallant serenades his beloved",
        "หนุ่มสเปนเซเรนาเดขับกล่อมคนรัก — บุคลิกภายนอกโรแมนติกมีศิลป์ กล้าแสดงความรู้สึกแบบมีริทึมของตัวเอง",
    ),
    # Owner MC — Aquarius 16.43° → Aquarius 17
    (10, 17): (
        "A watchdog standing guard",
        "สุนัขเฝ้ายามปกป้องเจ้านาย — อาชีพ/ภาพลักษณ์: ผู้พิทักษ์ระบบ/เทคโนโลยีที่เชื่อถือได้ มาตรฐานสูงเรื่องความภักดี",
    ),
}

_SABIAN_SOURCE = "Rudhyar, An Astrological Mandala (table entries verbatim)"


def sabian_symbol(longitude: float) -> dict:
    """Sabian symbol for an absolute tropical longitude.

    Indexing per spec 09: number = ceil(degree within sign), so any value in
    [N−1, N) maps to symbol N of the sign.
    """
    longitude %= 360.0
    sign_idx = int(longitude // 30)
    deg = longitude % 30
    number = min(30, max(1, math.ceil(round(deg, 6))))
    phrase_en, phrase_th = SABIAN_TABLE.get(
        (sign_idx, number),
        (f"symbol {number} of sign {sign_idx}", f"สัญลักษณ์ที่ {number} ของราศีที่ {sign_idx}"),
    )
    return {
        "sign": SIGNS[sign_idx],
        "degree": round(deg, 4),
        "number": number,
        "phrase_en": phrase_en,
        "phrase_th": phrase_th,
        "verbatim": (sign_idx, number) in SABIAN_TABLE,
        "source": _SABIAN_SOURCE if (sign_idx, number) in SABIAN_TABLE else "fallback-index",
    }


# --------------------------------------------------------------------------
# Module entry point
# --------------------------------------------------------------------------

_SABIAN_POINTS = ("Sun", "Moon")


def compute_fixed_stars(natal_chart: dict, when: datetime | None = None, orb: float = 2.0) -> dict:
    """Main entry point: royal-star contacts + Sabian symbols for Sun/Moon/ASC/MC."""
    when = when or _natal_epoch(natal_chart)
    contacts = find_fixed_star_conjunctions(natal_chart, when, orb)

    sabian: dict[str, dict] = {}
    for pt in _natal_points(natal_chart):
        key = pt["body"].lower()
        if key in ("sun", "moon", "asc", "mc"):
            sabian[key] = sabian_symbol(pt["longitude"])

    return {
        "status": "ok",
        "orb_deg": orb,
        "evaluated_at": when.isoformat(),
        "precession_note": "J2000 longitudes + 50.29\"/yr linear precession to chart epoch",
        "conjunctions": contacts,
        "royal_star_contacts": [c for c in contacts if c["royal"]],
        "sabian": sabian,
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }
