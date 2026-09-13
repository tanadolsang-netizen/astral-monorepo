"""ComfyUI generation endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.services.comfyui_prompt_builder import build_prompt_from_chart, get_negative_prompt
from src.services.comfyui_service import queue_prompt, poll_job, get_job
from src.services.chart_service import compute_chart, ChartValidationError

router = APIRouter()


class CosmicArtRequest(BaseModel):
    name: str = "Anonymous"
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    lat: float
    lon: float
    tz_offset_hours: float = 7.0
    system: str = "tropical"
    seed: Optional[int] = None


@router.post("/generate")
async def generate_cosmic_art(req: CosmicArtRequest):
    """Submit birth chart → compute → generate cosmic artwork via ComfyUI."""
    try:
        chart = compute_chart(
            name=req.name,
            date=req.date,
            time=req.time,
            tz_offset_hours=req.tz_offset_hours,
            lat=req.lat,
            lon=req.lon,
            system=req.system,
        )
    except ChartValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart computation failed: {e}") from e

    # Build cosmic prompt from chart data
    prompt = build_prompt_from_chart(chart)
    negative_prompt = get_negative_prompt()

    # Queue in ComfyUI (1024x1536 = portrait, tarot-card friendly)
    job_id = queue_prompt(
        prompt=prompt,
        width=1024,
        height=1536,
        steps=30,
        cfg=7.5,
        seed=req.seed,
        negative_prompt=negative_prompt,
    )

    return {
        "job_id": job_id,
        "prompt": prompt,
        "chart_summary": {
            "ascendant": chart.get("ascendant", {}).get("sign"),
            "sun": chart.get("sun", {}).get("sign"),
            "moon": chart.get("moon", {}).get("sign"),
        },
    }


@router.get("/status/{job_id}")
async def check_status(job_id: str):
    """Poll job status."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Try to poll for updates
    if job.get("status") == "running":
        job = poll_job(job_id)

    return job


@router.get("/health")
async def comfyui_health():
    """Check if ComfyUI server is reachable."""
    import httpx
    try:
        resp = httpx.get("http://127.0.0.1:8188/system_stats", timeout=5)
        resp.raise_for_status()
        return {"status": "online", "server": "127.0.0.1:8188"}
    except Exception as e:
        return {"status": "offline", "error": str(e)}
