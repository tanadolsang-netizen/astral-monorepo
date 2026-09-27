---
source_type: article
url: https://www.steeman.be/posts/syncing-claude-code-across-multiple-machines/
referenced_date: 2026-08-14
synthesized_into: "[[Company PC Setup]]"
---

# Raw source: "Syncing Claude Code Across Multiple Machines" — steeman.be

**URL:** https://www.steeman.be/posts/syncing-claude-code-across-multiple-machines/
**Retrieved:** 2026-08-14 via WebFetch.

## Approach described

A three-layer hybrid strategy for keeping a Claude Code + VSCode setup consistent across several machines:
- **NAS + symlinks** for settings, custom commands, skills, plugins, and project *configuration* — anything meant to be identical everywhere.
- **Syncthing (peer-to-peer)** for full project directories, including uncommitted/staged changes that git wouldn't capture — ~253,000 files across 30 projects in the author's case.
- **Machine-local only, never synced**: session history, cache, credentials — files that are inherently tied to one machine's state.

## Notable design choice

Splits changelog entries into machine-specific ("set up Samba on this box") vs. project-related — the former stays local, the latter travels with the code. Explicitly frames this as recognizing that work context differs by machine, not everything belongs in one shared timeline.

## Gotchas called out

NAS dependency (lose the sync if the network share is down), `.sync-conflict` files from simultaneous edits requiring manual resolution, plaintext API keys sitting on the NAS being a real risk, and absolute-path assumptions in plugins breaking if usernames differ across machines.

## Relevance to this vault

A different (heavier) approach to the same underlying problem [[Company PC Setup]] and `CLAUDE.md`'s "Auto-sync across machines" section solve more simply: this vault uses plain git (SessionStart pull, Stop push) for the *vault content itself*, not `~/.claude/` config. The article's approach is solving a broader problem (syncing the whole Claude Code environment — settings, skills, plugins, in-flight project state — not just one vault's markdown), which this vault doesn't currently need since its two machines already use the same global plugin/settings config independently. Worth flagging one gotcha that *does* apply directly: the article's "absolute path assumptions in plugins break if usernames differ across machines" is exactly the situation here (`Admin` on the home PC vs. `70098372` on the company PC, per [[Company PC Setup]]) — the vault's existing fix (the desktop-shortcut PowerShell script using `$env:USERPROFILE`/`$env:LOCALAPPDATA` instead of hardcoded paths) is already the correct mitigation this source independently arrives at.
