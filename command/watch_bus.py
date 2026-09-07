#!/usr/bin/env python3
"""Command Bus watchdog — stable-output monitor for cron.

State summary only; identical state -> identical bytes -> silent tick.
Any change (new report, new commit, queue shift, briefing file) changes
the bytes -> triggers the CMD agent run.
"""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path("C:/AI/command")


def git(repo: str, *args) -> str:
    try:
        r = subprocess.run(["git", "-C", repo, *args],
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception as exc:
        return f"ERR {exc}"


def main() -> None:
    lines = []

    # 1) queues (v2 queue file + legacy single-order file)
    for div in ("S1", "S2", "S3"):
        items = []
        qp = ROOT / "outbox" / f"{div}.queue.json"
        legacy = ROOT / "outbox" / f"{div}.json"
        if qp.exists():
            try:
                items = json.loads(qp.read_text(encoding="utf-8"))
            except Exception:
                items = []
        if legacy.exists():
            try:
                one = json.loads(legacy.read_text(encoding="utf-8"))
                if isinstance(one, dict):
                    items = items + [one]
            except Exception:
                pass
        p = sum(1 for t in items if t.get("status") == "PENDING")
        a = sum(1 for t in items if t.get("status") == "ACKED")
        d = sum(1 for t in items if t.get("status") == "DONE")
        lines.append(f"Q {div} pending={p} acked={a} done={d}")

    # 2) inbox digests
    inbox = ROOT / "inbox"
    if inbox.exists():
        for f in sorted(inbox.glob("*.md")):
            h = hashlib.md5(f.read_bytes()).hexdigest()[:8]
            lines.append(f"INBOX {f.name} {h} {f.stat().st_size}")

    # 3) briefing artifact
    b = ROOT / "briefing" / "daily_brief.py"
    lines.append(f"BRIEF exists={b.exists()} size={b.stat().st_size if b.exists() else 0}")

    # 4) repos
    for name, repo in (("FORGE", "C:/AI/NEW-AI-REBORN"),
                       ("ATLAS", "C:/AI/research-astrology"),
                       ("VAULT", "C:/AI/obsidian-vault")):
        head = git(repo, "log", "-1", "--format=%h %s")
        dirty = git(repo, "status", "--short")
        n = len([l for l in dirty.splitlines() if l.strip()])
        head_hash = head.split()[0] if head else "none"
        lines.append(f"GIT {name} head={head_hash} dirty={n}")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
