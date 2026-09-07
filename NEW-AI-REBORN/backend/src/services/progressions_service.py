"""Secondary progressions: "a day for a year".

The classical technique treats each day after birth as symbolic of one year
of life: the progressed chart for someone's Nth birthday is cast for the
moment birth_date + N days (same clock time, same birthplace — progressions
deliberately keep the natal location rather than relocating).
"""

from datetime import date as date_type, time as time_type, timedelta

from src.services.aspects import compute_cross_aspects
from src.services.chart_service import compute_chart


def progressed_date(birth_date: date_type, target_date: date_type) -> date_type:
    """The progressed calendar date for `target_date`: birth_date + age_in_years days.

    age_in_years is computed with the average Julian year (365.25 days) so a
    birthday-to-birthday span consistently advances by ~1 day of progression,
    matching the traditional "a day for a year" rule of thumb. The result is
    rounded to the nearest whole day before adding — `date + timedelta` only
    honours the `.days` component of a timedelta (fractional days are
    silently dropped, i.e. always floored), so rounding first avoids
    systematically under-progressing by up to a day.
    """
    age_days = round((target_date - birth_date).days / 365.25)
    return birth_date + timedelta(days=age_days)


def compute_progressions(
    name: str,
    birth_date: date_type,
    birth_time: time_type,
    target_date: date_type,
    tz_offset_hours: float = 7.0,
    lat: float = 13.8591,
    lon: float = 100.5217,
    system: str = "tropical",
) -> dict:
    """Progressed chart for `target_date`, plus its aspects back to the natal chart.

    Progressions keep the ORIGINAL birth lat/lon/tz — only the date advances
    (by the day-for-a-year rule), never the location, per the technique's
    definition.
    """
    natal_chart = compute_chart(
        name=name, date=birth_date, time=birth_time,
        tz_offset_hours=tz_offset_hours, lat=lat, lon=lon, system=system,
    )

    p_date = progressed_date(birth_date, target_date)

    progressed_chart = compute_chart(
        name=f"{name} (progressed)", date=p_date, time=birth_time,
        tz_offset_hours=tz_offset_hours, lat=lat, lon=lon, system=system,
    )

    aspects_to_natal = compute_cross_aspects(natal_chart, progressed_chart)

    return {
        "target_date": target_date.isoformat(),
        "progressed_date": p_date.isoformat(),
        "age_years": round((target_date - birth_date).days / 365.25, 4),
        "natal": natal_chart,
        "progressed": progressed_chart,
        "aspects_to_natal": aspects_to_natal,
    }
