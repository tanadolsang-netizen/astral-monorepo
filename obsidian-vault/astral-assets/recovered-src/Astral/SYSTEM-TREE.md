# Astral — System Tree & Work-Tree Instructions

Handoff snapshot for the SAME Hermes account, different machine (office).
Exported 2026-08-31 from home machine. State = "latest nightly system" (2026-08-30/31).

## Directory tree (this repo)

```
Astral/
├── backend/                 # NEW-AI-REBORN — FastAPI backend, premium PDF + starheart + tarot
│   ├── src/services/        #   chart_narrative_full, starheart_*, tarot_*, reel_reading, prediction_log
│   ├── scripts/             #   build_combined_premium.py, build_couple_premium.py, comfy_*, gen_ai_art.py
│   ├── data/prediction_log.json
│   ├── requirements.compiled
│   └── SYSTEM_FLOW.md       #   backend internal flow (already present)
├── vault/                   # Obsidian second-brain (git-pushed notes, no .git/backups/de421.bsp)
│   ├── Astral Project/      #   "State & Decisions" master doc
│   ├── INDEX.md
│   ├── Meta/ Topics/ User/ Real_one/ research/ sessions/
│   └── scripts/ server.py scraper.py
├── memory/
│   └── MEMORY.md            # Hermes persistent memory (durable facts/standing orders)
├── hermes/
│   └── profile-default.tar.gz   # `hermes profile export default` — import on office machine
└── README.md               # this handoff
```

## Other repos (NOT inside this monorepo — they have their own remotes)
These still live at home; clone separately if you need them at the office:
- `astral-expo/`  → github.com/tanadolsang-netizen/astral-expo  (Expo/React frontend)
- `command/`      → github.com/tanadolsang-netizen/command      (Command Bus dispatch.py; FORGE/ATLAS/ORACLE)
- `research-astrology/` → specs 01-15

## Work-tree setup on the office machine (SAME Hermes account)

1. Clone:
   ```
   git clone https://github.com/tanadolsang-netizen/Astral.git
   cd Astral
   ```
2. Restore Hermes profile (keeps skills, config, memories, cron, aliases):
   ```
   hermes profile import hermes/profile-default.tar.gz
   hermes profile use default
   ```
   Then restart Hermes desktop so the imported profile loads.
   (If `import` wants a name, use `default`. Memory file also lands in
    %LOCALAPPDATA%/hermes/memories/MEMORY.md — overwrite if prompted.)
3. Backend venv (Windows, RTX5060 / Blackwell cu128 torch):
   ```
   cd backend
   uv sync                      # or: python -m venv .venv && pip install -r requirements.compiled
   # If torch is CPU-only, inside .venv run:
   #   pip uninstall torch torchvision torchaudio
   #   pip install --index-url https://download.pytorch.org/whl/cu128 torch torchvision torchaudio
   ```
   de421.bsp (ephemeris) is gitignored — backend falls back to bundled `ephe/` or downloads on first run.
4. Obsidian: open `Astral/vault/` as a vault (or copy into your vault folder).

## Standing orders carried in memory/MEMORY.md (must-honor)
- Sync REAL state from disk before every action; never trust stale context.
- Present exactly 4 clickable options when a decision is needed.
- Premium/3D PDF → REAL browser renderer (Playwright headless print, print_background=True)
- "Keep top 1%" + "be more than AI" — every deliverable best-tier; warm tarot-reader presence.
- Treat user ナイ as all-knowing in astrology/cosmos — do not over-explain basics.

## Commit hygiene on this repo
- `backend/` is a snapshot via `git archive` (no nested .git). Do NOT `git init` inside it.
- To refresh backend: re-run `git archive --format=tar HEAD | tar -x -C <Astral>/backend`
  from the home NEW-AI-REBORN after committing there, then commit Astral.
- Large binaries (ai-art, de421.bsp) are intentional; keep them — offline work needs them.
