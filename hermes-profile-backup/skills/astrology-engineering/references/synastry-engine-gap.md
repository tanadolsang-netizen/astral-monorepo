# Synastry Engine Gap (FIXED 2026-08-22)

## Was failing test
`test_identical_charts_score_higher_emotional_bond_than_opposite` in `tests/test_synastry_score.py`

## Root cause (RESOLVED)
`_classify()` in `src/services/synastry_scoring.py` had no same-planet pair-kind.

**Consequence (before fix):**
- Identical charts (same birth data) earned 0 for Sun-Sun / Moon-Moon conjunction orb 0°
- A 180° chart-shift turned sextiles (harmonic weight 0.7) into trines (0.9) → won incorrectly

## Fix applied (2026-08-22)
Added new pair-kind `identity-resonance` in `src/services/synastry_scoring.py`:
- Trigger: same luminary or personal planet conjunction, orb ≤ 1°
- Dimension: `emotional_bond` (primary), `chemistry` (secondary)
- Weight: W ≈ 10 (via `_SAME_BODY_WEIGHT`)

```python
# In synastry_scoring.py - added near _classify():
_SAME_BODY_DIMENSION = {
    "Sun": "emotional_bond",
    "Moon": "emotional_bond",
    "Mercury": "communication",
    "Venus": "chemistry",
    "Mars": "chemistry",
    "Jupiter": "growth",
    "Saturn": "stability",
}
_SAME_BODY_WEIGHT = 10.0
```

**Result:** Test now PASSES. 142/142 green.

## Historical note
This file documents a FIXED gap. For future regressions, check if `identity-resonance` kind exists in `_classify()` and weights are ~
<tool_call>
<function=write_file>
<parameter=content>
# Synastry Engine Gap (FIXED 2026-08-22)

## Was failing test
`test_identical_charts_score_higher_emotional_bond_than_opposite` in `tests/test_synastry_score.py`

## Root cause (RESOLVED)
`_classify()` in `src/services/synastry_scoring.py` had no same-planet pair-kind.

**Consequence (before fix):**
- Identical charts (same birth data) earned 0 for Sun-Sun / Moon-Moon conjunction orb 0°
- A 180° chart-shift turned sextiles (harmonic weight 0.7) into trines (0.9) → won incorrectly

## Fix applied (2026-08-22)
Added new pair-kind `identity-resonance` in `src/services/synastry_scoring.py`:
- Trigger: same luminary or personal planet conjunction, orb ≤ 1°
- Dimension: `emotional_bond` (primary), `chemistry` (secondary)
- Weight: W ≈ 10 (via `_SAME_BODY_WEIGHT`)

```python
# In synastry_scoring.py - added near _classify():
_SAME_BODY_DIMENSION = {
    "Sun": "emotional_bond",
    "Moon": "emotional_bond",
    "Mercury": "communication",
    "Venus": "chemistry",
    "Mars": "chemistry",
    "Jupiter": "growth",
    "Saturn": "stability",
}
_SAME_BODY_WEIGHT = 10.0
```

**Result:** Test now PASSES. 142/142 green.

## Historical note
This file documents a FIXED gap. For future regressions, check if `identity-resonance` kind exists in `_classify()` and weights are ~10.