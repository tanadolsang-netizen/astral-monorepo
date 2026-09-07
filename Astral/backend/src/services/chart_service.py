import math
from datetime import date, time, datetime, timedelta, timezone

from src.services.ephemeris import earth, eph, ts, OBLIQUITY

SIGNS = [
    "เมษ(Aries)", "พฤษภ(Taurus)", "เมถุน(Gemini)", "กรกฎ(Cancer)",
    "สิงห์(Leo)", "กันย์(Virgo)", "ตุลย์(Libra)", "พิจิก(Scorpio)",
    "ธนู(Sagittarius)", "มังกร(Capricorn)", "กุมภ์(Aquarius)", "มีน(Pisces)",
]

BODIES = {
    "Sun": "sun",
    "Moon": "moon",
    "Mercury": "mercury",
    "Venus": "venus",
    "Mars": "mars",
    "Jupiter": "jupiter barycenter",
    "Saturn": "saturn barycenter",
    "Uranus": "uranus barycenter",
    "Neptune": "neptune barycenter",
    "Pluto": "pluto barycenter",
}

HOUSE_SYSTEMS = ("placidus", "koch")

# Domicile (rulership) signs by 0-based SIGNS index. Classical dual rulers for
# Mercury/Venus/Mars/Jupiter/Saturn are kept alongside the modern outer-planet
# co-rulers (Uranus/Neptune/Pluto), matching common modern software.
_DOMICILE_IDX = {
    "Sun": [4],
    "Moon": [3],
    "Mercury": [2, 5],
    "Venus": [1, 6],
    "Mars": [0, 7],
    "Jupiter": [8, 11],
    "Saturn": [9, 10],
    "Uranus": [10],
    "Neptune": [11],
    "Pluto": [7],
}

# Exaltation is only traditionally defined for the seven classical planets;
# modern-planet exaltations are disputed across sources so are left out.
_EXALTATION_IDX = {
    "Sun": 0,
    "Moon": 1,
    "Mercury": 5,
    "Venus": 11,
    "Mars": 9,
    "Jupiter": 3,
    "Saturn": 6,
}

DOMICILE = {planet: [SIGNS[i] for i in idxs] for planet, idxs in _DOMICILE_IDX.items()}
EXALTATION = {planet: SIGNS[i] for planet, i in _EXALTATION_IDX.items()}
DETRIMENT = {planet: [SIGNS[(i + 6) % 12] for i in idxs] for planet, idxs in _DOMICILE_IDX.items()}
FALL = {planet: SIGNS[(i + 6) % 12] for planet, i in _EXALTATION_IDX.items()}


def _build_chart(name: str, dt_utc, lat: float, lon: float, system: str, house_system: str) -> dict:
    houses = compute_houses(dt_utc, lat, lon, system, house_system)
    cusp_degs = [c["absolute_deg"] for c in houses["cusps"]]
    bodies = []
    for body_name in BODIES:
        t = ts.from_datetime(dt_utc)
        pos = earth.at(t).observe(eph[BODIES[body_name]])
        lat_ecl, lon_ecl, _ = pos.ecliptic_latlon()
        lon_deg = lon_ecl.degrees % 360
        if system == "sidereal":
            year_frac = dt_utc.year + (dt_utc.timetuple().tm_yday / 365.2425)
            lon_deg = (lon_deg - lahiri_ayanamsa(year_frac)) % 360
        sign, deg = _to_sign(lon_deg)
        bodies.append({
            "body": body_name,
            "sign": sign,
            "degree": round(deg, 4),
            "absolute_deg": round(lon_deg, 4),
            "house": _house_of(lon_deg, cusp_degs),
            "dignity": compute_dignity(body_name, sign),
        })
    asc = compute_ascendant(dt_utc, lat, lon, system)
    return {
        "name": name,
        "datetime_utc": dt_utc.isoformat() + "Z",
        "system": system,
        "bodies": bodies,
        "ascendant": asc,
        "midheaven": houses["midheaven"],
        "houses": houses,
    }


def compute_chart(
    name: str,
    date,
    time,
    tz_offset_hours: float = 7.0,
    lat: float = 13.8591,
    lon: float = 100.5217,
    system: str = "tropical",
    house_system: str = "placidus",
) -> dict:
    dt_local = datetime.combine(date, time)
    dt_utc = dt_local - timedelta(hours=tz_offset_hours)
    dt_utc = dt_utc.replace(tzinfo=timezone.utc)
    return _build_chart(name, dt_utc, lat, lon, system, house_system)


def compute_dual_chart(
    name: str,
    date,
    time,
    tz_offset_hours: float = 7.0,
    lat: float = 13.8591,
    lon: float = 100.5217,
    house_system: str = "placidus",
) -> dict:
    """Compute both tropical and sidereal charts from the same birth data."""
    dt_local = datetime.combine(date, time)
    dt_utc = dt_local - timedelta(hours=tz_offset_hours)
    dt_utc = dt_utc.replace(tzinfo=timezone.utc)
    tropical = _build_chart(name, dt_utc, lat, lon, "tropical", house_system)
    sidereal = _build_chart(name, dt_utc, lat, lon, "sidereal", house_system)
    return {
        "name": name,
        "datetime_utc": dt_utc.isoformat() + "Z",
        "tropical": tropical,
        "sidereal": sidereal,
    }


def compute_ascendant(dt_utc, lat: float, lon: float, system: str = "tropical") -> dict:
    t = ts.from_datetime(dt_utc)
    gmst = t.gmst
    lst = (gmst + lon / 15.0) % 24.0
    ramc = lst * 15.0
    asc_deg = (_to_xy(ramc, lat, OBLIQUITY) + 180.0) % 360.0
    if system == "sidereal":
        year_frac = dt_utc.year + (dt_utc.timetuple().tm_yday / 365.2425)
        asc_deg = (asc_deg - lahiri_ayanamsa(year_frac)) % 360
    sign, deg = _to_sign(asc_deg)
    return {"body": "ASC", "sign": sign, "degree": round(deg, 4), "absolute_deg": round(asc_deg, 4)}


def compute_houses(
    dt_utc,
    lat: float,
    lon: float,
    system: str = "tropical",
    house_system: str = "placidus",
) -> dict:
    """Compute the Ascendant, Midheaven, and 12 house cusps.

    house_system selects between "placidus" (iterative semi-arc division,
    the default) and "koch" (birthplace system, closed-form via the
    Ascendant's declination).
    """
    if house_system not in HOUSE_SYSTEMS:
        raise ValueError(f"Unsupported house_system: {house_system!r}. Choose one of {HOUSE_SYSTEMS}.")

    t = ts.from_datetime(dt_utc)
    gmst = t.gmst
    lst = (gmst + lon / 15.0) % 24.0
    ramc = lst * 15.0

    asc_deg = (_to_xy(ramc, lat, OBLIQUITY) + 180.0) % 360.0
    mc_deg = _ra_to_longitude(ramc, OBLIQUITY)

    if house_system == "koch":
        cusps_trop = _koch_cusps(ramc, lat, OBLIQUITY, asc_deg, mc_deg)
    else:
        cusps_trop = _placidus_cusps(ramc, lat, OBLIQUITY, asc_deg, mc_deg)

    if system == "sidereal":
        year_frac = dt_utc.year + (dt_utc.timetuple().tm_yday / 365.2425)
        ayanamsa = lahiri_ayanamsa(year_frac)
        cusps_trop = {house: (deg - ayanamsa) % 360 for house, deg in cusps_trop.items()}
        asc_deg = (asc_deg - ayanamsa) % 360
        mc_deg = (mc_deg - ayanamsa) % 360

    cusp_list = []
    for house_num in range(1, 13):
        lon_deg = cusps_trop[house_num]
        sign, deg = _to_sign(lon_deg)
        cusp_list.append({
            "house": house_num,
            "sign": sign,
            "degree": round(deg, 4),
            "absolute_deg": round(lon_deg, 4),
        })

    asc_sign, asc_deg_in_sign = _to_sign(asc_deg)
    mc_sign, mc_deg_in_sign = _to_sign(mc_deg)

    return {
        "house_system": house_system,
        "cusps": cusp_list,
        "ascendant": {
            "body": "ASC", "sign": asc_sign,
            "degree": round(asc_deg_in_sign, 4), "absolute_deg": round(asc_deg, 4),
        },
        "midheaven": {
            "body": "MC", "sign": mc_sign,
            "degree": round(mc_deg_in_sign, 4), "absolute_deg": round(mc_deg, 4),
        },
    }


def compute_dignity(body_name: str, sign: str) -> dict:
    """Essential dignity of a planet by sign: domicile, exaltation, detriment, fall."""
    domicile = sign in DOMICILE.get(body_name, [])
    exaltation = sign == EXALTATION.get(body_name)
    detriment = sign in DETRIMENT.get(body_name, [])
    fall = sign == FALL.get(body_name)

    score = 0
    if domicile:
        score += 5
    if exaltation:
        score += 4
    if detriment:
        score -= 5
    if fall:
        score -= 4

    if domicile:
        label = "domicile"
    elif exaltation:
        label = "exaltation"
    elif detriment:
        label = "detriment"
    elif fall:
        label = "fall"
    else:
        label = "peregrine"

    return {
        "domicile": domicile,
        "exaltation": exaltation,
        "detriment": detriment,
        "fall": fall,
        "score": score,
        "label": label,
    }


def _placidus_cusps(ramc: float, lat: float, obliquity_rad: float, asc_deg: float, mc_deg: float) -> dict:
    h11 = _iterate_placidus_cusp(ramc, lat, obliquity_rad, base=0.0, coeff=1 / 3, guess=30.0)
    h12 = _iterate_placidus_cusp(ramc, lat, obliquity_rad, base=0.0, coeff=2 / 3, guess=60.0)
    h2 = _iterate_placidus_cusp(ramc, lat, obliquity_rad, base=180.0, coeff=-2 / 3, guess=120.0)
    h3 = _iterate_placidus_cusp(ramc, lat, obliquity_rad, base=180.0, coeff=-1 / 3, guess=150.0)
    return {
        1: asc_deg, 10: mc_deg,
        4: (mc_deg + 180.0) % 360, 7: (asc_deg + 180.0) % 360,
        11: h11, 12: h12, 2: h2, 3: h3,
        5: (h11 + 180.0) % 360, 6: (h12 + 180.0) % 360,
        8: (h2 + 180.0) % 360, 9: (h3 + 180.0) % 360,
    }


def _iterate_placidus_cusp(
    ramc: float, lat: float, obliquity_rad: float, base: float, coeff: float, guess: float, iterations: int = 60,
) -> float:
    """Solve the implicit Placidus condition H = base + coeff * D(H) by fixed-point iteration.

    D(H) is the diurnal semi-arc of the ecliptic point currently at hour
    angle H from the meridian; the cusp is the point whose own semi-arc
    fraction matches its position, so D depends on the very H being solved.
    """
    h = guess
    for _ in range(iterations):
        ra = ramc + h
        lam = _ra_to_longitude(ra, obliquity_rad)
        dec = _declination(lam, obliquity_rad)
        d = _semi_diurnal_arc(dec, lat)
        new_h = base + coeff * d
        if abs(new_h - h) < 1e-8:
            h = new_h
            break
        h = new_h
    return _ra_to_longitude(ramc + h, obliquity_rad)


def _koch_cusps(ramc: float, lat: float, obliquity_rad: float, asc_deg: float, mc_deg: float) -> dict:
    asc_dec = _declination(asc_deg, obliquity_rad)
    val = math.tan(math.radians(lat)) * math.tan(math.radians(asc_dec))
    val = max(-1.0, min(1.0, val))
    a = math.degrees(math.asin(val))

    def lon_at(h_rel: float) -> float:
        return _ra_to_longitude(ramc + h_rel, obliquity_rad)

    c11, c12 = lon_at(30 + a / 3), lon_at(60 + 2 * a / 3)
    c2, c3 = lon_at(120 + 2 * a / 3), lon_at(150 + a / 3)
    return {
        1: asc_deg, 10: mc_deg,
        4: (mc_deg + 180.0) % 360, 7: (asc_deg + 180.0) % 360,
        11: c11, 12: c12, 2: c2, 3: c3,
        5: (c11 + 180.0) % 360, 6: (c12 + 180.0) % 360,
        8: (c2 + 180.0) % 360, 9: (c3 + 180.0) % 360,
    }


def _ra_to_longitude(ra_deg: float, obliquity_rad: float) -> float:
    """Ecliptic longitude of the point on the ecliptic (latitude 0) with the given right ascension."""
    ra_rad = math.radians(ra_deg)
    y = math.sin(ra_rad)
    x = math.cos(ra_rad) * math.cos(obliquity_rad)
    return math.degrees(math.atan2(y, x)) % 360


def _declination(lon_deg: float, obliquity_rad: float) -> float:
    lon_rad = math.radians(lon_deg)
    return math.degrees(math.asin(math.sin(obliquity_rad) * math.sin(lon_rad)))


def _semi_diurnal_arc(dec_deg: float, lat_deg: float) -> float:
    val = -math.tan(math.radians(lat_deg)) * math.tan(math.radians(dec_deg))
    val = max(-1.0, min(1.0, val))
    return math.degrees(math.acos(val))


def _house_of(lon_deg: float, cusp_degs: list[float]) -> int:
    lon_deg = lon_deg % 360
    for i in range(12):
        start = cusp_degs[i] % 360
        end = cusp_degs[(i + 1) % 12] % 360
        if start <= end:
            if start <= lon_deg < end:
                return i + 1
        else:
            if lon_deg >= start or lon_deg < end:
                return i + 1
    return 12


def _to_sign(longitude_deg: float) -> tuple[str, float]:
    idx = int(longitude_deg // 30) % 12
    return SIGNS[idx], longitude_deg % 30


def _to_xy(ramc: float, lat: float, obliquity_rad: float) -> float:
    """Descendant-branch of the textbook Ascendant arctan form.

    Returns atan2(-cos(RAMC), sin(RAMC)*cos(e) + tan(lat)*sin(e)), which
    lands on the Descendant; call sites add 180 deg to obtain the Ascendant.
    Verified two ways: Mai 2001-08-18 22:32 ICT @ 13.85N 100.52E ->
    (+180) = 36.34 = Taurus 6.34 (spec 03 section 1 machine-checked value),
    and an independent hour-angle horizon scan (rising point) agrees for
    both test charts.
    """
    ramc_rad = math.radians(ramc)
    lat_rad = math.radians(lat)
    num = -math.cos(ramc_rad)
    den = (
        math.sin(ramc_rad) * math.cos(obliquity_rad)
        + math.tan(lat_rad) * math.sin(obliquity_rad)
    )
    return math.degrees(math.atan2(num, den)) % 360.0


def lahiri_ayanamsa(year_frac: float) -> float:
    return 23.68 + (year_frac - 1997) * (50.29 / 3600)
