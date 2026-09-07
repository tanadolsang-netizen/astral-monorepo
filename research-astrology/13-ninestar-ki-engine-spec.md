# 13 · NINE STAR KI (九星気学) ENGINE SPEC
> **EN:** Integer-arithmetic Japanese astrology module (year/month/day stars on the Lo Shu magic square). Constants below need one cross-check pin at build [VERIFY].
> **TH:** โมดูลโหราศาสตร์ญี่ปุ่น — เลขจำนวนเต็มล้วนบนจัตุรัสวิเศษ Lo Shu · ค่าคงที่ต้อง pin อีกหนึ่งรอบตอน build

---

## 1 · Algorithms
**Year Star** (LiChun Feb 4 cutoff):
```python
def year_star(y, m, d):
    if (m, d) < (2, 4): y -= 1
    return (11 - (y % 9)) % 9 or 9      # 1997→3? verify; alternative constant: (y+7)%9
```
⚠️ **Constant dispute to resolve at build:** two published conventions give 1997 → **star 3** vs **star 6**. Pin against 2 known-person examples from honke sources, then hardcode. [VERIFY]
**Month Star:** month number from solar terms (same boundaries as BaZi months); `ms = ((year_star − month_index) mod 9)` mapping per standard table [VERIFY].
**Day Star:** sexagenary-day cycle → star = ((JDN + offset) mod 9), offset pinned by anchor day [VERIFY]; reuse JDN from spec 04.
**Lo Shu palaces:** star n's home palace = its position in the base square:
```
4 9 2      (SE S W)
3 5 7      (E  C W)   ← star 5 center; yearly motion = palace of star n in year Y:
8 1 6      (NE N NW)     palace_Y(n) = home(n) shifted by annual Lo-Shu rotation (each year the whole square rotates one step in the trajectory 1→2→3…→9 palace order)
```

## 2 · Test case (born 19 May 1997 — after LiChun)
- Year Star: **[VERIFY pin]** (3 or 6 by convention chosen at build; both shown so the build test catches it)
- Month Star (Si-month): [formula above, compute once constant pinned]
- Day Star: `((2450588 + off) mod 9)` — anchor-pinned [VERIFY]

## 3 · Meaning matrix (condensed)
| Star | Name | Element | Core TH/EN |
|---|---|---|---|
| 1 White | Water | Kan | ลึกลับ ปรับตัวเก่ing / adaptable depth |
| 2 Black | Earth | Kun | ผู้ดูแล อดทน / nurturing supporter |
| 3 Blue | Wood | Zhen | ทะเยอทะยาน ตรงไป / bold initiator |
| 4 Green | Wood | Xun | สื่อสาร มือทอง / networker-craftsman |
| 5 Yellow | Earth | Center | ผู้ควบคุม พลังกลาง / controller-core (kingly) |
| 6 White | Metal | Qian | ผู้นำ หน้าที่ / leader-duty |
| 7 Red | Metal | Dui | รื่นเริง ติดใจ / joy-pleasure seeker |
| 8 White | Earth | Gen | มั่นคง สะสม / steady accumulator |
| 9 Purple | Fire | Li | เปล่งประกาย สายตาคม / radiant-visionary |

## 4 · Annual movement generator
Each calendar year every star advances one palace along the Lo-Shu trajectory; the year's "center" star sets the collective tone. `palace(star, year)`: rotate base square by `(year_star_of_year)` steps. Output = meaning of YOUR star sitting in THAT palace for the year (9×9 interpretation grid JSON — ship full 81 cells TH/EN).
2026 example: year star 2026 = [pinned] → your star's palace → template *"ปี 2026 ดาวของคุณอยู่เรือน [palace]: [meaning]"*.

## 5 · Compatibility quick-rule
Element cycle between two people's Year Stars: generative (Wood→Fire→Earth→Metal→Water→Wood) +6 · same element +4 · destructive (Wood↔Earth, Water↔Fire, Metal↔Wood) −3. Cross-ref spec 03 dimensions.

## 6 · Templates
- TH: *"ดาวประจำปีเกิด: [n]-[color]-[element] — [core]. ปีนี้ดาวคุณย้ายเข้าเรือน [palace]: [annual line]"*
- EN mirror. Pure integers; no ephemeris; unit tests pin the disputed constants.

## Implementation Notes (QA 2026-08-23)
**(a) Formula/constants:** Year Star = `(11 - (year mod 9)) mod 9` mapped 0→9 (spec code path `(11-(y%9))%9 or 9`), LiChun Feb 4 cutoff (born earlier → use year−1); supported domain years ≥ 1900. ⚠️ The §1 constant dispute stays OPEN [VERIFY]: alternative published convention `(y+7)%9` yields a different star — build must pin two known-person honke examples before hardcoding. Month Star = `((year_star − month_index) mod 9)` per standard table; Day Star = `((JDN + offset) mod 9)`; both offsets remain unpinned [VERIFY].
**(b) Ground truth (M, born 1997-05-19, after LiChun):** 1997 mod 9 = 8 → (11−8) mod 9 = **Year Star 3 · Three Blue · Wood · Zhen/East** per the spec's current code (alternative convention would give 6 — see dispute above). JDN(birth) = 2450588 confirms §2. Month Star (Si-month) and Day Star are NOT computable yet — awaiting pinned offsets.
**(c) Degradation:** year < 1900 or invalid date → `{'status':'unavailable','reason':'year_out_of_supported_range'|'invalid_birth_date'}`; hitting an unpinned constant → `{'status':'unavailable','reason':'constant_unpinned:<star|month|day>'}` — never silently pick one side of the dispute.
