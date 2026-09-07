---
name: astral-llm-integration
description: Use when integrating LLM features into the Astral backend.
version: 1.0.0
author: curator
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [llm, openrouter, deepseek, hermes-memory, fastapi, astral]
    related_skills: []
---

# Astral LLM Integration

Class: integrating LLM features into the Astral astrology backend. Covers the OpenRouter API client, DeepSeek-R1 response quirks, and Hermes memory context injection.

## Architecture

```
routers/chat.py
    ↓
astro_chat_service.py (system prompt, provider status)
    ↓
llm_service.py ← SINGLE SOURCE OF TRUTH for all LLM calls
    ↓
OpenRouter API → DeepSeek-R1
    ↓
hermes_memory_service.py (context injection)
    ↓
C:\Users\ADMIN\AppData\Local\hermes\memories\
```

## Non-negotiable rules

1. **Single source of truth:** All LLM calls go through `src/services/llm_service.py`. Never call OpenRouter API directly from routers or other services.
2. **DeepSeek-R1 reasoning field:** When the model is thinking or content is null, the response puts text in `message["reasoning"]` instead of `message["content"]`. Always fall back:
   ```python
   reply = message.get("content") or message.get("reasoning") or ""
   ```
3. **Reasoning consumes tokens rapidly.** Set `max_tokens` generously (1000+) for narrative generation.
4. **Hermes memory path:** `C:\Users\ADMIN\AppData\Local\hermes` (verified). Do not hardcode alternative paths.
5. **Memory as context:** Hermes memory entries are injected as system messages before the conversation. Read both `memory` and `user` targets.
6. **Env var:** `OPENROUTER_API_KEY` must be set in `render.yaml` for production. Without it, `llm_service.use_api` is False and all calls return None.
6. **Model:** `deepseek/deepseek-r1` via `https://openrouter.ai/api/v1/chat/completions`.
7. **Temperature:** 0.7-0.8 works well for astrology narratives.
8. **Never log or expose API keys** in error responses or logs.
9. **Chart format:** Astral charts return `bodies` as a list (not dict), sign names in Thai format `พฤษภ(Taurus)`, and `ascendant`/`midheaven` as top-level keys. Use `absolute_deg` for 0-360 longitude. See `astral-external-api-integration` for the normalization pattern.

## Related skills

- `astral-external-api-integration` — service-layer pattern for all external APIs, chart normalization rules

## File map

| File | Role |
|------|------|
| `src/services/llm_service.py` | OpenRouter client, single source of truth |
| `src/services/hermes_memory_service.py` | Memory read/write |
| `src/services/astro_chat_service.py` | System prompt, provider status, delegates to llm_service |
| `src/routers/chat.py` | Chat endpoint |
| `render.yaml` | Env var `OPENROUTER_API_KEY` |

## Setup checklist

- [ ] `OPENROUTER_API_KEY` set in `render.yaml` (production) or .env (local)
- [ ] `llm_service.use_api` returns True (verify with health check)
- [ ] Hermes memory directory exists at `C:\Users\ADMIN\AppData\Local\hermes\memories\`
- [ ] Test: call `llm_service.generate("test")` → should return string, not None

## Common pitfalls

- **content=null with reasoning populated:** DeepSeek-R1 returns reasoning separately. Always use the fallback pattern above.
- **max_tokens too low:** R1 reasoning eats tokens. Below 500, you get truncated or null content.
- **Hermes path drift:** If someone changes the Hermes install location, `hermes_memory_service.py` path must be updated. Currently hardcoded to `C:\Users\ADMIN\AppData\Local\hermes`.
- **Missing env var:** In local dev without `OPENROUTER_API_KEY`, LLM silently returns None. Always check `llm_service.use_api` first.

## Migration history

- Previous: Hugging Face Inference API (DeepSeek V4) — replaced due to reliability.
- Earlier: Multi-provider system (custom/Groq/OpenRouter) in `astro_chat_service.py` — simplified to OpenRouter-only.
- Hermes path was `D:\AI\AOS\hermes` (wrong) → fixed to `C:\Users\ADMIN\AppData\Local\hermes`.
