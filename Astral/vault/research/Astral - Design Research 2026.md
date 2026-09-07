# Astral — Design Research 2026

> ⭐ **NORTH STAR (ยึดตาม session Astrology data and Research Department):**
> *"รวบรวมทุกศาสตร์เข้าด้วยกัน เป็นอันเดียว สำหรับแอพดูดวงที่โครตจะแม่นที่สุดของเรา ทุกด้านในชีวิต ปัจจุบัน ต้องแม่น — ไม่ต้องให้ user ไปเดาเอาเอง"*
> ทุก design decision ในเอกสารนี้ต้องรับใช้ภารกิจนี้: **accuracy-first · present-moment · zero self-interpretation**
> Engine specs: `C:/AI/research-astrology/` (01-transits · 02-vedic · 03-synastry · 04-thai-bazi)

> Research การออกแบบแอพมือถือล้ำๆ ปี 2026 — space / astrology / fortune / life tracking
> สถานะ: ✅ เสร็จสมบูรณ์ (22 ส.ค. 2026) — 3 agents, ~20 sources

## Project Context

- **Repo:** [github.com/tanadolsang-netizen/NEW-AI-REBORN](https://github.com/tanadolsang-netizen/NEW-AI-REBORN) → `C:/AI/NEW-AI-REBORN`
- **Backend:** FastAPI + skyfield ephemeris (offline) — natal, tarot, horary, synastry, transit, memory
- **Frontend:** Next.js 16 + Capacitor 8 (+ Expo prototype ใน `astral-expo`)
- **คู่แข่งหลัก:** Astra
- 📄 รายงานคู่แข่งเต็ม: [[astral-competitor-research-2025-2026]] (ใน folder `research/`)

---

## 1. 🎨 Design Trends 2026 (สำหรับ cosmic app)

### Visual Language
- **Glassmorphism → "Liquid Glass"** — iOS 26 ทำให้ glass กลายเป็น standard; ใช้เป็น overlay/card บนพื้นหลัง starfield
- **Aurora / Nebula gradients** — ยังเป็น niche accent (ไม่ใช่ main theme) — เหมาะเป็น accent glow รอบดาว/chart
- **Dark cosmic theme** — OLED true black + elevation ผ่าน layers + desaturated color + glow accents (อ่าน Dark Mode Guide)
- **Spatial/3D** — parallax depth, interactive 3D elements จาก visionOS influence; zodiac wheel แบบ 3D หมุนได้
- **Typography** — variable fonts + kinetic type; ตัวเลขวันที่/degree chart ขยับได้
- **Motion** — spring physics micro-interactions + haptics; Material 3 Expressive ยืนยันกระแส spring motion

### AI-native UI patterns
- streaming text, skeleton loading, **confidence indicators**, generative UI, human-in-the-loop
- Agentic UX: UI ที่ agent จัดให้แบบ proactive (zylos.ai research)

### Onboarding 2026
- ย้ายจาก "อธิบาย" → **evidence, consequence, rehearsal, better-timed prompts**
- = โชว์ chart จริงของ user ทันที (evidence) ไม่ใช่ slide อธิบาย feature

**Sources:** pixelmatters.com/insights/7-UI-design-trends-to-watch-in-2026 · ideakraft.com/top-5-design-trends-for-2026 · screensdesign.com/articles/app-onboarding-trends-2026 · groovyweb.co/blog/ui-ux-design-trends-ai-apps-2026 · abinantony.io/blog/material-3-expressive-beyond-card-ui · gsofttechnologies.com/blog/micro-interactions-motion-design-future-ios-ux-2026-20260310 · theinkorporated.com/insights/future-of-typography · superdesign.dev/styles/aurora · superfiles.in/mastering-dark-mode-ui-guide.php · elinext.com/services/ui-ux-design/trends/key-mobile-app-ui-ux-design-trends · developer.apple.com/videos/play/wwdc2026/234/

---

## 2. ⚔️ Competitors (สรุป — เต็มใน [[astral-competitor-research-2025-2026]])

| App | ราคา | จุดเด่น | จุดอ่อน |
|---|---|---|---|
| Co-Star | ~$550K/mo rev | social synastry, viral push | ย้ายฟีเจอร์ฟรีเข้า Plus (~$9/mo), notification fatigue, server ล่มวัน retrograde |
| The Pattern | $14.99/mo | psychology-first, Connect dating | rating ต่ำสุดกลุ่ม (4.0) — cancel-flow กัก user, paywall >50% เนื้อหาฟรี |
| Sanctuary | ~$20/mo + per-min chat | human astrologer ("Uber for astrology") | meter วิ่งตอนรอคิว 20–45 นาที, ไม่มี transcript |
| Chani | $11.99/mo, 4.9★ | anti-AI, 100% human-written + ritual/audio | rating สูงสุดใน category |
| Nebula | $1 hook → surprise $49.99 | growth machine | billing complaint ใหญ่สุดตลาด, thread "scam" ใน Google Play |
| Astra (ตรงเรา) | $6.99/สัปดาห์ hard paywall | AI-chat-as-UI, dream interpretation | **คำนวณ chart ผิดจริง** (DST, North Node), house system เลือกไม่ได้, personalization แค่ Big 3 |

**Rising stars:** Moonly (Luna AI จำ context) · Raka (AI ปฏิเสธทำนายผล = trust moat) · Stellium (one-time purchase) · AskSoma (client-side privacy)

**📈 Market:** Spiritual wellness ~$2.5B (2025) → $9.9B (2035), CAGR ~14.7% — APAC โตเร็วสุด

---

## 3. 📊 Life Tracking UX Patterns

- **Finch ($30M ARR, no VC):** gamification ผ่าน metaphor — นก pet โตตามการ self-care; core actions → progression ที่ user เห็นภาพ
- **Apple Activity Rings (HIG):** rings = daily progress ที่เข้าใจได้ใน 1 วินาที; close-the-ring psychology
- **How We Feel:** mood check-in เร็วด้วย emotion wheel + color zones
- **Starnote lunar journal:** journaling ผูกกับ moon phase = daily ritual ที่มี narrative
- Cosmic/circular viz: birth chart บน mobile ควร zoomable/tappable ต่อ element ไม่ใช่ภาพนิ่ง

**Sources:** blog.sparrowapps.io/p/finch-how-a-self-care-app-hit-30m-arr-without-vc-money · naavik.co/deep-dives/deep-dives-new-horizons-in-gamification/ · developer.apple.com/design/human-interface-guidelines/components/status/activity-rings · screensdesign.com/showcase/how-we-feel · starnote.app/meet-the-lunar-journal · auraeastrology.com/blog/the-pattern-app-review-2026-an-astrologers-honest-opinion

---

## 🚀 Implementation Status — Fusion Engine (22 ส.ค. 2026)

**เป้าหมาย:** รวมทุกศาสตร์เป็นอันเดียว — แม่น ปัจจุบัน user ไม่เดาเอง

| ไฟล์ | สิ่งที่ทำ |
|---|---|
| `src/services/fusion_engine.py` | 3 layers: Western transits (orb เข้ม, weighted) + Vedic Vimshottari/nakshatra + Thai/BaZi (ชง, ตรียัมปาไถ, ผู้คุณวัน) + fusion verdict 5 domains |
| `src/services/templates.py` | ประโยคไทย/อังกฤษ deterministic — ระบุหลักฐานทุกประโยค, polarity = ดาว×มุม (square ไม่ใช่ "หนุน") |
| `src/routers/fusion.py` | `POST /v1/fusion/today?lang=th` + `/domains` |
| `tests/test_fusion_engine.py` | ground truth จาก vault: Chitra pada 1, Jupiter MD 2022–2038, Fire Ox clash Goat, ตรียัมปาไถ 1-5-8-5 |

**Fusion precedence:** transit มีวันที่แม่น > dasha backdrop > BaZi day tone — ความขัดแย้งรายงานเป็น tension ไม่เฉลี่ยทิ้ง

**ผลจริง 22 ส.ค. 2026 (ดวง M):** 116 tests passed · Saturn opp Moon → love domain กดเพื่อจัดระเบียบ · Sun square Sun exact → health activation · ตรงกับ Jupiter-Saturn antardasha ที่กำลังปิด (สิ้นสุด ~พ.ย. 2026)

---

## 🏛️ Command Update — ระบบครบวงจร (22 ส.ค. 2026, สายค่ำ)

| ชิ้น | สถานะ |
|---|---|
| **คัมภีร์ engine specs** (`C:/AI/research-astrology/`) | ✅ ครบ 01-transit · 02-vedic · 03-synastry · 04-thai-bazi — ตัวเลข verify จริงทั้งหมด (DE421 + lunar-python) |
| **BaZi fixtures** | day pillar = (JDN + 49) mod 60 · เสาเจ้าของ 丁丑/乙巳/辛酉/辛卯 (Day Master 辛 โลหะหยิน) · ไหม 癸 น้ำหยิน |
| **Window Detector** | `POST /v1/transit/windows` (+ `/shared` สองดวง) — ซ้อมรบแล้ว: จัด 26–27 ส.ค. = วันดีสุดของคู่ M+Mai ตรงกับ transit scan อิสระของ S3 |
| **Profile Store** | `PUT /v1/fusion/profile/{name}` → `POST /v1/fusion/today/by-name/{name}` — บันทึกวันเกิดครั้งเดียว ดูดวงด้วยชื่อได้เลย (118 tests) |
| **Git** | commits `3dc21a2` (fusion) + `57ceefe` (profile store) push ขึ้น GitHub แล้ว |

**Regression วงจรปิด:** fusion API ↔ window detector ↔ manual scan ให้ผลตรงกันทุกจุดที่เทียบ (Saturn opp Moon · Ju-Sa backdrop · best-day 26–27 ส.ค.)

---

## 🎯 Strategic Takeaways สำหรับ Astral

1. **Trust-first billing = ช่องว่างที่ว่างที่สุด** — pain อันดับ 1 ของทั้ง category คือเรื่องเงิน ไม่ใช่ดวง (Nebula/The Pattern/Co-Star โดนหมด)
2. **Accuracy เป็น moat ที่เรามีอยู่แล้ว** — skyfield offline ephemeris + เลือก house system ได้ + horary (แทบไม่มีใครทำ) ตอบจุดอ่อน "chart ผิด" ของ Astra โดยตรง
3. **AI + memory + transcript** — reading ที่จำ context ได้ + เก็บ transcript ทุกครั้ง (ต่างจาก Sanctuary)
4. **Lifetime tier** — ต้าน subscription fatigue ที่ทำให้ rating ตก
5. **Localize ดูดวงไทย** — APAC โตเร็วสุดใน region
6. **Design direction:** dark OLED cosmic + liquid glass cards + aurora accent glow + 3D zodiac wheel (spring motion) + onboarding แบบ evidence-first (โชว์ chart จริงทันที)

---

## 📝 ORACLE Session Update — 22 ส.ค. 2026 21:30 (this session)

**GATE 142/142 GREEN + /v1/fusion/full/{name} LIVE (port 8001)**

### ✅ Fixes Applied This Session
- **BaZi Lichun near-cutoff FIXED**: `_adjusted_year()` now marks **Feb 1-7 as MEDIUM confidence** (was Feb 3-5) → `test_bazi.py` 13 passed
- **Synastry identity-resonance FIXED**: same-body conjunction (Sun-Sun, Moon-Moon, etc.) gets emotional_bond/chemistry points via `_SAME_BODY_DIMENSION` + `_SAME_BODY_WEIGHT` → `test_identical_charts_score_higher_emotional_bond_than_opposite` PASSED
- **pytest 142 passed, 1 warning** (all green)

### ✅ NEW ENDPOINT Deployed & Live-Verified
- **`GET /v1/fusion/full/{name}?lang=th&partner=mai`** → 200 OK
- Response shape verified:
  - `person`: {today (fuse_daily + reading TH/EN), profile (static layers)}
  - `compatibility`: {dimensions 6 มิติ, overall 44, top_bonds 3, frictions 3, karmic: dk_cross_check}
  - `upcoming`: {best_days 3 slots, shared_best: null}
- Live-verified with real charts: Owner (M) 1997-05-19 05:45 Chonburi + Partner (Mai) 2001-08-18 22:32 Nonthaburi

### 📁 Files Modified This Session
- `src/services/bazi_service.py`: near-cutoff rule (Feb 1-7 MEDIUM)
- `src/services/synastry_scoring.py`: identity-resonance kind
- `src/services/fusion_engine.py`: `compute_fusion_profile()`
- `src/routers/fusion_full.py`: NEW aggregator endpoint (96 lines)
- `src/main.py`: registered router (no double prefix)

### 📋 Command Bus Reports
- FORGE queue task "Unified Full Reading endpoint" → **DONE**
- S3 queue: daily_brief.py verified + gate now 142/142
- ORACLE: idle-ready for next order

---

## Related

- [[astral-competitor-research-2025-2026]]
- [[user_astrology_interest]]
- [[user_personality_natal]]