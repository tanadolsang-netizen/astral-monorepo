"""Solar and lunar returns.

A solar return is the moment the Sun's ecliptic longitude comes back to its
exact natal degree, nearest a requested calendar year (this recurs roughly
once a year, close to the birthday). A lunar return is the same idea for the
Moon, nearest a requested date (this recurs roughly every 27-29 days).

Both are found the same way: a numeric search over time for when a body's
ecliptic longitude crosses a target degree, using the same Skyfield call
chart_service.py uses for a body's position (earth.at(t).observe(...).ecliptic_latlon()).
There is no closed-form solution for "when does this planet reach exactly
this longitude" against a general ephemeris, so this is a coarse forward
scan for a sign change in the signed angular distance to the target,
followed by bisection to tighten it — not an analytic solve. Precision is
bounded by the bisection cutoff below (~1 second of time), which is far
finer than the few-arcminute accuracy meaningful for a return chart anyway.
"""

from datetime import date as date_type, time as time_type, datetime, timedelta, timezone

from src.services.chart_service import compute_chart, lahiri_ayanamsa
from src.services.ephemeris import earth, eph, ts

_BODY_KEYS = {"Sun": "sun", "Moon": "moon"}

# Any genuine longitude crossing moves by at most a few degrees per search
# step (the Moon, the fastest body used here, covers ~13deg/day). The signed
# angular distance below wraps at +-180deg, so far away from the target
# degree (on the opposite side of the circle) there is an unrelated ~360deg
# discontinuity that would otherwise look like a second "crossing" to a
# naive sign-change test. Anything jumping more than this threshold between
# consecutive samples is that wrap artifact, not a real crossing.
_JUMP_GUARD_DEG = 180.0


def _longitude_at(dt_utc: datetime, body: str, system: str) -> float:
    """Ecliptic longitude of `body` at `dt_utc`, in the same frame (tropical or
    Lahiri sidereal) chart_service.compute_chart uses, so it is directly
    comparable to a natal chart's body["absolute_deg"].
    """
    t = ts.from_datetime(dt_utc)
    pos = earth.at(t).observe(eph[_BODY_KEYS[body]])
    _, lon_ecl, _ = pos.ecliptic_latlon()
    lon_deg = lon_ecl.degrees % 360
    if system == "sidereal":
        year_frac = dt_utc.year + (dt_utc.timetuple().tm_yday / 365.2425)
        lon_deg = (lon_deg - lahiri_ayanamsa(year_frac)) % 360
    return lon_deg


def _signed_delta(lon_deg: float, target_deg: float) -> float:
    """Shortest signed angular distance from lon_deg to target_deg, in (-180, 180]."""
    return (target_deg - lon_deg + 180) % 360 - 180


def _find_return_time(
    body: str,
    target_deg: float,
    system: str,
    search_start: datetime,
    search_days: float,
    step_days: float,
) -> datetime:
    """Bisection search for when `body`'s longitude crosses `target_deg`,
    scanning forward from `search_start` for up to `search_days`.
    """
    t0 = search_start
    d0 = _signed_delta(_longitude_at(t0, body, system), target_deg)
    steps = max(1, int(search_days / step_days))
    for i in range(1, steps + 1):
        t1 = search_start + timedelta(days=step_days * i)
        d1 = _signed_delta(_longitude_at(t1, body, system), target_deg)
        is_sign_change = (d0 <= 0 <= d1) or (d0 >= 0 >= d1)
        if is_sign_change and abs(d1 - d0) < _JUMP_GUARD_DEG:
            lo, hi, lo_delta = t0, t1, d0
            for _ in range(40):
                mid = lo + (hi - lo) / 2
                mid_delta = _signed_delta(_longitude_at(mid, body, system), target_deg)
                if (lo_delta <= 0 <= mid_delta) or (lo_delta >= 0 >= mid_delta):
                    hi = mid
                else:
                    lo, lo_delta = mid, mid_delta
                if (hi - lo) < timedelta(seconds=1):
                    break
            return lo + (hi - lo) / 2
        t0, d0 = t1, d1
    raise ValueError(
        f"No {body} return found within {search_days} days of {search_start.isoformat()}"
    )


def _build_return_chart(
    name: str,
    body: str,
    return_dt_utc: datetime,
    tz_offset_hours: float,
    lat: float,
    lon: float,
    system: str,
) -> dict:
    dt_local = return_dt_utc + timedelta(hours=tz_offset_hours)
    chart = compute_chart(
        name=f"{name} ({body} return)",
        date=dt_local.date(),
        time=dt_local.time().replace(microsecond=0),
        tz_offset_hours=tz_offset_hours,
        lat=lat,
        lon=lon,
        system=system,
    )
    return {
        "body": body,
        "return_datetime_utc": return_dt_utc.isoformat().replace("+00:00", "Z"),
        "chart": chart,
    }


def compute_solar_return(
    name: str,
    birth_date: date_type,
    birth_time: time_type,
    target_year: int,
    tz_offset_hours: float = 7.0,
    lat: float = 13.8591,
    lon: float = 100.5217,
    system: str = "tropical",
    return_lat: float | None = None,
    return_lon: float | None = None,
) -> dict:
    """Solar return chart for `target_year`, searched near the birthday in that year.

    Relocation (return_lat/return_lon) is optional; defaults to the natal
    location, per the traditional definition of a solar return.
    """
    natal_chart = compute_chart(
        name=name, date=birth_date, time=birth_time,
        tz_offset_hours=tz_offset_hours, lat=lat, lon=lon, system=system,
    )
    natal_sun = next(b for b in natal_chart["bodies"] if b["body"] == "Sun")
    target_deg = natal_sun["absolute_deg"]

    try:
        anchor_date = date_type(target_year, birth_date.month, birth_date.day)
    except ValueError:
        # Feb 29 birthdays don't exist in non-leap target years.
        anchor_date = date_type(target_year, birth_date.month, 28)
    search_start = datetime.combine(anchor_date, time_type(0, 0), tzinfo=timezone.utc) - timedelta(days=6)

    return_dt_utc = _find_return_time("Sun", target_deg, system, search_start, search_days=12, step_days=0.5)

    result = _build_return_chart(
        name, "Sun", return_dt_utc, tz_offset_hours,
        return_lat if return_lat is not None else lat,
        return_lon if return_lon is not None else lon,
        system,
    )
    result["target_year"] = target_year
    result["natal_longitude"] = target_deg
    result["natal"] = natal_chart
    return result


def compute_lunar_return(
    name: str,
    birth_date: date_type,
    birth_time: time_type,
    target_date: date_type,
    tz_offset_hours: float = 7.0,
    lat: float = 13.8591,
    lon: float = 100.5217,
    system: str = "tropical",
    return_lat: float | None = None,
    return_lon: float | None = None,
) -> dict:
    """Lunar return chart nearest `target_date` (the Moon returns to its natal
    longitude roughly every 27-29 days, so the search window is +-15 days).
    """
    natal_chart = compute_chart(
        name=name, date=birth_date, time=birth_time,
        tz_offset_hours=tz_offset_hours, lat=lat, lon=lon, system=system,
    )
    natal_moon = next(b for b in natal_chart["bodies"] if b["body"] == "Moon")
    target_deg = natal_moon["absolute_deg"]

    search_start = datetime.combine(target_date, time_type(0, 0), tzinfo=timezone.utc) - timedelta(days=15)
    return_dt_utc = _find_return_time("Moon", target_deg, system, search_start, search_days=30, step_days=0.25)

    result = _build_return_chart(
        name, "Moon", return_dt_utc, tz_offset_hours,
        return_lat if return_lat is not None else lat,
        return_lon if return_lon is not None else lon,
        system,
    )
    result["target_date"] = target_date.isoformat()
    result["natal_longitude"] = target_deg
    result["natal"] = natal_chart
    return result
