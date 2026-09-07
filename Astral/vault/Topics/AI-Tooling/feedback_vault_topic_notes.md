# กติกา: สกัด topic สำคัญออกเป็นโน้ตของตัวเอง

สรุปย่อจาก native memory ของ Claude Code (`feedback_vault_topic_notes.md` — คนละไฟล์กับอันนี้ ดูหมายเหตุด้านล่าง)

เมื่อ topic ที่พูดถึงใน session log หรือ writeup ที่ฝังอยู่ใน `CLAUDE.md` (หรือโน้ตอื่น) โตจนสมควรมีที่ทางของตัวเอง ให้สกัดออกมาเป็นโน้ตเฉพาะ แล้วลิงก์จาก [[Knowledge Hub]] — ไม่ปล่อยให้จมอยู่ใน session log หรือทำให้เอกสารต้นทางบวม

**ที่มา:** ตั้งจากบรรทัดฐาน 2 ครั้งใน 2026-08-12 — สกัด [[Dispatch Console Build Kit - เสริมสุข]] ออกจาก session log (commit `511897e`), ตามด้วยสกัด [[LLM Wiki Pattern]] ออกจาก CLAUDE.md (commit `e43262d`) โดย commit message อ้างถึงกรณีแรกเป็นบรรทัดฐานตรงๆ

**วิธีใช้:** ตอน lint pass (หรือเมื่อไหร่ที่ topic โตเกินที่ทางเดิม) เช็ค [[Knowledge Hub]] ก่อนเพื่อไม่ให้ซ้ำกับโน้ตที่มีอยู่ แล้วสกัดเนื้อหาออกมาเป็นโน้ตใหม่ ลิงก์จากตารางใน Knowledge Hub และเหลือแค่ pointer สั้นๆ ไว้ที่เดิมแทนเนื้อหาเต็ม

**พื้นฐานทฤษฎี (Zettelkasten):** กติกานี้เป็นการ apply แนวคิด Zettelkasten ของ Sönke Ahrens (*How to Take Smart Notes*) โดย agent แทนที่จะเป็นมนุษย์ — `raw/` ≈ literature notes (สรุปแบบผูกกับ source ด้วยคำของตัวเอง), โน้ต topic ที่สกัดออกมาแล้ว ≈ permanent notes/zettels (ยืนได้ด้วยตัวเอง เชื่อมโยงด้วย `[[...]]`), session log ≈ fleeting notes (บันทึกดิบชั่วคราว ไม่ใช่ที่อยู่ถาวรของ topic ที่โตพอจะสกัดแล้ว) หลักการที่ว่าการ "rewrite เป็นคำตัวเอง" คือสิ่งที่ทำให้จำได้จริง ก็เป็นเหตุผลรองรับว่าทำไมกติกานี้ถึงบอกให้ "สังเคราะห์เป็นโน้ตใหม่" ไม่ใช่แค่ "ลิงก์กลับไปที่ session log ที่พูดถึง"

## Sources
- [[raw/2026-08-14-zettelkasten-ahrens-smart-notes]]

## เชื่อมโยง
- [[Knowledge Hub]]
- [[LLM Wiki Pattern]]
- [[Dispatch Console Build Kit - เสริมสุข]]

---
*หมายเหตุ: โน้ตนี้เป็น stub สรุปไว้ในตัว vault เพื่อให้ Graph View resolve ลิงก์จาก `CLAUDE.md` ได้ — ต้นฉบับจริงที่ Claude ใช้งานคือ native memory ที่ `~/.claude/projects/.../memory/feedback_vault_topic_notes.md` ไฟล์นี้ (ทั้งในตัว vault และ native memory) สร้างขึ้นใหม่ 2026-08-13 จากการสืบ git history เพราะไม่มีอยู่บนเครื่องบริษัทเลยมาก่อน — ถ้าเนื้อหาไม่ตรงกับที่จำได้จากเครื่องหลัก ให้แจ้งเพื่อแก้ไข*
