"""
Tests for knowledge base loader.
"""
from src.services.kb_loader import (
    get_sign_traits, get_aspect_meanings, get_house_placements,
    get_dignity_meanings, get_transit_aspects, get_synastry_aspects,
    get_nakshatra_meanings, get_dasha_meanings, get_yoga_meanings,
    get_arabic_parts_meanings, get_ziwei_meanings, get_varshaphal_meanings,
    get_fixed_star_meanings, get_asteroid_meanings,
)


def test_sign_traits_loaded():
    data = get_sign_traits()
    assert len(data) == 120
    assert "Sun in Aries" in data
    assert "Pluto in Pisces" in data


def test_aspect_meanings_loaded():
    data = get_aspect_meanings()
    assert len(data) == 450
    assert "Sun conjunction Moon" in data


def test_house_placements_loaded():
    data = get_house_placements()
    assert len(data) == 120
    assert "Sun in House 1" in data


def test_dignity_meanings_loaded():
    data = get_dignity_meanings()
    assert len(data) == 50
    assert "Sun domicile" in data
    assert "Sun exaltation" in data


def test_transit_aspects_loaded():
    data = get_transit_aspects()
    assert len(data) == 500
    assert "transit Sun conjunction natal Moon" in data


def test_synastry_aspects_loaded():
    data = get_synastry_aspects()
    assert len(data) == 500


def test_nakshatra_meanings_loaded():
    data = get_nakshatra_meanings()
    assert len(data) == 27
    assert "Ashwini" in data


def test_dasha_meanings_loaded():
    data = get_dasha_meanings()
    assert len(data) == 9
    assert "Jupiter" in data


def test_yoga_meanings_loaded():
    data = get_yoga_meanings()
    assert len(data) == 9
    assert "Gaja Kesari" in data


def test_arabic_parts_meanings_loaded():
    data = get_arabic_parts_meanings()
    assert len(data) == 6
    assert "Part of Fortune" in data


def test_ziwei_meanings_loaded():
    data = get_ziwei_meanings()
    assert len(data) == 12
    assert "Life" in data


def test_varshaphal_meanings_loaded():
    data = get_varshaphal_meanings()
    assert len(data) == 5
    assert "muntha" in data


def test_fixed_star_meanings_loaded():
    data = get_fixed_star_meanings()
    assert len(data) == 10
    assert "Aldebaran" in data


def test_asteroid_meanings_loaded():
    data = get_asteroid_meanings()
    assert len(data) == 9
    assert "Chiron" in data
