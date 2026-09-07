---
name: astrology-app-engine
description: Use when coding astrology features or the Astral backend.
version: 1.0.0
author: ox-alpha (curator)
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [astrology, fastapi, skyfield, ephemeris, astral]
    related_skills: []
---

# Astrology App Engine Development

Class: implementing astrology computation features in application backends. This user's ongoing project: "Astral" — repo `C:/AI/NEW-AI-REBORN` (FastAPI + skyfield DE421), prototype `C:/AI/astral-expo` (Expo), design research notes in Obsidian vault `C:\AI\obsidian-vault`, note "Astral - Design Research 2026".

## Current system map

- `src/main.py` — FastAPI app; routers registered here.
- `src/routers/` — domain routers: natal, transit, vedic, synastry, tarot, horary, bazi, muhurta, chat, memory, research, reports, fusion, chinese, dashboard, health.
- `src/services/` — computation engines; `grand/` subpackage holds phase-4 sciences.
- `src/services/grand/` — grand fusion orchestrator + 18 sciences: transit, western, vedic, BaZi, synastry, tarot, fixed_stars, Sabian, varshaphal, ziwei, numerology, iching, ninestar_ki, mayan, cosmobiology, asteroids, human_design, kalachakra.
- `src/routers/reports.py` — PDF report endpoints. Current endpoints: `/report/natal`, `/report/synastry`, `/report/synastry-dual`, `/report/composite`, `/report/transit`, `/report/muhurta`, `/report/vedic`, `/report/bazi`, `/report/human-design`, `/report/ziwei`, `/report/grand-summary`.
- `src/services/premium_pdf_service.py` — Chrome headless PDF renderer with biwheel SVG, Greek art, Met Museum CC0 images.
- `src/services/weasy_brochure.py` — WeasyPrint HTML→PDF brochure generator with TH/EN bilingual support, Thai font embedding, A4 premium styling.
- `docs/architecture.html` — auto-generated system architecture diagram.

## Non-negotiable correctness rules (each was a real bug or verified finding)

1. **Polarity = planet nature × aspect quality.** NEVER render Venus/Jupiter on a square or opposition as "supportive/หนุน". Hard aspect → "activating" (or "structuring" if Saturn). Soft aspect + benefic → supportive.
2. **skyfield returns numpy scalars** — comparisons produce `numpy.bool_`, which FastAPI cannot JSON-serialize. Cast with `bool(...)` before putting into response dicts.
3. **DE421 contains no Chiron.** Do not fabricate its position; use published ephemeris tables (serennu.com, cafeastrology) with interpolation, and label interpolated values as approximate.
4. **Fusion precedence:** exact dated transit > dasha phase (months backdrop) > BaZi/day tone. When systems disagree, report tension — never average away.
5. **Templates carry evidence.** Every output sentence names its source (which transit+orb, which dasha, which system) and dates where possible. No vague hedging beyond stated confidence.
6. Long installs/tests exceed the 600s foreground terminal cap → `terminal(background=true)` then poll.

## Report endpoint wiring rules

- Every new `/report/*` endpoint must call the **real engine function**, not a placeholder.
- Section builders must consume the actual computed payload keys; do not invent legacy keys like `chart.get("rashi")` unless the engine returns them.
- Remove hardcoded demo data from production narrative code. If demo content is needed, gate it behind an explicit `demo=True` flag.
- Verified engine signatures:
  - vedic: `compute_vedic(birth_datetime_local, lat, lon, tz_offset_hours, person_name)`
  - bazi: `four_pillars(date, time)`
  - human design: `compute_human_design(natal_chart=compute_chart(...))`
  - ziwei: `compute_ziwei(birth_date, birth_time)`
  - grand summary: `compute_grand_fusion(name, lang, years)` from a stored profile

## PDF generation rules

- Use `src/services/weasy_brochure.py` for brochure-style PDFs. Signature: `render_brochure(title, subtitle, sections, out_path, footer="", theme_hint="")`.
- `sections` shape: `[{"title": str, "lines": [str, ...]}, ...]`.
- Keep TH/EN bilingual; prefer natural Thai phrasing over literal translation.
- For server-rendered premium PDFs with charts/images, use `src/services/premium_pdf_service.py`.
- Do not mix both renderers in one report endpoint.

## Verified ground truth (use as regression tests)

Two real charts are locked in with computed positions, dasha sequences, BaZi pillars — see `references/ground-truth-charts.md`. Any new calculation must reproduce these numbers exactly before shipping. Highlights: M (19 May 1997 05:45 Chonburi): sidereal Moon Virgo 23.69° → Chitra pada 1 → Jupiter MD 2022–2038, Jup-Sat AD ends ≈2026.86; Venus Vargottama; AK=Jupiter, DK=Sun; BaZi Ding-Chou Fire Ox (clash Goat → 2027 ชงปีเกิด); ตรียัมปาไถ 1-5-8→5. Mai (18 Aug 2001 22:32 Nonthaburi): Sun+Moon Leo, Venus Cancer 19.90, Asc Taurus 6.34.

## Raw research bank

Vault `C:\AI\obsidian-vault
aw\` holds ~50 cited source notes (synastry overlays, composite vs Davison, Ashtakavarga thresholds, Jaimini karakas, progressions, competitor reviews). Read them before re-researching a technique. Engine-spec work from the Research Department lives in `C:/AI/research-astrology/` (verify_calcs.py, transit_hits.py are runnable checks).

## STARHEART deterministic bridge (chart → tarot reading)

User's standing demand: reel/tarot readings must be **eerily accurate (แม่นจนขนลุก)** — derived from the actual chart, never random. The bridge encodes the team hypothesis *"ดวงคำนวณ (de421) และ reel/ไพ่ คือ ปรากฏการณ์เดียวกันในระดับความละเอียดต่างกัน (coarse↔fine)"*: ephemeris chart = fine-grained state, reel/tarot = coarse-grained reading of that same state.

**Files (built 2026-08-31, verified running):**
- `src/services/starheart_map.py` — `extract_features(chart)` → feature vector; `MAP(chart)` → list of `{card, orientation, feature_source, provenance}` as a **pure function, no RNG**; `verify_reading(spread, chart)` checklist.
- `src/services/reel_reading.py` — calls `starheart_map.MAP(chart)` when `chart` is passed; keeps random `seed` behaviour when `chart is None` (backward-compat).
- `scripts/build_couple_premium.py` — `chart_echo(composite)` derives the couple reading deterministically from the composite chart.
- `src/services/prediction_log.py` + `src/db/prediction_log_store.py` + `src/services/specificity_scorer.py` + `src/services/hit_rate_audit.py` — timestamped proof system (pre_register before event, confirm/refute, Barnum-score gate, survivorship-safe hit-rate).

**Verification loop — NEVER ship one half without the other (user directive "อย่าลดทดสอบ คลิปกับดาว"):**
1. RETROSPECTIVE match: take real reel transcripts (e.g. IG clips), run `MAP(chart)` for both people, match each clip's theme to a `feature_source`. Report a hit-rate %. This proves the reading reflects real stars (coarse↔fine).
2. PROSPECTIVE register: `pre_register(chart, claim_text, expected_event)` for future events; confirm when they occur.
Skipping the retrospective clip↔chart test while rushing to prospective prediction is a hard failure — both must run. See `references/starheart-evidence-workflow.md` for the reel-transcription + matching recipe.

## Environment prerequisites

- Python runtime: use `uv run python` so project dependencies resolve.
- Missing optional packages: install explicitly, e.g. `uv add lunar-python` for Zi Wei; re-run import smoke test after install.
- Tests: `uv run pytest` from repo root; 430+ tests currently passing.

## Narrative depth rules (user directive 2026-09-05)

**CRITICAL:** Narrative must be **per-user, not generic**. User explicitly rejected template-style predictions:
- "อย่าลืม narative ประสบการของคนๆนั้นด้วย ไม่ใช่แค่ทำนายกว้างๆ แต่ต้องเจาะถึงสิ่งที่คิด ที่รู้สึก ที่คาดหวัง"
- Every narrative must pierce through to: **ความคิด (thoughts), ความรู้สึก (feelings), ความคาดหวัง (expectations), ความกลัว (fears), บทเรียนชีวิต (life lessons)**

### Narrative structure (8 sections, depth-first)
1. **Overview** — Sun/ASC with Thai idioms + depth psychology archetype
2. **Inner World** — Moon with emotional body description
3. **Fears & Shadows** — Saturn + detected complexes (Moon-Saturn, Sun-Saturn, etc.)
4. **Desires & Aspirations** — Jupiter + Venus with growth/love patterns
5. **Life Lessons** — Saturn return + nodal axis
6. **Relationships** — Mars + Venus dynamics
7. **Career** — MC + 10th house + Jupiter
8. **Summary** — integration of all above

### Depth psychology framework (Jungian / Liz Greene / CPA tradition)
- **Sun** = ego consciousness, developing Self, hero's journey
- **Moon** = personal unconscious, emotional memory, mother complex
- **Saturn** = Shadow, senex, father complex, limitation/structure
- **Venus** = the Lover, anima, relationship patterns
- **Mars** = the Warrior, animus, assertion/drive
- **Jupiter** = the Sage, growth, meaning
- **Uranus** = Promethean, rebellion, individuation
- **Neptune** = the Mystic, dissolution, transcendence
- **Pluto** = the Shadow, transformation, rebirth

### Complexes to detect (from tradition)
- **Moon-Saturn** = deprivation complex (emotional withholding)
- **Sun-Saturn** = father wound / authority complex
- **Mars-Saturn** = inhibition complex (repressed anger)
- **Venus-Pluto** = fusion complex (all-or-nothing love)
- **Sun-Pluto** = identity shadow complex

### Knowledge base files (in `src/services/knowledge/`)
- `depth_psychology.json` — 9 archetypes with fear/desire/shadow/individuation
- `complexes.json` — 5 major complexes with fear/healing
- `thai_idioms.json` — 24 Thai idioms for Sun/Moon in signs
- `transit_th_templates.json` — transit narratives in Thai
- `synastry_th_templates.json` — relationship dynamics in Thai
- `nakshatra_padas.json` — 108 padas (27 nakshatras × 4)
- `vimshottari_dasha.json` — 9 mahadashas with antardashas
- `vedic_yogas.json` — 10 major yogas with conditions/results
- `harmonic_charts.json` — D9/D10/D12 methods
- `midpoint_trees.json` — 5 major midpoints
- `arabic_parts.json` — 10 Arabic Parts with formulas

## Security & infrastructure rules

- **Rate limiting**: 60 req/min public, 120 req/min authenticated (sliding window)
- **Auth enforcement**: sensitive endpoints require valid Supabase token
- **Security headers**: HSTS, X-Frame-Options, X-XSS-Protection, X-Content-Type-Options
- **Request ID**: every response includes X-Request-ID header
- **Input validation**: date range 1899-2053 (DE421 bounds), lat [-90,90], lon [-180,180], tz [-12,14]
- **Error handling**: never expose internal paths; generic error messages with request_id

## House systems (4 supported)
1. **Placidus** — iterative semi-arc (100 iterations)
2. **Koch** — birthplace system, closed-form
3. **Equal** — each house starts 30° from ASC
4. **Whole Sign** — each house = one whole sign

## Advanced calculations (in `src/services/advanced_calculations.py`)
- `compute_nakshatra_pada(longitude)` → nakshatra + pada + ruler
- `compute_vimshottari_dasha(birth_jd, target_jd)` → mahadasha + antardasha
- `detect_vedic_yogas(chart)` → list of detected yogas
- `compute_harmonic_chart(chart, division)` → D9/D10/D12
- `compute_midpoints(chart)` → major midpoints
- `compute_arabic_parts(chart)` → Arabic Parts with formulas

## AI Narrative Generator (in `src/services/ai_generator.py`)

Rule-based AI that generates per-user narratives using depth psychology + knowledge base.

- `generate_full_reading(chart, user_id, lang)` → 8-section narrative
- Uses: depth_psychology.json, complexes.json, thai_idioms.json, aspect_meanings, house_placements
- NEVER generic template — always pierce to thoughts/feelings/expectations/fears

## Feedback Loop (in `src/services/feedback_service.py`)

- `submit_feedback(reading_id, user_id, rating, comment, section)` → store in `user_feedback` table
- `get_feedback_stats(user_id)` → average rating + count
- `get_low_rated_sections()` → sections with avg rating < 3 (need improvement)

## Event Mapping (in `src/services/event_service.py`)

- `record_event(user_id, event_date, category, description, significance, related_transit)` → store in `life_events` table
- `find_transit_event_correlations(user_id)` → match transits to real events

## User Preferences (in `src/services/user_service.py`)

- `get_preferences(user_id)` → preferred system, house, depth, language, notifications
- `set_preferences(user_id, **kwargs)` → update preferences

## Database Tables (migration `db_migration_99.py`)

- `narrative_readings` — log every narrative generated
- `user_feedback` — user ratings (1-5) + comments
- `life_events` — real life events with transit correlations
- `transit_tracking` — active transits with intensity
- `user_preferences` — per-user settings

## Frontend pipeline: narrative_lang.py → strings.js → components

The landing page (`landing/astral-app/`, React + Vite) uses a centralized language pipeline:

1. **`backend/src/services/narrative_lang.py`** — Single Source of Truth for ALL user-facing strings (Thai/English). Contains: astrology data (SIGN_NAMES, ELEMENT_NAMES, BODY_LABELS, HOUSE_ZONES, etc.) + UI sections (NAV, HERO, SECTION, BUTTONS, FORM, RESULT, APP, TAROT, BIRTH_FORM, INTRO).
2. **`backend/src/services/generate_strings_js.py`** — Generator: reads `narrative_lang.export_i18n()` → writes JS module. Quote ALL keys (e.g. `"01_title"`) since numeric-prefixed keys are invalid JS identifiers.
3. **`landing/astral-app/src/strings.js`** — AUTO-GENERATED. Never edit manually.
4. **React components** — Import `S` from `./strings.js`, use `S.nav.home`, `S.hero.pill`, etc.

**Pipeline command:**
```bash
cd C:/AI/NEW-AI-REBORN && python backend/src/services/generate_strings_js.py > landing/astral-app/src/strings.js
```

**To change any visible text:** edit `narrative_lang.py` → regenerate → strings.js auto-updates → components reflect changes.

### Frontend file map
- `landing/astral-app/src/App.jsx` — Main app: nav, view routing, hero section, all useRefactored to use `S.*`
- `landing/astral-app/src/LifeReport.jsx` — Life report view
- `landing/astral-app/src/SpacekitCosmos.jsx` — 3D solar system view
- `landing/astral-app/src/NatalWheel.jsx` / `SynastryWheel.jsx` — Chart wheels
- `landing/astral-app/src/MotionToggle.jsx` — Animation toggle
- `landing/astral-app/src/Intro.jsx` — Intro/warp animation
- `landing/astral-app/src/OrbitGalaxy.jsx` — Orbit selection
- `landing/astral-app/src/api.js` — API calls
- `landing/astral-app/src/styles.css` — All CSS (1081 lines)

### Deployment architecture (hard-won, 2026-09-05)

**Two-service split:**
- **Backend** → Render.com (FastAPI + Docker, `astral-pb5k.onrender.com`). Serves API + frontend static files.
- **Frontend** → Vercel (React + Vite static, `astral-orpin-rho.vercel.app`). CDN-backed, faster globally.

**Render deployment (backend + serves frontend too):**
- Repo root has `render.yaml` with `astral-backend` (Docker) + `astral-frontend` (static site).
- Dockerfile builds frontend (`npm run build`) → copies `dist/` → serves via FastAPI StaticFiles.
- Health check: `/ready` endpoint.
- Auto-deploy on git push to main.

**Vercel deployment (frontend-only, preferred):**
- `vercel.json` at repo root: build `landing/astral-app`, output `dist/`.
- **CRITICAL**: Vercel free plan has 100MB upload limit. CLI `vercel deploy` uploads the entire repo (including .venv, node_modules, backend = 1.7GB+). This fails with `File size limit exceeded (100 MB)`.
- **FIX**: Use Vercel dashboard (vercel.com) to trigger builds — Vercel builds on its own servers via git webhook, no upload needed.
- `.vercelignore` excludes: `.venv/`, `backend/`, `tests/`, `docs/`, `node_modules/`, `*.md`, `Dockerfile`, `render.yaml`, `.github/`.
- **Vercel CLI**: Requires latest version (59+). Install: `npm i -g --allow-scripts=esbuild vercel@latest`.
- Link: `vercel link --token $VERCEL_TOKEN --project $VERCEL_PROJECT_ID --yes`
- Vercel project ID: `prj_auv96e2Fifk2723bt2Rm4WZyU7Ed` (Astral project)
- Vercel token: stored as `vcp_...` (user-provided)
- **npm ci vs npm install**: On Windows, `npm ci` may fail with EPERM on esbuild.exe. Use `npm install` in build command.
- **Multi-service config**: Vercel CLI auto-detects FastAPI + Vite → conflicts with manual vercel.json. Configure via dashboard instead of CLI when possible.

**Frontend render debugging (when deployed site shows blank/white screen):**
1. Check if HTML loads: `curl -s https://url | grep root` → should show `<div id="root"></div>`
2. Check assets load: `curl -sI https://url/assets/index-*.js` → should be 200
3. **Common cause**: Intro animation never calls `onDone` → `introDone` stays false → UI has `visibility:hidden`.
   - Fix: Add `setTimeout` fallback (4s) in `Intro.jsx` alongside `requestAnimationFrame`.
4. **Common cause**: `CanvasBoundary` error boundary catches WebGL failure → returns null → starfield disappears.
   - Fix: Fallback returns `<div className="css-starfield-fallback" />` instead of null.
5. **Common cause**: Numeric-prefixed keys in generated JS (e.g. `01_title`) → `SyntaxError` → blank page.
   - Fix: `generate_strings_js.py` must quote ALL keys: `print(f'    "{k}": {val},')`

### Critical CSS/visual rules (hard-won, 2026-09-05)

1. **WebGL canvas z-index vs CSS background**: The `<Canvas id="bg-canvas">` (Three.js) renders OPPERATIVE full-screen with `z-index: 1` by default, COMPLETELY BLOCKING any CSS starfield on `body::before`/`::after` (which have `z-index: 0`). Fix: set `#bg-canvas { z-index: 0; opacity: .5; mix-blend-mode: screen; }` and put starfield on real `<div>` elements with `z-index: 3` (higher than canvas, lower than `.ui` at z-index: 10).

2. **body::before/::after pseudo-elements are unreliable** for animated starfields — some browsers don't animate them. Use real `<div className="starfield-real">` with nested `<div className="stars-layer">` and `<div className="nebula-layer">` instead.

3. **Build/deploy checklist** after CSS/JSX changes:
   ```bash
   cd landing/astral-app && ./node_modules/.bin/vite build
   ```
   Watch for: numeric separator errors (quote all JS keys), missing imports.

4. **Dev server port conflicts**: Kill all node processes (`taskkill /F /IM node.exe`) before restarting vite. Multiple vite instances on different ports (5175/5176) confuse the preview tool.

5. **Browser cache**: After CSS changes, user must hard-refresh (Ctrl+Shift+R). The preview tool may show stale CSS otherwise. Always verify by curling `/src/styles.css` and grep for new selectors.

### Premium visual standards (user standing order)

User expects "best-tier / นายท่าน level" output:
- Animated starfield (20+ stars, multi-color: white/gold/blue/purple)
- Nebula glow layers (3+ colors, slow drift animation)
- Glowing pill/CTA animations
- Premium button hover effects (lift + glow)
- Smooth scroll hint bounce
- Section decorative nebula blurs
- Nav blur + shadow on scroll
- All typography: Cinzel for headings, Sarabun for body, proper letter-spacing
- NO flat/static/dark-background-with-no-starfield look — that was explicitly rejected

## Patch note format (user requirement)

Every commit MUST include detailed patch note:
```
<type>: <short summary>

- <what changed 1>
- <what changed 2>
...

Result: <test count> tests passing
```
