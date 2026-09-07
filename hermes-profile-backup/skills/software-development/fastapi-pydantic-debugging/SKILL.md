---
name: fastapi-pydantic-debugging
description: "Debug FastAPI response validation failures in tests."
version: 0.1.0
author: Hermes Agent (curator-managed)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [fastapi, pydantic, debugging, testing, response-model]
    related_skills: [systematic-debugging, test-driven-development]
---

# FastAPI + Pydantic Response Debugging

Use when FastAPI tests fail with `ResponseValidationError`, field-type mismatches, missing keys, or nested narrative-shape bugs instead of plain assertion failures.

## Core Principle

**Trust the error contract, not the test assertion text.** When FastAPI/Pydantic rejects a response, the model schema is the source of truth. Fix the service payload to match the model first; only then adjust tests if they encode the wrong expectation.

## When to Use

- `ResponseValidationError` from FastAPI test client
- Pydantic validation errors in API responses
- Test assertions pass logically but fail because of `int` vs `str`, missing field, or wrong shape
- Narrative/reel reading endpoints where nested `cards`, `position`, `arcana`, `name` must align

## Debugging Loop

### 1. Read the model before the test
```bash
rg -n "class TarotCardDraw|class TarotDrawResponse|position:|arcana:" src/models/
```

### 2. Compare service return dict vs model fields
For every field in the response model, verify the service actually provides it with the correct type and alias. Common misses:
- Missing top-level `name` in draw response
- `position` as `int` when model expects `str`
- Missing `arcana` on each card

### 3. Re-run the narrowest failing test
```bash
pytest tests/test_tarot.py::test_api_draw_three_card -q
```

## Reusable Patterns

### Deterministic draw seeded from identity
If tests expect same draw for same caller but no explicit seed is supplied:
```python
if seed is None:
    seed = hash(name) % (2**31)
rng = random.Random(seed)
```
This makes `draw_spread("Mark", spread="three_card")` deterministic without requiring callers to pass `seed`.

### Element-balance field aliases
Inspect the actual balance dict before using it:
```python
print(compute_element_balance(chart))
# often contains: dominant, lacking, weakest, scores, percent
```
Fallback order for the target element:
```python
weakest = balance.get("weakest") or balance.get("lacking") or balance.get("dominant", "")
```

### Position-label mapping for narrative hooks
If hooks are keyed by semantic labels but card positions are numeric:
```python
_POSITION_LABEL = {1: "สถานการณ์ปัจจุบัน", 2: "อุปสรรค", 3: "คำแนะนำ"}
label = _POSITION_LABEL.get(int(position), str(position))
hook = _HOOKS_TH.get(label)
```
Otherwise `_HOOKS_TH.get(1)` will always miss.

### Card-name format must match source of truth
Dataset names like `Ace of Wands` require:
```python
MINOR_ARCANA = [
    f"{v} of {s}"
    for s in ["Wands", "Cups", "Swords", "Pentacles"]
    for v in ["Ace", "Two", ..., "King"]
]
```
Inverted `suit of rank` causes `KeyError` in story-lookup tables.

## Hermes Tooling

- `read_file` with exact line numbers to inspect response models
- `terminal` to run targeted pytest on the failing seam
- `search_files` to trace where bad values enter the response payload
- `execute_code` for one-off REPL inspection of computed shapes
