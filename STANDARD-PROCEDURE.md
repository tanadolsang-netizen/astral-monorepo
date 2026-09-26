# Astral Backend — Standard Procedure & Pipeline Contract

> Version: 2.0 | Updated: 2026-09-22
> Source of truth: `astral-monorepo/STANDARD-PROCEDURE.md`

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND LAYER                          │
│  astral-landing (React + Vite)    astral-expo (React Native)│
│         │                                │                  │
│         └──────────────┬─────────────────┘                  │
│                        ▼                                    │
│              fetch('/v1/...', { method, body })             │
│              JSON in → JSON out (typed)                     │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP / JSON
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND LAYER                           │
│                                                             │
│  main.py (FastAPI app factory)                              │
│    ├─ middleware: CORS, auth, rate-limit, request-id        │
│    ├─ /v1/* ──► routers/  (thin: parse → call → return)    │
│    │              ├─ natal.py, transit.py, synastry.py      │
│    │              ├─ vedic.py, bazi.py, chinese.py          │
│    │              ├─ tarot.py, horary.py, western.py        │
│    │              ├─ fusion.py, new_engines.py, reports.py   │
│    │              └─ payments.py, auth.py, chat.py           │
│    │                                                        │
│    ├─ services/       (pure computation, no FastAPI)        │
│    │    ├─ ephemeris.py        → planet positions           │
│    │    ├─ chart_service.py    → natal chart + houses       │
│    │    ├─ aspects.py          → aspect detection            │
│    │    ├─ transit_service.py  → transit computation         │
│    │    ├─ fusion_engine.py    → multi-system synthesis     │
│    │    ├─ rectification.py    → birth-time inference       │
│    │    └─ ... (70 services total)                          │
│    │                                                        │
│    ├─ integrations/   (external APIs only)                  │
│    │    ├─ supabase_client.py  (auth/users)                  │
│    │    └─ stripe_client.py     (payments)                  │
│    │                                                        │
│    └─ data/           (JSON dictionaries, no DB)            │
│         ├─ thai_mappings.json                               │
│         ├─ nakshatra.json                                   │
│         └─ tarot_deck.json                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Three-Layer Contract

### Rule 1: Routers are THIN

```python
# ✅ CORRECT — router is a thin wrapper
@router.post("/natal")
async def natal_endpoint(req: NatalRequest):
    result = compute_natal_chart(req.dict())  # all logic in service
    return result

# ❌ WRONG — business logic in router
@router.post("/natal")
async def natal_endpoint(req: NatalRequest):
    dt = parse_datetime(req.date, req.time, req.tz)
    t = ts.from_datetime(dt)
    pos = earth.at(t).observe(eph["sun"])
    lat, lon, _ = pos.ecliptic_latlon()
    # ... 50 lines of computation ...
```

**Router responsibilities ONLY:**
- Parse request (Pydantic model)
- Call service function
- Return response (dict/JSON)

### Rule 2: Services are PURE

```python
# ✅ CORRECT — pure function, no framework imports
def compute_natal_chart(params: dict) -> dict:
    """Compute natal chart. Input: dict → Output: dict"""
    # ... computation ...
    return {"bodies": [...], "houses": [...]}

# ❌ WRONG — service imports FastAPI
from fastapi import HTTPException  # NO!
def compute_natal_chart(params: dict) -> dict:
    if not params.get("date"):
        raise HTTPException(400, "date required")  # NO!
```

**Service responsibilities ONLY:**
- Accept dict/str/primitive input
- Perform computation
- Return dict/primitive output
- NO imports from `fastapi`, `starlette`, or any web framework
- NO direct file I/O (read data files at module load, not per-request)

### Rule 3: Integrations are ISOLATED

```python
# ✅ CORRECT — flat functions only
def create_customer(email: str, name: str) -> dict:
    """Create Stripe customer. Returns {id, email} or raises."""
    ...

def get_user_by_email(email: str) -> dict | None:
    """Fetch user from Supabase. Returns user dict or None."""
    ...

# ❌ WRONG — class hierarchy, mixed concerns
class PaymentManager:
    def __init__(self): ...
    def create_customer(self): ...
    def charge(self): ...
    def send_email(self): ...  # NO! email is not a payment concern
```

**Integration responsibilities ONLY:**
- Talk to ONE external API (Stripe OR Supabase, never both)
- Flat functions only (no class hierarchies)
- Return dict/primitive, raise on failure
- Services call integrations, routers call services

---

## 3. Standard Service Interface

Every service function MUST follow this signature pattern:

```python
def service_name(params: dict, **kwargs) -> dict:
    """
    Brief description of what this computes.

    Args:
        params: dict with keys:
            - key1 (type): description
            - key2 (type): description
        **kwargs:
            - tz_offset_hours (float): timezone offset (default: 7.0)

    Returns:
        dict with standardized keys:
            - success (bool): always present
            - data (dict): computation result (on success)
            - error (str | None): error message (on failure)
            - meta (dict | None): optional metadata (backend, version, etc.)

    Raises:
        ValueError: on invalid input
    """
    try:
        # 1. Validate input
        required = ["date", "time"]
        for key in required:
            if key not in params:
                raise ValueError(f"Missing required field: {key}")

        # 2. Compute
        result = _compute(params, **kwargs)

        # 3. Return standardized response
        return {
            "success": True,
            "data": result,
            "error": None,
            "meta": {"service": "service_name", "version": "2.0"}
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": str(e),
            "meta": {"service": "service_name", "version": "2.0"}
        }
```

### Standard Response Schema

Every service returns this exact structure:

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `success` | bool | YES | True if computation succeeded |
| `data` | dict | YES | Result payload (None on failure) |
| `error` | str\|None | YES | Error message (None on success) |
| `meta` | dict | NO | Metadata (backend, version, timing) |

---

## 4. Request/Response Flow

### Frontend → Backend

```typescript
// Frontend (React/RN)
const response = await fetch('/v1/natal', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'User',
    date: '1997-05-19',
    time: '05:45',
    tz_offset_hours: 7,
    lat: 13.3611,
    lon: 100.9847
  })
});

const data = await response.json();
// data = { success: true, data: {...}, error: null, meta: {...} }
```

### Backend Router

```python
# routers/natal.py
from pydantic import BaseModel
from src.services.chart_service import compute_chart

class NatalRequest(BaseModel):
    name: str
    date: str  # 'YYYY-MM-DD'
    time: str  # 'HH:MM'
    tz_offset_hours: float = 7.0
    lat: float
    lon: float

@router.post("/natal")
async def natal_endpoint(req: NatalRequest):
    result = compute_chart(
        name=req.name,
        date=parse_date(req.date),
        time=parse_time(req.time),
        tz_offset_hours=req.tz_offset_hours,
        lat=req.lat,
        lon=req.lon
    )
    return result  # Already standardized dict
```

### Backend Service

```python
# services/chart_service.py
from datetime import date, time, datetime, timezone, timedelta
from src.services.ephemeris import earth, eph, ts

def compute_chart(*, name: str, date: date, time: time,
                  tz_offset_hours: float, lat: float, lon: float,
                  system: str = "tropical") -> dict:
    """Compute natal chart. Returns standardized dict."""
    try:
        # 1. Build datetime
        dt_local = datetime.combine(date, time) - timedelta(hours=tz_offset_hours)
        dt_utc = dt_local.replace(tzinfo=timezone.utc)

        # 2. Compute positions
        t = ts.from_datetime(dt_utc)
        bodies = {}
        for body_key in BODIES:
            pos = earth.at(t).observe(eph[body_key])
            lat_ecl, lon_ecl, _ = pos.ecliptic_latlon()
            bodies[body_key] = {
                "absolute_deg": round(float(lon_ecl.degrees) % 360, 4),
                "lat_deg": round(float(lat_ecl.degrees), 4)
            }

        # 3. Compute houses
        houses = _compute_houses(dt_utc, lat, lon)

        # 4. Standardized response
        return {
            "success": True,
            "data": {
                "name": name,
                "datetime_utc": dt_utc.isoformat(),
                "bodies": bodies,
                "houses": houses,
                "ascendant": {"absolute_deg": houses["ascendant_deg"]}
            },
            "error": None,
            "meta": {"service": "compute_chart", "version": "2.0", "system": system}
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": str(e),
            "meta": {"service": "compute_chart", "version": "2.0"}
        }
```

---

## 5. Error Handling

### Service Layer

```python
# ✅ Return error in standardized response
def service_function(params: dict) -> dict:
    try:
        result = _compute(params)
        return {"success": True, "data": result, "error": None}
    except ValueError as e:
        return {"success": False, "data": None, "error": f"Invalid input: {e}"}
    except Exception as e:
        return {"success": False, "data": None, "error": f"Computation failed: {e}"}
```

### Router Layer

```python
# ✅ Pass through service response
@router.post("/natal")
async def natal_endpoint(req: NatalRequest):
    result = compute_chart(req.dict())
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
```

---

## 6. Import Rules

| Layer | Can import | Cannot import |
|-------|-----------|---------------|
| `routers/` | `fastapi`, `pydantic`, `src.services.*` | `src.integrations.*` (directly) |
| `services/` | `src.services.*`, `src.data.*` | `fastapi`, `starlette` |
| `integrations/` | `stripe`, `supabase`, `httpx` | `src.services.*` |

**Exception:** Services MAY import from other services (e.g., `chart_service` imports from `ephemeris`).

---

## 7. Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Router file | `snake_case.py` | `natal.py`, `vedic.py` |
| Service file | `snake_case.py` | `chart_service.py` |
| Service function | `snake_case()` | `compute_chart()`, `compute_houses()` |
| Integration function | `snake_case()` | `create_customer()` |
| Constant | `UPPER_SNAKE_CASE` | `BODIES`, `ASPECTS` |
| Private function | `_snake_case()` | `_compute_houses()` |

---

## 8. Testing Standard

```python
# tests/test_service.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.services.chart_service import compute_chart

def test_compute_chart_basic():
    result = compute_chart(
        name="Test",
        date=date(1997, 5, 19),
        time=time(5, 45),
        tz_offset_hours=7.0,
        lat=13.3611,
        lon=100.9847
    )
    assert result["success"] is True
    assert result["data"]["bodies"]["sun"]["absolute_deg"] == pytest.approx(58.34, abs=0.1)
```

---

## 9. New Feature Procedure

To add a new feature, follow this exact sequence:

1. **Create service** in `src/services/` following the standard interface
2. **Create router** in `src/routers/` (thin wrapper)
3. **Register router** in `src/main.py`
4. **Create test** in `tests/` following the test template
5. **Verify** with `PYTHONPATH=. python tests/test_new_feature.py`

---

## 10. Consolidation Plan

### Phase 1: Rectification (3 → 1)

| Current | Action | Rationale |
|---------|--------|-----------|
| `rectification.py` (392 lines) | **KEEP** as primary | Most complete: Saturn Return + Jupiter transit + Progressed Moon + Solar Arc |
| `rectification_tournament.py` (119 lines) | **MERGE** into primary | Cosine features are an upgrade, not a separate service |
| `sa_rectifier.py` (159 lines) | **MERGE** into primary | SA convergence is already in rectification.py |

**Consolidated:** `rectification.py` (~670 lines) with all three algorithms.

### Phase 2: Fusion (2 → 1)

| Current | Action | Rationale |
|---------|--------|-----------|
| `fusion_engine.py` (409 lines) | **KEEP** as primary | Complete multi-system synthesis |
| `fusion_transparency.py` (99 lines) | **MERGE** into primary | Wraps fusion_engine, not a separate concern |

**Consolidated:** `fusion_engine.py` (~510 lines) with built-in transparency.

### Phase 3: Future Consolidations

- `fusion_profile.py` — already removed (confirmed)
- Review all services for duplicate functionality
- Target: 70 services → ~50 services

---

## 11. Ephemeris Standard

- **Primary backend:** skyfield (DE421)
- **No fallback:** pyswisseph removed (DE406 differs by ~0.04°)
- **File location:** auto-discovered by `_find_bsp()` in `ephemeris.py`
- **Download:** only if no local copy found, tries NASA mirrors in order

---

*This document is the source of truth. Update it whenever the pipeline changes.*
