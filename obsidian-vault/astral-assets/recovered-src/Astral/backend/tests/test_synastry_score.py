"""Spec 03 §2/§4 synastry scoring — ground truths + endpoint contract.

Machine-verified anchors (spec 03 header: cross-aspects computed for real):
  Mai Venus Cancer 19.90 sextile M Mars Virgo 19.32   -> orb 0.58
  M Venus Gemini 10.15 conj Mai Saturn Gemini 13.59   -> orb 3.44
  M mean north node 1997-05-19 = Virgo ~25.75         -> no nodal contact
  DK(M) = Sun 4.37 (spec 02 §6) -> karmic via DK cross-check
Note: the spec's "M ASC Scorpio 25.96" is astronomically impossible for
05:45 ICT (minutes before sunrise the ASC must sit at the Sun's longitude);
an independent hour-angle horizon scan puts M ASC at Taurus ~26.0 and
confirms Mai ASC = Taurus 6.34 (spec value kept as ground truth).
"""

from datetime import date, time

from fastapi.testclient import TestClient

from src.main import app
from src.services.chart_service import compute_chart
from src.services.synastry_scoring import (
    DIMENSIONS,
    compute_synastry_profile,
    darakaraka,
    house_overlay,
    mean_north_node,
    north_node_deg,
)

client = TestClient(app)

M = dict(name="M", date=date(1997, 5, 19), time=time(5, 45),
         tz_offset_hours=7, lat=13.36, lon=100.98, system="tropical")
MAI = dict(name="Mai", date=date(2001, 8, 18), time=time(22, 32),
           tz_offset_hours=7, lat=13.85, lon=100.52, system="tropical")


def _pair_payload():
    base = {"tz_offset_hours": 7, "lat": 13.7563, "lon": 100.5018, "system": "tropical"}
    return {
        "a": {"name": "M", "date": "1997-05-19", "time": "05:45", **base},
        "b": {"name": "Mai", "date": "2001-08-18", "time": "22:32", **base},
    }


# ── Unit: karmic layer primitives ─────────────────────────────────────

def test_mean_node_matches_spec():
    chart = compute_chart(**M)
    node = north_node_deg(chart)
    assert node is not None
    assert abs(node - 175.75) < 0.5  # Virgo 25.75 per spec 03 §4
    jd = 2450586.15625  # 1997-05-18 15:45 UT
    assert abs(mean_north_node(jd) - 175.75) < 0.5


def test_darakaraka_owner_is_sun():
    dk = darakaraka(compute_chart(**M))
    assert dk is not None
    assert dk["planet"] == "Sun"          # spec 02 §6 verified
    assert abs(dk["degree_in_sign"] - 4.37) < 0.15


def test_house_overlay_mutual_detection():
    signs = ["เมษ(Aries)", "พฤษภ(Taurus)", "เมถุน(Gemini)", "กรกฎ(Cancer)",
             "สิงห์(Leo)", "กันย์(Virgo)", "ตุลย์(Libra)", "พิจิก(Scorpio)"]
    a = {"bodies": [], "ascendant": {"body": "ASC", "sign": signs[7], "absolute_deg": 265.0}}
    b = {"bodies": [], "ascendant": {"body": "ASC", "sign": signs[1], "absolute_deg": 36.0}}
    o = house_overlay(a, b)
    assert o["mutual_7th_asc"] is True  # Scorpio <-> Taurus mutual 7th
    assert house_overlay(a, {"bodies": [], "ascendant": {"body": "ASC", "sign": signs[0], "absolute_deg": 5.0}})["mutual_7th_asc"] is False


def test_dimensions_structure_and_range():
    prof = compute_synastry_profile(compute_chart(**M), compute_chart(**MAI))
    assert set(prof["dimensions"].keys()) == set(DIMENSIONS)
    for v in prof["dimensions"].values():
        assert 0 <= v <= 100
    assert prof["overall"] == round(sum(prof["dimensions"].values()) / 6)


def test_identical_charts_score_higher_emotional_bond_than_opposite():
    def synth(deg_shift):
        return {
            "name": "X", "system": "tropical",
            "datetime_utc": "2000-01-01T12:00:00+00:00",
            "bodies": [
                {"body": n, "sign": "s", "degree": (d + deg_shift) % 30,
                 "absolute_deg": (d + deg_shift) % 360}
                for n, d in [("Sun", 10), ("Moon", 40), ("Mercury", 70),
                             ("Venus", 100), ("Mars", 130)]
            ],
        }
    same = compute_synastry_profile(synth(0), synth(0))
    opp = compute_synastry_profile(synth(0), synth(180))
    assert same["dimensions"]["emotional_bond"] > opp["dimensions"]["emotional_bond"]
    assert same["dimensions"]["chemistry"] > opp["dimensions"]["chemistry"]


# ── Integration: POST /v1/synastry/score (real ephemeris) ─────────────

def test_score_endpoint_contract():
    res = client.post("/v1/synastry/score", json=_pair_payload())
    assert res.status_code == 200
    body = res.json()
    # spec 03 §6 contract + backward-compatible legacy keys
    for key in ("dimensions", "top_bonds", "frictions", "score", "cross_aspects", "note"):
        assert key in body
    assert "คะแนน" in body["note"]


def test_score_venus_mars_sextile_ground_truth():
    res = client.post("/v1/synastry/score", json=_pair_payload())
    body = res.json()
    vm = [c for c in body["top_bonds"] if c["kind"] == "Venus-Mars"]
    assert vm, "Venus-Mars contact missing from top bonds"
    assert vm[0]["aspect"] == "sextile"
    assert vm[0]["orb"] < 1.0  # spec: 0.58


def test_score_venus_saturn_conjunction_ground_truth():
    chart_a = compute_chart(**M)
    chart_b = compute_chart(**MAI)
    prof = compute_synastry_profile(chart_a, chart_b)
    vs = [c for c in prof["top_bonds"]
          if c["kind"] == "Venus-Saturn" and c["aspect"] == "conjunction"]
    assert vs
    assert abs(vs[0]["orb"] - 3.44) < 0.05  # spec: 3.44


def test_score_karmic_dk_cross_check_regression():
    res = client.post("/v1/synastry/score", json=_pair_payload())
    body = res.json()
    karmic = body["karmic"]
    assert karmic["method"] == "dk_cross_check"  # no nodal contact per spec 03 §4
    assert karmic["dk_a"]["planet"] == "Sun"     # spec 02 §6 regression anchor
    assert body["dimensions"]["karmic_pull"] >= 50


def test_score_frictions_are_real_hard_aspects():
    res = client.post("/v1/synastry/score", json=_pair_payload())
    frictions = res.json()["frictions"]
    assert frictions
    assert all(c["aspect"] in ("square", "opposition") for c in frictions)
    assert any("ASC" in (c["a_point"], c["b_point"]) for c in frictions)
    assert all(0 <= c["orb"] <= 8 for c in frictions)


def test_mai_ascendant_matches_spec():
    asc = compute_chart(**MAI)["ascendant"]
    assert abs(asc["absolute_deg"] - 36.34) < 0.05  # Taurus 6.34
