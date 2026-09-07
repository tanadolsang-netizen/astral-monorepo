---
name: astrology-engineering
description: Use when horoscope or fortune-app engine work is requested.
version: 1.0.0
author: ox-alpha (curator)
category: research
---

# Astrology Engineering

Two job classes live here: (A) answering personal horoscope requests from real ephemeris math (never generic sun-sign copy), and (B) building the unified fortune engine (specs + code) behind the user's apps (NEW-AI-REBORN FastAPI backend, Astral frontend).

## Ground truth — consult before computing anything
- Validated scripts: `C:/AI/obsidian-vault/scripts/` — `natal_chart.py` (import `compute_chart`; matches the Astra app), `transit_now.py`, `western_advanced.py`, `vedic_advanced.py`, with `de421.bsp` co-located. Do not reinvent chart math.
- Engine-spec library: `C:/AI/research-astrology/` — `00-MASTER-INDEX.md`, specs 01–04 (transit / vedic / synastry / thai-bazi), `verify_calcs.py`, `transit_hits*.py`.
- Birth data lives in vault notes (`Natal Chart - 19 พ.ค. 2540`, `Synastry - Mai (18 ส.ค. 2544)`); vault root = `C:/AI/obsidian-vault`. Per-person verified numbers + corrections ledger: `references/ground-truth-and-corrections.md`.

## Deterministic pipeline rules
- skyfield + JPL DE421 offline. Lahiri ayanamsa: `23.68 + (year_frac − 1997) × 50.29/3600`.
- NEVER mix tropical and sidereal within one interpretation step; label every table with its system.
- Houses = whole-sign unless asked otherwise. Slow movers in retrograde: report the full triple-pass window, never one date.
- BaZi: `lunar-python` (`Solar.fromYmdHms → getLunar().getEightChar()`); hand cross-check: day pillar `(JDN + 49) % 60` (1-based, 甲子=1); year pillar flips at Lichun ~Feb 4; hour stem via 五鼠遁 from day stem.

## Horoscope reading recipe ("เช็คดวงฉัน N วัน")
1. Pull birth data from vault/memory — never re-ask what is already recorded.
2. Daily scan (pattern: `scripts/transit_week_scan.py`): Moon sign + whole-sign house per day, sign ingresses in window, tight aspects (orb ≤ 2.5°) to personal points/ASC.
3. Output: one table per person (date · Moon sign/house · standout signals with orbs), then a theme paragraph, explicitly flag best/worst days, close with the symbolic-interpretation disclaimer line.

## Reading output style (user-set, standing)
- **Tarot-style reading pattern is the DEFAULT for personal readings** (user: "จำแพทเทิลนี้ไว้ พร้อมคำแนะนำคำอธิบายด้วย เหมือนเวลาฟังทาโรต์"): present as numbered cards/spreads — each "card" pairs the astronomical fact (placement, aspect, orb) with its narrative meaning + explicit คำอ่าน (interpretation) + 💡คำแนะนำ (guidance). Never hand the user raw positions to interpret; every data point arrives already interpreted with actionable advice.
- **Raw-ephemeris dumps are rejected** — a per-day table of longitudes/houses/orbs was interrupted and rolled back ("กลับไปแบบเดิม"); data-only output ("no interpretive language") reads as broken, not rigorous. Data lives inside the narrative.
- **Separate people explicitly** in couple readings: user asked "อันไหนของผม ไหนของไหม" — label each person's section (👤 M vs 👧 Mai) before any combined analysis.
- **Length escalation**: "ยาวกว่านี้" / "ลึกกว่านี้" = go deeper per card (mechanism → meaning → timing → advice) and add more cards, not pad prose.
- Long multi-section readings got network-truncated mid-stream several times; on "[continue exactly where you left off]" finish remaining sections without repeating earlier text.

## Pitfalls (each cost real time once)
- **Time-dependent ("today") tests are flaky by design:** a day-lord test asserting Saturday/Saturn passed on Saturdays only and broke Sunday morning. Fix pattern: give the endpoint an optional pinned date (`{"on": "YYYY-MM-DD"}` body → `now_utc` anchor) and pin the fixture to a known weekday. Never assert values derived from `datetime.now()` without an injectable clock.
- **Subagent reasoning-only death:** `delegate_task` children can plan perfectly then die producing NO file ("only internal reasoning, no final answer"). Mitigation that worked: embed the complete spec + all verified numbers in the goal text, demand literal write-tool usage, verify bytes on disk afterward, and treat ~half the batch as casualties — write their deliverables yourself immediately.
- **Legacy bad numbers circulate:** old notes/sessions carried wrong values (ASC Scorpio, composite Sun Gemini, "Sade Sati 2027", fake Moon-sextile). Always check the corrections ledger in the reference file before repeating any previously published claim.
- Lunar nodes move BACKWARD (~18 months/sign): ingress lists run Aquarius→Capricorn etc.; a nodal return lands ~18.6 years after birth, not "next year".
- Sibling sessions rewrite shared files mid-task: a write warning "modified by sibling subagent" means read-before-overwrite (see `multi-session-command-ops`).
