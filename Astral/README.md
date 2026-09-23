# Astral — Project Handoff (home → office)

Monorepo snapshot for the **same Hermes account**, synced from home machine on **2026-08-31**.
Contains the latest nightly system (2026-08-30/31): premium dark-mystical PDF, StarHeart

## What's in here

| Path | What | Source |
|------|------|--------|
| `backend/` | NEW-AI-REBORN FastAPI backend (full latest state) | `git archive` of home repo — no nested `.git` |
| `vault/` | Obsidian second-brain (notes only, no `.git`/`backups`/`de421.bsp`) | obsidian-vault |
| `memory/MEMORY.md` | Hermes persistent memory (standing orders, project facts) | %LOCALAPPDATA%/hermes/memories |
| `memory/USER.md` | User profile memory | same |
| `hermes/profile-default.tar.gz` | Exported Hermes `default` profile (skills+config+memories+cron) | `hermes profile export default` |
| `SYSTEM-TREE.md` | Directory tree + work-tree setup instructions | — |

## Restore on the office machine (SAME Hermes account)

```bash
# 1. Clone this repo
git clone https://github.com/tanadolsang-netizen/Astral.git
cd Astral

# 2. Import the Hermes profile (keeps skills/config/memories/cron/aliases)
hermes profile import hermes/profile-default.tar.gz
hermes profile use default
#   → restart Hermes desktop so the imported profile loads

# 3. Backend venv (Windows, RTX5060 / Blackwell cu128 torch)
cd backend
uv sync
#   If torch is CPU-only, inside .venv:
#     pip uninstall torch torchvision torchaudio
#     pip install --index-url https://download.pytorch.org/whl/cu128 torch torchvision torchaudio

# 4. Open Astral/vault/ as an Obsidian vault
```

Full detail in `SYSTEM-TREE.md`.

## Sync between machines (one command, both ways)

`Astral` is the HUB. After cloning on a machine, use `sync.sh` instead of copying by hand:

```bash
cd Astral
./sync.sh status    # what would change (drift vs hub)
./sync.sh up        # this machine -> hub  (commit backend src first if needed: ./sync.sh up --commit)
./sync.sh pull      # hub -> this machine
./sync.sh apply     # materialize hub's backend/vault/memory into local project dirs (use --yes to skip prompt)
```

Env overrides (defaults point at home paths): `BACKEND_SRC`, `VAULT_SRC`, `HERMES_MEM`,
`BACKEND_DST`, `VAULT_DST`, `ASTRAL_DIR`. On the office machine just set the `*_SRC`/`*_DST`
to that machine's paths (or clone the standalone repos alongside and let it detect `.git`).

Typical flow home → office:
1. Home: `./sync.sh up --commit`  (commits backend, refreshes vault+memory+profile, pushes)
2. Office: `git clone ...` (first time) then `./sync.sh pull && ./sync.sh apply --yes`

## Standalone repos (their own remotes — clone separately if needed)
- `astral-expo` → github.com/tanadolsang-netizen/astral-expo (Expo frontend)
- `command` → github.com/tanadolsang-netizen/command (Command Bus; FORGE/ATLAS/ORACLE)
- `research-astrology` → specs 01-15

## Standing orders (also in memory/MEMORY.md — must honor)
- Sync REAL disk state before every action; never trust stale context.
- Present exactly 4 clickable options when a decision is needed.
- "Keep top 1%" + "be more than AI" — best-tier deliverables, warm tarot-reader presence.
- Treat user ナイ as all-knowing in astrology/cosmos.
