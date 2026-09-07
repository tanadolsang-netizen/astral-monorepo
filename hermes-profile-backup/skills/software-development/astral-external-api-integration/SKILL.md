---
name: astral-external-api-integration
description: Use when integrating external APIs into the Astral backend.
version: 1.0.0
author: curator
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [astral, api-integration, elevenlabs, fastapi, external-api]
    related_skills: [astral-llm-integration]
---

# Astral External API Integration

Class: integrating external APIs into the Astral astrology backend. Covers the service-layer pattern, chart normalization, and provider-specific quirks.

## Architecture

```
routers/<feature>.py
    ↓
<feature>_service.py (business logic, prompt building)
    ↓
External API (OpenRouter, ElevenLabs, etc.)
    ↓
Response normalization → FastAPI response
```

## Non-negotiable rules

1. **Service layer pattern:** All external API calls go through a dedicated service module in `src/services/`. Never call APIs directly from routers.
2. **Chart format normalization:** Astral charts return `bodies` as a list (not a dict), with sign names in Thai format `พฤษภ(Taurus)`. Always normalize before processing:
   - Use `absolute_deg` for longitude (not `degree`)
   - Parse sign names with regex: `\(([A-Za-z]+)\)` to extract English name
   - `ascendant` and `midheaven` are separate top-level keys, not in `bodies`
3. **API key via env var:** All external API keys are read from environment variables. Never hardcode. Return structured error `{status: "missing_api_key"}` if not configured.
4. **Preview mode:** Endpoints should support a `generate` flag (default false) that returns the prompt/preview without calling the paid API.
5. **Timeout handling:** External APIs can be slow (30-120s). Use appropriate timeouts and return structured errors on timeout.
6. **Never log or expose API keys** in error responses or logs.

## Chart normalization

Astral charts from `compute_chart()` have this structure:

```python
{
    "name": str,
    "datetime_utc": str,
    "system": str,
    "bodies": [
        {
            "body": "Sun",
            "sign": "พฤษภ(Taurus)",  # Thai(English)
            "degree": 28.0568,        # Within sign
            "absolute_deg": 58.0568,  # 0-360 ecliptic longitude
            "house": 1,
            "dignity": {...}
        },
        ...
    ],
    "ascendant": {"body": "ASC", "absolute_deg": 55.9653, ...},
    "midheaven": {"body": "MC", "absolute_deg": 316.4291, ...},
    "houses": {"cusps": [...], ...}
}
```

Normalization steps:
1. Extract `absolute_deg` for longitude
2. Parse English sign name from parentheses
3. Build a `planets` dict for easier access
4. Add ASC and MC as synthetic planets

## File map

| File | Role |
|------|------|
| `src/services/llm_service.py` | OpenRouter LLM client (see `astral-llm-integration`) |

> **Note:** Astro Music feature (`astro_music_service.py`, `astro_music.py`) was built and then reverted on 2026-09-06 after user reversal. If revived, create fresh files following the patterns below.

## Provider selection & API key portability

**Music generation providers are NOT API-key-portable.** A key from one provider does NOT work on another:

| Provider | Endpoint | Key prefix | Notes |
|----------|----------|------------|-------|
| SunoAPI | `api.sunoapi.org/api/v1/generate` | `sh_...` | Requires `callBackUrl`; credits-based |
| Kie.ai / MusicHero | `api.kie.ai/api/v1/generate` | — | 5,000 free credits on signup; no credit card |
| ElevenLabs | `api.elevenlabs.io/v1/music/compose` | `xi-...` | Binary audio response; paid |

**Rule:** Always verify the key belongs to the provider you're calling. A 401/429 may mean wrong provider, not bad key.

## Feature development workflow

**Validate direction before building.** For novel features that expand system scope (music, video, new integrations):

1. Present a 1-page design: endpoints, data mapping, cost model, API key requirements
2. Get explicit user approval BEFORE writing service + router + tests
3. Build incrementally: service first → verify → router → verify → register
4. If user reverses: delete service + router + unregister from main.py + clear `__pycache__`

Building fully then reversing wastes a session and leaves dead code to clean up.

## References

- `references/elevenlabs-music-api.md` — ElevenLabs Music API specifics, prompt format, mapping tables