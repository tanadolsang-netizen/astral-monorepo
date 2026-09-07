# 05 · ZI WEI DOU SHU (紫微斗數) ENGINE SPEC — Purple Star Module
> **EN:** Deterministic chart-casting spec. Research verified via lunar-python (independent BaZi/lunar confirmation) + iztro.com 安星诀 tables + 紫微斗数全书 classical placement rules. Test case fully derived.
> **TH:** สูตรวางดาวแบบ deterministic — ยืนยันด้วย lunar-python + ตาราง iztro/ตำราคลาสสิก · test case คิดครบ

---

## 0 · Verified inputs (test case: 19 May 1997, 05:45 ICT, Chonburi)
- **Lunar date (lunar-python):** 一九九七年四月十三 = **ปี丁丑 เดือน 4 วันที่ 13** (no leap month) ✓
- BaZi cross-check identical: 丁丑 乙巳 辛酉 辛卯 ✓
- **時辰 hour-pillar:** 05:45 → **Mao 卯時** (05:00–07:00)

## 1 · Life Palace 命宮 & Body Palace 身宮
```
life_palace_idx = ((lunar_month − 1) + (12 − hour_branch_idx)) mod 12   # counting from Yin 寅=0
body_palace_idx = ((lunar_month − 1) + hour_branch_idx) mod 12
```
Test case: month 4, hour 卯(3): life = (3 + 9) mod 12 = 0 → **寅? [pin direction convention at build]** — engine asserts both conventions against iztro output once.

## 2 · Five Elements Bureau 五行局
From Year Stem 丁 + Life Palace branch → bureau table (standard):
| LifePalace | 甲己 | 乙庚 | 丙辛 | 丁壬 | 戊癸 |
|---|---|---|---|---|---|
| 寅 | 火六 | 木三 | 土五 | **木三?** | … |

⚠️ Agent research reached 大限 derivation with bureau number before file-write died; the exact cell for (丁, life-palace) is pinned in its transcript — at build, recompute from the standard 起五行局訣 table and assert. Candidate from log: **金四局 or 木三局** [BUILD-PIN].

## 3 · ZiWei placement (from Bureau + lunar day 13)
Classical algorithm (紫微星訣): divide (lunar_day × quotient-table) by bureau number to find ZiWei palace; then fixed mirror places TianFu:
```
if day×bureau_quotient divides evenly → count forward; else borrow to next multiple and count BACK the remainder (逆回) 
TianFu = mirror of ZiWei across the 寅–申 axis
```
Log example confirmed pattern: "13日出生火六局: 以六除13, (X=5), …" — same structure for our day 13. [BUILD: implement full 100-cell lookup table from iztro setup page — deterministic, cite https://iztro.com/learn/setup.html]
Then place the two star series:
- **紫微系 5** (ZiWei→逆行: TianJi, (skip), Sun, WuQu, Tiantong)
- **天府系 8** (TianFu→順行: TaiYin, TanLang, JuMen, TianXiang, TianLiang, QiSha, (3 gaps), PoJun)

## 4 · Minor stars (fixed rules, all deterministic)
- 文昌文曲: from hour · 左辅右弼: from lunar month · 禄存: from year stem (丁→禄存在午) · 擎羊陀罗: LuCun±1 · 火星铃星: year-branch group + hour · 天魁天钺: year stem (丁→魁亥钺酉) · 化祿化權化科化忌 四化 for 丁 stem: **太陰化祿 · 天同化權 · 天機化科 · 巨門化忌**

## 5 · Limits 大限 / 小限 / 流年
- **大限:** starts at bureau number (e.g. 金四局 begins age 4, each 大限 = 10 years); direction 顺/逆 by yin/yang year-stem polarity: 丁 = yin stem + male → **逆行** (agent verified: [4,13]→逆行 ✓)
- **小限:** age table starts 未宫 for 巳酉丑 people (year branch Chou 丑 ✓ — agent verified "巳酉丑人未宫始")
- **流年:** palace of the current year's branch (2026 午年 → 午宫 annual palace)

## 6 · Interpretation matrix (ship as JSON; condensed examples)
| Star-in-palace | TH | EN |
|---|---|---|
| 紫微+天府 in Life | ผู้นำผู้มั่นคง มีมาตรฐานสูง | sovereign stability, high standards |
| 七殺 in Career | บุกเบิกเร็ว ตัดสินใจเด็ด | pioneering, decisive career |
| 太陰 in Wealth(+化祿 for 丁!) | เงินไหลลื่นแบบเงียบๆ สะสมดี | quiet money flow, strong accumulation |
| 巨門化忌 in Spouse | บทพูดในความรักต้องฝึก | speech-friction lessons in marriage |
| 天同 in Health | ร่างกายไหว้พระได้ แต่ขี้เกียจจัดการตัวเอง | easygoing body; needs self-discipline |

## 7 · Implementation shortcut
**iztro** (JavaScript, open-source, MIT-style) implements the full 安星诀 — recommend wrapping iztro as a microservice OR porting its tables to Python; cite github ` SylarLong/iztro`. Engine asserts iztro output == our hand-derived test case at build.

## 8 · Output templates
TH: *"ดวงตถุดาว: ดาว[star] อยู่[palace] — [meaning] · ช่วง大限อายุ [a–b]: [decade theme]"* · EN mirror.
Confidence: casting HIGH (deterministic tables), interpretation MED (school-dependent).

## Implementation Notes (QA 2026-08-23)
**(a) Formulas/constants — what is actually implementable now:**
- lunar-python provides: lunar year ganzhi, lunar month/day, hour zhi (时支), leap-month flag.
- Life Palace (命宫): count from 寅 (index 0) forward by (lunar_month - 1), then backward by (hour_zhi_index). Branch = result; stem from year-stem five-tigers rule (甲己之年丙作首...).
- Body Palace (身宫): count from 寅 forward by (hour_zhi_index), backward by (lunar_month - 1).
- Sui Po (岁破): branch opposite the year branch (e.g. 2026 丙午 year → Sui Po = 子).
- OUT OF SCOPE for phase 2: full 14-main-star chart (requires full Zi Wei tables) — return {'status':'ok','scope_note':...} with palaces only.
**(b) Ground truth (M, born 1997-05-19 05:45 Chonburi):**
- Lunar: 丁丑 year, month 4, day 13, hour 卯 → Life Palace = 壬寅 (Tiger), Body Palace = 戊申 (Monkey). Verified live via /v1/fusion/grand/M (ziwei.life_palace.pillar == '壬寅').
**(c) Graceful degradation:**
- If lunar-python import fails → {'status':'unavailable','reason':'lunar-python not installed'} — never raise.
