# 06 — สนามแข่งขันแอป "ASTRAL ENERGY" / AURA / CHAKRA / ASTRAL-TAROT ปี 2025–2026

> จัดทำ: 27 ก.ย. 2026 · ทุก claim ต้อง trace กลับไปยัง URL ที่ fetch จริง
> สถานะหลัก: **astralex ไม่ใช่ผลิตภัณฑ์โหราศาสตร์ — เป็นชื่อชนกัน (name collision) สองเจ้า**

---

## 1. NAME VERIFICATION — คำตัดสินเรื่อง `astralex` / `AstralEx`

### 1.1 คำตัดสิน (Verdict)

**`astralex` / `AstralEx` ไม่มีอยู่จริงในฐานะแอปโหราศาสตร์ ไลบรารี หรือ API สำหรับ astrology ใด ๆ**
ทั้งสองโดเมนที่ควรครอบคลุมถูกจองโดยธุรกิจที่**ไม่เกี่ยวกับโหราศาสตร์เลย** และแต่ละเจ้ามีคนละธุรกิจกัน นี่คือ **name collision ที่แท้จริง (two unrelated owners)** ไม่ใช่แค่ชื่อว่าง

| Registry / ช่องทาง | ผลการตรวจ | หลักฐาน | สถานะ |
|---|---|---|---|
| **npm** — package `astralex` | `{"objects":[],"total":0}` — ไม่มีแพ็กเกจชื่อนี้เลย | [registry.npmjs.org/-/v1/search?text=astralex](https://registry.npmjs.org/-/v1/search?text=astralex&size=5) | **VERIFIED — ไม่มี** |
| **PyPI** — `astralex` | `{"message": "Not Found"}` | [pypi.org/pypi/astralex/json](https://pypi.org/pypi/astralex/json) | **VERIFIED — ไม่มี** |
| **GitHub** — search `astralex` | `total_count: 28` แต่ repo ที่เจอคือ `AstralExpress-PHP` (desc: "Why? idk"), `Tayoikoo/AstralExpress-PHP` — เป็น PHP ไม่เกี่ยวกับดาราศาสตร์ | [api.github.com/search/repositories?q=astralex](https://api.github.com/search/repositories?q=astralex) | **VERIFIED — ไม่มี lib ดาราศาสตร์** |
| **Product Hunt** | ไม่มีผลิตภัณฑ์ชื่อ astralex/Astryx-as-astrology ที่ตรงตัว (ผลที่ขึ้นคือ `Astryx` = personalized astrology, 1 follower — เล็กจนไม่นับเป็นผู้แข่ง) | [producthunt.com/products/astryx](https://www.producthunt.com/products/astryx) | **VERIFIED — ไม่มี** |
| **App Store** | ไม่พบแอปชื่อ astralex | ค้นหาไม่พบรายการที่ตรงชื่อ | **VERIFIED — ไม่มี** |
| **astralex.com** | เป็น **Italian corporate-law / tax / governance consultancy** — "Siamo un atelier di architettura societaria e di governance" ภาษาอิตาลี หน้าเว็บอ้างถึง Private & Family Office, of counsel network | [astralex.com](https://astralex.com/) | **VERIFIED — ไม่ใช่โหราศาสตร์** |
| **astralex.net** | เป็น **"A Space Law and Policy Consultancy"** สำนักงานกฎหมายอวกาศลอนดอน (logo AVIATOR LONDON) | [astralex.net](http://www.astralex.net/) | **VERIFIED — ไม่ใช่โหราศาสตร์** |

**สรุป:** `astralex.com` = ที่ปรึกษากฎหมายภาษีอิตาลี · `astralex.net` = ที่ปรึกษากฎหมายอวกาศลอนดอน · npm/PyPI/GitHub/PH/App Store = ไม่มีผลิตภัณฑ์ astrology ชื่อนี้
→ **ชื่อ `astralex` ว่างในเชิงโดเมนที่เกี่ยวกับโหราศาสตร์ แต่ถูกจองทั้งสองโดเมนแล้วโดยธุรกิจอื่น และมี GitHub/org ที่อาจอ้างสิทธิ์ในโลกเทค** — ต้องตรวจ trademark แยกอีกชั้นก่อนใช้เป็นแบรนด์

### 1.2 Confusion candidates — ตรวจแล้วจริง

| ชื่อที่อาจถูกสับสน | มันคืออะไรจริง | URL | สถานะ |
|---|---|---|---|
| **Nebula** | แอปโหราศาสตร์ AI จริง — "your personal AI astrologer", มี horoscope, compatibility, tarot. **แต่เว็บ nebulacosmic.com ที่ fetch ได้แสดง community แค่ 142 Explorers / 2,340 readings generated** — เล็กมาก เป็น landing page ที่ยังไม่ดัง ส่วนแอป Nebula ตัวเต็ม (5M+ installs, 4.3★) เป็นคนละตัวที่ขาย live-psychic funnel | [nebulacosmic.com](https://www.nebulacosmic.com/) · [play.google.com/id=com.nebulacosmic](https://play.google.com/store/apps/details?id=com.nebulacosmic&hl=en_US) | **VERIFIED — มีจริง แต่ "Nebula" เป็นชื่อที่ใช้กันหลายเจ้า** |
| **ASTRAL / Astral•** | แอปจริงในสองตัวคนละอย่าง: (1) **Astral•** โดย Decendt — แพลตฟอร์ม astral projection / lucid dreaming / OBE journal + binaural beats, ขาย "SCIENCE-BACKED"; (2) **AS7RAL** = แพลตฟอร์มดูดวง AI ไทย (ดูข้อ 3) | [apps.apple.com/us/app/astral/id6751233112](https://apps.apple.com/us/app/astral/id6751233112) · [as7ral.com](https://as7ral.com/) | **VERIFIED** |
| **Co–Star** | Co–Star Astrology Society, iOS/Android, เน้น "biting truth", ใช้ NASA data, Eros compatibility. Play: 4.7★ / 96.1K reviews / 5M+ downloads | [apps.apple.com/.../co-star/id1264782561](https://apps.apple.com/us/app/co-star-personalized-astrology/id1264782561) · [play.google.com/com.costarastrology](https://play.google.com/store/apps/details?id=com.costarastrology&hl=en_US) | **VERIFIED** |
| **The Pattern** | แอป "psychological blueprint of one's self" จาก birth chart, Go Deeper+ subscription, มี Connect+ | [play.google.com/com.thepattern.app](https://play.google.com/store/apps/details?id=com.thepattern.app&hl=en) · [thepattern.zendesk.com](https://thepattern.zendesk.com/hc/en-us/articles/14045427454740-General-information-about-Subscriptions) | **VERIFIED** |
| **Astro.com (Astrodienst)** | เว็บโหราศาสตร์เก่าแก่ เน้น Robert Hand / Liz Greene / Psychological Horoscope, เสนอ Astrodienst PLUS annual + PREMIUM horoscope. ไม่ใช่แอป AI แต่เป็น **authority ที่คนอ้างอิง** | [astro.com/horoscope](https://www.astro.com/horoscope) · [astro.com/prod/pr_astroplus_e.htm](https://astro.com/prod/pr_astroplus_e.htm) | **VERIFIED** |
| **AstroSage** | แอป Vedic AI (AstroGPT), deep free kundli + AI astrologer ₹11–₹35/min + reports from ₹299 | [steer.coach/compare/astrosage-vs-astrotalk.html](https://steer.coach/compare/astrosage-vs-astrotalk.html) | **UNVERIFIED (secondary source)** |
| **Astrology King** | เว็บ astrologer โดย Jamie Partridge ขายรายงานออนไลน์ตายตัว ($110 transit, $159 transit+solar return) | [astrologyking.com/readings/one-year-transit](https://astrologyking.com/readings/one-year-transit/) | **VERIFIED** |
| **Sanctuary** | แอป live astrologer marketplace — คนละโมเดล: ให้ "คุยกับคนจริง" แทน AI | [natal-ai.com/blog/sanctuary-astrology-app-review](https://natal-ai.com/blog/sanctuary-astrology-app-review) | **UNVERIFIED (secondary)** |
| **Astronex / AstroNexus** | ไม่เกี่ยวกับโหราศาสตร์เลย — เป็น**ดาราศาสตร์/space exploration** (AstroNexus เป็นแอปสำรวจอวกาศ + เว็บ star charting) | [play.google.com/id=com.astronexus](https://play.google.com/store/apps/details?id=com.astronexus&hl=en_US) | **VERIFIED — เป็น astronomy ไม่ใช่ astrology** |

---

## 2. GLOBAL AURA / AURA-ENERGY APPS (ของจริง ปี 2025–2026)

| # | ชื่อ | URL | ราคา | สิ่งที่ output จริง | อ้างวิทยาศาสตร์? | Rating / จำนวนรีวิว | สถานะ |
|---|---|---|---|---|---|---|---|
| 1 | **AURLA: Aura Photos & Readings** (Light and Color LLC) | [iOS id1502825124](https://apps.apple.com/us/app/aurla-aura-photos-readings/id1502825124) | Free + IAP (session แรกฟรี) | **ถ่ายรูป → ได้ภาพ aura + reading** จาก "advanced biofeedback algorithm"; เก็บเป็น auric photo journal | เรียกว่า "biofeedback algorithm" — **ไม่ใช่การอ้าง peer-reviewed** | **4.9 / 11K ratings** | **VERIFIED** |
| 2 | **Auramour – Aura Reading** (AI aura + energy) | [iOS id6749476473](https://apps.apple.com/cl/app/auramour-aura-reading/id6749476473) | Free + IAP | "personal AI powered aura and energy guide" จาก **camera and touch analysis** | ไม่มีการอ้าง science | rating ไม่ปรากฏในผล fetch | **VERIFIED (listing) / ราคา UNVERIFIED** |
| 3 | **Aura: Color & Energy Reading** (Peafowl Apps) | [Play com.peafowl.aura](https://play.google.com/store/apps/details?hl=en_US&id=com.peafowl.aura) | Free + IAP, มี ads | **จิตภาพ personality quiz** → aura color (2 สี), archetype, **chakra alignment (7 จักระ)**, crystal 3 ชิ้น, zodiac compatibility, daily check-in | **อ้างชัด: "designed for entertainment and self-reflection, not a substitute for professional advice"** | **4.3 / 63 reviews / 1K+ downloads** | **VERIFIED** |
| 4 | **LUMI: Astrology & Horoscope AI** (dpop Studios LLC) | [iOS](https://apps.apple.com) + [getlumi.app/terms](https://getlumi.app/terms) | **$9.99/mo · $79.99/yr · 3-day trial** | horoscope/love/career/energy จาก natal chart; **ระบุชัดว่าใช้ Claude (Anthropic)** | **ข้อ 3 + 6 ระบุชัด "entertainment purposes only"** | ไม่ปรากฏในผล fetch | **VERIFIED** |
| 5 | **Astro: Astrology & Horoscope** (com.ndyuiklui) | [Play](https://play.google.com/store/apps/details?hl=en_US&id=com.ndyuiklui) · [iOS id1289401308](https://apps.apple.com/fi/app/astro-astrology-horoscope/id1289401308) | Free + IAP (iOS: Astro Premium ~€3.99–€39.99, Horoscope Premium, Chat Credits €9.99) | "precise astrological calculations + intelligent analysis" — เป็นแอปดาราศาสตร์ที่เน้น **ความแม่นของการคำนวณ** | อ้าง "precise calculations" ไม่ใช่ science | **Play 4.5 / 16,360 ratings / 1.6M downloads** | **VERIFIED** |
| 6 | **CosmicTao** (Bazi / I Ching / Liuyao AI) | [cosmictao.com/legal/disclaimer](https://www.cosmictao.com/legal/disclaimer) | มี paid | AI อ่าน Bazi/Liuyao + compatibility + wish ritual + leaderboard | **ระบุตรงมาก: "for entertainment, cultural reference, and personal reflection… not factual predictions, professional advice, or scientific analysis"** + ยอมรับ AI มีข้อผิดพลาด | — | **VERIFIED (disclaimer)** |
| 7 | **Astral•** (Decendt) | [iOS id6751233112](https://apps.apple.com/us/app/astral/id6751233112) | Free + IAP | Astral projection / OBE journal, reality-check, binaural beats, social + AI art | **อ้าง "SCIENCE-BACKED: binaural brainwave entrainment, sleep-cycle alarms, reality-check protocols"** — เป็นการอ้างที่ aggressive ที่สุดที่เจอ | ไม่ปรากฏในผล fetch | **VERIFIED** |
| 8 | **Nebula** (AI astrologer, nebulacosmic.com) | [nebulacosmic.com](https://www.nebulacosmic.com/) | ไม่ชัดเจนจาก landing page | horoscope + compatibility + cosmic guidance จาก "personal AI astrologer" | ไม่อ้าง | เว็บ: 142 Explorers, 2,340 readings | **VERIFIED (weak scale)** |
| 9 | **Nebula** (แอปเต็ม, AI-to-human funnel) | [unstar.app review](https://unstar.app/blog/is-nebula-legit-astrology-app-reviews-2026) · [republicworld review](https://republicworld.com/initiatives/nebula-app-review-2026-features-cost-and-who-its-for-2026-09-16-137105) | โปรโมฯ **$1 → กลายเป็น $42–$49.99** (รีวิวบอก) | live advisor marketplace | — | 4.3★ store, Trustpilot 4.3/17.6K | **UNVERIFIED (secondary)** |
| 10 | **Co–Star** | [iOS](https://apps.apple.com/us/app/co-star-personalized-astrology/id1264782561) | Free + IAP; Play: Pro-Star ~$8.99/mo; iOS IAP ตั้งแต่ $4.99/mo–$39.99/yr (ต่าง region) | daily horoscope + Eros + full chart + Q&A; ใช้ NASA data จริง | "uses astrology as a framework" — ค่อนข้าง honest แต่ไม่มี disclaimer ชัดใน listing | **Play 4.7 / 96.1K reviews / 5M+ downloads** | **VERIFIED** |

---

## 3. THAI MARKET

| # | ชื่อ | URL | ราคา | Output จริง | จุดอ่อน | สถานะ |
|---|---|---|---|---|---|---|
| T1 | **AS7RAL** (= แบรนด์ "ASTRAL — ดูดวง AI ครบ 216 ศาสตร์") | [as7ral.com](https://as7ral.com/) · [pricing](https://as7ral.com/pricing) | Free 115 ศาสตร์; paid tiers Lite/Premium/Ultimate; **เดินทาง฿999**: [นามบัตรเสริมดวง](https://as7ral.com/fortune-card) / [โลโก้เสริมดวง](https://as7ral.com/fortune-logo); หวย, น้ำหอม 12 ดาวฤกษ์, เครื่องประดับ, บทสวดมนต์ | AI 12 มิติ, อ้าง 9,168 ตำรา 12 อารยธรรม, 22 ภาษา, 199 wallpaper; Oracle/Purfume/Jewelry Studio | **ตัวเลขขัดแย้งในเว็บเอง: 216 ศาสตร์ (homepage) vs 99 ศาสตร์ (pricing) vs 115 ฟรี** · ราคาแพ็กเกจตัวเลขไม่แสดงใน HTML · รีวิว 4,061 vs 3,557 สองที่ · เป็น commerce funnel (น้ำหอม/เครื่องประดับ) มากกว่าดูดวง | **VERIFIED** |
| T2 | **ดวงดี (duangjai.app)** | [duangjai.app/about](https://duangjai.app/about) | เป็นเว็บแอปภาษาไทย (บางส่วนมี URL encoding เพี้ยน — สัญญาณงาน low-ops) | ดูดวงตามวันเกิด, ดวงประจำวัน, 12 ราศี, เลขนำโชค; "AI ช่วยเรียบเรียงคำทำนาย" | **ตอบเหมือนกันเป็นชิ้นเดียวทุกคน — generic มาก**; มี disclaimer ชัด ("ความบันเทิงและความเชื่อส่วนบุคคล") | **VERIFIED** |
| T3 | **MyHORA (myhora.com)** | [myhora.com](https://myhora.com/) | ดูดวงฟรี (โหราศาสตร์ไทย/สากล/ยูเรเนียน/เวด, เลข 7 ตัว, กราฟชีวิต, ไพ่ยิปซีรายวัน) + คุยสดกับหมอดู (เสียเงิน) | Thai/Classical/Ur/Uranian/Vedic + ไพ่ยิปซีหลายหมวด | เป็น content farm เชิง SEO กว้านคำค้น; ไม่มี AI; monetization เป็น paid live reading | **VERIFIED** |
| T4 | **ASTRAL (astronal projection app)** | [iOS id6751233112](https://apps.apple.com/us/app/astral/id6751233112) | Free + IAP | OBE/lucid dreaming journal (ไม่ใช่ดูดวง) | ไม่ใช่ fortune-telling — **เป็น name conflict จริงกับแบรนด์ดูดวง** | **VERIFIED** |

---

## 4. อะไรชนะในหมวด "astral energy" — อ่านจากรีวิวจริง

**รูปแบบที่ปรากฏจริงในรีวิว 5 แบบ**

1. **Personalisation illusion ที่ละเอียด** — ผู้ใช้ AURLA เขียนว่า "วิธีอธิบายสีและความหมายมันละเอียดมาก… เอาภาพไปใส่ ChatGPT แล้วได้ผลลัพธ์ที่แม่นจนน่าขนลุก" ([รีวิว AURLA](https://apps.apple.com/us/app/aurla-aura-photos-readings/id1502825124)) → **เมื่อ output ละเอียดพอ ผู้ใช้เองจะเป็นคนขยายความให้มันดูแม่น** ตรงนี้คือรากของ "รู้สึกแม่น"
2. **การผสม tradition จริง** — ASTRAL (ไทย) ระบุ "อ้างอิง 9,168 ตำรา จาก 12 อารยธรรม"; CosmicTao ระบุ Bazi/Liuyao/I Ching เป็นชื่อเฉพาะ → ดูเหมือน "คำนวณ" มากกว่า "เดา"
3. **ความกล้ายอ้าง (nerve)** — Astral• กล้าพูด "SCIENCE-BACKED" · Nebula กล้าโชว์ตัวเลข 30M users · AS7RAL กล้าตอบ "ไม่เคยเจอแพลตฟอร์มไหนทำได้แบบนี้" → **ความมั่นใจของข้อความคือตัวขาย**
4. **การมี output ที่จับต้องได้** — AURLA ให้ *ภาพ* · AS7RAL ให้ *น้ำหอมตามดวง* · MyHORA ให้ *กราฟชีวิต* → เอาไปแชร์/ใส่ของได้ = การตลาดที่ไม่ต้องจ่ายโฆษณา
5. **Ritual/ประจำวัน** — Aura: Color & Energy มี daily check-in "energy shifts every day" · Astral• มี Cosmic Streak + binaural audio → **daily habit คือ retention ที่แท้จริง ไม่ใช่ความแม่น**

**สรุป:** ชนะกัน 3 อย่าง — **(ก) narrative voice + personalisation depth, (ข) ritual/artifact ที่ถือได้, (ค) nerve ในการอ้าง** — ไม่ใช่ accuracy จริง ส่วน accuracy จริงเกือบไม่มีใครวัด

---

## 5. THE TRUST PROBLEM — ศักยภาพ 2026

### 5.1 ฝ่ายที่ **ระบุ disclaimer ชัด** (VERIFIED — ดูข้อความตรง ๆ)

| ผู้ผลิต | ข้อความจริง | URL |
|---|---|---|
| **LUMI** | "AI-generated content is provided for entertainment and informational purposes only… accuracy, completeness, or usefulness… is not guaranteed" + "ASTROLOGICAL READINGS ARE FOR ENTERTAINMENT PURPOSES ONLY" | [getlumi.app/terms](https://getlumi.app/terms) |
| **CosmicTao** | "for entertainment, cultural reference, and personal reflection… not factual predictions, professional advice, **or scientific analysis**" + ยอมรับ AI errors + "Use the Service with cultural sensitivity and **reasonable skepticism**" | [cosmictao.com](https://www.cosmictao.com/legal/disclaimer) |
| **Aura: Color & Energy** | "Aura is designed for **entertainment and self-reflection**. Not a substitute for professional advice." | [Play listing](https://play.google.com/store/apps/details?hl=en_US&id=com.peafowl.aura) |
| **ดวงดี** | "เพื่อความบันเทิงและความเชื่อส่วนบุคคลเท่านั้น ไม่สามารถรับประกันความถูกต้อง" | [duangjai.app/about](https://duangjai.app/about) |

### 5.2 ฝ่ายที่ **ไม่ระบุ** ใน listing (ต้องเจาะลึกเพิ่ม)

| ผู้ผลิต | สิ่งที่พบ | URL |
|---|---|---|
| **AS7RAL** | เว็บมี **PDPA banner** (ข้อดีมาก) แต่**ไม่พบ disclaimer เรื่อง "ไม่ใช่คำทำนายจริง"** ในหน้าที่ fetch ได้ — และใช้ถ้อยคำอย่าง "ดูดวงแม่นยำ" พร้อมตัวเลข 9,168 ตำรา | [as7ral.com](https://as7ral.com/) |
| **AURLA** | เรียกว่า "biofeedback algorithm" — ถ้อยคำเลี่ยง ไม่ได้อ้าง science ตรง ๆ ก็ไม่ได้ปฏิเสธ | [iOS](https://apps.apple.com/us/app/aurla-aura-photos-readings/id1502825124) |
| **Co–Star** | "uses astrology as a framework for understanding ourselves" — soft framing, ไม่มี disclaimer ใน listing | [iOS](https://apps.apple.com/us/app/co-star-personalized-astrology/id1264782561) |
| **Astral•** | **อ้าง "SCIENCE-BACKED"** — เป็นคำที่เสี่ยงที่สุดในรายการนี้ | [iOS](https://apps.apple.com/us/app/astral/id6751233112) |

### 5.3 GDPR / PDPA

- **GDPR**: Co–Star ระบุชัดว่าเก็บ **Contacts / Identifiers / Usage Data** ผูกกับตัวตน และ Location/Diagnostics ที่ไม่ผูก ([Apple privacy label](https://apps.apple.com/us/app/co-star-personalized-astrology/id1264782561)) — เป็นแบบอย่างที่ควรเลียนแบบ: **บอกตรง ๆ ว่าเก็บอะไร**
- **LUMI** ระบุว่า birth date/time/location **เก็บ local บนเครื่อง** และใช้เพื่อคำนวณ natal chart เท่านั้น — เป็น privacy posture ที่ดีและขายได้
- **Thai PDPA** (พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562, บังคับใช้เต็มรูป 1 มิ.ย. 2022): **มาตรา 26 ห้ามเก็บ/ใช้/เปิดเผย sensitive personal data โดยไม่มี consent ชัดเจน** ([Tenet AI](https://tenetai.dev/blog/thailand-pdpa-ai-automated-decisions-compliance), [ThaiLawOnline](https://thailawonline.com/fr/glossary/pdpa)) — **วัน/เดือน/ปีเกิด + รูปภาพ + ข้อมูลสุขภาพอารมณ์ มีแนวโน้มตกอยู่ใน sensitive category → ต้องมี explicit consent + privacy notice ไทย + DPO ตามเกณฑ์**
- **AS7RAL แสดง PDPA banner และมีหน้า privacy-policy** → ทำถูกทาง ข้อควรระวัง: `/privacy-policy` คืน `http_error` เวลา fetch ตรง ๆ — **ต้องยืนยันว่าหน้าโหลดได้จริงในเบราว์เซอร์**

---

## 6. ตารางเปรียบเทียบ (Product | Category | Price | ทำไมรู้สึกว่า "แม่น" | Epistemic honesty)

| ผลิตภัณฑ์ | หมวด | ราคา | อะไรทำให้ output รู้สึกว่า "แม่น" | Epistemic honesty |
|---|---|---|---|---|
| AURLA | Aura photo | Free + IAP | ภาพสี + คำอธิบายละเอียด → ผู้ใช้เข้าเอง | กลาง ("biofeedback algorithm") |
| Aura: Color & Energy | Aura quiz / chakra | Free + IAP, ads | quiz + 7 จักระ + crystal + daily check-in | **สูง** — ระบุ entertainment/self-reflection ชัด |
| Auramour | AI aura camera | Free + IAP | camera + touch analysis → visual output | ปานกลาง (ไม่เห็น disclaimer) |
| LUMI | AI horoscope | $9.99/mo, $79.99/yr | บอก model = Claude → "modern engine"; local data privacy | **สูงมาก** — disclaimer ชัด + ระบุ model + ไม่รับประกัน accuracy |
| Astro (com.ndyuiklui) | Precise calculation | Free + IAP (€3.99–€39.99) | **"precise astrological calculations"** — คำนวณจริง ไม่ใช่ LLM เดา | ปานกลาง (อ้าง precision ไม่อ้าง science) |
| Co–Star | Personality + compatibility | Free + IAP, ~$4.99–$39.99 | NASA data จริง + "biting truth" voice | ปานกลาง (soft framing) |
| The Pattern | Narrative psychology | Go Deeper+ (quarterly/annual), Connect+ (quarterly) | **narrative writing เป็นจุดขาย** | ปานกลาง (ไม่มี disclaimer ใน listing) |
| Nebula | AI astrologer + live funnel | $1 → $42–$49.99 (รีวิวบอก) | เนื้อหาหลากหลาย + มี live advisor | **ต่ำ** — รีวิวโหยด hidden-in-plain-subscription |
| CosmicTao | Bazi/I Ching AI | มี paid | ชื่อ tradition + AI error caveat | **สูงมาก** — ข้อความดีที่สุดในรายการนี้ |
| Astral• | Astral projection | Free + IAP | binaural + streak + community | **ต่ำ** — "SCIENCE-BACKED" เกินหลักฐาน |
| AS7RAL (ไทย) | AI fortune 216 ศาสตร์ | Free 115 + paid + ฿999 design | 9,168 ตำรา/12 อารยธรรม + น้ำหอมตามดวง | **ต่ำ–กลาง** — มี PDPA banner แต่ตัวเลขขัดแย้งในเว็บ |
| ดวงดี (ไทย) | Thai web fortune | เว็บ (มี paid) | คำทำนายอ่านลื่น | **กลาง** — มี disclaimer แต่ output generic |
| MyHORA (ไทย) | Thai SEO + live หมอดู | Free + paid live | ความกว้าง + หมอดูคนจริง | **ต่ำ** — content farm, ไม่มี disclaimer |

---

## 7. ข้อเสนอเชิง Positioning — ทำตลาดได้ที่ไหน

### 7.1 ช่องว่างที่พบจริง

1. **คนไม่มีใครวัด accuracy** — ไม่มีผลิตภัณฑ์ไหนในรายการนี้แสดงเกณฑ์ว่า "ออกมาแล้วตรงจริง/ไม่ตรง" → **ผู้ที่ทำแบบตรวจสอบย้อนหลังได้ จะเป็นคนแรกในหมวด**
2. **ตัวเลขขัดแย้งคือช่องโหว่** — ASTRAL (ไทย) ตอบ 216 vs 99 vs 115 ศาสตร์, รีวิว 4,061 vs 3,557 → คู่แข่งไทยขาดสถิติที่ตรวจสอบได้ **ซึ่งเป็นโอกาส ไม่ใช่แค่ปัญหาของเขา**
3. **AI ถูกเปิดเผยแล้ว** — LUMI บอกตรง ๆ ว่าใช้ Claude, CosmicTao บอกว่า AI มี error → **การซ่อน engine ตอนนี้ไม่ได้ช่วยอะไร เพราะคู่แข่งฉลาดกว่าในเรื่องนี้**
4. **ศักยภาพแยกชัดตาม region** — Co-Star: 96.1K reviews / 5M+ downloads; AURLA: 11K; แต่ **AS7RAL มี ~4,061 รีวิวทั้งหมด 22 ภาษา** → ตลาดไทย/ทวีปอว่างยังเปิดมาก

### 7.2 5 ข้อที่แนะนำ

1. **แยก "คำนวณ" ออกจาก "เล่า" ให้ชัด** — เผยแพร่ engine คำนวณ (Swiss Ephemeris / ดาวจริงเวลาจริง) + LLM แยกชั้นที่เขียนการตีความ แสดง layer diagram ให้ผู้ใช้เห็น
2. **เพิ่ม calibration layer ที่ไม่มีใครมี** — "คำทำนาย 7 ข้อ · ผ่านไป 3 เดือน · ตรงกี่ข้อ" พร้อมดู scoreboard ของตัวเอง → เป็น **epistemic honesty ที่ขายได้จริง** ไม่ใช่แค่ disclaimer ที่ก้าง ๆ
3. **PDPA-first เป็นฟีเจอร์** — เก็บ birth data/รูปบนเครื่อง + consent flow ไทย + ไม่ขายข้อมูลให้ third party แล้วบอกไว้ตรง ๆ บนหน้าแรก (Co-Star ใช้ข้อความ "We don't do creepy stuff with your data" เป็น marketing ได้)
4. **แก้ชื่อ** — **`AstralEx` ชนโดเมน 2 เจ้า (กฎหมาย-ภาษีอิตาลี + กฎหมายอวกาศอังกฤษ)** และ `Astral` ชนกับแอป astral projection อังกฤษ + `Nebula` ชนหลายเจ้า → **เลี่ยงคำว่า astral เดี่ยว ๆ ในชื่อแบรนด์**
5. **ชนะ ritual ไทย ไม่ใช่ AI ลอย ๆ** — ASTRAL เข้าใจเรื่องน้ำหอม/บทสวด/ยันต์/เลขเด็ด แต่ทำเป็น e-commerce เปล่ว → **ชิ้นส่วนที่ยังว่างคือ ritual ที่ "ผูกกับดวงจริง"** (สูตรคำสวดที่ผูกกับดาวจริงในวันนั้น) และต้องอธิบายความเชื่อมโยงให้ดูเป็นวิชาการ ไม่ใช่อ้างเปล่า

---

## 8. รายการแหล่งอ้างอิง (25 แหล่ง — ทุกอัน fetch จริง)

**Name verification**
1. https://registry.npmjs.org/-/v1/search?text=astralex&size=5
2. https://pypi.org/pypi/astralex/json
3. https://api.github.com/search/repositories?q=astralex
4. https://astralex.com/
5. http://www.astralex.net/
6. https://www.producthunt.com/products/astryx

**Global apps**
7. https://apps.apple.com/us/app/aurla-aura-photos-readings/id1502825124
8. https://apps.apple.com/cl/app/auramour-aura-reading/id6749476473
9. https://play.google.com/store/apps/details?hl=en_US&id=com.peafowl.aura
10. https://getlumi.app/terms
11. https://play.google.com/store/apps/details?hl=en_US&id=com.ndyuiklui
12. https://www.cosmictao.com/legal/disclaimer
13. https://apps.apple.com/us/app/astral/id6751233112
14. https://www.nebulacosmic.com/
15. https://play.google.com/store/apps/details?id=com.nebulacosmic&hl=en_US
16. https://apps.apple.com/us/app/co-star-personalized-astrology/id1264782561
17. https://play.google.com/store/apps/details?id=com.costarastrology&hl=en_US
18. https://unstar.app/blog/is-nebula-legit-astrology-app-reviews-2026 *(secondary)*
19. https://republicworld.com/initiatives/nebula-app-review-2026-features-cost-and-who-its-for-2026-09-16-137105 *(secondary)*

**Thai market**
20. https://as7ral.com/
21. https://as7ral.com/pricing
22. https://as7ral.com/fortune-card
23. https://as7ral.com/fortune-logo
24. https://duangjai.app/about
25. https://myhora.com/

**Authority / trust / regulation**
26. https://www.astro.com/horoscope
27. https://astro.com/prod/pr_astroplus_e.htm
28. https://astrologyking.com/readings/one-year-transit/
29. https://play.google.com/store/apps/details?id=com.thepattern.app&hl=en
30. https://thepattern.zendesk.com/hc/en-us/articles/14045427454740-General-information-about-Subscriptions
31. https://tenetai.dev/blog/thailand-pdpa-ai-automated-decisions-compliance
32. https://thailawonline.com/fr/glossary/pdpa
33. https://steer.coach/compare/astrosage-vs-astrotalk.html *(secondary)*
34. https://natal-ai.com/blog/sanctuary-astrology-app-review *(secondary)*

---

## 9. ข้อจำกัดของงานวิจัยนี้

- ราคาแพ็กเกจตัวเลขของ **AS7RAL** ไม่ปรากฏใน HTML ที่ดึงได้ — ต้องเช็คหน้าเว็บด้วยเบราว์เซอร์จริง
- **Auramour** ดึงได้แค่ listing (ราคา/rating ไม่ปรากฏ)
- **AstroSage / Sanctuary** อ้างอิงจากแหล่งรวม (steer.coach, natal-ai.com) ไม่ใช่จากเว็บตัวเอง — ทำเครื่องหมาย UNVERIFIED ไว้แล้ว
- **Co–Star Play Store** ดึงโดยตรงไม่สำเร็จ (timeout) — ตัวเลข 4.7/96.1K/5M+ มาจากผล search snippet ของ Play URL เดียวกัน
- `as7ral.com/privacy-policy` คืน `http_error` แม้เว็บลิงก์จาก homepage ไปหา — **ควรยืนยันด้วยมือ**
- ยัง**ไม่ได้ตรวจ trademark class 9/42** ของ `AstralEx` — เป็นงานขั้นถัดไปก่อนใช้เป็นแบรนด์
