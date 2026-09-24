#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-D:/AI/NEW-AI-REBORN}"
HERMES_PROFILES="${LOCALAPPDATA:-C:/Users/70098372/AppData/Local}/hermes/profiles"
mkdir -p "$HERMES_PROFILES"
if [ -f "$REPO/.data/profiles/m.json" ]; then
  cp -f "$REPO/.data/profiles/m.json" "$HERMES_PROFILES/m.json"
  echo "Imported Hermes profile from repo: m.json"
else
  echo "No profile found at $REPO/.data/profiles/m.json"
fi
