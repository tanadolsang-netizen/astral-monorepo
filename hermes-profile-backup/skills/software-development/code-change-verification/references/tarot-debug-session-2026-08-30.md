# Tarot Backend Debugging Session (Aug 30, 2026)

## Subagent verification failures
- ATLAS claimed 78-card rewrite completed, but the produced `tarot_meanings_th.py` still contained EN/CJK fragments: `bambai`, `manipulating`, `正在餐`, `subconscious`, `mas俚`, etc.
- Subagent hit rate limits / iteration caps and still returned `completed`. Always verify artifact counts and sample content; do not trust completion claims.

## Patch failures on Unicode/dense strings
- `patch` repeatedly failed on `tarot_service.py` because the inline `_THAI_MEANINGS` block contained long Thai strings with embedded quotes and Unicode.
- Workaround: use `terminal` + Python rewrite targeting a unique anchor substring, then write the cleaned text. Re-compile with `python -m py_compile` immediately after.

## Root-cause ordering
- Smoke test showed collection errors (`ImportError: FULL_DECK`), then `KeyError: 'Four'`, then assertion failures, then EN narrative hook misses.
- Fix syntax/import/format issues first; behavior fixes applied during a broken import phase are wasted and create misleading diffs.

## Dataset-driven name generation
- `MINOR_ARCANA` was built as `f"{s} of {v}"` instead of `f"{v} of {s}"`, producing `Cups of Ace` instead of `Ace of Cups`.
- Downstream effect: `_generic_minor_story` parsed suit as `Queen`, causing `KeyError: 'Queen'`.
- Fix: validate generated names against the dataset immediately after generation.

## Position-label mapping mismatch
- `reel_reading.py` passed numeric `position` to `_HOOKS_TH` whose keys are Thai labels (`สถานการณ์ปัจจุบัน`, etc.).
- Fix: map `position` -> label via `_POSITION_LABEL` / `_POSITION_LABEL_EN` before hook lookup.

## Element balance key mismatch
- `_tilted_toward` used `weakest`, but `compute_element_balance` returns `lacking`.
- Fix: fallback chain `weakest` -> `lacking` -> `dominant`.
