# Dispatch Console Build Kit (เสริมสุข)

เครื่องมือ automation สำหรับทีมงานที่เสริมสุข — dashboard + บอทอัปเดตสถานะ shipment บนระบบ TMS (`th-ssc.certu.ai`) แทนการคลิกเอง

## สถาปัตยกรรม
```
Dispatch_Control_Console.html  →  หน้า Dashboard (UI)
        ↓ รันผ่าน
dispatch_console_app.py        →  ห่อเป็น .exe เดียว (pywebview + PyInstaller)
        ↓ เรียกใช้
Certu_auto.py                  →  บอท Playwright อัตโนมัติ
        ↓ ทำงานบน
th-ssc.certu.ai                →  ระบบ TMS/ขนส่งจริงของบริษัท (Certu)
```

- Login ครั้งเดียว → เก็บ session ที่ `certu_session.json` (Playwright `storage_state` มาตรฐาน — **ห้ามส่งไฟล์นี้ให้ใครรวมถึง Claude**, เทียบเท่าแชร์บัญชี)
- Auto-update HTML ผ่าน Google Drive (แชร์แบบ Viewer เท่านั้น)
- Team Activity tracker ส่ง username + event ไป Google Sheet กลาง

## สถานะล่าสุด (2026-08-12)
Build สุดท้ายพร้อมส่งทีมแล้ว — รวม fix บั๊ก 2 จุด + refactor + unit test 24 ตัวผ่านหมด

⚠️ **ไฟล์ build อยู่ใน scratchpad ของ session เดิม (`...\dispatch_kit\build_kit\dist_final\`) ซึ่งเป็น temp path ผูกกับ session — อาจถูกล้างไปแล้ว** ถ้ายังไม่ได้ส่งให้ทีม ต้อง build ใหม่หรือหาไฟล์จาก path นั้นก่อนมันหาย

## บั๊กที่พบระหว่างรีวิว/แก้ไปแล้ว
| ระดับ | จุด | รายละเอียด | สถานะ |
|---|---|---|---|
| 🔴 Build-breaking | Chromium ไม่ถูกฝังเข้า exe | ขาด `PLAYWRIGHT_BROWSERS_PATH=0` ก่อนโหลด Chromium → ได้ไฟล์ 53MB แทนที่จะเป็นหลักร้อย MB | ✅ แก้แล้ว (364MB ตรงตามควร) |
| 🟡 Logic bug | `process_single_shipment` (`Certu_auto.py` ~966-975) | shipment หลายขั้นตอน: ขั้นแรกสำเร็จจริง แต่ขั้นถัดไปเจอ `skip_month`/`no_date` → สถานะเขียนทับ ความสำเร็จขั้นแรกไม่ถูกนับใน report/`done_set` → resume รอบหน้าอาจทำซ้ำ, CSV นับสถิติต่ำกว่าจริง | ✅ แก้แล้ว |
| 🟢 Security (ต่ำ) | `dispatch_console_app.py:59` | Longdo Maps API key ฝังในซอร์ส — ดึงจาก .exe ได้ด้วย `strings.exe` (แต่เป็น free-tier key) | รับทราบ ไม่ร้ายแรง |

## ยังไม่ได้ทำ
- [ ] แจ้งทีมเรื่องเก็บ username อัตโนมัติ (เข้าข่าย PDPA) — ยังไม่มีการแจ้ง
- [ ] ยังไม่ได้ทดสอบ `--dry-run` กับเว็บจริง (ต้อง login เองที่เครื่อง)
- [ ] เพิ่มฟีเจอร์ใหม่ในบอท — ยังไม่มีโจทย์ชัดเจน

## เชื่อมโยง
- [[Claude Session 2026-08-12]] — รายละเอียดบทสนทนาเต็มตอน 16:02-16:21
- [[Knowledge Hub]]
