---
name: session-context-recovery
description: "Recover context from past sessions."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sessions, context, recovery, continuation]
    category: productivity
    related_skills: [session-librarian]
---

# Session Context Recovery

Continue work from a past session when the user asks to resume, pick up where they
left off, or reference a prior conversation by session ID.

## When to Use

- "Continue session <id>"
- "What were the last N sentences from session <id>?"
- "Pick up where we left off in <id>"
- User references an `@session:<profile>/<id>` link
- User wants to recover work context after context compaction
- A prior session is referenced by ID in a follow-up request

## Procedure

1. **Locate the session.** Use `session_search(session_id="<id>", limit=N, offset=0)`
   to retrieve messages. If the session has been compacted, the compaction summary
   is preserved in the session history.

2. **Handle spillover.** Large results (typically >40KB) are saved to spillover files
   under `...\hermes\cache\spillover\call_*.txt`. These files contain the JSON tool
   result but may have trailing non-JSON content (tool-loop warnings, idle markers,
   etc.). Parse with `json.JSONDecoder().raw_decode(raw)` instead of `json.loads(raw)`:
   ```python
   import json
   with open(path, "r", encoding="utf-8") as f:
       raw = f.read()
   decoder = json.JSONDecoder()
   data, _ = decoder.raw_decode(raw)
   ```

3. **Extract messages.** The result structure is:
   - `data["messages"]` — array of message objects
   - Each message has `role`, `content`, `timestamp`, `id`, and optionally `tool_calls`
   - `data["truncated"]` — boolean indicating if messages were truncated
   - `data["message_count"]` — total messages reported by the store

4. **Present the tail.** When the user asks for "last N messages," slice
   `messages[-N:]` and format each with its role, timestamp (human-readable), and
   content preview. Include tool call summaries (function name + truncated args)
   when `content` is empty.

5. **Resume work.** Identify the active task from the tail (the last user message,
   the last assistant action in progress). Report what was happening and ask if the
   user wants to continue or change direction.

## Pitfalls

- **Spillover JSON has trailing content.** `json.loads()` fails with
  "Extra data" on spillover files. Always use `json.JSONDecoder().raw_decode()`.
- **`truncated: true` means the store clipped messages.** If you need deeper
  history, use `session_search` with `around_message_id` to scroll further back.
- **Timestamps are Unix floats.** Convert with
  `datetime.fromtimestamp(ts, tz=ZoneInfo("Asia/Bangkok"))` for display.
- **Tool call contents can be huge.** Show only the first 300-500 chars of tool
  call arguments in summaries; show full args only when the user asks for details.
- **Session titles drift.** A session titled "Continue session X last 20 sentences"
  may contain prior context that predates the title — read the tail to confirm the
  actual topic.

## Verification

- Confirm the session ID matches what the user asked for.
- Verify the message count and truncation status.
- If resuming work, confirm with the user that the identified task is what they
  want to continue.
