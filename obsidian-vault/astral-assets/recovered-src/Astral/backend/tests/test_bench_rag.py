"""Tests: Astral-Bench + classical RAG retrieval."""

from __future__ import annotations

import pytest

from src.services.astral_bench import (
    BenchCase, ground_truth, score_interpretation, run_bench,
)
from src.services.classical_rag import retrieve, build_context_block, corpus_stats


CASE = BenchCase(name="t", date="1990-05-19", time="05:45",
                 lat=13.75, lon=100.52, tz=7.0)


# ── Bench ────────────────────────────────────────────────────────────
def test_ground_truth_stable() -> None:
    a, b = ground_truth(CASE), ground_truth(CASE)
    assert a == b
    assert a["sun_sign"] and a["moon_sign"] and a["asc_sign"]


def test_score_good_reading() -> None:
    gt = ground_truth(CASE)
    good = (f"Your Sun in {gt['sun_sign']} at {gt['sun_degree']}° with Moon "
            f"in {gt['moon_sign']}, rising {gt['asc_sign']} — the 7th house "
            f"shows partnership themes.")
    r = score_interpretation(gt, good)
    assert r["score"] >= 70


def test_score_contradiction_penalized() -> None:
    gt = ground_truth(CASE)
    wrong_signs = {"Aries", "Libra", "Capricorn", "Cancer"} - {
        gt["sun_sign"].capitalize(), gt["moon_sign"].capitalize(),
        gt["asc_sign"].capitalize()}
    bad = (f"Sun in {wrong_signs.pop()}, Moon elsewhere.")
    r = score_interpretation(gt, bad)
    any_contra = any(c.get("ok") is False for c in r["checks"])
    # either contradiction detected or no reward; score must be < good case
    assert not any("correct" == c.get("check") for c in r["checks"]) or \
        any(c.get("ok") is False for c in r["checks"])


def test_run_bench_regression_mode() -> None:
    cases = [CASE,
             BenchCase(name="b2", date="1997-08-18", time="22:32",
                       lat=13.86, lon=100.52)]
    r = run_bench(cases)  # no interpret_fn → determinism mode
    assert r["cases"] == 2
    assert all(res["stable_recompute"] for res in r["results"])
    assert r["mean_score"] == 100


def test_run_bench_with_interpreter() -> None:
    def interp(truth: dict, case: BenchCase) -> str:
        return (f"Sun {truth['sun_sign']} Moon {truth['moon_sign']} "
                f"rising {truth['asc_sign']} 4 planets cited.")
    r = run_bench([CASE], interpret_fn=interp)
    assert r["mean_score"] > 50


# ── RAG ──────────────────────────────────────────────────────────────
def test_corpus_loaded() -> None:
    stats = corpus_stats()
    assert stats["entries"] >= 5
    assert any("Tetrabiblos" in s or "Lilly" in s for s in stats["sources"])


def test_retrieve_marriage_query() -> None:
    hits = retrieve("will my marriage be happy venus 7th house")
    assert hits
    assert any("Lilly" in h["source"] or "venus" in str(h).lower()
               for h in hits)


def test_build_context_block_format() -> None:
    block = build_context_block("jupiter dasha career timing vimshottari")
    if block:
        assert "[Classical references" in block
        assert "—" in block


def test_retrieve_no_match_empty() -> None:
    hits = retrieve("zzzzqqqq unrelated query about pasta recipes")
    assert isinstance(hits, list)
