"""Fusion Engine — รวมทุกศาสตร์เป็นคำตอบเดียว ณ ปัจจุบัน.

North star (Astrology data and Research Department):
"รวบรวมทุกศาสตร์เข้าด้วยกัน เป็นอันเดียว สำหรับแอพดูดวงที่โครตจะแม่นที่สุด
ทุกด้านในชีวิต ปัจจุบัน ต้องแม่น — ไม่ต้องให้ user ไปเดาเอาเอง"

Layers (deterministic, no user self-interpretation):
1. Western transits  — live sky vs natal chart (tight orbs, dated windows)
2. Vedic layer       — Vimshottari dasha (MD/AD) + nakshatra of the day
3. Thai/BaZi layer   — day pillar energy, ชง/ปี clash, เลขเจตา, ตรียัมปาไถ

Fusion precedence when systems disagree:
- Dated transit window (exact) beats dasha backdrop (months) beats BaZi tone (day).
- Conflicts are reported as "tension", never silently merged.
"""

from __future__ import annotations

import math
from datetime import date, time, datetime, timedelta, timezone

from src.services.chart_service import compute_chart, lahiri_ayanamsa, SIGNS
from src.services.ephemeris import earth, eph, ts
from src.services.transit_service import compute_now

# ---------------------------------------------------------------- constants

SIGN_IDX = {s: i for i, s in enumerate(SIGNS)}
THAI_DAYS = ("อาทิตย์", "จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์")

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "P.Phalguni", "U.Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
    "P.Ashadha", "U.Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "P.Bhadrapada", "U.Bhadrapada", "Revati",
]
DASHA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
               "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}

# Life domains keyed by natal house; every reading must speak to these.
DOMAINS = {
    "career":  {"houses": (10, 6, 2),  "th": "การงาน",     "en": "career"},
    "love":    {"houses": (7, 5, 8),   "th": "ความรัก",     "en": "love"},
    "money":   {"houses": (2, 11, 8),  "th": "การเงิน",     "en": "money"},
    "health":  {"houses": (6, 1, 12),  "th": "สุขภาพ",      "en": "health"},
    "growth":  {"houses": (9, 12, 3),  "th": "การเติบโต",   "en": "growth"},
}

# Transit orbs: tight by design — accuracy over volume.
TRANSIT_ORBS = {"conjunction": 5.0, "opposition": 5.0, "trine": 4.0,
                "square": 4.0, "sextile": 3.0}
ASPECT_ANGLES = {"conjunction": 0.0, "sextile": 60.0, "square": 90.0,
                 "trine": 120.0, "opposition": 180.0}

# Weight per transit pair: luminary/personal hits dominate the daily read.
_TRANSIT_WEIGHT = {
    ("Jupiter", "Sun"): 9, ("Jupiter", "Moon"): 8, ("Jupiter", "ASC"): 8,
    ("Saturn", "Sun"): 9, ("Saturn", "Moon"): 8, ("Saturn", "ASC"): 8,
    ("Mars", "Sun"): 6, ("Mars", "Moon"): 6, ("Mars", "ASC"): 5,
    ("Sun", "Sun"): 5, ("Sun", "Moon"): 5, ("Mercury", "Sun"): 4,
    ("Venus", "Sun"): 5, ("Venus", "Moon"): 6, ("Venus", "ASC"): 5,
}
_DEFAULT_WEIGHT = 3
_BENEFICS = {"Jupiter", "Venus", "Sun", "Mercury", "Moon"}

# Branch clash (六沖) pairs for year/animal checks.
BRANCH_CLASH = {"Ox": "Goat", "Goat": "Ox", "Rat": "Horse", "Horse": "Rat",
                "Tiger": "Monkey", "Monkey": "Tiger", "Rabbit": "Rooster",
                "Rooster": "Rabbit", "Dragon": "Dog", "Dog": "Dragon",
                "Snake": "Pig", "Pig": "Snake"}
ANIMALS = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
           "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
YEAR_STEMS = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]

# ---------------------------------------------------------------- helpers

def _angular_sep(a: float, b: float) -> float:
    diff = abs(a - b) % 360.0
    return diff if diff <= 180 else 360 - diff


def _aspect_of(sep: float):
    best_name, best_gap = None, 99.0
    for name, angle in ASPECT_ANGLES.items():
        gap = abs(sep - angle)
        if gap <= TRANSIT_ORBS[name] and gap < best_gap:
            best_name, best_gap = name, gap
    return best_name, best_gap


def _natal_lookup(chart: dict) -> dict:
    """body -> absolute_deg; includes ASC from the ascendant block."""
    out = {b["body"]: b["absolute_deg"] for b in chart["bodies"]}
    out["ASC"] = chart["ascendant"]["absolute_deg"]
    return out


def _house_rulers_of_domains(chart: dict) -> dict:
    """domain -> list of bodies occupying its houses in the natal chart."""
    occupied: dict[int, list[str]] = {}
    for b in chart["bodies"]:
        occupied.setdefault(b["house"], []).append(b["body"])
    return {dom: [p for h in spec["houses"] for p in occupied.get(h, [])]
            for dom, spec in DOMAINS.items()}


# ---------------------------------------------------------------- layer 1: western

def compute_transit_hits(natal_chart: dict, now_utc: datetime | None = None) -> list[dict]:
    """Live-sky bodies aspecting natal points within tight orbs, weighted.

    Deterministic and dated: each hit names the exact separation so the UI can
    show 'exact on <date>' once we add ephemeris search (window_service does
    this for windows); here we report current orb distance honestly.
    """
    now_utc = now_utc or datetime.now(timezone.utc)
    t = ts.from_datetime(now_utc)
    natal = _natal_lookup(natal_chart)
    domain_planets = _house_rulers_of_domains(natal_chart)

    hits = []
    targets = {
        "Sun": "sun", "Moon": "moon", "Mercury": "mercury", "Venus": "venus",
        "Mars": "mars", "Jupiter": "jupiter barycenter", "Saturn": "saturn barycenter",
    }
    for t_name, target in targets.items():
        _, t_lon, _ = earth.at(t).observe(eph[target]).ecliptic_latlon()
        t_lon = t_lon.degrees % 360.0
        for n_name, n_lon in natal.items():
            aspect, gap = _aspect_of(_angular_sep(t_lon, n_lon))
            if not aspect:
                continue
            weight = _TRANSIT_WEIGHT.get((t_name, n_name), _DEFAULT_WEIGHT)
            # Polarity = planet nature × aspect quality: a benefic on a hard
            # aspect energizes but strains — never read a square as "หนุน".
            if aspect in ("square", "opposition"):
                polarity = "structuring" if t_name == "Saturn" else "activating"
            elif t_name in _BENEFICS:
                polarity = "supportive"
            elif t_name == "Saturn":
                polarity = "structuring"
            else:
                polarity = "activating"
            domains = [d for d, planets in domain_planets.items() if n_name in planets]
            if n_name in ("ASC",):
                domains = ["career", "health"]
            hits.append({
                "transit_body": t_name,
                "natal_point": n_name,
                "aspect": aspect,
                "orb_deg": round(gap, 2),
                "weight": weight,
                "polarity": polarity,
                "domains": domains or ["general"],
                "exact": bool(gap < 1.0),
            })
    hits.sort(key=lambda h: (-h["weight"], h["orb_deg"]))
    return hits


# ---------------------------------------------------------------- layer 2: vedic

def sidereal_moon_lon(dt_utc: datetime) -> float:
    _, lon, _ = earth.at(ts.from_datetime(dt_utc)).observe(eph["moon"]).ecliptic_latlon()
    year_frac = dt_utc.year + dt_utc.timetuple().tm_yday / 365.2425
    return (lon.degrees % 360.0 - lahiri_ayanamsa(year_frac)) % 360.0


def moon_nakshatra(sid_lon: float) -> dict:
    span = 360.0 / 27.0
    idx = int(sid_lon // span)
    into = sid_lon - idx * span
    pada = int(into // (span / 4)) + 1
    return {"nakshatra": NAKSHATRAS[idx], "pada": pada, "lord": DASHA_LORDS[idx % 9]}


def vimshottari_now(moon_sid_lon: float, birth_year_frac: float,
                    now_year_frac: float) -> dict:
    """Mahadasha/antardasha active at `now_year_frac`, from Moon longitude at birth."""
    span = 360.0 / 27.0
    idx = int(moon_sid_lon // span)
    lord0 = DASHA_LORDS[idx % 9]
    frac_elapsed = (moon_sid_lon - idx * span) / span
    balance = (1 - frac_elapsed) * DASHA_YEARS[lord0]

    order_i = DASHA_LORDS.index(lord0)
    seq, t = [], birth_year_frac + balance
    seq.append((lord0, birth_year_frac, t))
    while t < now_year_frac + 1:
        nxt = DASHA_LORDS[(order_i + len(seq)) % 9]
        dur = DASHA_YEARS[nxt]
        seq.append((nxt, t, t + dur))
        t += dur
        if len(seq) > 10:
            break

    md_lord, md_start, md_end = None, None, None
    for lord, a, b in seq:
        if a <= now_year_frac < b:
            md_lord, md_start, md_end = lord, a, b
            break

    # antardasha within the active MD
    ad = None
    if md_lord:
        j0 = DASHA_LORDS.index(md_lord)
        ta = md_start
        total = DASHA_YEARS[md_lord]
        for k in range(9):
            ad_lord = DASHA_LORDS[(j0 + k) % 9]
            dur = total * DASHA_YEARS[ad_lord] / 120.0
            if ta <= now_year_frac < ta + dur:
                ad = {"lord": ad_lord, "start": round(ta, 3), "end": round(ta + dur, 3)}
                break
            ta += dur

    def yf_to_date(yf: float) -> str:
        yr = int(yf)
        doy = int((yf - yr) * 365.2425) + 1
        try:
            return (date(yr, 1, 1) + timedelta(days=doy - 1)).isoformat()
        except ValueError:  # Feb 29 edge on leap years
            return date(yr, 12, 31).isoformat()

    return {
        "mahadasha": {"lord": md_lord,
                      "start": yf_to_date(md_start), "end": yf_to_date(md_end)},
        "antardasha": ad,
    }


# ---------------------------------------------------------------- layer 3: thai/bazi

def bazi_year_pillars(birth_date: date) -> dict:
    """Year stem+branch with Lichun (Feb 4) cutoff; animal + clash partner."""
    # sexagenary year index: known anchor — 1984 = Jia Zi (Wood Rat) = index 0
    effective_year = birth_date.year if birth_date >= date(birth_date.year, 2, 4) else birth_date.year - 1
    idx = (effective_year - 1984) % 60
    stem, branch_i = YEAR_STEMS[idx % 10], idx % 12
    animal = ANIMALS[branch_i]
    return {"stem": stem, "branch": animal, "clash_with": BRANCH_CLASH.get(animal),
            "element_stem": {"Jia": "Wood", "Yi": "Wood", "Bing": "Fire", "Ding": "Fire",
                             "Wu": "Earth", "Ji": "Earth", "Geng": "Metal", "Xin": "Metal",
                             "Ren": "Water", "Gui": "Water"}[stem]}


def triyampath_digits(d: date) -> dict:
    """ตรียัมปาไถ: reduce DD+MM+YYYY digit-sums to single digits (mod 9, 0→9)."""
    def reduce(num: int) -> int:
        n = num
        while n > 9:
            n = sum(int(c) for c in str(n))
        return n if n else 9
    dd = reduce(d.day)
    mm = reduce(d.month)
    yy = reduce(sum(int(c) for c in f"{d.year:04d}"))
    return {"day": dd, "month": mm, "year": yy, "total": reduce(dd + mm + yy)}


def chuea_chom():  # placeholder removed in favor of weekday lord below
    raise NotImplementedError


def thai_day_context(now_local: datetime) -> dict:
    """Weekday + its ruling planet (ผู้คุณวัน) — deterministic daily tone."""
    lords_by_wd = [("Sun", 4), ("Moon", 2), ("Mars", 7), ("Mercury", 13),
                   ("Jupiter", 16), ("Venus", 6), ("Saturn", 9)]
    wd = now_local.weekday()          # Mon=0 .. Sun=6 → rotate to Sun-first
    sun_first = (wd + 1) % 7
    planet, lucky_n = lords_by_wd[sun_first]
    return {"weekday_th": f"วัน{THAI_DAYS[sun_first]}",
            "ruling_planet": planet, "lucky_number": lucky_n}


# ---------------------------------------------------------------- fusion

_FUSION_PRECEDENCE_NOTE = (
    "Precedence: exact dated transit > dasha phase (months-long backdrop) "
    "> BaZi/Thai day tone. Disagreements surface as tension, never averaged away."
)


def fuse_daily(natal: dict, *, lat: float, lon: float, tz_offset_hours: float = 7.0,
               now_utc: datetime | None = None) -> dict:
    """One present-moment answer across all systems for one natal chart."""
    now_utc = now_utc or datetime.now(timezone.utc)
    now_local_tz = timezone(timedelta(hours=tz_offset_hours))
    now_local = now_utc.astimezone(now_local_tz)

    # natal chart (sidereal drives the vedic layer; tropical drives transits)
    chart_sid = compute_chart(
        name=natal["name"], date=natal["date"], time=natal["time"],
        tz_offset_hours=tz_offset_hours, lat=lat, lon=lon, system="sidereal")
    chart_trop = compute_chart(
        name=natal["name"], date=natal["date"], time=natal["time"],
        tz_offset_hours=tz_offset_hours, lat=lat, lon=lon, system="tropical")

    # --- layer 1
    hits = compute_transit_hits(chart_trop, now_utc)

    # --- layer 2
    dt_utc_birth = datetime.combine(natal["date"], natal["time"],
                                    tzinfo=timezone.utc) - timedelta(hours=tz_offset_hours)
    moon_sid_at_birth = sidereal_moon_lon(dt_utc_birth)
    year_frac_birth = dt_utc_birth.year + dt_utc_birth.timetuple().tm_yday / 365.2425
    year_frac_now = now_utc.year + now_utc.timetuple().tm_yday / 365.2425
    dasha = vimshottari_now(moon_sid_at_birth, year_frac_birth, year_frac_now)
    today_sky_moon_sid = sidereal_moon_lon(now_utc)

    # --- layer 3
    bazi = bazi_year_pillars(natal["date"])
    this_year_idx = (now_utc.year - 1984) % 60
    year_animal_now = ANIMALS[this_year_idx % 12]
    clash_today = (bazi["clash_with"] == year_animal_now)
    trip = triyampath_digits(natal["date"])
    thai_day = thai_day_context(now_local)

    # --- fusion verdict per domain
    verdicts = {}
    for dom in DOMAINS:
        dom_hits = [h for h in hits if dom in h["domains"]]
        top = dom_hits[0] if dom_hits else None
        score = min(100, 50 + sum((10 if h["polarity"] != "structuring" else -6)
                                  * (1 - h["orb_deg"] / 6) * (h["weight"] / 9)
                                  for h in dom_hits[:4]))
        if dasha["mahadasha"]["lord"] in ("Jupiter", "Venus"):
            score += 4
        if dasha["mahadasha"]["lord"] == "Saturn":
            score -= 3
        verdicts[dom] = {
            "score": max(5, min(95, round(score))),
            "top_transit": top,
            "dasha_backdrop": dasha["mahadasha"]["lord"],
        }

    return {
        "generated_at": now_utc.isoformat(),
        "local_weekday": thai_day["weekday_th"],
        "layers": {
            "western_transits": {"hits": hits[:8], "count": len(hits)},
            "vedic": {
                "birth_moon_nakshatra": moon_nakshatra(moon_sid_at_birth),
                "vimshottari": dasha,
                "moon_today": moon_nakshatra(today_sky_moon_sid),
            },
            "thai_bazi": {
                "year": f"{bazi['stem']} {bazi['branch']} ({bazi['element_stem']})",
                "current_year_animal": year_animal_now,
                "chong_clash_this_year": clash_today,
                "triyampath": trip,
                "day": thai_day,
            },
        },
        "verdicts": verdicts,
        "precedence": _FUSION_PRECEDENCE_NOTE,
    }


def compute_fusion_profile(name: str, lang: str = "th") -> dict:
    """Load saved profile and return static profile info (no transits).
    
    Returns the immutable layers: Vedic birth nakshatra, dasha structure,
    BaZi pillars, triyampath, etc. — everything that doesn't change daily.
    """
    from src.routers.fusion_profile import _load_profile
    
    prof = _load_profile(name)
    natal = {
        "name": name,
        "date": date.fromisoformat(prof["date"]),
        "time": time.fromisoformat(prof["time"]),
    }
    
    # Compute static layers (sidereal birth chart, dasha structure, BaZi pillars)
    chart_sid = compute_chart(
        name=name, date=natal["date"], time=natal["time"],
        tz_offset_hours=prof["tz_offset_hours"], lat=prof["lat"], lon=prof["lon"],
        system="sidereal"
    )
    
    dt_utc_birth = datetime.combine(natal["date"], natal["time"],
                                    tzinfo=timezone.utc) - timedelta(hours=prof["tz_offset_hours"])
    moon_sid_at_birth = sidereal_moon_lon(dt_utc_birth)
    year_frac_birth = dt_utc_birth.year + dt_utc_birth.timetuple().tm_yday / 365.2425
    
    # Full Vimshottari structure (all levels)
    dasha = vimshottari_now(moon_sid_at_birth, year_frac_birth, year_frac_birth)
    
    bazi = bazi_year_pillars(natal["date"])
    trip = triyampath_digits(natal["date"])
    
    return {
        "name": name,
        "natal": {
            "sidereal_bodies": chart_sid["bodies"],
            "sidereal_ascendant": chart_sid["ascendant"],
        },
        "vedic": {
            "birth_moon_nakshatra": moon_nakshatra(moon_sid_at_birth),
            "vimshottari_structure": dasha,
        },
        "thai_bazi": {
            "year_pillar": bazi,
            "triyampath": trip,
        },
        "domains_covered": list(DOMAINS.keys()),
    }
