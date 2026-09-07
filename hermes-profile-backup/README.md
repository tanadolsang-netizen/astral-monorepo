# Hermes Profile Backup

Astral workspace profile — portable across machines.

## Structure

```
hermes-profile-backup/
├── skills/          # 22 procedural skills (astrology, devops, creative, etc.)
├── memories/        # MEMORY.md + USER.md (persistent memory)
├── cron/            # Scheduled jobs
├── config/          # config.yaml + skills snapshot
├── SOUL.md          # Persona definition
└── restore.sh       # One-click restore script
```

## Restore on new machine

```bash
# Clone monorepo
git clone https://github.com/tanadolsang-netizen/astral-monorepo.git
cd astral-monorepo

# Run restore script (backs up existing profile first)
bash hermes-profile-backup/restore.sh
```

## What's NOT included (sensitive/large)

- `state.db` (185MB session history)
- `.env` (API keys)
- `auth.json` (auth tokens)
- `sessions/` (conversation history)
- `logs/`, `cache/`, `images/` (runtime)

These are machine-specific and should stay local.
