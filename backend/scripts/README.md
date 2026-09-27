# `backend/scripts/` — สิ่งที่ต้องรู้ก่อนลบอะไร

สคริปต์ทั้งหมดนี้เป็น **เครื่องมือวินิจฉัย/ตรวจสอบ** ไม่ใช่โค้ดที่รันตอนบริการ แต่**บางไฟล์ถูก production และ test import จริง** — ห้ามลบมั่ว

## 🔴 ห้ามลบ — มีคน import อยู่

| ไฟล์ | ถูก import โดย |
|---|---|
| `accuracy_report.py` | `src/routers/accuracy.py` (production) |
| `meeus_reference.py` | `tests/test_parans_frames.py` (test) |
| `probe_nutation_split.py` | import `meeus_reference` (ยังไม่มีใครเรียกมัน แต่อยู่ในชุดงานเดียวกัน) |

> `accuracy_report.py` กับ `meeus_reference.py` ดูเหมือน probe เหลือ แต่ลบแล้ว build พังทันที

## 🟢 ยืนยันแล้ว — หลักฐานของงาน parans frame (27 ก.ย. 2026)

อันเหล่านี้คือหลักฐานที่ยืนยันการแก้ครบ 3 ข้อ **เก็บไว้เป็นหลักฐานได้**

| ไฟล์ | บทบาท |
|---|---|
| `fetch_star_catalogue.py` | ดึงตำแหน่ง ICRS + proper motion จาก VizieR `I/311/hip2` (van Leeuwen 2007) ผ่าน SIMBAD — **แหล่งอิสระ** ไม่ใช้ `sefstars.txt` |
| `star_catalogue.json` | ผลลัพธ์ข้างบน (23 ดวงจริง + `Aldebaran_N` ที่ note ไว้ว่าไม่ใช่ดาวอิสระ) |
| `emit_stars_table.py` | ปั่นค่า `STARS` literal ความละเอียดเต็มจาก catalogue |
| `sofa_oracle_check.py` | **oracle อิสระ** เทียบ engine กับ ERFA `pnm06a` → `0.000000″` |
| `probe_omitted_terms.py` | วัดว่า frame เดิมตกเทอมอะไร → `228″/cy` (docstring เดิมเขียน `0.2″/cy` = ผิด 1140 เท่า) |
| `probe_poa_criterion.py` | พิสูจน์ว่าเกณฑ์ exact-angle เดิมผิด — Sun × Alcyone ที่ ASC มี POA ต่างกัน `0.69′` แต่โค้ดให้ `0` คู่ |
| `fetch_bright_star_catalogue.py` | รวม catalogue เดียว (Yale BSC ∪ parans) → `star_catalogue.py`; resolve ผ่าน SIMBAD แล้ว**ตรวจตำแหน่งจริง** กันชื่อผิดกลายเป็น astrometry |
| `bright_star_cache.json` | cache ของ `fetch_bright_star_catalogue.py` (**schema 3**) — ลบได้ แต่จะต้องต่อเน็ตใหม่ · bump schema เมื่อเปลี่ยนวิธี resolve ชื่อ เพราะชื่อ↔HIP ที่ผูกเก่าจะทำให้ดาวผิดตัวเงียบ ๆ |
| `probe_parans_validation.py` | ตรวจ chain ด้วย 2 อ้างอิงอิสระ |
| `probe_swisseph_compare.py` | เทียบกับ Swiss Ephemeris 2.10.03 |
| `report_star_table_divergence.py` | **permanent** — เทียบตารางดาวของแอปกับ catalogue ด้วยค่า J2000 ตีพิมพ์ จับ row misalignment ที่ตาเปล่ามองไม่เห็น |

> ⚠️ `asu-tsv` ของ VizieR **เมิน `-c.eq` / `-c.r` เงียบ ๆ** — คืนแถวแรกของตาราง ไม่ใช่ cone search
> ต้องดาวน์โหลด `Hpmag<7.5` แล้วหาเฉียะใกล้สุดในเครื่อง (แบ่งช่วง HIP ไม่ให้เกิน 5000 แถว)

## 🟡 one-off diagnostics — รันครั้งเดียวเสร็จ ไม่ต้องรันซ้ำ

`probe_api_shape.py` · `probe_obliquity_indep.py` · `probe_paran_bugs.py` · `probe_paran_validate.py` ·
`probe_parans_debug.py` · `probe_precession_diag.py` · `probe_precession_meeus.py` ·
`probe_star_precession.py` · `probe_test_truth.py` · `precession_ref.py` · `star_accuracy.py`

> เป็นผลจากการไล่หาสาเหตุทีละจุด ถ้าจะลบ — **ลบทั้งชุดพร้อมกัน** และอย่าลบ `meeus_reference.py`

## ⚪ งานคนละเรื่อง — ไม่เกี่ยวกับ parans

`audit_auth.py` (สแกน auth) · `deep_scan.py` (Qwen3 scan) · `gen_tarot_bing.py` / `gen_tarot_images.py` (สร้างภาพ) ·
`horizons_validator.py` (JPL Horizons) · `precision_audit.py` · `register_future_predictions.py` (ลงทะเบียน prediction) ·
`verify_ayanamsa.py`

**ไม่ควรแตะในงาน parans** — เป็นของงานอื่น

---

## รันยังไง

```bash
cd C:/AI/backend
./.venv/Scripts/python.exe scripts/sofa_oracle_check.py     # oracle หลัก
./.venv/Scripts/python.exe scripts/probe_omitted_terms.py  # ตกเทอมอะไร
```

`fetch_star_catalogue.py` ต่อ **เน็ต** (VizieR/SIMBAD) — ผลถูก commit เป็น `star_catalogue.json` แล้ว ไม่ต้องรันซ้ำเว้นแต่อยากรีเฟรช

## เทสต์

```bash
cd C:/AI/backend
./.venv/Scripts/python.exe -m pytest tests/test_parans_precession.py tests/test_parans_frames.py -q   # 29
./.venv/Scripts/python.exe -m pytest tests/test_star_catalogue_integrity.py -q                        # 6
./.venv/Scripts/python.exe -m pytest tests/test_star_reference_positions.py -q                        # 20  ← ตรวจค่า published
./.venv/Scripts/python.exe -m pytest tests/ -q                                                          # 755
```
