#!/usr/bin/env python3
"""Command Bus v2 — C:/AI/command/

RULES:
  - Scratch files (temp json/txt/test scripts) NEVER go on Desktop -> use C:/AI/workspace-scratch/

COMMAND (เซสชันผู้บัญชาการ) ยิงคำสั่ง → แต่ละแผนกรับ-ทำ-รายงานผล

v2: queue หลายช่องต่อแผนก + priority + STATE.md integration

Usage:
  python dispatch.py send FORGE "หัวข้อ" "รายละเอียด/DoD" [high|normal|low]
  python dispatch.py board                    # ภาพรวมคิว+สถานะทุกแผนก
  python dispatch.py next FORGE               # งานถัดไปของแผนก (pop จากคิว)
  python dispatch.py ack FORGE <id-prefix>    # รับงาน (status -> ACKED)
  python dispatch.py done FORGE <id-prefix> "ผลสรุป"   # จบงาน + เขียน report
  python dispatch.py report FORGE "<ข้อความ>" # รายงานอิสระ (ไม่ผูก task)
  python dispatch.py clear FORGE [id-prefix]  # ล้างงานจบแล้ว/งานเฉพาะ

รับได้ทั้ง FORGE/ATLAS/ORACLE และ S1/S2/S3
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QUEUE_DIR = ROOT / "outbox"
INBOX = ROOT / "inbox"
STATE_DIR = ROOT / "state"
ALIAS = {"FORGE": "S1", "ATLAS": "S2", "ORACLE": "S3",
         "S1": "S1", "S2": "S2", "S3": "S3"}
LABEL = {"S1": "FORGE", "S2": "ATLAS", "S3": "ORACLE"}
PRIO_ORDER = {"high": 0, "normal": 1, "low": 2}


def canon(name: str) -> str:
    return ALIAS.get(name.upper().strip(), "")


def _qpath(div: str) -> Path:
    return QUEUE_DIR / f"{div}.queue.json"


def _read(p: Path):
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _write(p: Path, data) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _sorted_queue(items: list) -> list:
    return sorted(items, key=lambda t: (t.get("status") == "ACKED",
                                        PRIO_ORDER.get(t.get("priority"), 1),
                                        t["id"]))


def _find(items: list, prefix: str):
    for i, t in enumerate(items):
        if t["id"].startswith(prefix):
            return i, t
    return -1, None


def main() -> None:
    args = sys.argv[1:]
    cmd = args[0].lower() if args else ""

    if cmd == "send":
        div, title = canon(args[1]), args[2]
        if not div:
            print(f"ไม่รู้จักแผนก '{args[1]}' — ใช้ FORGE/ATLAS/ORACLE"); return
        body = args[3] if len(args) > 4 else ""
        prio = args[4].lower() if len(args) > 4 else "normal"
        items = _read(_qpath(div))
        task = {
            "id": time.strftime("%Y%m%d-%H%M%S"),
            "title": title, "body": body, "priority": prio,
            "status": "PENDING", "issued_by": "COMMAND",
            "issued_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        items.append(task)
        _write(_qpath(div), _sorted_queue(items))
        print(f"➤ {LABEL[div]} รับคำสั่ง #{task['id']} [{prio}] {title}")

    elif cmd == "board":
        for d in ("S1", "S2", "S3"):
            items = _sorted_queue(_read(_qpath(d)))
            pend = sum(1 for t in items if t["status"] == "PENDING")
            acked = sum(1 for t in items if t["status"] == "ACKED")
            rep = (INBOX / f"{d}.md").exists()
            st = ""
            sp = STATE_DIR / f"{d}.md"
            if sp.exists():
                first = sp.read_text(encoding="utf-8").splitlines()
                st = next((l for l in first if l.startswith(">")), "")
            line = f"[{LABEL[d]}·{d}] คิว {len(items)} (รอ {pend} · ทำอยู่ {acked})"
            line += f" | รายงาน: {'✓' if rep else '—'}"
            if st:
                line += f"\n    {st}"
            print(line)

    elif cmd == "next":
        div = canon(args[1])
        items = _sorted_queue(_read(_qpath(div)))
        nxt = next((t for t in items if t["status"] != "DONE"), None)
        print(json.dumps(nxt, ensure_ascii=False, indent=2) if nxt
              else f"{LABEL[div]}: คิวว่าง")

    elif cmd == "ack":
        div = canon(args[1])
        items = _read(_qpath(div))
        legacy_path = QUEUE_DIR / f"{div}.json"
        if len(args) > 2:
            i, t = _find(items, args[2])
            if not t:
                print(f"ไม่พบงาน id-prefix '{args[2]}'"); return
        else:
            # legacy protocol (no id): ack oldest PENDING; migrate legacy file if present
            t = next((x for x in _sorted_queue(items) if x.get("status") == "PENDING"), None)
            if t:
                i = items.index(t)
            elif legacy_path.exists():
                try:
                    t = json.loads(legacy_path.read_text(encoding="utf-8"))
                    items.append(t)
                    i = len(items) - 1
                    legacy_path.unlink()
                except Exception:
                    t = None
            if not t:
                print(f"{LABEL[div]}: ไม่มีคำสั่งรอรับ"); return
        t["status"] = "ACKED"
        t["acked_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{LABEL[div]} รับงาน #{t['id']} — {t['title']}")
        _write(_qpath(div), _sorted_queue(items))

    elif cmd == "done":
        div = canon(args[1])
        items = _read(_qpath(div))
        i, t = _find(items, args[2])
        if not t:
            print(f"ไม่พบงาน id-prefix '{args[2]}'"); return
        t["status"] = "DONE"
        t["result"] = args[3] if len(args) > 3 else ""
        INBOX.mkdir(parents=True, exist_ok=True)
        with open(INBOX / f"{div}.md", "a", encoding="utf-8") as f:
            f.write(f"\n## DONE #{t['id']} — {t['title']}\n{t['result']}\n")
        print(f"{LABEL[div]} จบงาน #{t['id']} → inbox/{div}.md")
        _write(_qpath(div), _sorted_queue(items))

    elif cmd == "report":
        div, text = canon(args[1]), args[2]
        INBOX.mkdir(parents=True, exist_ok=True)
        with open(INBOX / f"{div}.md", "a", encoding="utf-8") as f:
            f.write(f"\n## REPORT — {time.strftime('%Y-%m-%d %H:%M')}\n{text}\n")
        print(f"{LABEL[div]} รายงาน → inbox/{div}.md")

    elif cmd == "clear":
        div = canon(args[1])
        p = _qpath(div)
        if len(args) > 2:
            items = _read(p)
            i, t = _find(items, args[2])
            if t:
                items.pop(i); _write(p, items)
                print(f"ลบงาน #{t['id']} แล้ว")
        else:
            keep = [t for t in _read(p) if t["status"] != "DONE"]
            _write(p, keep)
            print(f"{LABEL[div]}: เก็บเฉพาะงานค้าง ({len(keep)} งาน)")

    else:
        print(__doc__)


if __name__ == "__main__":
    main()
