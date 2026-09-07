---
source_type: github_repo
url: https://github.com/diegosouzapw/OmniRoute
referenced_date: 2026-08-14
synthesized_into:
---

# แหล่งข้อมูลดิบ: OmniRoute — The Free AI Gateway (GitHub repo)

**URL:** https://github.com/diegosouzapw/OmniRoute
**Clone มาไว้ที่:** `C:\Users\70098372\Desktop\OmniRoute` (เครื่องบริษัท)
**npm global install:** `omniroute@3.8.48`

## คืออะไร

AI gateway แบบ self-hosted (Next.js app) ที่รวม free tier ของ AI provider ~339 เจ้า (90+ ฟรี) มาไว้หลัง endpoint เดียว (`localhost:20128`) แล้วให้เครื่องมืออย่าง Claude Code / Cursor / Copilot ชี้มาใช้แทนบัญชีจริง README เขียนเองว่ามี "15 providers ToS-flagged so you decide" — รู้ตัวว่าบาง provider อาจขัดเงื่อนไขบริการ

## สิ่งที่พบจากการใช้งานจริงวันนี้ (เครื่องบริษัท)

- **Windows path-length bug:** clone ครั้งแรกล้มเพราะไฟล์ทดสอบ (`__tests__/modelCompatPopover-*.test.tsx`) ยาวเกิน Windows MAX_PATH — แก้ด้วย `git config --global core.longpaths true`
- **`omniroute launch` ไม่ inject `ANTHROPIC_MODEL`** — พึ่ง `CLAUDE_CONFIG_DIR` ชี้ไปโปรไฟล์ (`~/.claude/profiles/<name>/settings.json`) เท่านั้น ถ้าไม่ใส่ `--profile` จะใช้โมเดลเดิมที่ Claude Code เคยเลือกไว้ (เช่น "Opus 5 1M") ซึ่งไม่มีในแคตาล็อกของ OmniRoute → error "model may not exist"
- **Free-tier pool ส่วนใหญ่ตายจาก IP เครื่องบริษัทนี้:** `theoldllm/*` ทุกโมเดล 403 Forbidden, `opencode/*` ฟรีส่วนใหญ่ 401 "not supported" หรือ 429 rate-limited, `mimocode` 400, `auggie/*` ต้องมี CLI ชื่อ `auggie` ติดตั้งแยกในเครื่อง (ไม่มี → 502) — ทำให้ combo `auto/best-coding` ไล่ลองจนหมดเวลาก่อนจะสำเร็จ (สาเหตุจริงของ error "Subprocess initialization did not complete within 60000ms" ที่เจอตอนแรก ไม่ใช่ปัญหาเน็ต/proxy อย่างที่สงสัยตอนแรก)
- **`omniroute autostart enable` ใช้ไม่ได้บน Windows จริง** (README บอกรองรับแค่ Linux systemd user service) — error "system cannot find the path specified" เงียบๆ แต่ยังรายงาน enabled:true ผิด ใช้ VSCode task (`runOptions.runOn: folderOpen`) แทนสำเร็จกว่า
- **Provider connection มี health-flag ที่ค้างได้:** ยิง request ที่ 402 (credits exhausted) ครั้งเดียวจะ mark ทั้ง connection เป็น `credits_exhausted` บล็อกคำขอถัดไปทุกโมเดลรวมถึงโมเดลฟรี ต้องยิง `/api/providers/[id]/test` ซ้ำเพื่อ clear flag
- **ทางที่ใช้งานได้จริงสุดท้าย:** เพิ่ม OpenRouter API key ของผู้ใช้เอง (`api.openrouter.ai`) เข้า OmniRoute แล้วใช้เฉพาะโปรไฟล์ที่ลงท้าย `-free` (เช่น `openrouter-nvidia-nemotron-3-super-120b-a12b-free`) — โปรไฟล์ที่ไม่ใช่ `-free` หรือ `auto-*` เสี่ยงชนโมเดลเสียเงิน (เจอ 402 จริงกับ Claude Haiku ผ่าน OpenRouter)

## หมายเหตุความปลอดภัย

ผู้ใช้พิมพ์ OpenRouter API key ดิบลงแชท 2 ครั้ง หลุดเข้า `Claude Session 2026-08-14.md` ทั้งคู่ (ก่อน Stop hook จะ push อัตโนมัติ) — redact สำเร็จครั้งแรกก่อน commit, ครั้งที่สอง user สั่งไม่ให้ redact (`ผมอนุญาต`) แต่ hook `secret-scan.js` ของ `pro-workflow` บล็อกการเขียนคีย์ดิบกลับเข้าไฟล์แบบ hard-block เลยยังคง redacted อยู่ทั้งคู่จริง — ดูรายละเอียดเต็มใน `Claude Session 2026-08-14.md`

## เชื่อมโยง
- [[Knowledge Hub]]
- [[Company PC Setup]]
- [[Claude Code Tooling]]
