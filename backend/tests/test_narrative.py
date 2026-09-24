"""
Tests for narrative engine and routers.
"""
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_natal_narrative_endpoint():
    res = client.post(
        "/v1/narrative/natal",
        json={
            "name": "Test",
            "date": "1990-05-15",
            "time": "14:30:00",
            "tz_offset_hours": 7,
            "lat": 13.7563,
            "lon": 100.5018,
            "system": "tropical",
        },
        params={"lang": "th"},
    )
    assert res.status_code == 200
    body = res.json()
    assert "sections" in body or "overview" in body
    if "sections" in body:
        assert "overview" in body["sections"]
        assert "personality" in body["sections"]
        assert "summary" in body["sections"]
    else:
        assert "overview" in body
        assert "personality" in body
        assert "summary" in body


def test_natal_narrative_en():
    res = client.post(
        "/v1/narrative/natal",
        json={
            "name": "Test",
            "date": "1990-05-15",
            "time": "14:30:00",
            "tz_offset_hours": 7,
            "lat": 13.7563,
            "lon": 100.5018,
        },
        params={"lang": "en"},
    )
    assert res.status_code == 200
    body = res.json()
    assert "sections" in body or "overview" in body


def test_transit_narrative_endpoint():
    res = client.post(
        "/v1/narrative/transit",
        json={
            "name": "Test",
            "date": "1990-05-15",
            "time": "14:30:00",
            "tz_offset_hours": 7,
            "lat": 13.7563,
            "lon": 100.5018,
        },
        params={"lang": "th"},
    )
    assert res.status_code == 200
    body = res.json()
    assert "sections" in body or "active_transits" in body or "overview" in body


def test_synastry_narrative_endpoint():
    res = client.post(
        "/v1/narrative/synastry",
        json={
            "a": {
                "name": "A",
                "date": "1990-05-15",
                "time": "14:30:00",
                "tz_offset_hours": 7,
                "lat": 13.7563,
                "lon": 100.5018,
            },
            "b": {
                "name": "B",
                "date": "1992-11-02",
                "time": "10:00:00",
                "tz_offset_hours": 7,
                "lat": 13.7563,
                "lon": 100.5018,
            },
        },
        params={"lang": "th"},
    )
    assert res.status_code == 200
    body = res.json()
    # Response ใหม่มี sections กับ overview/personality/summary แทน dynamics/strengths/challenges
    has_structure = ("sections" in body or "overview" in body or 
                     "dynamics" in body or "challenges" in body)
    assert has_structure


def test_composite_narrative_endpoint():
    res = client.post(
        "/v1/narrative/composite",
        json={
            "a": {
                "name": "A",
                "date": "1990-05-15",
                "time": "14:30:00",
                "tz_offset_hours": 7,
                "lat": 13.7563,
                "lon": 100.5018,
            },
            "b": {
                "name": "B",
                "date": "1992-11-02",
                "time": "10:00:00",
                "tz_offset_hours": 7,
                "lat": 13.7563,
                "lon": 100.5018,
            },
        },
    )
    assert res.status_code == 200


def test_grand_varshaphal_narrative():
    res = client.post(
        "/v1/narrative/grand/varshaphal",
        json={"data": {"muntha": {"sign": "Aries"}}},
        params={"lang": "th"},
    )
    assert res.status_code == 200


def test_grand_ziwei_narrative():
    res = client.post(
        "/v1/narrative/grand/ziwei",
        json={"data": {"palace_wheel": [{"name_en": "Life", "branch": "寅"}]}},
        params={"lang": "th"},
    )
    assert res.status_code == 200


def test_grand_fixed_stars_narrative():
    res = client.post(
        "/v1/narrative/grand/fixed-stars",
        json={"data": {"conjunctions": [{"star": "Aldebaran"}]}},
        params={"lang": "th"},
    )
    assert res.status_code == 200


def test_grand_asteroids_narrative():
    res = client.post(
        "/v1/narrative/grand/asteroids",
        json={"data": {"positions": {"Chiron": {"absolute_deg": 120.5}}}},
        params={"lang": "th"},
    )
    assert res.status_code == 200


def test_grand_nakshatra_narrative():
    res = client.post(
        "/v1/narrative/grand/nakshatra",
        json={"data": {"moon": {"name": "Ashwini"}}},
        params={"lang": "th"},
    )
    assert res.status_code == 200


def test_grand_dasha_narrative():
    res = client.post(
        "/v1/narrative/grand/dasha",
        json={"data": {"Jupiter": {}}},
        params={"lang": "th"},
    )
    assert res.status_code == 200


def test_grand_yoga_narrative():
    res = client.post(
        "/v1/narrative/grand/yoga",
        json={"data": {"Gaja Kesari": {}}},
        params={"lang": "th"},
    )
    assert res.status_code == 200


def test_grand_arabic_parts_narrative():
    res = client.post(
        "/v1/narrative/grand/arabic-parts",
        json={"data": {"Part of Fortune": {}}},
        params={"lang": "th"},
    )
    assert res.status_code == 200
