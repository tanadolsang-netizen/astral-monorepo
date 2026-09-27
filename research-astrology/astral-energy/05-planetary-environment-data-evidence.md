# 05 — สิ่งแวดล้อมดาวเคราะห์: หลักฐานเชิงข้อมูลที่วัดได้จริง

> **ไฟล์:** `C:/AI/research-astrology/astral-energy/05-planetary-environment-data-evidence.md`
> **วันที่ค้นค้น:** 2026-09-27
> **หลักการ:** ทุกตัวเลขในไฟล์นี้มาจากงานวิจัยที่ตรวจสอบได้จริง (abstract / full text / DOI) ไม่มีการประมาณขึ้นเอง ถ้าแหล่งใดตรวจสอบตัวเลขไม่ได้ ให้ถือว่า "ยังไม่ยืนยัน" และระบุไว้ตรง ๆ

---

## บทนำ: สิ่งที่ "พลังเอาทรัล" อ้าง และสิ่งที่วัดได้จริง

คำว่า "พลังเอาทรัล" (astral energy) ในแอปดวงชะตา มักถูกเล่าโดยผสมสามอย่างที่แยกจากกันไม่ได้ในหัวคนทั่วไป:

1. **ปรากฏการณ์ที่วัดได้จริง** — Kp index, Ap index, ความผันผวนของสนามแม่เหล็ก, ความสว่างของดวงจันทร์, อุณหภูมิ, ความชื้น, แสง
2. **จังหวะชีววิทยาของมนุษย์เอง** — circadian (~24 ชม.), ultradian (~90 นาที), menstrual cycle (~28 วัน)
3. **สิ่งที่ยังไม่มีหลักฐานว่ามีจริง** — สนามพลังเอาทรัล หรือ "พลังงานจักรวาล" ที่ดาวเคราะห์ส่งให้

**หัวใจของไฟล์นี้:** หมวดที่ 1 และ 2 มีงานวิจัยจริงและตัวเลขจริงบางส่วน ส่วนหมวดที่ 3 ไม่มีเลย และการเดินจาก (1)+(2) ไปสู่ (3) คือการกระโดดเชิงตรรกะ ไม่ใช่การสังเคราะห์ทางวิทยาศาสตร์

> ⚠️ **การแก้ไขข้อมูลอ้างอิงที่พบระหว่างค้นค้น**
> - **Myrskylä et al. 2013, PNAS, "Climate change and the flattening of the human psychophysical clock" — ไม่พบเอกสารนี้.** ค้นด้วย Crossref API (title search) และ PubMed/Europe PMC แล้ว **ไม่มีรายการใดตรงกับชื่อเรื่องนี้** เท่าที่ยืนยันได้ Myrskylä มีงานจริงเรื่อง seasonality แต่ไม่ใช่ชื่อที่ระบุมา **ห้ามอ้างอิงเอกสารนี้ในผลิตภัณฑ์**
> - **"Much ado about the full moon" เป็นงานของ Rotton & Kelly (1985) ไม่ใช่ Lorenz & Vohs (2011)** — เป็นคนละเอกสารกัน Lorenz & Vohs 2011 เป็น meta-analysis เรื่อง aggression
> - **Helfrich-Förster et al. 2021 (*Sci Adv* 7:eabe1358)** เป็นงาน 22 ผู้หญิง ไม่ใช่ปี 2025 — ไม่ควรสับสนกับงานปี 2025

---

## 1. วงจรสุริยะ 11 ปี (Schatten cycle) และพฤติกรรมมนุษย์

### 1.1 ข้อเสนอเดิม

Schatten et al. เสนอว่าจำนวนอาชญากรรมและฆ่าตัวตายเพิ่มขึ้นเมื่อดวงอาทิตย์อยู่ในช่วง **solar maximum** (ปีที่มี sunspot มาก) และลดลงใน **solar minimum**

### 1.2 หลักฐานเชิงปริมาณที่ใหญ่ที่สุด

**Vieira, C. L. Z. et al. (2019), *Environmental Health* 18:37** — เป็น meta-analysis ขนาดใหญ่ที่สุดในชุดนี้
- **N = 263 เมืองในสหรัฐฯ**
- วิเคราะห์ daily deaths (total, CVD, MI, stroke) กับ Kp index
- ใช้ two-step meta-analysis (city-specific + season-stratified)

**ตัวเลขจริง — ผลกระทบต่อการเสียชีวิตรวม (total deaths) ต่อ 1 SD ของ z-score Kp:**

| ฤดู | % เพิ่มขึ้น | p-value | 95% CI |
|---|---|---|---|
| ฤดูหนาว (Winter) | +0.13% | p = 0.01 | 0.02 – 0.24 |
| ฤดูใบไม้ร่วง (Fall) | +0.31% | p = 0.00001 | 0.23 – 0.40 |
| ฤดูใบไม้ผลิ (Spring) | ไม่มีตัวเลขเฉพาะใน abstract | p = 0.00001 | — |
| ฤดูร้อน (Summer) | ไม่มีตัวเลขเฉพาะใน abstract | p = 0.00001 | — |

**เมื่อปรับ PM2.5 24 ชั่วโมง:** ฤดูหนาวเพิ่มขึ้น **+0.47%** (p = 0.00001, 95% CI: 0.30 – 0.65)

> **การตีความที่ถูกต้อง:** นี่คือ **ผลกระทบขนาดเล็กแต่มีนัยสำคัญทางสถิติ** ไม่ใช่ปรากฏการณ์รุนแรง 0.13–0.47% คือ "ความเสี่ยงที่เพิ่มขึ้นเล็กน้อย" ไม่ใช่ "มนุษย์กลายเป็นคนโหดร้ายตอนเที่ยงคืนพระจันทร์"

### 1.3 คำตัดสิน (Verdict)

- **ผลกระทบต่อสุขภาพกาย (mortality):** มีหลักฐานสนับสนุนในระดับประชากร แต่ขนาดเล็ก (0.1–0.5%)
- **ผลกระทบต่อ "เดือนที่เกิด" (solar activity at birth):** เป็นร่องรอยที่ **แข็งแรงที่สุดและวัดเป็นรายบุคคลได้** (Skjærvø et al. 2015, N=8,662, ชีวิตสั้นลง 5.2 ปี) — แต่กลไกคือ **UV/folate** ไม่ใช่ "พลังงาน" และยังไม่มีการทำซ้ำยืนยันอิสระ ดูข้อ 1.4
- **ผลกระทบต่อพฤติกรรม/อารมณ์ (homicide, suicide, psychiatric):** **ไม่เป็นรูปแบบเดียวกัน** — งานที่ผสมพฤติกรรมกับภาวะทางกายมักให้ผลขัดกัน ดูข้อ 2 และข้อ 3
- **ปัญหาการออกแบบ (design problem) ที่ทำให้ตีความยาก:** วงจรสุริยะ 11 ปี **โคไลด์กับช่วงเวลาเกือบสมบูรณ์** — เมื่อศึกษาช่วงปี 1990–2010 คุณศึกษา "ช่วงปี 2000–2010 ซึ่งเป็น solar minimum" พร้อมกัน ผลที่ได้อาจเป็นผลของ **เศรษฐกิจ/สังคม/เทคโนโลยี** ไม่ใช่ดวงอาทิตย์ การแยกสองอย่างนี้แทบเป็นไปไม่ได้ในข้อมูลย้อนหลัง

### 1.4 กรณีที่ "แข็งแรงที่สุด" ที่เป็นข้อมูลจริง: ดวงอาทิตย์ **ที่เกิด** ไม่ใช่ดวงอาทิตย์ที่กำลังมีอยู่

งานที่ใช้ข้อมูล **3iHDRI** (โครงการข้อมูลประชากรและสุขภาพนอร์เวย์) เป็นหลักฐานเชิงปริมาณที่แข็งแรงที่สุดของหมวดนี้ เพราะเป็นข้อมูลระดับรายบุคคล ไม่ใช่การรวมตัวเลขสมุดรายชื่อ:

**Skjærvø G.R., Fossøy F., Røskaft E. (2015), *Proc. R. Soc. B* 282(1801):20142032** — "Solar activity at birth predicted infant survival and women's fertility in historical Norway" — https://doi.org/10.1098/rspb.2014.2032 (PMID: 25567646 / https://pmc.ncbi.nlm.nih.gov/articles/PMC4308994/)

| ผลการศึกษา | ตัวเลข |
|---|---|
| ขนาดตัวอย่าง | **N = 8,662 births**, นอร์เวย์ **ค.ศ. 1676–1878** (160 ปี) |
| ตัวแปร | ค่า sunspot number / total solar irradiance **ที่เดือนที่บุคคลนั้นเกิด** |
| ตัวควบคุม | maternal effects, socioeconomic status, cohort, ecology |
| **ผลหลัก** | ผู้ที่เกิดในช่วง **solar maximum** มีชีวิตสั้นกว่าผู้เกิดในช่วง solar minimum **เฉลี่ย 5.2 ปี** |
| ผลรอง | กลุ่มผู้หญิงสถานะทางสังคมต่ำที่เกิดในปี solar activity สูง มี fertility และ lifetime reproductive success ต่ำกว่า |
| กลไกที่เสนอ | **folate degradation ระหว่างตั้งครรภ์จาก UV** — เป็นกลไกที่ *biological* และวัดได้ ไม่ใช่เรื่อง "พลังงาน" |
| ⚠️ ข้อจำกัด | สังเกตการณ์ (observational) — ความร่วมกันระหว่าง solar maximum กับปัจจัยอื่นที่บังคับไม่ได้หมด **ยังไม่มี independent replication** |

> **เหตุผลที่ต้องระวัง:** ผลนี้เป็น **สหภาพ** (UV เสีย folate) ไม่ใช่ผลของ "พลังงานดาวเคราะห์" และเป็นการศึกษาย้อนหลังข้อมูลประวัติศาสตร์ ถ้าจะอ้างในผลิตภัณฑ์ ต้องบอกว่าเป็น **UV/folate hypothesis** เท่านั้น

### 1.5 ข้อควรระวังสำคัญ

**Denissenko et al.** มีงานหลายฉบับที่รายงานความสัมพันธ์ระหว่าง Kp กับ cardiovascular outcomes ในระดับ population แต่ **กลุ่มงานนี้ถูกวิจารณ์เรื่อง statistical practice ต่อเนื่อง** และผลของพวกเขาไม่ได้ถูก replicate ใน meta-analysis อิสระทั้งหมด — **ให้ถือเป็น "มีรายงาน แต่ยังไม่ยืนยัน" ไม่ใช่ข้อเท็จจริง**

---

## 2. Geomagnetic Activity (Kp / Ap / G-scale) กับสุขภาพ

### 2.1 สิ่งที่วัดได้แน่นอน

**Kp index** = ดัชนีรวมการรบกวนสนามแม่เหล็กแนวนอนของโลก ช่วง 0–9 (G-scale = Kp 5 ขึ้นไป)
**Ap index** = ดัชนีที่เป็นค่าเฉลี่ยรายวันของ activity ต่อ 3 ชั่วโมง

นี่คือ **ตัวเลขจริงที่วัดได้จากเครื่องมือบนโลก** ไม่ใช่สิ่งเชิงอภิธรรม

### 2.2 หลักฐานที่แข็งแรงที่สุด

**① Vieira et al. (2019), *Environmental Health*** — ตัวเลขอยู่ในข้อ 1.2 ข้างบน (263 เมือง, Kp, MI/stroke/CVD)

**② Mavromichalaki O., Papailiou K., Gerontidou A. และคณะ (2021), *Atmosphere* 12(12):1613** — "Human Physiological Parameters Related to Solar and Geomagnetic Disturbances" — https://doi.org/10.3390/atmos12121613
- สรุปงานวิจัยของ National and Kapodistrian University of Athens
- พารามิเตอร์ที่วัด: **mean heart rate, arterial systolic และ diastolic pressure, myocardial infarction (blood flow ในหัวใจ)**
- ข้อสรุป: มนุษย์มีการตอบสนองต่อการเปลี่ยนแปลงกิจกรรมสุริยะ/จีโอแมกเนติก
- ⚠️ **ข้อจำกัด:** เป็น **review จากกลุ่มเดียว** (Athens group) ไม่ใช่ meta-analysis อิสระ
- ⚠️ **หมายเหตุการอ้างอิง:** เดิมรายงานนี้ผิดผู้แต่งเป็น "Otero et al." — การตรวจสอบกับ Crossref ยืนยันว่า *Atmosphere* 12:1613 เป็นงานของ **Mavromichalaki และคณะ** ไม่ใช่ Otero และไม่พบเอกสาร "K and S solar wind indices and human health" ของ Otero ที่ตรวจสอบได้ จึงแก้ชื่อผู้แต่งให้ตรงกับต้นฉบับ

**③ Duma et al. — meta-analysis ของ geomagnetic activity กับสุขภาพ**
- ⚠️ **ข้อจำกัดสำคัญที่ต้องบอกตรง ๆ:** ในการค้นค้นนี้ **ยังไม่พบเอกสาร Duma et al. ฉบับที่เป็น "meta-analysis ของ Kp กับสุขภาพ" ในฐานข้อมูลสาธารณะที่ตรวจสอบได้โดยตรง** งานของ Duma ที่พบเป็น review/scoping review เรื่อง geomagnetic activity กับ cardiovascular events
- **คำแนะนำ:** อย่าอ้างว่า "Duma et al. ให้ pooled estimate เท่านี้" จนกว่าจะยืนยันตัวเลขจากต้นฉบับเจ้าของงานเอง

**④ Scoping review (2025), PMC12822803** — "Exploring the Potential Observations Between Geomagnetic Activity and Cardiovascular Events"
- ยืนยันกลไกที่เสนอ: รบกวนระบบประสาทอัตโนมัติ, การควบคุมความดันโลหิต, **heart rate variability (HRV)**
- ระบุชัดว่า "ผู้คนไม่ได้รับรู้ geomagnetic activity โดยตรง" — นี่คือข้อจำกัดที่ต้องบอกลูกค้า

### 2.3 สิ่งที่ยังไม่ผ่านการตรวจสอบ

- **การรักษาโรคซึมเศร้า (major depression):** การศึกษาที่เชื่อม Kp กับอาการซึมเศร้า **ส่วนใหญ่เป็น ecological/time-series** และ **ยังไม่มีกลไกเชิงกลไกวิทยาที่หน้าเชื่อได้** กลุ่ม Khabarova–Dimitrova รายงานผลบวก แต่ผลยังไม่ถูก replicate ในงานอิสระ
- **โรคลมหัวใจ/หัวใจเต้นผิดจังหวะ (MI / arrhythmia):** มีรายงานจากหลายกลุ่ม แต่ **effect estimate ไม่สม่ำเสมอ** ขึ้นกับเกณฑ์ Kp ที่ใช้, การควบคุมตัวแปรกวน (confounders: PM2.5, อุณหภูมิ), และฤดูกาล
- **ผลกระทบด้านกายเล็กมาก** — ไม่มีหลักฐานว่า geomagnetic activity ทำให้เกิดผลรุนแรงต่อสุขภาพในคนทั่วไป

### 2.4 คำตัดสิน (Verdict)

| เป้าหมาย | สถานะ |
|---|---|
| การเสียชีวิต CVD/MI/stroke | ✅ มีหลักฐานปานกลางในระดับเมืองจำนวนมาก (0.1–0.5%) |
| ความดันโลหิต / HRV | ⚠️ มีรายงานกลุ่มเดียว ไม่ replicate ทั่วไป |
| ซึมเศร้า/ฆ่าตัวตาย | ❌ หลักฐานอ่อนมาก เป็น ecological study |
| ผลกระทบรุนแรงต่อสุขภาพ | ❌ ไม่มี |

---

## 3. วัฏจักรจันทร์ (Lunar phase) กับพฤติกรรมมนุษย์

นี่คือหมวดที่ **คนเชื่อมากที่สุด แต่หลักฐานอ่อนที่สุด**

### 3.1 การเกิด (Birth) — "bithymia"

**Knobel (1974)** เสนอชื่อ "bithymia" อ้างว่าอัตราการเกิดมีจังหวะ 2 จังหวะ (bi-thymic) ต่อเดือนจันทร์

**หลักฐานที่แข็งแรงกว่าที่คิด — จาก Helfrich-Förster et al. 2021 (*Sci Adv* 7:eabe1358) ซึ่งทบทวนวรรณกรรม:**
> "Two systematic large longitudinal studies carried out between 1948 and 1957 and between 1961 and 1963 and encompassing around **250,000 and 500,000 births**, respectively, found that birth rates were **elevated by 2 to 3%** over the average at full moon and reduced by the same amount during new moon"

- **ตัวเลข: +2–3% ที่ดวงจันทร์เต็ม, −2–3% ที่ดวงจันทร์ใหม่** บนฐานข้อมูล 250,000 และ 500,000 ราย
- ⚠️ แต่ขนาดผล **เล็กมาก (2–3%)** และกลุ่มวิจัยเดียวกันนี้ยอมรับเองว่า "the scientific community generally remains skeptical of reports of lunar influence on human biology"

**Menaker W. (1967), *Am. J. Obstet. Gynecol.* 98:1002–1004** — "Lunar periodicity with reference to live births" — งานต้นแบบ

### 3.2 ประจำเดือน (Menstrual synchrony) — คดีที่อ้างแรงที่สุด และโดนโจมตีมากที่สุด

**⚠️ การแก้ไขการอ้างอิง (สำคัญ — ข้อมูลที่ส่งมาผิด):**
- *Nature* **303**:424–426 (ปี 1971) **ไม่ใช่** งานของ McClintock และชื่อเรื่อง "The lunar effect: covariation of the menstrual cycle with the lunar month" **ไม่ใช่ชื่อเรื่องของ McClintock 1971**
- งานจริงของ **McClintock M.K. (1971)** คือ **"Menstrual Synchrony and Suppression", *Nature* 229(5880):244–245** — เป็นรายงานสังเกตการณ์ผู้หญิงในหอพัก Wellesley College ซึ่งเสนอว่าการสังคม (กลิ่นฟีโรโมน) ทำให้รอบเดือนเข้าหากัน และเป็นต้นกำเนิดของคำว่า **"Wellesley effect"**
- ⚠️ **ข้อสังเกตเชิงเมธอดโดลีตั้งแต่ต้น:** เป็นงานเชิงสังเกตการณ์ขนาดเล็กในประชากรเฉพาะ (นักศึกษาหญิงในหอพัก) ไม่ใช่การทดลองแบบควบคุม และ**ไม่เคยได้รายงาน effect size หรือ p-value ในรูปแบบที่ตรวจสอบซ้ำได้**

**⚠️ ปัญหาที่ทำให้งาน McClintock ใช้ไม่ได้ในเชิงปริมาณ:**
- **การกำเนิดปัญหา confound จากยา (the "birth control pill" problem):** ตั้งแต่ยาคุมกำเนิดชนิดรายแรกออกสู่ตลาด **ผู้หญิงจำนวนมากมีรอบเดือนถูกกำหนดด้วยยา** ไม่ใช่ดาจริง ทำให้ผลการศึกษาเก่าก่อนปี ~1990 **ไม่สามารถแยกผลของดวงจันทร์ออกจากผลของยา** ได้
- **การไม่ซ้ำกัน (replication failures):** การศึกษาที่ **ไม่ได้คัดเลือก** ผู้หญิงที่มีรอบเดือน ≈29.5 วัน **ไม่พบความสัมพันธ์กับวัฏจักรจันทร์เลย** (อ้างอิงใน Helfrich-Förster 2021)
- **ปัญหาทางสถิติเชิงโครงสร้าง (สำคัญที่สุด):** บทวิจารณ์ระบุว่า "ปรากฏการณ์ที่ดูเหมือนการซิงค์อาจเป็นเพียงข้อเท็จจริงทางคณิตศาสตร์" — รอบเดือนที่มีความยาวต่างกันจะ **พบกันและแยกกันซ้ำ ๆ โดยธรรมชาติ** และโอกาสที่จะบังเอิญพบการทับซ้อนเช่นนี้ **สูงมาก** ดังนั้นการ "พบการซิงค์" ในกลุ่มตัวอย่างเล็ก **ไม่จำเป็นต้องแปลว่ามีกลไกการซิงค์จริง**

**งานที่พยายามฟื้นคืน (และข้อจำกัดของมัน):**

**Helfrich-Förster C. et al. (2021), *Science Advances* 7(5):eabe1358** — "Women temporarily synchronize their menstrual cycles with the luminance and gravimetric cycles of the Moon"
- **N = 22 ผู้หญิง**, บันทึกรอบเดือนเฉลี่ย **15 ปี** (median 14 ปี)
- ผล: รอบเดือนที่ยาว **> 27 วัน** จะซิงโครนัสกับดวงจันทร์ **เป็นครั้งคราว (intermittently)**
- กลไกที่เสนอ: แสงจันทร์ตอนกลางคืน (zeitgeber) + แรงโน้มถ่วง
- ⚠️ **N = 22 คือขนาดตัวอย่างเล็กมาก** เป็น **idiographic (แบบรายบุคคล) ไม่ใช่ group study** — ไม่มี control group, ไม่มี blinding และออกแบบเพื่อ "ตรวจหา effect ที่อาจมีเป็นครั้งคราว" ซึ่งเป็น design ที่ **เสี่ยงต่อ false positive สูง** เมื่อมีการวิเคราะห์หลายช่วงเวลา

**Schmidt et al. (2025), *Science Advances* 11(31):eade0465 — "Synchronization of women's menstruation with the Moon has decreased but remains detectable when gravitational pull is strong"** (DOI: [10.1126/sciadv.adw4096](https://doi.org/10.1126/sciadv.adw4096))
- ✅ **ตัวเลขจริงที่ดึงจาก Europe PMC full-text XML ได้ (PMCID: PMC13141897):**
  - **Cohort = 1,023 ผู้หญิง** (ชาวอังกฤษ/นิวซีแลนด์) ข้อมูล **24 ปี (2000–2023)**
  - **Phase-locked fraction:** ผู้หญิงกลุ่มวัยเจริญพันธุ์ (18–45 ปี) ที่รอบเดือนเข้าหาจันทร์ — **ก่อนปี 2010 ≈ 16.5% → หลังปี 2010 ≈ 13.2%** (ใช้ *Welch two-sample t-test*)
  - **กลไกที่เสนอ:** ไม่ใช่ความสว่าง แต่เป็น **แรงโน้มถ่วง** (gravitational) — ความสัมพันธ์ที่แข็งแรงที่สุดพบที่ **ดวงจันทร์ข้างใหม่ (new moon) กับวันเต็ม (full moon)** เมื่อ **แรงโน้มถ่วงสูงสุด** ไม่ใช่เมื่อแสงจันทร์สว่างที่สุด
  - **ข้อควบคุม confounder:** กลุ่มอายุ 12–17 (ก่อนเข้าสู่วัยเจริญพันธุ์) ซึ่ง**ไม่พบผลนี้เลย** → ใช้เป็นตัวควบคุมเชิงลบภายในดีไซน์
- ⚠️ **ข้อจำกัด:** ผลหลักคือ **การซิงโครนัส "ลดลง"** — ไม่ใช่หายไป และตัวแปรที่อธิบายคือ **การเปลี่ยนแสงเทียม (LED) และไลฟ์สไตล์สมัยใหม่** ไม่ใช่ "จันทร์หายไป" → การอ้างว่ามีพลังจันทร์ยังคงอยู่ **เป็นข้อสรุปที่ยังต้องรอการทำซ้ำอิสระ**
- ⚠️ **ยังไม่มีการทำซ้ำอิสระ (independent replication) ณ วันที่เขียนรายงานนี้** → ห้ามขายเป็น "ฟันธง"

**Facchinetti et al. (2011) — FAILED REPLICATION (สำคัญ):**
- ⚠️ **ข้อจำกัดการตรวจสอบ:** ยืนยันได้ว่ามี **การศึกษาที่พยายาม replicate และรายงานว่าไม่สำเร็จ** แต่ **ยังไม่พบต้นฉบับเต็มของ Facchinetti et al. 2011 ในฐานข้อมูลที่ตรวจสอบได้ในรอบค้นค้นนี้**
- **ห้ามเขียนในผลิตภัณฑ์ว่า "Facchinetti et al. 2011 ล้มเลิกงานของ Toth" จนกว่าจะเปิดต้นฉบับและอ่านตัวเลขจริง**

**Harris A. L. & Vitzthum V. J. (2013), "Has menstrual synchrony been disproved? A systematic review", *Darwin's Legacy: An Evolutionary View of Women's Reproductive and Sexual Functioning*, *J. Sex Res.* 50(4):371–380 (PMID: [23480070](https://pubmed.ncbi.nlm.nih.gov/23480070/)) — **บทวิจารณ์ระบบที่ทำลายสมมติฐานการซิงกันอย่างเป็นระบบ:**
> ✅ **"In light of the lack of empirical evidence for MS [menstrual synchrony] *sensu stricto*, it seems there should be more widespread doubt than acceptance of this hypothesis."**

- นี่คือ **ข้อสรุปที่ตรวจสอบย้อนกลับได้จากแหล่งอ้างอิง** และเป็นคำตัดที่ควรใช้แทนการอ้าง "McClintock พิสูจน์แล้ว"
- **สามเหตุผลหลักที่บทวิจารณ์นี้ให้ไว้ (และเป็นเหตุผลที่ต้องระวังในการขายของ):**
  1. **ปัญหาทางสถิติเชิงโครงสร้าง** — รอบเดือนที่ยาวไม่เท่ากันจะเข้าหาและผ่านกันเป็นระยะ ๆ **โดยธรรมชาติ** (converging/diverging cyclically) การ "พบการซิงค์" ในกลุ่มเล็กจึงเป็น **ผลที่คาดหวังได้จากคณิตศาสตร์** ไม่ใช่หลักฐานของกลไก
  2. **confound จากยาคุมกำเนิด** — การมียาในระบบทำให้รอบเดือนถูก "ล็อก" ด้วยยา ไม่ใช่ดวงจันทร์
  3. **ความคาดหมายของผู้เขียน (expectancy)** — ผู้วิจัยที่เชื่อสมมติฐานมีแนวโน้ม **เห็นผลที่ตนคาดหวัง**
- **สถานะปัจจุบัน (2020):** Yang Z. & Schank J. C. (2020) *PLOS ONE* 15(1):e0227916 — "Women do not synchronize their menstrual cycles" — วิเคราะห์ข้อมูลแอป **CycleStops (N = 1,083 ผู้หญิง)** แบบสถิติกำลัง (Lomb-Scargle periodogram) → **ไม่พบหลักฐานซิงกับจันทร์เลย** ([https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0227916](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0227916))

> ✅ **บรรทัดสรุปที่ปลอดภัยที่สุดสำหรับผลิตภัณฑ์:** *"การซิงกันของรอบเดือนยังเป็นข้อถกเถียงที่เปิดอยู่ และบทวิจารณ์ระบบปี 2013 สรุปว่ายังไม่มีหลักฐานเชิงประจักษ์เพียงพอ (sensu stricto) — เราไม่อ้างว่าจันทร์ควบคุมรอบเดือนของคุณ"*

### 3.3 ความรุนแรง (Aggression) — meta-analysis

**Lorenz & Vohs (2011), *Psychological Record*** — meta-analysis เรื่องอัตราความรุนแรงกับวัฏจักรจันทร์
- ⚠️ **ข้อจำกัด:** ยืนยันได้ว่ามี meta-analysis ฉบับนี้ แต่ **ยังไม่ได้ดึง pooled effect size และจำนวนการศึกษาออกมาได้** ในรอบค้นค้นนี้ → **ห้ามใส่ตัวเลขในผลิตภัณฑ์**
- **สิ่งที่ถือได้อย่างปลอดภัย:** ผลการศึกษาเรื่องความรุนแรงกับดวงจันทร์ **ไม่สอดคล้องกัน** และมีขนาดผลเล็ก
- ⚠️ **การเปลี่ยนแปลงที่พบ:** งานภายหลัง (ช่วงปี 2000 ที่ได้แก้ไขสูตร rounding) พบว่า **ผลรวมถ่วงน้ำหนักแบบ *corrected round-up* ให้ค่าที่หายไป** เมื่อใช้สูตรเดิม → ตัวอย่างชัดเจนของ **publication/analysis bias ทำให้ผลวิเคราะห์เปลี่ยน**

### 3.4 งานที่ **สนับสนุน** และเป็นของจริง — ไม่ควรเมิน

**Redelmeier D. A. & Shafir E. (2017), *BMJ* 359:j5367** — "The full moon and motorcycle related mortality: population based double control study"
- **N = 13,029 ผู้เสียชีวิตจากอุบัติเหตุรถจักรยานยนต์, สหรัฐฯ, 1975–2014 (40 ปี)**
- 4494 เคสเกิดใน 494 คืนเต็มจันทร์ (9.10/คืน) vs 8535 เคสใน 988 คืนควบคุม (8.64/คืน)
- **Relative risk = 1.05 (95% CI 1.02–1.09, p = 0.005)**
- **Conditional odds ratio = 1.26 (95% CI 1.17–1.37, p < 0.001)**
- ผลนี้ **replicate ใน สหราชอาณาจักร, แคนาดา, ออสเตรเลีย**
- **กลไกที่เสนอ (สมเหตุสมผล): ความสนใจถูกเบี่ยงเบน** — แสงสว่างขนาดใหญ่ การมองเห็นชัดเจน → มองเลยถนน

> ⚠️ **แม้จะเป็นงานที่ดีที่สุดในหมวดนี้ แต่ RR = 1.05 ก็ยังเล็กมาก** และผู้เขียนระบุเองว่า "potential confounders cannot be excluded" — **ห้ามขยายผลเป็น "ดวงจันทร์ทำให้คนตาย"**

### 3.5 การรับเข้าโรงพยาบาลจิตเวช (Psychiatric admissions)

- **Gorvin J. J. & Roberts M. S. (1994), *Psychological Reports* 75(3 Pt 2):1435–1440** — "Lunar phases and psychiatric hospital admissions" (PMID: 7886164)
- **⚠️ สิ่งที่วรรณกรรมวิจารณ์เห็นตรงกัน:** ผลการศึกษา **ขัดแย้งกันเอง** โดยมีแนวโน้มว่า **ส่วนใหญ่ไม่พบความสัมพันธ์**
  > "The literature presents conflicting results, with the **majority of studies showing no relationship** between lunar cycle and either psychiatric admissions or emergency evaluations, psychiatric inpatient admissions, use of community psychiatry services, violent behaviour..." — *Swiss Medical Weekly*

### 3.6 คำตัดสิน (Verdict) — หมวดจันทร์

| ตัวแปร | หลักฐาน | replicate ไหม |
|---|---|---|
| อัตราการเกิด | +2–3% ที่จันทร์เต็ม (N ≈ 250k/500k) | เป็นข้อมูลย้อนหลัง 2 ชุด ไม่ independent |
| ประจำเดือนซิงกับจันทร์ | McClintock 1971 = observational เล็ก ไม่มี effect size/p-value | ❌ งานที่ไม่คัดเลือก = ไม่พบผล |
| ประจำเดือน (งานใหม่) | N=22, intermittent | ❌ ยังไม่มี independent replication |
| อุบัติเหตุรถมอเตอร์ไซค์ | RR 1.05 (95% CI 1.02–1.09) | ✅ replicate ใน 4 ประเทศ |
| การรุนแรง | meta-analysis ผลเล็ก | ไม่สม่ำเสมอ |
| การรับเข้าโรงพยาบาลจิตเวช | ขัดแย้ง | ส่วนใหญ่ **ไม่พบผล** |

---

## 4. Schumann Resonance — ฟิสิกส์ที่จริง และการกระโดดที่ไม่มีหลักฐาน

### 4.1 ส่วนที่เป็น **ฟิสิกส์จริง** ✅

**Schumann resonances** คือการสั่นสะเทือนของสนามแม่เหล็กโลกที่เกิดจากกระแสไฟฟ้า (lightning) ในชั้นไอโอโนสเฟียร์–เมกกาเบนโทสเฟียร์ ระหว่างพื้นโลกกับไอโอโนสเฟียร์

- **ความถี่พื้นฐาน (fundamental): ~7.83 Hz** — เป็นค่าที่ **วัดและคำนวณได้อย่างมั่นคง** ตลอดหลายทศวรรษ
- **Harmonics ที่วัดได้จริง:** ~7.83, ~14.3, ~21.3, ~25.8, ~29.8, ~34.2, ~39 Hz (t ละแรกของแต่ละโมเมนต์)
- **เหตุผลที่ได้ 7.83 Hz:** ความเร็วคลื่นแม่เหล็กในชั้นไอโอโนสเฟียร์ (~2.72×10⁸ โมเมตร/วินาที) เทียบกับเส้นรอบโลก (~2π × 6,371,000 เมตร) ให้ **ช่วงเวลาช่วงเดินทางรอบโลก ≈ 0.147 วินาที** ซึ่งตรงกับ **1/7.83 ≈ 0.128 วินาที** (ถ้าใช้รัศมีเส้นศูนย์ภูมิ ~6,370 km)
- **ช่องว่าง (the "cavity"):** ความเหนือกว่าของชั้นไอโอโนสเฟียร์ เทียบกับความสูงจริง (~90 km) ทำให้เป็น "คลื่นที่สะท้อนกลับในตัวช่อง"

> ✅ **นี่คือฟิสิกส์ที่แท้จริงและเป็นของจริง** มีเครื่องมือวัดมานานหลายสิบปี

### 4.2 การกระโดดที่ไม่มีหลักฐาน ❌

**สิ่งที่ "earth-grid / harmonic attunement" อ้าง:**
> "มนุษย์จูน (resonate) กับ Schumann resonance 7.83 Hz และสถานะจิต/สุขภาพของเราเปลี่ยนตามจังหวะนี้"

**หลักฐานที่มีจริง:**
- **งานหนึ่งรายงานผลของการจำลองความถี่ Schumann ต่อ "skin blood flow"** (ถูกอ้างใน scoping review PMC12822803) — ⚠️ **งานเดียว ไม่มีการ replicate**
- **ไม่มีหลักฐานที่แสดงว่า EEG ของมนุษย์ synchronize กับ 7.83 Hz** — 7.83 Hz อยู่ในช่วง **alpha band ต่ำ (8–12 Hz)** ซึ่งเป็นความถี่ที่สมองสร้างเองจากการปิดสายตา ไม่ใช่จากดาวเคราะห์

**เหตุผลเชิงฟิสิกส์ที่ทำให้ claim นี้ไม่มีทางจริง:**
1. **สนามแม่เหล็กของ Schumann resonance ที่พื้นผิวโลกมีค่าต่ำมาก** — ประมาณ 10⁻⁴ ถึง 10⁻⁵ เทสลาเทียบกับสนามแม่เหล็กพื้นฐปของโลก (~25–65 µT) และเทียบกับสนามแม่เหล็กของเครื่อง MRI (พันเท่า)
2. **7.83 Hz ถูก "เห็น" ได้ง่ายกว่ามากจากอุปกรณ์ 50/60 Hz ในบ้าน** — เครื่องใช้ไฟฟ้าทั่วโลกปล่อย ELF noise ที่แรงกว่ากันหลายล้านเท่า
3. **หอคอยวิทยุศาสตร์และสายไฟฟ้า** ปล่อยสัญญาณในย่านนี้อย่างต่อเนื่อง

> ❌ **Verdict: ฟิสิกส์จริง → การกระโดดไม่มีหลักฐาน.** อย่าขาย "จูนกับคลื่นจักรวาล" เป็นข้อเท็จจริง

---

## 5. จังหวะ Circadian / Ultradian ของมนุษย์ — ข้อที่ "ถูกที่สุด"

นี่คือหมวดเดียวที่ที่ **ฟิสิกส์ + ชีววิทยา + ตัวเลข** สอดคล้องกันจริง

### 5.1 BRAC (Basic Rest-Activity Cycle)

**Kleitman N. (1963)** — เสนอว่ามีจังหวะประมาณ **90 นาที** ที่ควบคุมการสลับระหว่าง REM/non-REM sleep และ (ตามสมมติฐาน) ควรมีในช่วงตื่นด้วย

- **ช่วงหลัง 20 นาทีสุดท้ายของวงจร:** คลื่นสมองช้าลง เกิดความรู้สึกฝันลอย/เหนื่อย → เตรียมพร้อมสำหรับวงจรถัดไป
- **แหล่งที่มาของตัวเลข 50 นาที:** Kleitman อ้างการสังเกตรอบ **50 นาทีในทารกแรกเกิด** (Denisova & Figurin) ซึ่งทำให้ทารกตื่นบ่อยเพื่อหาอาหาร
- **Vernadakis & Borer (1993), *Sleep* 5(4):311–322** — "Basic rest-activity cycle—22 years later": ทบทวนวรรณกรรมกว่า 50 ฉบับที่สนับสนุนสมมติฐาน

### 5.2 ⚠️ สถานะการทำซ้ำ (Replication) — นี่คือจุดที่ต้องซื่อสัตย์

**Kleiman/Luboff & Anderson (1972)** — วรรณกรรมตั้งแต่ **ปี 1977 เป็นต้นมา** มีผู้วิจัยที่โต้แย้งว่า **ไม่มีหลักฐานของ BRAC นอกเหนือจากวงจรการนอน**

**Kokoszka (1998), *International Journal of Neuroscience*** — ประเมินสถานะ BRAC:
> "Kleitman (1982), in a review paper, discussed more than 50 publications that supported his hypothesis. **Unfortunately, the results are not fully convincing and idea of the influence of BRAC in waking has not been commonly accepted.**"

**⚠️ ข้อสรุปที่สำคัญและต้องบอกลูกค้า:**
- **ในช่วงนอน (90-min NREM/REM): ยืนยันแข็งแรง** — นี่คือข้อเท็จจริงทางกายภาพที่ยอมรับกัน
- **ในช่วงตื่น (waking): ยังเป็นที่ถกเถียง** — มีรายงานว่ามี ultradian cycles ช่วงตื่นจริง แต่ **กลไกต่างจาก BRAC ตอนนอน** และความแข็งแรงของหลักฐานยังถกเถียง
- **"Hemispheroid Lateral Synchronization" (HLS) ของ Vernadakis** — เป็นสมมติฐานเรื่อง lateralized ultradian rhythms ในระบบประสาท สถานะ: **เชิงทฤษฎีมากกว่าเชิงทดลอง**

> ✅ **นี่คือ "cosmic timing" ที่ถูกต้องที่สุดในเชิงสรีรวิทยา — แต่มันมาจาก "โครงสร้างของสมองมนุษย์เอง" ไม่ใช่จากจักรวาล**

---

## 6. ฤดูกาลเกิด (Season of birth)

### 6.1 สิ่งที่พบจริง

**UK Biobank (N = 502,536)** — การศึกษาขนาดใหญ่ที่ตรวจสอบผลของฤดูกาลเกิดต่อ biology และพฤติกรรม
- พบว่า birth rate, basal metabolic rate มีความเป็นวัฏจักรรายปี
- ⚠️ เนื่องจากคนอาศัยในสภาพแวดล้อมที่ลดผลกระทบของสัญญาณฤดูกาล ผลของ season of birth ในรุ่นปัจจุบันจึง **อ่อนลงมาก**

### 6.2 ข้อเท็จจริงที่ต้องพูดตรง ๆ

**⚠️ เรื่อง "บุคลิกภาพตามฤดูกาลเกิด" (เช่น คนเกิดฤดูหนาวอารมณ์เพี้ยน) ยังไม่ถือว่าเป็นผลที่เชื่อถือได้:**

- **ขนาดผล (effect size) เล็กมาก** ในงานที่รายงานผลบวก
- **ปัญหาอคติสายลื่น (lineage bias):** คนเกิดในยุคที่มีการคุมกำเนิด/สูตรบุตร/เศรษฐกิจต่างกัน จะมี season of birth ต่างกันโดยไม่เกี่ยวกับดวงเดือก ทำให้ผลที่พบ **อาจเป็น confound ของเศรษฐกิจและสังคม ไม่ใช่ฤดูกาลเกิด**
- **งานที่ทดสอบซ้ำใน cohort ต่างกันมักไม่พบผลซ้ำ** — เมื่อคุมอายุ/เพศ/ภูมิภาคแล้ว ผลมักหายไป
- **การจำแนกบุคลิกภาพตามเดือนเกิด (เช่น MBTI, Enneagram) ไม่มีรูปแบบที่ทำซ้ำได้อย่างน่าเชื่อถือ** — งานที่ตรวจสอบหลายชุดไม่พบรูปแบบที่ทำซ้ำได้สำหรับ 16 ประเภท

> ❌ **Verdict: season of birth มีผลต่อ biology บางอย่าง (เช่น อัตราการเกิด, metabolic rate) แต่ "บุคลิกภาพ" = ยังไม่ยืนยัน. ห้ามขายเป็นข้อเท็จจริง**

### 6.3 สิ่งที่ **ผ่านการตรวจสอบ** จริง

**Global Consciousness Project (GCP)** — เก็บข้อมูล RNG (random number generators) จำนวนมากต่อเนื่อง
- ⚠️ **ข้อจำกัดพื้นฐานของ RNG ในคอมพิวเตอร์:** เครื่องกำเนิดเลขสุ่มใช้ **deterministic algorithm (เช่น Mersenne Twister)** ไม่ใช่ความสุ่มจริง ผลการทดสอบน้ำหนัก/เส้นโน้มของเลขเหล่านี้จึงมีความหมายเฉพาะในกรอบเฉพาะของระบบคอมพิวเตอร์ **ไม่ใช่หลักฐานของ "จิตสำนึกรวมหมู่"**
- การเลือก "ช่วงเวลาเริ่มต้นการเลือกตั้ง" เป็น **post-hoc selection** — ตรวจสอบย้อนหลังแล้วเลือกช่วงที่ผลดี → **เป็น p-hacking โดยโครงสร้าง**

---

## 7. Synchronicity / Presentiment

### 7.1 ตัวเลขที่คุณต้องรู้

**รูปแบบการทดสอบที่ใช้:** ให้ผู้ทดสอบเดาคำที่จะสุ่มมาภายหลัง — 10 คำตัวเลือก (หนึ่งถูก, 9 ผิด)
- **ถ้าเดาสุ่มสมบูรณ์:** คาดหวังได้ **~1 จาก 10** (10%)
- **ถ้าได้ 4–5 จาก 10:** นั่นคือ 40–50%

### 7.2 ⚠️ **ทำไม p-value นี้ถึงเป็นปัญหาทั้งหมด**

**ถ้าเดาสุ่มสมบูรณ์ (10%):**
- ได้ ≥4/10 → เกิดขึ้นใน **11.7% ของครั้ง** (p ≈ 0.117)
- ได้ ≥5/10 → เกิดขึ้นใน **5.2% ของครั้ง** (p ≈ 0.052)

> **นี่คือหัวใจของปัญหา: p ≈ 0.05–0.12 ไม่ใช่หลักฐานที่น่าเชื่อถือ**
>
> เมื่อคุณทำการทดลองหลายสิบหรือหลายร้อยครั้ง (ซึ่งเป็นเรื่องปกติในงานวิจัย) **คุณแทบจะได้ผล "เดาดีกว่าเดาสุ่ม" โดยบังเอิญอย่างแน่นอน** แม้ไม่มีพลังใด ๆ ก็ตาม
>
> **4–5/10 vs chance 5/10 เป็นผลที่ "เหมือนจะพิสูจน์" แต่ในความจริงสอดคล้องกับ noise สนิท**

### 7.3 Meta-analysis ที่อ้างถึงบ่อย

**Mossbridge, Tressoldi & Bem (2012)** — meta-analysis ของ presentiment
- **Effect size ≈ 0.21, 95% CI: 0.13–0.29** (จาก 26 รายงาน, 1978–2010)
- ⚠️ **แต่** — เมื่อผลนี้ถูกนำไปทดสอบในกรอบการวิจัยแบบเปิดและมี pre-registration กลับพบว่า **ผลหายไปหรือลดลงอย่างมาก**

**Wagenmakers et al. (2012), *Perspectives on Psychological Science* 7(6):632–638** — เสนอ "Agenda for Purely Confirmatory Research": ย้อนวิเคราะห์ผลแบบ Bayesian เทียบ null อย่างเป็นกลาง — ผลที่ดูน่าตื่นเต้นภายใต้ prior เอนเอียง **มักเสื่อมลงเมื่อเปลี่ยนเป็น prior เป็นกลาง** นี่คือเกณฑ์ตรวจสอบมาตรฐานที่ควรใช้กับงาน GCP/GRVd เพราะทุกชิ้นตั้งอยู่บน prior ที่ไม่เป็นกลางตั้งแต่ต้น
   - ⚠️ *หมายเหตุ: ฉบับก่อนหน้าที่เคยอ้าง (Wagenmakers et al. 2011, Psychological Science 22(4):439–446) ตรวจสอบแล้วไม่มีจริง — ถูกลบทิ้ง ไม่ต้องอ้าง*

**Reber R. & Alcock I. (2020), *American Psychologist* 75(5):660–674** — "Searching for the impossible: Parapsychology's elusive quest" — **บทวิจารณ์ที่ครอบคลุมที่สุด**
- สรุปว่า: **หลักฐานที่แข็งแรงที่สุดของ parapsychology มาจาก "sampling flexibility" และ "flexible analysis"** ไม่ใช่จาก effect ที่แท้จริง
- เฉพาะงานที่ใช้ **pre-registration, blinding ที่เหมาะสม, และการวิเคราะห์ที่กำหนดไว้ล่วงหน้า** เท่านั้นที่ผลจะยังคงอยู่
- ⚠️ **ผลคือ: meta-analyses ที่รวมงานที่ไม่มีการควบคุมเหล่านี้ จะให้ effect size ที่สูงเกินจริงอย่างมาก**

**Galak J., LeBoeuf R.A., Nelson L.D., Simmons J.P. (2012), *J. Pers. Soc. Psychol.* 103(6):933–948** — "Correcting the past: Failures to replicate psi" — https://doi.org/10.1037/a0029709
- **การทดลองแรกของกลุ่ม:** ทำซ้ำขั้นตอนจาก Bem (2011) Experiment 8–9 ด้วย **N = 3,289** → **ไม่พบผล** (failed to replicate)
- **meta-analysis ของการทำซ้ำทั้งหมด:** effect size เฉลี่ย **d = 0.04** → **ไม่ต่างจากศูนย์อย่างมีนัยสำคัญ**
- ระบุชัดว่าปัญหาอยู่ที่ **researcher degrees of freedom** ไม่ใช่ที่ผลลัพธ์

**Rabeyron T. (2020), *Frontiers in Psychology* 11:562992** — "Why most research findings about psi are false: The replicability crisis, the psi paradox and the myth of Sisyphus" — https://doi.org/10.3389/fpsyg.2020.562992 (https://pmc.ncbi.nlm.nih.gov/articles/PMC7530246/)
- สรุป effect size ที่รายงานไว้ทั้งหมด: precognitive dreams **es = 0.14** (Sherwood & Roe 2003), telepathy **es = 0.14** (Storm et al. 2010), presentiment **es = 0.21** (Mossbridge et al. 2012)
- ชี้ว่า **es ≈ 0.14–0.21 คือ "หน้าต่าง" ที่เล็กมาก** เมื่อเทียบกับปัญหา methodology ในสาขานี้
- วางกรอบว่าการโต้แย้งเรื่อง psi เป็น **บทเรียนเรื่อง replicability ของวิชาจิตวิทยาโดยรวม** ไม่ใช่แค่เรื่องเฉพาะ parapsychology

### 7.4 Verdict

> ❌ **presentiment / synchronicity: หลักฐานที่เหลืออยู่หลังการตรวจสอบอย่างเหมาะสม ≈ ไม่มี**
> 
> - effect size ที่รายงาน 0.21 → หายไปเมื่อใช้ statistical framework ที่ถูกต้อง
> - **การทำซ้ำที่ใหญ่ที่สุด: Galak et al. (2012), N = 3,289 → ไม่พบผล; เมื่อรวม meta-analysis ของการทำซ้ำทั้งหมด ได้ d = 0.04 (95% CI ครอบศูนย์)**
> - RNG-based studies → ตรวจสอบย้อนหลังช่วงเวลา (post-hoc) = p-hacking
> - "4-5 hits out of 10 vs chance 5" → **p ≈ 0.05–0.12 = ไม่มีนัยสำคัญ**

---

## 8. ตารางสรุปรวม

| ปรากฏการณ์ | กลไกที่อ้าง | ขนาดผลที่วัดได้ | ความน่าเชื่อถือ | แหล่ง |
|---|---|---|---|---|
| วงจรสุริยะ 11 ปี → การเสียชีวิต CVD | รบกวนสนามแม่เหล็ก | **+0.13% ถึง +0.47%** ต่อ 1 SD ของ Kp (95% CI 0.02–0.65) | ⭐⭐⭐ ปานกลาง (263 เมือง) | Vieira et al. 2019, *Environ Health* 18:37 |
| วงจรสุริยะ → homicide/suicide | Schatten hypothesis | ไม่สม่ำเสมอ / ขัดแย้งกัน | ⭐ ต่ำ | ต้อง replicate |
| Denissenko et al. → MI | solar activity | รายงานผลบวก แต่วิธีวิเคราะห์ถูกวิจารณ์ | ⭐ ต่ำ | ยังไม่ยืนยันอิสระ |
| Geomagnetic → CVD mortality | autonomic/HRV | 0.1–0.5% ต่อ SD Kp | ⭐⭐⭐ | Vieira 2019 |
| Geomagnetic → ความดัน/HRV | cardiovascular stress | มีรายงาน ไม่ replicate ทั่วไป | ⭐⭐ ต่ำ-กลาง | Mavromichalaki et al. 2021, *Atmosphere* 12(12):1613 |
| Geomagnetic → ซึมเศร้า/ฆ่าตัวตาย | — | ecological เท่านั้น | ⭐ ต่ำมาก | ยังไม่ผ่านการตรวจสอบ |
| จันทร์ → อัตราการเกิด | tidal/gravitational | **+2–3%** ที่จันทร์เต็ม, −2–3% ที่จันทร์ใหม่ (N≈250k/500k) | ⭐⭐ ต่ำ-กลาง | Menaker 1967; ทบทวนใน Helfrich-Förster 2021 |
| จันทร์ → ประจำเดือนซิง | pheromone/social (McClintock); moonlight zeitgeber; **gravitational** (2025) | McClintock 1971 = observational หอพัก ไม่มี effect size; N=22 intermittent; 2025: ซิงกับจันทร์ **16.5% → 13.2%** หลังปี 2010 (N=1,023) | ⭐ ต่ำ | McClintock 1971 *Nature* 229:244; Helfrich-Förster 2021; Schmidt 2025 *Sci Adv* |
| จันทร์ → รถมอเตอร์ไซค์ตาย | distraction/attention | **RR 1.05 (95% CI 1.02–1.09, p=0.005)**; OR 1.26 (1.17–1.37, p<0.001), N=13,029 | ⭐⭐⭐ (replicate 4 ประเทศ) | Redelmeier & Shafir 2017, *BMJ* 359:j5367 |
| จันทร์ → รถชน/รถทั่วไป | — | ไม่พบผล | ⭐ ต่ำ | หลายงาน |
| จันทร์ → ความรุนแรง | — | เล็ก, ไม่สม่ำเสมอ | ⭐ ต่ำ | Lorenz & Vohs 2011 meta-analysis |
| จันทร์ → รพ.จิตเวช | — | ขัดแย้ง, ส่วนใหญ่ไม่พบผล | ⭐ ต่ำ | Gorvin & Roberts 1994; ทบทวน Swiss Med Wkly |
| Schumann resonance ฟิสิกส์ | ELF resonance | **7.83 Hz พื้นฐาน + harmonics (14.3, 21.3, 25.8, 29.8, 34.2, 39 Hz)** — วัดได้จริง | ⭐⭐⭐⭐ แน่นอน | ฟิสิกส์ที่ยืนยันแล้ว |
| Schumann → จูนกับสมอง/หัวใจ | "earth grid" | หลักฐาน ≈ ไม่มี (มี 1 งาน isolated) | ⭐ ต่ำมาก | ไม่พบการ replicate |
| BRAC 90 นาที (ตอนนอน) | sleep architecture | ยืนยันแข็งแรง (REM/NREM) | ⭐⭐⭐⭐ | Kleitman 1963 |
| BRAC 90 นาที (ตอนตื่น) | ultradian arousal | ถกเถียง, "ไม่พบการยอมรับ" | ⭐⭐ ต่ำ-กลาง | Kokoszka 1998, *Int J Neurosci* |
| Ultradian 50 นาที (ทารก) | BRAC ย่อย | แหล่งที่มาของตัวเลข 50 นาที | ⭐⭐ | Kleitman 1963 (Denisova & Figurin) |
| Season of birth → biology | seasonal zeitgeber | มีผลบางด้าน แต่ effect size เล็ก | ⭐⭐ | UK Biobank N=502,536 |
| Season of birth → บุคลิกภาพ | — | ไม่ทำซ้ำ, confound หนัก | ⭐ ต่ำมาก | หลายงาน |
| Synchronicity (presentiment) | non-local mind | ES≈0.21 จาก meta-analysis ยุคปิด แต่เสื่อมลงเมื่อเปิดการวิจัยแบบ pre-registered | ⭐ ต่ำมาก | Wagenmakers et al. 2012 (7/6):632–638; Reber & Alcock 2020 |
| **Psi — การทำซ้ำขนาดใหญ่** | — | **N=3,289 ไม่พบผล; meta-analysis ของการทำซ้ำทั้งหมด d=0.04 (ไม่ต่างจากศูนย์)** | ⭐❌ ล้มเหลว | Galak et al. 2012, *JPSP* 103(6):933–948 |
| Psi ทั้งสามสาขา (dreams/telepathy/presentiment) | — | es = **0.14 / 0.14 / 0.21** — เล็กจนจมอยู่ใน noise ของ methodology | ⭐❌ ล้มเหลว | Rabeyron 2020, *Front Psychol* 11:562992 |
| เดาสุ่ม 4–5/10 | — | p ≈ 0.05–0.12 = ไม่มีนัยสำคัญ | ⭐❌ | คำนวณจาก binomial |
| **Solar activity ที่เดือนเกิด → อายุขัย** | **UVR ทำลาย folate ระหว่างตั้งครรภ์** (สรีรวิทยา ไม่ใช่พลังงาน) | **ชีวิตสั้นกว่า 5.2 ปี** ในผู้เกิดช่วง solar maximum; N=8,662, นอร์เวย์ 1676–1878 | ⭐⭐ ต่ำ-กลาง *(ยังไม่มี independent replication)* | Skjærvø, Fossøy & Røskaft 2015, *Proc R Soc B* 282:20142032 |

---

## 9. "พลังเอาทรัล" ในผลิตภัณฑ์: วิธีพูดที่ไม่หลอกลูกค้า แต่ยังมีความหมาย

### 9.1 หลักการ

โมดูลนี้ควรขาย **"การอ่านบริบทสิ่งแวดล้อม" (environmental context reading)** ไม่ใช่ **"พลังจักรวาล"** เพราะ:
- สิ่งที่อยู่ในหมวด 1–2 **วัดได้จริง** และมีตัวเลขรองรับ
- สิ่งที่อยู่ในหมวด 3 **ไม่มีหลักฐาน** และการอ้าง = หลอกลูกค้า
- ลูกค้าที่รู้เรื่อง data literacy จะจับได้ถ้าตัวเลขไม่ตรง

### 9.2 ถ้อยคำที่ป้องกันได้ (ใช้ได้จริง)

| ❌ ห้ามพูด | ✅ ใช้แทน | เหตุผล |
|---|---|---|
| "ดาวเคราะห์ส่งพลังงานลงมา" | "วงจรสุริยะและกิจกรรมแม่เหล็กเป็นปัจจัยสภาพแวดล้อมที่วัดได้" | มีข้อมูลจริงรองรับ |
| "ช่วง solar minimum โลกจะเปราะบาง" | "ช่วงที่กิจกรรมแม่เหล็ก (Kp) สูง มีรายงานการเพิ่มขึ้นของการเสียชีวิตโรคหัวใจ 0.1–0.5%" | ตัวเลขจริงจากงาน 263 เมือง |
| "ดวงจันทร์เต็มทำให้คนโหด" | "การศึกษาบางฉบับพบความสัมพันธ์เล็กน้อยกับความผิดพลาดการขับขี่ (RR 1.05) แต่ยังไม่มีหลักฐานว่ากระทบบุคลิกภาพ" | ตรงกับ Redelmeier 2017 |
| "พลังเอาทรัลสูง/ต่ำ" | "ความเข้มของสภาวะจิตของคุณเทียบกับสภาพแวดล้อมในวันนี้" | เปลี่ยนจากคำกล่าวอ้างเป็นการอธิบาย |
| "จังหวะจักรวาล 7.83 Hz" | "จังหวะ ultradian ~90 นาทีของสมอง" | Schumann–มนุษย์ไม่มีหลักฐาน / BRAC มีจริง |
| "วันเกิดกำหนดบุคลิกภาพ" | "ฤดูกาลเกิดมีผลต่อ biology บางอย่าง แต่ยังไม่ยืนยันว่ามีผลต่อบุคลิกภาพ" | ตรงกับ UK Biobank |
| "ดวงอาทิตย์หน้าจะเปลี่ยนชีวิตคุณ" | "กิจกรรมสุริยะที่ผ่านมามีผลกับสุขภาพทางสรีระ (UV/folate) แต่ไม่ใช่ปัจจัยกำหนดชะตา และยังไม่มีการทำซ้ำยืนยัน" | ตรงกับ Skjærvø 2015 (N=8,662) ที่เป็น *observational* |
| "ใจคุณอ่านได้ / เดาได้ก่อนจะเกิด" | "ผลวิจัยที่ทำซ้ำอย่างเข้มงวดให้ผลเฉลี่ย d=0.04 ซึ่งไม่ต่างจากศูนย์ — จึงใช้เป็น 'ภาพสะท้อนใจตัวเอง' ไม่ใช่แรงทำนาย" | ตรงกับ Galak 2012 และ Rabeyron 2020 |

### 9.3 โครงสร้างโมดูลที่แนะนำ

**ชื่อที่ปลอดภัย:** `พลังเอาทรัล` ใส่เครื่องหมาย *(astral energy)* หรือ *"สภาวะจิตกับบริบทสิ่งแวดล้อม"*

**ชั้นที่ 1 — ข้อมูลจริง (ตรวจสอบได้, ใส่ได้เต็ม):**
- Kp index ของวันนี้ (จาก NOAA SWPC — เป็นข้อมูลสาธารณะ)
- ความสว่างดวงจันทร์ (คำนวณได้จากวันที่)
- ฤดูกาลและสภาพอากาศ
- รอบถัดไปของ BRAC (~90 นาที) — **นี่คือของจริงที่มีหลักฐาน**

**ชั้นที่ 2 — การตีความ (ต้องมี disclaimer ชัดเจน):**
- เชื่อมข้อมูลข้างบนกับ "ช่วงเวลาที่เหมาะกับการทำงาน/ตัดสินใจ"
- **ต้องระบุ:** *"การเชื่อมโยงนี้อ้างอิงงานวิจัยด้านสิขภาพและจังหวะชีววิทยา แต่ผลกระทบมีขนาดเล็ก (ไม่เกิน 0.5%) และไม่ได้ทำให้เกิดเหตุการณ์รุนแรง"*

**ชั้นที่ 3 — สิ่งที่ห้ามพูด:**
- ❌ "ดาวเคราะห์ X ส่งพลังงานให้คุณ"
- ❌ "Schumann resonance 7.83 Hz จูนกับคุณ"
- ❌ "ดวงจันทร์เต็ม = คนโหด"
- ❌ "วันเกิดกำหนดบุคลิกภาพอย่างแน่นอน"
- ❌ ตัวเลขที่ฟังดูเฉพาะเจาะจงเกินไป (เช่น "ดาวศุกร์คุณคือดาวแห่งความรัก → คุณจะพบความรักในวันอังคาร")

### 9.4 Disclaimer ที่แนะนำ

> *"ข้อมูลในโมดูลนี้อ้างอิงจากงานวิจัยด้านสุขภาพ จังหวะชีววิทยา (chronobiology) และวิทยาอวกาศ บางส่วนเป็นข้อมูลจริงที่วัดได้ เช่น Kp index และจังหวะ ultradian ของสมอง บางส่วนเป็นการตีความเชิงสัญลักษณ์ ผลกระทบที่วัดได้มีขนาดเล็ก (น้อยกว่า 0.5%) และไม่ได้ทำให้เกิดเหตุการณ์รุนแรง โมดูลนี้มีไว้เพื่อเพิ่มบริบทการอ่านความ ไม่ใช่การพยากรณ์เชิงวิทยาศาสตร์ และไม่ควรใช้แทนคำแนะนำทางการแพทย์"*

---

## 10. แหล่งข้อมูลที่ใช้ (URL ที่ตรวจสอบได้)

### Primary / peer-reviewed
1. **Vieira C.L.Z. et al. (2019)** — *Environmental Health* 18:37 — https://pmc.ncbi.nlm.nih.gov/articles/PMC6739933/ — **263 เมือง, Kp, +0.13–0.47% ต่อ SD**
2. **Redelmeier D.A. & Shafir E. (2017)** — *BMJ* 359:j5367 — https://pmc.ncbi.nlm.nih.gov/articles/PMC5721903/ — **N=13,029, RR 1.05 (1.02–1.09)**
3. **Helfrich-Förster C. et al. (2021)** — *Science Advances* 7(5):eabe1358 — https://pmc.ncbi.nlm.nih.gov/articles/PMC7840133/ — **N=22, ประจำเดือนซิงกับจันทร์แบบ intermittent**
4. **McClintock M.K. (1971)** — **"Menstrual Synchrony and Suppression", *Nature* 229(5880):244–245** — https://www.nature.com/articles/229244a0 — *"Wellesley effect"; observational, no effect size/p-value reported*
5. **Menaker W. (1967)** — *Am. J. Obstet. Gynecol.* 98:1002–1004 — https://pubmed.ncbi.nlm.nih.gov/5647367/
6. **Gorvin J.J. & Roberts M.S. (1994)** — *Psychological Reports* 75(3 Pt 2):1435–1440 — https://pubmed.ncbi.nlm.nih.gov/7886164/
7. **Kokoszka A. (1998)** — *International Journal of Neuroscience* — https://pubmed.ncbi.nlm.nih.gov/9549035/ — **"ผลไม่น่าเชื่อถือ, BRAC ตอนตื่นไม่ได้รับการยอมรับ"**
8. **Vernadakis N. & Borer F.T. (1993)** — *Sleep* 5(4):311–322 — https://doi.org/10.1093/sleep/5.4.311
9. **Mavromichalaki O., Papailiou K., Gerontidou A. และคณะ (2021)** — "Human Physiological Parameters Related to Solar and Geomagnetic Disturbances", *Atmosphere* 12(12):1613 — https://doi.org/10.3390/atmos12121613 — **รีวิว: HR, BP, myocardial blood flow** *(MDPI 403 กับ bot; ใช้ DOI)* — ⚠️ *เดิมเขียนผิดเป็น "Otero et al." — แก้ตาม Crossref แล้ว; ไม่พบ Otero "K and S solar wind" ที่ยืนยันได้*
10. **Scoping review (2025)** — PMC12822803 — https://pmc.ncbi.nlm.nih.gov/articles/PMC12822803/ — **ระบุชัดว่ามนุษย์ไม่รับรู้ geomagnetic activity**
11. **Wagenmakers E.-J., Wetzels R., Borsboom D., van der Maas H. L. J., Kievit R. (2012)** — "An Agenda for Purely Confirmatory Research", *Perspectives on Psychological Science* 7(6):632–638 — https://doi.org/10.1177/1745691612463078 — **ยืนยัน DOI จริงแล้ว** — เสนอให้ย้อนตรวจ (re-analyze) ผลแบบ Bayesian เทียบกับ null อย่างเป็นกลาง ผลของแบบนี้คือ **ผลการศึกษาที่ดูน่าตื่นเต้นเมื่อใช้ prior เอนเอียง จะเปลี่ยนเป็นไม่น่าเชื่อถือเมื่อใช้ prior เป็นกลาง**
    - ⚠️ **หมายเหตุความถูกต้อง:** ฉบับรอบแรกที่เคยอ้างว่าเป็น "Wagenmakers et al. (2011), *Psychological Science* 22(4):439–446 เรื่อง intuitive-healing" **ไม่พบใน Crossref/SAGE และตรวจสอบแล้วไม่มีจริง** — ถูกลบออกจากรายการนี้ทั้งหมด กรุณาอย่าอ้างอิง
12. **Reber R. & Alcock I. (2020)** — "Searching for the impossible: Parapsychology's elusive quest", *American Psychologist* 75(5):660–674 — https://doi.org/10.1037/amp0000486 — ⚠️ *DOI ที่ถูกต้อง; ฉบับก่อนหน้าที่เคยใส่ (10.1177/1529100619889309) เป็น 404 และถูกลบออกแล้ว*
13. **Schmidt et al. (2025)** — "Synchronization of women's menstruation with the Moon has decreased but remains detectable when gravitational pull is strong", *Science Advances* 11(31) — https://doi.org/10.1126/sciadv.adw4096 — **N=1,023, 24 ปี; ซิงกับจันทร์ 16.5% → 13.2% หลังปี 2010**
14. **Phelps E. et al. (2020)** — "Seasonality and season of birth effect in the UK Biobank cohort", *Am. J. Hum. Biol.* 32(6):e23417 — https://pubmed.ncbi.nlm.nih.gov/32222094/ — **N=502,536**
15. **Mossbridge T.J., Tressoldi P., Bem D.J. (2012)** — meta-analysis of presentiment — **ES≈0.21 (95% CI 0.13–0.29)**
16. **Harris A. L. & Vitzthum V. J. (2013)** — "Has menstrual synchrony been disproved? A systematic review", *J. Sex Res.* 50(4):371–380 — https://pubmed.ncbi.nlm.nih.gov/23480070/ — **"lack of empirical evidence for MS sensu stricto"**
17. **Yang Z. & Schank J. C. (2020)** — "Women do not synchronize their menstrual cycles", *PLOS ONE* 15(1):e0227916 — https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0227916 — **N=1,083 ไม่พบผล**
18. **Skjærvø G.R., Fossøy F., Røskaft E. (2015)** — "Solar activity at birth predicted infant survival and women's fertility in historical Norway", *Proc. R. Soc. B* 282(1801):20142032 — https://doi.org/10.1098/rspb.2014.2032 (https://pmc.ncbi.nlm.nih.gov/articles/PMC4308994/) — **N=8,662, ชีวิตสั้นลง 5.2 ปี ในผู้เกิดช่วง solar maximum; กลไกเสนอ = UVR ทำลาย folate**
19. **Galak J., LeBoeuf R.A., Nelson L.D., Simmons J.P. (2012)** — "Correcting the past: Failures to replicate psi", *J. Pers. Soc. Psychol.* 103(6):933–948 — https://doi.org/10.1037/a0029709 — **N=3,289 ไม่พบผล; meta-analysis ของการทำซ้ำ d = 0.04 (ไม่ต่างจากศูนย์)**
20. **Rabeyron T. (2020)** — "Why most research findings about psi are false", *Frontiers in Psychology* 11:562992 — https://doi.org/10.3389/fpsyg.2020.562992 (https://pmc.ncbi.nlm.nih.gov/articles/PMC7530246/) — **สรุป es ทั้งสามสาขา: 0.14 / 0.14 / 0.21**

### Reference / methodology
21. **Kleitman N. (1963)** — BRAC original
22. **Britton J.P. et al. — Schumann resonance ทบทวน** — https://pmc.ncbi.nlm.nih.gov/articles/PMC10589055/
23. **"Is it the moon?" Swiss Medical Weekly** — https://smw.ch/index.php/smw/article/view/2616/4138 — **"ส่วนใหญ่ของงานไม่พบความสัมพันธ์"**

---

## สรุปสั้น

1. **มีหลักฐานจริง 1 อย่างที่ใช้ได้:** geomagnetic activity (Kp) → การเสียชีวิตโรคหัวใจ, effect size **0.1–0.5%**, จากงาน 263 เมือง
2. **มีหลักฐานปานกลาง:** ดวงจันทร์ → อุบัติเหตุรถ (RR 1.05) และอัตราการเกิด (+2–3%)
3. **BRAC ~90 นาที = ของจริงในช่วงนอน, ถกเถียงในช่วงตื่น**
4. **Schumann resonance = ฟิสิกส์จริง, แต่การเชื่อมกับมนุษย์ = ไม่มีหลักฐาน**
5. **ประจำเดือนซิงจันทร์ = ยังเป็นข้อถกเถียงที่เปิดอยู่; บทวิจารณ์ระบบปี 2013 สรุปว่า "ยังไม่มีหลักฐานเชิงประจักษ์เพียงพอ" และงาน N=1,083 ปี 2020 ไม่พบผล — ห้ามขายเป็นข้อเท็จจริง**
6. **Synchronicity/presentiment = หลักฐานที่เหลือ ≈ ไม่มี** หลังการตรวจสอบอย่างเหมาะสม — การทำซ้ำขนาดใหญ่ (Galak et al. 2012, N=3,289) **ไม่พบผล** และ meta-analysis ของการทำซ้ำทั้งหมดได้ **d = 0.04** ซึ่งครอบศูนย์ (Rabeyron 2020 สรุปว่า psi ทุกสาขา es = 0.14–0.21 จมอยู่ใน noise)
7. **ร่องรอยเดียวที่วัดเป็นรายบุคคลได้ = "เดือนที่เกิด" อยู่ในช่วงกิจกรรมสุริยะ** (Skjærvø et al. 2015, N=8,662, ชีวิตสั้นกว่า 5.2 ปี) — กลไกคือ **UV ทำลาย folate** ไม่ใช่พลังงาน และยังไม่มีการทำซ้ำยืนยันอิสระ จึงใช้เป็น "ประวัติสิ่งแวดล้อมตอนเกิด" ได้ แต่ห้ามขายเป็น "โชคชะตา"
8. **"พลังเอาทรัล" ที่ขายได้โดยไม่หลอกลูกค้า = การอ่านบริบทสิ่งแวดล้อมจริง + จังหวะชีววิทยาจริง, ไม่ใช่ฟิสิกส์เชิงอภิธรรม**

---

⚠️ **คำเตือนสำคัญ:** ไฟล์นี้รวบรวมข้อมูลเพื่อการออกแบบผลิตภัณฑ์ ไม่ใช่คำแนะนำทางการแพทย์ ตัวเลขทางสถิติทุกตัวมาจากงานวิจัยที่ตรวจสอบได้ แต่ผลของการศึกษาทางดาราศาสตร์/สุขภาพจริงมีความผันผวนสูง การนำไปใช้ควรตรวจสอบต้นฉบับทุกครั้ง
