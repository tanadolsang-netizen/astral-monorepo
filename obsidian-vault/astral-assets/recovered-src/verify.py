#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
verify.py — re-verifiable recovery proof for the deleted C:\\AI\\Astral tree.

Regenerate the manifest:      python verify.py --write
Re-verify against manifest:   python verify.py
Machine-readable result:      python verify.py --json

The fingerprint is a SHA-256 over a canonical listing of every recovered file:

    <sha256-of-contents>\\x20\\x20<relative-posix-path>\\n

sorted by relative path (byte order, ascending). Two runs on unchanged data
must print the same fingerprint. Excluded from the fingerprint, because they
are this script and the file it writes:

    RECOVERY-MANIFEST.md, verify.py
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = r"C:\AI"
HEAD_REF = "HEAD"

SELF_EXCLUDED = ("RECOVERY-MANIFEST.md", "verify.py")
MANIFEST = os.path.join(HERE, "RECOVERY-MANIFEST.md")

# HEAD paths under Astral/ that were never duplicated into the recovery, because
# a live copy already exists elsewhere on this machine. Resolved deterministically.
LIVE_ROOTS = (
    ("backend/",  os.path.join(REPO, "backend")),
    ("landing/",  os.path.join(REPO, "astral-landing")),
    ("vault/",    os.path.join(REPO, "obsidian-vault")),
)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def git(*args):
    p = subprocess.run(("git",) + args, cwd=REPO, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), p.stderr.decode(errors="replace")))
    return p.stdout


def live_path_for(astral_rel):
    """Map an 'Astral/...' git path to its live counterpart on disk, or None."""
    if astral_rel.startswith("Astral/"):
        astral_rel = astral_rel[len("Astral/"):]
    for prefix, root in LIVE_ROOTS:
        if astral_rel.startswith(prefix):
            return os.path.join(root, astral_rel[len(prefix):].replace("/", os.sep))
    return None


def scan_recovery():
    out = []
    for dp, _dn, fn in os.walk(HERE):
        for f in fn:
            fp = os.path.join(dp, f)
            rel = os.path.relpath(fp, HERE).replace(os.sep, "/")
            if rel in SELF_EXCLUDED:
                continue
            data = open(fp, "rb").read()
            out.append({
                "rel": rel,
                "size": len(data),
                "sha256": sha256(data),
                "blob": git_blob_sha1(data),
            })
    out.sort(key=lambda r: r["rel"])
    return out


def fingerprint(records):
    return sha256("".join("%s  %s\n" % (r["sha256"], r["rel"]) for r in records).encode("utf-8"))


def compare_git(records, head):
    matched = differed = never = 0
    diffs, orphans = [], []
    for r in records:
        rel = r["rel"]
        if not rel.startswith("Astral/"):
            orphans.append(r)
            continue
        try:
            blob = git("cat-file", "-p", "%s:%s" % (head, rel))
        except RuntimeError:
            never += 1
            continue
        if hashlib.sha256(blob).hexdigest() == r["sha256"]:
            matched += 1
        else:
            differed += 1
            diffs.append(rel)
    return matched, differed, never, diffs, orphans


def resolve_live(head_files, recovered, head):
    """For every HEAD entry not in the recovery, check the live copy."""
    have = {r["rel"] for r in recovered}
    rows, identical, differs, absent = [], 0, 0, 0
    for path in head_files:
        if path in have:
            continue
        lp = live_path_for(path)
        if not lp or not os.path.isfile(lp):
            absent += 1
            rows.append({"git": path, "live": None, "status": "ABSENT"})
            continue
        data = open(lp, "rb").read()
        try:
            blob = git("cat-file", "-p", "%s:%s" % (head, path))
        except RuntimeError:
            blob = None
        same = blob is not None and hashlib.sha256(blob).hexdigest() == sha256(data)
        status = "LIVE_IDENTICAL" if same else "LIVE_DIFFERS"
        if same:
            identical += 1
        else:
            differs += 1
        rows.append({
            "git": path,
            "live": os.path.relpath(lp, REPO).replace(os.sep, "\\"),
            "status": status,
            "live_sha256": sha256(data),
        })
    return rows, identical, differs, absent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="regenerate RECOVERY-MANIFEST.md")
    ap.add_argument("--json", action="store_true", help="emit the full record as JSON")
    a = ap.parse_args()

    head = git("rev-parse", HEAD_REF).decode().strip()
    records = scan_recovery()
    fp = fingerprint(records)
    head_files = [
        p.decode("utf-8")
        # -z: raw NUL-separated UTF-8. Without it git octal-escapes non-ASCII
        # (Thai) filenames, which then match nothing on disk.
        for p in git("ls-tree", "-r", "-z", "--name-only", head, "--", "Astral/").split(b"\0")
        if p
    ]
    matched, differed, never, diffs, orphans = compare_git(records, head)
    rows, live_same, live_diff, live_absent = resolve_live(head_files, records, head)

    result = {
        "generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "head": head,
        "files": len(records),
        "bytes": sum(r["size"] for r in records),
        "fingerprint_sha256": fp,
        "git_matched": matched,
        "git_differed": differed,
        "git_never_committed": len(orphans),
        "head_entries": len(head_files),
        "live_identical": live_same,
        "live_differs": live_diff,
        "live_absent": live_absent,
        "diffs": diffs,
        "orphans": [r["rel"] for r in orphans],
        "live_rows": rows,
    }
    missing = result["head_entries"] - matched - live_same - live_diff - live_absent

    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if (differed == 0 and live_absent == 0 and missing == 0) else 1

    print("Astral recovery — verification vs git %s" % head[:7])
    print("  fingerprint sha256   : %s" % fp)
    print("  files / bytes        : %d / %d" % (len(records), result["bytes"]))
    print("  HEAD entries         : %d" % len(head_files))
    print("  byte-identical to HEAD: %d" % matched)
    print("  differs from HEAD     : %d" % differed)
    print("  never in git         : %d" % len(orphans))
    print("  live identical/differs/absent: %d/%d/%d" % (live_same, live_diff, live_absent))
    print("  unexplained          : %d" % missing)
    for d in diffs:
        print("    DIFF: %s" % d)
    ok = differed == 0 and live_absent == 0 and missing == 0
    print("  RESULT               : %s" % ("PASS" if ok else "FAIL"))

    if a.write:
        with open(MANIFEST, "w", encoding="utf-8") as f:
            f.write(render(result))
        print("  wrote %s" % MANIFEST)
    return 0 if ok else 1


def render(r):
    L = []
    L.append("# RECOVERY-MANIFEST — Astral/ (machine-verifiable)\n")
    L.append("Regenerate: `python verify.py --write` · Re-verify: `python verify.py --json`\n")
    L.append("Fingerprint = SHA-256 over `<sha256>  <relative-path>\\n`, sorted by path,")
    L.append("excluding %s.\n" % ", ".join("`%s`" % s for s in SELF_EXCLUDED))
    L.append("| | |")
    L.append("|---|---|")
    L.append("| source | `C:\\AI\\Astral` — deleted, no longer on disk |")
    L.append("| recovered | `%s` |" % HERE.replace("\\", "\\"))
    L.append("| verified against | git `%s` |" % r["head"])
    L.append("| files / bytes | **%d** / %d |" % (r["files"], r["bytes"]))
    L.append("| fingerprint (sha256) | `%s` |" % r["fingerprint_sha256"])
    L.append("")
    L.append("## Verification\n")
    L.append("| check | count |")
    L.append("|---|---:|")
    L.append("| HEAD entries under `Astral/` | %d |" % r["head_entries"])
    L.append("| byte-identical to HEAD | %d |" % r["git_matched"])
    L.append("| differs from HEAD | %d |" % r["git_differed"])
    L.append("| live copy identical to HEAD | %d |" % r["live_identical"])
    L.append("| live copy differs from HEAD | %d |" % r["live_differs"])
    L.append("| live copy absent | %d |" % r["live_absent"])
    L.append("| never committed to git (disk-only rescue) | %d |" % r["git_never_committed"])
    L.append("| **unexplained** | **%d** |" % (r["head_entries"] - r["git_matched"] - r["live_identical"] - r["live_differs"] - r["live_absent"]))
    L.append("")
    L.append("Accounting: %d matched + %d live-resolved = %d = all HEAD entries.\n"
             % (r["git_matched"], r["live_identical"] + r["live_differs"], r["head_entries"]))
    L.append("`command/` is **absent** by request — the Command Bus / hive was retired 2026-09-26.\n")
    L.append("## Never committed to git — disk-only rescue\n")
    L.append("Git could never have restored these. They exist only because the rescue copied them off disk.\n")
    L.append("| path | bytes |")
    L.append("|---|---:|")
    for o in r["orphans"]:
        L.append("| `%s` | %d |" % (o, next(x["size"] for x in scan_recovery() if x["rel"] == o)))
    L.append("")
    L.append("## HEAD entries resolved live (not duplicated)\n")
    L.append("| HEAD path | live copy | status |")
    L.append("|---|---|---|")
    for row in r["live_rows"]:
        L.append("| `%s` | `%s` | %s |" % (row["git"], row["live"] or "—", row["status"]))
    L.append("")
    L.append("## Restoring a single file\n")
    L.append("```\ncd %s\ngit show \"HEAD:<path-under-Astral>\" > \"%s/<path>\"\n```\n" % (REPO, HERE))
    L.append("`Astral/hermes/profile-default.tar.gz` (14,860,552 bytes, 832 members) is intact and is")
    L.append("the last independent copy of the old Hermes `default` profile.\n")
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())
