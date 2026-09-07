---
name: multi-session-command-ops
description: Use at session start to sync orders via Command Bus.
version: 1.0.0
author: ox-alpha (curator)
---

# Multi-session command ops

Standing user instruction (first-class): **"Sync คำสั่งจาก session CMD อยู่ตลอด"** — always re-sync orders and state from the coordinating session before working. Several sessions share one workspace and mutate it concurrently.

## Protocol (every work block)
1. `python C:/AI/command/dispatch.py board` — open orders + division statuses. Units accept both new names (FORGE/ATLAS/ORACLE) and legacy S1/S2/S3.
2. Queue v2: `send` appends to `outbox/<UNIT>.queue.json` (timestamp id + priority) — multiple orders per unit supported (the old single-slot file silently overwrote pending orders). Accept/work/report: `ack <UNIT> [id-prefix]` → work → `done <UNIT> <id-prefix> "<result>"` (appends result to `inbox/<UNIT>.md`). Bare `ack FORGE` (legacy, no id) still works — takes oldest PENDING and migrates a legacy single-order file if present. `next <UNIT>` prints your oldest PENDING order as JSON.
3. Mark `done` immediately when work actually lands — leftover ACKED/PENDING rows made CMD re-inspect finished work the next morning. Board must match disk/git reality.
3. Re-verify disk state (git status, ls, mtimes) IMMEDIATELY before acting — sibling sessions change files/git/processes between your turns; stale context caused real double-writes (spec files edited by two agents at once).
4. A write-tool warning "file modified by sibling subagent/session" = read the file before overwriting; never blind-write.

## Division map (as run by the user)
- **CMD 👑** — coordinator chat; issues orders, arbitrates spec ambiguity (e.g. undefined tarot tilt-basis).
- **FORGE 🔨** (session 'Genaral') — engineering: NEW-AI-REBORN backend; owns git commits and port 8000.
- **ATLAS 🗺️** (session 'Astrology data and Research Department') — engine-spec canon at `C:/AI/research-astrology/`.
- **ORACLE** (session 'Fortune telling'; S3 alias OK) — real-chart QA / acceptance gates; combat reports at `C:/AI/research-astrology/S3-report-*.md`.
Commanding rule from CMD: specs are contracts code must obey; every phase passes real-chart verification before "done".

## CMD role boundary (user directive, first-class)
When this chat IS the coordinating session (CMD): it does NOT do division work itself — no editing division code/specs, no fixing sibling code. Its loop is exactly: dispatch orders → verify reports on disk/git → summarize. When the user says "ลุย" for division work, spawn `delegate_task` workers acting as that division (brief them with the bus protocol + port rules), never patch files as CMD. One real incident: CMD reverted a sibling's mid-edit chart_service.py patch and destroyed in-flight work; another time CMD and FORGE edited bazi_service.py concurrently. Also: `state/S1..S3.md` files hold each unit's current work/files-touched/prohibitions — read before dispatching anything overlapping.

## Conventions
- Port allocation is per-unit and stated inside every order brief: 8000 = FORGE's live server, FORGE workers use 8001, ORACLE uses 8002, ad-hoc CMD checks use 8003. A worker starting on an occupied port silently serves stale code — always put the port rule in delegation briefs.
- SEREP report format (user-requested standing summary shape): per division, five rows — **S** สถานะ (status) / **E** Evidence (commits, test counts, file paths) / **R** ควรทำต่อ / **E** เหตุผล (why it matters) / **P** Priority 🔺สูง 🔸กลาง 🔹ต่ำ. User asking for "S E R A P"/"SEREP"/"รายงาน" means this exact shape.
- `gh` CLI is installed but NOT on the default bash PATH — `export PATH="$PATH:/c/Program Files/GitHub CLI"`. It is already authed as tanadolsang-netizen; check existing repos with `gh repo list tanadolsang-netizen` before assuming "Repository not found" means you must create one.
- Project test gates: `cd C:/AI/NEW-AI-REBORN && ./.venv/Scripts/python.exe -m pytest -q` — the project venv carries the deps; the system interpreter does not.
- Reports carry root causes + an ordered fix list with file:line, not just pass/fail counts.
- Address the user as ท่าน/Sir with polished, concise status reporting (JARVIS-style) — in chat and in formal reports alike.

## Pitfalls
- **`dispatch.py send` QUEUES but does NOT EXECUTE.** It only appends an order to `outbox/<UNIT>.queue.json` — it never spawns a worker session. A queued order with no active agent shows "ทำอยู่ 0" on the board and produces **no files**. This bit hard this session: orders were dispatched via the bus, the board looked busy, but nothing ran and the user said "ไม่เห็น agent เลย" (don't see any agent). To actually get work done, SPAWN via `delegate_task` briefed as that division (FORGE/ATLAS/ORACLE) — the bus is for order tracking, `delegate_task` is for execution. Use the bus `board`/`done`/`report` to track, but spawn the doer separately.
- Even when acting as CMD, prefer `delegate_task` over hand-patching: one real incident was CMD overwriting a sibling's in-flight `chart_service.py` patch.

## References
- `references/p0-gate-report-example.md` — worked example of an ORACLE acceptance-gate report (root causes, file:line fix list).
