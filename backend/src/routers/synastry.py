"""Synastry endpoints: cross-aspects, composite, and scoring."""

from fastapi import APIRouter, HTTPException
from src.models.chart import ChartRequest
from src.services.chart_service import compute_chart, compute_dual_chart
from src.services.aspects import compute_cross_aspects
from src.services.caveat import CAVEAT
from src.services.element_service import compute_element_balance
from src.services.composite_service import compute_composite, compute_relationship_score
from src.services.synastry_scoring import compute_synastry_profile

router = APIRouter()


@router.post("/cross-aspects")
async def cross_aspects(a: ChartRequest, b: ChartRequest):
    try:
        chart_a = compute_chart(**{k: v for k, v in a.model_dump().items() if k not in ("system", "dual")})
        chart_b = compute_chart(**{k: v for k, v in b.model_dump().items() if k not in ("system", "dual")})
        return {
            "a": chart_a,
            "b": chart_b,
            "cross_aspects": compute_cross_aspects(chart_a, chart_b),
            "elements_a": compute_element_balance(chart_a),
            "elements_b": compute_element_balance(chart_b),
            "caveat": CAVEAT,
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Computation failed: {exc}") from exc


@router.post("/cross-aspects-dual")
async def cross_aspects_dual(a: ChartRequest, b: ChartRequest):
    try:
        dual_a = compute_dual_chart(**{k: v for k, v in a.model_dump().items() if k not in ("system", "dual")})
        dual_b = compute_dual_chart(**{k: v for k, v in b.model_dump().items() if k not in ("system", "dual")})
        return {
            "a_tropical": dual_a["tropical"],
            "a_sidereal": dual_a["sidereal"],
            "b_tropical": dual_b["tropical"],
            "b_sidereal": dual_b["sidereal"],
            "cross_aspects_tropical": compute_cross_aspects(dual_a["tropical"], dual_b["tropical"]),
            "cross_aspects_sidereal": compute_cross_aspects(dual_a["sidereal"], dual_b["sidereal"]),
            "elements_a_tropical": compute_element_balance(dual_a["tropical"]),
            "elements_a_sidereal": compute_element_balance(dual_a["sidereal"]),
            "elements_b_tropical": compute_element_balance(dual_b["tropical"]),
            "elements_b_sidereal": compute_element_balance(dual_b["sidereal"]),
            "caveat": CAVEAT,
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Computation failed: {exc}") from exc


@router.post("/composite")
async def composite(a: ChartRequest, b: ChartRequest):
    try:
        chart_a = compute_chart(**{k: v for k, v in a.model_dump().items() if k not in ("system", "dual")})
        chart_b = compute_chart(**{k: v for k, v in b.model_dump().items() if k not in ("system", "dual")})
        comp = compute_composite(chart_a, chart_b)
        return {
            "a": chart_a,
            "b": chart_b,
            "composite": comp,
            "caveat": CAVEAT,
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Computation failed: {exc}") from exc


@router.post("/score")
async def score(a: ChartRequest, b: ChartRequest):
    try:
        chart_a = compute_chart(**{k: v for k, v in a.model_dump().items() if k not in ("system", "dual")})
        chart_b = compute_chart(**{k: v for k, v in b.model_dump().items() if k not in ("system", "dual")})
        # Spec 03 profile (6 dimensions + bonds/frictions) merged into the legacy
        # response shape: score/cross_aspects/elements/note stay for compatibility.
        legacy = compute_relationship_score(chart_a, chart_b)
        profile = compute_synastry_profile(chart_a, chart_b)
        return {
            **legacy,
            "dimensions": profile["dimensions"],
            "overall": profile["overall"],
            "top_bonds": profile["top_bonds"],
            "frictions": profile["frictions"],
            "karmic": profile["karmic"],
            "house_overlay": profile["house_overlay"],
            "weights_version": profile["weights_version"],
            "note": profile["note"],
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Computation failed: {exc}") from exc
