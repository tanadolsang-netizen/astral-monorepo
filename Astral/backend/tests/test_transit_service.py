from src.services.transit_service import compute_now


def test_compute_now_shape_and_types():
    result = compute_now(lat=13.7563, lon=100.5018, tz_offset_hours=7.0)
    assert result["lat"] == 13.7563
    assert result["lon"] == 100.5018
    assert len(result["bodies"]) == 10
    for b in result["bodies"]:
        assert isinstance(b["is_retrograde"], bool)
        assert 0 <= b["degree"] < 30
        assert 0 <= b["absolute_deg"] < 360


def test_sun_and_moon_are_never_retrograde():
    result = compute_now(lat=13.7563, lon=100.5018, tz_offset_hours=7.0)
    by_body = {b["body"]: b for b in result["bodies"]}
    assert by_body["Sun"]["is_retrograde"] is False
    assert by_body["Moon"]["is_retrograde"] is False
