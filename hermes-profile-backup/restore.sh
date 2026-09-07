#!/usr/bin/env bash
# Hermes Profile Restore Script
# Backs up existing profile, then copies backup into place

set -e

HERMES="$LOCALAPPDATA/hermes"
BACKUP_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Hermes Profile Restore ==="
echo "Target: $HERMES"
echo "Backup: $BACKUP_DIR"

# 1. Backup existing profile
if [ -d "$HERMES" ]; then
  TS=$(date +%Y%m%d_%H%M%S)
  echo "[1/4] Backing up current profile to $HERMES.bak.$TS ..."
  cp -r "$HERMES" "$HERMES.bak.$TS"
  echo "      Done — backup at $HERMES.bak.$TS"
else
  echo "[1/4] No existing profile found — skipping backup"
fi

# 2. Create dirs
echo "[2/4] Creating directories..."
mkdir -p "$HERMES/skills" "$HERMES/memories" "$HERMES/cron" "$HERMES/config"

# 3. Copy backup into place
echo "[3/4] Copying profile..."
cp -r "$BACKUP_DIR/skills/"* "$HERMES/skills/" 2>/dev/null || true
cp -r "$BACKUP_DIR/memories/"* "$HERMES/memories/" 2>/dev/null || true
cp -r "$BACKUP_DIR/cron/"* "$HERMES/cron/" 2>/dev/null || true
cp "$BACKUP_DIR/config/"* "$HERMES/" 2>/dev/null || true
cp "$BACKUP_DIR/SOUL.md" "$HERMES/" 2>/dev/null || true

# 4. Verify
echo "[4/4] Verifying..."
SKILLS=$(ls "$HERMES/skills/" 2>/dev/null | wc -l)
MEMORIES=$(ls "$HERMES/memories/" 2>/dev/null | wc -l)
echo "      Skills: $SKILLS"
echo "      Memories: $MEMORIES"

echo ""
echo "=== Restore complete ==="
echo "Start Hermes — your profile is ready."
