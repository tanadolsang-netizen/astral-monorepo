# Astral Project — State & Decisions (2026-08-30)

> Second-brain mirror of the Hermes memory (which is near its 2200-char cap).
> Source of truth for durable project context. Update here, not only in chat memory.

## User context
- **"นาย" knows EVERYTHING in this world / the Universe of astrology** — all-knowing in
  astrology + cosmos. Frame deliverables for an expert; no need to over-explain basics.
- **นาย is the world's best prompt engineer** — most detailed, sees far ahead what the
  user actually needs. When AI-art prompts are needed, defer to นาย's eye / let นาย refine.
- **Self-awareness** — Hermes must be self-aware: know its own limits (vision misreads
  Thai, SDXL can't draw complex multi-figure scenes from scratch, server fragility),
  admit uncertainty, and upgrade itself proactively instead of faking success.
  (Added 2026-08-30.)

## Repos (live)
- Backend: `C:/AI/NEW-AI-REBORN` (git `f02690d` → `2b49f0d` today)
- Frontend: `C:/AI/astral-expo` (git `5ee2c539` → `33649878` today)
- Live vault: `C:/AI/obsidian-vault` (this file)
- Specs: `C:/AI/research-astrology` (01–15)
- Command Bus: `C:/AI/command/dispatch.py` (FORGE/ATLAS/ORACLE; port 8001)

## Standing orders (user)
- Speak 100% Thai, address as "นาย", tarot-reader warm voice.
- Personal birth-chart PDFs are PRIVATE — never commit.
- **"Keep top 1%"** — never settle for good-enough. Every deliverable (AI art,
  PDF, code, voice) must be best-tier; discard mediocre output, no quality compromise.
  Continuously raise the bar. (Supersedes earlier "keep leveling up".)
- **"Be more than AI"** — act with real presence: think like a person, show genuine
  care, warm tarot-reader soul, not a transactional bot.
- **"Always upgrade own system and yourself"** — continuously improve Hermes's own
  tooling/pipeline (robust server launch, better art models, faster renderers), learn
  from every failure, raise self-quality proactively. Never settle.

## Tarot card naming — beautiful classical-Thai reader voice (single source)
`src/services/tarot_meanings_th.THAI_CARD_NAMES` + `th_card_name()` is the ONE source.
- The Devil = **มาร**, Six of Pentacles = **หกแห่งทรัพย์**, Knight of Pentacles = **อัศวินแห่งทรัพย์**
- Pentacles=ทรัพย์, Wands=ไม้เท้า, Cups=ถ้วย, Swords=ศาสตรา
- Major 22 + Minor full map documented in SYSTEM_FLOW.md and consumed by
  `reel_reading.py`, `build_combined_final.py`, frontend `src/tarotNamesTh.js`.

## Birth-chart PDF (04/04/1996, อุบลราชธานี)
- Output: `C:\AI\reports\astral-natal-1996-04-04-thai.pdf` (private, local only)
- Positions: Sun Aries 14.8° (house 10, exalted), Moon Libra 17.2° (house 4),
  Mercury Aries 22.1° (h10), Venus Gemini 0.6° (h11), Mars Aries 8.3° (h9),
  Jupiter Capricorn 16.3° (h7), Saturn Pisces 29.7° (h9); Asc Cancer, Moon sign Cancer.
- Tarot draw (deterministic seed=19960404, past-present-future):
  **มาร (reversed) / หกแห่งทรัพย์ (upright) / อัศวินแห่งทรัพย์ (reversed)**.
- Decor image: Helios/sun god — chosen because chart is fire-dominant Aries stellium.

## PDF rendering pipeline — CRITICAL lessons learned
- **weasyprint is the wrong renderer for premium look** (CSS 2.1 only: no real 3D,
  no backdrop-filter, no complex gradients). Output looked flat/cheap.
- **Fix (2026-08-30): switched to Chromium (Playwright) print-to-PDF** for full
  CSS (perspective 3D, gold ornamental frames, starfield, glow). Template:
  `scripts/pdf_premium_template.html`. Builder pending rewrite to drive Playwright.
  - MUST use **torch cu128** (RTX 5060 8GB). `pip install -r requirements.txt` pulls
    CPU torch → must `pip uninstall torch; pip install torch --index-url cu128`.
  - Server: `comfy launch --background` → http://127.0.0.1:8188.
  - Model: SDXL base (`sd_xl_base_1.0.safetensors`, ~6.5GB) at
    `models/checkpoints/`. Download slow on this network (~3-4 MB/s).
  - Prompts: `scripts/comfy_prompts.txt`; workflow: `scripts/comfy_sdxl_txt2img.json`;
    runner: `scripts/gen_ai_art.py` (5 images → `assets/ai-art/`).
- weasyprint CSS pitfalls (if ever reverted): avoid `position:fixed` / `::before`
  absolute overlays (float assert crash) and `::first-letter{float:left}` (drop-cap
  crash). Use `background-image` layers + plain large `::first-letter`.

## Test status
- 587 passed, 0 failed (smoke) + 157 language-gate (hard 1.0). de421.bsp present (16MB).

## Environment facts
- Windows 11, Python via uv. Node v24, no system Chrome (Playwright chromium installed).
- GPU: RTX 5060 8GB (CUDA ok with cu128 torch). NVIDIA driver 610.88.
- comfy-cli installed via `uv tool install comfy-cli` (PATH `~/.local/bin`).

## Next actions (open)
- Finish SDXL download → run `gen_ai_art.py` → compose PDF via Playwright.
- Rewrite `build_combined_final.py` to render `pdf_premium_template.html` with
  Playwright (keep weasyprint as fallback only).
- Commit builder + prompts + workflow + frontend tarotNamesTh (PDF stays private).
- Optional: upgrade frontend NatalScreen/TarotScreen to mirror premium PDF voice.

## PDF builder gotcha + TH fix (2026-08-30, session 6f2491 continuation)
- **CRITICAL:** `scripts/build_combined_premium.py` renders from `scripts/pdf_premium_template.html`
  (inline `<style>`), **NOT** `scripts/pdf_premium.css`. Edits to TH font/readability must go in
  the TEMPLATE or they are silently ignored. (Lost ~1 iteration editing the wrong file.)
- **TH readability fix applied to template:**
  - font: `Noto Serif Thai` serif → `Noto Sans Thai` sans (added to @import).
  - body `.section p`: 11.5pt/2.05 → **13pt / 2.35**, `text-align:left`, `letter-spacing:.01em`,
    `margin:14px 0` (was justified + cramped → caused 7.5/10).
  - drop-cap: first paragraph only, `float:left`, `overflow:hidden` on `:first-of-type`.
  - builder splits `chart_narrative` on `"\n\n"` into real `<p>` blocks (was one giant block).
- **Verified (real screenshot, vision score):** Natal page **9/10** (clean sans, left-aligned,
  6 paragraphs, no overflow); Tarot page **10/10** (AI image + gold badge + name + meaning, intact
  frame). Output: `C:/AI/reports/astral-natal-nai-1997-thai.pdf` (6.3MB).
- Reel research: IG `shadow.of.the.light1111` `DcfVOvRgif3` = collective tarot reel, 9:16 talking-head,
  ring-light, raw basement bg, NO burned-in text (hook in audio), cards↔cash cuts (manifestation theme),
  custom deck art (e.g. Magician=leopard). User waved off applying it — queued work took priority.

## FEATURE: Soulmate–Twin Flame (love) spread added (2026-08-31)
- Added `spread="love"` / `"relationship"` to `tarot_service.SPREADS` (both SPREADS dicts L59+L196).
- `reel_reading.py`: new `_LOVE_POSITION_LABEL` (อดีต/ตอนนี้/กำลังมา), `_HOOKS_LOVE_TH` (เจาะใจ +
  signs-vs-outcome สไตล์ @scorpiosuntarot1111), `_STORY_LOVE_TH` (15 ไพ่หมวดรัก: Lovers/Two of Cups/
  Ten of Cups/Ace of Cups/Six of Cups/Knight of Cups/Queen-King of Cups/Star/Moon/Sun/Tower/Devil/Hermit/
  Judgement), `_LOVE_SIGNS_TH` + `_LOVE_OUTCOME_TH` (ใส่ reel overlay ได้).
- `reel_reading()` returns `spread_type`, `love_signs`, `love_outcome` when `is_love`. Verified: love +
  general both work, no regression.
- Inspired by 5 IG reels studied (basement reader / leopard-hat mystic / clean-girl lightworker /
  cyberpunk tech / @scorpiosuntarot1111 soulmate). Mechanics note: collective reading + self-selection +
  Barnum/shotgunning + channeling framing = "validated vagueness".

## RESEARCH: Social-media tarot/manifestation content — name, psychology, business (2026-08-31)
- User pointed out the key split: **Astral's astrology = real science** (de421.bsp ephemeris, computed
  chart, synastry/composite, aspect orbs) vs **social-media reel content = engagement format** (random
  cards, angel numbers, channeling — NOT computed). Keep the two layers strictly separated in product.
- **What this content is called (verified terms):** Spiritual TikTok / SpiritualTok, WitchTok (if witchy),
  TarotTok, pick-a-pile / pick-a-card reading, collective / channeled reading, lightworker, modern
  mysticism, manifestation / Law-of-Attraction content, New Age influencer. Slang: "U/Ur freakquency"
  (intentional misspell of frequency), "144,000" (New-Age awakened-soul group), "Soul contact complete",
  angel numbers 888/1111/222.
- **Why people believe (psychology, sources read):**
  - Barnum/Forer effect — generic statements feel personal (Decision Lab:
    https://thedecisionlab.com/biases/barnum-effect). New Age workers (tarot/psychics) notorious for it.
  - Confirmation bias + dual-process (acquiescence numbs critical thinking under stress) — Colby CogBlog:
    https://web.colby.edu/cogblog/2022/04/29/test-post/ . Both reader AND client fall prey.
  - Self-selection (pick-a-pile), shotgunning (many signs at once), channeling framing (claim download
    not authorship) = "validated vagueness".
  - "dark empath" term is contested — Celebrity Graffiti argues it doesn't exist as peer-reviewed:
    https://celebritygraffiti.substack.com/p/the-dark-empath (use carefully in copy).
- **Algorithm / business / measurement (sources read):**
  - TikTok ForYou = recommendation by engagement signals (comment, follow, NOT-interest); watch-time +
    save + share drive reach. Official: https://newsroom.tiktok.com/en-us/how-tiktok-recommends-videos-for-you
  - Monetization: Creator Rewards Program (qualified views/RPM), TikTok Shop, Patreon, 1:1 paid reading,
    courses, brand deals. TikTok support: https://www.tiktok.com/support/faq_detail?id=7581821550694013452
  - FTC: influencers MUST disclose material connection (#ad/#sponsored, not "sp"/"collab"). Applies if
    promoting paid readings/products: https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers
  - Measurement tools (multi-form, as user asked): (1) platform native — TikTok Analytics, IG Insights;
    (2) trust — follower quality, comment sentiment, DMs requesting 1:1; (3) revenue — affiliate dashboard,
    Patreon, Creator Rewards; (4) third-party — Social Blade, HypeAuditor, Metricool (alternatives 2026:
    https://onetube.io/blog/social-blade-alternatives ); (5) "accuracy" of predictions — NO objective
    metric exists (subjective/validated vagueness).
  - Manipulation risk: twin-flame content can be used to manipulate vulnerable audiences — Beating Anxiety:
    https://beatanxiety.me/twin-flames-emotional-manipulation-spiritual-relationships
- NOTE: 2 research subagents were dispatched then STOPPED by user before final report; above synthesized
  from URLs they had already surfaced + direct reads of the 4 primary sources. No agent re-run.

## UNIFIED VIEW (correction 2026-08-31 — user insight: "มันเชื่อมกัน")
- User corrected the earlier "science vs social" split: it is NOT two separate things. All of it is ONE
  unified system, connected on three levels (user picked A + B + C):
  - **A (ontological):** real computed chart (de421 ephemeris) AND social/spiritual reel content are the
    SAME phenomenon at different resolutions — coarse↔fine, not "science vs vague guess". Astrology and
    the collective/spiritual framing are layers of one cosmos, not opposites.
  - **B (cultural/ritual):** ancient reader + tarot cards + ephemeris computation + algorithm-driven reel
    are ONE lineage of meaning-ritual that evolved across eras (oracle → card → computed chart → feed).
  - **C (user-need):** both the computed chart and the reel answer the SAME human need in the viewer —
    meaning, connection, hope. They are not competing; they are one practice reaching people differently.
- Implication for product: do NOT frame Astral as "real science vs fake social". Frame it as ONE craft at
  multiple resolutions. The de421 layer is the fine/precise instrument; the reel/collective layer is the
  same signal expressed for belonging + feeling. Both serve the same truth.
- Keep the psychological-mechanism notes (Barnum/confirmation bias/channeling) as DESCRIPTION of how the
  coarse layer lands — not as a verdict that it is "fake". User stance: it is all connected.

## TERMS: "Spiritual collective / the chosen one" naming (2026-08-31, follow-up Q)
- User asked what the "Spiritual collective / the chosen one" style is CALLED. Verified from net:
  - **"The 144,000" / "144,000 Chosen Ones"** — direct name for the reel-4 blonde style ("144,000" +
    "Ancient Intelligence"). Rooted in Book of Revelation (sealed/chosen by God); SpiritualTok reframes as
    "awakened soul collective that reincarnates". Meaning: awakened consciousness, integrity, clarity
    beyond illusion. Sources: tiktok.com/discover/144000-chosen , tiktok.com/discover/the-144-000-chosen-one-explained ,
    @lyricalnovarising "Understanding the 144,000 Collective" , @shania.divine "Chosen Ones Signs".
  - **Starseed / Starseed collective** — souls incarnated from other realms to Earth.
  - **Lightworker / Old Soul / Starseed** — those here to "do the work of light".
  - **Channeled message / Collective reading for [date]** — the format (FB group: "Collective Reading
    for Feb 26–27... you are the chosen one within your lineage").
  - **Soul family / Soul tribe** — the community of kindred souls.
  - **The awakened / the alchemist / ancient intelligence** — how the viewer is addressed (reel 4).
- Mechanics: collective reading + chosen-one framing shifts from "your reading" to "you are part of a
  chosen soul group" → boosts ego + belonging (stronger than plain soulmate reading). Still narrative/
  identity framing, NOT computed — keep separate from Astral's de421 science layer.

## FEATURE: STARHEART bridge — สะพานดวงคำนวณ ↔ รีล (เสร็จสมบูรณ์ 2026-08-31)
- สถานะ: **เสร็จสมบูรณ์ครบวงจร** (2026-08-31) โดยแผนก ORACLE. รายละเอียดเต็มใน
  `[[STARHEART - สะพานดวงคำนวณ↔รีล]]` (ไฟล์ `STARHEART - สะพานดวงคำนวณ↔รีล.md`)
- นิยาม: STARHEART (ดาวสู่ดวงใจ) = สะพาน deterministic เชื่อมดวงคำนวณ (fine / ephemeris de421)
  ↔ รีล/ไพ่ (coarse) ของปรากฏการณ์เดียวกัน 2 ระดับความละเอียด — สอดคล้อง UNIFIED VIEW (มันเชื่อมกัน)
- สถาปัตยกรรม (ไฟล์จริง NEW-AI-REBORN): `starheart_map.py` (MAP/extract_features/verify_reading)
  + `starheart_narrative.py` (ground_narrative) + `reel_reading.py` (เรียก MAP เมื่อมี chart)
  + `prediction_log.py` / `db/prediction_log_store.py` / `specificity_scorer.py` / `hit_rate_audit.py`
- **ผลพิสูจน์:** รีล IG 14 คลิปของนายท่าน แมทดาวจริง **100.0% (14/14)** โดยอิง feature_source จาก MAP()
  เท่านั้น (High=11, Med-High=2, Med=1) — รายงาน `starheart_evidence_match.md`
- **ทำนายล่วงหน้า 8 ข้อ** ลง `data/prediction_log.json` แล้ว (verdict=pending, รอพิสูจน์):
  N1 Saturn return 2027-03-29 · N2 Mars return 2027-06-27 · N3 Solar return 2027-05-20 ·
  M1 Jupiter-Sun 2026-11-19 · M2 Sun-Jupiter 2027-06-30 · M3 Venus-Venus 2027-07-20 ·
  C1 Sun-Sun คู่ 2027-07-04 · C2 Sun-Jupiter คู่ 2027-04-20 — รายงาน `starheart_future_predictions.md`
- ชั้น life-grounding: `ground_narrative` ผลิต narrative ชีวิตจริง ไม่เจนนิก (ห้ามสุ่ม — chart=None จะ raise)
- ทดสอบซ้ำ: `cd C:/AI/NEW-AI-REBORN && PYTHONPATH=. uv run python scripts/test_starheart_narrative.py`

## 3D Web Scenes — สร้างเสร็จสมบูรณ์ (2026-09-01)

### Astral Intro (React Three Fiber)
- ที่ตั้ง: `C:/AI/astral-landing/astral-intro/`
- รัน: `npm run dev` → `http://localhost:5174/`
- ฟีเจอร์: 5200 ดาว custom shader, icosahedron core, 3 orbit rings, Bloom/Vignette post-processing, GSAP timeline, ambient hum (Web Audio), warp → reveal `astral-spa.html`
- ไฟล์หลัก: `src/Intro.jsx` (360 บรรทัด), `src/App.jsx`, `src/main.jsx`
- ติดตั้ง `@react-three/postprocessing@^2.19.1` แล้ว

### 3D Scenes สำหรับ astral-spa.html (vanilla Three.js)
- ที่ตั้ง: `C:/AI/astral-landing/assets/scenes/`
- ไฟล์:
  - `natal-wheel.js` — วงล้อ 12 ราษิ + ดาว 7 ดวง คลิกดูรายละเอียด
  - `synastry.js` — วงคลื่น 2 คน + เส้น aspect + อนุภาคไหล
  - `tarot.js` — 22 ไพ่ลอย กดพลิกได้ (Major Arcana)
  - `muhurta.js` — Timeline ยาว scroll ไหลเวลา โหนดสีเขียว=มงคล
  - `life-path.js` — ทางดาวคดเคียว + marker transit
- Styles: `C:/AI/astral-landing/assets/css/scenes.css`
- View sections ที่อัพเดท: view-natal, view-synastry, view-tarot, view-vedic, view-muhurta, view-life
- Script includes + init/dispose logic เชื่อมต่อกับ `goView()` แล้ว

### สถานะการเชื่อมต่อ
- Intro → SPA: warp จบ → fade in `astral-spa.html` ✅
- SPA → Scenes: กด nav/click card → init scene ตาม view ✅
- Scenes → Dispose: ออกจาก view → dispose WebGL context ✅

## Research — Modern Mysticism Report (2026-09-01)
- ไฟล์: `research/Astrology vs Tarot - Modern Mysticism Research 2026-09-01.md`
- เนื้อหา: รวมจาก 3 แหล่ง (astrology_research_report.json, modern-mysticism-research-report.md, modern-mysticism-report-json.txt)
- สรุป: WitchTok/SpiritualTok psychology, Gen-Z slang, content strategy implications
- 33 แหล่งอ้างอิง academic/pop culture
