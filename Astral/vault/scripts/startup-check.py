#!/usr/bin/env python3
"""SessionStart verification: reports anything out of sync or missing on
this machine, across both git repos and installed Claude Code plugins.
Runs AFTER the pull hooks (obsidian-sync/claude-config-sync/build-kit-sync)
so it's checking post-pull state.

Silent (prints nothing, exits 0) when everything checks out. Only speaks
up when something needs attention - printed as a systemMessage so it's
visible in the Claude Code UI at session start.

Checks:
1. Each of the 2 known git repos (vault-backup content, and the shared
   "Privacy-" repo's two branches: master for settings/memory, build-kit
   for the Dispatch Console project) for uncommitted changes or a branch
   that's diverged/behind origin.
2. Plugin parity: every plugin declared true in settings.json's
   enabledPlugins is actually present in `claude plugin list`.
"""
import json
import os
import subprocess
import sys

HOME = os.path.expanduser("~")
REPOS = {
    "vault": r"C:\Users\70098372\Documents\Obsidian Vault",
    "claude-config-sync (master)": os.path.join(HOME, ".claude-config-sync"),
    "build_kit (build-kit branch)": os.path.join(HOME, "Desktop", "build_kit"),
}
SETTINGS = os.path.join(HOME, ".claude", "settings.json")


def _run(cmd, cwd):
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def check_repo(name, path):
    problems = []
    if not os.path.isdir(os.path.join(path, ".git")):
        return [f"{name}: not a git repo at {path}"]

    dirty = _run(["git", "status", "--porcelain"], cwd=path)
    if dirty.stdout.strip():
        n = len(dirty.stdout.strip().splitlines())
        problems.append(f"{name}: {n} uncommitted/untracked change(s)")

    _run(["git", "fetch", "--quiet"], cwd=path)
    status = _run(["git", "status", "-sb", "--porcelain=v1"], cwd=path)
    first_line = status.stdout.splitlines()[0] if status.stdout else ""
    if "behind" in first_line:
        problems.append(f"{name}: local branch is behind origin (pull didn't fully catch up)")
    if "ahead" in first_line and "gone" not in first_line:
        # ahead is expected right after a Stop-hook push failure; only flag
        # if there's no upstream at all (diverged tracking)
        pass
    if "gone" in first_line:
        problems.append(f"{name}: upstream branch is gone/misconfigured")

    return problems


def check_plugins():
    if not os.path.exists(SETTINGS):
        return []
    with open(SETTINGS, encoding="utf-8") as f:
        settings = json.load(f)
    expected = [k for k, v in settings.get("enabledPlugins", {}).items() if v]
    if not expected:
        return []

    r = _run(["claude", "plugin", "list"], cwd=HOME)
    installed_output = r.stdout or ""
    missing = [p for p in expected if p not in installed_output]
    if missing:
        return [f"plugin(s) declared but not installed on this machine: {', '.join(missing)} — run `claude plugin install <name>`"]
    return []


def main():
    problems = []
    for name, path in REPOS.items():
        problems += check_repo(name, path)
    problems += check_plugins()

    if problems:
        msg = "Startup check found issues:\n" + "\n".join(f"- {p}" for p in problems)
        print(json.dumps({"systemMessage": msg}))


if __name__ == "__main__":
    main()
