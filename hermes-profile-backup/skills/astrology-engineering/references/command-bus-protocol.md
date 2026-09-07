# Multi-session Command Bus Protocol (learned 2026-08-22)

## Dispatch script
- Location: `C:/AI/command/dispatch.py`
- Actions: `board`, `ack`, `report`

## Divisions (codenames chosen by user)
- **FORGE** = backend NEW-AI-REBORN (session 'Genaral', owns port 8000)
- **ATLAS** = engine-specs research (session 'Astrology data and Research Department')
- **ORACLE** = real-chart QA (session 'Fortune telling', this unit)

## Flow
1. `python dispatch.py board` at session start
2. `ack` → do work
3. `report <UNIT> "message"` writes to `command/inbox/<UNIT>.md`

## ORACLE loop
- sync board → check FORGE git/tests → spin up API on **port 8001** → live-fire endpoints → gate results → report back
- Repeat on every FORGE push