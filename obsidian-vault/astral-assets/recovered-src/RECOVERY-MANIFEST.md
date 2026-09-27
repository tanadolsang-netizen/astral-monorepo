# RECOVERY-MANIFEST — Astral/ (machine-verifiable)

Regenerate: `python verify.py --write` · Re-verify: `python verify.py --json`

Fingerprint = SHA-256 over `<sha256>  <relative-path>\n`, sorted by path,
excluding `RECOVERY-MANIFEST.md`, `verify.py`.

| | |
|---|---|
| source | `C:\AI\Astral` — deleted, no longer on disk |
| recovered | `C:\AI\obsidian-vault\astral-assets\recovered-src` |
| verified against | git `0a889edf8ee7f7a4e6798839222a8088909700f8` |
| files / bytes | **363** / 27802754 |
| fingerprint (sha256) | `180b8c2809b37942d5a301c0c0451f61d2d83e1725ffac3252fa16651721ca7b` |

## Verification

| check | count |
|---|---:|
| HEAD entries under `Astral/` | 373 |
| byte-identical to HEAD | 339 |
| differs from HEAD | 0 |
| live copy identical to HEAD | 11 |
| live copy differs from HEAD | 23 |
| live copy absent | 0 |
| never committed to git (disk-only rescue) | 24 |
| **unexplained** | **0** |

Accounting: 339 matched + 34 live-resolved = 373 = all HEAD entries.

`command/` is **absent** by request — the Command Bus / hive was retired 2026-09-26.

## Never committed to git — disk-only rescue

Git could never have restored these. They exist only because the rescue copied them off disk.

| path | bytes |
|---|---:|
| `README.md` | 1628 |
| `_rescue-list.txt` | 18935 |
| `handoff-README.md` | 3277 |
| `handoff-SYSTEM-TREE.md` | 3676 |
| `handoff-sync.sh` | 14622 |
| `landing-astral-app-2026-08-31/.gitignore` | 38 |
| `memory-stale-2026-08-31/MEMORY.md` | 1606 |
| `memory-stale-2026-08-31/USER.md` | 1177 |
| `services/chart_narrative_full.py` | 14377 |
| `services/fixedstars_service.py` | 19328 |
| `services/hit_rate_audit.py` | 3332 |
| `services/houses_service.py` | 4287 |
| `services/narrative_gate.py` | 13909 |
| `services/narrative_sanitizer.py` | 1348 |
| `services/narrative_writer.py` | 14278 |
| `services/pdf_report_service.py` | 4959 |
| `services/push_service.py` | 823 |
| `services/specificity_scorer.py` | 4076 |
| `services/tarot_downloader.py` | 4473 |
| `src/backend/assets/art/met-picks.json` | 663 |
| `src/backend/scripts/test_pipeline_multi.py` | 3400 |
| `src/backend/scripts/test_starheart_narrative.py` | 3677 |
| `src/backend/tests/test_grand_modules.py` | 11564 |
| `src/backend/tests/test_grand_phase4.py` | 14665 |

## HEAD entries resolved live (not duplicated)

| HEAD path | live copy | status |
|---|---|---|
| `Astral/backend/assets/fonts/Sarabun-Bold.ttf` | `backend\assets\fonts\Sarabun-Bold.ttf` | LIVE_IDENTICAL |
| `Astral/backend/assets/fonts/Sarabun-Regular.ttf` | `backend\assets\fonts\Sarabun-Regular.ttf` | LIVE_IDENTICAL |
| `Astral/backend/ephe/seas_18.se1` | `backend\ephe\seas_18.se1` | LIVE_IDENTICAL |
| `Astral/backend/src/__init__.py` | `backend\src\__init__.py` | LIVE_IDENTICAL |
| `Astral/landing/assets/clips/audio/c1.wav` | `astral-landing\assets\clips\audio\c1.wav` | LIVE_IDENTICAL |
| `Astral/landing/assets/clips/audio/c4.wav` | `astral-landing\assets\clips\audio\c4.wav` | LIVE_IDENTICAL |
| `Astral/vault/.obsidian/Untitled.canvas` | `obsidian-vault\.obsidian\Untitled.canvas` | LIVE_IDENTICAL |
| `Astral/vault/.obsidian/appearance.json` | `obsidian-vault\.obsidian\appearance.json` | LIVE_IDENTICAL |
| `Astral/vault/.playwright-mcp/console-2026-08-14T12-14-30-204Z.log` | `obsidian-vault\.playwright-mcp\console-2026-08-14T12-14-30-204Z.log` | LIVE_IDENTICAL |
| `Astral/vault/Astral Project/Astral Project - State & Decisions 2026-08-30.md` | `obsidian-vault\Astral Project\Astral Project - State & Decisions 2026-08-30.md` | LIVE_DIFFERS |
| `Astral/vault/Astral Project/Natal Chart - 19 พ.ค. 2540.md` | `obsidian-vault\Astral Project\Natal Chart - 19 พ.ค. 2540.md` | LIVE_DIFFERS |
| `Astral/vault/Astral Project/STARHEART - สะพานดวงคำนวณ↔รีล.md` | `obsidian-vault\Astral Project\STARHEART - สะพานดวงคำนวณ↔รีล.md` | LIVE_DIFFERS |
| `Astral/vault/Astral Project/Synastry - Mai (18 ส.ค. 2544).md` | `obsidian-vault\Astral Project\Synastry - Mai (18 ส.ค. 2544).md` | LIVE_DIFFERS |
| `Astral/vault/Astral Project/Tarot/Tarot & Energy Reading - 2026-08-12.md` | `obsidian-vault\Astral Project\Tarot\Tarot & Energy Reading - 2026-08-12.md` | LIVE_DIFFERS |
| `Astral/vault/Astral Project/Tarot/Tarot - Two Spreads (13 ส.ค. 2026).md` | `obsidian-vault\Astral Project\Tarot\Tarot - Two Spreads (13 ส.ค. 2026).md` | LIVE_DIFFERS |
| `Astral/vault/Meta/Company PC Setup.md` | `obsidian-vault\Meta\Company PC Setup.md` | LIVE_DIFFERS |
| `Astral/vault/Meta/Dispatch Console Build Kit - เสริมสุข.md` | `obsidian-vault\Meta\Dispatch Console Build Kit - เสริมสุข.md` | LIVE_DIFFERS |
| `Astral/vault/Meta/Knowledge Hub.md` | `obsidian-vault\Meta\Knowledge Hub.md` | LIVE_DIFFERS |
| `Astral/vault/Real_one/.obsidian/app.json` | `obsidian-vault\Real_one\.obsidian\app.json` | LIVE_IDENTICAL |
| `Astral/vault/Real_one/.obsidian/appearance.json` | `obsidian-vault\Real_one\.obsidian\appearance.json` | LIVE_IDENTICAL |
| `Astral/vault/Topics/AI-Tooling/Claude Code Tooling.md` | `obsidian-vault\Topics\AI-Tooling\Claude Code Tooling.md` | LIVE_DIFFERS |
| `Astral/vault/Topics/AI-Tooling/LLM Wiki Pattern.md` | `obsidian-vault\Topics\AI-Tooling\LLM Wiki Pattern.md` | LIVE_DIFFERS |
| `Astral/vault/Topics/AI-Tooling/Remember System Setup.md` | `obsidian-vault\Topics\AI-Tooling\Remember System Setup.md` | LIVE_DIFFERS |
| `Astral/vault/Topics/Alchemy/144000 & The Chosen One.md` | `obsidian-vault\Topics\Alchemy\144000 & The Chosen One.md` | LIVE_DIFFERS |
| `Astral/vault/Topics/Alchemy/Alchemist Archetype.md` | `obsidian-vault\Topics\Alchemy\Alchemist Archetype.md` | LIVE_DIFFERS |
| `Astral/vault/Topics/HTB/HTB Methodology.md` | `obsidian-vault\Topics\HTB\HTB Methodology.md` | LIVE_DIFFERS |
| `Astral/vault/research/Astral - Design Research 2026.md` | `obsidian-vault\research\Astral - Design Research 2026.md` | LIVE_DIFFERS |
| `Astral/vault/research/Astrology Research Digest - 2026-08-22.md` | `obsidian-vault\research\Astrology Research Digest - 2026-08-22.md` | LIVE_DIFFERS |
| `Astral/vault/sessions/Claude Session 2026-08-12.md` | `obsidian-vault\sessions\Claude Session 2026-08-12.md` | LIVE_DIFFERS |
| `Astral/vault/sessions/Claude Session 2026-08-13.md` | `obsidian-vault\sessions\Claude Session 2026-08-13.md` | LIVE_DIFFERS |
| `Astral/vault/sessions/Claude Session 2026-08-14.md` | `obsidian-vault\sessions\Claude Session 2026-08-14.md` | LIVE_DIFFERS |
| `Astral/vault/sessions/Claude Session 2026-08-15.md` | `obsidian-vault\sessions\Claude Session 2026-08-15.md` | LIVE_DIFFERS |
| `Astral/vault/sessions/Claude Session 2026-08-16.md` | `obsidian-vault\sessions\Claude Session 2026-08-16.md` | LIVE_DIFFERS |
| `Astral/vault/sessions/Claude Session 2026-08-22.md` | `obsidian-vault\sessions\Claude Session 2026-08-22.md` | LIVE_DIFFERS |

## Restoring a single file

```
cd C:\AI
git show "HEAD:<path-under-Astral>" > "C:\AI\obsidian-vault\astral-assets\recovered-src/<path>"
```

`Astral/hermes/profile-default.tar.gz` (14,860,552 bytes, 832 members) is intact and is
the last independent copy of the old Hermes `default` profile.
