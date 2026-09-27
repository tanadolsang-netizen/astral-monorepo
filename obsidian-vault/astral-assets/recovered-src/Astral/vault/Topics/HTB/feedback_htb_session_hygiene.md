# กติกา: เล่น HTB 1 เครื่อง = 1 conversation

สรุปย่อจาก native memory ของ Claude Code (`feedback_htb_session_hygiene.md` — คนละไฟล์กับอันนี้ ดูหมายเหตุด้านล่าง)

เล่น HackTheBox (หรือ pentest/CTF แบบเดียวกัน) ทีละเครื่องต่อ 1 conversation ไม่ต่อ exploit chain ของหลายเครื่องยาวๆ ในบทสนทนาเดียว

**ที่มา:** exploit chain ยาว (recon → enumerate → foothold → privesc) ข้ามหลายเครื่องในบทสนทนาเดียวทำให้ auto-mode safety classifier บล็อกแบบถาวรกลางทาง — เจอตอน privesc ของหนึ่งใน 3 เครื่องแรกที่เล่น (Meow, Cap, TwoMillion; 2026-08-13 ดู [[HTB Methodology]])

**วิธีใช้:** ถ้า auto mode บล็อกกลางทางตอนทำงาน pentest/CTF ให้สลับจาก auto เป็น **default permission mode** สำหรับ session นั้น แล้วรันคำสั่งเดิมซ้ำ — จะผ่านได้ด้วยการยืนยันทีละคำสั่งแทน เริ่ม conversation ใหม่ต่อเครื่องช่วยไม่ให้ปัญหานี้เกิดตั้งแต่แรก

**ยืนยันจากแหล่งภายนอก (2026-08-14):** Bishop Fox ([[raw/2026-08-14-ai-agent-security-guardrails-pentest]]) ตั้งธีซิสไว้ตรงกันว่า "model-level safeguards are not security boundaries" — guardrail ที่ใช้งานได้จริงต้องอยู่นอกตัวโมเดล (โครงสร้าง/process) ไม่ใช่พึ่งการโต้เถียงหรือ prompt โมเดลให้ยอมทำต่อ ปัญหาที่เจอที่นี่ (safety classifier บล็อกถาวรกลาง exploit chain) เป็นตัวอย่างของการพึ่ง model-level safeguard ตรงๆ ส่วนวิธีแก้ที่ใช้อยู่ (สลับ permission mode / เริ่ม session ใหม่ต่อเครื่อง) คือการปรับ session/scope boundary ซึ่งเป็น *ประเภท* การแก้ที่ตรงกับธีซิสนี้ — ยืนยันว่านี่ไม่ใช่แค่ workaround เฉพาะหน้าที่ผู้ใช้คิดขึ้นเอง

## Sources
- [[raw/2026-08-14-ai-agent-security-guardrails-pentest]]

## เชื่อมโยง
- [[HTB Methodology]]
- [[Knowledge Hub]]

---
*หมายเหตุ: โน้ตนี้เป็น stub สรุปไว้ในตัว vault เพื่อให้ Graph View resolve ลิงก์จาก `HTB Methodology.md` ได้ — ต้นฉบับจริงที่ Claude ใช้งานคือ native memory ที่ `~/.claude/projects/.../memory/feedback_htb_session_hygiene.md` ไฟล์นี้ (ทั้งในตัว vault และ native memory) สร้างขึ้นใหม่ 2026-08-13 จากเนื้อหาที่สรุปไว้ในตัว `HTB Methodology.md` เอง เพราะไม่มีอยู่บนเครื่องบริษัทเลยมาก่อน — ไม่เกี่ยวกับ [[project_htb_kali_lab]] (infra/credentials) ซึ่งยังกู้คืนไม่ได้และไม่ควรเดา*
