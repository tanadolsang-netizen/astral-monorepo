from datetime import date, time

from src.services.chart_service import BODIES, compute_chart


def _chart(system="tropical"):
    return compute_chart(
        name="Test",
        date=date(1990, 5, 15),
        time=time(14, 30),
        tz_offset_hours=7.0,
        lat=13.7563,
        lon=100.5018,
        system=system,
    )


def test_compute_chart_returns_all_bodies():
    chart = _chart()
    assert {b["body"] for b in chart["bodies"]} == set(BODIES)


def test_body_positions_are_in_range():
    chart = _chart()
    for b in chart["bodies"]:
        assert 0 <= b["degree"] < 30
        assert 0 <= b["absolute_deg"] < 360
    asc = chart["ascendant"]
    assert 0 <= asc["degree"] < 30
    assert 0 <= asc["absolute_deg"] < 360


def test_sidereal_is_offset_from_tropical_by_ayanamsa():
    tropical = _chart("tropical")
    sidereal = _chart("sidereal")
    for t_body, s_body in zip(tropical["bodies"], sidereal["bodies"]):
        assert t_body["body"] == s_body["body"]
        offset = (t_body["absolute_deg"] - s_body["absolute_deg"]) % 360
        # Lahiri ayanamsa in 1990 is roughly 23.6-23.7 degrees.
        assert 23.0 < offset < 24.5


def test_datetime_utc_reflects_timezone_offset():
    chart = _chart()
    assert chart["datetime_utc"].startswith("1990-05-15T07:30:00")
