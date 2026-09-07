from datetime import date, time

from fastapi.testclient import TestClient

from src.main import app
from src.services.chart_service import compute_chart
from src.services.element_service import ELEMENTS, compute_element_balance

client = TestClient(app)

# Mai: fire/air heavy, earth thin — used as a known-shape fixture.
_MAI = dict(
    name="Mai", date=date(2001, 8, 18), time=time(22, 32),
    tz_offset_hours=7.0, lat=13.8622, lon=100.5144,
)


def test_percentages_sum_to_100():
    chart = compute_chart(system="tropical", **_MAI)
    balance = compute_element_balance(chart)
    assert abs(sum(balance["percent"].values()) - 100.0) < 0.5


def test_all_four_elements_present_in_output():
    chart = compute_chart(system="tropical", **_MAI)
    balance = compute_element_balance(chart)
    assert set(balance["scores"]) == set(ELEMENTS)
    assert balance["dominant"] in ELEMENTS
    assert balance["lacking"] in ELEMENTS


def test_known_chart_is_earth_light():
    chart = compute_chart(system="tropical", **_MAI)
    balance = compute_element_balance(chart)
    assert balance["scores"]["earth"] < balance["scores"]["fire"]


def test_balance_works_for_sidereal_too():
    chart = compute_chart(system="sidereal", **_MAI)
    balance = compute_element_balance(chart)
    assert abs(sum(balance["percent"].values()) - 100.0) < 0.5


def test_horary_returns_chart_for_now():
    res = client.post("/v1/horary/ask", json={"question": "ควรเปลี่ยนงานตอนนี้ไหม"})
    assert res.status_code == 200
    body = res.json()
    assert body["question"] == "ควรเปลี่ยนงานตอนนี้ไหม"
    assert body["moon"]["body"] == "Moon"
    assert body["ascendant"]["body"] == "ASC"
    assert set(body["elements"]["scores"]) == set(ELEMENTS)
    assert "caveat" in body


def test_horary_rejects_empty_question():
    res = client.post("/v1/horary/ask", json={"question": ""})
    assert res.status_code == 422
