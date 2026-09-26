#!/bin/bash
# hive_check.sh — health probe for the Astrology hive, run every 30m by cron.
# Prints one line per check. Exit 0 = all green, 1 = something degraded.
# NOTE: native Windows binaries need forward-slash native paths (C:/AI/...),
# never MSYS paths (/c/AI/... -> C:\c\AI\...).

OK=0
say() { printf '%s %s\n' "$1" "$2"; [ "$1" = "FAIL" ] && OK=1; return 0; }

# 1. backend venv + test suite presence
if [ -x "C:/AI/backend/.venv/Scripts/python.exe" ]; then
  say "ok  " "backend venv present"
else
  say "FAIL" "backend venv missing at C:/AI/backend/.venv"
fi

# 2. backend health endpoint
if curl -fsS --max-time 10 http://127.0.0.1:8001/health >/dev/null 2>&1; then
  say "ok  " "backend :8001 healthy"
else
  say "WARN" "backend :8001 not responding (may be intentionally stopped)"
fi

# 3. Command Bus board readable
if (cd C:/AI/command && python dispatch.py board >/dev/null 2>&1); then
  say "ok  " "command bus board readable"
else
  say "FAIL" "command bus board unreadable"
fi

# 4. git working tree clean
if [ -z "$(cd C:/AI && git status --porcelain 2>/dev/null)" ]; then
  say "ok  " "C:/AI tree clean"
else
  say "WARN" "C:/AI has uncommitted changes"
fi

# 5. disk headroom
AVAIL_GB=$(df -BG /c 2>/dev/null | awk 'NR==2{gsub("G","",$4); print $4}')
if [ -n "${AVAIL_GB:-}" ] && [ "$AVAIL_GB" -lt 20 ]; then
  say "WARN" "disk headroom low: ${AVAIL_GB}G free"
else
  say "ok  " "disk headroom ${AVAIL_GB:-?}G"
fi

# 6. daily brief still runs
if (cd C:/AI && bash hermes/data/scripts/daily_brief.sh >/dev/null 2>&1); then
  say "ok  " "daily_brief.sh runs"
else
  say "FAIL" "daily_brief.sh failed"
fi

exit $OK
