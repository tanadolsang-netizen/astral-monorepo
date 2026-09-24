# Astral Horoscope SOP
Last updated: 2026-09-04  
Scope: backend chart computation + frontend narrative reading

## 1. Zodiac & Ayanamsa
- Default: **Tropical** zodiac.
- Sidereal/Lahiri only when explicitly requested.
- When `system == "sidereal"`, apply Lahiri ayanamsa using year fraction, then normalize to `[0, 360)`.

## 2. Ephemeris
- Use **Skyfield** with **DE440** ephemeris.
- Source: `backend/src/services/ephemeris.py`.
- Compute positions from Julian Day; do not use randomized or fake animation data.

## 3. Houses
- Default: **Placidus**.
- House cusps computed via `compute_houses()`.
- Body-to-house assignment via `_house_of(lon_deg, cusp_degs)`.
- Validation rule: every body must fall within its assigned house interval.

## 4. Bodies
Standard set ( Tropical order):
- Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto

Per-body fields:
- `body`, `sign`, `degree`, `absolute_deg`
- `house`
- `dignity` (label + score)
- `latitude` — ecliptic latitude from Skyfield
- `motion_per_day` — daily motion heuristic
- `retrograde` — boolean from daily motion

### Retrograde / Speed heuristic
- Use **daily motion** between `t-1 day` and `t+1 day`, not instantaneous velocity.
- `motion = (lon_p1 - lon_m1) % 360`, then wrap into `[-180, +180)`.
- `retrograde = motion < 0`.
- If Skyfield fails for a body, set `motion_per_day = None` and `retrograde = False` rather than crashing.

### Latitude
- Store ecliptic latitude in the body record.
- Current state: **stored but not integrated into aspect interpretation**.
- Future work: use latitude to tighten orbs or flag high-latitude bodies.

## 5. Dignities
- Labels: domicile, exaltation, detriment, fall, peregrine.
- Score mapping defined in `compute_dignity()`.
- Include `label` and `score` in every body record.

## 6. Aspects
- Compute cross-aspects between all body pairs via `compute_cross_aspects()`.
- Standard aspects: conjunction, sextile, square, trine, opposition.
- Orbs: configured per aspect type.
- Applying/separating: use daily motion heuristic (not exact instantaneous velocity).
- Output fields: `body_a`, `body_b`, `aspect`, `orb`, `applying`.

## 7. Narrative Reading Rules
- Voice: warm tarot-reader, **star → card → life**, humanizer always.
- No AI-slop: be expert-level accurate.
- Paragraph length: **2–4 sentences** each.
- Tropical-first language; mention Sidereal/Lahiri only when explicitly used.
- Retrograde wording: explain as internal/reflective energy, not “bad”.
- Latitude: describe when relevant, but do not invent aspect-level latitude rules until integrated.

## 8. Frontend Sync
- Frontend consumes backend `/v1/natal/compute`, `/v1/sky/view`, `/v1/sky/life`.
- Use Vite proxy for local dev; direct Railway calls may 429.
- Fallback mock data (`buildFallbackSky`) is allowed only when backend is unavailable.

## 9. Validation Checklist
Before publishing any reading:
- [ ] All bodies have `absolute_deg`, `sign`, `house`, `dignity`
- [ ] `latitude`, `motion_per_day`, `retrograde` present (or gracefully absent)
- [ ] House assignment passes interval check
- [ ] Aspects include applying/separating flags
- [ ] Narrative uses 2–4 sentence paragraphs
- [ ] Zodiac system stated explicitly
