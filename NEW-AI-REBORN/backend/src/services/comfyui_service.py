"""ComfyUI client service — queue prompts, poll for results, return image paths."""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import Any

import httpx

logger = logging.getLogger("astral.comfyui")

COMFYUI_URL = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")
COMFYUI_OUTPUT_DIR = Path(os.getenv("COMFYUI_OUTPUT_DIR", r"C:/Users/ADMIN/Documents/comfy/ComfyUI/output"))
POLL_INTERVAL = float(os.getenv("COMFYUI_POLL_INTERVAL", "2.0"))
MAX_WAIT = int(os.getenv("COMFYUI_MAX_WAIT", "300"))  # 5 minutes max

# In-memory job store (use Redis/DB in production)
_jobs: dict[str, dict[str, Any]] = {}
_jobs_lock = Lock()


def _new_job_id() -> str:
    return f"job_{uuid.uuid4().hex[:12]}"


def get_job(job_id: str) -> dict[str, Any] | None:
    with _jobs_lock:
        return _jobs.get(job_id)


def list_jobs() -> list[dict[str, Any]]:
    with _jobs_lock:
        return list(_jobs.values())


def _set_status(job_id: str, status: str, **extra: Any) -> None:
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id]["status"] = status
            _jobs[job_id]["updated_at"] = time.time()
            _jobs[job_id].update(extra)


def queue_prompt(
    prompt: dict[str, Any],
    workflow: dict[str, Any] | None = None,
    width: int = 1024,
    height: int = 1536,
    steps: int = 30,
    cfg: float = 7.5,
    sampler: str = "dpmpp_2m",
    scheduler: str = "karras",
    seed: int | None = None,
    negative_prompt: str = "",
) -> str:
    """Queue a txt2img job in ComfyUI. Returns job_id for polling."""
    job_id = _new_job_id()

    with _jobs_lock:
        _jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "created_at": time.time(),
            "updated_at": time.time(),
            "image_url": None,
            "error": None,
        }

    # Build the workflow JSON
    wf = workflow or _default_txt2img_workflow(
        prompt=prompt,
        width=width,
        height=height,
        steps=steps,
        cfg=cfg,
        sampler=sampler,
        scheduler=scheduler,
        seed=seed or int(time.time() * 1000) % 2**32,
        negative_prompt=negative_prompt,
    )

    try:
        resp = httpx.post(f"{COMFYUI_URL}/prompt", json={"prompt": wf}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        prompt_id = data.get("prompt_id", "")
        _set_status(job_id, "running", prompt_id=prompt_id)
        logger.info("ComfyUI job %s queued (prompt_id=%s)", job_id, prompt_id)
    except Exception as e:
        _set_status(job_id, "failed", error=str(e))
        logger.error("ComfyUI queue failed for %s: %s", job_id, e)

    return job_id


def poll_job(job_id: str) -> dict[str, Any]:
    """Check job status. Returns current job dict."""
    job = get_job(job_id)
    if not job:
        return {"error": "Job not found"}

    if job["status"] in ("completed", "failed"):
        return job

    # Check if ComfyUI has output for this job
    if job.get("status") == "running":
        # Look for new files in output directory
        image = _find_latest_output(job["created_at"])
        if image:
            rel_path = image.relative_to(COMFYUI_OUTPUT_DIR)
            image_url = f"/comfyui-output/{rel_path}"
            _set_status(job_id, "completed", image_url=str(image_url))
            logger.info("ComfyUI job %s completed: %s", job_id, image_url)

    return get_job(job_id) or {"error": "Job not found"}


def _find_latest_output(since: float) -> Path | None:
    """Find the most recent output file created after `since`."""
    if not COMFYUI_OUTPUT_DIR.exists():
        return None

    latest: Path | None = None
    latest_mtime: float = 0

    for f in COMFYUI_OUTPUT_DIR.iterdir():
        if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
            mtime = f.stat().st_mtime
            if mtime > since and mtime > latest_mtime:
                latest = f
                latest_mtime = mtime

    return latest


def _default_txt2img_workflow(
    prompt: str,
    width: int,
    height: int,
    steps: int,
    cfg: float,
    sampler: str,
    scheduler: str,
    seed: int,
    negative_prompt: str,
) -> dict[str, Any]:
    """Build a simple SDXL txt2img workflow."""
    return {
        "3": {
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": sampler,
                "scheduler": scheduler,
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
            "class_type": "KSampler",
        },
        "4": {
            "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"},
            "class_type": "CheckpointLoaderSimple",
        },
        "5": {
            "inputs": {"width": width, "height": height, "batch_size": 1},
            "class_type": "EmptyLatentImage",
        },
        "6": {
            "inputs": {"text": prompt, "clip": ["4", 1]},
            "class_type": "CLIPTextEncode",
        },
        "7": {
            "inputs": {"text": negative_prompt, "clip": ["4", 1]},
            "class_type": "CLIPTextEncode",
        },
        "8": {
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
            "class_type": "VAEDecode",
        },
        "9": {
            "inputs": {
                "filename_prefix": "astral",
                "images": ["8", 0],
            },
            "class_type": "SaveImage",
        },
    }
