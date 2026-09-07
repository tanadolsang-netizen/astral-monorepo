from fastapi.testclient import TestClient

from src.main import app
from src.services.tarot_service import FULL_DECK, SPREADS, draw_spread

client = TestClient(app)


def test_deck_has_78_unique_cards():
    assert len(FULL_DECK) == 78
    assert len({c["name"] for c in FULL_DECK}) == 78


def test_draw_spread_is_deterministic_per_name():
    a = draw_spread("Mark", spread="three_card")
    b = draw_spread("Mark", spread="three_card")
    assert a == b


def test_draw_spread_differs_across_names():
    a = draw_spread("Mark", spread="three_card")
    b = draw_spread("Mai", spread="three_card")
    assert [c["card"] for c in a["cards"]] != [c["card"] for c in b["cards"]]


def test_draw_spread_no_duplicate_cards_within_spread():
    result = draw_spread("Someone", spread="celtic_cross")
    names = [c["card"] for c in result["cards"]]
    assert len(names) == len(set(names)) == 10


def test_unknown_spread_raises():
    try:
        draw_spread("X", spread="not_real")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_api_draw_three_card():
    res = client.post("/v1/tarot/draw", json={"name": "Mark", "spread": "three_card"})
    assert res.status_code == 200
    body = res.json()
    assert body["name"] == "Mark"
    assert [c["position"] for c in body["cards"]] == ["1", "2", "3"]


def test_api_draw_invalid_spread_returns_422():
    res = client.post("/v1/tarot/draw", json={"name": "Mark", "spread": "bogus"})
    assert res.status_code == 422
