# 17 · ELECTIONAL / MUHURTA ENGINE SPEC — Auspicious Timing Finder
> **EN:** "When should I?" module — finds the best real datetime windows for an action, per classical electional + Vedic Muhurta rules already researched in vault (`research/astrology-branches/electional-astrology.md`). Deterministic search over ephemeris.
> **TH:** โมดูลเลือกวันมงคล — ค้นหาช่วงเวลาจริงที่ดีที่สุดสำหรับการกระทำแต่ละประเภท · deterministic

---

## 1 · Search algorithm
```python
def find_windows(action_type, start_date, days=60, lat, lon):
    for each minute-step (or hour coarse→minute fine) t in [start, start+days]:
        score = base_chart_score(t)                # §2
        score += personal_overlay(t, user_chart)   # §3 (needs T1 chart)
        if eclipse_within_24h(t): skip             # hard rule
        if score >= threshold: emit window(t±margin)
    return ranked windows with reasons[]
```

## 2 · Base scoring (classical rules → weights; sources: vault electional note + Lilly tradition)
| Condition | Weight |
|---|---|
| Asc ruler dignified (domicile/exalt) | +10 |
| Moon waxing | +8 |
| Moon void-of-course until next sign | −15 (or skip) |
| Moon applying benefic aspect ≤ orb | +8 per |
| Moon applying malefic hard aspect | −8 per |
| Benefic angular (Jup/Venus in 1/4/7/10 whole-sign) | +7 each |
| Malefic on Asc (Sat/Mars) | −12 |
| Via Combusta (Moon 15 Libra–15 Scorpio) | −6 |
| Mercury retrograde | −6 (launch-type) |

## 3 · Action profiles (which conditions matter most)
| Action | Priority planets/houses | Extra rules |
|---|---|---|
| Marriage/engagement | Venus strong, 7th lord, Moon | avoid Venus retro; Moon-Venus aspect |
| Business launch | MC/10th, Jupiter, Mercury | avoid Mercury Rx; waxing Moon |
| Contract signing | Mercury direct, 7th lord | — |
| Travel | 9th house, Moon strong | avoid Mars on ASC |
| Surgery | avoid Mars/Saturn on ASC/6th, Moon waning? no—Moon strong | classical: avoid malefic on 1/6 |
| Moving house | 4th house, Moon | — |
| Product/app launch (our use!) | Mercury+Jupiter, MC, avoid Rx | fuse with user's transit engine HIGH days |

**Vedic layer (Muhurta):** Abhijit muhurta (~11:36–12:24 local solar) always auspicious +6 · Rahu Kalam daily window −10 (compute from sunrise/sunset tables) · tithi/nakshatra quality table (e.g. avoid Chaturthi for travel etc.) [ship lookup JSON from panchang source drikpanchang at build].

## 4 · Personal overlay (fusion with transit engine)
Window gets `personal_bonus` if: transit hits user's natal benefic point that day (reuse spec-01 hit list, +5..+10 by orb), or user's Ju-Me/Ju-Ve antardasha active (+3), and `personal_penalty` during Ashtama-Shani-style windows (−3). Output always lists BOTH general & personal scores.

## 5 · Test case (concrete deliverable)
"Best day to launch app update, Oct–Dec 2026, Bangkok": scan must avoid Mercury Rx **24 Oct–13 Nov 2026** (in Scorpio = owner's old-note flag) → first HIGH candidates after 14 Nov 2026 with waxing Moon + Jupiter direct… engine emits top-3 dated windows with reason bullets.

## 6 · Templates
TH: *"ช่วงมงคลสำหรับ[action]: [date HH:MM–HH:MM] — เหตุผล: [rules hit]. เลี่ยง: [conflict]"* · EN mirror.
