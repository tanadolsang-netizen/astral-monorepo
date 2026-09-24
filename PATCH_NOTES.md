# Patch Notes

## v3.0.1 — 2026-09-24 (`6067750`)

### Repo Structure
- **Consolidated repo root**: `NEW-AI-REBORN/backend` → `backend/`, landing pages → `astral-landing/`, CI workflow → `.github/workflows/ci.yml` (single source of truth, no duplicate trees)
- Removed 65 dead files from the old tree (deprecated templates, wav clips, stale audits, gitlink submodules)

### Test Suite — 19 failures → 0
- **556 passed, 0 failed** (was 537 passed / 19 failed)
- Fixed `observability.py` middleware: `UnboundLocalError` when an exception bubbled through (`status` never set on the 500 path)
- Fixed stale tests asserting old API shapes:
  - `test_vedic_muhurta.py`: vedic chart endpoint takes flat `{name, date, time}`, not nested `birth` object
  - `test_chat_and_narrative.py`: rewritten for the unified local LLM client (Ollama/Qwen3) — old tests asserted removed multi-provider `LLMConfig.providers` API
  - `test_chinese.py`: pydantic validation returns 422 (not 400) for malformed dates — expected behavior, test corrected
- **New `tests/conftest.py`**: autouse fixture resets the in-memory rate limiter between tests — 9 "random" failures were the 60 req/min public limit tripping mid-suite (test isolation bug, not app bug)
- Regenerated `astral.db` via `db/setup_local_db.py` for local_db tests

### Dependencies
- Added missing `openai` package to `pyproject.toml` (`llm_client.py` imports it; was absent — caught by fresh-install verification)

### New Tooling
- **`scripts/deep_scan.py`** — local Qwen3 code auditor: feeds every `src/` file to `qwen3-8b-uc` via Ollama, caches per-file JSON results in `scan_results/` (resumable), aggregates to `FULL_CODE_ANALYSIS.md`
  - Thinking-model fix: `/no_think` prefix + `max_tokens=2500` (Qwen3 burned the whole 500-token budget on hidden reasoning, returned empty content)
  - 106/142 files scanned before this commit; rerun `uv run python scripts/deep_scan.py` to finish + generate the report

### Verified
- Full suite green: `556 passed` in 84s
- Live boot check: `/health` `/metrics` `/docs` `/` `/landing/astral.html` all 200
- `/v1/chat/health` → `{"ok":true,"engine":"ollama","model":"qwen3-8b-uc:latest"}`

---

## v3.0.0 (`2ac8837`)
- Backend merge 2→1, LLM router (local Qwen3), observability middleware, security audit, local config
