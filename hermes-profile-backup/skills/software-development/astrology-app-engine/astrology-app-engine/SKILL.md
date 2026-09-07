---
name: astrology-app-engine
description: Use when coding astrology features or the Astral backend.
version: 1.0.1
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

- Use `src/services/weasy_brochure.py` for all report endpoints. Signature: `render_brochure(sections, out_path, *, person_name="", lang="th", theme_hint="", biwheel="", section_art=None, raw_section="", raw_title="")`.
- `sections` shape: `[{"title": str, "lines": [str, ...]}, ...]`. **Every item in `lines` must be a string.** Non-string values crash WeasyPrint with `AttributeError: 'dict' object has no attribute 'replace'`.
- Keep TH/EN bilingual; prefer natural Thai phrasing over literal translation.
- For artwork/biwheel/tarot extras, pass `biwheel`, `section_art`, `raw_section`, `raw_title` to `render_brochure`. Unused extras are safely ignored.
- Do not mix renderers in one report endpoint.
- For detailed migration notes and verified router patterns, see `references/weasyprint-brochure-notes.md`.

## Verified ground truth (use as regression tests)

Two real charts are locked in with computed positions, dasha sequences, BaZi pillars — see `references/ground-truth-charts.md`. Any new calculation must reproduce these numbers exactly before shipping. Highlights: M (19 May 1997 05:45 Chonburi): sidereal Moon Virgo 23.69° → Chitra pada 1 → Jupiter MD 2022–2038, Jup-Sat AD ends ≈2026.86; Venus Vargottama; AK=Jupiter, DK=Sun; BaZi Ding-Chou Fire Ox (clash Goat → 2027 ชงปีเกิด); ตรียัมปาไถ 1-5-8→5. Mai (18 Aug 2001 22:32 Nonthaburi): Sun+Moon Leo, Venus Cancer 19.90, Asc Taurus 6.34.

## Raw research bank

Vault `C:\AI\obsidian-vault` holds ~50 cited source notes (synastry overlays, composite vs Davison, Ashtakavarga thresholds, Jaimini karakas, progressions, competitor reviews). Read them before re-researching a technique. Engine-spec work from the Research Department lives in `C:/AI/research-astrology/` (verify_calcs.py, transit_hits.py are runnable checks).

## Environment prerequisites

- Python runtime: use `uv run python` so project dependencies resolve.
- Missing optional packages: install explicitly, e.g. `uv add lunar-python` for Zi Wei; re-run import smoke test after install.
- Tests: `uv run pytest` from repo root; 430+ tests currently passing.

## Pitfalls

- Do not commit personal birth profiles to git; keep them in `.data/profiles/` locally or exclude via `.gitignore`.
- When syncing Hermes profile data across machines, use branch `hermes-profile` and copy `.hermes-profile/*` into `%APPDATA%/Local/hermes/` on the target.
- Report endpoint helpers must return **non-empty** `lines` lists; empty sections are filtered out before rendering.
- WeasyPrint requires font paths as `file:///` URLs; use `.as_posix()` for Windows paths.

## Ephemeris / DE421 BSP rule

- `src/services/ephemeris.py` now tries multiple NASA mirrors and auto-downloads `de421.bsp` into the repo root when missing.
- `.gitignore` contains `de421.bsp`; do not commit the binary.
- If BSP download is unavailable in an environment, prefer fixing the mirror/fallback chain rather than disabling ephemeris-dependent tests.

## Artwork path rule

- `_pick_greek_art()` and any artwork lookup must use repo-relative paths, e.g. `Path(__file__).resolve().parents[2] / "assets" / "art"`.
- Never hardcode `D:\...` absolute paths; they break on other machines and in CI.

## Report extras wiring

- Every `/report/*` and `/brochure/*` endpoint should pass `section_art=_section_art_map(theme_hint, len(sections))` to `render_brochure()`.
- Synastry endpoints additionally pass `biwheel`, `raw_section`, and `raw_title`.

## Server / port rule

- Uvicorn on port 8001 may fail with `Errno 10048` if the port is already in use.
- Do not blindly retry the same command. Either free the port, use another port such as 8002, or use `TestClient` for smoke tests.