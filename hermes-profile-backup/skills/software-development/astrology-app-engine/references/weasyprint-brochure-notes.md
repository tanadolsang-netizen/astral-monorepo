# WeasyPrint Brochure Integration Notes

## Verified working signature

```python
from src.services.weasy_brochure import render_brochure

render_brochure(
    sections,
    out_path,
    *,
    person_name="",
    lang="th",
    theme_hint="",
    biwheel="",
    section_art=None,
    raw_section="",
    raw_title="",
)
```

## Critical constraint: lines must be strings

WeasyPrint crashes during render if any section line is not a string:

```
AttributeError: 'dict' object has no attribute 'replace'
```

Section builders must therefore coerce values before returning:

```python
lines = [
    f"Life: {life.get('pillar', '')} ({life.get('animal', '')})",
    f"Body: {body.get('pillar', '')} ({body.get('animal', '')})",
    f"Lunar: {lunar.get('year_ganzhi', '')} / {lunar.get('month', '')}-{lunar.get('day', '')}",
]
return [{"title": f"Zi Wei Dou Shu — {name}", "lines": lines}]
```

## Router migration pattern

1. Replace `from src.services.premium_pdf_service import render_pdf` with `from src.services.weasy_brochure import render_brochure`.
2. Replace every `render_pdf(...)` call with `render_brochure(...)`.
3. Keep `biwheel_svg` import if synastry routes still need it for the `biwheel=` arg.
4. Pass `raw_section=` and `raw_title=` for tarot/raw HTML blocks; the brochure generator ignores unknown extras safely.

## grand-summary rule

`/report/grand-summary` must call `compute_grand_fusion(name, lang=...)` directly. Do NOT call the HTTP endpoint `/v1/fusion/grand/...` from inside the report router; in-process tests and offline runs have no server listening, which causes `ConnectionRefusedError`.

## Engine signatures used in report endpoints

- vedic: `compute_vedic(birth_datetime_local, lat, lon, tz_offset_hours, person_name)`
- bazi: `four_pillars(date, time)`
- human design: `compute_human_design(natal_chart=compute_chart(...))`
- ziwei: `compute_ziwei(birth_date, birth_time)`
- grand summary: `compute_grand_fusion(name, lang, years)` returns a dict with keys like `person`, `reading`, `extended`, `precedence_note`

## Observed output sizes with owner test data

- natal: ~19 KB
- vedic: ~18 KB
- bazi: ~16.5 KB
- human-design: ~11.6 KB
- ziwei: ~12.9 KB
- grand-summary: ~27.7 KB