---
source_type: documentation
url: https://code.claude.com/docs/en/hooks
referenced_date: 2026-08-14
synthesized_into: "[[Claude Code Tooling]]"
---

# Raw source: "Hooks reference" — official Claude Code docs

**URL:** https://code.claude.com/docs/en/hooks
**Retrieved:** 2026-08-14 via WebFetch.

## What hooks are

User-defined shell commands, HTTP endpoints, LLM prompts, or MCP tools that fire automatically at specific points in Claude Code's lifecycle, across every surface (terminal, IDE, Desktop, web) — not a vault-specific or plugin-specific feature.

## Lifecycle events (grouped by cadence)

- **Once per session:** `SessionStart`, `SessionEnd`, `Setup`
- **Once per turn:** `UserPromptSubmit`, `UserPromptExpansion`, `Stop`, `StopFailure`
- **Every tool call:** `PreToolUse` (can block), `PermissionRequest`, `PermissionDenied`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`
- **Other:** file/config change events, compaction events, notification events, subagent/task lifecycle events, MCP elicitation events, worktree events

## Configuration

Defined in JSON at three nesting levels: hook event → matcher group (e.g. "only for Bash tool") → handler(s). Config can live in `~/.claude/settings.json` (all projects, not shareable), `.claude/settings.json` (project, shareable/git-tracked), `.claude/settings.local.json` (project, not shareable), managed org policy settings, a plugin's `hooks/hooks.json`, or skill/agent frontmatter.

Handler types: command (shell, JSON on stdin), HTTP (POST to an endpoint), MCP tool, prompt (single-turn Claude eval), or agent (subagent-based verification, experimental).

## Security notes (directly relevant to how this vault's hooks are set up)

- **No sandbox** — hooks run with full user permissions; a misconfigured hook can delete files or leak secrets. This is exactly the risk the vault's `warn-secrets-in-files` hookify rule is guarding against.
- Exit code 2 blocks the tool call (cannot be overridden by JSON output in most cases); other non-zero codes are non-blocking unless valid JSON supplies a decision; a hook that times out does **not** block.
- `disableAllHooks: true` disables everything at once (temporary escape hatch), but individual hooks can't be selectively disabled — must be removed from config.
- Frontmatter hooks (in skills/subagents) only run after the workspace-trust dialog is accepted for that folder — matches the "Company PC Setup" note's step about accepting the trust prompt on a new machine.

## Relevance to this vault

Grounds [[Claude Code Tooling]]'s mention of `obsidian-sync.py` (a `Stop` hook) and the two `hookify` rules in the actual documented event model and security posture, rather than just the vault's own usage description. Confirms the Stop hook choice is correct for "run once at the end of every turn" (matches the "once per turn" cadence group) and that the "no sandbox" warning is the real reason the `warn-secrets-in-files` rule exists as a safety net rather than a redundant check.
