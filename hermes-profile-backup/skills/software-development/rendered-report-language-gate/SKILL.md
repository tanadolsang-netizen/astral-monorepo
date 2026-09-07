---
name: rendered-report-language-gate
description: "Use when PDF reports must render clean TH without CJK noise."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [pdf, reports, rendering, language, sanitization, thai, narrative]
    category: software-development
---

# Rendered-Report Language Gate

Class-level skill for enforcing clean target-language output in any generated PDF/report pipeline.

## When to use

- Multiple builders/sections feed one renderer and language mixing has occurred
- Engine output is structurally correct but narratively broken (mixed scripts, CJK fragments, EN tokens in TH output)
- User explicitly demands permanent auto-correction before rendering, not per-file patches
- Adding a new report endpoint or section builder that must match existing voice/language standards
- Any meaning/mapping file becomes the single source of truth for rendered text

## Core pattern

```
Raw engine output
       ↓
[narrative_gate] ← mandatory, single chokepoint
       ↓
Renderer (WeasyPrint / Chrome PDF / etc.)
       ↓
PDF
```

**Rule:** every section dict passes through exactly one gate before render. No exceptions.

## Gate responsibilities

1. **Script whitelist** — strip characters outside the target language’s allowed Unicode blocks
2. **Artifact blocklist** — remove known garbled tokens from prior generations (`cuatro palos`, `etalon`, `rutin`, `painstakingly`, ` estat分析`, etc.)
3. **Machine-list → natural paragraph** — convert raw key-value dicts into conversational prose matching the project’s voice rules
4. **Empty-line pruning** — drop blank lines so layout doesn’t inject stray whitespace
5. **Language-consistent rewrite** — if `lang=th`, output is pure TH; if `lang=en`, output is pure EN. Never mix in one sentence.
6. **Meaning-file purity sweep** — when a dedicated meanings module exists, treat it as render-time input too; any EN/CJK/Latin residue there will appear in final output.

## Implementation template

Create a single module, e.g. `src/services/narrative_gate.py`, with:

- `_clean(text, lang)` — whitelist + artifact removal
- Language-specific natural converters for known machine-list sections (human design, zi wei, bazi, vedic)
- `NarrativeGate(lang).render(sections)` — processes all sections
- `apply_narrative_gate(sections, lang)` — public API used by renderer

Wire it in the renderer:

```python
from src.services.narrative_gate import apply_narrative_gate

def render_brochure_v2(sections, ..., lang="th", ...):
    ...
    sections = apply_narrative_gate(list(sections), lang)
    ...
```

## Meaning-dict single source of truth rule

If meanings live in a dedicated module, do **not** duplicate them inline in the service file. Keep exactly one source:

- Preferred: `src/services/tarot_meanings_th.py` → `TAROT_MEANINGS_TH`
- Service imports it as `_THAI_MEANINGS` only
- Remove any inline meanings block in `tarot_service.py`

Why: duplicated inline dicts drift, acquire mixed-language edits, and break syntax when imports are pasted mid-file.

## Meaning-file gate test pattern

Add a lightweight pytest file, e.g. `tests/test_language_gate.py`, that asserts:

- all expected cards are present
- purity threshold by language block
- no known fragment strings survive (`正在餐`, `subconscious`, `正在餐discourage`, `clarity emerging`, `正在餐 approaching`, `正在餐到来`, `正在餐存在`)

This turns “one bad meaning” into a CI failure instead of a user-visible PDF defect.

## Hard-threshold policy

- **Temporary cleanup aid:** when cleaning legacy mixed-language meanings, start with a soft purity threshold in `tests/test_language_gate.py` so CI still runs while repairs are in flight.
- **Permanent policy:** harden to `p >= 1.0` only after cleanup is complete and verified on disk. Do not leave the project on a soft threshold indefinitely.
- **Gate-the-gate-too:** `narrative_gate.py` itself can accumulate mixed-language strings. Run the language gate against the gate module values, not just final render output.

## Encoding-corruption distinction

Mixed CJK/Hangul/Cyrillic/Latin/Greek fragments in meaning files are often **encoding artifacts from OCR or file conversion**, not intentional multilingual content. Treat them as data corruption to strip, not as translations to preserve. A quick discriminant: if the same fragment repeats across unrelated entries, or appears mid-Thai word, it is almost certainly corruption.

## PDF inspection fallback

Some environments cannot render PDFs directly in the preview/browser path. Fallback sequence:
1. Install `pymupdf` in the project venv.
2. Convert pages to PNG with `fitz`/`pymupdf`.
3. Use vision-based page inspection on the PNGs to verify headings, layout, and artifacts.

## Delegated-cleanup verification rule

Subagents hitting rate limits or iteration caps may leave duplicated blocks, truncated files, or duplicated sections. After any delegated meaning cleanup:
1. Re-read the file shape before trusting it.
2. Verify syntax with `python -m py_compile`.
3. Run the language-gate and smoke tests on disk.
4. If the file shape looks wrong, re-write from the canonical dataset instead of patching blindly.

## Reel-reading position-to-hook mapping rule

When `reel_reading.py` renders by numeric position and another module stores hooks by labeled position, normalize first:

- map `int(position)` → label before hook lookup
- keep TH/EN label maps in one place
- never assume the position string already matches hook keys

Otherwise hooks silently vanish and EN narrative tests fail despite correct data.

## Frontend hookup pattern

When the frontend is still a stub, treat backend connectivity as a first-class checklist item instead of an afterthought:

- Inspect `App.js`, `app.json`, `package.json`, and any `.env`/`EXPO_PUBLIC_*` references before assuming API URL exists.
- If no backend URL/config is present, add one config source with a clear `API_URL`/`EXPO_PUBLIC_API_URL` convention before preview/deploy.
- After backend URL is wired, verify with one non-mock network flow rather than only local UI rendering.

## Voice rules (project-specific)

1. Write to one person: use “คุณ” throughout
2. Open with image/metaphor, not jargon
3. Numbers as witnesses, not heroes
4. Wound → gift arc in every section
5. No system terms: module, endpoint, status, verify, unavailable
6. Short + long sentences alternate
7. End with mirror, not promise

## Pitfalls

- **Patch-after-patch decay:** fixing one builder today and another tomorrow never ends. Build the gate once.
- **Inline bilingual mixing:** `ตุลย์(Libra)` in one sentence breaks flow. Use separate TH/EN blocks per section.
- **EN translated from TH:** produces stiff prose. Rewrite EN from idea; do not literal translate.
- **Subtitle = lang string:** some renderers inject `subtitle = lang` literally. Sanitize or blank when `person_name` is absent.
- **Chart cache keys:** when adding chart caching, avoid double-prefix names like `_cached__cached_compute_chart`.
- **Recursive builder references:** `_syn_builders` calling itself instead of returning builder dicts causes infinite loops.
- **Inline duplicate meaning blocks:** copy-pasting meanings into the service file after a module import creates syntax breakage and drift. Keep meanings in one module only.
- **Hook-key mismatch:** position-numbered output compared against label-keyed hooks returns no hooks. Normalize mapping before lookup.
- **Thai whitelist typo:** `pdf_renderer.py` used the literal characters `฀-๿` instead of the Unicode range `\u0E00-\u0E7F`. That silently fails to strip non-Thai glyphs. Always use the escaped range in whitelist regexes.
- **Gate mappings themselves can rot:** `narrative_gate.py` can accumulate EN/CJK/Hangul/Cyrillic strings over time. Run the language gate against the gate module too, not just final render output.
- **Delegated cleanup can corrupt files:** subagents hitting rate limits/iteration caps may leave duplicated blocks, truncated files, or duplicated sections. Always verify syntax and test results on disk after delegated meaning cleanup; re-rewrite from dataset if the file shape looks wrong.
- **Soft threshold during cleanup:** when cleaning legacy mixed-language meanings, start with a soft purity threshold in `tests/test_language_gate.py` so CI still runs. Harden to strict only after cleanup is complete.

## Supporting scripts

- `scripts/verify_narrative_gate.py` — smoke test: feed dirty sections, assert clean output
- `references/tarot-deck-downloader.md` — optional background downloader pattern for card image assets
- `references/meaning-gate-test-template.md` — template for lightweight language-gate tests over meaning dicts
