# Astral Monorepo — Architecture

> Version: 2.0 | Updated: 2026-09-22

## Overview

Astral is a full-stack astrology platform with two frontends sharing one backend.

```
astral-monorepo/
├── astral-landing/          # React SPA (Vite)
│   └── astral-app/
│       └── src/
│           ├── App.jsx      # Main router
│           ├── api.js       # API client (fetch wrapper)
│           ├── components/  # 3D scenes (Three.js)
│           └── sections/    # Feature sections
│
├── astral-expo/             # React Native app
│   └── src/
│       ├── screens/         # Screen components
│       ├── components/      # Shared components
│       └── i18n.js          # TH/EN translations
│
├── Astral/
│   └── backend/             # FastAPI (Python)
│       └── src/
│           ├── main.py      # App entry + middleware
│           ├── routers/     # API endpoints (thin wrappers)
│           ├── services/    # Pure computation (no FastAPI)
│           ├── integrations/# External APIs only
│           └── data/        # JSON dictionaries
│
└── STANDARD-PROCEDURE.md    # Pipeline contract + coding standard
```

## Data Flow

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                    │
│                                                      │
│   astral-landing (React)    astral-expo (RN)         │
│        │                          │                  │
│        └──────────┬───────────────┘                  │
│                   ▼                                  │
│         fetch('/api/v1/...')                        │
│         JSON in → JSON out (typed)                   │
└───────────────────┬─────────────────────────────────┘
                    │ HTTP / JSON
                    ▼
┌─────────────────────────────────────────────────────┐
│                   BACKEND LAYER                       │
│                                                      │
│   main.py                                            │
│     ├─ middleware  (auth, rate-limit, CORS)          │
│     ├─ /api/v1/*  ──► routers/                       │
│     │                  ├─ natal.py                   │
│     │                  ├─ transit.py                 │
│     │                  ├─ synastry.py                │
│     │                  ├─ tarot.py                   │
│     │                  ├─ vedic.py                   │
│     │                  ├─ chat.py                    │
│     │                  ├─ payments.py                │
│     │                  └─ reports.py                 │
│     │                                               │
│     ├─ services/        (pure computation)          │
│     │    ├─ ephemeris.py   → planet positions (skyfield)│
│     │    ├─ chart_service.py → natal chart + houses   │
│     │    ├─ aspects.py     → aspect detection         │
│     │    ├─ transit_service.py → transit computation  │
│     │    ├─ fusion_engine.py → multi-system synthesis│
│     │    ├─ rectification.py → birth-time inference  │
│     │    └─ ... (~50 services after consolidation)   │
│     │                                               │
│     ├─ integrations/    (external only)              │
│     │    ├─ supabase_client.py  (auth/users)         │
│     │    └─ stripe_client.py     (payments)          │
│     │                                               │
│     └─ data/            (JSON dicts, no DB)          │
│          ├─ thai_mappings.json                       │
│          ├─ nakshatra.json                           │
│          └─ tarot_deck.json                          │
└─────────────────────────────────────────────────────┘
```

## Design Rules

### 1. Routers are thin
- Parse request → call service → return response
- No business logic in routers
- All computation lives in `services/`

### 2. Services are pure
- No FastAPI imports in services/
- Input: dict/str → Output: dict (standardized)
- Easy to test, easy to move between frameworks

### 3. Integrations are isolated
- Only `integrations/` talks to external APIs
- Functions only — no class hierarchies
- Swap Stripe/Supabase without touching services

### 4. Standard service interface
Every service returns:
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": { "service": "name", "version": "2.0" }
}
```

### 5. No database
- All data in `data/*.json`
- User state in Supabase (auth only)
- Reports computed on-the-fly

### 6. Ephemeris standard
- **Primary:** skyfield (DE421) — no fallback
- Auto-discovers de421.bsp from known locations
- Downloads from NASA mirrors only if no local copy

## API Convention

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/natal` | Generate natal chart |
| POST | `/api/v1/transit` | Transit analysis |
| POST | `/api/v1/synastry` | Relationship compatibility |
| POST | `/api/v1/tarot` | Tarot reading |
| POST | `/api/v1/vedic` | Vedic astrology |
| POST | `/api/v1/chat` | AI chat |
| POST | `/api/v1/payments/checkout` | Stripe checkout |
| GET | `/api/v1/reports/{id}` | Get report |

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend (landing) | React + Vite + Three.js |
| Frontend (mobile) | React Native + Expo |
| Backend | FastAPI + Python 3.11 |
| Auth | Supabase Auth |
| Payments | Stripe |
| Ephemeris | skyfield (DE421) |
| Deployment | Vercel (frontend) + Railway (backend) |

## Service Consolidation (2026-09-22)

### Completed
- Rectification: 3 → 1 (`rectification_tournament.py` + `sa_rectifier.py` merged into `rectification.py`)
- Fusion: 2 → 1 (`fusion_transparency.py` merged into `fusion_engine.py`)

### Result
- Services: 70 → 67 (target: ~50)
- All existing function signatures preserved
- Standardized response format applied

## See Also

- `STANDARD-PROCEDURE.md` — full pipeline contract + coding standard
- `Astral/README.md` — backend-specific documentation
- `research-astrology/` — research papers (01-15)
