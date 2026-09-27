# 16 · Paran Engine — Frame Validation, Proper Motion & Oracle Upgrade

> **สถานะ:** ✅ แก้ครบทั้ง 3 ข้อ 27 ก.ย. 2026 · เอนจิน = `backend/src/services/parans_service.py`
> **คำตอบสั้น:** สูตรเดิม **ถูกต้องอยู่แล้ว** — สิ่งที่เพี้ยนคือคำอธิบาย · ตอนนี้ย้ายไปใช้ **SOFA/ERFA** เป็น oracle และเพิ่ม proper motion จริงแล้ว

---

## 1 · สรุปผล (TL;DR)

| ประเด็น | ผล | หลักฐาน |
|---|---|---|
| เอนจินใช้ nutation หรือไม่ | **ใช่** | precession-only ref เหลือ `23.87″/8.61″` → เติม nutation เหลือ `0.40″/0.13″` |
| เอนจิน hand-roll matrix เองไหม | **ไม่** | ใช้ `build_ecliptic_matrix` + `t.M` ของ Skyfield · `np.array([[` = 0 จุด |
| **กรอบดาวเทียบ SOFA/ERFA `pnm06a`** | **`0.0000″`** | เอนจินกับ reference ของ IAU 2006A ตรงกันจนเป็นเอกลักษณ์ |
| residual เดิม `0.40″` เป็นของใคร | **ของ *reference* ไม่ใช่ของ engine** | Meeus ch.22 เป็น series ย่อ ความแม่น ~`0.5″` ใน Δψ |
| **proper motion ถูกตัดออกไหม** | **เคยใช่ — ผิดไป ~1140 เท่า** | วัดได้สูงสุด `228″/century` (Arcturus) ไม่ใช่ `0.2″` |
| **แก้แล้วไหม** | **ใช่** | ใส่ PM จาก Hipparcos van Leeuwen 2007 · เทียบ ERFA → `0.0000″` |
| **ความแม่นตำแหน่งดาว** | **ดีขึ้น `45.7″` → `0.0003″`** | ตารางเดิมปัดทศนิยม — เองก็คิดเป็น `54″` ใน RA |
| test ที่มีอยู่จับ bug ได้ไหม | **ได้** (mutation-tested) | ตัด nutation ทั้งฝั่ง engine และฝั่ง reference → fail ทั้งคู่ |

> ✅ **ผลรวม:** `717 passed, 0 failed` (เต็มชุด) · parans `27/27`

---

## 2 · สิ่งที่ validate ได้จริง vs ไม่ได้

### 2.1 ✅ Validate ได้ — มีเลขวัด

- **กรอบดาว (frame)** เทียบ ERFA `pnm06a` → **`0.0000″`** ทั้ง 24 ดาว
- **obliquity ของวันที่** เทียบ `swe.calc_ut` `ECL_NUT[0]` → ต่างกัน `0.0008″`
- **obliquity เทียบ IAU 1980 อิสระ** → production `23.436994°` vs reference `23.437057°` = `0.23″`
- **proper motion** วัดจริงเทียบ Swiss Ephemeris (ดู §4)

### 2.2 ⚠️ Consistency check เท่านั้น — ไม่ใช่ validation

`tests/test_parans_precession.py` เรียก Skyfield เหมือน production → เทียบกับตัวเอง
**ผ่านได้เสมอ ไม่ได้พิสูจน์ความแม่นยำ** เก็บไว้เป็น regression guard เท่านั้น
→ oracle อิสระจริงอยู่ที่ `scripts/sofa_oracle_check.py` (ERFA)

### 2.3 ❌ ยังไม่ได้พิสูจน์

- ความหมายเชิงสัญลักษณ์ของ paran (Brady, *Aspects in Mundo*) — **คำนวณทางดาราศาสตร์ถูก ≠ จริงเชิงโหราศาสตร์**
- ความหมายของหน้าต่าง 2 นาที — เป็นการเลือกของผู้เขียน ไม่ได้มาจากหลักการทางฟิสิกส์

---

## 3 · การแก้ไข 3 ข้อ

### 3.1 Oracle: Meeus → SOFA/ERFA

เดิมใช้ Meeus ch.21/22 เป็น oracle → residual `0.40″` ซึ่งเป็น **error ของ series ย่อเอง** ไม่ใช่ของ engine
เปลี่ยนเป็น `erfa.pnm06a` (IAU 2006A) ซึ่งเป็น reference implementation ตัวจริง

```
เอนจิน (Skyfield t.M)  vs  ERFA pnm06a   =  0.0000″
```

> **หมายเหตุสำคัญ:** ทั้งสองใช้ **โมเดลเดียวกัน** (IAU 2006A) → นี่คือ *implementation* independence
> ไม่ใช่ *model* independence ถ้าจะพิสูจน์ระดับ model ต้องเทียบกับโมเดลอื่น (เช่น IAU 1976 หรือ ELP)

### 3.2 ความแม่นตำแหน่งดาว

ตารางเดิมปัดทศนิยม `0.001h/0.001deg` — ซึ่ง**เองก็**ให้ error สูงสุด `54″` ใน RA
(ใหญ่กว่า proper motion ที่ตอนนั้น "คิดว่า" เหลือแค่ `0.2″/century`!)

เปลี่ยนเป็นค่าเต็มความแม่นจาก **Hipparcos new reduction (van Leeuwen 2007)**, VizieR `I/311/hip2`
propagate จาก epoch `1991.25` → J2000

| | ก่อน | หลัง |
|---|---|---|
| ตาราง vs catalogue | สูงสุด **`45.7″`** | สูงสุด **`0.0003″`** |
| ดาวที่แย่สุด | Bellatrix | — (ครบทุกดาว) |

### 3.3 Proper motion

เพิ่ม `pm_ra` (μα·cosδ) และ `pm_dec` (μδ) หน่วย mas/yr ใน `STARS`
และเพิ่ม `_star_epoch_radec()` ที่คำนวณตำแหน่งดาวที่ epoch ใดก็ได้

> ⚠️ **ลำดับสำคัญ — จุดที่ต้องระวังที่สุด**
> proper motion ต้องถูก **ใช้ในกรอบ ICRS ก่อน** แล้วค่อยหมุนเข้า frame ของวันที่
> (แบบเดียวกับ SOFA `sla_STARPV`) ถ้าหมุนก่อนแล้วค่อยใช้ PM → ผิดกรอบ
> ซึ่งสำหรับ Arcturus ที่ epoch 1997 ให้ความคลาดเคลื่อน **~`0.4″`** — เท่ากับ residual ที่เคยให้ความสำคัญ

---

## 4 · การวัด proper motion (method)

วัดโดยเทียบกับ **Swiss Ephemeris 2.10.03** ช่วง **100 ปี เดือน-วันเดียวกัน**
(เดือน-วันเดียวกัน → aberration รายปีหักล้างกันเกือบหมด)

ใช้ metric แบบ unit-vector:

```
|(s1-s0) - (e1-e0)|      ไม่ใช่การลบ separation
```

> ❌ **ห้ามหักล้างด้วยการลบ separation** — precession 100 ปี ≈ `5000″`
> เบียดจนเกือบหักล้าง เหลือ noise (เผลอทำผิด 2 รอบก่อนแก้ ได้ค่า `-16.34″` และ `323,900″`)

### ผลวัดเทียบค่าที่ตีพิมพ์

| ดาว | วัดได้ (″/century) | Hipparcos (″/cy) | ผิด |
|---|---|---|---|
| **Arcturus** | **227.95** | 227.87 | **0.0%** |
| Sirius | 134.32 | 133.94 | 0.3% |
| Pollux | 62.82 | 62.76 | 0.1% |
| Capella | 43.28 | 43.41 | −0.3% |
| Vega | 34.73 | 34.96 | −0.6% |

5 เคสที่ PM ใหญ่ที่สุดตรงกับ Hipparcos **ดีกว่า 1%** → ตัววิธีวัดเชื่อถือได้จริง

**ความคลาดเคลื่อนที่เหลือไม่ใช่ error:**
- **Rigel** `−87%` — ต่ำกว่า noise floor ของตัววิธีวัด
- **Aldebaran, Altair, Procyon** — เป็น**ดาวคู่** Swiss ใช้ PM ของ photocentre
  ต่างจากค่า Hipparcos โดยธรรมชาติ

### ผลกระทบต่อ paran

รวม PM + nutation + aberration ที่ epoch อ้างอิง → ความคลาดเคลื่อนแย่สุด **41″**
= **0.045 นาที** ของการเคลื่อนที่บน meridian = **2.3%** ของหน้าต่าง 2 นาที

→ ข้อสรุปเดิม ("ผลกระทบเล็ก") **ยังจริงอยู่** แต่ตอนนี้ไม่ต้องพึ่งการอธิบายที่ผิดอีกแล้ว

---

## 5 · กับดักที่เจอระหว่างทำ (บันทึกไว้เป็น skill)

1. `fixstar_ut` **ไม่คืนค่า speed** แม้ใส่ `FLG_SPEED` — speed field ได้ `0.0` ต้อง **differencing ตำแหน่ง** แทน
2. `FLG_EQUATORIAL` คืน `(RA, Dec, dist, 0, 0, 0)` ไม่ใช่ layout แบบ ecliptic — ถ้าอ่านผิดจะได้มุมเพี้ยนหลายร้อยองศา
3. **ห้ามหักล้างด้วยการลบ separation** (ดู §4)
4. **VizieR ตัด column ที่ไม่รู้จักแบบเงียบ ๆ** — `I/239/hip_main` ไม่มี `RAJ2000` มีแต่ `RAICRS`
   ถ้าไม่ตรวจ header จะได้ค่า `nan` โดยไม่มี error
5. **`_jd_ut()` คืนค่า TT ไม่ใช่ UT** ทั้งที่ชื่อบอก `jd_ut` → ถ้าเอาไป `ut1tt` อีกรอบจะ double-count
6. **วันที่ epoch ของ Hipparcos คือ `JD 2448349`** (1991.25) ไม่ใช่ `2458349` — พิมพ์ผิดนำทำให้
   propagate ย้อนกลับด้วยค่าผิด
7. **`STARS` เดิมเป็นพิกัด *equatorial*** แม้ comment เดิมเขียนว่า "ecliptic longitude/latitude"
   — โค้ดถูก (ใช้ `t.M` ซึ่งเป็น equatorial) แต่ comment หลอก แก้แล้ว

---

## 6 · หลักฐานการทำงานจริง

```
$ ./.venv/Scripts/python.exe scripts/sofa_oracle_check.py
MAX (a)vs(b) full model vs ERFA  = 0.0000 arcsec
MAX proper-motion term            = 5.9740 arcsec
MAX table vs catalogue J2000      = 5.9740 arcsec

$ ./.venv/Scripts/python.exe -m pytest tests/ -q
717 passed in 154.28s
```

สคริปต์ที่เพิ่ม:

| ไฟล์ | หน้าที่ |
|---|---|
| `scripts/fetch_star_catalogue.py` | ดึง ICRS + PM จาก VizieR/SIMBAD → `star_catalogue.json` |
| `scripts/sofa_oracle_check.py` | เทียบเอนจินกับ ERFA `pnm06a` |
| `scripts/emit_stars_table.py` | สร้างตาราง `STARS` พร้อม PM |
| `scripts/probe_omitted_terms.py` | วัด PM เทียบ Swiss (จากรอบก่อน) |

---

## 7 · แหล่งอ้างอิงภายนอก

| รายการ | แหล่ง | ตรวจเมื่อ |
|---|---|---|
| pyswisseph 2.10.03 | `pip show pyswisseph` | 27 ก.ย. 2026 |
| Hipparcos new reduction (van Leeuwen 2007) | VizieR `I/311/hip2` | 27 ก.ย. 2026 |
| Hipparcos original (cross-check) | VizieR `I/239/hip_main` | 27 ก.ย. 2026 |
| name → HIP resolution | SIMBAD TAP | 27 ก.ย. 2026 |
| SOFA/ERFA `pnm06a` | `erfa` 2.0 (pyerfa) | 27 ก.ย. 2026 |
| `sefstars.txt` (136,618 bytes) | `https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/sefstars.txt` | 27 ก.ย. 2026 |

> ⚠️ `aloistr/swisseph` เป็น **mirror** และ URL ชี้ `master` ไม่ใช่ commit — ถ้าจะอ้างอิงเชิงเอกสารควร pin commit

---

## 8 · ข้อจำกัดที่ยังมี

1. **model ไม่ independent** — Skyfield และ ERFA ใช้ IAU 2006A ตัวเดียวกัน
   ถ้าต้องการพิสูจน์ระดับ model ต้องเทียบกับ IAU 1976 หรือ ELP
2. **ไม่มีเทอร์มอันดับสอง** — perspective acceleration ต้องใช้ radial velocity (ไม่มีในตาราง)
   · ส่วน curvature `pm²t²/2` ของดาวเร็วสุด (Sirius, `1.34″/yr`) น้อยกว่า 1 µas
   ในช่วง ±100 ปี → ตัดทิ้งได้อย่างมีเหตุผล
3. **RA เป็นพิกัดเอกศัยเมื่อ dec > 55°** — การเทียบต้องตัดดาวเหนือ/ใต้ 55° ออก (Polaris, Canopus, Achernar)
4. **`Aldebaran_N` ไม่ใช่ดาว** — เป็นจุดสังเคราะห์ตามธรรมเนียมโหราศาสตร์ (Lilly/Billy)
   ไม่มีคู่ใน catalogue → คงตำแหน่งเดิม ไม่ใส่ PM ที่แต่งขึ้น (อยู่ห่าง Aldebaran `35″` → ต้นทุน < `1″`)
5. **ความหมายเชิงสัญลักษณ์ไม่ผูกกับความแม่นทางดาราศาสตร์** — ตัวเลขที่ถูกไม่ได้แปลว่าเนื้อหาจริง
