# Recovered from stale Astral/ snapshot (2026-09-26)

These 11 modules exist in `Astral/backend/src/services/` but NOT in the live
`C:/AI/backend/src/`. Nothing in live code imports them, so they were dropped
from the real backend at some point. Kept here before the snapshot is deleted.

- `src/services/chart_narrative_full.py` — 227 lines
- `src/services/fixedstars_service.py` — 433 lines
- `src/services/hit_rate_audit.py` — 92 lines
- `src/services/houses_service.py` — 102 lines
- `src/services/narrative_gate.py` — 265 lines
- `src/services/narrative_sanitizer.py` — 42 lines
- `src/services/narrative_writer.py` — 228 lines
- `src/services/pdf_report_service.py` — 125 lines
- `src/services/push_service.py` — 24 lines
- `src/services/specificity_scorer.py` — 116 lines
- `src/services/tarot_downloader.py` — 144 lines

## Residue with no live equivalent (recovered 2026-09-26)

`Astral/` was a cross-machine handoff snapshot exported 2026-08-31 from the home
machine. Live `C:/AI` is strictly newer on all 36 overlapping source files, so the
snapshot itself was deleted. These files existed ONLY in it:

- `backend/assets/art/met-picks.json`
- `backend/scripts/test_pipeline_multi.py`
- `backend/scripts/test_starheart_narrative.py`
- `backend/tests/test_grand_modules.py`
- `backend/tests/test_grand_phase4.py`
- `memory/MEMORY.md`
- `memory/USER.md`
- `README.md`
- `SYSTEM-TREE.md`
- `sync.sh`
- `landing/astral-app/.gitignore`
- `hermes/profile-default.tar.gz` (14.9 MB) -> backed up to `hermes/data/cache/scratch/astral-handoff-profile-2026-08-31.tar.gz`
