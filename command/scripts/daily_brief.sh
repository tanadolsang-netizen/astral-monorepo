#!/bin/bash
# daily_brief.sh — morning brief for Owner & Mai
# NOTE: native Windows python does NOT understand MSYS paths (/c/AI -> C:\c\AI).
# Always pass forward-slash native paths to native binaries: C:/AI/...
# daily_brief.py needs skyfield, which only exists in the backend venv — the
# bare `python` on PATH is Hermes' own 3.14 and cannot import it.
cd C:/AI || exit 1
C:/AI/backend/.venv/Scripts/python.exe "C:/AI/command/briefing/daily_brief.py" 2>&1
