# 📄 Pipeline สร้าง PDF ดวงชะตา + ไพ่ทาโรต์ (ไทยล้วน 100%)

## โครงสร้างโปรเจกต์ (C:\AI)
```
C:\AI\
├── NEW-AI-REBORN\        ← Backend + PDF pipeline (ที่นี้)
├── astral-expo\          ← Frontend (React Native)
├── obsidian-vault\       ← Second brain (จัดระเบียบแล้ว)
├── reports\              ← PDF ส่วนตัว (ห้าม commit)
├── command\              ← Command Bus
├── research-astrology\   ← งานวิจัยโหรา
├── tools\  workspace-scratch\  _scratch\  ← ของไม่ใช้/ทดลอง
```

## ไฟล์หลักใน NEW-AI-REBORN (scripts/)
| ไฟล์ | หน้าที่ |
|------|--------|
| `build_combined_premium.py` | **หลัก** — ประกอบ PDF ด้วย Playwright/Chromium (3D + gold frame) |
| `comfy_launch_stable.py` | Launch ComfyUI แบบ auto-restart (แก้ server ดับ) |
| `comfy_prompts.txt` | Prompt วาดรูป AI (5 ใบ) |
| `comfy_sdxl_txt2img.json` / `comfy_sdxl_img2img.json` | Workflow ComfyUI |
| `pdf_premium_template.html` | Template HTML (CSS 3D, gold, starfield) |
| `test_pipeline_multi.py` | ทดสอบ pipeline ดวงอื่น |

## รูป AI (assets/ai-art/)
```
cover_helios.png              ← ปก อาทิตย์เทพขับรถม้า
card_devil_final.png          ← มาร (มีคนโซ่)
card_six_pentacles_final.png  ← หกแห่งทรัพย์ (คนจนรับเหรียญ)
card_knight_pentacles_final.png ← อัศวินแห่งทรัพย์ (ถือเพนท์เคิล)
frame_gold.png                ← กรอบทอง
ref/                          ← รูปอ้างอิง Rider-Waite
```

## วิธีรันสร้าง PDF
```bash
# 1. เปิด ComfyUI (ถ้ายังไม่เปิด)
uv run python scripts/comfy_launch_stable.py

# 2. สร้าง PDF
PYTHONPATH=. uv run python scripts/build_combined_premium.py
# → C:\AI\reports\astral-natal-1996-04-04-thai.pdf
```

## กฎเหล็ก
- PDF = **ส่วนตัว** ห้าม commit ลง git เด็ดขาด
- ไทยล้วน 100% (ตรวจผ่าน LATIN NONE)
- รูปวาดด้วย ComfyUI SDXL (RTX5060) ไม่ใช้รูปสแกนเก่า
