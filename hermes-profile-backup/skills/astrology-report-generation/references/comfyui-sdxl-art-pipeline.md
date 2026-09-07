# ComfyUI + SDXL Art Pipeline — Concrete Recipes (2026-08-30)

Box: RTX 5060 8GB (Blackwell), Windows 11, ComfyUI 0.34.0, torch 2.11 +cu128,
Python venv. Goal: draw premium tarot + cover art for the Thai astrology PDF.

## 1. Stable launch (auto-restart watchdog)
```python
# comfy_launch_stable.py — run as detached background; restarts if server dies
import subprocess, time, urllib.request
COMFY = r"C:\Users\ADMIN\Documents\comfy\ComfyUI"
while True:
    try:
        urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=3)
    except Exception:
        subprocess.Popen(
            [COMFY + r"\.venv\Scripts\python.exe", "main.py",
             "--listen", "127.0.0.1", "--port", "8188", "--lowvram",
             "--preview-method", "none"],
            cwd=COMFY)
    time.sleep(15)
```
Launch: `uv run python scripts/comfy_launch_stable.py &` (background, detached).
Health: `curl http://127.0.0.1:8188/system_stats`.

## 2. img2img from Rider-Waite reference (the ONLY reliable way for tarot)
- Reference URLs (via Wikimedia Commons API — hash-guessing 404s):
  - Devil: `https://upload.wikimedia.org/wikipedia/commons/5/55/RWS_Tarot_15_Devil.jpg`
  - Six of Pentacles: `https://upload.wikimedia.org/wikipedia/commons/a/a6/Pents06.jpg`
  - Knight of Pentacles: `https://upload.wikimedia.org/wikipedia/commons/d/d5/Pents12.jpg`
- Workflow `comfy_sdxl_img2img.json`: LoadImage(node 10) -> VAEEncode ->
  KSampler(denoise 0.55) -> VAEDecode -> SaveImage. Inject prompt at node 6,
  negative at node 7, seed at node 4, image filename at node 10.
- Python REST pattern: upload ref via `POST /upload/image` (multipart),
  queue via `POST /api/prompt`, poll `GET /api/history/{pid}`, download via
  `GET /api/view?filename=...`. Prompts live in `scripts/comfy_prompts.txt`.

## 3. Remove English text SDXL injects (PIL crop)
```python
from PIL import Image
img = Image.open("card_knight_pentacles_final.png")
w, h = img.size
img.crop((0, 0, w, int(h*0.84))).save("card_knight_pentacles_final.png")  # drop bottom 16%
```
Devil: drop bottom 14%. Then assert zero Latin in the final PDF.

## 4. Render in Chromium (NOT base64)
```python
# build_combined_premium.py (Playwright)
import shutil
art_dir = html_path.parent / "_preview_art"
art_dir.mkdir(exist_ok=True)
shutil.copy(COVER_IMG, art_dir / "cover.png")
# ... in HTML: <img src="_preview_art/cover.png">
await page.goto(html_path.as_uri(), wait_until="load")
await page.wait_for_timeout(3000)
await page.pdf(path=OUT, format="A4", print_background=True)
```

## 5. Thai-only gate (pymupdf, not vision)
```python
import fitz, re
doc = fitz.open(pdf_path)
txt = "".join(p.get_text() for p in doc)
lat = re.findall(r"[A-Za-z]+", txt)
assert not lat, f"LATIN WORDS: {lat}"   # must be empty
```
vision_analyze MISREADS Thai (saw "รดianteng" for "ผสาน"); use pymupdf for truth.
