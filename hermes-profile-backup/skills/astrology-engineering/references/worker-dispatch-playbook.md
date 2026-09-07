# Worker dispatch playbook — Command Bus v2 + delegation lessons (2026-08-23)

Supplements `command-bus-protocol.md` (v1 basics: board/ack/report flow, division codenames).

## Dispatch script v2 (queue-based)
`C:/AI/command/dispatch.py`: `send FORGE "title" "DoD" [high|normal|low]` · `board` · `next FORGE` · `ack FORGE <id-prefix>` (legacy no-id form works) · `done FORGE <id-prefix> "<result>"` · `report ATLAS "..."`. Old codes S1/S2/S3 are aliases. Port map: 8000=other session (never touch), FORGE=8001, ORACLE=8002, others 8003+. Scratch rule #0: temp files NEVER on Desktop → `C:/AI/workspace-scratch/`.

## Delegation survival stats (~10 batches)
~Half of large worker batches die mid-run from API rate limits/timeouts/reasoning-only deaths. What worked repeatedly:
1. **Split small**: 4-spec chunks, not 7; single-file missions beat multi-file ones.
2. **Put the numbers in the brief**: exact formulas/constants/ground-truth values embedded in goal text — workers that must re-derive them die before writing.
3. **Demand literal write-tool usage** in the brief ("use write_file, not just reasoning").
4. **Verify disk truth afterward**: git log + grep for expected strings. A completed status with no bytes on disk = dead worker; write its deliverable yourself immediately.
5. Mark stale queue entries DONE only after disk verification — board reflects reality.

## CMD verification loop (before marking any order done)
git log/status → full pytest run → live curl of changed endpoints via background uvicorn on the division's port → kill server → mark done. Foreground server-start commands are rejected by tooling; always background=true.

## GitHub workflow-scope blocker
Pushing `.github/workflows/*` requires OAuth token with `workflow` scope; plain git push fails with "refusing to allow an OAuth App to create or update workflow". Fix needs interactive user consent: `gh auth refresh -h github.com -s workflow`. Workaround used: commit frontend/code normally, hold ci.yml locally untracked until user completes auth.

## Standing crons
- Watchdog `watch_bus.py` (copies in C:/AI/command/ AND ~/.hermes/scripts/ — cron requires relative filename): stable-output change monitor over queues/inbox/git heads; pause when machine shuts down.
- Daily briefing 06:00: runs `briefing/daily_brief.py`, delivered to this chat (`deliver: origin`). weekly_digest.py also available (--json flag, deterministic).
