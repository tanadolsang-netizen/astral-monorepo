# Remember System Setup — สรุปละเอียด

บันทึกการตั้งค่าทั้งหมดที่ทำไปในเซสชันนี้ แยกตามหมวดหมู่ พร้อมสถานะปัจจุบันของแต่ละไฟล์

---

## 1. Remember Plugin — Config (`.remember/config.json`)

**สถานะปัจจุบัน: ไม่มีไฟล์นี้แล้ว (ลบทิ้ง) → ใช้ค่า default ของปลั๊กอิน**

| ค่า | Default (ปัจจุบัน) | เคยลองปรับเป็น | ผล |
|---|---|---|---|
| `thresholds.min_human_messages` | 3 | 1 | ยกเลิก |
| `thresholds.delta_lines_trigger` | 50 | 10 | ยกเลิก |
| `cooldowns.save_seconds` | 120 | 15 | ยกเลิก |

**เหตุผลที่ยกเลิก:** ทุกครั้งที่ save trigger จะเรียกโมเดล haiku จริง (เห็น token cost ใน log ~$0.018–0.02/ครั้ง) ค่าที่ลดไปทำให้ trigger ถี่เกินไป เสียเงินสะสมโดยไม่จำเป็น จึงลบ config override ทิ้ง กลับไปใช้ default

---

## 2. Remember Plugin — Identity (`.remember/identity.md`)

**สถานะ: สร้างแล้ว, ยังไม่ผ่านการตรวจจากคุณ**

เนื้อหาปัจจุบัน:
- อีเมล: tanadol.sang@gmail.com
- ใช้งานผ่าน VSCode เป็นหลัก ไม่ใช่ Obsidian app โดยตรง
- สื่อสารด้วยภาษาไทย

ไฟล์นี้ถูกฉีดเข้า context **ทุก session แบบเต็ม ไม่มีเงื่อนไข** (ต่างจาก `now.md`/`today-*.md` ที่ต้องผ่านเกณฑ์ humam-message/delta ก่อน) — ควรเปิดตรวจว่าตรงกับตัวคุณจริงไหม เพราะถ้าผิดจะทำให้ทุก session เข้าใจคุณผิดตาม

**⚠ ความเป็นส่วนตัว (อัปเดต 2026-08-12):** ~~มีอีเมลอยู่ในไฟล์นี้ตรงๆ~~ เช็คแล้ว — เนื้อหาปัจจุบันไม่มีอีเมลแล้ว มีแค่ "ทำงานผ่าน VSCode เป็นหลัก, สื่อสารภาษาไทย" ตรงกับความจริง ไม่ต้องแก้ไข

---

## 3. Remember Plugin — Gitignore (`.remember/.gitignore`)

**สถานะ: แก้แล้ว**

| ก่อน | หลัง |
|---|---|
| `*` (ignore ทั้งโฟลเดอร์) | `tmp/`<br>`logs/` |

ผล: ถ้ามี git repo ในอนาคต ไฟล์ความจำจริง (`now.md`, `today-*.md`, `identity.md`) จะถูก track ได้ ส่วน `tmp/` (marker/lock files) กับ `logs/` (debug log) ยังถูก ignore เหมือนเดิม

---

## 4. Remember Plugin — เนื้อหาความจำที่มีอยู่ตอนนี้

- `.remember/now.md` — buffer สด มี 3 รายการจากเซสชันนี้ (ปรับ config, สร้าง CLAUDE.md, ติดตั้ง taste-skill)
- `.remember/today-2026-08-12.md` — มี 1 รายการจาก background save ครั้งเดียวที่เกิดขึ้นตอน threshold ยังต่ำอยู่

---

## 5. ระบบความจำ Native ของ Claude Code

**ตำแหน่ง:** `C:\Users\ADMIN\.claude\projects\c--Users-ADMIN-Documents-Obsidian-Vault\memory\`

**คนละระบบกับ remember plugin ข้อ 1-4** — ระบบนี้เก็บข้อมูลถาวร/ภาพรวมผู้ใช้ที่ Claude คัดกรองเอง ไม่ใช่ log บทสนทนาดิบ

รายการที่บันทึกไว้แล้ว:
- `user_tooling.md` — ผู้ใช้ทำงานผ่าน VSCode เป็นหลัก ไม่ใช่ Obsidian app

---

## 6. Obsidian (`.obsidian/app.json`)

**สถานะ: แก้แล้ว**

เพิ่ม `"userIgnoreFilters": [".remember/"]` — โฟลเดอร์ความจำจะไม่โผล่ในรายการโน้ตหรือ graph view ของ Obsidian อีก (ไฟล์ยังอยู่จริง แค่ไม่แสดง)

---

## 7. VSCode (`.vscode/settings.json`)

**สถานะ: แก้แล้ว**

เพิ่ม `"files.exclude": {".remember": true}` — ซ่อนโฟลเดอร์ความจำจาก file explorer ของ VSCode เช่นกัน (เหตุผลเดียวกับข้อ 6 แต่คนละโปรแกรม)

---

## 8. Plugin/Marketplace อื่น

**ตรวจสอบแล้ว ไม่ต้องทำอะไร:** `taste-skill` (จาก `https://github.com/Leonxlnx/taste-skill.git`) ติดตั้งอยู่แล้วที่ `~/.claude/plugins/marketplaces/taste-skill` — remote URL ตรงกับที่ให้มา ไม่ใช่การติดตั้งซ้ำ

---

## 9. เอกสารอ้างอิง (`CLAUDE.md`)

**สถานะ: สร้าง+อัปเดตแล้ว** อยู่ที่ root ของ vault มี 2 หัวข้อ:
- Remember plugin config (อธิบายว่าตอนนี้ใช้ default, เคยลองปรับแล้วยกเลิกเพราะเรื่องค่าใช้จ่าย)
- ความแตกต่างระหว่างสองระบบความจำ (native vs remember plugin)

---

## จุดที่ยังไม่ได้ทำ / ควรพิจารณา

- [x] ~~Vault นี้ยังไม่ใช่ git repo — ไม่มี backup/version history เลย~~ แก้แล้ว (2026-08-12): `git init` + private GitHub remote ดู "Git backup" ใน [[CLAUDE]]
- [x] ~~ตรวจ/แก้เนื้อหา `.remember/identity.md` ให้ตรงกับตัวคุณจริง~~ ตรวจแล้ว (2026-08-12): ตรงกับความจริง ไม่มีอีเมลอยู่ในไฟล์
- [x] ~~`.remember/` โฟลเดอร์เก่ายังไม่ได้ลบ~~ ลบแล้ว (2026-08-12) — remember plugin ปิดใช้งานแล้ว ไม่มีอะไรอ้างอิงถึง

> **หมายเหตุ (lint 2026-08-12):** ข้อ 5 ด้านบน ("รายการที่บันทึกไว้แล้ว: `user_tooling.md`") ล้าสมัยแล้ว — native memory มีรายการเพิ่มขึ้นมากตั้งแต่เขียนโน้ตนี้ ดูรายการปัจจุบันจริงที่ `MEMORY.md` ใน native memory (ไม่ได้ sync เข้า vault นี้โดยตรง) แทนที่จะยึดลิสต์ในข้อ 5

## เชื่อมโยง
- [[Knowledge Hub]]
