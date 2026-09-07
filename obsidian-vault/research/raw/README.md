# raw/

เอกสารดิบที่ยังไม่ได้สังเคราะห์ — บทความที่ clip มา, งานวิจัย, transcript ฯลฯ

**Read-only จากมุมมอง LLM**: agent ไม่แก้ไขไฟล์ในนี้ มีหน้าที่แค่อ่านแล้วสังเคราะห์ออกไปเป็นโน้ตใน vault หลัก (ลิงก์ผ่าน [[Knowledge Hub]])

วิธี ingest: ใช้ Obsidian Web Clipper (browser extension) clip บทความเว็บมาเป็น markdown วางในนี้ ตั้ง attachment folder เป็น `raw/assets/` ใน Obsidian Settings → Files and links ถ้าต้องการโหลดรูปมาเก็บ local ด้วย

## 2 รูปแบบ frontmatter ใน raw/

ไฟล์ในโฟลเดอร์นี้มี 2 ที่มา — schema frontmatter ไม่เหมือนกัน อย่าสับสน:

**1. Archive มือ** (agent สร้างตอนคุยถึงแหล่งอ้างอิงในบทสนทนา — ดู `2026-08-12-llm-wiki-pattern-walkthrough.md` เป็นตัวอย่าง):

```yaml
source_type: youtube|article|pdf|...
url: https://...
referenced_date: YYYY-MM-DD
synthesized_into: "[[ชื่อโน้ตปลายทาง]]"
```

**2. Obsidian Web Clipper** (ตั้งค่า template ไว้แล้ว 2026-08-13 — filename `{{date:YYYY-MM-DD}}-{{title}}`, path `raw`):

```yaml
title: {{title}}
source: {{url}}
author: {{author}}
published: {{published}}
created: {{date}}
description: {{description}}
tags: clippings
```

ไม่มี `synthesized_into` — ต้องเติมเองตอน agent สังเคราะห์ไฟล์นี้เข้า wiki (เทียบ field: `source`≈`url`, `created`≈`referenced_date`, `source_type` ไม่มี ให้เดาจาก `source`/เนื้อหา)

อ้างอิง pattern เต็มจาก gist ของ Andrej Karpathy: [github.com/karpathy/gist llm-wiki.md](https://gist.github.com/karpathy)
