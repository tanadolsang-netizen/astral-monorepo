# Session Notes 2026-08-29

## Repo Cleanup
- Removed `frontend/`, `mobile/`, `out/`, `scripts/`, `supabase/`, `docs/`, `.data/` from git and disk.
- Added `.gitignore` rules for runtime artifacts, demo files, and private data.
- Personal birth profiles (`mai.json`, `m.json`) must stay local/private; never commit.

## Section Art Wiring
- All 11 `/report/*` endpoints now pass `section_art=_section_art_map(theme, len(sections))` to `render_brochure()`.
- Synastry endpoints use `_pick_greek_art()` for content-based art selection plus `biwheel`, `raw_section`, `raw_title`.
- Fixed `_pick_greek_art()` to use repo-relative `assets/art/` paths instead of hardcoded `D:\AI\...`.

## Ephemeris Issue
- `src/services/ephemeris.py` requires `de421.bsp` at import time.
- JPL mirror `naif.jpl.nasa.gov` returned 404 for `de421.bsp`.
- Tests in `tests/test_western.py` fail at collection when BSP is absent.
- Documented in `SYSTEM_FLOW.md` as a known issue; do not silently swap ephemeris engine.

## Uvicorn Lesson
- Port 8001 conflict causes exit code 3 / `Errno 10048`.
- Fix: use alternate port or `TestClient` for smoke tests.
- Added rule to `SYSTEM_FLOW.md`.
