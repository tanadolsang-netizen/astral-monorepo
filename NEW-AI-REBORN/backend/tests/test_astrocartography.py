"""Astro-cartography engine tests — relocation scoring anchors."""

from __future__ import annotations

import pytest

from src.services.astrocartography_service import (
    score_relocation, compare_cities, CITIES, _whole_sign_house,
)


def test_whole_sign_house_math() -> None:
    assert _whole_sign_house(0.0, 0.0) == 1      # same sign = 1st
    assert _whole_sign_house(29.9, 0.0) == 1
    assert _whole_sign_house(31.0, 0.0) == 2     # next sign = 2nd
    assert _whole_sign_house(355.0, 5.0) == 12   # wrap-around: -10° = 12th
    assert _whole_sign_house(25.0, 355.0) == 2   # 30° ahead = 2nd


def test_score_relocation_deterministic() -> None:
    a = score_relocation("1990-05-19T05:45", 13.75, 100.52, 7.0, city_key="tokyo")
    b = score_relocation("1990-05-19T05:45", 13.75, 100.52, 7.0, city_key="tokyo")
    assert a["score"] == b["score"]
    assert a["summary_th"] == b["summary_th"]


def test_score_bounds() -> None:
    for city in ("tokyo", "london", "newyork"):
        r = score_relocation("1997-08-18T22:32", 13.86, 100.52, 7.0, city_key=city)
        assert 5 <= r["score"] <= 98


def test_compare_cities_ranked() -> None:
    rows = compare_cities("1990-05-19T05:45", 13.75, 100.52)
    scores = [r["score"] for r in rows]
    assert scores == sorted(scores, reverse=True)
    assert len(rows) >= 10


def test_unknown_city_raises() -> None:
    with pytest.raises(ValueError):
        score_relocation("1990-05-19T05:45", 13.75, 100.52, 7.0, city_key="atlantis")


def test_custom_coordinates() -> None:
    r = score_relocation("1990-05-19T05:45", 13.75, 100.52, 7.0,
                         custom_lat=48.8566, custom_lon=2.3522)
    assert "พิกัดที่กำหนด" in r["place"]["th"] or r["place"]["en"]
