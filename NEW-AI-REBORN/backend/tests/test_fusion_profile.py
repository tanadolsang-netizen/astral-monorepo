"""Profile Store tests — save once, read by name.

Ground truth: M = 1997-05-19 05:45 ICT Chonburi; the fusion engine's verified
Saturday behavior is Saturn day-lord + Ju-Saturn backdrop (test_fusion_engine).
"""

from datetime import date

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

M_PROFILE = {
    "date": "1997-05-19",
    "time": "05:45:00",
    "tz_offset_hours": 7.0,
    "lat": 13.36,
    "lon": 100.98,
}


def test_profile_roundtrip_and_reading(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_MEMORY_ROOT", str(tmp_path))
    # re-import-free approach: call helpers through the API after env set;
    # router reads env at request time via _profiles_dir().
    r = client.put("/v1/fusion/profile/M", json=M_PROFILE)
    assert r.status_code == 200, r.text
    assert r.json() == {"saved": True, "name": "M"}

    g = client.get("/v1/fusion/profile/M")
    assert g.status_code == 200
    body = g.json()
    assert body["date"] == "1997-05-19"
    assert body["lat"] == 13.36

    # Pin a known Saturday (2026-08-22): day-lord Saturn + lucky number 9.
    # Using "today" made this test flaky — it only passed on Saturdays.
    today = client.post(
        "/v1/fusion/today/by-name/M?lang=th",
        json={"on": "2026-08-22"},
    )
    assert today.status_code == 200, today.text
    reading = today.json()["reading"]
    text = reading["synthesis"]
    assert "Saturn" in text and "9" in text  # Saturday lord + lucky number 9
    assert reading["domains"], "domains must not be empty"


def test_profile_missing_returns_404(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_MEMORY_ROOT", str(tmp_path))
    r = client.post("/v1/fusion/today/by-name/nobody?lang=th")
    assert r.status_code == 404
