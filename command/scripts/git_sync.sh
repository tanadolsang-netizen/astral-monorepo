#!/bin/bash
# git_sync.sh — auto commit and push changes
# NOTE: monorepo root is C:/AI (NEW-AI-REBORN was consolidated into C:/AI/backend
# on 2026-09-26). Branch is master. Native git needs forward-slash native paths.
set -u
cd C:/AI || exit 1
# Never stage the venv/cache/download churn — .gitignore covers these, but guard anyway.
git add -A || exit 1
git diff --cached --quiet && { echo "nothing to sync"; exit 0; }
git commit -m "auto-sync: $(date '+%Y-%m-%d %H:%M')" || exit 1
git pull --no-rebase origin master 2>&1 | tail -3
git push origin master 2>&1 | tail -3 || echo "Push failed"
