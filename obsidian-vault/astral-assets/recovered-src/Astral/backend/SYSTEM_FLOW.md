# Astral Astrology System — Flow Tree for Hermes Agents

## Repo & Working Directory
- Main repo: `C:/AI/NEW-AI-REBORN`
- Branch: `main`
- Tests: `uv run python -m pytest` → 587 passing (smoke) + 157 language-gate (hard threshold 1.0)
- Server: `uvicorn src.main:app --host 0.0.0.0 --port 8001`

### Uvicorn Port-Conflict Rule
- If port 8001 is already in use, uvicorn exits with code 3 / `Errno 10048`.
- Do NOT blindly retry the same command. First free the port or start on another port, e.g. `8002`.
- For automated checks, prefer `TestClient` smoke tests over live server startup when port availability is uncertain.

### Essential Folders (tracked in git)
- `src/` — backend source code
- `tests/` — pytest suite
- `assets/` — Thai fonts + Met Open Access artwork
- `raw/` — astrology/tarot source markdown
- `db/` — migrations + seeds
- `ephe/` — Swiss Ephemeris data

### Root Files (tracked)
- `pyproject.toml`, `uv.lock`, `README.md`
- `SYSTEM_FLOW.md` — this file
- `.github/workflows/ci.yml` — CI

### Not Tracked (`.gitignore`)
- `.venv/`, `__pycache__/`, `*.pyc`
- `.env`, `.data/`, `node_modules/`
- `frontend/`, `mobile/`, `out/`
- `scripts/`, `supabase/`, `docs/`
- Runtime artifacts: `astral.db`, `de421.bsp`
- Demo files: `frontend_demo.html`, `premium-sample.pdf`, `synastry-Mark-mai.pdf`
- CI/config: `codemagic.yaml`, `MOBILE_BUILD.md`

---

## High-Level Architecture

```
Client Request
     │
     ▼
FastAPI Router (src/main.py)
     │
     ├── /v1/fusion/grand/*            ← Grand fusion 18-science engine
     ├── /v1/bazi/*                    ← BaZi engine
     ├── /v1/vedic/*                   ← Vedic engine
     └── ...other routers
     │
     ▼
PDF Brain (src/services/weasy_brochure.py)
     │
     ├── render_brochure(sections, out_path, ...)
     │       ├── sections: [{"title": str, "lines": [str]}]
     │       ├── theme_hint: str → artwork mapping
     │       ├── biwheel / section_art / raw_section / raw_title
     │       └── WeasyPrint HTML → A4 PDF
     │
     ▼
PDF File (temp dir, returned as {ok, file, sections})
```

---

## Calculation Brains

### 1. chart_service — Western Natal Base
- `compute_chart(name, date, time, tz_offset_hours, lat, lon, system)`
- Returns: bodies, ascendant, midheaven, houses
- Used by: human design, composite, transit, synastry

### 2. grand_fusion — 18 Sciences Aggregator
- `compute_grand_fusion(name, lang)`
- Returns: person, reading (th/en), extended
- Sub-engines called inside:
  - fixed_stars, sabian, varshaphal, ziwei
  - asteroids, numerology, iching
  - ninestar_ki, mayan_tzolkin, cosmobiology
  - human_design, kalachakra

### 3. Service Engines
| Engine | File | Key Function |
|--------|------|--------------|
| Vedic | src/services/vedic_service.py | compute_vedic() |
| BaZi | src/services/bazi_service.py | four_pillars() |
| Human Design | src/services/grand/human_design.py | compute_human_design() |
| Ziwei | src/services/grand/ziwei.py | compute_ziwei() |
| Composite | src/services/composite_service.py | compute_composite() |
| Transit | src/services/fusion_engine.py | compute_transit_hits() |
| Muhurta | src/services/muhurta_service.py | find_windows() |

---

## Report Endpoints → Section Builders → PDF

| Endpoint | Engine | Section Builder | Theme |
|----------|--------|-----------------|-------|
| `/report/natal` | compute_chart | build_natal_sections() | natal |
| `/report/composite` | compute_composite | build_composite_sections() | composite midpoint |
| `/report/transit` | compute_transit_hits | build_transit_sections() | transit now |
| `/report/muhurta` | find_windows | build_muhurta_sections() | electional |
| `/report/synastry` | compute_synastry_profile | build_synastry_sections() | synastry |
| `/report/synastry-dual` | same | same | synastry dual |
| `/report/vedic` | compute_vedic | _vedic_sections() | vedic |
| `/report/bazi` | four_pillars | _bazi_sections() | bazi |
| `/report/human-design` | compute_human_design | _human_design_sections() | human design |
| `/report/ziwei` | compute_ziwei | _ziwei_sections() | ziwei |
| `/report/grand-summary` | compute_grand_fusion | _grand_sections() | grand summary |

Same engines/builders as above, but single-system standalone PDFs.
| Endpoint | Source Report |
|----------|---------------|
| `/brochure/natal` | natal |
| `/brochure/composite` | composite |
| `/brochure/transit` | transit |
| `/brochure/muhurta` | muhurta |
| `/brochure/synastry` | synastry |
| `/brochure/synastry-dual` | synastry-dual |
| `/brochure/vedic` | vedic |
| `/brochure/bazi` | bazi |
| `/brochure/human-design` | human-design |
| `/brochure/ziwei` | ziwei |

---

## Section Builder Output Shape

```python
# All builders return:
[
    {
        "title": "Section Title — Name",
        "lines": ["line 1", "line 2", ...],
        # optional:
        "html": True,           # if lines contain HTML (tarot cards)
    }
]

# Special cases:
# - synastry returns: (sections, tarot_html, tarot_title)
# - grand-summary returns: 5-7 sections from all systems combined
```

---

## PDF Generation Flow

```
render_brochure(sections, out_path, ...)
     │
     ├── 1. Pick cover art from assets/art/*.jpg via theme mapping
     ├── 2. Build HTML:
     │       ├── <div class='cover'> + cover image + credit
     │       ├── for each section:
     │       │       ├── <div class='section'>
     │       │       ├── <div class='title'>
     │       │       ├── <img class='cover-art'> (if section_art)
     │       │       └── <div class='line'> per line
     │       └── <div class='footer'>
     ├── 3. Apply CSS (_CSS + _font_faces())
     └── 4. WeasyPrint HTML(string=html, base_url=repo_root) → PDF
```

### Artwork Mapping
| Theme | Artwork |
|-------|---------|
| natal, vedic | venus_mars.jpg |
| bazi | cupid_psyche.jpg |
| human-design | venus_mars.jpg |
| ziwei | diana.jpg |
| grand-summary | venus_mars.jpg |
| composite | venus_mars.jpg |
| transit | diana.jpg |
| muhurta | cupid_psyche.jpg |
| synastry | venus_mars.jpg |

### CSS Theme
- Colors: gold `#9a7b34`, ivory `#f6f0e2`, ink `#3b3324`
- Thai fonts embedded from `assets/fonts/*.ttf`
- Cover: radial gradient + border + rounded corners
- Section: white card, soft gold border, line-height 1.7

---

## Key Files

| File | Role |
|------|------|
| `src/main.py` | FastAPI app, router includes |
| `src/routers/reports.py` | All report + brochure endpoints |
| `src/services/pdf_renderer.py` | Ground-up PDF renderer (WeasyPrint) + strict `sanitize_text()` 100% TH whitelist + `apply_narrative_gate()` |
| `src/services/tarot_service.py` | Tarot deck (78), `draw_spread()` deterministic seed, Thai meanings |
| `src/services/tarot_images.py` | Card-name → `NN.jpg` index + web URL map |
| `src/services/tarot_downloader.py` | Optional Rider-Waite image downloader (background, never blocks) |
| `src/services/narrative_gate.py` | TH/EN language gate (hard threshold 1.0) + narrative sanitizer |
| `src/services/narrative_sanitizer.py` | Garbled-token / stray-script cleaner |
| `scripts/build_combined_final.py` | **CLI builder: combined birth-chart + tarot PDF (chart-derived decor + real card art)** |
| `assets/art/myth/*.jpg` | Public-domain mythology decor images (Helios, Selene, Hermes, etc.) |
| `assets/tarot/sola-busca/*.jpg` | Rider-Waite card art (real, 78 files; originally shipped as blank templates, replaced) |
| `src/services/chart_service.py` | Western natal chart base |
| `src/services/vedic_service.py` | Vedic chart |
| `src/services/bazi_service.py` | BaZi four pillars |
| `src/services/grand/human_design.py` | Human Design |
| `src/services/grand/ziwei.py` | Ziwei Dou Shu |
| `src/services/grand/grand_fusion.py` | 18-science aggregator |
| `src/services/composite_service.py` | Composite chart |
| `src/services/fusion_engine.py` | Transit hits |
| `src/services/muhurta_service.py` | Muhurta electional |
| `assets/art/*.jpg` | CC0 artwork for covers/sections |
| `assets/fonts/*.ttf` | Thai font faces |

---

## Data Flow Example: `/report/grand-summary`

```
  payload: {name, date, time, tz_offset_hours, lat, lon, lang}
     │
     ▼
compute_grand_fusion(name, lang)
     │
     ├── person + birth from input
     ├── reading.th / reading.en from 18 engines
     └── extended metadata
     │
     ▼
_grand_sections(payload)
     │
     ├── Recompute: compute_chart, compute_vedic, four_pillars,
     │   compute_human_design, compute_ziwei
     ├── sections.extend(_vedic_sections(...))
     ├── sections.extend(_bazi_sections(...))
     ├── sections.extend(_human_design_sections(...))
     ├── sections.extend(_ziwei_sections(...))
     └── Append reading.th + reading.en as sections
     │
     ▼
render_brochure(sections, out_path,
    person_name=name, lang=lang, theme_hint="grand summary")
     │
     ├── Cover art: venus_mars.jpg
     ├── 7 sections with gold/ivory styling
     └── PDF ~4.7 MB
     │
     ▼
Return {ok: True, file: "/tmp/astral_grand_.../astral-grand-...pdf", sections: 7}
```

---

## Section Builder Contracts

### _vedic_sections(name, chart)
- Input: `compute_vedic()` output
- Output: 1-2 sections (TH interpretation + optional EN)

### _bazi_sections(name, chart)
- Input: `four_pillars()` output
- Output: 1 section (4 pillars + day master + zodiac_th)

### _human_design_sections(name, chart)
- Input: `compute_human_design()` output
- Output: 1 section (type, authority, profile, centers, channels, gates)

### _ziwei_sections(name, chart)
- Input: `compute_ziwei()` output
- Output: 1 section (life palace, body palace, lunar date)

### build_natal_sections(name, chart)
- Input: `compute_chart()` output
- Output: 1 section (Sun/Moon/Mercury + Ascendant narrative)

### build_composite_sections(name_a, name_b, chart_a, chart_b)
- Input: 2 natal charts + `compute_composite()`
- Output: 1 section (composite Sun/Moon/Asc)

### build_transit_sections(name, natal_chart, transits)
- Input: natal chart + `compute_transit_hits()`
- Output: 1 section (current transits narrative)

### build_muhurta_sections(action, windows)
- Input: muhurta windows list
- Output: 1 section (top 3 windows)

### build_synastry_sections(name_a, name_b, chart_a, chart_b, spread)
- Input: 2 natal charts + synastry profile + tarot spread
- Output: (sections, tarot_html, tarot_title)
- sections: 5 sections (overview, bonds, frictions, score, advice)

---

## Grand Summary Section Order

1. Vedic — {name} (from _vedic_sections)
2. Interpretation (from _vedic_sections)
3. BaZi — {name} (from _bazi_sections)
4. Human Design — {name} (from _human_design_sections)
5. Zi Wei Dou Shu — {name} (from _ziwei_sections)
6. th (reading.th from grand_fusion)
7. en (reading.en from grand_fusion)

---

## Payload Models

All in `src/routers/reports.py`:

```python
class NatalPayload(BaseModel):
    name: str
    date: date
    time: time
    tz_offset_hours: float = 7.0
    lat: float = 13.8591
    lon: float = 100.5217
    system: str = "tropical"

class SynastryPayload(BaseModel):
    a: NatalPayload
    b: NatalPayload
    spread: str = "three_card"

class VedicReportPayload(BaseModel):
    name: str
    date: date
    time: time
    tz_offset_hours: float = 7.0
    lat: float = 13.8591
    lon: float = 100.5217
    ayanamsa: str = "lahiri"

class BaZiReportPayload(BaseModel):
    name: str
    date: date
    time: time
    tz_offset_hours: float = 7.0
    lat: float = 13.8591
    lon: float = 100.5217

class HumanDesignReportPayload(BaseModel):
    name: str
    date: date
    time: time
    tz_offset_hours: float = 7.0
    lat: float = 13.8591
    lon: float = 100.5217

class ZiWeiReportPayload(BaseModel):
    name: str
    date: date
    time: time
    tz_offset_hours: float = 7.0
    gender: str = "female"

class GrandSummaryPayload(BaseModel):
    name: str
    date: date
    time: time
    tz_offset_hours: float = 7.0
    lat: float = 13.8591
    lon: float = 100.5217
    lang: str = "th"
```

---

## Response Shape

```python
class ReportPdfResponse(BaseModel):
    ok: bool
    file: str          # temp file path
    sections: int      # number of sections rendered
```

---

## Important Notes for Agents

1. **Always sync disk state first** — other Hermes sessions mutate `C:/AI` concurrently
2. **Pull before acting** — `git pull origin main` before any repo change
3. **Tests must pass** — 587/587 smoke green + 157/157 language-gate green before commit
4. **Memory is shared** — check `MEMORY.md` and `USER.md` for user preferences
5. **TH-only, no English** — user wants 100% Thai narrative, non-AI-slop, humanized
   (tarot-reader warm voice). `narrative_gate` enforces hard 1.0 TH purity;
   `sanitize_text` whitelist drops any EN/CJK fragment.
6. **Personal profiles are private** — never commit birth profiles to git
7. **PDFs are temp files** — returned path is in temp dir, copy if you need to keep
8. **WeasyPrint requires GTK** — installed in this environment, not portable
9. **Brochure endpoints mirror report endpoints** — same engine, same builder, different route
10. **Grand summary is the "all-in-one"** — use when user wants consolidated PDF

---

## Quick Command Reference

```bash
# Run tests
cd C:/AI/NEW-AI-REBORN && uv run python -m pytest -q

# Start server
cd C:/AI/NEW-AI-REBORN && uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

# Smoke test all report endpoints
cd C:/AI/NEW-AI-REBORN && uv run python - <<'PY'
from fastapi.testclient import TestClient
from src.main import app
client = TestClient(app)
routes = [
    # ... add all routes
]
for route, payload in routes:
    r = client.post(route, json=payload)
    print(route, r.status_code, r.json().get("ok"))
PY

# Check health
```

---

*Last updated: 2026-08-29 | Branch: main | Status: 430 tests passing*

---

## Birth Chart + Tarot Combined PDF Pipeline

A standalone CLI pipeline (not an API route) that produces a single bilingual-free
**100% Thai** PDF combining the natal chart reading AND a tarot spread for one person.
Built 2026-08-30; example output: `C:\AI\reports\astral-natal-1996-04-04-thai.pdf`.

### When to use
- User wants ONE PDF with chart + tarot, tarot-reader warm voice, Thai only,
  real card art, and a chart-derived decorative image.
- Output is a private local file (never commit to git).

### Pipeline shape
```
scripts/build_combined_final.py
   ├── 1. Load chart facts (TH prose: personality / positions / summary)
   ├── 2. Draw tarot deterministically
   │       tarot_service.draw_spread(name, spread="past-present-future",
   │                                seed=<birthdate int>) -> 3 cards
   ├── 3. Derive ONE decorative image from the WHOLE chart
   │       analyze dominant element (e.g. fire stellium in Aries)
   │       pick matching myth image (e.g. Helios/sun god) + TH WHY-caption
   ├── 4. Sanitize every string via sanitize_narrative(lang="th")
   │       100% Thai whitelist (Thai block + ASCII only; drops EN/CJK)
   ├── 5. Build HTML (weasyprint): cover, decor img+caption, sections,
   │       tarot section with real Rider-Waite <img> per card, summary, footer
   ├── 5b. Style via `scripts/pdf_premium.css` (dark-mystical theme: indigo-plum ground,
   │       gold-cream text, gold drop-cap + keyword highlights, starfield texture,
   │       gold-glow tarot frames, reversed cards rotated 180°). Fonts: Sarabun.
   └── 6. HTML.write_pdf() -> A4 PDF (verified 0 latin tokens)
```

### Critical rules learned (2026-08-30)
1. **REPO path**: builder in `scripts/`, so `REPO = Path(__file__).resolve().parents[1]`
   (NOT `parents[2]` — that resolves to `C:/AI` and silently breaks asset loading).
2. **Images use `file:///` URIs**, not `data:` URIs — weasyprint here drops base64
   data-URI images (PDF ends with 0 embedded images). Use `f"file:///{path.as_posix()}"`
   and pass `base_url=str(REPO)` to `HTML()`.
3. **Card art shipped as BLANK TEMPLATES** (English-labeled placeholders) in
   `assets/tarot/sola-busca/`. Replaced the 3 needed cards with real Rider-Waite art
   from Wikimedia Commons (public domain, via `api.php?action=query`). Templates are
   invalid for PDF (violate TH-only rule + render empty).
4. **Decorative image = DERIVED, not one-per-item.** Analyze the whole chart, pick the
   single best-fitting image, explain WHY under it. Do not stamp a myth image per planet.
5. **`narrative_gate.py` corruption risk**: a prior session overwrote it with chart
   text (SyntaxError). If `import src.services.narrative_gate` fails, restore via
   `git checkout -- src/services/narrative_gate.py` before building.
6. **Humanize the voice**: avoid AI-slop (em-dash overuse, rule-of-three, "testament"/
   "vibrant", bold-stuffing). Warm tarot-reader Thai, address user as "นาย",
   first-person "กระผม".
7. **weasyprint CSS pitfalls**: avoid `position: fixed` / `::before` absolute overlays
   (assertion crash in float layout) and `::first-letter { float: left }` (drop-cap
   float crash). Use `background-image` layers on `html,body` for starfield, and a plain
   large `::first-letter` (no float) for the drop cap. Rotate reversed cards via
   `transform: rotate(180deg)` on an img class.

### Thai tarot card name map (beautiful classical-reader voice)
Used by `th_card_name()` in `scripts/build_combined_final.py`. Avoid stiff
literal translations; use mythic/classical Thai.
```
MAJOR ARCANA (22)
  The Fool=เพลิงบ้า        The Magician=นักเล่นเวท     The High Priestess=นางสันโดษ
  The Empress=พระนางเจ้า   The Emperor=พระจักรพรรดิ   The Hierophant=มหาปุโรหิต
  The Lovers=คู่ตรัส       The Chariot=ราชรถ         Strength=ใจหาญ
  The Hermit=นักพรต       Wheel of Fortune=วงล้อวารี  Justice=ธรรมะ
  The Hanged Man=บุรุษแขวนกาย  Death=กรรม            Temperance=ศาสตร์สมดุล
  The Devil=มาร           The Tower=หอพัง          The Star=ดารา
  The Moon=จันทรา         The Sun=อาทิตยา          Judgement=พิพากษา
  The World=จักรวาล
MINOR ARCANA — suit names: Wands=ไม้เท้า Cups=ถ้วย Swords=ศาสตรา Pentacles=ทรัพย์
  ranks: Ace=หนึ่ง Two=สอง ... Ten=สิบ Page=มหาดเล็ก Knight=อัศวิน Queen=ราชินี King=ราชา
  e.g. Six of Pentacles=หกแห่งทรัพย์  Knight of Pentacles=อัศวินแห่งทรัพย์
        Three of Cups=สามแห่งถ้วย  Queen of Swords=ราชินีแห่งศาสตรา
```
1. Sync disk + verify `narrative_gate.py` imports cleanly (git checkout if broken).
2. Confirm/repair card art: `assets/tarot/sola-busca/{idx}.jpg` is real art
   (>50 KB, not blank template). Fetch from Wikimedia if missing.
3. Compute or load chart facts; write TH personality + positions + summary prose.
4. `draw_spread(name, spread="past-present-future", seed=birthdate)`.
5. Analyze chart -> choose 1 decor image + write TH WHY-caption.
6. Render with weasyprint using `file:///` image URIs, `base_url=REPO`.
7. Verify: `pypdf` extract -> assert 0 latin tokens >=3 chars; vision-check pages.
8. Deliver private local PDF; do NOT commit (birth profile is private).

---

*Last updated: 2026-08-30 | Branch: main | Status: 587 tests passing | TH-only combined PDF pipeline added*

## Known Issues / TODO
- **Ephemeris BSP missing**: `src/services/ephemeris.py` requires `de421.bsp` at import time.
  - Current repo does not include `de421.bsp`.
  - Skyfield attempts to download from `https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de421.bsp` which returns 404.
  - Effect: `tests/test_western.py` and any route importing `ephemeris` fails at collection/import.
  - Next step: find a valid BSP mirror or vendor a supported ephemeris file; do not change ephemeris engine until validated.
