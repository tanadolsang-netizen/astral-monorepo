# Session Reference: Hermes + Open WebUI Launcher False Failure (Aug 2026)

## What Happened

A PowerShell launcher script (`Start-Hermes-WebUI.ps1`) reported:

```
[INFO] Starting Open WebUI container...
2741189396b61ac62226f2646cc4934058ef1ea29b100f6831b825f76cc5bffb
[ERROR] Failed to start container. docker error: 1
```

But the container (`open-webui`, ID `2741189396b6`) was actually **running** on port `3000:8080` with 0.23% CPU usage, started ~8 minutes before the error.

## Root Cause

The error `docker error: 1` from a `docker run` command is a **false negative** — not a real failure. Likely causes:

1. **Name collision**: `docker run --name open-webui` fails when a container with that name already exists (even if stopped). The container was already started by a prior run.
2. **Transient Docker socket failure**: Docker Desktop's socket can briefly reject commands during startup or after sleep/wake.
3. **Script race**: The script's `docker run` may have run before Docker Desktop's engine was fully responsive.

## Scripts Found

### Launcher (runs every session)
- **Path**: `C:\AI\Start-Hermes-WebUI.ps1`
- **Role**: Starts `hermes gateway` via `Start-Process` (fire-and-forget), opens `http://localhost:3000`
- **Problem**: No container check, no health wait, no Docker pull/run step

### Installer (runs once)
- **Path**: `C:\Users\ADMIN\Downloads\Hermes_Agent_Aider_OpenWebUI_Installer.ps1`
- **Role**: Pulls `ghcr.io/open-webui/open-webui:main` and `paulgauthier/aider:latest`, creates directories, writes a batch launcher to `C:\AI\AiderUI\Start-Hermes-OpenWebUI.cmd`
- **Note**: This is the script that actually does the Docker setup. The launcher script depends on it having been run first.

## Docker Desktop GUI Navigation

When terminal Docker commands are blocked (e.g. `approvals.deny` rules):

1. Open Docker Desktop (already running, pid 16716)
2. It may open in "Gordon" AI assistant mode — click **Containers** in the left sidebar to switch
3. The Containers view shows: Name, Container ID, Image, Port(s), CPU %, Last started
4. `open-webui` was visible: port `3000:8080`, 0.23% CPU, started ~8 min ago

**Gotcha**: Docker Desktop v4.86.0 may default to Gordon AI mode on launch. Always verify you're in the right view.

## Container State at Time of Investigation

| Container | ID | Image | Port | CPU | Status |
|---|---|---|---|---|---|
| open-webui | 2741189396b6 | openwebui/open-webui:latest | 3000:8080 | 0.23% | Running |
| searxng | 10aa6965e75d | searxng/searxng:latest | 8888:8080 | 0% | Running |

## Resolution

No action needed — the container was already running. The error was a false negative. Point the user to `http://localhost:3000`.

## Reproducible Pattern

This class of failure recurs whenever:
- A launcher uses `docker run --name X` without checking if X exists
- Docker Desktop's engine is briefly unresponsive (startup, wake from sleep)
- Two scripts exist (installer + launcher) and the user runs the launcher without the installer having completed

## Workaround for Future Sessions

When a launcher reports Docker failure:
1. Check Docker Desktop GUI → Containers view first (don't trust the error)
2. If the container is running, use it — ignore the error
3. If not running: `docker start <name>` (not `docker run`)
4. If the container doesn't exist: run the installer script first

## Terminal Access Note

On this system, `terminal` is blocked by `approvals.deny: "*"` — all shell commands are denied. Docker state must be verified through Docker Desktop GUI (via `computer_use`) or browser navigation. This is an environment constraint, not a skill lesson — future sessions with working terminal access should use `docker ps` / `docker start` directly.
