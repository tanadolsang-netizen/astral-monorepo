# Frontend Visual Patterns — Hard-Won Lessons (2026-09-05)

## Problem: CSS starfield invisible behind WebGL canvas

**Symptom:** User sees flat black background, no stars, no glow — even though CSS has `body::before` with 20+ radial-gradient stars and animations.

**Root cause:** `<Canvas id="bg-canvas">` (Three.js) renders at `z-index: 1` with opaque black, completely covering `body::before`/`::after` pseudo-elements at `z-index: 0`.

**Fix:**
1. Set `#bg-canvas { z-index: 0; opacity: .5; mix-blend-mode: screen; }`
2. Move starfield from `body::before/::after` to real `<div className="starfield-real">` at `z-index: 3`
3. Nest `<div className="stars-layer">` and `<div className="nebula-layer">` inside
4. `.ui` stays at `z-index: 10` (above starfield)

## Problem: body::before/::after animations unreliable

Pseudo-elements on `body` don't animate consistently across browsers. Use real div elements for animated backgrounds.

## Problem: Dev server port conflicts

Multiple vite instances (5175, 5176) confuse the preview tool. Fix:
```bash
taskkill /F /IM node.exe
cd landing/astral-app && ./node_modules/.bin/vite --port 5175 --force
```

## Problem: Browser cache shows stale CSS

After CSS changes, preview tool may show old styles. Verify with:
```bash
curl -s http://localhost:5175/src/styles.css | grep -c 'starfield-real'
```
If count > 0, the new CSS is served — user needs Ctrl+Shift+R.

## Problem: Numeric-prefixed JS object keys fail build

`generate_strings_js.py` outputs `01_title: "..."` which is invalid JS (numeric separator error at build). Fix: quote all keys → `"01_title": "..."`.

## Premium visual checklist (user standing order)

- [ ] Animated starfield (20+ stars, multi-color)
- [ ] Nebula glow layers (3+ colors, slow drift)
- [ ] Glowing pill animation
- [ ] Premium button hover (lift + glow)
- [ ] Scroll hint bounce
- [ ] Section decorative blurs
- [ ] Nav blur + shadow on scroll
- [ ] Cinzel headings + Sarabun body
- [ ] NO flat/static look

## File map

```
landing/astral-app/
├── src/
│   ├── App.jsx          (main app, starfield div, nav, views)
│   ├── styles.css       (all CSS, ~1081 lines)
│   ├── strings.js       (AUTO-GENERATED from narrative_lang.py)
│   ├── LifeReport.jsx
│   ├── SpacekitCosmos.jsx
│   ├── NatalWheel.jsx / SynastryWheel.jsx
│   ├── MotionToggle.jsx
│   ├── Intro.jsx
│   ├── OrbitGalaxy.jsx
│   └── api.js
└── public/
    └── i18n.json        (JSON export for frontend)
```

## Pipeline command

```bash
cd C:/AI/NEW-AI-REBORN && python backend/src/services/generate_strings_js.py > landing/astral-app/src/strings.js
```

## Problem: Vercel CLI deploy fails for large repos (>100MB)

**Symptom:** `vercel deploy --prod` uploads entire repo (1.7GB+ with .venv, node_modules, backend) → `File size limit exceeded (100 MB)`.

**Root cause:** Vercel free plan has 100MB upload limit. CLI `vercel deploy` uploads local files, not just git-tracked ones.

**Fix:** Use Vercel dashboard (vercel.com) to trigger builds via git webhook — Vercel builds on its own servers, no upload needed.

1. Go to vercel.com → Project → Deployments → New Deployment → select branch `main` → Deploy
2. Or: Project Settings → Git → enable auto-deploy on push

**`.vercelignore`** (exclude non-frontend files):
```
.venv/
backend/
tests/
docs/
node_modules/
*.md
Dockerfile
render.yaml
.github/
```

## Problem: npm ci fails on Windows (esbuild.exe locked)

**Symptom:** `npm ci` → `EPERM: operation not permitted, unlink '...\@esbuild\win32-x64\esbuild.exe'`

**Root cause:** esbuild.exe is held by another process (vite dev server, antivirus, or previous build).

**Fix:** Use `npm install` instead of `npm ci` in Vercel build command:
```json
{
  "buildCommand": "cd landing/astral-app && npm install && npm run build"
}
```

## Problem: Vercel multi-service config is fragile via CLI

**Symptom:** `vercel link` / `vercel project update` fail with:
- `Service name "0" is invalid`
- `The top-level properties buildCommand, outputDirectory, framework cannot be used with services`
- `Project names can be up to 100 characters`

**Root cause:** Vercel CLI auto-detects services (FastAPI backend + Vite frontend) and conflicts with manual `vercel.json` config.

**Fix:** Configure project settings via dashboard instead:
1. vercel.com → Project → Settings → Framework Preset → Vite
2. Build Command: `cd landing/astral-app && npm install && npm run build`
3. Output Directory: `landing/astral-app/dist`
4. Install Command: (leave default)

## Problem: Deployed site shows blank page (astral-pb5k.onrender.com)

**Symptom:** HTML loads (200 OK), assets load (200 OK), but React doesn't render — white/black screen.

**Root cause chain (all three can trigger this):**
1. **Intro animation never completes** — `requestAnimationFrame` may not fire → `introDone` stays `false` → UI has `visibility:hidden`.
   - Fix: Add `setTimeout` fallback (4s) in `Intro.jsx`.
2. **CanvasBoundary catches WebGL failure** → returns `null` → starfield + canvas disappear.
   - Fix: Fallback returns `<div className="css-starfield-fallback" />` instead of null.
3. **Numeric-prefixed JS keys** → `SyntaxError` → blank page.
   - Fix: `generate_strings_js.py` must quote ALL keys.

**Debug checklist:**
```bash
# 1. Check HTML loads
curl -s https://url | grep '<div id="root">'

# 2. Check assets load
curl -sI https://url/assets/index-*.js  # → 200
curl -sI https://url/assets/index-*.css # → 200

# 3. Check for JS errors in bundle
curl -s https://url/assets/index-*.js | grep -c 'SyntaxError\|ReferenceError'

# 4. Check if new CSS is served
curl -s https://url/assets/index-*.css | grep -c 'starfield-real'
```