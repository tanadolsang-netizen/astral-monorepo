from datetime import date, time

from src.services.chart_service import compute_chart, SIGNS
from src.services.composite_service import (
    circular_midpoint,
    compute_composite,
    compute_relationship_score,
)


def _synth(bodies: dict[str, float]) -> dict:
    return {"name": "X", "system": "tropical", "bodies": [
        {"body": n, "sign": "เมษ(Aries)", "degree": d % 30, "absolute_deg": d}
        for n, d in bodies.items()
    ]}


# ── circular_midpoint ───────────────────────────────────────────────

def test_midpoint_same_sign():
    assert circular_midpoint(10.0, 20.0) == 15.0


def test_midpoint_across_sign_boundary():
    mp = circular_midpoint(25.0, 35.0)
    assert abs(mp - 30.0) < 1e-9


def test_midpoint_wraparound():
    mp = circular_midpoint(350.0, 10.0)
    assert abs(mp - 0.0) < 1e-9 or abs(mp - 360.0) < 1e-9


def test_midpoint_symmetric():
    assert circular_midpoint(10.0, 50.0) == circular_midpoint(50.0, 10.0)


# ── compute_composite ───────────────────────────────────────────────

def test_composite_returns_matching_bodies_only():
    ca = _synth({"Sun": 10.0, "Moon": 50.0, "Venus": 90.0})
    cb = _synth({"Sun": 20.0, "Moon": 40.0})
    comp = compute_composite(ca, cb)
    names = {b["body"] for b in comp["bodies"]}
    assert "Sun" in names
    assert "Moon" in names
    assert "Venus" not in names


def test_composite_body_fields():
    ca = _synth({"Sun": 10.0, "Moon": 20.0})
    cb = _synth({"Sun": 10.0, "Moon": 20.0})
    comp = compute_composite(ca, cb)
    for b in comp["bodies"]:
        assert set(b.keys()) == {"body", "sign", "degree", "absolute_deg"}
        assert b["sign"] in SIGNS
        assert 0 <= b["degree"] < 30


def test_composite_name_combines():
    ca = _synth({"Sun": 10.0})
    ca["name"] = "Alice"
    cb = _synth({"Sun": 10.0})
    cb["name"] = "Bob"
    comp = compute_composite(ca, cb)
    assert comp["name"] == "Alice & Bob"


def test_composite_positions_are_midpoints():
    ca = _synth({"Sun": 10.0, "Moon": 100.0})
    cb = _synth({"Sun": 30.0, "Moon": 140.0})
    comp = compute_composite(ca, cb)
    by_name = {b["body"]: b for b in comp["bodies"]}
    assert by_name["Sun"]["absolute_deg"] == 20.0
    assert by_name["Moon"]["absolute_deg"] == 120.0


# ── compute_relationship_score ──────────────────────────────────────

def test_score_range():
    ca = _synth({"Sun": 0.0, "Moon": 60.0, "Mercury": 120.0,
                 "Venus": 180.0, "Mars": 240.0})
    cb = _synth({"Sun": 5.0, "Moon": 65.0, "Mercury": 125.0,
                 "Venus": 185.0, "Mars": 245.0})
    result = compute_relationship_score(ca, cb)
    assert 0 <= result["score"] <= 100


def test_identical_charts_score_higher_than_opposite():
    same_a = _synth({"Sun": 0.0, "Moon": 60.0, "Mercury": 120.0,
                      "Venus": 180.0, "Mars": 240.0})
    same_b = _synth({"Sun": 0.0, "Moon": 60.0, "Mercury": 120.0,
                      "Venus": 180.0, "Mars": 240.0})
    opp_b = _synth({"Sun": 180.0, "Moon": 240.0, "Mercury": 300.0,
                     "Venus": 0.0, "Mars": 60.0})
    high = compute_relationship_score(same_a, same_b)["score"]
    low = compute_relationship_score(same_a, opp_b)["score"]
    assert high > low
