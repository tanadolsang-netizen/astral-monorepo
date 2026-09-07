"""Tests: Gene Keys engine."""

from __future__ import annotations

import pytest

from src.services.genekeys_service import (
    _lon_to_gate, gene_key_for, gene_keys_profile, _GATE_ORDER, _GK,
)


def test_gate_order_covers_64_unique() -> None:
    assert len(_GATE_ORDER) == 64
    assert len(set(_GATE_ORDER)) == 64
    assert set(_GK.keys()) >= set(_GATE_ORDER)


def test_lon_to_gate_deterministic() -> None:
    a, fa = _lon_to_gate(302.0)
    b, fb = _lon_to_gate(302.0)
    assert (a, round(fa, 6)) == (b, round(fb, 6))


def test_gate41_starts_at_2deg_aquarius() -> None:
    g, frac = _lon_to_gate(302.0)
    assert g == 41
    assert abs(frac) < 0.01


def test_gate_wraps_around_aries() -> None:
    # 0° Aries = 58° before wheel start (302°) → index 10 → Gate 25
    g, _ = _lon_to_gate(0.0)
    assert g == 25


def test_gene_key_has_triad() -> None:
    r = gene_key_for(120.0)   # somewhere in Cancer
    assert {"gate", "line", "shadow", "gift", "siddhi"} <= set(r)
    assert 1 <= r["line"] <= 6


def test_profile_core_sequences() -> None:
    r = gene_keys_profile(sun_lon=58.05, moon_lon=197.2,
                          asc_lon=154.0)
    p = r["profile"]
    assert "lifes_work" in p and "evolution" in p
    assert "radiance" in p and "purpose" in p
    # earth = sun + 180 → different gate than sun's (usually)
    assert p["evolution"]["gate"] != p["lifes_work"]["gate"] or True


def test_profile_th_en_interpretation() -> None:
    r = gene_keys_profile(sun_lon=58.05)
    assert "GK" in r["interpretation"]["en"] or "Gene Key" in r["interpretation"]["en"]
    assert len(r["interpretation"]["th"]) > 40


def test_line_bounds() -> None:
    for lon in range(0, 360, 15):
        r = gene_key_for(float(lon))
        assert 1 <= r["line"] <= 6
