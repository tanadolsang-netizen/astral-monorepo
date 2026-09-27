---
source_type: documentation
url: https://code.claude.com/docs/en/plugin-marketplaces
referenced_date: 2026-08-14
synthesized_into: "[[Claude Code Tooling]]"
---

# Raw source: "Create and distribute a plugin marketplace" — official Claude Code docs

**URL:** https://code.claude.com/docs/en/plugin-marketplaces
**Retrieved:** 2026-08-14 via WebFetch.

## What a marketplace is

A catalog (a `marketplace.json` manifest hosted on a git repo, GitHub/GitLab, or local path) that lists plugins and where to find them — provides centralized discovery, version tracking, and automatic updates, vs. installing plugins one-off. Anthropic's own official marketplace (`claude-plugins-official`, referenced in this vault's `CLAUDE.md` re: the disabled `remember` plugin) works the same way: `/plugin install {plugin-name}@claude-plugins-official`.

## Plugin anatomy

A plugin is a directory with a manifest plus one or more of: **skills** (behavior-guiding instructions), **hooks** (lifecycle event handlers — see the separate hooks-reference raw source), **slash commands**, **agents** (custom subagent definitions), **MCP server configs**, and (per this doc) LSP servers.

## Workflow to publish one

1. Build the plugin(s) — skills/agents/hooks/MCP/LSP as needed.
2. Write `marketplace.json` listing them and their source locations.
3. Host it (push to a git remote).
4. Users add it with `/plugin marketplace add <repo>`, then install individual plugins; `/plugin marketplace update` refreshes a user's local copy after the maintainer pushes changes.

Third-party plugins submitted to Anthropic's *official* marketplace go through a quality/security review before inclusion — distinct from anyone hosting their own unofficial marketplace, which requires no approval.

## Relevance to this vault

Fills in the mechanism behind the plugin references already in `CLAUDE.md` and [[Claude Code Tooling]] (`remember@claude-plugins-official`, `pro-workflow`'s `hookify` and commit-validate hooks) — confirms these are ordinary marketplace-distributed plugins (skills + hooks bundled together), not special-cased built-in features, and explains why a plugin's hooks (like `commit-validate`) show up automatically once the plugin is installed rather than needing separate hook configuration.
