"""Vedic + Muhurta engine tests — verified anchors + endpoint contracts."""

from __future__ import annotations

from datetime import datetime

from fastapi.testclient import TestClient

from src.main import app
from src.services.vedic_service import compute_vedic, _sidereal, _ayanamsa
from src.services.muhurta_service import find_windows, score_chart, _is_mercury_rx

client = TestClient(app)


# ── vedic ────────────────────────────────────────────────────────────
def test_ayanamsa_sane() -> None:
    # Lahiri ~23.85° at J2000, drifts ~50.29"/yr → 2026 ≈ 24.22°
    a = _ayanamsa(datetime(2026, 6, 1))
    assert 24.0 < a < 24.4


def test_sidereal_shifts_back() -> None:
    tropical = 100.0
    sid = _sidereal(tropical, datetime(2026, 1, 1))
    assert abs((tropical - sid) - _ayanamsa(datetime(2026, 1, 1))) < 0.01


def test_vedic_1990_05_19_anchor() -> None:
    # 1990-05-19 05:45 ICT Bangkok: sidereal Sun in Taurus (Vrishabha)
    r = compute_vedic("1990-05-19T05:45", lat=13.75, lon=100.52)
    assert r["surya_rashi"]["sign_en"] == "Vrishabha"
    assert r["nakshatra"]["pada"] in (1, 2, 3, 4)
    assert len(r["interpretation"]["th"]) > 80
    assert len(r["interpretation"]["en"]) > 60


def test_vedic_endpoint() -> None:
    res = client.post("/v1/vedic/chart", json={
        "name": "test",
        "birth": {"date": "2000-01-01", "time": "12:00"},
    })
    assert res.status_code == 200
    data = res.json()
    assert data["system"] == "vedic"
    assert "chandra_rashi" in data and "nakshatra" in data


# ── muhurta ──────────────────────────────────────────────────────────
def test_mercury_rx_windows_cover_oct_nov_2026() -> None:
    assert _is_mercury_rx(datetime(2026, 11, 1)) is True
    assert _is_mercury_rx(datetime(2026, 12, 1)) is False


def test_find_windows_contract_launch() -> None:
    # spec §5: launch scan Oct–Dec 2026 must skip Mercury Rx 24 Oct–13 Nov
    r = find_windows("contract", "2026-10-01", days=80, top_n=3)
    assert r["action"] == "contract"
    for w in r["windows"]:
        when = datetime.fromisoformat(w["when_local"])
        assert not (datetime(2026, 10, 24) <= when <= datetime(2026, 11, 13)), \
            f"window inside Mercury Rx: {when}"
        assert w["score"] >= 12
    assert len(r["summary_th"]) > 30
    assert len(r["summary_en"]) > 30


def test_find_windows_unknown_action_raises() -> None:
    try:
        find_windows("party", "2026-10-01")
        raise AssertionError("should have raised ValueError")
    except ValueError:
        pass


def test_score_chart_returns_reasons() -> None:
    from src.services.chart_service import compute_chart
    c = compute_chart("t", datetime(2026, 11, 20).date(),
                      datetime(2026, 11, 20).time(), lat=13.75, lon=100.5)
    score, th, en = score_chart(c, "business")
    assert isinstance(score, int)
    assert len(th) == len(en)


def test_muhurta_endpoints() -> None:
    h = client.get("/v1/muhurta/actions")
    assert h.status_code == 200
    ids = [a["id"] for a in h.json()["actions"]]
    assert set(ids) == {"marriage", "business", "contract", "travel", "moving"}

    r = client.post("/v1/muhurta/find", json={
        "action": "marriage", "start_date": "2027-01-01", "days": 60,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["action"] == "marriage"

    bad = client.post("/v1/muhurta/find", json={
        "action": "party", "start_date": "2027-01-01",
    })
    assert bad.status_code == 422
