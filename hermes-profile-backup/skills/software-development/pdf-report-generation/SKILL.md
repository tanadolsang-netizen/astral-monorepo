---
name: pdf-report-generation
description: Use when generating astrology PDF reports or brochure PDFs.
version: 1.0.0
author: ox-alpha (curator)
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [pdf, reports, astrology, weasyprint, narrative, thai, english]
    related_skills: []
---

# PDF Report Generation

Class: producing astrology PDF reports from computed chart data. This skill covers narrative quality, language separation, section builder architecture, and rendering wiring.

## Non-negotiable quality rules

1. **Never mix Thai and English narrative in one builder file.** Split into `src/services/pdf_agent_th.py` and `src/services/pdf_agent_en.py`, each returning natural conversational text in its language only.
2. **No CJK glyphs in Thai output.** Strip Chinese/Japanese/Korean characters from Thai lines before rendering.
3. **No English labels in Thai sections.** Remove glossary-style output like `Type:`, `Authority:`, `Centers:`, `Gates:`, `Life:`, `Body:`, `Lunar:`, `Day Master`, `Year:`, `Month:`, `Day:`, `Hour:` from Thai narrative. Convert to natural Thai paragraphs.
4. **No artifact strings.** Remove leftover code/translation artifacts such as `Axami`, `Kps`, `εστι`, `oportun`, `Ars`, `Kritikal`, ` вnglish`, `wajik indian`, `cuatro palos`, `etalon`, `rutin`, ` Monsug`, `inward`, `caring`, `inner world`, `composite chart`, `super couple`, `relationship energy`, `ไม่ได้บวกตรงๆ`, `เลขที่ไม่ได้บอกทุกอย่าง`, `ทำลงในความจริง`, ` presencia `, ` estat分析`, `cross-reference`, `future ที่`, `track ที่`, `从来`, `观众`, `天蝎`, `白羊`, `金牛`, `双子`, `巨蟹`, `狮子`, `处女`, `天秤`, `射手`, `摩羯`, `水瓶`, `双鱼`.
5. **Narrative tone.** Thai should read like a tarot reader on social media: direct, emotional, conversational, no literal translation. English should read like natural copy, not glossary output.

## Section builder architecture

- Keep one builder per section type: `build_natal_sections`, `build_synastry_sections`, `build_composite_sections`, `build_transit_sections`, `build_muhurta_sections`.
- Each builder returns `list[dict]` with shape `[{"title": str, "lines": [str, ...]}, ...]`.
- In `src/routers/reports.py`, select the language set with small helpers:
  - `_syn_builders(lang)`, `_natal_builders(lang)`, `_comp_builders(lang)`, `_transit_builders(lang)`, `_muhurta_builders(lang)`
- Pass `req.lang` from the endpoint payload into these helpers.

## PDF rendering rules

- Use `src/services/weasy_brochure.py` for brochure-style PDFs. Signature: `render_brochure(sections, out_path, person_name=..., lang=..., theme_hint=...)`.
- `render_brochure` accepts `section_art`, `biwheel`, `raw_section`, `raw_title` extras.
- Do not hardcode absolute Windows paths for assets. Use repo-relative paths under `assets/` or omit when unavailable.
- Tarot image HTML should not assume `frontend/public` exists; guard with fallback when `card_image_url` returns empty.

## Report endpoint wiring rules

- Every `/report/*` endpoint must call a real engine function, not a placeholder.
- Section builders must consume actual computed payload keys; do not invent legacy keys.
- Grand summary should accept optional `partner_*` fields for synastry and `muhurta_*` fields for electional timing, all optional with sensible fallbacks.
- Remove hardcoded demo data from production narrative code.

## Verified ground truth

Two real charts are locked in with computed positions: Owner (19 May 1997 05:45 Chonburi) and Mai (18 Aug 2001 22:32 Nonthaburi). Any new narrative or calculation must remain consistent with these charts before shipping.

## Environment prerequisites

- Use `uv run python` for execution so project dependencies resolve.
- Tests: `uv run pytest` from repo root; currently 430+ passing.
- Do not commit personal birth profiles to git; keep them in `.data/profiles/` locally or exclude via `.gitignore`.

## Pitfalls

- Mixed-language builders cause user-facing PDFs to look broken and unprofessional. Always split by language at the file level.
- Empty `lines` lists are filtered out before rendering; builders must return non-empty lists.
- WeasyPrint requires font paths as `file:///` URLs; use `.as_posix()` for Windows paths.
- If a PDF still shows mixed text after a builder rewrite, search for hardcoded English/CJK strings inside `src/routers/reports.py` section builders and the `pdf_agent_*.py` files.
- Thai render whitelist typo: do not use the literal range `฀-๿`. Use `\u0E00-\u0E7F` in regex character classes; otherwise non-Thai glyphs survive sanitization.
- Delegated meaning cleanup can leave duplicated or truncated files. After any subagent or script rewrites `tarot_meanings_th.py`, verify syntax, count, and language-gate tests before continuing PDF work.

## WeasyPrint CSS pitfalls (learned 2026-08-30, hard-won)

These crash or silently break `weasyprint` (weasy_brochure / build_combined_final):

- **`position: fixed` on `body::before` (or any pseudo-element overlay)** → `AssertionError: isinstance(box, boxes.BlockReplacedBox)` inside `float_layout`. WeasyPrint does NOT support fixed-position overlays. For a starfield/texture, put `radial-gradient(...)` layers directly on `html, body { background: ... }` instead.
- **`::first-letter { float: left }` for drop caps** → same float-layout AssertionError. Use a plain large `::first-letter` (no `float`), e.g. `font-size: 34pt; font-weight: bold;` with padding — it still reads as a drop cap.
- **`data:` URI images are DROPPED** by weasyprint here → PDF embeds 0 images. Always use `file:///{path.as_posix()}` and pass `base_url=str(REPO)` to `HTML()`.
- **Reversed tarot cards**: rotate the `<img>` via a CSS class, e.g. `img.reversed { transform: rotate(180deg); }`. Set the class from the card's orientation string in the builder.
- **`box-shadow` glow** works fine and is the cheap way to make cards "pop" on a dark ground (e.g. `box-shadow: 0 0 26px rgba(201,166,74,.45)`).
- After any CSS change, re-run the actual `write_pdf` call (not just lint) — weasyprint errors only surface at render time.

## Premium visual quality — weasyprint is NOT enough for "real" 3D/premium

WeasyPrint only implements a CSS 2.1 subset. It CANNOT do: `backdrop-filter`, real
`transform: perspective/rotateX/Y` 3D, `filter`, `position: fixed` overlays, `::before`
absolute overlays, `float` drop caps, or rich gradients/filters. Output therefore looks
FLAT — and the user (2026-08-30) explicitly REJECTED a weasyprint dark-mystical theme as
"แย่มาก / downgrade / ไม่สวย / 3D อะไรก็ไม่มี". A weasyprint PDF is fine for utilitarian
reports; it is NOT premium.

For a genuinely premium / magazine-grade / 3D PDF, use a REAL BROWSER renderer:

1. **Render with Playwright + Chromium headless print** (not weasyprint):
   - `uv pip install playwright` then `uv run python -m playwright install chromium`.
   - Build full HTML/CSS (gradients, `backdrop-filter`, 3D `transform`, SVG, web fonts).
   - Print: `page.pdf(path=..., format='A4', print_background=True)` — `print_background=True`
     is required or CSS backgrounds/gradients are dropped.
   - Chromium renders real CSS, so all the "premium" techniques work. File size is fine
     (user said large files OK).
2. **Generate art with ComfyUI** (local feasible on this box: RTX 5060 8GB, `comfy install
   --nvidia --fast-deps`; SDXL comfortable). Draw cover/decor + tarot cards as fine
   classical-painting art (NOT flat public-domain scans). User wants AI-drawn art, not
   reused Visconti/Rider-Waite scans. Prompts live in `scripts/comfy_prompts.txt`.
3. Keep the weasyprint pitfalls above ONLY for the utilitarian brochure path; do not present
   weasyprint as the premium solution.

## Chromium premium CSS pitfalls (learned 2026-08-30, hard-won)

The Playwright/Chromium path renders real CSS, but the SAME stylesheet that scores **EN
~9.1/10 (deep, readable)** scores **TH only ~7.5/10** for the same content, because Thai
narrative prose is longer and denser per line than English copy. Symptoms: font looks
small, line-height too tight, paragraphs feel cramped/unreadable.

- **Do NOT reuse the EN CSS verbatim for the TH blocks.** After writing TH prose (which
  runs much longer than EN), bump TH typography: larger `font-size` (e.g. +1–2pt over EN)
  and looser `line-height` (e.g. 1.8–2.0 vs 1.5), plus slightly wider `padding`/margins.
- Verify TH legibility with `vision_analyze` on the rendered page PNG — but remember
  vision MISREADS Thai glyphs (see astrology-report-generation skill), so judge
  **legibility/structure only** (font size, spacing, crowding), never language purity.
- Language purity gate stays `pymupdf` regex (LATIN-block sweep), not vision.
- Iterate TH CSS until the TH page reads as comfortably as the EN page; do not ship a
  PDF where one language looks cramped next to the other.

## Narrative fallback when no life context (transcripts) exists

STARHEART life-grounding requires real transcripts/facts about the person. When generating a PDF for someone **other than the user** (e.g. a friend, client, or stranger), `life_context` will be `None`.

**Do NOT skip the life-story section.** Instead, write a direct narrative derived purely from the chart positions:

1. Read each planet's sign + house from the computed chart.
2. For each planet, write 1-2 sentences connecting its position to personality/life themes (e.g. "อาทิตย์มังกร b12 = ทะเยอทะยาน วินัย ต้องการได้รับการยอมรับ" — short, direct, no invented biography).
3. Structure as: core identity (ASC+Sun+Moon) → mind/communication (Mercury+Venus) → drive/expansion (Mars+Jupiter) → lessons (Saturn) → generational (Uranus/Neptune/Pluto).
4. For the "life story" section, write 4 paragraphs: childhood → adolescence → adulthood → present — each derived from chart dynamics (Moon/Mercury = childhood learning, Sun = adolescent identity, etc.). **Do not invent specific events** (no "at age 12 you moved").
5. Keep tone warm but grounded — this is still a tarot-reader voice, just without personal facts.

Example fallback builder: `scripts/build_mo_pdf.py` (generated for โม, 14 Jan 2003).

## Chart calculation verification (cross-check)

When precision matters (user questions accuracy, or a chart looks off), verify against raw Swiss Ephemeris:

```python
import swisseph as swe
swe.set_ephe_path('de421.bsp')
# Convert ICT to UTC: 07:15 ICT = 00:15 UTC = 0.25h
julday = swe.julday(year, month, day, utc_hour)
result = swe.calc(julday, swe.SUN)  # lon = result[0][0]
result = swe.houses(julday, lat, lon, b'P')  # Placidus
asc = result[1][0]
```

Verified chart for โม (14 Jan 2003 07:15 ICT, 13.78N 100.54E):
- ASC กุมภ์ 0.00° · Sun มังกร 23.4° b12 · Moon เมถุน 1.0° b4 · Mercury มังกร 18.3° b12 · Venus ธนู 6.5° b10 · Mars พิจิก 27.9° b10 · Jupiter สิงห์ 15.5° b7 · Saturn เมถุน 23.5° b5 · Uranus กุมภ์ 26.8° b1 · Neptune กุมภ์ 10.0° b1 · Pluto ธนู 18.7° b11
- Backend matched Swiss Ephemeris to <0.1° for all bodies.

## ComfyUI not reachable — graceful fallback

When ComfyUI is down, `build_combined_premium.py` skips AI art generation and still produces a PDF. The `ensure_art()` function prints a warning but continues. This is intentional — the PDF ships without tarot card images rather than failing entirely.

User rejects stiff literal translations ("ปีศาจ", "หกแห่งเหรียญ") as ugly. Tarot card names MUST use beautiful classical-reader Thai voice, as a SINGLE SOURCE in `src/services/tarot_meanings_th.THAI_CARD_NAMES` + `th_card_name()`:

- The Devil = **มาร**, Six of Pentacles = **หกแห่งทรัพย์**, Knight of Pentacles = **อัศวินแห่งทรัพย์**, Pentacles = **ทรัพย์**, Wands = **ไม้เท้า**, Cups = **ถ้วย**, Swords = **ศาสตรา**
- Major Arcana map: The Fool=เพลิงบ้า, The Magician=นักเล่นเวท, The High Priestess=นางสันโดษ, The Empress=พระนางเจ้า, The Emperor=พระจักรพรรดิ, The Hierophant=มหาปุโรหิต, The Lovers=คู่ตรัส, The Chariot=ราชรถ, Strength=ใจหาญ, The Hermit=นักพรต, Wheel of Fortune=วงล้อวารี, Justice=ธรรมะ, The Hanged Man=บุรุษแขวนกาย, Death=กรรม, Temperance=ศาสตร์สมดุล, The Tower=หอพัง, The Star=ดารา, The Moon=จันทรา, The Sun=อาทิตยา, Judgement=พิพากษา, The World=จักรวาล
- Consume `th_card_name()` everywhere (PDF builder, reel_reading, frontend). Never duplicate the map per-file — when a second consumer appears, import the single source, delete the copy.
- This rule applies to BOTH the PDF and chat context, permanently.

## Decorative image = ONE, derived from whole chart (user rule)

User correction: do NOT stamp a myth/decor image per planet (not "10 images, one each"). Instead:
- Analyze the WHOLE chart (dominant element / stellium / exalted planet).
- Pick the SINGLE best-fitting decorative image (e.g. fire-dominant Aries stellium → Helios/sun god).
- Print a WHY caption UNDER the image explaining why it fits this specific input.
- This keeps the PDF focused and premium rather than a sticker sheet.