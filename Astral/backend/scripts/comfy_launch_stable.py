"""Stable ComfyUI launcher with auto-restart watchdog (Hermes self-upgrade).

Problem fixed: `comfy launch --background` and bare `main.py` kept dying when the
spawning shell exited or on VRAM hiccup -> WinError 10061. This script starts
ComfyUI as a detached subprocess and restarts it if it stops responding, so the
image-generation pipeline is reliable.

Run:  uv run python scripts/comfy_launch_stable.py
Stop:  Ctrl+C (kills the watchdog + child).
"""
import subprocess, time, urllib.request, sys, os
from pathlib import Path

COMFY = Path.home() / "Documents" / "comfy" / "ComfyUI"
PY = COMFY / ".venv" / "Scripts" / "python.exe"
URL = "http://127.0.0.1:8188/system_stats"
ARGS = [str(PY), str(COMFY / "main.py"), "--listen", "127.0.0.1",
        "--port", "8188", "--lowvram", "--preview-method", "none"]


def up() -> bool:
    try:
        urllib.request.urlopen(URL, timeout=4).read(80)
        return True
    except Exception:
        return False


def main() -> None:
    proc = None
    while True:
        if proc is None or proc.poll() is not None:
            if proc is not None:
                print(f"[watchdog] child exited ({proc.returncode}); restarting...")
            print("[watchdog] launching ComfyUI...")
            proc = subprocess.Popen(ARGS, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL,
                                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
            # give it time to boot
            for _ in range(40):
                time.sleep(3)
                if up():
                    print(f"[watchdog] ComfyUI UP (pid {proc.pid})")
                    break
            else:
                print("[watchdog] still not up after 2 min; will retry")
        time.sleep(15)
        if not up():
            print("[watchdog] health check failed; killing and restarting")
            try:
                proc.kill()
            except Exception:
                pass
            proc = None


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[watchdog] stopped by user")
        sys.exit(0)
