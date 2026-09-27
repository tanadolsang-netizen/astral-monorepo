"""Reel-style tarot reading — narrative layer over draw_spread()."""

from __future__ import annotations

from src.services.reel_reading import reel_reading
from src.services.tarot_meanings_th import th_card_name


def test_three_card_has_narrative_th_and_en() -> None:
    r = reel_reading("สมหญิง", spread="three_card", seed=42)
    assert set(r["narrative"].keys()) == {"th", "en"}
    assert len(r["narrative"]["th"]) > 100
    # every card (Thai name) appears in the narrative
    for c in r["cards"]:
        assert th_card_name(c["card"]) in r["narrative"]["th"]


def test_narrative_mentions_position_labels() -> None:
    r = reel_reading("อรุณ", spread="three_card", seed=7)
    for c in r["cards"]:
        assert c["position"] in r["narrative"]["th"]


def test_major_arcana_gets_story_beat() -> None:
    r = reel_reading("มาลี", spread="single", seed=999)
    # deterministic seed → same card; narrative must be longer than bare meaning
    card = r["cards"][0]
    assert th_card_name(card["card"]) in r["narrative"]["th"]
    assert len(r["narrative"]["th"]) > len(card["meaning"]) + 40


def test_deterministic_with_same_seed() -> None:
    a = reel_reading("kwan", spread="three_card", seed=123)
    b = reel_reading("kwan", spread="three_card", seed=123)
    assert a["narrative"]["th"] == b["narrative"]["th"]
    assert [c["card"] for c in a["cards"]] == [c["card"] for c in b["cards"]]


def test_celtic_cross_ten_cards() -> None:
    r = reel_reading("big", spread="celtic_cross", seed=5)
    assert len(r["cards"]) == 10
    assert r["narrative"]["th"].count("[") >= 10
