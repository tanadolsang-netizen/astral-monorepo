---
name: ollama-local-models
description: "Run local Ollama models in Hermes: pull, config, verify."
version: 1.0.0
author: ox-alpha (curator)
---

# Ollama local models → Hermes binding

Class playbook for running a local model behind Hermes Agent (desktop app / CLI / gateway). Environment of record: Windows host, Ollama at `%LOCALAPPDATA%\Programs\Ollama`, server auto-starts on port 11434, GPU NVIDIA RTX 5060 8 GB.

## Workflow

1. **Sync disk state first** (house rule — sibling sessions mutate the box):
   - `curl -s http://localhost:11434/api/tags` — server alive? which models installed?
   - `nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv` — VRAM budget.
2. **Pull in background, never foreground** — multi-GB pulls blow past foreground timeouts:
   `terminal(command="ollama pull <tag>", background=true, notify_on_complete=true)`
   Reference speed on this line: 7.4 GB ≈ 30 min (~4–5 MB/s). `notify_on_complete` fires exactly once on exit — do NOT poll every turn while waiting; post one progress note, then let the notification resume the work.
3. **Bind with `hermes config set` ONLY** (never hand-edit config.yaml):
   ```
   hermes config set model.provider openai          # Ollama speaks the OpenAI protocol
   hermes config set model.name "<model-tag>"       # e.g. gemma4:12b
   hermes config set model.base_url "http://localhost:11434/v1"
   hermes config set model.api_key ollama           # any non-empty string
   ```
   If the config already points at `localhost:11434/v1` (it has since the qwen days), only `model.name` needs changing.
4. **Verify with a REAL query**, not a config read: `hermes chat -q "..."`.
5. **Replacing a model ⇒ delete the old one**: `ollama rm <old-tag>`. User directive (2026-08-23): superseded local models are removed, not stockpiled (freed ~17 GB deleting two qwen builds when gemma4 arrived). Keep `/api/tags` minimal.

## User preferences (first-class corrections)

- **Do NOT lower `model.context_length` to save VRAM.** Proposed dropping 64K→32K because a 12B Q4 nearly fills the 8 GB card — explicitly overridden by the user (2026-08-23): keep the configured context untouched and let the runtime handle overflow. Only propose VRAM tuning if asked.
- Old models get `ollama rm`'d promptly once a replacement is chosen (see step 5).

## Pitfalls

- `hermes` CLI may be missing from the git-bash PATH: `export PATH="$PATH:/c/Users/ADMIN/AppData/Local/hermes/hermes-agent"` (or invoke `python "$LOCALAPPDATA/hermes/hermes-agent/hermes_cli/main.py"` directly).
- `ollama pull` spams progress lines into process output — read only the tail when polling.
- Model sizes: a `:12b` Q4 tag ≈ 7–8 GB download; check free disk (`df -h /c`) before pulling.

## References

- `references/gemma4-notes.md` — Gemma 4 family quick facts: variants/tags, context lengths, thinking-mode control tokens, sampling defaults, multimodal prompt ordering.
