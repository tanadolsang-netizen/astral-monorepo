"""Generate premium AI art for the astrology+tarot PDF via local ComfyUI (SDXL).

Self-driving: pass a list of (key, prompt, neg) and it submits each to the
ComfyUI /prompt API, waits for completion, then copies the latest output image
into assets/ai-art/<key>_final.png. Only generates what is missing unless
--force is given.

Usage:
    PYTHONPATH=. uv run python scripts/gen_ai_art.py \
        --key world --prompt "..." --neg "..." \
        --key star  --prompt "..." --neg "..."
"""
from __future__ import annotations

import argparse
import io
import json
import shutil
import sys
import time
import urllib.request
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[1]
ART_DIR = REPO / "assets" / "ai-art"
COMFY_OUT = Path.home() / "Documents" / "comfy" / "ComfyUI" / "output"
COMFY_URL = "http://127.0.0.1:8188"

# Standard SDXL txt2img workflow (API format). Node 6 = positive CLIP,
# 7 = negative CLIP, 4 = KSampler, 9 = SaveImage (filename_prefix "astral").
WORKFLOW = {
    "3": {"class_type": "CheckpointLoaderSimple",
          "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
    "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["3", 1]}},
    "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["3", 1]}},
    "4": {"class_type": "KSampler", "inputs": {
        "seed": 0, "steps": 32, "cfg": 7.0, "sampler_name": "dpmpp_2m",
        "scheduler": "karras", "denoise": 1.0,
        "model": ["3", 0], "positive": ["6", 0], "negative": ["7", 0],
        "latent_image": ["5", 0]}},
    "5": {"class_type": "EmptyLatentImage",
          "inputs": {"width": 832, "height": 1216, "batch_size": 1}},
    "8": {"class_type": "VAEDecode", "inputs": {"samples": ["4", 0], "vae": ["3", 2]}},
    "9": {"class_type": "SaveImage",
          "inputs": {"filename_prefix": "astral", "images": ["8", 0]}},
}


def _post(endpoint: str, payload: dict, timeout: int = 600) -> dict:
    r = requests.post(f"{COMFY_URL}/{endpoint}", json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()


def queue_prompt(workflow: dict) -> str:
    """Submit workflow, return prompt_id."""
    data = _post("prompt", {"prompt": workflow, "client_id": "astral-builder"})
    return data["prompt_id"]


def wait_for(prompt_id: str, timeout: int = 540) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            hist = requests.get(f"{COMFY_URL}/history/{prompt_id}", timeout=10).json()
            if prompt_id in hist:
                return True
        except Exception:
            pass
        time.sleep(3)
    return False


def latest_output(prefix: str = "astral") -> Path | None:
    files = sorted(COMFY_OUT.glob(f"{prefix}*.png"), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def generate(key: str, prompt: str, neg: str, seed: int, force: bool = False) -> Path:
    out = ART_DIR / f"{key}_final.png"
    if out.exists() and not force:
        print(f"  [skip] {key} exists")
        return out
    wf = json.loads(json.dumps(WORKFLOW))  # deep copy
    wf["6"]["inputs"]["text"] = prompt
    wf["7"]["inputs"]["text"] = neg
    wf["4"]["inputs"]["seed"] = seed
    before = {p.name for p in COMFY_OUT.glob("astral*.png")}
    pid = queue_prompt(wf)
    print(f"  [gen ] {key} (prompt {pid})")
    if not wait_for(pid):
        raise TimeoutError(f"ComfyUI did not finish {key} in time")
    # find the newest file not present before
    after = sorted(COMFY_OUT.glob("astral*.png"), key=lambda p: p.stat().st_mtime)
    new = [p for p in after if p.name not in before] or after[-1:]
    src = new[-1]
    shutil.copy(src, out)
    print(f"  [done] {key} -> {out.name} ({out.stat().st_size//1024} KB)")
    return out


# Default prompts for the cards the builder needs (Thai-readable names mapped).
PROMPTS = {
    "world": (
        "Traditional Tarot card 'The World': a serene dancing figure inside a large "
        "wreath circle, four living creatures (angel, eagle, bull, lion) in the corners "
        "holding the four elements, ornate gilded card border, dark indigo and gold "
        "mystical palette, classical fine-art oil painting, sharp focus, hyperdetailed, "
        "symmetric, ethereal completion and wholeness",
        "malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
        "cartoon, minimal, CGI, blurry, text, letters, watermark"),
    "star": (
        "Traditional Tarot card 'The Star': a naked woman kneeling by a pool, pouring "
        "water from two jugs onto land and water, a large eight-pointed star above with "
        "seven smaller stars, calm night sky, ornate gilded card border, dark indigo and "
        "gold mystical palette, classical fine-art oil painting, sharp focus, "
        "hyperdetailed, symmetric, hope and serenity",
        "malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
        "cartoon, minimal, CGI, blurry, text, letters, watermark"),
    "the_empress": (
        "Traditional Tarot card 'The Empress': a serene crowned goddess seated on a "
        "throne in a lush flowering garden, holding a scepter and a heart-shaped shield "
        "with the Venus symbol, ripe wheat and abundant nature around her, ornate gilded "
        "card border, dark indigo and gold mystical palette, classical fine-art oil "
        "painting, sharp focus, hyperdetailed, symmetric, abundant fertility and love",
        "malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
        "cartoon, minimal, CGI, blurry, text, letters, watermark"),
    "king_cups": (
        "Traditional Tarot card 'King of Cups': a dignified bearded king seated on a "
        "throne at the edge of a calm sea, holding a golden cup in one hand and a scepter "
        "in the other, gentle waves behind, ornate gilded card border, dark indigo and "
        "gold mystical palette, classical fine-art oil painting, sharp focus, "
        "hyperdetailed, symmetric, emotional mastery and tenderness",
        "malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
        "cartoon, minimal, CGI, blurry, text, letters, watermark"),
    "ace_cups": (
        "Traditional Tarot card 'Ace of Cups': a single ornate golden chalice overflowing "
        "with sacred water, a white dove above offering a host, five streams of water "
        "pouring into a pool, a hand emerging from a luminous cloud, ornate gilded card "
        "border, dark indigo and gold mystical palette, classical fine-art oil painting, "
        "sharp focus, hyperdetailed, symmetric, new love and open emotion",
        "malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
        "cartoon, minimal, CGI, blurry, text, letters, watermark"),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", action="append", default=[])
    ap.add_argument("--prompt", action="append", default=[])
    ap.add_argument("--neg", action="append", default=[])
    ap.add_argument("--seed", type=int, default=19970519)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--all", action="store_true", help="generate all default prompts")
    args = ap.parse_args()

    ART_DIR.mkdir(parents=True, exist_ok=True)
    jobs = []
    if args.all:
        for k, (p, n) in PROMPTS.items():
            jobs.append((k, p, n))
    for i, k in enumerate(args.key):
        p = args.prompt[i] if i < len(args.prompt) else PROMPTS.get(k, ("", ""))[0]
        n = args.neg[i] if i < len(args.neg) else PROMPTS.get(k, ("", ""))[1]
        if not p:
            print(f"no prompt for {k}", file=sys.stderr)
            continue
        jobs.append((k, p, n))

    if not jobs:
        print("nothing to do (pass --key/--prompt or --all)", file=sys.stderr)
        return 2

    # quick health check
    try:
        requests.get(f"{COMFY_URL}/system_stats", timeout=5).raise_for_status()
    except Exception as e:
        print(f"ComfyUI not reachable: {e}", file=sys.stderr)
        return 1

    for k, p, n in jobs:
        generate(k, p, n, seed=args.seed, force=args.force)
    print("ALL DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
