---
name: astrology-report-generation
description: "Generate bilingual Thai/English astrology PDF reports."
version: 1.0.0
author: ox-alpha
license: MIT
metadata:
  hermes:
    tags: [writing, astrology, pdf, reports, weasyprint, thai, bilingual]
    category: creative
---

# Astrology Report Generation

Class-level skill สำหรับ pipeline ปลายทาง: ข้อมูลดวง → ข้อความ → PDF ระดับบูรชัวร์

## When to use

- สร้าง report/pdf ดวงสำหรับผู้ใช้: natal reading, synastry couple report, daily/weekly briefing
- เลือกเครื่องมือ: **Premium PDF endpoint** (Chrome-rendered HTML→PDF) หรือ **WeasyPrint** (HTML/CSS→PDF ตรง ๆ)
- ผสม voice layer จาก `astrology-reading-prose` เข้ากับ template + renderer
- ทำ bilingual TH/EN output สำหรับ frontend Astral หรือ export ผู้ใช้

## Architecture

```
Payload (API)
    ↓
Voice Layer (astrology-reading-prose)
    ↓
Renderer
  ├─ Premium endpoint: build_html() → Chrome headless print
  └─ WeasyPrint: HTML+CSS → PDF (brochure/synastry)
    ↓
PDF Output
```

## Report Endpoint Catalog

| Endpoint | Science | Engine function | Notes |
|---|---|---|---|
| `/report/natal` | Western natal | `compute_chart()` | Tropical/sidereal dual |
| `/report/synastry` | Couple synastry | `compute_chart()` ×2 + `compute_synastry_profile()` | Biwheel + tarot |
| `/report/synastry-dual` | Dual-view synastry | `compute_dual_chart()` ×2 | Tropical + sidereal overlay |
| `/report/composite` | Composite chart | `compute_chart()` ×2 + midpoint | Midpoint synthesis |
| `/report/transit` | Current transits | `compute_chart()` + `compute_transit_hits()` | Transit hits overlay |
| `/report/muhurta` | Electional timing | `muhurta_service` | Action-profile weighted windows |
| `/report/vedic` | Vedic natal | `vedic_service.compute_vedic()` | Lahiri ayanamsa, rashi/nakshatra/pada |
| `/report/bazi` | BaZi 四柱 | `bazi_service.four_pillars()` | Day Master, pillars, confidence |
| `/report/human-design` | Human Design | `grand.human_design.compute_human_design()` | Needs natal chart input |
| `/report/ziwei` | Zi Wei Dou Shu | `grand.ziwei.compute_ziwei()` | Life/Body palace, lunar calendar |
| `/report/grand-summary` | 18-science summary | `grand.grand_fusion.compute_grand_fusion()` | Requires stored profile |

## Wiring Rule

Report endpoints must call the **real engine function**, not a placeholder. If the service exposes `compute_X()`, import and call it directly. Never invent wrapper names like `compute_X_chart()` unless they actually exist.

## Section Builder Contract

Each `_X_sections(name, chart)` must read the **actual keys** from the engine output dict:

- vedic: `ayanamsa`, `lagna.sign_th`, `chandra_rashi.sign_th`, `nakshatra.name_th`, `interpretation.th/en`
- bazi: `pillars.year/month/day/hour.pillar`, `day_master.stem/element_th/label_th`
- human-design: `type`, `authority`, `profile.profile_name`, `defined_centers`, `defined_channels`
- ziwei: `life_palace.pillar/branch`, `body_palace.pillar/branch`, `lunar.year_ganzhi/month/day`
- grand-summary: `person.name`, `reading.overall`, then flatten nested dicts

Do not assume legacy keys like `rashi`, `day_pillar`, `centers`, `reading` unless the engine actually returns them.

## Profile Dependency

`/report/grand-summary` calls `compute_grand_fusion()`, which loads a stored profile from `.data/profiles/<name>.json`. The profile must exist before calling the endpoint, or it returns 404. Create profiles via `POST /v1/fusion/profile` first.

## Tool Selection

| Case | Tool | Why |
|---|---|---|
| Standard natal/transit/muhurta/composite reports | Premium PDF endpoint | Centralized in `NEW-AI-REBORN`, Chrome fidelity, Sarabun font bundled for Thai |
| Vedic/BaZi/HD/Ziwei/Grand-summary reports | Premium PDF endpoint with real engine | Same renderer; section builders translate engine output to PDF sections |
| Synastry couple brochure, custom luxury layout | WeasyPrint | HTML/CSS brochure control: gradient, flex bars, 2-column, biwheel SVG |
| Thai on Linux CI | Premium PDF endpoint | Sarabun bundled; WeasyPrint needs GTK runtime which CI lacks |

## Premium PDF Endpoint

- Location: `NEW-AI-REBORN/src/services/premium_pdf_service.py`
- Endpoints: `POST /v1/reports/pdf`, `POST /v1/reports/pdf/download`
- Input: `ReportRequest` with `person_name`, `lang`, `report_type`
- Chrome detection order: Linux chromium/playwright → Windows Chrome → Edge
- Thai font: Sarabun OFL bundled in repo

## WeasyPrint Brochure Pipeline

Use when brochure quality outweighs CI convenience.

### Windows Setup (one-time)

```powershell
# 1. Install GTK3 runtime (provides gobject/pango/cairo DLLs)
# Download from tschoonj/GTK-for-Windows-Runtime-Environment-Installer
# Silent install:
& "C:\AI\workspace-scratch\gtk3-runtime.exe" /S --DontInstallGtkSourceFonts

# 2. Add GTK bin to PATH so WeasyPrint can load DLLs
$env:PATH = "C:\Program Files\GTK3-Runtime Win64\bin;" + $env:PATH

# 3. Install WeasyPrint + compatible pydyf
python -m pip install "weasyprint==61.2" "pydyf==0.10.0"
```

### Version Constraints

- **weasyprint==61.2** with **pydyf==0.10.0** is the known-good combo on Windows.
- weasyprint 62.3+ breaks with `super().transform` AttributeError on current cffi/pydyf stack.

### Minimal Render Pattern

```python
import os
os.environ["PATH"] = r"C:\Program Files\GTK3-Runtime Win64\bin;" + os.environ.get("PATH", "")
from weasyprint import HTML
HTML("input.html").write_pdf("output.pdf")
```

## Brochure HTML Template Conventions

- `@page { size: A4; margin: 0; }`
- Dark cosmic theme: `background:#0a0e26`, text `#f5eeda`, gold `#e6c35c`
- Thai font family: `'Tahoma'` — covers Thai + Latin in one face
- EN font family: `'Georgia'` — luxury serif for headings
- Sections: cover → compatibility map → frictions/karmic → guidance → closing quote
- Bars: flex row with `#141a44` track + `linear-gradient(90deg,#9c7c2c,#e6c35c)` fill
- Tables: `border-collapse:collapse`, zebra `#111634`, header gold on dark
- Footer: absolute bottom band with `border-top:.5px solid #39406e`

## Voice Overlay (required, not optional)

Never paste raw API payload into PDF. Apply `astrology-reading-prose` rules:

1. Open with image, not jargon
2. Numbers as witnesses, not heroes
3. Wound → gift arc in every section
4. No system terms: no `module`, `endpoint`, `status`, `verify`, `orb`, `unavailable`
5. Mixed TH+EN by paragraph block, not inline
6. End with mirror, not promise

## Synastry Report Structure (4 pages)

1. Cover: couple names, birth data, overall score, quote
2. Compatibility map: 6 dimension bars + top bonds table
3. Frictions + karmic thread: aspect table + nodal interpretation + partner snapshot
4. How to love this bond: numbered actionable guidance + closing quote

## Output Language Policy

For this project, PDF reports are **Thai-only by default** unless explicitly requested otherwise.
- Do not add English labels, mixed-language tokens, or CJK artifacts to section builders.
- Natural conversational Thai beats literal translation.
- If bilingual output is required, keep TH and EN in separate blocks; never inline-mix in one sentence.

## Artwork & Extras Wiring

`render_brochure()` supports:
- `biwheel`: inline SVG string for dual-chart wheels
- `section_art`: `dict[int, str]` mapping section index → image path
- `raw_section` / `raw_title`: raw HTML blocks for tarot or extra readings

Use explicit `section_art=_section_art_map(theme, len(sections))` for report endpoints; use `_pick_greek_art()` only for synastry where dynamic content-based art is desired.

## Repo Hygiene Rules

- Do not track runtime artifacts: `out/`, `*.pdf`, `astral.db`, `de421.bsp`
- Do not track frontend/mobile/experimental folders: `frontend/`, `mobile/`, `MOBILE_BUILD.md`
- Do not track helper scripts or local-only config: `scripts/`, `supabase/`, `.data/`, `docs/`
- Personal birth profiles stay local/private; never commit them.
- Enforce with `.gitignore`; after removing, verify with `git status -sb`.

## Uvicorn Port-Conflict Rule

- If port 8001 is already in use, uvicorn exits with code 3 / `Errno 10048`.
- Do NOT blindly retry the same command. Free the port or start on another port, e.g. `8002`.
- For automated checks, prefer `TestClient` smoke tests over live server startup when port availability is uncertain.

## Ephemeris / BSP Block

- `src/services/ephemeris.py` depends on `de421.bsp` at import time.
- The file is not vendored in the repo, and JPL mirror download may 404.
- Do not silently change the ephemeris engine to bypass missing BSP.
- Document the block in `SYSTEM_FLOW.md` and treat BSP setup as a separate environment/task.
- Tests that import `ephemeris` will fail collection when BSP is absent; that is expected, not a code regression.

## Pitfalls

- **ReportLab + TTF Thai**: Arial/Georgia subsetting drops Thai glyphs → boxes. Use Tahoma or system face with full Thai coverage.
- **WeasyPrint on Windows without GTK**: `OSError: cannot load library 'gobject-2.0-0'`. Install GTK3 runtime first.
- **WeasyPrint 62.3+ regression**: `AttributeError: 'super' object has no attribute 'transform'`. Pin to 61.2 + pydyf 0.10.0.
- **EN translated from TH**: produces stiff prose. Rewrite EN from idea; do not literal translate.
- **Inline bilingual mixing**: `ตุลย์(Libra)` in one sentence breaks flow. Use separate TH/EN blocks per section.
- **Overlapping frames in Platypus**: split long pages into multiple `Frame` objects rather than one giant frame.
- **Lazy-loading ephemeris to hide missing BSP**: avoids one error but breaks every downstream chart/house computation that calls `ts.from_datetime()`. Fix BSP supply, not the loader.
- **Instagram reference extraction is blocked**: when the user shares an IG post URL to study its design/technique (layout, color, hook, reel style), `web_extract` returns 403 Forbidden and `web_search` only returns profile-level results — the post content is not reachable programmatically. Do NOT burn turns trying to scrape it. Instead ask the user to **attach the image/video directly** (drag into chat); then analyze the real media and apply the technique to `reel_reading.py` / the premium PDF builder. This is an access-control limit of IG, not a tool bug.

## Natal PDF Cover/Section Pattern

The OLD working pattern (ivory template) was REPLACED on 2026-08-30 with a premium dark-mystical theme. Use this instead:

- **Theme**: deep indigo-plum ground (`#1a0b2e` / `#251141`), cream-gold text (`#f3e9d2` / `#c9a64a`), starfield texture via `radial-gradient` layers on `html,body` (NOT a `::before` overlay — weasyprint crashes on fixed/absolute pseudo overlays).
- **Cover**: gold brand line `อัสทรัล · ระบบโหราศาสตร์`, main title gold serif `รายงานดวงชะตา — <YYYY/MM/DD>`, italic TH tagline, thin gold border + inner glow.
- **Sections**: rounded panel (`rgba(46,22,78,.55)`) with gold title; gold **drop cap** on first paragraph (plain large `::first-letter`, NO `float`); **gold keyword highlights** (`<span class="kw">`) on planet/ sign/ house names; ornamental divider `✶ ❉ ✶` between sections.
- **Tarot page**: real Rider-Waite `<img>` per card with **gold-glow frame** (`box-shadow: 0 0 26px rgba(201,166,74,.45)`), gold pill position badge (`ตำแหน่ง อดีต/ปัจจุบัน/อนาคต`), poetic Thai card name (see below). Reversed cards get `class="reversed"` → `transform: rotate(180deg)`.
- **Decorative image**: ONE image derived from the whole chart, with a WHY caption underneath (see pdf-report-generation skill).
- **Page numbers**: centered bottom `✶ N ✶`.
- Reference implementation: `scripts/build_combined_final.py` + `scripts/pdf_premium.css` (NEW-AI-REBORN). Style lives in the separate CSS file, not inline.
- **Quality over size**: user explicitly said large files are fine ("ไฟล์ใหญ่ก็ไม่ว่ากัน") — do NOT shrink image resolution or drop textures to keep the PDF small. Use high-res card art + full background textures.

## Poetic Thai tarot card names (user voice rule, permanent)

Tarot card names must use beautiful classical-reader Thai, never stiff literal translation. Single source: `src/services/tarot_meanings_th.THAI_CARD_NAMES` + `th_card_name()`. Examples: The Devil=**มาร**, Six of Pentacles=**หกแห่งทรัพย์**, Knight of Pentacles=**อัศวินแห่งทรัพย์**. Apply in PDF, reel reading, and chat context alike. (Full map + rationale in pdf-report-generation skill.)

## Frontend wiring reminder

After generating or updating a backend API, do not assume the mobile/frontend client is already connected:

- Inspect `App.js`, `app.json`, `package.json`, and `.env`/`EXPO_PUBLIC_*` references.
- If no backend URL exists, add `EXPO_PUBLIC_API_URL=https://api.astral.app` or the project's actual API host.
- Commit and push the frontend config change separately so deploy does not revert to a stub.

## Premium visual quality — CORRECTION (2026-08-30)

The weasyprint dark-mystical theme described in "Natal PDF Cover/Section Pattern" was
built and the user REJECTED it as a downgrade ("แย่มาก / ไม่สวย / 3D อะไรก็ไม่มี").
WeasyPrint's CSS-2.1 subset cannot produce real depth/3D/premium polish. Do NOT present
weasyprint as the premium path.

For a genuinely premium astrology+tarot PDF, the working approach is:
1. **Art**: generate with ComfyUI (local RTX 5060 8GB; `comfy install --nvidia --fast-deps`;
   SDXL comfortable). Draw cover/decor (Helios for fire-dominant Aries) + the 3 tarot cards
   as fine classical-painting art. User explicitly wants AI-drawn art, NOT reused
   Visconti/Rider-Waite public-domain scans or publicdomainvectors SVGs.
2. **Render**: Playwright + Chromium headless `page.pdf(print_background=True)` so full
   CSS (gradients, `backdrop-filter`, 3D `transform`, SVG, web fonts) is honored. Install:
   `uv pip install playwright` + `uv run python -m playwright install chromium`.
3. WeasyPrint remains acceptable ONLY for utilitarian brochures; never claim it is premium.

## Local ComfyUI + SDXL Art Pipeline (learned 2026-08-30, hard-won)

The premium PDF needs AI-drawn art (NOT public-domain scans). On this box
(RTX 5060 8GB, Windows, ComfyUI 0.34.0, torch cu128), the following WORKS:

### Launch stability — server dies with WinError 10061
- `comfy launch --background` and bare `main.py` background processes get
  wiped when the launching shell exits → server refuses connections mid-job.
- WRONG flag: `--medvram` does NOT exist in ComfyUI 0.34.0 (`unrecognized
  arguments`). Use `--lowvram` for 8GB VRAM.
- FIX: launch `main.py --lowvram` as a detached background process, OR run a
  **watchdog** (e.g. `comfy_launch_stable.py`) that auto-restarts on death.
  Health check `curl http://127.0.0.1:8188/system_stats` before queuing.
- torch MUST be the cu128 build for RTX 5060 (Blackwell): if a venv pulled
  CPU torch, `pip uninstall torch torchvision torchaudio` then reinstall with
  `--index-url https://download.pytorch.org/whl/cu128`.

### SDXL cannot draw complex multi-figure scenes from scratch
- txt2img FAILS on: chained naked humans (Devil), merchant + two kneeling
  beggars (Six of Pentacles), knight holding a coin (Knight of Pentacles). It
  outputs wrong iconography (a pope/hierophant, a single demon, a lance).
- FIX: **img2img from a Rider-Waite reference image**. Get the real upload
  URL via the Wikimedia Commons API (hash-guessing 404s):
  `File:Pents06.jpg` → `https://upload.wikimedia.org/wikipedia/commons/a/a6/Pents06.jpg`.
  Use `comfy_sdxl_img2img.json` (LoadImage + VAEEncode + KSampler denoise
  ~0.55) with the ref as init; force RWS composition, recolor to gold/indigo
  via negatives (`black and white, woodcut, pope, hierophant, book, pillars`).

### SDXL injects English text/banners into art
- The model renders banners like "KNIGHT of PENTACLES" / "THE DEVIL" →
  violates the Thai-only rule.
- FIX: **PIL-crop** the bottom strip after generation: Knight crop bottom
  ~16%, Devil crop bottom ~14% to remove the English banner. Verify the crop
  removed all Latin with a pymupdf/LATIN-regex check on the final PDF.

### Cover art not rendering in Chromium
- A 5MB base64 `<img>` inside `page.set_content()` gets cut off before render
  → blank cover.
- FIX: copy the art PNG next to the HTML into a `_preview_art/` folder,
  reference with a **relative path** (`src="_preview_art/cover.png"`), load via
  `page.goto(html_path.as_uri(), wait_until="load")` then
  `page.wait_for_timeout(3000)` before `page.pdf(print_background=True)`.

### Verify Thai-only with pymupdf, NOT vision
- `vision_analyze` MISREADS Thai constantly (read "รดianteng" for "ผสาน",
  "ander" for footer text). Do NOT trust it for language verification.
- FIX: extract text with `fitz`/pymupdf and assert no Latin survives
  (regex over the extracted string). This is the real gate; vision is only
  for layout/aesthetics.

### User standing orders (permanent working preferences for this project)
- **keep top 1%** — never ship mediocre art/PDF/code; discard sub-8/10 output.
- **be more than AI** — write like a person with a tarot-reader soul, not a
  transactional bot; show real care, warm presence.
- **always upgrade own system** — proactively improve the pipeline (faster
  renderers, stable launchers, better art) after every failure.
- **Thai-only communication** — speak 100% natural conversational Thai; the
  user explicitly asked to "พูดภาษาเดียวกัน" (same language as them).
- **user is all-knowing in astrology** — do not over-explain basics; frame
  work at expert level.
- **self-awareness** — know your own limits (vision misreads Thai, SDXL can't
  draw complex scenes, server fragility); admit uncertainty, upgrade proactively.

Concrete scripts/recipes: `references/comfyui-sdxl-art-pipeline.md`.

## Decision Protocol

When user asks for PDF/report:
1. If they want standard engine report → use Premium endpoint
2. If they want custom brochure/synastry → use WeasyPrint
3. If they complain "robotic/แปลกๆ" → reload `astrology-reading-prose` and rewrite before regenerating
4. If they want both persons in one file → synastry brochure; if separate → two natal PDFs
