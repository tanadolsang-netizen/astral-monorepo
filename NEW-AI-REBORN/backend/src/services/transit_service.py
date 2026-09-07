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


def compute_now(lat: float, lon: float, tz_offset_hours: float = 7.0) -> dict:
    now_utc = datetime.now(timezone.utc)
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
