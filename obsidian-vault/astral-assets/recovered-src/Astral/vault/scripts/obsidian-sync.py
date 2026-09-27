#!/usr/bin/env python3
"""Stop hook: append the latest user+assistant turn to the Obsidian vault.

Reconstructed 2026-08-13 on the company PC — the original script (created
2026-08-12 on the main machine, see "Claude Code Tooling.md" / CLAUDE.md in
the vault) was never committed to the vault repo, so its exact source isn't
recoverable. This is a best-effort rebuild from the documented behavior:
truncate (no LLM call), append to `Claude Session {date}.md`, global hook
covering every project. Silent on success; emits a systemMessage on failure
so a broken hook doesn't fail invisibly.
"""
import json
import sys
from datetime import datetime

VAULT_DIR = r"C:\Users\70098372\Documents\Obsidian Vault"
MAX_CHARS = 4000


def warn(message):
    print(json.dumps({"systemMessage": f"obsidian-sync.py: {message}"}))


def truncate(text):
    text = text.strip()
    if len(text) > MAX_CHARS:
        return text[:MAX_CHARS] + "\n...[truncated]"
    return text


def extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
        return "\n".join(p for p in parts if p)
    return ""


def is_real_user_turn(entry):
    if entry.get("type") != "user":
        return False
    if "toolUseResult" in entry:
        return False
    message = entry.get("message", {})
    if message.get("role") != "user":
        return False
    return bool(extract_text(message.get("content")).strip())


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        warn(f"couldn't read hook input ({e})")
        return

    transcript_path = payload.get("transcript_path")
    session_id = (payload.get("session_id") or "")[:8]
    if not transcript_path:
        warn("no transcript_path in hook input")
        return

    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            lines = [json.loads(line) for line in f if line.strip()]
    except Exception as e:
        warn(f"couldn't read transcript ({e})")
        return

    last_user_idx = None
    for i in range(len(lines) - 1, -1, -1):
        if is_real_user_turn(lines[i]):
            last_user_idx = i
            break
    if last_user_idx is None:
        return

    user_text = extract_text(lines[last_user_idx]["message"].get("content"))

    assistant_parts = []
    for entry in lines[last_user_idx + 1:]:
        if entry.get("type") != "assistant":
            continue
        text = extract_text(entry.get("message", {}).get("content"))
        if text:
            assistant_parts.append(text)
    assistant_text = "\n\n".join(assistant_parts)

    if not user_text and not assistant_text:
        return

    now = datetime.now()
    heading = f"## {now.strftime('%H:%M')} (session {session_id})"
    block = f"\n{heading}\n**User:** {truncate(user_text)}\n\n**Claude:** {truncate(assistant_text)}\n"

    note_path = f"{VAULT_DIR}\\Claude Session {now.strftime('%Y-%m-%d')}.md"
    try:
        try:
            with open(note_path, "r", encoding="utf-8") as f:
                pass
            new_file = False
        except FileNotFoundError:
            new_file = True

        with open(note_path, "a", encoding="utf-8") as f:
            if new_file:
                f.write(f"# Claude Code – สรุปงานวันนี้ ({now.strftime('%Y-%m-%d')})\n")
            f.write(block)
    except Exception as e:
        warn(f"couldn't write note ({e})")
        return


if __name__ == "__main__":
    main()
