from datetime import date, time

import pytest
from fastapi.testclient import TestClient

from src.integrations.supabase_client import User
from src.main import app
from src.routers import dashboard as dashboard_router
from src.services import chart_store
from src.services.caveat import CAVEAT
from src.services.chart_service import compute_chart
from src.services.element_service import compute_element_balance
from src.services.tarot_service import FULL_DECK, _weights_for, draw_spread
from src.services.window_service import compute_windows, find_shared_windows

client = TestClient(app)

_MARK = dict(name="Mark", date=date(1997, 5, 19), time=time(5, 45),
             tz_offset_hours=7.0, lat=13.3611, lon=100.9847)
_MAI = dict(name="Mai", date=date(2001, 8, 18), time=time(22, 32),
            tz_offset_hours=7.0, lat=13.8622, lon=100.5144)

_TEST_USER = User(id="test-user", email="test@astral.app")


# --- element-weighted tarot (#3) ----------------------------------------

def test_weights_boost_the_lacking_element():
    chart = compute_chart(system="tropical", **_MARK)  # water 0%
    weights = _weights_for(compute_element_balance(chart))

    cups = [w for c, w in zip(FULL_DECK, weights) if c["name"].endswith("of Cups")]
    earth = [w for c, w in zip(FULL_DECK, weights) if c["name"].endswith("of Pentacles")]
    assert min(cups) > max(earth)


def test_major_arcana_stay_at_baseline_weight():
    chart = compute_chart(system="tropical", **_MARK)
    weights = _weights_for(compute_element_balance(chart))
    majors = [w for c, w in zip(FULL_DECK, weights) if c["arcana"] == "major"]
    assert all(w == 1.0 for w in majors)


def test_no_balance_means_uniform_weights():
    assert set(_weights_for(None)) == {1.0}


def test_weighted_draw_has_no_duplicates():
    chart = compute_chart(system="tropical", **_MAI)
    result = draw_spread("Mai", spread="celtic_cross",
                         element_balance=compute_element_balance(chart))
    names = [c["card"] for c in result["cards"]]
    assert len(set(names)) == 10
    # Recalibrated with the ASC-formula fix: Mai's rising sign moved into
    # Taurus, whose +3.0 earth weight lifts earth off the bottom — air is
    # now her thinnest element (dominant stays fire).
    assert result["tilted_toward"] == "air"


def test_api_draw_with_birth_data_reports_tilt():
    res = client.post("/v1/tarot/draw", json={
        "name": "Mai",
        "spread": "three_card",
        "birth": {"date": "2001-08-18", "time": "22:32:00",
                  "lat": 13.8622, "lon": 100.5144},
    })
    assert res.status_code == 200
    body = res.json()
    assert body["tilted_toward"] == "air"  # see note on test above
    assert body["elements"]["dominant"] == "fire"


# --- transit windows (#4) ------------------------------------------------

def test_windows_returns_three_slots_per_day():
    natal = compute_chart(system="tropical", **_MARK)
    out = compute_windows(natal, start=date(2026, 8, 21), days=3)
    assert len(out["slots"]) == 9
    assert {s["hour"] for s in out["slots"]} == {6, 12, 20}


def test_windows_best_is_sorted_and_rated():
    natal = compute_chart(system="tropical", **_MAI)
    out = compute_windows(natal, start=date(2026, 8, 21), days=7)
    scores = [s["score"] for s in out["best"]]
    assert scores == sorted(scores, reverse=True)
    assert all(s["rating"] in {"favourable", "neutral", "caution"} for s in out["slots"])


def test_windows_rejects_out_of_range_days():
    natal = compute_chart(system="tropical", **_MARK)
    with pytest.raises(ValueError):
        compute_windows(natal, start=date(2026, 8, 21), days=99)


def test_shared_windows_require_both_positive():
    a = compute_windows(compute_chart(system="tropical", **_MARK),
                        start=date(2026, 8, 21), days=7)
    b = compute_windows(compute_chart(system="tropical", **_MAI),
                        start=date(2026, 8, 21), days=7)
    shared = find_shared_windows(a, b)
    assert all(s["score_a"] > 0 and s["score_b"] > 0 for s in shared)
    combined = [s["combined"] for s in shared]
    assert combined == sorted(combined, reverse=True)


def test_api_windows_endpoint():
    res = client.post("/v1/transit/windows", json={
        "natal": {"name": "Mark", "date": "1997-05-19", "time": "05:45:00",
                  "lat": 13.3611, "lon": 100.9847},
        "start": "2026-08-21", "days": 3,
    })
    assert res.status_code == 200
    assert len(res.json()["slots"]) == 9


def test_api_shared_windows_endpoint():
    res = client.post("/v1/transit/windows/shared", json={
        "natal_a": {"name": "Mark", "date": "1997-05-19", "time": "05:45:00",
                    "lat": 13.3611, "lon": 100.9847},
        "natal_b": {"name": "Mai", "date": "2001-08-18", "time": "22:32:00",
                    "lat": 13.8622, "lon": 100.5144},
        "start": "2026-08-21", "days": 7,
    })
    assert res.status_code == 200
    assert len(res.json()["shared"]) <= 5


# --- caveat coverage (#5) ------------------------------------------------

def test_reading_endpoints_all_return_the_caveat():
    responses = [
        client.post("/v1/natal/compute", json={
            "name": "Mark", "date": "1997-05-19", "time": "05:45:00"}),
        client.post("/v1/tarot/draw", json={"name": "Mark"}),
        client.post("/v1/horary/ask", json={"question": "ทดสอบ"}),
        client.get("/v1/transit/now"),
    ]
    for res in responses:
        assert res.status_code == 200
        assert res.json()["caveat"] == CAVEAT


# --- dashboard persistence (#6) -----------------------------------------

def test_dashboard_returns_stored_rows(monkeypatch):
    app.dependency_overrides[dashboard_router._require_user] = lambda: _TEST_USER
    rows = [{"id": "abc", "name": "Mark", "date": "1997-05-19",
             "time": "05:45:00", "system": "tropical",
             "created_at": "2026-08-20T00:00:00Z"}]
    monkeypatch.setattr(chart_store, "list_recent", lambda uid, limit: rows)
    try:
        res = client.post("/v1/dashboard/recent", json={"limit": 5})
        assert res.status_code == 200
        assert res.json()["recent"][0]["name"] == "Mark"
    finally:
        app.dependency_overrides.pop(dashboard_router._require_user, None)


def test_dashboard_503_when_storage_unconfigured(monkeypatch):
    app.dependency_overrides[dashboard_router._require_user] = lambda: _TEST_USER

    def _boom(uid, limit):
        raise RuntimeError("Supabase not initialized")

    monkeypatch.setattr(chart_store, "list_recent", _boom)
    try:
        res = client.post("/v1/dashboard/recent", json={"limit": 5})
        assert res.status_code == 503
    finally:
        app.dependency_overrides.pop(dashboard_router._require_user, None)


def test_dashboard_requires_auth():
    res = client.post("/v1/dashboard/recent", json={"limit": 5})
    assert res.status_code == 401


def test_no_demo_rows_remain_in_dashboard_module():
    import src.routers.dashboard as mod
    assert not hasattr(mod, "_DEMO_RECENT")
