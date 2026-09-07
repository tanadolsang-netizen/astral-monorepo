#!/usr/bin/env python3
"""hive.py — Queen Bee orchestrator รวงผึ้ง ASTRAL

Queen Bee ทำหน้าที่:
- สั่งงาน Worker Bees (FORGE/ATLAS/ORACLE) ผ่าน command bus
- ตรวจสอบสุขภาพระบบ (health check)
- ฟื้นตัวอัตโนมัติเมื่อ component ตาย (self-heal)
- รายงานสถานะรวงทุกรอบ

ใช้ร่วมกับ command/dispatch.py (Pheromone trails)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────
COMMAND_DIR = Path("C:/AI/command")
QUEUE_DIR = COMMAND_DIR / "outbox"
STATE_FILE = COMMAND_DIR / "state" / "hive_state.json"
LOG_FILE = COMMAND_DIR / "state" / "hive_log.txt"

# ── Divisions ───────────────────────────────────────────────────
DIVISIONS = {
    "FORGE": {"port": 8000, "emoji": "🔨", "role": "backend engineering"},
    "ATLAS": {"port": 8001, "emoji": "🗺️", "role": "research & spec"},
    "ORACLE": {"port": 8002, "emoji": "🔮", "role": "QA & acceptance"},
}

# ── Helpers ─────────────────────────────────────────────────────
def now_ict() -> datetime:
    return datetime.now(timezone(timedelta(hours=7)))

def log(msg: str) -> None:
    ts = now_ict().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"cycles": 0, "last_health_check": None, "workers_alive": {}, "alerts": []}

def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

def run_cmd(cmd: list[str], timeout: int = 30, cwd: str | None = None) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd or "C:/AI")
        return r.returncode, (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"
    except Exception as e:
        return -1, str(e)

# ── Health Checks ───────────────────────────────────────────────
def check_port(port: int) -> bool:
    """เช็คว่า port เปิดอยู่ไหม"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            return s.connect_ex(("127.0.0.1", port)) == 0
    except Exception:
        return False

def check_disk_space() -> dict:
    """เช็คพื้นที่ดิสก์"""
    try:
        import shutil
        total, used, free = shutil.disk_usage("C:/AI")
        return {
            "total_gb": round(total / (1024**3), 1),
            "used_gb": round(used / (1024**3), 1),
            "free_gb": round(free / (1024**3), 1),
            "percent_used": round(used / total * 100, 1),
        }
    except Exception:
        return {}

def check_git_sync() -> dict:
    """เช็คว่า git sync ล่าสุดเมื่อไหร่"""
    code, output = run_cmd(["git", "-C", "C:/AI/NEW-AI-REBORN", "status", "--short"])
    if code == 0:
        changes = [l for l in output.split("\n") if l.strip()]
        return {"clean": len(changes) == 0, "pending_changes": len(changes)}
    return {"clean": False, "pending_changes": -1}

def check_tests() -> dict:
    """เช็ค test suite"""
    code, output = run_cmd(
        ["C:/AI/NEW-AI-REBORN/.venv/Scripts/python.exe", "-m", "pytest", "backend/tests/", "-q", "--tb=no"],
        timeout=120,
        cwd="C:/AI/NEW-AI-REBORN",
    )
    if code == 0:
        passed = 0
        for line in output.split("\n"):
            if "passed" in line:
                try:
                    passed = int(line.split("passed")[0].strip().split()[-1])
                except (ValueError, IndexError):
                    pass
        return {"ok": True, "passed": passed, "output_tail": output[-200:]}
    return {"ok": False, "passed": 0, "output_tail": output[-300:]}

# ── Self-Heal ───────────────────────────────────────────────────
def heal_forge() -> bool:
    """ฟื้นตัว FORGE — restart backend server"""
    log("🐝 FORGE กำลังจะตาย — พยายาม restart...")
    # หา process ที่ใช้ port 8000 แล้ว kill
    code, output = run_cmd(["netstat", "-ano"])
    if code == 0:
        for line in output.split("\n"):
            if ":8000" in line and "LISTENING" in line:
                pid = line.strip().split()[-1]
                run_cmd(["taskkill", "/F", "/PID", pid])
                log(f"  killed stale PID {pid}")
                time.sleep(1)
                break
    # restart
    code, output = run_cmd(
        ["start", "/B", "C:/AI/NEW-AI-REBORN/.venv/Scripts/python.exe", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"],
        timeout=10,
    )
    time.sleep(3)
    alive = check_port(8000)
    log(f"  FORGE restart: {'✅ alive' if alive else '❌ still dead'}")
    return alive

def heal_atlas() -> bool:
    """ฟื้นตัว ATLAS — แค่ verify ว่า research-astrology ยังอยู่"""
    atlas_dir = Path("C:/AI/research-astrology")
    if atlas_dir.exists():
        files = list(atlas_dir.glob("*.md"))
        log(f"  ATLAS: {len(files)} spec files present — ✅ healthy")
        return True
    else:
        log("  ATLAS: ❌ research-astrology directory missing!")
        return False

def heal_oracle() -> bool:
    """ฟื้นตัว ORACLE — verify test suite ยังรันได้"""
    result = check_tests()
    if result["ok"]:
        log(f"  ORACLE: ✅ tests green ({result['passed']} passed)")
    else:
        log(f"  ORACLE: ❌ tests failing — {result['output_tail'][:100]}")
    return result["ok"]

# ── Queen Bee Cycle ─────────────────────────────────────────────
def queen_cycle() -> dict:
    """รอบการทำงานของ Queen Bee"""
    state = load_state()
    state["cycles"] += 1
    cycle_num = state["cycles"]
    
    log(f"═══ Queen Bee Cycle #{cycle_num} ═══")
    
    # 1. Health check
    health = {
        "timestamp": now_ict().isoformat(),
        "ports": {},
        "disk": check_disk_space(),
        "git": check_git_sync(),
        "tests": check_tests(),
    }
    
    for div, info in DIVISIONS.items():
        alive = check_port(info["port"])
        health["ports"][div] = {"port": info["port"], "alive": alive}
        state["workers_alive"][div] = alive
        status = "✅" if alive else "❌"
        log(f"  {info['emoji']} {div} (port {info['port']}): {status}")
    
    # 2. Self-heal
    heal_needed = False
    for div, info in DIVISIONS.items():
        if not health["ports"][div]["alive"]:
            heal_needed = True
            if div == "FORGE":
                heal_forge()
            elif div == "ATLAS":
                heal_atlas()
            elif div == "ORACLE":
                heal_oracle()
    
    if not heal_needed:
        log("  🐝 All workers healthy — no healing needed")
    
    # 3. Disk alert
    if health["disk"].get("percent_used", 0) > 90:
        alert = f"🚨 Disk {health['disk']['percent_used']}% full!"
        state["alerts"].append(alert)
        log(f"  {alert}")
    
    # 4. Git alert
    if not health["git"]["clean"]:
        log(f"  📝 Git: {health['git']['pending_changes']} uncommitted changes")
    
    # 5. Test alert
    if not health["tests"]["ok"]:
        alert = "🚨 Test suite FAILING"
        state["alerts"].append(alert)
        log(f"  {alert}")
    
    state["last_health_check"] = health["timestamp"]
    save_state(state)
    
    return health

# ── CLI ─────────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="🐝 Queen Bee — ASTRAL Hive Orchestrator")
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    parser.add_argument("--loop", type=int, default=0, help="Run continuously (minutes interval)")
    parser.add_argument("--report", action="store_true", help="Print current hive status")
    args = parser.parse_args()
    
    if args.report:
        state = load_state()
        print(f"🐝 ASTRAL Hive State")
        print(f"   Cycles: {state['cycles']}")
        print(f"   Last check: {state['last_health_check']}")
        print(f"   Workers:")
        for div, alive in state.get("workers_alive", {}).items():
            print(f"     {div}: {'✅' if alive else '❌'}")
        if state.get("alerts"):
            print(f"   Recent alerts: {len(state['alerts'])}")
            for a in state["alerts"][-3:]:
                print(f"     {a}")
        return
    
    if args.once:
        queen_cycle()
        return
    
    if args.loop > 0:
        log(f"🐝 Queen Bee starting loop (every {args.loop} min)")
        while True:
            try:
                queen_cycle()
            except KeyboardInterrupt:
                log("🐝 Queen Bee stopped by user")
                break
            except Exception as e:
                log(f"🐝 Queen Bee error: {e}")
            time.sleep(args.loop * 60)
        return
    
    # default: one cycle
    queen_cycle()

if __name__ == "__main__":
    main()
