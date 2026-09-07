---
name: fullstack-hosting
description: "Deploy full-stack web apps to Render.com or Vercel."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [deployment, hosting, render, vercel, fullstack, frontend, backend]
    related_skills: [docker-ai-workspace, systematic-debugging]
---

# Full-Stack Hosting

## Overview

Deploy full-stack web applications (backend API + frontend SPA) to cloud platforms. Primary focus: Render.com for unified backend+frontend hosting.

## When to Use

- User asks to deploy frontend, backend, or full-stack app
- Need to choose between hosting platforms (Render vs Vercel vs others)
- Configuring render.yaml or vercel.json
- Debugging deployment failures

## Platform Selection

### Render.com (Preferred for full-stack)

**Pros:** Single platform for backend (Docker/Python/Node) + frontend (static), free tier, auto-deploy from Git, SPA routing support.

**Cons:** Free tier spins down after 15min inactivity (cold start ~30s).

**Configuration:** `render.yaml` at repo root defines services.

### Vercel (Frontend-only)

**Pros:** Excellent CDN, instant global edge, great DX.

**Cons:** 100MB file upload limit (CLI), no native backend (serverless functions only), production deploys can lag behind Git.

**Use when:** Frontend-only, or team already has Vercel.

### Decision Matrix

| Need | Choice |
|------|--------|
| Backend + Frontend, unified | Render |
| Frontend only, max performance | Vercel |
| Python/FastAPI backend | Render (Docker) |
| Serverless functions | Vercel |

## Render.com Configuration

### render.yaml Structure

```yaml
services:
  # Backend: Docker-based Python/FastAPI
  - type: web
    name: my-backend
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

  # Frontend: Static site (React/Vite)
  - type: static
    name: my-frontend
    branch: main
    rootDir: .
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: ./frontend/dist
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
    envVars:
      - key: NODE_VERSION
        value: 18
```

### Key Fields

- `healthCheckPath`: Backend health endpoint (e.g., `/ready`)
- `staticPublishPath`: Where built frontend files live
- `routes`: SPA routing — rewrite all paths to `/index.html`
- `rootDir`: Relative to repo root (use `.` for repo root)

### Triggering Deploys

1. **Auto-deploy:** Push to `main` branch (if enabled in dashboard)
2. **Manual:** Render Dashboard → Service → Deploy Latest Commit
3. **API:** `POST https://api.render.com/v1/services/{service_id}/deploy` with `Authorization: Bearer {token}`

### Environment Variables

- `sync: false` — value set manually in dashboard (secrets)
- `value: ...` — hardcoded value
- Use dashboard for sensitive keys (API keys, DB passwords)

## Vercel Configuration (if needed)

### vercel.json

```json
{
  "framework": "vite",
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

### .vercelignore

Critical for large repos — exclude:
- `.git/`, `backend/`, `tests/`, `docs/`
- `.venv/`, `node_modules/` (top-level only)
- `*.md`, `Dockerfile`, `docker-compose*.yml`
- **Keep:** `frontend/` (or `landing/astral-app/`) with `package.json`, `src/`, `public/`

### Vercel CLI Deploy

```bash
# Link project
vercel link --project <project_id> --yes

# Build locally
vercel build

# Deploy prebuilt (avoids 100MB upload limit)
vercel deploy --prebuilt --prod

# Promote preview to production
vercel promote <preview-url>
```

**Gotcha:** `vercel deploy` without `--prebuilt` uploads entire repo — fails if >100MB. Always use `vercel build` + `vercel deploy --prebuilt` for large repos.

## Debugging Deployments

### Checklist

1. **Build passes locally:** `npm run build` in frontend dir
2. **Correct commit deployed:** Check deployment commit hash vs `git log`
3. **Assets return 200:** `curl -I <url>/assets/index-*.js`
4. **SPA routing works:** Deep links (e.g., `/natal`) return `index.html`
5. **Backend health:** `curl <backend-url>/ready` returns 200

### Common Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| 404 on assets | Wrong `staticPublishPath` or `outputDirectory` | Verify path matches build output |
| Blank page, no render | SPA routing missing | Add rewrite route |
| Stale content | Old build cached | Redeploy, check commit hash |
| 100MB limit (Vercel) | Repo too large for CLI upload | Use `--prebuilt` or `.vercelignore` |
| Build fails on platform | Missing env var or wrong Node version | Check `NODE_VERSION` env var |

### Verifying Production

```bash
# Check which JS bundle is served
curl -s <url>/ | grep -oE 'index-[A-Za-z0-9_]+\.js'

# Verify that bundle has latest code
curl -s <url>/assets/index-*.js | grep -c 'expected_function'

# Check backend health
curl -s <backend-url>/ready
```

## Lessons Learned (Astral Project, 2026-09)

### User Preference

- **Use Render.com only — no Vercel.** User explicitly requested dropping Vercel and keeping everything on Render.com. This avoids dual-platform complexity and the 100MB CLI upload limit.

### Render.com Specifics

1. **Render static site rootDir:** For monorepo frontend (e.g., `landing/astral-app/`), set `rootDir: landing/astral-app` in render.yaml. Using `rootDir: .` with a `cd` in buildCommand creates a new service that doesn't match the dashboard-created one.
2. **npm ci vs npm install:** On Windows, `npm ci` fails with EPERM when `esbuild.exe` is held by another process (Vite dev server, antivirus). Use `npm install` in buildCommand as a robust alternative.
3. **Dashboard vs render.yaml services:** Services created through Render Dashboard don't auto-update from render.yaml on existing services. Either:
   - Delete the dashboard service and let render.yaml recreate it, OR
   - Manually update settings in Dashboard → Service Settings
4. **Render auto-deploy:** Push to `main` triggers auto-deploy if enabled. Verify new JS bundle hash after deploy: `curl -s <url>/ | grep -oE 'index-[A-Za-z0-9_]+\.js'`
5. **Publish directory path:** When `rootDir: landing/astral-app`, use `staticPublishPath: ./dist` (relative to rootDir). Render resolves this to `landing/astral-app/dist`. Using absolute-looking paths like `landing/astral-app/dist` in `staticPublishPath` causes 404s because Render looks for `landing/astral-app/landing/astral-app/dist`.

### Render CLI on Windows

**Install:** Download from GitHub releases (Homebrew is macOS only).
```bash
curl -L -o "$LOCALAPPDATA/Temp/render.zip" https://github.com/render-oss/cli/releases/download/v2.11.0/cli_2.11.0_windows_amd64.zip
unzip -o "$LOCALAPPDATA/Temp/render.zip" -d "$LOCALAPPDATA/hermes/bin/"
mv "$LOCALAPPDATA/hermes/bin/cli_v2.11.0.exe" "$LOCALAPPDATA/hermes/bin/render.exe"
render --version
```

**Auth limitation on Windows:** `render login` requires browser interaction and often fails in headless/agent contexts. Use `RENDER_API_KEY` env var with the REST API directly instead of the CLI for automated workflows.

**CLI env var:** Prefix commands with `RENDER_API_KEY=xxx` — the CLI reads it automatically.

### Render.com API (Programmatic Deploy)

The Render REST API enables creating and triggering deploys without the dashboard. Preferred on Windows where CLI auth is unreliable.

**Auth:** `Authorization: Bearer <token>` (from Render Dashboard → Account Settings → API Keys)

**List owners (to get ownerId):**
```
GET https://api.render.com/v1/owners
```

**Create web_service (Docker):**
```
POST https://api.render.com/v1/services
{
  "ownerId": "tea-xxxxxxxxxxxx",
  "type": "web_service",
  "name": "astral",
  "repo": "https://github.com/<user>/<repo>",
  "branch": "main",
  "env": "docker",
  "serviceDetails": {
    "env": "docker",
    "plan": "free",
    "region": "singapore",
    "dockerfilePath": "./Dockerfile",
    "healthCheckPath": "/ready",
    "envVars": [
      {"key": "PYTHONPATH", "value": "/app/backend"},
      {"key": "PORT", "value": "10000"}
    ]
  }
}
```

**Important API details:**
- `type` must be `web_service` (not `web`) — valid types: `static_site, web_service, private_service, background_worker, cron_job, workflow`
- `repo` must be full URL: `https://github.com/user/repo` (not `user/repo`)
- `ownerId` is required (get from `/v1/owners`)
- Docker services require `serviceDetails.env: "docker"`
- Env vars in `serviceDetails.envVars` may not propagate fully on creation — verify in Dashboard after creation and add missing keys (e.g., `OPENROUTER_API_KEY`, `HERMES_MEMORY_ROOT`) via Dashboard or API patch

**Create static site:**
```
POST https://api.render.com/v1/services
{
  "type": "static_site",
  "name": "astral-frontend",
  "repo": "https://github.com/<user>/<repo>",
  "branch": "main",
  "rootDir": "landing/astral-app",
  "buildCommand": "npm install && npm run build",
  "publishPath": "./dist",
  "routes": [{"source": "/*", "destination": "/index.html", "action": "rewrite"}],
  "ownerId": "tea-xxxxxxxxxxxx"
}
```

**Trigger deploy:**
```
POST https://api.render.com/v1/services/{service_id}/deploys
```

**Payment info required for web_service:** The API returns `"Payment information is required"` when creating `web_service` types via API. Static sites work without payment info. To create a backend web_service, either add a card at render.com/billing first, or create the service through the Dashboard.

**Gotcha:** After creating a service via API, the response includes `service.id` (e.g., `srv-xxxxx`) and `deployId`. Save the service ID — you need it to trigger deploys, check logs, and add env vars. The `deployId` tracks the initial auto-triggered deploy.

### Common Render Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Exit 128 on deploy | Start command fails or health check unreachable | Check `startCommand` path/port matches Dockerfile EXPOSE and healthCheckPath |
| Static site 404 | Wrong `staticPublishPath` relative to `rootDir` | Use `./dist` not absolute paths |
| Dashboard service ignores render.yaml | Dashboard-created services are independent | Delete and recreate via YAML, or manually update dashboard settings |
| Build succeeds but page blank | SPA routing missing or Intro never completes | Add `/* → /index.html` rewrite route; add `setTimeout` fallback in Intro |
| Empty commit doesn't trigger rebuild | Render caches build; service in stuck state | Delete service entirely via API/Dashboard, recreate from render.yaml |
| Backend deploy repeatedly fails at same commit | Cached broken build or env issue | Delete service, verify Dockerfile builds locally, recreate |

### Vercel Pitfalls (historical — project no longer uses Vercel)

1. **Vercel 100MB limit:** Repo was 1.7GB (`.venv`, `node_modules`). `vercel promote` creates new build from potentially stale settings — unreliable for cache-busting.

### Frontend Debugging

1. **Three.js deprecation warning:** `three-mesh-bvh@0.7.8` warns about three.js incompatibility. Fix: `npm install three-mesh-bvh@0.8.0`.
2. **Intro not completing:** If `introDone` never becomes `true`, add a `setTimeout` fallback (4s) alongside `requestAnimationFrame` — RAF can fail on production. Also ensure `CanvasBoundary` fallback renders starfield div, not `null`.
3. **Production build mismatch:** Always verify the deployed JS bundle contains expected code: `curl -s <url>/assets/index-*.js | grep -c 'expected_string'`

## Related

- `docker-ai-workspace` — Docker container debugging
- `systematic-debugging` — 4-phase root cause analysis
