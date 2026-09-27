#!/usr/bin/env python3
"""Sync ~/.omniroute (OmniRoute's local server data: .env with
STORAGE_ENCRYPTION_KEY + storage.sqlite) across machines via the
`omniroute` branch of the same private repo used for claude-config-sync
and build-kit-sync (https://github.com/tanadolsang-netizen/Privacy-.git) -
a separate branch so it never mixes with those repos' content.

~/.omniroute is turned into its own git repo in place (like build_kit),
scoped by a .gitignore that excludes everything except .env and
storage.sqlite (db_backups/, logs/, server/, and the *.sqlite-wal/-shm
journal files are machine-local/transient and never synced).

Before every push, checkpoints the WAL into the main storage.sqlite file
(sqlite3 stdlib, PRAGMA wal_checkpoint(TRUNCATE)) so the synced file is
self-consistent without needing the -wal/-shm files.

Usage: omniroute-sync.py pull|push
"""
import os
import sqlite3
import subprocess
import sys

REPO = os.path.join(os.path.expanduser("~"), ".omniroute")
DB = os.path.join(REPO, "storage.sqlite")

GITIGNORE = """\
*
!.gitignore
!.env
!storage.sqlite
"""


def _run(cmd):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)


def _ensure_gitignore():
    path = os.path.join(REPO, ".gitignore")
    if not os.path.exists(path) or open(path, encoding="utf-8").read() != GITIGNORE:
        with open(path, "w", encoding="utf-8") as f:
            f.write(GITIGNORE)


def _checkpoint_wal():
    if not os.path.exists(DB):
        return
    try:
        conn = sqlite3.connect(DB, timeout=5)
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.close()
    except sqlite3.Error as e:
        print(f"omniroute-sync: WAL checkpoint skipped: {e}", file=sys.stderr)


def pull():
    if not os.path.isdir(os.path.join(REPO, ".git")):
        print("omniroute-sync: repo not found, skipping pull", file=sys.stderr)
        return
    r = _run(["git", "pull", "--ff-only", "origin", "omniroute"])
    if r.returncode != 0:
        print(f"omniroute-sync: pull failed: {r.stderr.strip()}", file=sys.stderr)
    else:
        print("omniroute-sync: pulled")


def push():
    if not os.path.isdir(os.path.join(REPO, ".git")):
        print("omniroute-sync: repo not found, skipping push", file=sys.stderr)
        return
    _ensure_gitignore()
    _checkpoint_wal()
    _run(["git", "add", "-A"])
    diff = _run(["git", "diff", "--cached", "--quiet"])
    if diff.returncode == 0:
        return  # nothing changed
    c = _run(["git", "commit", "-m", "sync: update omniroute data"])
    if c.returncode != 0:
        print(f"omniroute-sync: commit failed: {c.stderr.strip()}", file=sys.stderr)
        return
    r = _run(["git", "push", "origin", "HEAD:omniroute"])
    if r.returncode != 0:
        print(f"omniroute-sync: push failed: {r.stderr.strip()}", file=sys.stderr)
    else:
        print("omniroute-sync: pushed")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "pull":
        pull()
    elif mode == "push":
        push()
    else:
        print("usage: omniroute-sync.py pull|push", file=sys.stderr)
        sys.exit(1)
