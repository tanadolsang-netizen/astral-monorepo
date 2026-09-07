---
name: warn-pii-in-memory-files
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.remember/.*\.md$
  - field: content
    operator: regex_match
    pattern: '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
action: warn
---

⚠️ **Email address detected in a `.remember/` memory file**

These files (especially `identity.md`) are injected into every session and may end up git-tracked.

Confirm the user actually wants this personal info stored here before continuing — especially if this vault's remote could ever be public.

(Added 2026-08-12 after an email address was found in `.remember/identity.md` right as `.gitignore` was changed to start tracking that folder.)
