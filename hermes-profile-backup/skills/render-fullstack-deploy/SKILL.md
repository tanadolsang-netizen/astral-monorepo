---
name: render-fullstack-deploy
description: Deploy full-stack app to Render (backend serves frontend).
version: 1.0.0
platforms: [windows, linux, macos]
tags: [render, deployment, fullstack, docker, fastapi, react, vite]
---

# Render Full-Stack Deploy

Deploy a Python backend + React/Vite frontend to Render.com as a single service
where the backend serves the frontend static files at `/`.

## Architecture (Current: API-Only Mode)

As of 2026-09-06 commit `2755f45`, the Dockerfile runs API-only (no frontend build in container):

```
Browser → https://astral-v2fo.onrender.com/
         ↓
    FastAPI (uvicorn) on port 10000
    ├── /ready          → health check (200 + JSON)
    ├── /v1/*           → API routes (natal, transit, synastry, chat, etc.)
    ├── /docs           → Swagger UI
    └── /               → API info JSON (not HTML)
```

**Note:** Earlier versions served frontend from backend (single-service mode). Current mode is backend-only. Frontend is deployed separately or not at all in this configuration.

## Why Single Service

- Render API cannot create `web_service` without payment info (workaround: use Dashboard or existing payment method)
- Single Docker service avoids CORS, simplifies deploy
- Vercel has 100MB file limit — Render does not

## render.yaml

```yaml
services:
  - type: web
    name: astral
    runtime: docker
    plan: free
    region: singapore
    branch: main
    dockerfilePath: ./Dockerfile
    healthCheckPath: /ready
    envVars:
      - key: PYTHONPATH
        value: /app/backend
      - key: PORT
        value: 10000
```

## main.py — Serve Frontend

```python
import pathlib
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

_CLIENT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "landing" / "astral-app" / "dist"

if _CLIENT_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=str(_CLIENT_DIR / "assets")), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_root():
        return FileResponse(str(_CLIENT_DIR / "index.html"))

    @app.get("/{path:path}", include_in_schema=False)
    async def serve_spa(path: str):
        file_path = _CLIENT_DIR / path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(_CLIENT_DIR / "index.html"))
```

## Key Gotchas

1. Render API + web_service = payment required (use Dashboard or existing payment method on file)
2. `npm ci` fails on Render — use `npm install`
3. Add `node_modules/` and `.venv/` to `.gitignore` (avoid 1.7GB upload)
4. ComfyUI SDXL: templates lack VAE. Build JSON: CheckpointLoaderSimple → KSampler → VAEDecode → SaveImage
5. **Windows CLI auth:** `render login` needs browser — use `RENDER_API_KEY` env var with REST API directly
6. **Service recreation:** Old service IDs can disappear from the account. Verify with `curl` + API key before assuming a service exists.

## Verification

- [ ] `python -c "from src.main import app"` imports cleanly
- [ ] `curl https://<url>/ready` returns HTTP 200 + JSON {"status":"ok"}
- [ ] `curl https://<url>/` returns API info JSON
- [ ] `curl https://<url>/docs` returns HTTP 200
