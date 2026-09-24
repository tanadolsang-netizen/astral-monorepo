from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_ready():
    res = client.get("/ready")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_natal_compute():
    res = client.post(
        "/v1/natal/compute",
        json={
            "name": "Test",
            "date": "1990-05-15",
            "time": "14:30:00",
            "tz_offset_hours": 7,
            "lat": 13.7563,
            "lon": 100.5018,
            "system": "tropical",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert len(body["bodies"]) == 10
    assert "ascendant" in body


def test_transit_now():
    res = client.get("/v1/transit/now", params={"lat": 13.7563, "lon": 100.5018, "tz": 7})
    assert res.status_code == 200
    body = res.json()
    assert len(body["bodies"]) == 10
    assert all("is_retrograde" in b for b in body["bodies"])


def test_synastry_cross_aspects_present():
    base = {
        "time": "14:30:00",
        "tz_offset_hours": 7,
        "lat": 13.7563,
        "lon": 100.5018,
        "system": "tropical",
    }
    res = client.post(
        "/v1/synastry/cross-aspects",
        json={
            "a": {"name": "A", "date": "1990-05-15", **base},
            "b": {"name": "B", "date": "1992-11-02", **base},
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert "cross_aspects" in body
    assert isinstance(body["cross_aspects"], list)


def test_branches_list_and_detail():
    res = client.get("/v1/branches/list")
    assert res.status_code == 200
    slugs = [b["slug"] for b in res.json()["branches"]]
    assert "thai-horoscope" in slugs

    detail = client.get("/v1/branches/thai-horoscope")
    assert detail.status_code == 200
    assert "content" in detail.json()


def test_branches_rejects_path_traversal():
    res = client.get("/v1/branches/..%2f..%2fpyproject")
    assert res.status_code == 404


def test_dashboard_recent_requires_auth():
    # /recent now serves the caller's own saved charts out of public.charts
    # rather than a fixed demo list, so anonymous access must be rejected.
    res = client.post("/v1/dashboard/recent", json={"limit": 2})
    assert res.status_code == 401
