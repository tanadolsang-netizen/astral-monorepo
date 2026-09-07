# LLM Wiki Pattern

Pattern จาก [Andrej Karpathy](https://gist.github.com/karpathy) สำหรับสร้าง personal knowledge base ด้วย LLM agent — ต้นทางจริงคือ[gist ของ Karpathy เอง](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) ([[raw/2026-08-14-karpathy-llm-wiki-gist]]) ส่วนที่วางรากฐานให้โน้ตนี้ตอนแรกคือคลิป [walkthrough นี้](https://www.youtube.com/watch?v=egBoq66lCRc) (2026-08-12) ซึ่งเป็นแค่ secondary explainer ของ gist ตัวนี้ แทนที่จะใช้ RAG แบบค้นแล้วลืม ให้ agent ค่อยๆ compile เอกสารดิบเป็น wiki ที่สะสมความรู้และเชื่อมโยงกันเอง Karpathy เรียก pattern นี้ว่า "intentionally abstract" — จงใจไม่ล็อครายละเอียด implementation ไว้ ปล่อยให้ผู้ใช้แต่ละคน (รวมถึง vault นี้) ตีความ folder layout เองตามบริบท

## แนวคิดหลัก

ประสบการณ์ทั่วไปกับ LLM + เอกสารคือ RAG: อัปโหลดเอกสาร, LLM ค้นหา ณ เวลา query, ตอบ — ใช้งานได้แต่ไม่มีการสะสม LLM ค้นพบความรู้เดิมซ้ำทุกครั้ง

แทนที่ด้วย **wiki ที่คงอยู่ (persistent)** — LLM ค่อยๆ สร้างและดูแล wiki แบบมีโครงสร้าง เชื่อมโยงกัน สังเคราะห์จากทุกอย่างที่เคยอ่าน ความต่างสำคัญ: **wiki เป็น artifact ที่สะสมและคงอยู่** cross-reference ถูก flag ไว้แล้ว ข้อขัดแย้งถูกตรวจพบแล้ว การสังเคราะห์สะท้อนทุกอย่างที่อ่านมาแล้วในทุก query — ไม่ใช่ค้นใหม่ทุกครั้ง

## โครงสร้าง

```
Vault/
├── raw/          — เอกสารดิบ (article, research, ...) read-only
├── wiki/
│   ├── index.md  — สารบัญ: ทุกหน้า + ลิงก์ + สรุป 1 บรรทัด + metadata (category, source, date)
│   └── log.md    — ประวัติแบบ append-only, prefix สม่ำเสมอ (เช่น `# [2026-04-08] ingest [ชื่อบทความ]`) เพื่อให้ grep ได้
└── CLAUDE.md     — กติกาบอก agent ว่าดูแล wiki ยังไง
```

## กระบวนการหลัก 3 อย่าง

- **Query** — agent ค้นหน้าที่เกี่ยวข้องใน wiki ก่อน อ่าน แล้วสังเคราะห์คำตอบพร้อม citation คำถามที่ตอบไม่ได้จาก wiki ค่อยหาข้อมูลเพิ่ม
- **Ingest** — เพิ่มเอกสารดิบใหม่ลง `raw/` แล้วให้ agent สังเคราะห์เข้า wiki (สร้างหน้าใหม่ หรืออัปเดตหน้าเดิม)
- **Lint** — เป็นระยะๆ ให้ agent เช็คสุขภาพ wiki: หา contradiction ระหว่างหน้า, claim เก่าที่ล้าสมัยแล้ว, orphan page (ไม่มีลิงก์เข้า), concept สำคัญที่ถูกพูดถึงแต่ยังไม่มีหน้าเป็นของตัวเอง, data gap ที่เติมได้ด้วย web search

## ทำไมถึง scale ได้ / ข้อจำกัด

| | LLM Wiki | RAG |
|---|---|---|
| เหมาะกับ | ส่วนตัว/ทีม (ร้อย–แสนเอกสาร) | องค์กร (ล้านเอกสาร) |
| ความรู้สะสมไหม | สะสม (compounding) | ไม่ — ค้นใหม่ทุก query |
| การสังเคราะห์ | ทำไว้ล่วงหน้าแล้ว | ค้นพบใหม่ทุกครั้ง |
| Contradiction | flag ครั้งเดียว คงอยู่ | เจอซ้ำทุกครั้ง |
| Infrastructure | markdown ธรรมดา | vector DB + embedding pipeline |
| ต้นทุน | ถูกกว่ามาก | แพงกว่ามาก |

ข้อจำกัด: **scale ไปถึงล้านเอกสารไม่ได้** — คอขวดคือ context window ของ LLM เอง โมเดล navigation ของ wiki ชนเพดานฟิสิกส์ตรงนี้โดยตรง

## ความเสี่ยง / จุดที่พัง (failure modes)

จาก comment thread ของ gist ต้นฉบับ ([[raw/2026-08-14-karpathy-llm-wiki-gist]]) — ไม่ได้อยู่ในสองวิดีโอ explainer เลย และเกี่ยวข้องโดยตรงกับ vault นี้เพราะเรารัน pattern นี้จริง:

- **Wiki อ้างอิงตัวเองวนเป็นวง (self-citation loop) เมื่อโตถึงระดับ ~1000+ ไฟล์** — ยิ่งหน้าเยอะ agent ยิ่งมีแนวโน้ม cross-reference หน้าที่อ้างอิงกันเองแทนที่จะกลับไปเช็คแหล่งดิบ vault นี้ยังเล็ก (~19 โน้ต) ยังไม่เจอ แต่ควรจับตาเมื่อโน้ตเพิ่มขึ้นเรื่อยๆ
- **ไม่มี human review gate** — Karpathy เตือนว่าถ้าไม่มีจุดให้มนุษย์ตรวจสอบ ข้อขัดแย้งหรือข้อสรุปที่ AI สร้างขึ้นเองอาจกลายเป็น "สิ่งที่องค์กรเชื่อ" แบบเงียบๆ โดยไม่มีใครยืนยัน — vault นี้ตอนนี้ Claude เขียนและ lint wiki เองทั้งหมด ไม่มี review gate แยกจากคนจริงๆ
- **Wiki drift จาก reality ที่เปลี่ยนไป** — ต่างจาก contradiction ระหว่างโน้ต (ที่ lint process ที่มีอยู่แล้วจับได้) นี่คือกรณีที่ตัวความจริงภายนอกเปลี่ยน (เช่น โค้ดถูกแก้) แต่ไม่มีใครไปบอก wiki เลยไม่มีกลไกตรวจจับ — vault นี้ไม่มีกลไกนี้เช่นกัน

## Prior art — คนอื่นทำ pattern นี้ยังไงบ้าง

จาก [[raw/2026-08-14-llm-wiki-hn-community-implementations]] (Hacker News, community angle ที่สองวิดีโอ explainer ไม่มี):

- **Open-source MCP implementation** — Lucas Astorian ทำ implementation ที่ ingest เอกสารได้หลายฟอร์แมต (PDF/Word/Excel ฯลฯ) แปลงเป็น markdown ที่ index ไว้ แล้ว expose wiki ให้ Claude ผ่าน MCP server ให้ agent จัดการ/แก้ไข/เชื่อมโยง/cite เองอัตโนมัติ — คนละแนวกับ vault นี้ที่ใช้แค่กติกาใน `CLAUDE.md` บวก Claude Code session ธรรมดา ไม่มี MCP server เฉพาะ
- **รายงานการใช้งานจริงที่ scale ใหญ่กว่า vault นี้มาก** — ผู้ใช้ HN (vbarsoum) เอา pattern นี้ไปใช้กับหนังสือธุรกิจ 3 เล่ม (~155K คำ) ระดับ chapter ได้ผลลัพธ์ 210 concept pages กับ ~4,600 cross-references พร้อมรายงาน "unprompted synthesis across sources" — ยืนยันว่า behavior แบบ compounding/cross-reference ที่ Karpathy อ้างเกิดขึ้นจริงที่ scale ใหญ่กว่า toy demo
- **ข้อวิจารณ์ที่ควรจำไว้** — ผู้ใช้ HN (qaadika) ตั้งคำถามว่างานบัญชี/ดูแลระบบที่ Karpathy เสนอให้ยกให้ LLM ทำแทน (filing, cross-reference, สรุป) อาจเป็นส่วนที่ทำให้มนุษย์**เข้าใจเนื้อหาจริงๆ** — automate ส่วนนี้ออกไปอาจเอาส่วนที่มีคุณค่าออกไปด้วย ไม่ใช่แค่ส่วนที่น่าเบื่อ คำถามนี้ยังไม่มีคำตอบชัดเจนสำหรับ vault นี้ — ผู้ใช้ยัง curate แหล่งข้อมูล/กำหนดทิศทางเองอยู่ (ตามที่ Karpathy บอกว่าเป็นงานที่เหลือของมนุษย์) แต่ยังไม่ชัดว่าบทบาทนั้นพอไหม หรือการเขียนโน้ตด้วยมือยังจำเป็นสำหรับการเรียนรู้บางแบบ

## เครื่องมือเสริม (จำเป็นเมื่อ wiki โตขึ้นเท่านั้น — ไม่ต้องสร้างล่วงหน้า)

- Search engine ในตัว markdown (hybrid BM25/vector, on-device) — จำเป็นเมื่อ wiki โตเกิน ~100 หน้า ที่ index.md อย่างเดียวไม่พอ
- **Obsidian Web Clipper** (browser extension) — clip บทความเว็บเป็น markdown ใส่ `raw/` โดยตรง
- **Download images locally** — Obsidian Settings → Files and links → ตั้ง attachment folder path คงที่ (เช่น `raw/assets/`) แล้วใช้ hotkey "Download attachments for current file" ให้ agent อ้างอิงรูปแบบ local ได้แทนที่จะพึ่ง URL ที่อาจตายในอนาคต
- **Graph view** — วิธีที่ดีที่สุดในการเห็นรูปร่างของ wiki: อะไรเชื่อมกับอะไร หน้าไหน orphan หน้าไหนเป็นศูนย์กลาง
- Git repo ของ markdown files — ได้ version history, branching, collaboration ฟรี

## ประเด็นสำคัญที่สุด

งานหลักของการดูแล knowledge base ไม่ใช่การอ่านหรือคิด — คือ**งานบัญชี/ดูแลระบบ** (bookkeeping): อัปเดต cross-reference, รักษาสรุปให้ทันสมัย, สังเกตเมื่อข้อมูลใหม่ขัดแย้งกับหน้าเก่า, ดูแล log มนุษย์เลิกทำ wiki เพราะภาระดูแลโตเร็วกว่าความรู้ที่เพิ่ม — LLM ไม่เบื่อ ไม่ลืมอัปเดต cross-reference และแตะได้ 15 ไฟล์ในรอบเดียว **งานของมนุษย์คือ curate แหล่งข้อมูล กำหนดทิศทางการวิเคราะห์ ถามคำถามที่ดี และคิดว่าทั้งหมดมันหมายความว่าอะไร**

## Mapping เข้ากับ vault นี้

ส่วนใหญ่มีอยู่แล้วก่อนตั้งชื่อ pattern นี้ให้มัน — ดูรายละเอียดที่ [[CLAUDE]] หัวข้อ "LLM Wiki pattern":

- `raw/` — สร้าง (2026-08-12) และตั้งกติกาให้ auto-archive แหล่งอ้างอิงภายนอกทุกครั้งที่คุยถึง (URL/PDF/YouTube/บทความ) ไม่ต้องรอผู้ใช้สั่งให้ clip — ดูตัวอย่างที่ `raw/2026-08-12-llm-wiki-pattern-walkthrough.md`
- [[Knowledge Hub]] เล่นบท `index.md`
- `git log` เล่นบท `log.md` (ไม่ได้สร้างไฟล์แยก — ซ้ำซ้อนกับ git history ที่มีอยู่แล้ว)
- ติดตั้ง Obsidian Web Clipper แล้ว และตั้งค่าเสร็จ/ทดสอบผ่านจริง (2026-08-13, ดูตัวอย่างไฟล์ที่ clip สำเร็จ `raw/2026-08-13-Obsidian Web Clipper.md`) — ค่าที่ถูกต้องคือ:
  - **General → Vaults**: ใส่แค่**ชื่อ vault** คือ `Obsidian Vault` เฉย ๆ ห้ามใส่ full path (เช่น `C:\Users\70098372\...`) เพราะ Obsidian URI protocol (`obsidian://`) match ด้วยชื่อ ไม่ใช่ path — ใส่ path ไปจะขึ้น error "Vault not found" ทันที (ชื่อโฟลเดอร์ vault เหมือนกันทั้ง 2 เครื่อง เลยใช้ชื่อเดียวได้ ไม่ต้องแยกตามเครื่อง)
  - **Template → Location → Vault**: เลือกชื่อ `Obsidian Vault` (ไม่ใช่ path เหมือนกัน)
  - **Template → Location → Note location**: `raw`
  - **Template → Location → Note name**: `{{date|date:"YYYY-MM-DD"}}-{{title}}` — ใช้ **filter syntax แบบ pipe** (`|date:"..."`) เท่านั้น ห้ามใช้ `{{date:YYYY-MM-DD}}` (colon ตรง ๆ) เพราะ extension ไม่รู้จัก จะขึ้น "Unknown variable" แล้วไม่สร้างไฟล์เลย
  - ส่วน frontmatter ที่ได้ (`title`/`source`/`author`/`published`/`created`/`description`/`tags`) คนละ field name กับ convention มือ (`source_type`/`url`/`referenced_date`/`synthesized_into`) — ดูตาราง mapping เต็มที่ `raw/README.md`; `synthesized_into` ต้องเติมเองทีหลังตอน agent สังเคราะห์เข้า wiki เสมอ เพราะ Web Clipper ไม่รู้ล่วงหน้าว่าจะไปโยงกับโน้ตไหน

## แหล่งอ้างอิงที่สอง (ยืนยัน pattern ซ้ำ)

ดูวิดีโอที่สองเรื่องเดียวกันนี้ 2026-08-13 (คนละ creator: Teacher's Tech แทน Huel-shirt guy) — เนื้อหาตรงกับที่สรุปไว้ข้างบนเกือบทั้งหมด ไม่มีอะไรขัดแย้ง รายละเอียดเต็มที่ `raw/2026-08-13-karpathy-llm-wiki-teachers-tech.md`

## Sources

- [[raw/2026-08-14-karpathy-llm-wiki-gist]] — gist ต้นฉบับของ Karpathy (primary source), edge case: self-citation loop / review gate / drift
- [[raw/2026-08-14-llm-wiki-hn-community-implementations]] — Hacker News: open-source MCP implementation, รายงานการใช้งานที่ scale ใหญ่ (210 หน้า/4,600 cross-refs), ข้อวิจารณ์
- [[raw/2026-08-12-llm-wiki-pattern-walkthrough]] — วิดีโอ walkthrough แรกที่พาโน้ตนี้เกิดขึ้น (secondary explainer)
- [[raw/2026-08-13-karpathy-llm-wiki-teachers-tech]] — วิดีโอ explainer ตัวที่สอง ยืนยัน pattern ซ้ำ (secondary explainer)

## เชื่อมโยง
- [[CLAUDE]]
- [[Knowledge Hub]]
