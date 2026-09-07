# S3 COMBAT REPORT — P0 Gate Check (22 ส.ค. 2026, 18:5x)
> จาก: S3 Fortune-telling session · ถึง: Command Center (CMD 👑) + S1 FORGE
> สรุป: **P0 ยังไม่ผ่าน gate** — 137/142 tests ผ่าน, 5 พัง (3 สาเหตุราก)

## ผลรันจริง (`./.venv/Scripts/python.exe -m pytest -q`)
```
5 failed, 137 passed in 3.16s
```

## สาเหตุรากทั้ง 3 (พร้อมจุดแก้)

### 🔴 1. BaZi typo ทำ test ล้ม 2 ตัว
`src/services/bazi_service.py` บรรทัด ~166:
```python
"label_th": f"{STEM_ELEMENT_TH[dm_idx]}{'ยิน' if dm_idx % 2 else 'หยาง'}"
```
`'ยิน'` → ต้องเป็น `'หยิน'` (ตก ห) — แก้แล้ว `test_owner_four_pillars` + `test_year_lichun_cutoff` จะกลับมาเขียวทันที (pillars ถูกหมดแล้ว: 丁丑/乙巳/辛酉/辛卯 ตรงกับ lunar-python ที่ S3 verify ไว้)

### 🟠 2. Lichun confidence ไม่ตรงสัญญา
`test_year_lichun_cutoff`: วันที่ 1997-02-01 (ใกล้ cutoff 4 ก.พ.) ต้องได้ `confidence=MEDIUM` แต่ impl คืน `HIGH`
→ S1 ต้องเพิ่มกฎใน bazi_service: ถ้า |date − Lichun(fixed-date approx)| ≤ ~7 วัน → MEDIUM (ตาม spec 04 §1.1 ที่บังคับไว้)

### 🟠 3. Synastry emotional_bond กลับด้าน (สำคัญสุด — แตะมาตรฐานยอมรับของ S3)
`test_identical_charts_score_higher_emotional_bond_than_opposite`: ดวงเหมือนกันเอง (65) ต้อง > ดวงตรงข้าม (79) แต่กลับกัน
→ น่าจะมาจากการที่ดวงตรงข้ามได้แต้มจาก opposition ที่คูณ HARMONIC 0.25 แล้วยังทำ dimension นั้นบวกสุทธิ หรือ capacity normalization ของ emotional_bond ต่ำเกิน — ให้ S1 ตรวจ `synastry_scoring.py` §DIMENSIONS/CAPACITY + กรณี same-chart (aspect ต่อตัวเองควรได้ conj 1.0 เต็มๆ)

### 🟡 4. Tarot tilted_toward — test/impl ขัดกัน (ต้องตัดสิน ไม่ใช่แก้เฉยๆ)
`test_api_draw_with_birth_data_reports_tilt` + `test_weighted_draw_has_no_duplicates`: test คาด `earth` แต่ impl ให้ `air` สำหรับดวง Mai
→ **spec ยังไม่นิยาม "tilt basis"** (นับ personal planets เท่านั้น? รวม ASC/MC ไหม?) — ให้ S1 เลือกนิยามแล้ว align อีกฝั่ง หรือยิงคำถามกลับ Command

## สถานะ Git (งาน A1 ของ S1 ยังไม่เสร็จ)
```
 M src/main.py  M src/routers/synastry.py  M src/services/chart_service.py
 ?? src/routers/bazi.py  ?? src/services/bazi_service.py
 ?? src/services/synastry_scoring.py  ?? tests/test_bazi.py  ?? tests/test_synastry_score.py
```
⚠️ Fusion Engine ยัง uncommitted — เสี่ยงหาย ให้แก้ #1 แล้ว commit เป็นล็อตเดียว

## คำแนะนำลำดับแก้ (ให้ S1)
1. typo หยิน (1 นาที) → รัน pytest ให้เหลือ 3 failed
2. Lichun confidence rule (10 นาที) → เหลือ 2
3. emotional_bond inversion (ตรวจ scoring) → gate เขียว
4. tilted_toward: ตัดสินนิยามก่อนแก้
5. commit ทั้งล็อต + push → ประกาศ P0 ผ่าน → S3 เริ่มยิงดวงจริงผ่าน API (P3)
