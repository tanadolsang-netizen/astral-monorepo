from src.services.aspects import compute_cross_aspects


def _chart(bodies: dict[str, float]) -> dict:
    return {"bodies": [{"body": name, "absolute_deg": deg} for name, deg in bodies.items()]}


def test_detects_conjunction_within_orb():
    chart_a = _chart({"Sun": 10.0})
    chart_b = _chart({"Moon": 12.0})
    aspects = compute_cross_aspects(chart_a, chart_b)
    assert len(aspects) == 1
    result = aspects[0]
    assert result["body_a"] == "Sun"
    assert result["body_b"] == "Moon"
    assert result["aspect"] == "conjunction"
    assert result["orb"] == 2.0
    assert isinstance(result["applying"], bool)


def test_no_aspect_outside_any_orb():
    chart_a = _chart({"Sun": 0.0})
    chart_b = _chart({"Moon": 40.0})
    assert compute_cross_aspects(chart_a, chart_b) == []


def test_detects_opposition_across_wraparound():
    chart_a = _chart({"Mars": 5.0})
    chart_b = _chart({"Venus": 183.0})
    aspects = compute_cross_aspects(chart_a, chart_b)
    assert len(aspects) == 1
    assert aspects[0]["aspect"] == "opposition"
    assert aspects[0]["orb"] == 2.0


def test_results_sorted_by_tightest_orb_first():
    chart_a = _chart({"Sun": 0.0, "Moon": 0.0})
    chart_b = _chart({"Mercury": 1.0, "Venus": 61.0})
    aspects = compute_cross_aspects(chart_a, chart_b)
    orbs = [a["orb"] for a in aspects]
    assert orbs == sorted(orbs)
