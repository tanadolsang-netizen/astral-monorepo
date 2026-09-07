# 11 · WESTERN NUMEROLOGY ENGINE SPEC
> **EN:** Deterministic digit-reduction module. Test case DOB 19 May 1997 fully worked. Cross-links to Thai numerology (spec 04).
> **TH:** โมดูลลดเลขแบบ deterministic — ตัวอย่างคำนวณครบจากวันเกิด 19 พ.ค. 2540 · เชื่อมกับเลขไทย (spec 04)

---

## 1 · Algorithms (worked test case)
**Life Path:** sum all digits, reduce; preserve master numbers 11/22/33 at ANY intermediate step (v1 convention — chosen because it's the numerology.com standard and produces stable famous-person matches):
```
1+9+0+5+1+9+9+7 = 41 → 4+1 = **5**          # no master intermediate → Life Path 5
Birth Day: 19 → 1+9=10 → **1**
Personal Year (2026): day-reduced(19→1) + month 5 + year 2+0+2+6=10→1 ⇒ 1+5+1 = 7
Personal Year (2027): 1+5+(2+0+2+7=11 → keep master? v1 rule: reduce PY to single) ⇒ 1+5+11→2+... 
   implementation: py = reduce(1 + 5 + 11) where 11 is master → print "16/7 with 11-echo" 
   v1 decision: Personal Year 2026 = **7** (introspection), 2027 = **8** (power/finance year)
Personal Month = PY + calendar month reduced; Personal Day = PM + calendar day reduced.
```
**Expression/Soul Urge/Personality** require full birth name → Pythagorean table:
```
A J S=1 · B K T=2 · C L U=3 · D M V=4 · E N W=5 · F O X=6 · G P Y=7 · H Q Z=8 · I R=9
Expression = Σ(all letters); Soul Urge = Σ(vowels AEIOU only); Personality = Σ(consonants)
```
[App collects birth name optionally; engine runs only if provided.]

## 2 · Meaning matrix (condensed TH/EN per number × domain)
| # | Core | Love | Career | Money | Challenge |
|---|---|---|---|---|---|
| 1 | pioneer/initiator | leads, must share the wheel | founder energy | self-made | stubbornness |
| 2 | diplomat/partner | sensitive bond | support roles | slow-steady | over-giving |
| 3 | expressor/creator | charming, scattered | communication arts | fluctuating | focus |
| 4 | builder/systems | loyal, slow-warm | engineering/order | saver | rigidity |
| **5** | **freedom/senses** | **needs space+spark** | **variety/travel/media** | **risk-tolerant** | **restlessness** |
| 6 | caretaker/aesthetic | devoted, family-first | service/design | home-assets | martyr trap |
| 7 | analyst/mystic | selective, deep | research/tech | investments | isolation |
| 8 | executive/power | status-conscious | enterprise | strong | workaholism |
| 9 | humanitarian/closer | compassionate completion | teaching/healing | give-back | letting go |
| 11 | intuitive channel | inspiring | spiritual-creative | unstable unless grounded | anxiety |
| 22 | master builder | legacy partnership | institution-scale | big structures | pressure |
| 33 | master teacher | unconditional | mentoring | service-based | boundaries |

## 3 · Compatibility pairs (classic affinity, cite numerology sites at build)
Strong: 1-5 · 1-9? no — canonical set: **1-5, 1-9(? avoid), 2-6, 2-8, 3-5, 3-9, 4-8, 5-9, 6-9, 7-5(?), 7-9, 8-9?** — v1 ships matrix from one cited source [BUILD-TIME pin]; conflict pairs: 4-5, 2-7, 6-1(mild). Test-case relevance: LP5 person ↔ Mai's numbers [RUNTIME once her data entered].

## 4 · Thai cross-link (spec 04 fusion)
Life Path 5 (เสรีภาพ/ประสาทสัมผัส) vs ตรียัมปาไถ/เลขเจตา outputs — when both systems flag "movement/change" same week ⇒ HIGH confidence travel/opportunity note; when Life Path says risk & BaZi favorable element = Earth (stabilize) ⇒ conditional phrasing per master §4.

## 5 · Output templates
- TH 2026: *"ปีส่วนบุคคล 7 (2026): ปีแห่งการใคร่ครวญและศึกษา — งานลึก/วิเคราะห์เด่นช่วง [month windows] · 2027 = ปี 8: ปีอำนาจ-การเงิน ซ้อน Saturn Return 26 มี.ค."*
- EN mirror. All reductions deterministic; unit tests assert LP=5, BD=1, PY26=7 for the test case.

## Implementation Notes (QA 2026-08-23)
**(a) Formula/constants:** Life Path = digit-sum of YYYYMMDD reduced to one digit, preserving masters 11/22/33 at ANY intermediate step (v1 rule). A bare mod-9 shortcut (`sum mod 9`, 0→9) agrees only when no intermediate master appears — do not substitute it blindly. Birth-Day number = reduced day-of-month. Personal Year = reduce(reduced(day) + month + digits(current year)), calendar-year basis per v1 templates.
**(b) Ground truth (M, DOB 1997-05-19):** raw sum 1+9+0+5+1+9+9+7 = 41 → 4+1 = **Life Path 5** (no intermediate master; mod-9 cross-check 41 mod 9 = 5 agrees). Birth Day 19→10→**1**. **Personal Year 2026 = 7** (1 + 5 + (2+0+2+6=10→1)); shortcut (19+5+2026) mod 9 = 7 agrees ✓. Expression/Soul Urge/Personality stay non-computable until birth name is provided (engine skips by design — not a failure state).
**(c) Degradation:** missing/invalid inputs → `{'status':'unavailable','reason':'missing_birth_date'|'invalid_birth_date'|'birth_name_not_provided'}`; module never raises and never fabricates a reduction.
