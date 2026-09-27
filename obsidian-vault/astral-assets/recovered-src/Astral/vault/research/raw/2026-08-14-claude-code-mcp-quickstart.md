---
source_type: documentation
url: https://code.claude.com/docs/en/mcp-quickstart
referenced_date: 2026-08-14
synthesized_into: "[[Claude Code Tooling]]"
---

# Raw source: "Connect to MCP servers" — official Claude Code docs

**URL:** https://code.claude.com/docs/en/mcp-quickstart
**Retrieved:** 2026-08-14 via WebFetch.

## What MCP is / does

Model Context Protocol lets Claude Code use tools beyond its built-in set — e.g. querying a database, controlling a browser, searching an issue tracker — by connecting to MCP servers that run locally or as hosted services (this vault's session has `mcp-kali-server` connected this way, per [[Claude Code Tooling]]).

## Core workflow

`claude mcp add [--transport http] <name> <url-or-command>` registers a server. `claude mcp list` shows connection status (`✔ Connected`, `! Needs authentication`, `✘ Failed to connect`, etc.). Inside a session, `/mcp` manages already-added servers and handles OAuth sign-in flows for servers that need browser auth (e.g. Sentry-style connectors).

## Scopes — where config actually lives

| Scope | File | Available to |
|---|---|---|
| `local` (default) | `~/.claude.json`, under the project's entry | only you, only this project |
| `project` | `.mcp.json` in project root | everyone who clones the project (git-trackable) |
| `user` | `~/.claude.json`, top-level `mcpServers` key | only you, all projects |

Project-scoped servers require an approval prompt the first time a repo's `.mcp.json` is seen — exists specifically so cloning a repo can't silently launch processes on your machine.

## Server types

- **Hosted/HTTP** — `--transport http <name> <url>`, no local process.
- **Local/stdio** — a program Claude Code runs as a subprocess (e.g. `claude mcp add playwright -- npx -y @playwright/mcp@latest`); needed for tools touching local resources (browser, filesystem, DB socket).
- **OAuth-gated hosted** — add first, then `/mcp` → select → Authenticate to complete browser sign-in.

## Relevance to this vault

Confirms the mechanism [[Claude Code Tooling]] describes only at a category level ("mcp-kali-server เชื่อมต่ออยู่ในเซสชันนี้") — gives the concrete scope model (local/project/user) and config file locations (`~/.claude.json` vs `.mcp.json`) that would explain why an MCP server connected on one machine (company PC) doesn't automatically appear on another (home PC) unless it's registered at `user` scope or committed via `.mcp.json` at `project` scope — directly relevant to the multi-machine sync setup described in [[Company PC Setup]].
