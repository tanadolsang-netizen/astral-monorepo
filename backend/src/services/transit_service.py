from datetime import datetime, timezone, timedelta

from src.services.ephemeris import earth, eph, ts, OBLIQUITY

from src.services.chart_service import _to_sign, lahiri_ayanamsa

# Sun and Moon never appear retrograde from Earth; every other body can.
_CAN_RETROGRADE = {"Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"}

# Sampled a day apart so short-lived librations near a station don't flip the
# sign spuriously; retrograde periods for these bodies last weeks to months.
_RETROGRADE_SAMPLE_DAYS = 1.0


def _ecliptic_lon_deg(target: str, when: datetime) -> float:
    t = ts.from_datetime(when)
    pos = earth.at(t).observe(eph[target])
    _, lon, _ = pos.ecliptic_latlon()
    return lon.degrees % 360


def _is_retrograde(body_name: str, target: str, now_utc: datetime, current_lon_deg: float) -> bool:
    if body_name not in _CAN_RETROGRADE:
        return False
    earlier = now_utc - timedelta(days=_RETROGRADE_SAMPLE_DAYS)
    earlier_lon_deg = _ecliptic_lon_deg(target, earlier)
    delta = (current_lon_deg - earlier_lon_deg + 540) % 360 - 180
    return bool(delta < 0)


def _compute_bodies(now_utc: datetime) -> list:
    """The shared, date-determined part: 10 planetary positions at now_utc.

    This is what gets cached per (date, tz-group) — identical for every user
    in the same tz bucket, which is Co-Star's key scale insight.
    """
    t = ts.from_datetime(now_utc)
    bodies = []
    for name, target in {
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
    }.items():
        pos = earth.at(t).observe(eph[target])
        _, body_lon, _ = pos.ecliptic_latlon()
        lon_deg = body_lon.degrees % 360
        sign, deg = _to_sign(lon_deg)
        bodies.append({
            "body": name,
            "sign": sign,
            "degree": round(deg, 4),
            "absolute_deg": round(lon_deg, 4),
            "is_retrograde": _is_retrograde(name, target, now_utc, lon_deg),
        })
    return bodies


def compute_now(lat: float, lon: float, tz_offset_hours: float = 7.0) -> dict:
    now_utc = datetime.now(timezone.utc)
    # Shared state (same for all users in the same tz bucket) goes through
    # the Redis cache; the per-user shell (lat/lon/tz) is assembled here.
    from src.services.cache_service import get_or_compute, cache_key

    key = cache_key(now_utc.date().isoformat(),
                    f"UTC{int(round(tz_offset_hours)):+d}",
                    "all", "position")
    bodies = get_or_compute(
        key,
        lambda: _compute_bodies(now_utc),
        ttl=3600,  # positions refresh hourly; Moon moves ~0.5deg/hour
    )
    return {
        "now_utc": now_utc.isoformat(),
        "tz_offset_hours": tz_offset_hours,
        "lat": lat,
        "lon": lon,
        "bodies": bodies,
    }
def compute_dual_now(lat: float, lon: float, tz_offset_hours: float = 7.0) -> dict:
    """Return both tropical and sidereal transit positions."""
    tropical = compute_now(lat=lat, lon=lon, tz_offset_hours=tz_offset_hours)
    now_utc = datetime.fromisoformat(tropical["now_utc"]).replace(tzinfo=timezone.utc)
    year_frac = now_utc.year + (now_utc.timetuple().tm_yday / 365.2425)
    ayanamsa = lahiri_ayanamsa(year_frac)
    sidereal_bodies = []
    for b in tropical["bodies"]:
        lon_deg = (b["absolute_deg"] - ayanamsa) % 360
        sign, deg = _to_sign(lon_deg)
        sidereal_bodies.append({
            "body": b["body"],
            "sign": sign,
            "degree": round(deg, 4),
            "absolute_deg": round(lon_deg, 4),
            "is_retrograde": b.get("is_retrograde"),
        })
    return {
        **tropical,
        "tropical": {"bodies": tropical["bodies"]},
        "sidereal": {"bodies": sidereal_bodies},
    }


# Aspects transits can form to natal bodies, with orb and "karmic weight"
_ASPECTS = {
    "conjunction": 0.0,
    "sextile": 60.0,
    "square": 90.0,
    "trine": 120.0,
    "opposition": 180.0,
}
_ORB_DEG = {
    "conjunction": 6.0,
    "sextile": 4.0,
    "square": 6.0,
    "trine": 6.0,
    "opposition": 6.0,
}

# Bodies that make big life impacts when they aspect natal points
_SLOW_BODIES = {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"}


def _angular_diff(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


def compute_transits_to_natal(
    natal_chart: dict, lat: float, lon: float, tz_offset_hours: float = 7.0
) -> list[dict]:
    """Find active transits to natal bodies right now.

    Args:
      natal_chart: output of compute_chart (bodies + ascendant)
      lat, lon: user's current location (for house placement)

    Returns:
      List of contacts:
        {transit, natal, aspect, orb, applying, sign, house, impact_weight}

    This is the personalization engine: every user gets a different set
    of contacts because their natal chart differs. Two people born on the
    same day at the same tz still differ if their birth location moves
    their Ascendant.
    """
    now = compute_now(lat=lat, lon=lon, tz_offset_hours=tz_offset_hours)

    natal_bodies = []
    for b in natal_chart["bodies"]:
        natal_bodies.append({
            "name": b["body"],
            "abs_deg": b["absolute_deg"],
            "sign": b["sign"],
            "is_retrograde": b.get("is_retrograde", False),
        })
    # ASC as a contact point
    natal_bodies.append({
        "name": "ASC",
        "abs_deg": natal_chart["ascendant"]["absolute_deg"],
        "sign": natal_chart["ascendant"]["sign"],
        "is_retrograde": False,
    })

    contacts = []
    for transit_body in now["bodies"]:
        tb_deg = transit_body["absolute_deg"]
        tb_name = transit_body["body"]
        tb_retro = transit_body.get("is_retrograde", False)

        for natal in natal_bodies:
            for aspect_name, aspect_deg in _ASPECTS.items():
                orb = _angular_diff(tb_deg, natal["abs_deg"] + aspect_deg)
                if orb > _ORB_DEG[aspect_name]:
                    continue

                # Impact weight: slow transiting body + tight orb + retrograde
                weight = 1.0
                if tb_name in _SLOW_BODIES:
                    weight *= 2.5
                weight *= max(0.1, 1.0 - (orb / _ORB_DEG[aspect_name]))
                if tb_retro:
                    weight *= 1.3  # retro transits linger

                contacts.append({
                    "transit": tb_name,
                    "natal": natal["name"],
                    "aspect": aspect_name,
                    "orb": round(orb, 2),
                    "impact_weight": round(weight, 3),
                    "transit_sign": transit_body["sign"],
                    "natal_sign": natal["sign"],
                })

    # sort by impact descending
    contacts.sort(key=lambda c: c["impact_weight"], reverse=True)
    return contacts
