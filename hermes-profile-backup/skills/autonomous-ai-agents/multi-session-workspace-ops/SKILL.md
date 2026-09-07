---
name: multi-session-workspace-ops
description: Use when sibling agents share a workspace; sync disk first.
version: 1.0.0
author: ox-alpha
license: MIT
platforms: [windows]
---

# Multi-Session Workspace Operations

Work seamlessly when several Hermes sessions act on the same project tree at
once (this user runs a "CMD session" and others against `C:/AI` permanently).
Your in-context knowledge of files, git state, servers, and ports goes stale
within minutes. The user's standing instruction: **always sync real state from
disk before acting** ("Sync คำสั่งจาก session CMD อยู่ตลอดนะ").

## Sync-before-act checklist

Run these BEFORE any feature work or fix in a shared workspace — batch them in
one terminal call:

1. **Directory census**: `ls` the workspace root. Folders appear/vanish between turns (repos get cloned, vaults get migrated).
2. **Git truth, not memory truth**: `git status --short` + `git log --oneline -5` per repo you care about. Sibling sessions commit YOUR earlier outputs and add uncommitted WIP on top.
3. **Test baseline first**: run the suite *before* changing anything. Failures you find may be a sibling's uncommitted WIP, not your regression — diagnose via `git diff`, never assume the last known-green state still holds.
4. **Port probe**: `curl -s -m 3 http://127.0.0.1:<port>/ready`. Ports are owned per-session (in this environment: 8000 = another session's backend; fall back to 8001+). Never bind a port another session is using; kill only processes YOU started (track your `session_id`s from `terminal(background=true)`).
5. **Read-before-overwrite shared docs/specs**: in folders siblings write to (specs, indexes, README maps), re-read the file immediately before every write/patch. Append or patch anchored on fresh content; never `write_file` a whole shared doc from a stale copy.
6. **Check the command bus** (if present): shared workspaces here use `command/inbox/` (reports FROM units) and `command/outbox/` (task orders TO units, JSON with `status: ACKED/DONE`). Before choosing next work, read inbox reports — a sibling may have finished or contradicted your plan.

## Workspace map discipline

If the root has a `README.md` describing departments/folders/rules, treat it as
authoritative for *who owns what* and re-read it when it changes. In this
environment it encodes: which folder is backend vs specs vs vault, the git-push
state of each, and the port rule. Do not duplicate that map into memory — point
at the file.

## Vault/file migrations mid-session

A sibling session may relocate big trees (e.g. an Obsidian vault) while you work.
During an announced migration: pause writes to that tree entirely, then re-resolve
the new absolute path from disk afterward and update memory. Old paths can linger
as stale copies — verify which copy is the live one (newest mtimes, presence of
recently created notes) before writing.

## Recovering lost subagent/delegate output

When a `delegate_task` batch completes but a child's summary arrives empty,
truncated, or "reasoning-only", the research is usually NOT lost. See
[references/delegation-transcript-recovery.md](references/delegation-transcript-recovery.md)
for the exact cache paths and extraction recipe.

## Cross-machine git handoff hub (same account, different machines)

When the same Hermes account runs on two machines (e.g. home + office) and both
can edit the project tree, use a **git hub repo** as the single source of truth.
This user's `Astral` repo (`github.com/tanadolsang-netizen/Astral`) is that hub —
a monorepo snapshot carrying backend, vault, memory, and Hermes profile.

### sync.sh v2 protocol (already in the repo)

The repo ships `sync.sh` with three concurrent-edit safeguards:

1. **Conflict detection** — `_detect_conflicts()` diffs local working-tree files
   against `origin/main` for the same subtree; if both sides changed the same file,
   `up` aborts with the file list unless `--force` (last-writer-wins) is passed.
2. **Per-machine branch** — each machine works on `machine-<hostname>`; `up`
   commits there, pushes, then fast-forwards `main`. Divergence = manual merge.
3. **Single-writer lock** — `lock`/`unlock` manage `memory/.sync-lock` (1h
   auto-expiry) so MEMORY.md isn't silently clobbered mid-edit.

### Two-machine workflow

Machine A (sender):
```bash
cd Astral
./sync.sh up --commit    # commits backend src, refreshes vault+memory+profile, pushes
```

Machine B (receiver):
```bash
cd Astral
./sync.sh pull           # fetch + fast-forward local to origin/main
./sync.sh apply --yes    # materialize hub's backend/vault/memory into local project dirs
```

### Path handling on Windows (MSYS)

`git -C` and `hermes` need **native Windows paths** (`C:\AI\Astral`); bash tools
(`tar`, `find`, `rm`, `cp`) want **unix paths** (`/c/AI/Astral`). The script keeps
`ASTRAL_DIR_UNIX` for bash and converts via `cygpath -w` at the `git -C` /
`hermes` boundary. If you write a similar script, separate the two path spaces
from the start — mixing them is the #1 silent failure.

### de421.bsp ephemeris

The backend's `de421.bsp` is gitignored in the source repo (too big, ephemeris
data) but is **force-added** in the hub's `backend/` so offline machines can
launch without downloading. When refreshing backend, preserve it *outside* the
backend dir first (temp file), `rm -rf backend/*`, re-archive, then restore —
otherwise it vanishes on the next sync.

## Pitfalls

- **Never trust conversation history for repo/server state after any interruption.** Interrupted turns are exactly when the sibling session did its work.
- Don't `git push` or clean branches you didn't create without checking `git log --all` — siblings coordinate through commits.
- Don't re-run a sibling's half-finished migration or "fix" their WIP by deleting it; finish-or-wait is a user decision unless the user asked you to take over (then say so in your summary).
- Foreground terminal timeout caps at 600s: long installs/builds in a busy workspace → `background=true` + `notify_on_complete=true`, then poll.
- **Cross-machine: always `./sync.sh status` before `up`** — it shows drift, lock state, and conflict risk so you don't push blind into a collision.
