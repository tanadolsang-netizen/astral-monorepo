---
source_type: youtube
url: https://www.youtube.com/watch?v=egBoq66lCRc
referenced_date: 2026-08-12
synthesized_into: "[[LLM Wiki Pattern]]"
---

# แหล่งข้อมูลดิบ: LLM Wiki pattern walkthrough (YouTube)

**URL:** https://www.youtube.com/watch?v=egBoq66lCRc
**ความยาว:** 19:19 (1159s)
**ดูเมื่อ:** 2026-08-12 ผ่าน `/watch` skill

## หมายเหตุการ ingest

- ไม่มี caption ในตัวคลิป (yt-dlp โดน HTTP 429 ตอนดึง caption) และไม่ได้ตั้งค่า Whisper API key ไว้ → **ไม่มี transcript** ข้อมูลด้านล่างมาจากการดูเฟรมภาพ (scene-aware, 32 เฟรมจากทั้งคลิป) เท่านั้น ไม่ใช่คำพูดจริงของผู้พูด
- ต้องแก้บั๊กใน `watch` skill script ก่อนถึงจะดึงเฟรมได้ (`-vsync` ที่ ffmpeg 9.0 เอาออกไปแล้ว → เปลี่ยนเป็น `-fps_mode`) — บั๊กเดียวกันเจอซ้ำอีกครั้งบนเครื่องบริษัท 2026-08-13 (ทั้ง `watch@claude-video` และ `claude-real-video`) เพราะ patch ที่ทำที่นี่ไม่ได้อยู่ใน repo (อยู่ใน plugin cache/pip site-packages) เลยไม่ sync ข้ามเครื่อง — ดูรายละเอียดเต็มที่ [[CLAUDE]] หัวข้อ "บั๊กเดิม เจอซ้ำ 2 ครั้ง แก้เองบนเครื่องทุกครั้ง"

## เนื้อหาที่อ่านได้จากเฟรม (สรุป)

- ผู้พูด (สวมเสื้อ "Huel") สาธิตการสร้าง "2nd Brain" ด้วย Obsidian + Claude Code ตาม LLM Wiki pattern ของ Andrej Karpathy
- อ้างอิง 2 โพสต์จาก X ของ Karpathy (@karpathy): โพสต์แรกอธิบายไอเดีย "LLM Knowledge Bases", โพสต์ตอบกลับให้ลิงก์ gist `github.com/karpathy/llm-wiki.md` ฉบับปรับปรุง
- เนื้อหา gist ที่อ่านได้จากเฟรม: core idea, query/lint/indexing process, index.md vs log.md, tips (Obsidian Web Clipper, attachment folder, graph view, git), และตารางเทียบ "LLM Wiki vs RAG: Trade-offs and Scale"
- โครงสร้างที่ผู้พูดวาดด้วย Excalidraw: `Vault/raw/`, `Vault/wiki/index.md`, `Vault/wiki/log.md`, `Vault/CLAUDE.md`
- มีช่วงคั่นด้วยวิดีโอ AI-generated (Veo) เด็กในห้องสมุดหนังสือลอย — ดูเหมือน sponsor segment ไม่เกี่ยวกับเนื้อหาหลัก
- มีตัวอย่างการ clip GitHub README ("MiroFish" — โปรเจกต์จำลองสังคม AI agent) เป็น demo การใช้ Web Clipper เฉยๆ ไม่ใช่เนื้อหาหลักของคลิป

## สังเคราะห์แล้วที่

- [[LLM Wiki Pattern]] — บทความเต็มของ pattern + mapping เข้ากับ vault นี้
