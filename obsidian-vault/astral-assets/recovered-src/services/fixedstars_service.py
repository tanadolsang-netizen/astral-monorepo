"""Fixed Stars / Sabian / Decans / Arabic Lots — engine spec 09 service layer.

Complements ``src/services/grand/fixed_stars.py`` (which owns the J2000 star
table, linear precession and the compact Sabian table). This service adds the
spec-09 layers that module does not carry:

1. **Strict-orb star contacts** (§1): conjunction only — luminaries ≤1°,
   planets ≤30′, ASC/MC ≤1°. Nothing outside is counted (ห้ามยืด).
2. **Decans** (§3): standard Chaldean faces lookup (Agrippa order), e.g.
   Taurus 3rd face = Saturn — matching the spec's worked example.
3. **Arabic Lots** (§4): Fortune/Spirit with correct day/night formulas plus
   the Hermes/Paulus Marriage lot. Sect comes from the Sun's real altitude
   when coordinates are supplied (borderline |alt| ≤5° ⇒ BOTH variants are
   returned and flagged ``sect_uncertain``, mirroring the spec's 05:45 vs
   sunrise ~05:52 case); without coordinates a purely zodiacal horizon rule
   applies and is labelled as such.

Every interpretive block carries ``th`` + ``en`` in natural astrologer voice,
and the integrated reading keeps to max ONE sentence per layer (§5) with the
spec's confidence tags: stars HIGH · Sabian MED · Lots MED (sect-flagged).

Deterministic throughout; never raises on missing data — degraded layers
return explicit reasons instead of invented text.
"""

from __future__ import annotations

from datetime import datetime, timezone

from src.services.chart_service import SIGNS
from src.services.grand.fixed_stars import (
    find_fixed_star_conjunctions,
    sabian_symbol,
)

# ---------------------------------------------------------------------------
# Decans — Chaldean faces (per sign: ruler of 0–10°, 10–20°, 20–30°)
# ---------------------------------------------------------------------------

DECAN_RULERS: list[list[str]] = [
    ["Mars", "Sun", "Venus"],        # Aries
    ["Mercury", "Moon", "Saturn"],   # Taurus  (3rd = Saturn ✓ spec 09 §3)
    ["Jupiter", "Mars", "Sun"],      # Gemini
    ["Venus", "Mercury", "Moon"],    # Cancer
    ["Saturn", "Jupiter", "Mars"],   # Leo
    ["Sun", "Venus", "Mercury"],     # Virgo
    ["Moon", "Saturn", "Jupiter"],   # Libra
    ["Mars", "Sun", "Venus"],        # Scorpio
    ["Mercury", "Moon", "Saturn"],   # Sagittarius
    ["Jupiter", "Mars", "Sun"],      # Capricorn
    ["Venus", "Mercury", "Moon"],    # Aquarius
    ["Saturn", "Jupiter", "Mars"],   # Pisces
]

_DECAN_RULER_TH = {
    "Mars": "ดาวอังคาร", "Sun": "ดาวอาทิตย์", "Venus": "ดาวศุกร์",
    "Mercury": "ดาวพุธ", "Moon": "ดวงจันทร์", "Saturn": "ดาวเสาร์",
    "Jupiter": "ดาวพฤหัส",
}

_DECAN_QUALITY_EN = {
    "Saturn": "mastery through patience and structure — builds slowly but permanently, distrusts shortcuts",
    "Jupiter": "expansion through generosity and vision — luck grows when it is shared outward",
    "Mars": "drive through courage and initiative — acts first, refines later",
    "Sun": "vitality through mastery and honour — shines when leading honestly",
    "Venus": "grace through art and harmony — attracts what it appreciates",
    "Mercury": "cleverness through craft and words — wins by precision, not force",
    "Moon": "depth through feeling and adaptation — reads the room before it speaks",
}
_DECAN_QUALITY_TH = {
    "Saturn": "ความชำนาญผ่านความอดทนและโครงสร้าง สร้างช้าแต่มั่นคง ไม่เชื่อทางลัด",
    "Jupiter": "การขยายตัวผ่านความใหญ่และวิสัยทัศน์ โชคขยายเมื่อแบ่งปันออกไป",
    "Mars": "แรงขับผ่านความกล้าและการลงมือก่อน ค่อยเก็บรายละเอียดทีหลัง",
    "Sun": "พลังชีวิตผ่านความเชี่ยวชาญและเกียรติ เปล่งประกายเมื่อนำแบบซื่อตรง",
    "Venus": "เสน่ห์ผ่านศิลป์และความกลมกลืน ดึงดูดสิ่งที่ตัวเองให้คุณค่า",
    "Mercury": "ความฉลาดผ่านฝีมือและถ้อยคำ ชนะด้วยความละเอียด ไม่ใช้แรง",
    "Moon": "ความลึกผ่านอารมณ์และการปรับตัว อ่านสถานการณ์เก่งก่อนจะพูด",
}

_ORDINAL_EN = {1: "1st", 2: "2nd", 3: "3rd"}
_POINT_TH = {
    "Sun": "ดวงอาทิตย์", "Moon": "ดวงจันทร์", "ASC": "ลัคนา", "MC": "มัชฌิมฯ",
}


def _sign_idx(longitude: float) -> int:
    return int((longitude % 360.0) // 30)


def _sign_en(idx: int) -> str:
    label = SIGNS[idx]
    return label[label.index("(") + 1 : label.rindex(")")] if "(" in label else label


def _sign_th(idx: int) -> str:
    label = SIGNS[idx]
    return label.split("(")[0].strip()


def _ordinal_th(n: int) -> str:
    return {1: "ที่ 1", 2: "ที่ 2", 3: "ที่ 3"}[n]


def decan_of(longitude: float) -> dict:
    """Chaldean-face decan for an absolute tropical longitude."""
    longitude %= 360.0
    idx = _sign_idx(longitude)
    deg_in_sign = longitude % 30.0
    n = min(3, int(deg_in_sign // 10) + 1)
    ruler = DECAN_RULERS[idx][n - 1]
    sign_en, sign_th = _sign_en(idx), _sign_th(idx)
    return {
        "sign": sign_en,
        "sign_th": sign_th,
        "degree_in_sign": round(deg_in_sign, 4),
        "decan_number": n,
        "ruler": ruler,
        "ruler_th": _DECAN_RULER_TH[ruler],
        "quality_en": _DECAN_QUALITY_EN[ruler],
        "quality_th": _DECAN_QUALITY_TH[ruler],
        "line_en": (
            f"{sign_en} {_ORDINAL_EN[n]} decan, ruled by {ruler} — "
            f"{_DECAN_QUALITY_EN[ruler]}."
        ),
        "line_th": (
            f"ดีแคน{_ordinal_th(n)}ของ{sign_th} ปกครองโดย{_DECAN_RULER_TH[ruler]} "
            f"— {_DECAN_QUALITY_TH[ruler]}"
        ),
    }


# ---------------------------------------------------------------------------
# Sect detection — real solar altitude when possible, zodiacal rule otherwise
# ---------------------------------------------------------------------------

_BORDERLINE_ALT_DEG = 5.0


def solar_altitude_deg(natal_chart: dict, lat: float, lon: float) -> float | None:
    """True solar altitude at the birth instant/place, or None on failure."""
    try:
        from skyfield.api import wgs84

        from src.services.ephemeris import earth, eph, ts
    except Exception:
        return None
    try:
        stamp = str(natal_chart.get("datetime_utc", "")).rstrip("Z")
        dt = datetime.fromisoformat(stamp)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        observer = earth + wgs84.latlon(float(lat), float(lon))
        alt = (
            observer.at(ts.from_datetime(dt))
            .observe(eph["sun"])
            .apparent()
            .altaz()[0]
            .degrees
        )
        return float(alt)
    except Exception:
        return None


def solar_sect(natal_chart: dict, lat: float | None = None, lon: float | None = None) -> dict:
    """Day/night sect of the chart, with an honest method label."""
    sun = next(
        (b for b in natal_chart.get("bodies", []) if b["body"] == "Sun"), None,
    )
    asc = natal_chart.get("ascendant")
    if not sun or not asc:
        return {"sect": None, "uncertain": True, "method": "missing_sun_or_asc"}

    if lat is not None and lon is not None:
        alt = solar_altitude_deg(natal_chart, lat, lon)
        if alt is not None:
            return {
                "sect": "day" if alt > 0 else "night",
                "sun_altitude_deg": round(alt, 3),
                "uncertain": abs(alt) <= _BORDERLINE_ALT_DEG,
                "method": "solar_altitude",
            }

    diff = (float(sun["absolute_deg"]) - float(asc["absolute_deg"])) % 360.0
    above_horizon = diff > 180.0  # houses 7→12 sit above the horizon
    return {
        "sect": "day" if above_horizon else "night",
        "sun_altitude_deg": None,
        "uncertain": False,
        "method": "zodiacal_horizon_rule",
    }


def _norm(lon: float) -> float:
    return lon % 360.0


def arabic_lots(
    natal_chart: dict,
    lat: float | None = None,
    lon: float | None = None,
) -> dict:
    """Fortune / Spirit / Marriage (Hermes-Paulus) lots with sect handling."""
    def body_lon(name: str) -> float | None:
        b = next((x for x in natal_chart.get("bodies", []) if x["body"] == name), None)
        return float(b["absolute_deg"]) if b else None

    asc_b = natal_chart.get("ascendant")
    if not asc_b:
        return {"status": "unavailable", "reason": "no_ascendant_birth_time_unknown"}
    asc = float(asc_b["absolute_deg"])
    sun, moon, venus, saturn = (body_lon(n) for n in ("Sun", "Moon", "Venus", "Saturn"))
    if None in (sun, moon):
        return {"status": "unavailable", "reason": "missing_sun_or_moon"}

    sect_info = solar_sect(natal_chart, lat, lon)
    sect = sect_info.get("sect") or "day"

    def fortune(s: str) -> float:
        return _norm(asc + moon - sun) if s == "day" else _norm(asc + sun - moon)

    def spirit(s: str) -> float:
        return _norm(asc + sun - moon) if s == "day" else _norm(asc + moon - sun)

    marriage = None
    if venus is not None and saturn is not None:
        marriage = _norm(asc + venus - saturn)  # Hermes/Paulus male-chart formula

    lots: dict[str, dict] = {}
    variants = [sect] + ([("day" if sect == "night" else "night")] if sect_info.get("uncertain") else [])
    for s in variants:
        tag = "" if s == sect else "_other_sect"
        lots[f"fortune{tag}"] = {
            "formula": "ASC+Moon−Sun" if s == "day" else "ASC+Sun−Moon",
            "sect_assumed": s,
            "longitude": round(fortune(s), 4),
            **_sign_of(fortune(s)),
        }
        lots[f"spirit{tag}"] = {
            "formula": "ASC+Sun−Moon" if s == "day" else "ASC+Moon−Sun",
            "sect_assumed": s,
            "longitude": round(spirit(s), 4),
            **_sign_of(spirit(s)),
        }
    if marriage is not None:
        lots["marriage"] = {
            "formula": "ASC+Venus−Saturn (Hermes/Paulus)",
            "longitude": round(marriage, 4),
            **_sign_of(marriage),
            "note": "some authors swap Venus/Saturn roles — formula pinned to Paulus",
        }

    return {
        "status": "ok",
        "sect": sect,
        "sect_method": sect_info.get("method"),
        "sun_altitude_deg": sect_info.get("sun_altitude_deg"),
        "sect_uncertain": bool(sect_info.get("uncertain")),
        "confidence": "MED",
        "lots": lots,
    }


def _sign_of(lon: float) -> dict:
    idx = _sign_idx(lon)
    return {"sign": _sign_en(idx), "sign_th": _sign_th(idx), "degree_in_sign": round(lon % 30.0, 4)}


# ---------------------------------------------------------------------------
# Strict-orb fixed-star contacts (spec §1: luminary ≤1°, planet ≤30′, angle ≤1°)
# ---------------------------------------------------------------------------

_STRICT_ORB_PLANET = 30.0 / 60.0
_STRICT_ORB_LUMINARY_ANGLE = 1.0


def strict_orb_for(point_name: str) -> float:
    name = point_name.upper()
    if name in ("SUN", "MOON"):
        return _STRICT_ORB_LUMINARY_ANGLE
    if name in ("ASC", "MC"):
        return _STRICT_ORB_LUMINARY_ANGLE
    return _STRICT_ORB_PLANET


def strict_star_contacts(natal_chart: dict, when: datetime | None = None) -> list[dict]:
    """Star conjunctions under the spec's own orb rules (never widened)."""
    out: list[dict] = []
    points = [
        (b["body"], float(b["absolute_deg"]))
        for b in natal_chart.get("bodies", [])
    ]
    if natal_chart.get("ascendant"):
        points.append(("ASC", float(natal_chart["ascendant"]["absolute_deg"])))
    if natal_chart.get("midheaven"):
        points.append(("MC", float(natal_chart["midheaven"]["absolute_deg"])))

    for pt_name, pt_lon in points:
        orb_limit = strict_orb_for(pt_name)
        hits = find_fixed_star_conjunctions(
            {**natal_chart, "bodies": [
                b for b in natal_chart.get("bodies", []) if b["body"] == pt_name
            ], "ascendant": natal_chart.get("ascendant") if pt_name == "ASC" else None,
             "midheaven": natal_chart.get("midheaven") if pt_name == "MC" else None},
            when=when, orb=orb_limit,
        )
        for h in hits:
            h["orb_rule"] = f"≤{orb_limit:g}° ({pt_name})"
            h["confidence"] = "HIGH"
        out.extend(hits)
    out.sort(key=lambda c: c["orb_deg"])
    return out


# ---------------------------------------------------------------------------
# Integrated layer output — max one sentence per layer (spec §5)
# ---------------------------------------------------------------------------

_SABIAN_POINTS = (("Sun", "sun"), ("Moon", "moon"), ("ASC", "asc"), ("MC", "mc"))


def _chart_point_lon(natal_chart: dict, name: str) -> float | None:
    if name in ("ASC", "MC"):
        key = "ascendant" if name == "ASC" else "midheaven"
        p = natal_chart.get(key)
        return float(p["absolute_deg"]) if p else None
    b = next((x for x in natal_chart.get("bodies", []) if x["body"] == name), None)
    return float(b["absolute_deg"]) if b else None


def compute_fixedstars_layer(
    natal_chart: dict,
    lat: float | None = None,
    lon: float | None = None,
    when: datetime | None = None,
) -> dict:
    """Full spec-09 layer: strict stars + Sabian + decans + lots, TH/EN."""
    when = when or datetime.now(timezone.utc)

    # --- stars ---------------------------------------------------------
    contacts = strict_star_contacts(natal_chart, when)
    royal = [c for c in contacts if c.get("royal")]
    if contacts:
        top = contacts[0]
        stars_line_en = (
            f"{top['natal_point']} sits on fixed star {top['star']} "
            f"(orb {top['orb_deg']:.2f}°) — {top['meaning_en']}"
        )
        stars_line_th = (
            f"{_POINT_TH.get(top['natal_point'], top['natal_point'])}ขึ้นบนดาว{top['star']} "
            f"(ลูกโค้ง {top['orb_deg']:.2f}°) — {top['meaning_th']}"
        )
        if royal:
            stars_line_en += ". A Royal Star: integrity attached."
            stars_line_th += " เป็นดาวหลวง — ผูกกับความซื่อตรงไว้ด้วย"
    else:
        stars_line_en = "no fixed-star contact inside the strict orbs"
        stars_line_th = "ไม่มีดาวฤกษ์ตรึงในลูกโค้งที่กำหนด"

    # --- sabian (reuse grand module's verbatim table) -------------------
    sabian: dict[str, dict] = {}
    for name, key in _SABIAN_POINTS:
        lon_pt = _chart_point_lon(natal_chart, name)
        if lon_pt is not None:
            sym = sabian_symbol(lon_pt)
            sym["line_en"] = f"{name}: “{sym['phrase_en']}”"
            sym["line_th"] = f"{_POINT_TH[name]}: “{sym['phrase_th']}”"
            sabian[key] = sym
    sab_focus = sabian.get("sun") or next(iter(sabian.values()), None)
    sab_line_en = sab_focus["line_en"] if sab_focus else "sabian unavailable"
    sab_line_th = sab_focus["line_th"] if sab_focus else "ซาเบียนไม่พร้อมใช้งาน"

    # --- decans ----------------------------------------------------------
    decans: dict[str, dict] = {}
    for name in ("Sun", "Moon", "ASC"):
        lon_pt = _chart_point_lon(natal_chart, name)
        if lon_pt is not None:
            d = decan_of(lon_pt)
            d["line_en"] = f"{name}: {d['line_en']}"
            d["line_th"] = f"{_POINT_TH[name]}: {d['line_th']}"
            decans[name.lower()] = d
    dec_focus = decans.get("sun") or next(iter(decans.values()), None)
    dec_line_en = dec_focus["line_en"] if dec_focus else "decans unavailable"
    dec_line_th = dec_focus["line_th"] if dec_focus else "ดีแคนไม่พร้อมใช้งาน"

    # --- lots -------------------------------------------------------------
    lots_block = arabic_lots(natal_chart, lat, lon)
    if lots_block.get("status") == "ok":
        fl = lots_block["lots"]
        main_key = "fortune" if "fortune" in fl else next(iter(fl))
        fort = fl[main_key]
        unc = ", sect-uncertain so both day/night variants printed" if lots_block["sect_uncertain"] else ""
        lots_line_en = (
            f"Lot of Fortune at {fort['degree_in_sign']:.2f}° {fort['sign']} ({fort['formula']}){unc}"
        )
        lots_line_th = (
            f"ลอตฟอร์จูน {fort['degree_in_sign']:.2f}° {fort['sign_th']} ({fort['formula']})"
            + (" กำเนิดอยู่เส้นแบ่งกลางวัน-กลางคืน จึงพิมพ์ทั้งสองสูตร" if lots_block["sect_uncertain"] else "")
        )
    else:
        lots_line_en = "lots suppressed — no birth time"
        lots_line_th = "ลอตถูกซ่อน — ไม่มีเวลาเกิด"

    return {
        "status": "ok",
        "evaluated_at": when.isoformat(),
        "stars": {
            "contacts": contacts,
            "royal_contacts": royal,
            "confidence": "HIGH",
            "orb_rules": {
                "luminaries": "<=1deg", "planets": "<=30arcmin", "angles": "<=1deg",
                "note": "conjunction only — never widened",
            },
            "line_en": stars_line_en,
            "line_th": stars_line_th,
        },
        "sabian": {"points": sabian, "confidence": "MED",
                   "line_en": sab_line_en, "line_th": sab_line_th},
        "decans": {"points": decans, "system": "chaldean_faces",
                   "line_en": dec_line_en, "line_th": dec_line_th},
        "lots": {**lots_block, "line_en": lots_line_en, "line_th": lots_line_th},
        "reading": {
            "th": " · ".join([
                f"ดาวฤกษ์: {stars_line_th}", f"ซาเบียน: {sab_line_th}",
                f"ดีแคน: {dec_line_th}", f"ลอต: {lots_line_th}",
            ]),
            "en": " | ".join([
                f"Stars: {stars_line_en}", f"Sabian: {sab_line_en}",
                f"Decan: {dec_line_en}", f"Lots: {lots_line_en}",
            ]),
        },
    }
