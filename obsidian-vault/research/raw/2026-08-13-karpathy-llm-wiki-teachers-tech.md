---
source_type: youtube
url: https://youtu.be/iXd0t60YmMw
referenced_date: 2026-08-13
synthesized_into: "[[LLM Wiki Pattern]]"
---

# แหล่งข้อมูลดิบ: Karpathy's LLM Wiki — Full Beginner Setup Guide (Teacher's Tech)

**URL:** https://youtu.be/iXd0t60YmMw (ช่อง: Teacher's Tech, ผู้บรรยาย: Jamie)
**ความยาว:** 15:05 (904.5s)
**ดูเมื่อ:** 2026-08-13 ผ่าน `crv` (claude-real-video) — เต็ม transcript จริง (whisper local, base model)

## หมายเหตุการ ingest

- ลอง `/watch` (watch@claude-video) ตรงจาก YouTube URL ก่อน แต่เครื่องบริษัทบล็อก `youtube.com` ที่ระดับ firewall (TCP timeout ทุกครั้ง, ยืนยันแล้วว่าเป็น network policy ไม่ใช่บั๊ก — ดู [[CLAUDE]]) จึงใช้ไฟล์สำเนาที่ผู้ใช้อัปโหลดไว้ใน Google Drive แทน (`gdown` ดาวน์โหลดมาเป็นไฟล์ local แล้วรัน `crv` กับไฟล์นั้น)
- เจอบั๊ก ffmpeg `-vsync` เดียวกับที่เคยเจอมาก่อนใน `raw/2026-08-12-llm-wiki-pattern-walkthrough.md` — แก้ซ้ำใน `claude-real-video` ด้วย (ดูรายละเอียดที่ [[CLAUDE]])
- นี่คือวิดีโอ **คนละอันกับ** ที่สังเคราะห์ไว้แล้วใน `raw/2026-08-12-llm-wiki-pattern-walkthrough.md` (คนละ creator, คนละช่อง) — เนื้อหาตรงกับ pattern เดิมเกือบทั้งหมด ถือเป็นแหล่งยืนยันที่สอง (second confirming source)

## เนื้อหาสรุป (จาก transcript เต็ม)

ปัญหาที่พูดถึง: RAG แบบเดิม (upload → ค้นหา chunk → ตอบ) เริ่มจากศูนย์ทุกครั้งที่ถาม ไม่มีอะไรถูกสะสมไว้

**LLM Wiki** (ไอเดียของ Andrej Karpathy): แทนที่จะค้นทุกครั้ง ให้ AI อ่านเอกสารครั้งเดียวแล้วสร้าง wiki ที่เป็น markdown เชื่อมโยงกัน — แหล่งใหม่จะถูกอ่าน สกัดประเด็น อัปเดตหน้าเดิม สร้างหน้าใหม่ เชื่อมโยง และ flag ข้อขัดแย้งทันทีถ้ามี

คำอุปมา: "Obsidian คือ IDE, LLM คือโปรแกรมเมอร์, wiki คือ codebase"

**สามชั้น:** raw (read-only source of truth) → wiki (markdown ที่ AI ดูแล) → schema/`CLAUDE.md` (กฎ: ทุกหน้ามี summary บนสุด, ทุก claim ต้องอ้างอิงแหล่งที่มา)

**Demo:** clip บทความท่องเที่ยวโตเกียวด้วย Web Clipper ใส่ `raw/` → สั่ง Claude Code ingest → ได้ wiki pages มีโครงสร้างใน ~3 นาที → เพิ่มแหล่งที่สอง → AI อัปเดตหน้าเดิมที่เกี่ยวข้องด้วย ไม่ใช่แค่สร้างใหม่ → ถามคำถามข้าม 2 แหล่ง → AI ตอบจาก wiki พร้อม cite หน้า ไม่กลับไปอ่าน source ใหม่

**Lint wiki เป็นระยะ:** หา contradiction ระหว่างหน้า, claim ล้าสมัย, orphan pages, concept ที่พูดถึงแต่ไม่มีหน้าเป็นของตัวเอง

**ข้อจำกัดที่พูดตรงๆ:** เหมาะสเกลส่วนตัว (~100 บทความ), garbage-in-garbage-out, ต้องมี coding agent (Obsidian เฉยๆ ทำเองไม่ได้), AI พลาดได้ (เหตุผลที่มี lint)

## สังเคราะห์แล้วที่

- [[LLM Wiki Pattern]] — ยืนยัน pattern เดิมซ้ำ ไม่มีอะไรขัดแย้งกับสิ่งที่มีอยู่แล้ว
