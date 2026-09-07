---
name: docker-ai-workspace
description: "Verify Docker containers despite launcher false failures."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [docker, containers, open-webui, ai-workspace, troubleshooting]
    related_skills: [computer-use, systematic-debugging]
---

# Docker AI Workspace

## Overview

AI agent workspaces run backend services in Docker containers with a launcher script. When a launcher reports failure, the container may actually be running — the error is often a transient Docker socket issue or a name-collision false negative.

This skill covers: verifying real container state when scripts report failure, navigating Docker Desktop GUI, launcher script patterns, and two-script confusion.

## When to Use

- A launcher reports "Failed to start container" but you suspect it's already running
- Open WebUI or another web UI isn't loading and you need to check container state
- You need to navigate Docker Desktop to see what's actually running
- You're writing or fixing a launcher script for a Docker-based AI workspace

## Quick Verification Checklist

When a launcher reports failure, verify in this order:

### 1. Check Docker Desktop GUI

Open Docker Desktop → Containers view. Look for the container by name. Check: status (Running?), port mapping (e.g. `3000:8080`), CPU usage (non-zero means active), last started time.

**Gotcha:** Docker Desktop may open in "Gordon" AI assistant mode. Click "Containers" in the left sidebar to switch views.

### 2. Check the browser

Try `http://localhost:3000` (Open WebUI), `http://localhost:11434` (Ollama), etc.

### 3. Understand the error

`docker error: 1` from `docker run` is often: name collision (container already exists), transient Docker socket failure, or image not pulled.

## Launcher Script Patterns

A well-behaved launcher should: check if container exists before creating it, pull images explicitly, wait for services to be ready before opening the browser, handle name collisions gracefully, and print clear status.

### Two-script confusion

Workspaces often have two scripts with different roles:

| Script | Role | When |
|---|---|---|
| **Installer** | Pulls images, creates dirs, writes launcher | One-time setup |
| **Launcher** | Starts containers, opens browser, prints status | Every session |

Don't confuse them. If the launcher fails, check whether the installer was ever run successfully.

### Anti-patterns

- **Fire-and-forget Start-Process**: Starting `hermes gateway` without waiting for readiness means the browser opens before the service is up
- **No container pre-check**: `docker run --name X` without checking if X exists causes spurious failures
- **Opening browser before health check**: User sees connection refused

## Docker Desktop GUI Navigation

### Switching from Gordon AI mode to Containers

If Docker Desktop opens showing the Gordon chat panel: look at the left sidebar (Gordon, Containers, Images, Logs, etc.) and click "Containers". May need foreground delivery on some builds.

### Reading container state

Each row shows: Name (the `--name` value), Container ID (first 12 chars), Image, Port(s) (host:container mapping), CPU %, Last started.

## Troubleshooting Flow

```
Launcher reports failure
         |
         v
1. Open Docker Desktop → Containers view
         |
         v
   Container visible and running?
   /                  \
  YES                  NO
  |                    |
  v                    v
Check browser       1. Check if image pulled
  http://localhost:   (Images view)
  PORT                2. docker start <name>
  |                    3. docker run manually
  v                    (read real error)
  Working?              
  /      \              docker logs <name>
 YES      NO
  |        |
  v        v
Done     Check port mapping / firewall
```

## Related Tools

- **computer-use**: Drive Docker Desktop GUI when terminal Docker access is restricted
- **systematic-debugging**: Apply 4-phase root cause when container genuinely isn't starting
