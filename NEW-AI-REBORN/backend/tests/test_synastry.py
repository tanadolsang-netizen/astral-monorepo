from datetime import date, time

from fastapi.testclient import TestClient

from src.main import app
from src.services.chart_service import compute_chart
from src.services.composite_service import compute_relationship_score

client = TestClient(app)


def _pair(name_a="Alice", date_a="1990-05-15", time_a="14:30",
          name_b="Bob", date_b="1992-11-02", time_b="08:15"):
    base = {"tz_offset_hours": 7, "lat": 13.7563, "lon": 100.5018, "system": "tropical"}
    return {
        "a": {"name": name_a, "date": date_a, "time": time_a, **base},
        "b": {"name": name_b, "date": date_b, "time": time_b, **base},
    }


# ── /composite endpoint ─────────────────────────────────────────────

def test_composite_endpoint_200():
    res = client.post("/v1/synastry/composite", json=_pair())
    assert res.status_code == 200
    body = res.json()
    assert "composite" in body
    assert isinstance(body["composite"]["bodies"], list)
    assert len(body["composite"]["bodies"]) == 10


def test_composite_endpoint_name_combines():
    res = client.post("/v1/synastry/composite", json=_pair())
    assert res.json()["composite"]["name"] == "Alice & Bob"


# ── /score endpoint ─────────────────────────────────────────────────

def test_score_endpoint_200():
    res = client.post("/v1/synastry/score", json=_pair())
    assert res.status_code == 200
    body = res.json()
    assert "score" in body
    assert "cross_aspects" in body
    assert "note" in body


def test_score_in_range():
    res = client.post("/v1/synastry/score", json=_pair())
    score = res.json()["score"]
    assert 0 <= score <= 100


def test_score_note_contains_thai():
    res = client.post("/v1/synastry/score", json=_pair())
    assert "คะแนน" in res.json()["note"]


# ── score unit (no ephemeris) ───────────────────────────────────────

def _synth(name, bds):
    return {"name": name, "system": "tropical", "bodies": [
        {"body": n, "sign": "เมษ(Aries)", "degree": d % 30, "absolute_deg": d}
        for n, d in bds.items()
    ]}


def test_unit_score_identical_higher_than_opposite():
    same = _synth("X", {"Sun": 0, "Moon": 60, "Mercury": 120,
                         "Venus": 180, "Mars": 240})
    opp = _synth("Y", {"Sun": 180, "Moon": 240, "Mercury": 300,
                        "Venus": 0, "Mars": 60})
    assert compute_relationship_score(same, same)["score"] > \
           compute_relationship_score(same, opp)["score"]


def test_cross_aspects_still_works():
    res = client.post("/v1/synastry/cross-aspects", json=_pair())
    assert res.status_code == 200
    assert "cross_aspects" in res.json()
