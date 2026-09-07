# Report Endpoint Wiring Reference

Verified engine mappings for `NEW-AI-REBORN/src/routers/reports.py` as of 2026-08-28.

## Real Engine Functions

| Endpoint | Import path | Function signature | Returns |
|---|---|---|---|
| `/report/vedic` | `src.services.vedic_service` | `compute_vedic(birth_datetime_local: str, lat, lon, tz_offset_hours=7.0, person_name="") -> dict` | `system, ayanamsa, lagna, chandra_rashi, surya_rashi, nakshatra, interpretation` |
| `/report/bazi` | `src.services.bazi_service` | `four_pillars(d: date, t: time) -> dict` | `pillars.{year,month,day,hour}, day_master, zodiac_th/en, confidence` |
| `/report/human-design` | `src.services.grand.human_design` | `compute_human_design(natal_chart: dict) -> dict` | `type, authority, profile, defined_centers, defined_channels, personality, design` |
| `/report/ziwei` | `src.services.grand.ziwei` | `compute_ziwei(birth_date, birth_time, annual_years=None) -> dict` | `lunar, life_palace, body_palace, palace_wheel, annual` |
| `/report/grand-summary` | `src.services.grand.grand_fusion` | `compute_grand_fusion(name, lang="th", years=None, profile=None) -> dict` | `person, extended.{fixed_stars,asteroids,varshaphal,ziwei,...}` |

## Section Builder Keys

Each `_X_sections(name, chart)` helper must read these exact keys:

```python
# vedic
chart["ayanamsa"]
chart["lagna"]["sign_th"] / ["sign_en"]
chart["chandra_rashi"]["sign_th"]
chart["nakshatra"]["name_th"] / ["name_en"] / ["pada"]
chart["interpretation"]["th"] / ["en"]

# bazi
chart["pillars"]["year"]["pillar"]   # e.g. "丁丑"
chart["pillars"]["year"]["animal_th"]  # e.g. "วัว(ฉลู)"
chart["pillars"]["year"]["stem_element_th"]  # e.g. "ไฟ"
chart["day_master"]["stem"]  # e.g. "辛"
chart["day_master"]["element_th"]  # e.g. "โลหะ"
chart["day_master"]["label_th"]  # e.g. "โลหะหยิน"

# human design
chart["type"]  # e.g. "Generator"
chart["authority"]  # e.g. "Emotional (Solar Plexus)"
chart["profile"]["profile_name"]  # e.g. "4/6"
chart["defined_centers"]  # list of center names
chart["defined_channels"]  # list of channel names

# ziwei
chart["life_palace"]["pillar"]  # e.g. "壬寅"
chart["life_palace"]["animal"]  # e.g. "Tiger"
chart["body_palace"]["pillar"]  # e.g. "戊申"
chart["lunar"]["year_ganzhi"]  # e.g. "丁丑"
chart["lunar"]["month"]  # int
chart["lunar"]["day"]  # int
```

## Profile Dependency

`/report/grand-summary` calls `compute_grand_fusion()`, which loads profile from `.data/profiles/<name>.json`. The profile must exist first.

Create via router in `src/routers/fusion_profile.py`:
- `PUT /v1/fusion/profile/{name}` with `{date, time, tz_offset_hours, lat, lon}`

## Pitfalls

- `lunar-python` is required for ziwei; install via `uv add lunar-python`.
- Human Design needs natal chart input with Sun longitude; always call `compute_chart(system="tropical")` first.
- Vedic expects `birth_datetime_local` as ISO string `YYYY-MM-DDTHH:MM`, not separate date/time args.
- BaZi uses local birth time directly; no timezone conversion inside `four_pillars()`.
- Do not invent wrapper names like `compute_vedic_chart()` or `compute_bazi_chart()` — they do not exist.
