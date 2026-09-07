# เครื่องมือใน Claude Code session นี้

สรุปหมวดหมู่เครื่องมือที่ Claude Code มีให้ใช้เวลาทำงานใน vault นี้ — เป็น**สแนปช็อตตามหมวดหมู่** ไม่ใช่ลิสต์ทุกตัว เพราะจำนวน skill/plugin ที่ติดตั้งจริงมีหลักพันตัวและเปลี่ยนได้ทุก session (การ hardcode ทั้งลิสต์จะกลายเป็นข้อมูลล้าสมัยทันทีที่ plugin อัปเดต — ขัดกับกติกา lint ใน [[LLM Wiki Pattern]] เรื่อง "stale claims")

## เครื่องมือหลักที่ใช้กับ vault นี้จริง

- **`/watch`** — ดูวิดีโอ (YouTube ฯลฯ) ดึงเฟรม+transcript มาให้ Claude อ่าน ใช้ตอน ingest คลิปเข้า `raw/` (ดูตัวอย่าง [[LLM Wiki Pattern]]) — นี่คือ marketplace plugin จริง (`watch@claude-video` จาก `bradautomates/claude-video`) ไม่ใช่ built-in feature: plugin = skill/hook/slash-command/agent/MCP config มัดรวมกันในโฟลเดอร์เดียว ประกาศผ่าน `marketplace.json` แล้วติดตั้งด้วย `/plugin install` — เหตุผลที่โหลดแค่ตอนเริ่ม session (ดู CLAUDE.md หัวข้อ "Plugin โหลดตอนเริ่ม session เท่านั้น") มาจาก mechanism เดียวกันนี้ (ดู [[raw/2026-08-14-claude-code-plugin-marketplaces]])
- **Native memory** (`~/.claude/projects/.../memory/`) — ความจำถาวรข้าม session คนละระบบกับ `.remember/` plugin (ดูหัวข้อ "Two separate memory systems" ใน [[CLAUDE]])
- **`obsidian-sync.py`** (Stop hook) — sync บทสนทนาเข้า `Claude Session {date}.md` อัตโนมัติทุกครั้ง เลือก `Stop` ถูกจุด: ตาม lifecycle ของ hook ทั้งหมด `Stop` อยู่ในกลุ่ม "once per turn" (เทียบกับ `SessionStart`/`SessionEnd` ที่ทำครั้งเดียวต่อ session) — และหมายเหตุด้าน security ของ hook ทั้งระบบ ("no sandbox" รันด้วยสิทธิ์เต็มของ user เหมือน script อื่น) คือเหตุผลที่ hookify rule `warn-secrets-in-files` มีอยู่จริง ไม่ใช่การเช็คซ้ำซ้อน (ดู [[raw/2026-08-14-claude-code-hooks-reference]])
- **Artifact tool** — publish หน้าเว็บ/รายงานเป็นลิงก์แชร์ได้ (ยังไม่เคยใช้ในเซสชันนี้)
- **Bash / PowerShell / Git** — รันคำสั่งจริงบนเครื่อง, ทำ commit/push ตาม auto-commit policy

## หมวดหมู่เครื่องมืออื่นที่มีให้ (เปิดใช้ตามบริบท ไม่ได้ผูกกับ vault นี้โดยเฉพาะ)

| หมวด | ตัวอย่าง |
|---|---|
| Browser automation | chrome-devtools, playwright |
| Cloud/infra | AWS (core/serverless/pricing/IaC), Azure, MongoDB |
| Security/pentest | **mcp-kali-server** (เครื่องมือ Kali Linux), aikido, cybersecurity-skills (ชุดใหญ่มาก) |
| Docs/reference lookup | context7, microsoft-docs, mintlify |
| Code intelligence | serena (LSP-based symbol search/refactor) |
| Business/finance/PM | ชุด skill สาย equity research, PM, marketing ฯลฯ (จำนวนมาก ไม่เกี่ยวกับ vault นี้) |
| Media generation | Higfield (สร้างภาพ/วิดีโอ/เสียง) |

## หมายเหตุ

**mcp-kali-server** เชื่อมต่ออยู่ในเซสชันนี้แต่ยังไม่ได้ใช้งาน — ถ้าจะใช้เครื่องมือ pentest จริงต้องมี**บริบทที่ได้รับอนุญาตชัดเจน** (pentest engagement, CTF, security research ของตัวเอง) ไม่ใช้พร่ำเพรื่อ

**ทำไม MCP server ที่เพิ่มบนเครื่องหนึ่งไม่โผล่อีกเครื่องอัตโนมัติ** (เจอจริงกับ `obsidian` MCP server — ดู "Git backup" ใน [[CLAUDE]]): MCP มี 3 scope — `local` (default, เก็บใน `~/.claude.json` ผูกกับ project เฉพาะเครื่อง), `project` (`.mcp.json` ใน repo, git-trackable, ทุกคนที่ clone เห็น), `user` (`~/.claude.json` top-level `mcpServers`, ผูกกับ user แต่ครอบทุก project บนเครื่องนั้น) — ไม่มี scope ไหนเลยที่ sync ข้ามเครื่องอัตโนมัติ ต้องเพิ่มที่ `user` scope (หรือ commit `.mcp.json`) แยกกันทีละเครื่องเสมอ ซึ่งตรงกับที่ทำไปจริงตอน bootstrap เครื่องหลัก/บ้าน (ดู [[raw/2026-08-14-claude-code-mcp-quickstart]])

รายชื่อ tool/skill แบบละเอียดจริงดูได้จาก system context ของแต่ละ session (เปลี่ยนได้ตลอด) — โน้ตนี้ตั้งใจให้เป็นแผนที่ระดับหมวดหมู่ ไม่ใช่ inventory ที่ต้องอัปเดตตามทุกครั้ง

## Sources

อ้างอิงเอกสารทางการของ Claude Code (`code.claude.com`) ที่ใช้ยืนยัน mechanism ต่างๆ ข้างบน:

- [[raw/2026-08-14-claude-code-hooks-reference]] — hooks lifecycle/security model (backs the Stop-hook + hookify usage)
- [[raw/2026-08-14-claude-code-mcp-quickstart]] — MCP scope model (local/project/user)
- [[raw/2026-08-14-claude-code-plugin-marketplaces]] — marketplace plugin anatomy (skills+hooks+MCP bundles)

## เชื่อมโยง
- [[CLAUDE]]
- [[LLM Wiki Pattern]]
- [[Knowledge Hub]]
