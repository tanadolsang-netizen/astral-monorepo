---
name: warn-secrets-in-files
enabled: true
event: file
conditions:
  - field: content
    operator: regex_match
    pattern: -{5}BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-{5}|ghp_[A-Za-z0-9]{30,}|gho_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}
action: warn
---

⚠️ **Secret-like pattern detected in file content**

This write matches a known secret format (private key header, GitHub token, AWS access key, or similar API key pattern).

**Before proceeding:**
- Confirm this file should actually contain a live credential.
- If it will be git-tracked, make sure it's covered by `.gitignore` — or that this is intentional and the repo is private/trusted.
- Prefer environment variables or a secrets manager over hardcoding.

(Added 2026-08-12 after a private-key/API-key near-miss during the vault's first `git commit`.)
