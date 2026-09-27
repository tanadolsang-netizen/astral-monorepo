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


def test_draw_spread_never_repeats_a_card_for_any_name():
    """The top-up loop used to draw blind from the whole deck.

    It only surfaced for the names whose weighted sample happened to collapse
    on a duplicate, which is why a single-name test passed most of the time.
    Sweep a wide name space so the assertion covers the tail.
    """
    for i in range(300):
        result = draw_spread(f"person-{i}", spread="celtic_cross")
        names = [c["card"] for c in result["cards"]]
        assert len(names) == 10, f"person-{i}: got {len(names)} cards"
        assert len(set(names)) == 10, f"person-{i}: duplicate in {names}"


def test_draw_spread_is_stable_across_processes():
    """Same name, same spread -- in a different interpreter.

    The seed used to come from ``hash(name)``, which Python salts per process.
    Within one test session that looks perfectly deterministic, so only a real
    second process exposes it.  This is what made a user's reading change on
    every page reload.
    """
    import os
    import subprocess
    import sys

    snippet = (
        "from src.services.tarot_service import draw_spread;"
        "print(','.join(c['card'] for c in"
        " draw_spread('Mark', spread='celtic_cross')['cards']))"
    )
    runs = set()
    for seed in ("0", "1", "12345"):
        out = subprocess.run(
            [sys.executable, "-c", snippet],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONHASHSEED": seed},
            cwd=os.getcwd(),
        )
        assert out.returncode == 0, out.stderr
        runs.add(out.stdout.strip())
    assert len(runs) == 1, f"spread changed with PYTHONHASHSEED: {runs}"


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
