# 08 · BIRTH-TIME-UNKNOWN FALLBACK MODE — Engine Spec
> **EN:** How the engine degrades gracefully when the user doesn't know their birth time. Deterministic at every tier.
> **TH:** โหมดสำรองเมื่อ user ไม่รู้เวลาเกิด — deterministic ทุกระดับ พร้อมป้ายความแม่นยำชัดเจน

---

## 1 · Confidence tiers (engine always labels which tier is active)
| Tier | Input | What works | What's disabled |
|---|---|---|---|
| **T1 exact** | date+time+place | everything (ASC/houses/D9/dasha-precise) | — |
| **T2 window** | date+place + time range (e.g. "morning") | planets, dasha (±), transits to planets | ASC/houses/D9/lot/HD-type [flag LOW] |
| **T3 noon-default** | date only | planets ±6h error (Moon ≤3° err, fast planets fine except Moon) | all angle-based systems |
| **T4 date-only minimal** | date only | Sun sign, BaZi year/day pillars, numerology, Mayan kin, NSK year star, ZiWei (hour→noon fallback flagged), transit-to-Sun/Mars+ outer | Moon-sensitive outputs |

## 2 · Deterministic rules per system
| System | Fallback behavior |
|---|---|
| Western natal | T3: cast 12:00 local, hide ASC/houses; show planets w/ "±6h" badge; Moon shown with range arc of that day |
| Vedic | T2/T3: Vimshottari from Moon — compute dasha at BOTH day boundaries; if same MD → print it HIGH-conf; if differs → print both + boundary dates ("MD switches between HH:MM–HH:MM this day"); D9 hidden below T1; nakshatra same dual-boundary rule |
| Transit timing | transits to Sun/Venus/Mars/Jupiter… OK from T3; transits-to-ASC/MC hidden below T1; eclipse-on-point uses planet points only |
| Synastry | composite/Davison require BOTH charts ≥T2; aspect scoring runs on planetary layer only; overlay matrix disabled below T2 |
| BaZi | year pillar solid from date (LiChun) ✓ · month pillar needs solar-term margin check (>36h from term boundary = safe) · **day pillar solid (no time needed)** · hour pillar omitted → strength analysis reruns without hour pillar, favorable elements get wider band |
| Numerology/Mayan/NSK-year | unaffected by birth time ✓ (pure date math) — engine surfaces these FIRST in unknown-time mode |
| Zi Wei Dou Shu | requires hour strictly; if unknown → cast at 午時 noon BUT label every palace "[hour-assumed]" and suppress spouse/career palace verdicts unless user opts in |
| Thai เลขเจตา/ตรียัมปาไถ | unaffected (date-based) ✓ |

## 3 · UX contract
1. Ask flow never blocks: user can skip time input entirely.
2. Every reading carries `tier` field; UI shows one honest line: TH *"โหมดไม่ทราบเวลาเกิด — ผลชุดนี้ใช้ข้อมูลระดับ [date-only] จึงไม่รวมลัคนา/เรือน"* · EN mirror.
3. Time-recovery nudge (once per week max): "ถ้ารู้เวลาเกิดจากสูติบัตร/แม่ ระบบจะปลดล็อกลัคนา+ดวงจีนเต็มรูปแบบ"
4. If user later adds time → recompute silently, diff-report what changed ("ลัคนาของคุณคือ X — readings อัปเกรดแล้ว").

## 4 · Test case (vault owner without time)
Date 1997-05-19 only → engine returns: Sun Taurus 28° ✓ · Moon Libra ~17° ±3° · Life Path 5 ✓ · Kin 239 Blue Overtone Storm ✓ · BaZi 丁丑/乙巳/辛酉 (hour suppressed) · Vimshottari: Mars-balance→Rahu→Jupiter MD stable across full day ✓ (Chitra margin 0.36° > Moon daily motion? NO — Moon moves ~13°/day ⇒ nakshatra flips within the day! → engine prints both Chitra & Hasta branches with their divergent MD timelines, confidence MED) · ASC/houses/D9/Lots/ZiWei-hour: suppressed with explanation.
