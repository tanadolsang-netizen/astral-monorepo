#!/usr/bin/env python3
"""Sync a curated subset of ~/.claude (settings keys + native memory) across
machines via a dedicated private git repo, separate from any project repo.

Usage: claude-config-sync.py pull|push

pull (SessionStart): git pull the sync repo, then merge its settings keys
into the real ~/.claude/settings.json (never touching "hooks" — that's
machine-local, e.g. hardcoded paths/usernames) and copy memory/*.md files
from the sync repo into each project's real memory dir.

push (Stop): mirror the current settings' synced keys and memory files
into the sync repo, commit, and push — no-ops if nothing changed.

Deliberately does NOT touch: hooks, session transcripts, OAuth/credentials,
plugin cache, or anything else under ~/.claude not explicitly listed below.
"""
import json
import os
import shutil
import subprocess
import sys

HOME = os.path.expanduser("~")
CLAUDE_DIR = os.path.join(HOME, ".claude")
SYNC_REPO = os.path.join(HOME, ".claude-config-sync")
REAL_SETTINGS = os.path.join(CLAUDE_DIR, "settings.json")
SYNC_SETTINGS = os.path.join(SYNC_REPO, "settings.sync.json")
REAL_PROJECTS = os.path.join(CLAUDE_DIR, "projects")
SYNC_PROJECTS = os.path.join(SYNC_REPO, "projects")

# Only these top-level settings.json keys are synced. Everything else
# (notably "hooks") is left untouched on each machine.
SYNCED_KEYS = [
    "enabledPlugins",
    "extraKnownMarketplaces",
    "agentPushNotifEnabled",
    "remoteControlAtStartup",
    "language",
    "autoMode",
]


def _run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def _load(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _merge(local, incoming):
    """Merge incoming into local without silently deleting local-only data.
    dict: recursively merge, keys only in `local` are preserved.
    list: union, preserving local's order then appending new incoming items.
    otherwise: incoming wins (scalars are meant to be uniform across machines).
    """
    if isinstance(local, dict) and isinstance(incoming, dict):
        merged = dict(local)
        for k, v in incoming.items():
            merged[k] = _merge(local.get(k), v) if k in local else v
        return merged
    if isinstance(local, list) and isinstance(incoming, list):
        merged = list(local)
        for item in incoming:
            if item not in merged:
                merged.append(item)
        return merged
    return incoming


def _copy_memory_dirs(src_projects, dst_projects):
    if not os.path.isdir(src_projects):
        return
    for slug in os.listdir(src_projects):
        src_mem = os.path.join(src_projects, slug, "memory")
        if not os.path.isdir(src_mem):
            continue
        dst_mem = os.path.join(dst_projects, slug, "memory")
        os.makedirs(dst_mem, exist_ok=True)
        for fname in os.listdir(src_mem):
            if fname.endswith(".md"):
                shutil.copy2(os.path.join(src_mem, fname), os.path.join(dst_mem, fname))


def pull():
    if not os.path.isdir(os.path.join(SYNC_REPO, ".git")):
        print("claude-config-sync: sync repo not found, skipping pull", file=sys.stderr)
        return
    r = _run(["git", "pull", "--ff-only"], cwd=SYNC_REPO)
    if r.returncode != 0:
        print(f"claude-config-sync: pull failed: {r.stderr.strip()}", file=sys.stderr)
        return

    real = _load(REAL_SETTINGS)
    synced = _load(SYNC_SETTINGS)
    for key in SYNCED_KEYS:
        if key in synced:
            real[key] = _merge(real.get(key), synced[key]) if key in real else synced[key]
    _save(REAL_SETTINGS, real)

    _copy_memory_dirs(SYNC_PROJECTS, REAL_PROJECTS)
    print("claude-config-sync: pulled settings + memory")


def push():
    if not os.path.isdir(os.path.join(SYNC_REPO, ".git")):
        print("claude-config-sync: sync repo not found, skipping push", file=sys.stderr)
        return

    real = _load(REAL_SETTINGS)
    synced = {k: real[k] for k in SYNCED_KEYS if k in real}
    _save(SYNC_SETTINGS, synced)

    _copy_memory_dirs(REAL_PROJECTS, SYNC_PROJECTS)

    _run(["git", "add", "-A"], cwd=SYNC_REPO)
    diff = _run(["git", "diff", "--cached", "--quiet"], cwd=SYNC_REPO)
    if diff.returncode == 0:
        return  # nothing changed
    c = _run(["git", "commit", "-m", "sync: update settings/memory"], cwd=SYNC_REPO)
    if c.returncode != 0:
        print(f"claude-config-sync: commit failed: {c.stderr.strip()}", file=sys.stderr)
        return
    r = _run(["git", "push", "-u", "origin", "master"], cwd=SYNC_REPO)
    if r.returncode != 0:
        print(f"claude-config-sync: push failed: {r.stderr.strip()}", file=sys.stderr)
    else:
        print("claude-config-sync: pushed settings + memory")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "pull":
        pull()
    elif mode == "push":
        push()
    else:
        print("usage: claude-config-sync.py pull|push", file=sys.stderr)
        sys.exit(1)
