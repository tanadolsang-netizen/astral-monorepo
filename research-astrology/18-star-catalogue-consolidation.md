# 18 — Bright-Star Catalogue Consolidation + Astrometry Provenance

**Date:** 2026-09-27 · **Status:** ✅ verified · **Engine:** `src/services/star_catalogue.py`

---

## 1. สรุปปัญหาที่เจอ

`src/services/sky_view.py` มีตารางดาวแบบ hardcode ขนาดตัวเอง 82 แถว แยกจาก
`src/services/star_catalogue.py` ที่ดึงมาจาก Hipparcos — **สองแหล่งความจริงชนกัน**
และแถวทั้งสองฝั่งไม่ตรงกัน

`scripts/report_star_table_divergence.py` เทียบทั้งสองฝั่งกับค่า J2000 ที่คัดลอกมาจาก Hipparcos:

```
71 จาก 82 แถว ผิด
ตัวอย่าง: Ursa Major η (Alkaid) → ได้พิกัดของ α UMa (Dubhe)
```

**สาเหตุ** ไม่ใช่ตัวเลขลอย ๆ — เป็น **row misalignment**: ตอน splice ตารางเข้าไป บรรทัด
เยื้องหนึ่งทำให้ชื่อกับพิกัดไหลต่อกัน แล้วทุกแถวหลังจากนั้นจึงผิดทั้งชุด ยิ่งตรวจด้วยสายตา
ยิ่งเห็นว่า "ดูดี ๆ" เพราะแต่ละแถวเดี่ยว ๆ เป็นค่าที่ถูกต้อง — มันผิดที่ **การจับคู่ชื่อ↔พิกัด**

## 2. สิ่งที่ทำ

### 2.1 รวมเป็นแหล่งเดียว (สิ่งที่ "จำเป็น" เท่านั้น)

`sky_view.STARS` เลิกเก็บพิกัดเอง กลายเป็น **projection** จาก `BRIGHT_STARS` ตอน import
→ ข้อมูลดาวมีที่เดียว ข้อความตรงกันโดยโครงสร้าง ไม่ใช่ด้วยวินัย

> "รวมเป็น 1 engine ได้ถ้าจำเป็น" — จุดที่จำเป็นจริงคือ **source of truth ที่ซ้ำกันและขัดแย้งกัน
> เพียงจุดเดียว** บริการอื่น (`parans_service` 24 รายการ ฯลฯ) แยก semantic กันจริง
> จึงไม่แตะ — การ refactor ที่ไม่จำเป็นคือการเพิ่มความเสี่ยงโดยไม่ได้ประโยชน์

### 2.2 Identity ของดาว — cache เก่าผูก HIP ผิด

พบว่า 3 ดวงแรกที่เทียบไม่ตรง (`Altair`, `Capella`, `Alcyone`) ไม่ใช่ปัญหาตำแหน่ง แต่เป็น
**ชื่อถูกผูกกับ HIP ผิดตัว** — ไม่ใช่ Hipparcos ให้ค่าผิด แต่ name-resolution cache
(ซึ่งเก็บแยกจาก VizieR rows ที่ดึงแพง) ค้างค่าเก่า

| ดาว | HIP ที่ cache เก่าให้ | ถูกต้อง (SIMBAD) |
|---|---|---|
| Altair | 83675 | **97649** |
| Capella | 116228 | **24608** |
| Alcyone | 88528 | **17702** |
| α Centauri | 48310 | **71683** (`alf Cen A`) |

แก้ที่ต้นเหตุ: **เพิ่ม `schema` version เป็น 3 → cache `names` เก่าถูกทิ้งอัตโนมัติ
แต่ VizieR rows ที่ดึงมาแพงยังถูกใช้ซ้ำ** (ไม่ต้องต่อเน็ตใหม่ทั้งชุด)

### 2.3 α Centauri — SIMBAD มีหลาย component

`Alpha Centauri` ไม่ใช่วัตถุเดียวใน SIMBAD ฟังก์ชัน resolver เดิม query ครั้งเดียว
แล้วยอมรับผลแรก (ซึ่งอาจเป็น component ผิด) แก้เป็นวนลูกเรียง candidate
(`simbad_name()` → component `A`/`B`/ปรกติ) และหยุดที่ component ที่ resolve ได้
โดยแยก query/retry ออกเป็น `_hip_from_simbad()`

### 2.4 7 ดวงที่ยังพิสูจน์ไม่ได้ — ถอดออกจากสิ่งที่วาด

`SIMBAD` ไม่มีวัตถุเดียวสำหรับ 7 ชื่อนี้ พิกัดจึงถูก **สืบทอดจากตารางเดิมของแอป** —
ซึ่งกำลังพิสูจน์ว่าไม่น่าเชื่อถือ (`Aldebaran B` ได้ magnitude `1.66` ทั้งที่จริงราว `13`)

ตัดสินใจ: จัด `precision` เป็น `yale_rounded` และ **`sky_view` วาดเฉพาะ `hip2_full`**
→ ข้อมูลที่พิสูจน์ไม่ได้ไม่ถูกวาดทับท้องฟ้าในตำแหน่งที่ผิด

> เหตุผลที่ไม่ใช่ "เก็บไว้เผื่อ": ดาวที่ความสว่างผิดและตำแหน่งผิดที่ถูกวาด
> แย่กว่าการไม่วาดเลย — ผิด 2 ทางแทนที่จะผิด 0 ทาง

## 3. หลักฐาน — ตรวจอิสระจากตัว generator

`tests/test_star_reference_positions.py` เทียบ 19 ดวงกับ **ค่า J2000 ที่ตีพิมพ์**
(ไม่ใช้ Hipparcos ตัวเดิมเป็นหลักฐาน และไม่ใช้ `sefstars.txt` ตามข้อห้าม)

```
ทั้ง 19 ดวง ตรงภายใน ≤ 0.02″
Fomalhaut 0.02″ · Arcturus 0.01″ · Capella 0.01″ · Spica 0.01″ · α Cen 0.00″
```

หมายเหตุการตรวจครั้งแรก: `Alcyone` เคยไม่ตรง 9.88″ — เป็น **ค่า reference ที่ผมพิมพ์ผิด**
(สัมผัส `+23°56′` แทน `+24°06′`) ไม่ใช่ catalogue ผิด แก้ที่ reference

## 4. Mutation test — เทสต์จับบั๊กได้จริงไหม

| การทำลาย | ผล |
|---|---|
| seed กลับไปใช้ `hash(name)` | ✅ CAUGHT (`test_draw_spread_is_stable_across_processes`) |
| top-up กลับไป `rng.choice(ALL_CARDS)` | ✅ CAUGHT (sweep 300 ชื่อ) |
| ตัด filter `hip2_full` ออกจาก `sky_view` | ✅ CAUGHT |
| ทำให้ Sirius Dec เพี้ยน 0.5° | ✅ CAUGHT (`test_catalogue_position_matches_published_value[Sirius]`) |

## 5. บั๊กที่เจอระหว่างทาง (นอกขอบเขตดาว)

`tests/test_tarot.py::test_draw_spread_no_duplicate_cards_within_spread` fail แบบ
order-dependent (ผ่าน 5/5 เมื่อรันเดี่ยว) สืบไปเจอ **บั๊กจริง 2 ตัวใน `tarot_service.draw_spread`**

1. **`seed = hash(name)`** — Python salt `hash(str)` ต่อโปรเซส (`PYTHONHASHSEED`)
   → **คนเดิมเปิดแอปใหม่ได้ดวงใหม่ทุกครั้ง** เทสต์เดิมผ่านเพราะทั้งสอง call
   อยู่ในโปรเซสเดียวกัน แก้เป็น `sha256(name)` แล้วเพิ่มเทสต์ที่รัน subprocess
   ด้วย `PYTHONHASHSEED` 3 ค่า
2. **ลูปเติมการ์ดสุ่มจากทั้งสำรับโดยไม่เช็คซ้ำ** — หลัง dedupe ถ้ายังไม่ครบ
   10 ใบ (celtic cross) จะเติมการ์ดที่อาจซ้ำ → แก้เป็นสุ่มจาก `remaining` เท่านั้น

> บั๊กข้อ 1 สำคัญกว่าที่ดู: มันทำให้ "อ่านดวงวันนี้" ของผู้ใช้ไม่คงที่ ซึ่งเป็นสิ่งที่
> ผู้ใช้จับได้ทันทีโดยไม่ต้องรู้เรื่อง seed

## 6. สถานะสุดท้าย

```
catalogue   86 rows = 79 hip2_full (ตรวจแล้ว) + 7 yale_rounded (กันไว้ ไม่วาด)
sky_view    79 drawable · 52 สว่างกว่า 2.5 mag
tests       755 passed, 0 failed   (เดิม 727)
```

ยังไม่ได้ทำ: proper-motion propagation ใน `sky_view` (ตอนนี้วาด J2000 ตรง ๆ) ·
Mizar ไม่อยู่ใน base set เดิม (เป็นช่องว่างความครอบคลุม ไม่ใช่บั๊ก)

---

## §2.3 หมายเหตุเชิงหลักการ

ตัวเลขดาราศาสตร์ที่ถูกต้อง **ไม่ได้** ทำให้เนื้อหาเชิงสัญลักษณ์กลายเป็นข้อเท็จจริง
แต่ตัวเลขที่ **ผิดโดยเงียบ** ทำลายความน่าเชื่อถือทั้งระบบ — และแย่กว่าการไม่มีตัวเลขเลย
ดู `16-parans-frame-validation.md` §2.3 สำหรับกรอบเดียวกัน
