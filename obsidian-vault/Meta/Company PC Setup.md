# ตั้งเครื่องที่สอง (คอมบริษัท) ให้ sync กับเครื่องหลัก

ทำตามนี้ครั้งเดียวบนคอมบริษัท เพื่อให้ auto-sync (ดู [[CLAUDE]] หัวข้อ "Auto-sync across machines") ทำงานเหมือนกันทั้งสองเครื่อง

## สิ่งที่ต้องมีก่อน
- Git for Windows (เช็ค: เปิด terminal พิมพ์ `git --version`)
- VSCode + Claude Code extension

## ขั้นตอน

**1. สร้าง Personal Access Token (PAT) จาก GitHub** (ถ้ายังไม่มี — อันเดียวกับที่ใช้กับ Obsidian Git บนมือถือได้เลย ไม่ต้องสร้างใหม่)
- GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
- Scope: repo `tanadolsang-netizen/obsidian-vault-backup` เท่านั้น, permission: Contents (read/write)

**2. Clone repo**
```
git clone https://github.com/tanadolsang-netizen/obsidian-vault-backup.git "C:\Users\<ชื่อผู้ใช้>\Documents\Obsidian Vault"
```
ตอน prompt ถาม username/password: username = GitHub username, password = **PAT** (ไม่ใช่รหัสผ่านจริง) — Git Credential Manager จะจำให้อัตโนมัติหลังจากนั้น

**3. เปิดโฟลเดอร์นั้นใน VSCode → เปิด Claude Code**
- จะมี prompt ถาม "trust this folder's hooks?" (เพราะมี `.claude/settings.json`) → กด **trust/allow**
- ถ้าไม่มี prompt ขึ้นแปลว่า Claude Code เวอร์ชันนั้นอาจ trust อัตโนมัติ ให้ไปเช็คต่อข้อ 4 ได้เลย

**4. ทดสอบว่า sync ทำงานจริง**
- ให้ Claude Code ทำอะไรสักอย่างเล็กๆ (ถามคำถามธรรมดาก็พอ)
- เช็ค pull: ตอนเปิด session ควรเงียบ (สำเร็จ = ไม่มีอะไรขึ้น, ล้มเหลว = จะมี warning message)
- เช็ค push: หลัง Claude ตอบจบ รัน `git log --oneline -3` หรือเช็คหน้า GitHub repo ว่า commit ล่าสุดขึ้นไปจริงไหม

**5. ถ้า push ล้มเหลว (credential ใช้ไม่ได้)**
- รัน `git push` มือครั้งนึงในเทอร์มินัลธรรมดา (ไม่ใช่ผ่าน Claude) เพื่อให้ Windows Credential Manager เก็บ PAT ไว้ก่อน
- ถ้ายังไม่ได้: เช็คว่า Git Credential Manager ติดตั้งมาด้วยไหม (`git credential-manager --version`) — บาง corporate build ของ Git for Windows ตัดออก ต้องขอ IT ติดตั้งเพิ่ม

**6. (ถ้าต้องการ) Desktop shortcut เปิด VSCode เข้า vault นี้เต็มจอ + จำ layout ไว้เสมอ**

ทำแล้วบนคอมบริษัท (2026-08-13) ผลลัพธ์: ไอคอนบน Desktop เปิด VSCode พาเข้าโฟลเดอร์ vault ทันที เต็มจอทุกครั้ง และ panel/sidebar/layout ที่เปิดค้างไว้ครั้งก่อนจะกลับมาเหมือนเดิม

Username ของ 2 เครื่อง (สำหรับอ้างอิง): เครื่องที่บ้าน = `Admin`, เครื่องบริษัทนี้ = `70098372`

สคริปต์ด้านล่างใช้ `$env:USERPROFILE` / `$env:LOCALAPPDATA` แทนการเขียน path ตรงๆ — **copy-paste รันได้เลยทั้ง 2 เครื่องโดยไม่ต้องแก้อะไร** เพราะ env var จะ resolve เป็นของเครื่องนั้นเองอัตโนมัติ:

```powershell
$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Obsidian Vault (VSCode).lnk")
$shortcut.TargetPath = "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe"
$shortcut.Arguments = "--maximized `"$env:USERPROFILE\Documents\Obsidian Vault`""
$shortcut.WorkingDirectory = "$env:USERPROFILE\Documents\Obsidian Vault"
$shortcut.IconLocation = "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe,0"
$shortcut.Description = "Open Obsidian Vault project in VSCode, maximized"
$shortcut.Save()
```

เพิ่ม 2 บรรทัดนี้ใน VSCode user settings (`%APPDATA%\Code\User\settings.json`) ให้จำ window state/layout ไว้เสมอ:

```json
"window.restoreWindows": "all",
"window.newWindowDimensions": "maximized"
```

หมายเหตุ: shortcut + user settings เป็น local เฉพาะเครื่อง **ไม่ sync ผ่าน git** (อยู่นอก repo ทั้งคู่ — `Desktop\*.lnk` และ `%APPDATA%\Code\User\`) ต้องทำซ้ำเองทุกเครื่องที่ต้องการ

**เทียบกับแนวทางอื่น (2026-08-14):** มีบทความ [[raw/2026-08-14-syncing-claude-code-multiple-machines|steeman.be]] ที่ sync ทั้ง environment ของ Claude Code (NAS symlink + Syncthing) ข้ามเครื่อง — หนักกว่าที่ทำที่นี่มาก และแก้ปัญหาคนละระดับ (sync settings/plugins/project state ทั้งหมด ไม่ใช่แค่ vault นี้) ไม่ได้ใช้แนวทางนั้น เพราะสองเครื่องนี้ตั้ง global config แยกกันเองอยู่แล้วและ vault ใช้ git ธรรมดาก็พอ แต่บทความเตือนเรื่อง **hardcoded path พังเมื่อ username ต่างเครื่องไม่เหมือนกัน** — ตรงกับสถานการณ์นี้เป๊ะ (`Admin` vs `70098372`) และ script shortcut ด้านบนที่ใช้ `$env:USERPROFILE`/`$env:LOCALAPPDATA` แทน path ตรงๆ ก็คือวิธีเลี่ยงปัญหานั้นอยู่แล้ว — ยืนยันว่าถูกทางแล้ว ไม่ต้องแก้อะไรเพิ่ม

## ข้อจำกัดที่แก้จากเครื่องนี้ไม่ได้
- ถ้า IT บล็อกการเข้าถึง github.com จากเครื่องบริษัท (firewall/proxy policy) ต้องขอ exception เอง
- ถ้าบริษัทบล็อกการติดตั้ง VSCode extension เอง (managed device) ต้องขอสิทธิ์ก่อน

## Sources
- [[raw/2026-08-14-syncing-claude-code-multiple-machines]] — แนวทาง sync Claude Code ข้ามเครื่องแบบหนัก (NAS + Syncthing) ที่ไม่ได้ใช้ที่นี่ แต่ช่วยยืนยันจุดออกแบบเรื่อง path ด้านบน

## เชื่อมโยง
- [[CLAUDE]]
- [[Knowledge Hub]]
