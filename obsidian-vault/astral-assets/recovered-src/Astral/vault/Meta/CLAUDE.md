# CLAUDE.md

## ปิดการใช้งาน Remember plugin

Plugin `remember` ปิดแล้ว (2026-08-12) — ซ้ำซ้อนกับ Stop hook `obsidian-sync.py` ด้านล่าง (ฟรี, ไม่เรียก LLM) `.remember/` ถูกลบจาก repo แล้ว (กู้จาก git history ได้ถ้าจะเปิดใหม่) **อย่า** เปิดใช้ซ้ำหรือลด threshold ใน `.remember/config.json` จนกว่าผู้ใช้จะขอเอง

## ความจำข้ามเซสชันตัวจริง: `obsidian-sync.py` (Stop hook)

Global hook (`~/.claude/hooks/obsidian-sync.py`) ทำงานทุก Stop ใน *ทุก* โปรเจกต์ ต่อท้ายบทสนทนา (truncate ไม่สรุปด้วย LLM) เข้า `Claude Session {date}.md` — เช็คที่นี่ก่อนเพื่อความต่อเนื่อง/ประวัติ

## ระบบความจำ 2 ระบบที่แยกกัน

1. **Native auto-memory** — `~/.claude/projects/<slug>/memory/MEMORY.md` เก็บข้อเท็จจริงถาวร ดูแลโดย Claude ข้าม session
2. **Plugin `remember`** (ปิดอยู่) — `.remember/` เก็บ log บทสนทนาดิบรายวัน

ไม่ sync กัน คนละจุดประสงค์

## นโยบาย Auto-commit (2026-08-12)

Commit ทุกการเปลี่ยนแปลงใน vault นี้ได้เลยไม่ต้องถามก่อน (ยกเว้นกฎทั่วไปเฉพาะโปรเจกต์นี้) — รายงานทีหลังว่า commit อะไรไปบ้าง ต้อง: ไม่มี secret, ใช้ conventional-commits format (`<type>(<scope>): <summary>`, บังคับโดย hook `pro-workflow` commit-validate), และยังต้องถามก่อน action ทำลายล้าง (force-push, เขียน history ใหม่)

**บั๊ก commit-validate:** อย่าใช้ `git commit -m "$(cat <<'EOF' ... EOF)"` — regex ของ hook จับ `-m` ตัวแรกแบบ raw ทำให้ parse พัง ใช้ `-m` หลายตัวแทน (`-m "type(scope): summary" -m "body"`)

**`git stash drop`/`clear` โดน hook `git-blast-radius` บล็อกเสมอ** (ตั้งใจ, safety guard) — อย่าพยายามข้าม ปล่อย stash ทิ้งไว้เฉยๆ ไม่มีผลเสีย แจ้งผู้ใช้แทน

**Git identity:** ทุกเครื่องต้องตั้ง `git config --global user.name`/`user.email` ก่อนเชื่อ "pushed" จาก sync script ใดๆ — sync script (`claude-config-sync.py`, `build-kit-sync.py`) เช็ค exit code ของ `git commit` ก่อน push แล้ว (แก้ 2026-08-14) แต่ sync script ใหม่ที่เขียนเองต้องเช็ค exit code ทุก git command ด้วยเสมอ ไม่ใช่แค่ push ตัวสุดท้าย

## Git backup (2026-08-12)

Vault เป็น git repo, GitHub remote private: `github.com/tanadolsang-netizen/obsidian-vault-backup` ใช้ `gh` CLI แบบ portable zip ที่ `~/AppData/Local/gh-cli/bin/gh.exe` (ถ้าต้องลงใหม่ ใช้ portable zip ไม่ใช่ winget) เข้าจากมือถือผ่าน Obsidian Git plugin ด้วย Personal Access Token

### Auto-sync ข้ามเครื่อง

Hook 2 ตัวใน `.claude/settings.json` (commit แล้ว, sync ทั้งสองเครื่อง):

- **SessionStart** → `git pull --ff-only` — fail ชัดเจนถ้า history แยกกัน (ไม่ auto-merge เงียบๆ)
- **Stop** → `git push origin master`

ต้องมี `gh` authenticated ในแต่ละเครื่อง hook ที่เพิ่มกลาง session ต้อง restart ถึงโหลด

**คู่มือแก้ conflict** เมื่อ `--ff-only` fail:

1. `git status` ก่อนเสมอ — ห้าม `reset`/`checkout -- .`/`clean`
2. `git pull` ธรรมดา (merge จริง)
3. ถ้ามี conflict marker: อ่านทั้งสองฝั่ง รวมเนื้อหาที่ตั้งใจไว้ ลบ marker, `git add` + commit แบบ merge commit (ไม่ใช้ `--no-verify`)
4. push — Stop hook จัดการให้

**ช่องโหว่ที่รู้:** กฎ auto-archive raw/ กับคู่มือนี้เป็นแค่คำสั่ง ไม่บังคับด้วย hook — Lint pass ควรเช็คไขว้ session-log กับ `raw/` ว่ามีช่องโหว่ไหม

### `obsidian-sync.py` — git-track แล้ว

Script อยู่ที่ [`scripts/obsidian-sync.py`](scripts/obsidian-sync.py) (global hook เป็น per-machine, sync เข้า repo ไม่ได้โดยตรง)

**เครื่องใหม่ทุกเครื่อง:**

1. copy `scripts/obsidian-sync.py` → `~/.claude/hooks/obsidian-sync.py`
2. merge เข้า **global** `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      { "hooks": [ { "type": "command", "command": "python \"<path to>/.claude/hooks/obsidian-sync.py\"" } ] }
    ]
  }
}
```

1. แก้ `VAULT_DIR` ที่บนสุดของ script ถ้า path ต่างจากนี้

แก้ script นี้เมื่อไหร่ ให้อัปเดตสำเนาใน `scripts/` ใน commit เดียวกันเสมอ (ไม่มีอะไรบังคับอัตโนมัติ)

ทั้ง 2 เครื่อง (บริษัท + บ้าน) ตั้งค่าแล้ว รวม MCP server `obsidian` (`user` scope) — `mcp-kali-server` ตั้งค่าได้แค่เครื่องหลัก (ต่อ Kali VM local เท่านั้น เครื่องบริษัทไม่มีสิทธิ์ admin ตั้งเองไม่ได้)

### `claude-config-sync.py` — sync settings/native memory ข้ามเครื่อง

`~/.claude/settings.json` บาง key และ native memory ไม่ sync ข้ามเครื่องเอง เพราะอยู่นอก repo vault — แก้ด้วย repo แยก private ชื่อ `Privacy-` เก็บ:

- `settings.sync.json` — เฉพาะ key ที่ควรเหมือนกันทุกเครื่อง (`enabledPlugins`, `extraKnownMarketplaces`, `agentPushNotifEnabled`, `remoteControlAtStartup`, `language`, `autoMode`) **ไม่รวม** `hooks` (มี path เฉพาะเครื่อง)
- `projects/<slug>/memory/*.md`

Script `~/.claude/hooks/claude-config-sync.py` (สำรอง: [`scripts/claude-config-sync.py`](scripts/claude-config-sync.py)):

- **SessionStart** → `pull`: merge เฉพาะ key ที่กำหนด (dict merge key-level, list union — ไม่ overwrite ทั้งก้อน, ทดสอบแล้วจริง) เข้า settings.json จริง + copy memory files
- **Stop** → `push`: copy กลับเข้า repo sync, commit, push

**เครื่องใหม่ทุกเครื่อง:**

1. Copy `scripts/claude-config-sync.py` → `~/.claude/hooks/claude-config-sync.py`
2. `git clone https://github.com/tanadolsang-netizen/Privacy-.git ~/.claude-config-sync`
3. เพิ่ม hook เข้า **global** `~/.claude/settings.json` (merge เข้า `hooks` เดิม ไม่ทับ):

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "python \"<path>/.claude/hooks/claude-config-sync.py\" pull" } ] }
    ],
    "Stop": [
      { "hooks": [
        { "type": "command", "command": "python \"<path>/.claude/hooks/obsidian-sync.py\"" },
        { "type": "command", "command": "python \"<path>/.claude/hooks/claude-config-sync.py\" push" }
      ] }
    ]
  }
}
```

1. รัน `python ~/.claude/hooks/claude-config-sync.py pull` มือครั้งแรก (SessionStart hook ยังไม่ทำงานจนกว่าจะเปิด session ใหม่)

ทั้ง 2 เครื่องตั้งค่าแล้ว (`git clone` ของ private repo อาจโดน auto-mode classifier บล็อกรอบแรก ต้องยืนยันกับผู้ใช้)

### `build-kit-sync.py` และ `startup-check.py`

**`build-kit-sync.py`** ทำแบบเดียวกับ `claude-config-sync.py` แต่สำหรับ `~/Desktop/build_kit/` (โปรเจกต์ Dispatch Console คนละเรื่องกับ vault) ใช้ repo `Privacy-` เดียวกันแต่แยก **branch `build-kit`** (กัน content ปน) สคริปต์สำรองที่ `build_kit/build-kit-sync.py` (`REPO` path ใช้ `os.path.expanduser("~")` portable ข้ามเครื่องได้ตรงๆ)

เครื่องใหม่: `git clone -b build-kit https://github.com/tanadolsang-netizen/Privacy-.git ~/Desktop/build_kit` แล้ว copy script + เพิ่ม hook แบบเดียวกับข้างบน

**`startup-check.py`** (สำรอง: [`scripts/startup-check.py`](scripts/startup-check.py)) SessionStart hook ตัวสุดท้าย เช็คแล้วเงียบถ้าไม่มีปัญหา:

- ทั้ง 3 repo (vault, `claude-config-sync` master, `build_kit` build-kit) มี uncommitted change/behind origin ไหม
- plugin ใน `enabledPlugins` ติดตั้งจริงหรือยัง (`claude plugin list`)

**ไฟล์นี้ต้องแก้ `REPOS` dict ต่อเครื่อง** (hardcode path) ไม่ portable แบบ path เดียวกันหมด — ใส่ `encoding="utf-8", errors="replace"` ให้ `subprocess.run` ทุกจุด (Windows cp874 decode พังกับอักขระพิเศษจาก `claude plugin list`)

ทั้ง 2 เครื่องตั้งค่าแล้ว

### `omniroute-sync.py` — sync ข้อมูล OmniRoute ข้ามเครื่อง (2026-08-14)

OmniRoute (`omniroute` npm CLI, self-hosted AI gateway ดู [[OmniRoute — The Free AI Gateway]] ถ้ามี) เก็บ account/API key/session ไว้ที่ `~/.omniroute/` (`.env` มี `STORAGE_ENCRYPTION_KEY`, `storage.sqlite` เข้ารหัสด้วยคีย์นั้น) แต่ละเครื่องที่ลง `npm install -g omniroute` ครั้งแรกจะ **generate key สุ่มเองคนละตัว** — sync ไฟล์ข้ามเครื่องโดยไม่ sync key คู่กันจะ decrypt ไม่ได้เลย ต้อง sync ทั้งคู่พร้อมกันเสมอ

ทำแบบเดียวกับ `build-kit-sync.py`: turn `~/.omniroute/` เป็น git repo ในตัว (ไม่ใช่ mirror แยก) บน **branch `omniroute`** ของ repo `Privacy-` เดียวกัน `.gitignore` จำกัดให้ sync แค่ `.env` + `storage.sqlite` (ไม่เอา `db_backups/`, `logs/`, `server/`, หรือ `*.sqlite-wal`/`-shm` ที่เป็น journal ชั่วคราว) ก่อน push ทุกครั้งจะ `PRAGMA wal_checkpoint(TRUNCATE)` (sqlite3 stdlib) เพื่อ merge WAL เข้าไฟล์หลักก่อน ให้ไฟล์ที่ sync ไปสมบูรณ์ในตัวเอง สคริปต์สำรอง: [`scripts/omniroute-sync.py`](scripts/omniroute-sync.py)

**Bootstrap ครั้งแรกสำคัญมาก (ต่างจาก build-kit):** `~/.omniroute/` มีข้อมูลจริงอยู่ก่อนแล้วทั้ง 2 เครื่อง (ไม่ใช่โฟลเดอร์ว่างที่ clone ใส่ได้) เครื่องที่มี **account จริงที่ใช้งานอยู่** (ตอนนี้คือเครื่องบริษัท) ต้อง push ขึ้น branch `omniroute` เป็นเครื่องแรกเสมอ — เครื่องอื่นที่เพิ่งลงใหม่ (มี key/DB ว่างเปล่าที่เพิ่ง generate) ห้าม push ทับก่อน ให้ pull มารับของจริงแทน (ถ้า pull ครั้งแรกแล้ว `--ff-only` fail เพราะ history ไม่เกี่ยวกัน คือคาดหวังแล้ว — ลบ local commit ว่างๆ ทิ้ง แล้ว `git reset --hard origin/omniroute` แทนที่ด้วยของจริงได้เลย เพราะ local เป็นแค่ของว่างที่สร้างไว้ชั่วคราว)

**เครื่องใหม่ทุกเครื่อง:**

1. Copy `scripts/omniroute-sync.py` → `~/.claude/hooks/omniroute-sync.py`
2. `npm install -g omniroute@3.8.48` (เวอร์ชันที่เครื่องบ้าน+บริษัทใช้อยู่ตอนนี้ — เช็ค `omniroute --version` เทียบก่อนถ้าเวลาผ่านไปนาน เผื่อมีอัปเดต)
3. `cd ~/.omniroute && git init && git remote add origin https://github.com/tanadolsang-netizen/Privacy-.git && git fetch origin`
4. ถ้า branch `omniroute` มีอยู่แล้วบน remote (เครื่องอื่น bootstrap ไปแล้ว): `git checkout -b omniroute origin/omniroute` ทับข้อมูลเครื่องนี้ทิ้งเลย (ของว่างเปล่า ไม่มีอะไรเสีย) — **อย่า push ก่อน pull**
5. ถ้ายังไม่มี branch เลย (เครื่องแรกสุดที่ setup): `git checkout -b omniroute`, สร้าง `.gitignore` (`*` / `!.gitignore` / `!.env` / `!storage.sqlite`), commit, push เป็นเครื่องแรก
6. เพิ่ม hook เข้า **global** `~/.claude/settings.json` (merge เข้า `hooks.SessionStart`/`hooks.Stop` เดิม ไม่ทับ): `omniroute-sync.py pull` ใน SessionStart, `omniroute-sync.py push` ใน Stop

**Service (auto-start):** `omniroute autostart enable` ใช้ไม่ได้บน Windows จริง (ดูหัวข้อ ffmpeg/OmniRoute ด้านล่าง) ลองตั้ง **Windows Scheduled Task** ชื่อ `OmniRoute` (trigger: AtLogOn, รันผ่าน `powershell -WindowStyle Hidden -Command "Start-Process ... -WindowStyle Hidden"`) แต่ `Register-ScheduledTask` ต้อง elevate ผ่าน UAC prompt ซึ่งโดน cancel 2 รอบติด (2026-08-14) — **ยังไม่ได้ตั้ง** ใช้ **VSCode task ที่ sync มาอยู่แล้วแทนไปก่อน** (`.vscode/tasks.json`, `runOn: folderOpen`, ดูหัวข้อ "สิ่งที่พบจากการใช้งานจริงวันนี้" ในโน้ต OmniRoute ที่ยืนยันว่าใช้ได้จริงบนเครื่องบริษัท) ถ้าจะลอง Scheduled Task อีกครั้ง ต้องมีคนอยู่หน้าเครื่องกด UAC prompt จริงๆ ไม่ใช่ผ่าน background task

เครื่องบ้านตั้งค่า sync script + hook แล้ว (2026-08-14) แต่ **ยังไม่ push** (ข้อมูลว่างเปล่า รอ push จริงจากเครื่องบริษัทก่อน) เครื่องบริษัทยังไม่ได้ setup sync นี้เลย

## Claude Code plugins — แยกตามเครื่อง ไม่ sync กัน

Marketplace plugins อยู่ใน global `~/.claude/` ไม่เดินทางมากับ repo — เครื่องใหม่ที่ไม่มี `enabledPlugins`/`~/.claude/plugins/` เลย ต้องรัน:

```sh
claude plugin marketplace add bradautomates/claude-video
claude plugin install watch@claude-video
```

(`/plugin marketplace add` ใช้ไม่ได้ใน VSCode-extension environment — ใช้ `claude plugin ...` CLI ผ่าน Bash แทน)

**Plugin โหลดตอนเริ่ม session เท่านั้น** — ติดตั้งกลาง session ต้อง restart ก่อนใช้ได้

**เครื่องใหม่ทุกเครื่อง:** รัน `claude plugin list` เทียบกับเช็คลิสต์ด้านล่าง อัปเดตลิสต์ทุกครั้งที่ติดตั้ง/ถอด plugin

### เช็คลิสต์ Plugin ทั้ง 2 เครื่อง

- [x] `watch@claude-video` (marketplace: `bradautomates/claude-video`) — ให้ `/watch` (ดึงเฟรม+transcript วิดีโอ ใช้กับ `raw/`) ติดตั้งครบทั้ง 2 เครื่องแล้ว
- [x] `claude-real-video@claude-real-video` (marketplace: `HUANGCHIHHUNGLeo/claude-real-video`) — เพิ่มเติมจาก `watch`: speaker diarization, ค้นข้ามวิดีโอ (`crv-ask`) ติดตั้งครบทั้ง 2 เครื่องแล้ว **ยังไม่ทดสอบใช้งานจริง**

**ตั้งใจไม่ติดตั้ง:** `remember@claude-plugins-official` — ดูหัวข้อแรกของไฟล์นี้

**บั๊ก ffmpeg `-vsync` ซ้ำๆ:** ffmpeg 9.0+ เปลี่ยน `-vsync vfr` เป็น `-fps_mode vfr` — เครื่องมือ video/frame-extraction เก่าที่ hardcode `-vsync` จะพัง แก้โดยตรงในไฟล์ปลั๊กอิน (`~/.claude/plugins/cache/.../frames.py`, `.../claude_real_video/core.py` เป็นต้น) การแก้ไม่ได้อยู่ใน repo (plugin cache/pip site-packages ไม่ track) จะ**หายทุกครั้งที่ update plugin/pip package** และไม่ sync ข้ามเครื่อง — เจอ error `vsync` จาก ffmpeg ในเครื่องมือไหนก็ตาม ให้แก้แบบเดิมทันที ไม่ต้องสงสัยว่าเป็นปัญหาอื่น

## กฎ Hookify (2026-08-12)

กฎ 2 ตัวใน `.claude/hookify.*.local.md` (`event: file`, `action: warn`, จับ field `content` ครอบคลุมทั้ง `Write`/`Edit`):

- `warn-secrets-in-files` — ตรวจจับ private-key header / token (`ghp_`/`gho_`/AWS/`sk-`) ก่อนเขียนไฟล์
- `warn-pii-in-memory-files` — ตรวจจับอีเมลเขียนลง `.remember/*.md`

## ตัวช่วยด้านโหราศาสตร์ (2026-08-12)

`scripts/transit_now.py` คำนวณตำแหน่งดาวเคราะห์ปัจจุบัน (tropical + ไทย/Lahiri sidereal) ด้วย `skyfield` + JPL DE421 — รันด้วย `python3 scripts/transit_now.py` (ดาวน์โหลด `de421.bsp` ~17MB อัตโนมัติทุกครั้ง ไม่เก็บใน repo) ดู `[[user_astrology_interest]]`/`[[user_personality_natal]]` ใน native memory ว่าควรใช้กรอบนี้เมื่อไหร่

## LLM Wiki pattern (2026-08-12)

Vault นี้ใช้ pattern LLM Wiki ของ Andrej Karpathy — ดู [[LLM Wiki Pattern]] สรุปสั้น: `raw/` = แหล่งดิบยังไม่สังเคราะห์, [[Knowledge Hub]] = `index.md`, `git log` = `log.md` (ไม่แยกไฟล์ log ต่างหาก) Lint เป็นระยะ: orphan notes, claim เก่าขัดแย้งโน้ตใหม่, topic ที่ควรมีโน้ตของตัวเอง, แหล่งข้อมูลภายนอกที่พูดถึงแต่ไม่มี `raw/` ตรงกัน

**Auto-archive แหล่งข้อมูลดิบ:** ทุกครั้งที่บทสนทนาอ้างถึงข้อมูลภายนอก (URL/PDF/วิดีโอ/บทความ) บันทึกลง `raw/YYYY-MM-DD-short-slug.md` (frontmatter: `source_type`, `url`, `referenced_date`, `synthesized_into`) ก่อนหรือพร้อมกับเขียนโน้ต wiki — ดูฟอร์แมตที่ `raw/2026-08-12-llm-wiki-pattern-walkthrough.md`

**Auto-research เมื่อมี raw/data ใหม่:** กลับด้าน — มีเนื้อหาใหม่เข้า `raw/` หรือโน้ตใหม่ที่ยังไม่มี `raw/` รองรับ ให้ไป research หาแหล่งภายนอกเพิ่ม (เหมาะมอบ background agent) **กันวนซ้ำ:** เช็ค `ls raw/` ก่อนเสมอ, ทำแค่ 1 ชั้น ไม่ trigger รอบถัดไป

## เชื่อมโยง

- [[Knowledge Hub]]
