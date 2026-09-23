"""Major Asteroids + Chiron (Ceres, Pallas, Juno, Vesta, Chiron) — real positions.

Phase 4.7 (2026-08-23) — REAL via Swiss Ephemeris:

- ``pyswisseph`` (Swiss Ephemeris 2.10) computes all five bodies in-process.
- The three ephemeris files (``seas_18.se1`` main asteroids, ``sepl_18.se1``
  planets, ``semo_18.se1`` Moon; 1800–2399 CE, 1.92 MB total) are vendored in
  ``<repo>/ephe/`` and COMMITTED so deploys work offline. Source:
  github.com/aloistr/swisseph/master/ephe (byte-verified by ATLAS,
  research-astrology/data/asteroids_ephe_guide.json, commit b5ac4d0).
- Body ids: Chiron = 15 (swe.CHIRON); the four major asteroids are numbered
  minor planets ``swe.AST_OFFSET + n`` = 10001 Ceres, 10002 Pallas,
  10003 Juno, 10004 Vesta (swe.CERES/PALLAS/JUNO/VESTA are aliases of these).
  Verified live: calc_ut(jd, 17) == calc_ut(jd, 10001).
- Frames: tropical geocentric (Swiss Ephemeris default) AND sidereal Lahiri
  computed with the same ``chart_service.lahiri_ayanamsa`` linear formula the
  rest of the app's vedic pipeline uses, so sections stay mutually
  consistent. Ground truth (M, 1997-05-19 05:45 ICT = JD 2450587.447917):
  Chiron tropical 206.7767° (26°46' Libra Rx) — pinned in tests.
- Skyfield's de421.bsp does NOT carry these bodies (no asteroid/centaur
  segments), so if pyswisseph is missing or a file is absent every
  entrypoint degrades gracefully to
  ``{'status': 'unavailable', 'reason': ...}`` — never raises.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path

from src.services.chart_service import SIGNS, _to_sign, lahiri_ayanamsa

# Swiss Ephemeris optional import — the whole module stays importable without it.
try:  # pragma: no cover - depends on interpreter/wheel availability
    import swisseph as _swe
except Exception as _exc:  # ImportError, or broken .so/.pyd on this runtime
    _swe = None
    _SWE_IMPORT_ERROR = str(_exc)
else:
    _SWE_IMPORT_ERROR = ""

# Swiss Ephemeris body ids (asteroids_ephe_guide.json, verified live 2026-08-23):
# Chiron=15; Ceres/Pallas/Juno/Vesta = AST_OFFSET(10000) + minor-planet number.
_AST_OFFSET = getattr(_swe, "AST_OFFSET", 10000) if _swe is not None else 10000
_SWE_BODIES = {
    "Chiron": 15,
    "Ceres": _AST_OFFSET + 1,  # 10001 (swe.CERES alias)
    "Pallas": _AST_OFFSET + 2,  # 10002 (swe.PALLAS alias)
    "Juno": _AST_OFFSET + 3,  # 10003 (swe.JUNO alias)
    "Vesta": _AST_OFFSET + 4,  # 10004 (swe.VESTA alias)
}

# Mean Lilith (mean lunar apogee) — spec 10 §1 decision: MEAN for v1 (stable;
# astro.com default; the osculating apogee swings ±2°+/day). Computed by
# pyswisseph analytically/semi-analytically — no extra .se1 file needed beyond
# the vendored sepl/semo pair already required for the planets.
MEAN_APOG_ID = getattr(_swe, "MEAN_APOG", 12) if _swe is not None else 12

NATURE = {
    "Chiron": "The Wounded Healer — core wound turned into healing gift",
    "Ceres": "Nurture, agriculture, loss/return, mothering",
    "Pallas": "Wisdom, strategy, pattern recognition, creative intelligence",
    "Juno": "Partnership, marriage, commitment, equality in relationships",
    "Vesta": "Devotion, focus, sacred work, sexuality/spirituality integration",
    "Lilith": (
        "Mean Lilith (mean lunar apogee) — untamed shadow desire; where "
        "suppression backfires and integration becomes a power source"
    ),
}

# <repo>/ephe/ — vendored Swiss Ephemeris files, committed for offline deploys.
# (this file is <repo>/src/services/grand/asteroids.py → parents[3] = repo root)
EPHE_DIR = Path(__file__).resolve().parents[3] / "ephe"
_REQUIRED_EPHE_FILES = ("seas_18.se1", "sepl_18.se1", "semo_18.se1")


def _unavailable(reason: str) -> dict:
    return {"status": "unavailable", "reason": reason, "positions": {}, "computed_at": None}


def _jd_utc(dt_utc: datetime) -> float:
    """Julian day (UT) from an aware datetime."""
    dt_utc = dt_utc.astimezone(timezone.utc)
    hour = dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600 + dt_utc.microsecond / 3.6e9
    return _swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour)


def _year_frac(dt_utc: datetime) -> float:
    """chart_service's fractional year (drives its Lahiri ayanamsa formula)."""
    return dt_utc.year + (dt_utc.timetuple().tm_yday / 365.2425)


def _positions_at_instant(dt_utc: datetime) -> tuple[dict[str, dict], list[str]]:
    """Chiron + 4 asteroids at one instant: tropical + sidereal Lahiri."""
    jd = _jd_utc(dt_utc)
    ayanamsa = lahiri_ayanamsa(_year_frac(dt_utc))
    positions: dict[str, dict] = {}
    errors: list[str] = []
    for name, body_id in _SWE_BODIES.items():
        try:
            xx, _retflag = _swe.calc_ut(jd, body_id, _swe.FLG_SWIEPH | _swe.FLG_SPEED)
            lon = xx[0] % 360.0
            sid = (lon - ayanamsa) % 360.0
            sign, deg = _to_sign(lon)
            sid_sign, sid_deg = _to_sign(sid)
            positions[name] = {
                "body": name,
                "sign": sign,
                "degree": round(deg, 4),
                "absolute_deg": round(lon, 4),
                "sidereal": {
                    "sign": sid_sign,
                    "degree": round(sid_deg, 4),
                    "absolute_deg": round(sid, 4),
                },
                "speed_lon_deg_per_day": round(xx[3], 6),
                "retrograde": xx[3] < 0,
                "nature": NATURE[name],
            }
        except Exception as exc:
            errors.append(f"{name}: {exc}")
    return positions, errors


def compute_asteroid_positions(now_utc: datetime | None = None) -> dict:
    """Tropical + sidereal Lahiri longitudes of Chiron + the four asteroids.

    ``now_utc`` defaults to the current instant. Returns
    ``{'status': 'ok'|'partial'|'unavailable', ...}``. Never raises.
    """
    now_utc = now_utc or datetime.now(timezone.utc)

    if _swe is None:
        return _unavailable(
            "pyswisseph is not installed on this runtime "
            f"(import failed: {_SWE_IMPORT_ERROR}); de421.bsp does not carry "
            "Chiron/asteroids, so no real source is available"
        )

    missing = [f for f in _REQUIRED_EPHE_FILES if not (EPHE_DIR / f).exists()]
    try:
        if EPHE_DIR.is_dir():
            _swe.set_ephe_path(str(EPHE_DIR))
        positions, errors = _positions_at_instant(now_utc)
    except Exception as exc:
        return _unavailable(f"swisseph setup failed: {exc}")

    if not positions:
        # Typical cause: the Swiss Ephemeris .se1 files are absent.
        hint = (
            f"swiss ephemeris returned no positions ({'; '.join(errors[:2])}). "
            f"Place {'+'.join(_REQUIRED_EPHE_FILES)} in {EPHE_DIR} to enable"
        )
        if missing:
            hint = f"missing ephemeris files {missing} in {EPHE_DIR} — {hint}"
        return _unavailable(hint)

    return {
        "status": "ok" if not errors else "partial",
        "source": "swisseph/seas_18+sepl_18+semo_18 (vendored in ephe/)",
        "frames": ["tropical", "sidereal_lahiri"],
        "errors": errors or None,
        "positions": positions,
        "computed_at": now_utc.isoformat(),
    }


_ASPECT_ANGLES = {
    "conjunction": 0.0,
    "sextile": 60.0,
    "square": 90.0,
    "trine": 120.0,
    "opposition": 180.0,
}


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


def asteroid_aspects_to_natal(asteroid_positions: dict, natal_chart: dict, orb: float = 2.0) -> list[dict]:
    """Aspects from transiting asteroids/Chiron to natal planets/angles."""
    aspects: list[dict] = []
    for ast_name, ast_data in asteroid_positions.items():
        ast_lon = ast_data["absolute_deg"]
        for pt in _natal_points(natal_chart):
            sep = _angular_sep(ast_lon, pt["longitude"])
            for aspect_name, angle in _ASPECT_ANGLES.items():
                gap = abs(sep - angle)
                if gap <= orb:
                    aspects.append({
                        "asteroid": ast_name,
                        "aspect": aspect_name,
                        "natal_point": pt["body"],
                        "orb_deg": round(gap, 2),
                        "asteroid_sign": ast_data["sign"],
                        "asteroid_degree": ast_data["degree"],
                        "nature": NATURE.get(ast_name, ""),
                    })
                    break
    aspects.sort(key=lambda a: a["orb_deg"])
    return aspects


def natal_asteroid_positions(natal_chart: dict) -> dict:
    """Chiron + asteroids at the chart's own birth instant (any chart).

    Reads ``natal_chart['datetime_utc']`` (chart_service serialisation:
    isoformat + trailing ``Z``). Graceful under every failure.
    """
    if _swe is None:
        return _unavailable(f"pyswisseph not installed: {_SWE_IMPORT_ERROR}")
    try:
        s = str(natal_chart.get("datetime_utc", "")).strip()
        if s.endswith("Z"):
            s = s[:-1]
        birth_utc = datetime.fromisoformat(s)
        if birth_utc.tzinfo is None:
            birth_utc = birth_utc.replace(tzinfo=timezone.utc)
    except ValueError:
        return _unavailable("invalid_or_missing_datetime_utc")
    try:
        if EPHE_DIR.is_dir():
            _swe.set_ephe_path(str(EPHE_DIR))
        positions, errors = _positions_at_instant(birth_utc)
    except Exception as exc:
        return _unavailable(f"swisseph setup failed: {exc}")
    if not positions:
        return _unavailable(f"no positions ({'; '.join(errors[:2])})")
    return {
        "status": "ok" if not errors else "partial",
        "errors": errors or None,
        "positions": positions,
        "computed_at": birth_utc.isoformat(),
    }


def compute_asteroids(
    natal_chart: dict,
    now_utc: datetime | None = None,
    transit_orb: float = 2.0,
) -> dict:
    """Main entry point for the Asteroids module. Graceful under all failures.

    Returns transit positions (now), NATAL positions at the chart instant,
    and transit→natal aspects.
    """
    now_utc = now_utc or datetime.now(timezone.utc)
    try:
        result = compute_asteroid_positions(now_utc)
    except Exception as exc:  # absolute last-resort guard — must never crash
        result = _unavailable(f"unexpected asteroid computation failure: {exc}")

    if result.get("status") == "unavailable":
        return result

    result["natal_positions"] = natal_asteroid_positions(natal_chart)
    result["transit_aspects"] = asteroid_aspects_to_natal(
        result["positions"], natal_chart, transit_orb
    )
    return result


def sign_index_of(sign: str) -> int:
    """0-based SIGNS index, tolerating Thai-prefixed sign labels."""
    try:
        return SIGNS.index(sign)
    except ValueError:
        for i, s in enumerate(SIGNS):
            if sign in s or s in sign:
                return i
    return 0


_ = math  # keep import surface stable for external callers


# ===========================================================================
# Spec-10 completion (2026-08): mean Lilith, whole-sign houses, sign+house
# meaning rules (§3), TH/EN output templates (§6) and synastry add-on
# weights (§4). The original five-body contract above is unchanged —
# compute_asteroid_positions still returns exactly Chiron+Ceres+Pallas+
# Juno+Vesta; Lilith joins through natal_asteroid_readings.
# ===========================================================================

def lilith_position(dt_utc: datetime) -> dict | None:
    """Mean Lilith (mean lunar apogee) at one instant: tropical + sidereal.

    Same shape as the five bodies in ``_positions_at_instant``. Returns
    None only if pyswisseph itself is unavailable.
    """
    if _swe is None:
        return None
    jd = _jd_utc(dt_utc)
    ayanamsa = lahiri_ayanamsa(_year_frac(dt_utc))
    xx, _retflag = _swe.calc_ut(jd, MEAN_APOG_ID, _swe.FLG_SWIEPH | _swe.FLG_SPEED)
    lon = xx[0] % 360.0
    sid = (lon - ayanamsa) % 360.0
    sign, deg = _to_sign(lon)
    sid_sign, sid_deg = _to_sign(sid)
    return {
        "body": "Lilith",
        "sign": sign,
        "degree": round(deg, 4),
        "absolute_deg": round(lon, 4),
        "sidereal": {
            "sign": sid_sign,
            "degree": round(sid_deg, 4),
            "absolute_deg": round(sid, 4),
        },
        "speed_lon_deg_per_day": round(xx[3], 6),
        "retrograde": xx[3] < 0,
        "nature": NATURE["Lilith"],
    }


# --- Whole-sign houses -----------------------------------------------------

HOUSE_AREAS_EN = {
    1: "self, body and first impressions",
    2: "money, resources and self-worth",
    3: "communication, siblings, daily learning",
    4: "home, family and roots",
    5: "romance, creativity and children",
    6: "daily work, health and service",
    7: "partnership and one-to-one bonds",
    8: "shared resources, depth and crisis",
    9: "travel, higher learning and belief",
    10: "career and public standing",
    11: "friends, networks and long hopes",
    12: "solitude, the subconscious and letting go",
}
HOUSE_AREAS_TH = {
    1: "ตัวตน ร่างกาย บุคลิกแรกพบ",
    2: "เงินทรัพย์ ทรัพยากร คุณค่าในตัวเอง",
    3: "การสื่อสาร ญาติพี่น้อง การเรียนรู้รายวัน",
    4: "บ้าน ครอบครัว รากเหง้า",
    5: "ความรัก ความสร้างสรรค์ บุตร",
    6: "งานประจำวัน สุขภาพ การรับใช้",
    7: "คู่ครอง หุ้นส่วน ความสัมพันธ์เดียว",
    8: "ทรัพย์ร่วม เรื่องลึก วิกฤต",
    9: "การเดินทาง ศาสตร์ชั้นสูง ความเชื่อ",
    10: "อาชีพ ชื่อเสียง สถานะสาธารณะ",
    11: "มิตรสหาย กลุ่มคน ความฝันระยะยาว",
    12: "ความโดดเดี่ยว จิตใต้สำนึก การปล่อยวาง",
}


def whole_sign_house(lon_abs: float, asc_abs: float) -> int:
    """Whole-sign house 1..12 of a longitude given the ASC longitude."""
    return int(((float(lon_abs) - float(asc_abs)) % 360.0) // 30) + 1


# --- Sign+house meaning rules (spec 10 §3) → output templates (§6) ---------

JUNO_SIGN_STYLE_EN = {
    "Aries": ("direct pursuit and independence", "chases honestly and needs room to lead"),
    "Taurus": ("steadiness and loyalty", "stays, provides, keeps promises slowly but surely"),
    "Gemini": ("words and shared curiosity", "talks with you daily and never stops being interesting"),
    "Cancer": ("home-building and nurture", "makes a nest and shows up when it matters"),
    "Leo": ("devotion and open admiration", "loves out loud and celebrates you"),
    "Virgo": ("acts of reliable service", "takes care of the details you drop"),
    "Libra": ("fair partnership", "meets you halfway as an equal"),
    "Scorpio": ("total depth and trust", "goes all the way under the surface with you"),
    "Sagittarius": ("freedom and shared adventure", "travels life beside you without a leash"),
    "Capricorn": ("built-to-last commitment", "builds status and security together"),
    "Aquarius": ("friendship first and breathing room", "is your best friend who refuses to cage you"),
    "Pisces": ("romantic soul-merging", "blends dreams and compassion with you"),
}
JUNO_SIGN_STYLE_TH = {
    "Aries": ("ไล่ล่าตรงๆ และรักอิสระ", "ซื่อตรงกับใจตัวเองและต้องมีที่ให้นำ"),
    "Taurus": ("มั่นคงและซื่อสัตย์", "อยู่ข้าง หล่อเลี้ยง ทำสัญญาช้าแต่ไม่คืนคำ"),
    "Gemini": ("คำพูดและความอยากรู้ร่วมกัน", "คุยกับคุณทุกวันและไม่มีวันน่าเบื่อ"),
    "Cancer": ("สร้างบ้านและดูแลเอาใจใส่", "ทำรังและอยู่ดูแลเวลาที่สำคัญ"),
    "Leo": ("ภักดิ์และชื่นชมแบบเปิดเผย", "รักแบบโชว์ไม่ปิดบังและยกย่องคุณ"),
    "Virgo": ("การรับใช้ที่แน่นอน", "เก็บรายละเอียดที่คุณหลุดให้ทัน"),
    "Libra": ("ความสัมพันธ์ที่เป็นธรรม", "ก้าวสวนคุณครึ่งหนึ่งอย่างเท่าเทียม"),
    "Scorpio": ("ลึกและเชื่อใจแบบทั้งหมด", "กล้าดำลงไปถึงก้นบึ้งพร้อมคุณ"),
    "Sagittarius": ("อิสระและผจญภัยร่วมกัน", "เดินชีวิตข้างคุณโดยไม่ปลูกกรง"),
    "Capricorn": ("ผูกพันแบบสร้างยาว", "สร้างสถานะและความมั่นคงไปด้วยกัน"),
    "Aquarius": ("มิตรภาพมาก่อนและมีพื้นที่หายใจ", "เป็นเพื่อนแท้ที่ไม่ขังคุณไว้"),
    "Pisces": ("หลอมรวมดวงจิตแบบโรแมนติก", "ผสานความฝันและเมตตาเข้ากับคุณ"),
}

_BODY_TEMPLATES_EN = {
    "Juno": lambda p, h, area: (
        f"Juno in {p['sign']}, house {h} ({area}): you commit through "
        f"{JUNO_SIGN_STYLE_EN[_sign_en(p['sign'])][0]}; your real partner is "
        f"someone who {JUNO_SIGN_STYLE_EN[_sign_en(p['sign'])][1]}."
    ),
    "Chiron": lambda p, h, area: (
        f"Chiron in house {h} ({area}): the old wound around {area} is your "
        f"healing gift — the deeper you understand that hurt, the deeper you heal."
    ),
    "Lilith": lambda p, h, area: (
        f"Mean Lilith in {p['sign']}, house {h} ({area}): what you suppress "
        f"there backfires; owned honestly, it becomes your raw power source."
    ),
    "Vesta": lambda p, h, area: (
        f"Vesta in house {h} ({area}): you burn brightest when you dedicate "
        f"yourself to this area."
    ),
    "Pallas": lambda p, h, area: (
        f"Pallas in house {h} ({area}): your tactical intelligence plays out here."
    ),
    "Ceres": lambda p, h, area: (
        f"Ceres in house {h} ({area}): this is how you nurture — and how you "
        f"need to be fed."
    ),
}
_BODY_TEMPLATES_TH = {
    "Juno": lambda p, h, area: (
        f"จูโน่{p['sign']} เรือน {h} ({area}) — คุณผูกมัดผ่าน"
        f"{JUNO_SIGN_STYLE_TH[_sign_th_key(p['sign'])][0]} คู่ที่จริงของคุณคือคนที่"
        f"{JUNO_SIGN_STYLE_TH[_sign_th_key(p['sign'])][1]}"
    ),
    "Chiron": lambda p, h, area: (
        f"ไครออนเรือน {h} ({area}) — แผลเก่าเรื่อง{area}คือของขวัญการเยียวยา"
        f"ของคุณ ยิ่งเข้าใจจุดที่เจ็บ ยิ่งรักษาคนอื่นได้ลึก"
    ),
    "Lilith": lambda p, h, area: (
        f"ลีลิธ{p['sign']} เรือน {h} ({area}) — สิ่งที่คุณกดซ่อนในเรื่องนี้จะ"
        f"ย้อนกลับมาเสมอ ยอมรับเมื่อไหร่ มันกลายเป็นแหล่งพลังดิบของคุณ"
    ),
    "Vesta": lambda p, h, area: (
        f"เวสต้าเรือน {h} ({area}) — คุณสว่างที่สุดเมื่ออุทิศตัวให้เรื่องนี้"
    ),
    "Pallas": lambda p, h, area: (
        f"พัลลัสเรือน {h} ({area}) — สนามฝึกปัญญาเชิงกลยุทธ์ของคุณอยู่ตรงนี้"
    ),
    "Ceres": lambda p, h, area: (
        f"ซีรีสเรือน {h} ({area}) — คุณเลี้ยงดูคนอื่นและต้องการถูกเลี้ยงดู"
        f"ผ่านเรื่องนี้"
    ),
}

_SIGN_KEYS_TH = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


def _sign_en(sign_label: str) -> str:
    """English zodiac name from chart_service's 'ไทย(English)' labels."""
    label = str(sign_label)
    if "(" in label and label.rstrip().endswith(")"):
        return label[label.index("(") + 1 : label.rindex(")")].strip()
    return label


def _sign_en_idx(sign_label: str) -> int:
    en = _sign_en(sign_label)
    try:
        return _SIGN_KEYS_TH.index(en)
    except ValueError:
        return 0


def _sign_th_key(sign_label: str) -> str:
    return _SIGN_KEYS_TH[_sign_en_idx(sign_label)]


def natal_asteroid_readings(natal_chart: dict) -> dict:
    """Spec-10 completion entry point: six bodies incl. mean Lilith at the
    chart's own instant, whole-sign houses from the ASC, and one natural
    astrologer line per body ('th' + 'en'). Graceful under all failures."""
    natal = natal_asteroid_positions(natal_chart)  # five bodies via swisseph
    result: dict[str, dict] = {
        "status": natal.get("status", "unavailable"),
        "reason": natal.get("reason"),
        "positions": dict(natal.get("positions") or {}),
        "readings": {},
        "reading_lines": {"th": [], "en": []},
    }
    if result["status"] == "unavailable":
        return result
    if _swe is not None:
        try:
            s = str(natal_chart.get("datetime_utc", "")).rstrip("Z")
            birth_dt = datetime.fromisoformat(s)
            if birth_dt.tzinfo is None:
                birth_dt = birth_dt.replace(tzinfo=timezone.utc)
            lil = lilith_position(birth_dt)
            if lil is not None:
                result["positions"]["Lilith"] = lil
        except Exception:
            pass  # Lilith stays absent rather than breaking the five-body core

    asc = natal_chart.get("ascendant")
    asc_lon = float(asc["absolute_deg"]) if asc else None

    order = ["Juno", "Chiron", "Lilith", "Vesta", "Pallas", "Ceres"]
    for name in order:
        pos = result["positions"].get(name)
        if not pos or asc_lon is None:
            continue
        house = whole_sign_house(pos["absolute_deg"], asc_lon)
        area_en = HOUSE_AREAS_EN[house]
        area_th = HOUSE_AREAS_TH[house]
        reading = {
            "sign": pos["sign"],
            "degree_in_sign": pos["degree"],
            "whole_sign_house": house,
            "house_area_en": area_en,
            "house_area_th": area_th,
            "nature": pos.get("nature", ""),
        }
        if name == "Juno":
            reading["commit_style_en"] = JUNO_SIGN_STYLE_EN[_sign_en(pos["sign"])][0]
            reading["commit_style_th"] = JUNO_SIGN_STYLE_TH[_sign_th_key(pos["sign"])][0]
        if name == "Lilith":
            reading["variant"] = "mean_apogee"
        result["readings"][name] = {
            **reading,
            "line_en": _BODY_TEMPLATES_EN[name](pos, house, area_en),
            "line_th": _BODY_TEMPLATES_TH[name](pos, house, area_th),
        }
        result["reading_lines"]["en"].append(result["readings"][name]["line_en"])
        result["reading_lines"]["th"].append(result["readings"][name]["line_th"])

    if not result["readings"]:
        result["status"] = "unavailable"
        result["reason"] = result.get("reason") or "no_ascendant_whole_sign_houses"
    return result


# --- Synastry add-ons (spec 10 §4 weights on the spec-03 scale) -------------

_SYNASTRY_ORB = 3.0
_MAJOR_ASPECTS = (("conjunction", 0.0), ("sextile", 60.0), ("square", 90.0),
                  ("trine", 120.0), ("opposition", 180.0))


def asteroid_synastry(person_a_positions: dict, person_b_chart: dict) -> list[dict]:
    """Weighted asteroid contacts from A's asteroid positions to B's chart.

    Spec 10 §4: Juno conj partner's Sun/Moon/Venus/Desc ≤3° → +8;
    Juno–Juno major aspect ≤3° → +5; Chiron conj partner's luminary → ±5
    (flowing gift / hard wound); Lilith conj partner's Venus/Mars ≤3° → ±4
    (magnetic shadow pull — both voices printed).
    """
    b_points: list[tuple[str, float]] = []
    for body in person_b_chart.get("bodies", []):
        if body["body"] in ("Sun", "Moon", "Venus", "Mars"):
            b_points.append((body["body"], float(body["absolute_deg"])))
    if person_b_chart.get("ascendant"):
        asc = float(person_b_chart["ascendant"]["absolute_deg"])
        b_points.append(("Desc", (asc + 180.0) % 360.0))
        b_points.append(("ASC", asc))

    contacts: list[dict] = []

    def _aspect(a: float, b: float) -> tuple[float, str]:
        sep = abs(a - b) % 360.0
        sep = min(sep, 360.0 - sep)
        best_name, best_gap = "", 999.0
        for nm, ang in _MAJOR_ASPECTS:
            gap = abs(sep - ang)
            if gap < best_gap:
                best_name, best_gap = nm, gap
        return best_gap, best_name

    # A-side Juno/Chiron/Lilith come from A's own natal readings payload.
    a_pos = person_a_positions.get("positions") or {}
    juno_a = a_pos.get("Juno")
    chiron_a = a_pos.get("Chiron")
    lilith_a = a_pos.get("Lilith")

    if juno_a:
        for pname, plon in b_points:
            if pname in ("Sun", "Moon", "Venus", "Desc"):
                gap, aspect = _aspect(juno_a["absolute_deg"], plon)
                if gap <= _SYNASTRY_ORB and aspect == "conjunction":
                    contacts.append({
                        "rule": "juno_conj_spouse_significator",
                        "weight": 8, "orb_deg": round(gap, 3),
                        "detail": f"A-Juno conj B-{pname}",
                    })
    if juno_a and (person_a_positions.get("counterpart_juno") is not None):
        gap, aspect = _aspect(
            juno_a["absolute_deg"],
            person_a_positions["counterpart_juno"]["absolute_deg"],
        )
        if gap <= _SYNASTRY_ORB:
            contacts.append({
                "rule": "juno_juno_major_aspect", "weight": 5,
                "orb_deg": round(gap, 3), "aspect": aspect,
                "detail": f"A-Juno {aspect} B-Juno",
            })
    if chiron_a:
        for pname, plon in b_points:
            if pname in ("Sun", "Moon"):
                gap, aspect = _aspect(chiron_a["absolute_deg"], plon)
                if gap <= _SYNASTRY_ORB and aspect == "conjunction":
                    contacts.append({
                        "rule": "chiron_conj_luminary",
                        "weight": -5, "orb_deg": round(gap, 3),
                        "voice": "wound_activation_hard",
                        "also_voice": "healing_bond_when_worked_consciously",
                        "detail": f"A-Chiron conj B-{pname}",
                    })
                elif gap <= _SYNASTRY_ORB and aspect in ("trine", "sextile"):
                    contacts.append({
                        "rule": "chiron_flow_to_luminary",
                        "weight": 5, "orb_deg": round(gap, 3),
                        "voice": "healing_gift_flowing",
                        "detail": f"A-Chiron {aspect} B-{pname}",
                    })
    if lilith_a:
        for pname, plon in b_points:
            if pname in ("Venus", "Mars"):
                gap, aspect = _aspect(lilith_a["absolute_deg"], plon)
                if gap <= _SYNASTRY_ORB and aspect == "conjunction":
                    contacts.append({
                        "rule": "lilith_conj_venus_mars",
                        "weight": -4, "orb_deg": round(gap, 3),
                        "voice": "magnetic_shadow_pull",
                        "also_voice": "raw_creativity_when_integrated",
                        "detail": f"A-Lilith conj B-{pname}",
                    })

    contacts.sort(key=lambda c: (-abs(c["weight"]), c["orb_deg"]))
    return contacts

