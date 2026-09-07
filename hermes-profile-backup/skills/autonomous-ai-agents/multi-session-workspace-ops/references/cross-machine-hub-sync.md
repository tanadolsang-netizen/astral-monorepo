# Cross-Machine Git Hub Sync

Astral sync v2 pattern for same Hermes account across multiple machines.

## Hub repo structure (`github.com/tanadolsang-netizen/Astral`)

```
Astral/
├── backend/                 # NEW-AI-REBORN snapshot (git archive, no nested .git)
├── vault/                   # Obsidian second-brain (excl .git/backups/de421.bsp)
├── memory/                  # Hermes MEMORY.md + USER.md + .sync-lock
├── hermes/                  # profile-default.tar.gz (hermes profile export)
├── sync.sh                 # sync tool (v2)
├── SYSTEM-TREE.md           # tree + work-tree instructions
└── README.md                # handoff + sync workflow
```

## sync.sh commands

| Command | Purpose | Flags |
|---------|---------|-------|
| `status` | drift report: uncommitted files, lock state, branch list, conflict risk | — |
| `up` | this machine → hub (commit backend src, refresh vault+memory+profile, push) | `--commit` auto-commit uncommitted backend src; `--force` push even if conflict |
| `pull` | hub → local Astral clone (fast-forward) | — |
| `apply` | materialize hub's backend/vault/memory into local project dirs | `--yes` skip confirmation |
| `lock` | acquire single-writer lock on MEMORY.md | — |
| `unlock` | release lock | — |

## Workflow: home → office

```bash
# Home machine
cd Astral
./sync.sh status         # check drift + no conflicts
./sync.sh up --commit    # commits backend src, refreshes vault+memory+profile, pushes

# Office machine
cd Astral
./sync.sh pull           # fetch + fast-forward local to origin/main
./sync.sh apply --yes    # materialize hub's backend/vault/memory into local project dirs
hermes profile import hermes/profile-default.tar.gz
hermes profile use default   # then restart Hermes desktop
```

## Workflow: 2 machines concurrent (both editing)

1. Machine A: `./sync.sh status` → `./sync.sh up --commit`
2. Machine B: `./sync.sh pull` (gets A's changes) → `./sync.sh apply --yes`
3. If both machines edited the **same files** → conflict detection aborts `up` with file list → resolve manually or use `--force` (last-writer-wins)

## Conflict detection logic

`_detect_conflicts()` compares local working-tree files against `origin/main`:
- Extract hub subtree to temp: `git archive origin/main <subdir>` → tar to tmp
- For each local file: if hub version exists AND differs → conflict
- Deletions NOT detected (file in hub but not local = no conflict flag)

## Single-writer lock (.sync-lock)

```
machine-desktop-inq7mup
1710000000
```

- Line 1: machine ID (hostname, sanitized)
- Line 2: epoch timestamp
- Auto-expires after 1 hour (LOCK_TIMEOUT=3600)
- `lock` creates + `git add -f`
- `unlock` removes + `git rm --cached`

## Windows path handling (MSYS gotcha)

`git -C` and `hermes` need **native Windows paths** (`C:\AI\Astral`) — MSYS path `/c/AI/Astral` fails silently with "cannot change to".

Bash tools (`tar`, `find`, `rm`, `cp`, `mkdir`) need **unix paths** (`/c/AI/Astral`).

Solution: keep `ASTRAL_DIR_UNIX` for bash tools; wrap git with:
```bash
# in sync.sh
native_dir="$(cygpath -w "$ASTRAL_DIR_UNIX")"
git -C "$native_dir" ...
```

## de421.bsp ephemeris preservation

- Gitignored in source repo (`NEW-AI-REBORN/`)
- Force-added in hub's `backend/` for offline launch
- **Preservation pattern**: copy to temp OUTSIDE backend dir → `rm -rf backend/*` → re-archive → restore → `git add -f backend/de421.bsp`
- If you forget, it vanishes on next sync and offline launch fails

## Typical new-machine setup

```bash
git clone https://github.com/tanadolsang-netizen/Astral.git
cd Astral
hermes profile import hermes/profile-default.tarmes
hermes profile use default   # restart Hermes desktop
cd backend
uv sync                      # ComfyUI: never `comfy install` in venv (CPU torch bug)
# If torch is CPU-only: pip uninstall torch torchvision torchaudio
#   then: pip install --index-url https://download.pytorch.org/whl/cu128 torch torchvision torchaudio
```

## Integration with Command Bus

This pattern complements (does not replace) the Command Bus (`C:/AI/command/dispatch.py`). Command Bus coordinates sibling sessions on the SAME machine; Astral hub sync coordinates DIFFERENT machines.

When both are active:
- Same-machine siblings: use Command Bus inbox/outbox
- Cross-machine: use Astral hub sync
- Always sync disk state before acting (standing order)
