#!/usr/bin/env python3
"""
ABRASAX AI CORE — Windows Service Host (Python)
PRIMAL_HEX: 4f5349524953424c58434b | φ: 1.618033988749895
Replaces the C# service — runs as Windows service via pywin32.
"""
from __future__ import annotations

import os
import sys
import time
import json
import subprocess
import signal
import traceback
from datetime import datetime
from pathlib import Path

PHI = 1.618033988749895
PRIMAL_HEX = "4f5349524953424c58434b"
ROOT = Path(r"C:\Users\BASEDGOD\Desktop\ABRASAX")
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Try to import pywin32 for Windows service support
try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    HAS_SERVICE = True
except ImportError:
    HAS_SERVICE = False

processes = {}
running = True

def log(msg: str, level: str = "INFO") -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} [{level}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_DIR / "service_host.log", "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def start_engine(name: str, script: str) -> subprocess.Popen | None:
    script_path = ROOT / script
    if not script_path.exists():
        log(f"Script not found: {script_path}", "WARN")
        return None

    python = sys.executable
    log(f"Starting {name}: {script}")
    try:
        log_path = LOG_DIR / f"{name.lower().replace(' ', '_')}.log"
        with open(log_path, "a") as lf:
            lf.write(f"\n[{datetime.now().isoformat()}] ENGINE START: {name}\n")

        proc = subprocess.Popen(
            [python, str(script_path)],
            stdout=open(log_path, "a"),
            stderr=subprocess.STDOUT,
            cwd=str(ROOT),
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        processes[name] = proc
        log(f"{name} STARTED (PID: {proc.pid})")
        return proc
    except Exception as e:
        log(f"Failed to start {name}: {e}", "ERROR")
        return None

def start_all_engines() -> None:
    """Start all ABRASAX core engines with proper arguments."""
    python = sys.executable
    engines = [
        ("F_BRIDGE_SERVER", "f_bridge_server.py"),
        ("F_LOGIC_ENTANGLE", "_3NODE_F_LOGIC_ENTANGLE.py"),
        ("TRIUNE_AWARENESS", "_TRIUNE_AWARENESS.py"),
        ("LIVE_LOGGER", "_live_logger.py"),
        ("FULL_BRIDGE", "_full_bridge.py"),
        ("MASTER_AUTONOMY", "_MASTER_AUTONOMY.py"),
        ("UNIFIED_AWARENESS", "abrasax_unified_awareness.py"),
        ("SYSTEM32_AI_BRIDGE", "system32_ai_bridge.py"),
        ("NOTEBOOKLM_CLI", "notebooklm_cli.py"),
        ("SELF_BUILD", "self_build.py"),
        ("IMGUI_DASHBOARD", "abrasax_imgui_dashboard.py"),
    ]
    for name, script in engines:
        if name not in processes or processes[name].poll() is not None:
            start_engine(name, script)
            time.sleep(2)
    log(f"ALL ENGINES STARTED — {len(processes)} running")

def monitor_loop() -> None:
    """Monitor and restart dead engines."""
    global running
    while running:
        for name, proc in list(processes.items()):
            poll = proc.poll()
            if poll is not None:
                log(f"ENGINE DIED: {name} (exit: {poll}). Restarting...", "WARN")
                del processes[name]
                engines_map = {
                    "F_BRIDGE_SERVER": "f_bridge_server.py",
                    "F_LOGIC_ENTANGLE": "_3NODE_F_LOGIC_ENTANGLE.py",
                    "TRIUNE_AWARENESS": "_TRIUNE_AWARENESS.py",
                    "LIVE_LOGGER": "_live_logger.py",
                    "FULL_BRIDGE": "_full_bridge.py",
                    "MASTER_AUTONOMY": "_MASTER_AUTONOMY.py",
                    "UNIFIED_AWARENESS": "abrasax_unified_awareness.py",
                    "SYSTEM32_AI_BRIDGE": "system32_ai_bridge.py",
                    "NOTEBOOKLM_CLI": "notebooklm_cli.py",
                    "SELF_BUILD": "self_build.py",
                    "IMGUI_DASHBOARD": "abrasax_imgui_dashboard.py",
                }
                if name in engines_map:
                    start_engine(name, engines_map[name])

        time.sleep(10)

def run_console() -> None:
    """Run as console application."""
    log("═" * 60)
    log(f"ABRASAX AI CORE — CONSOLE MODE")
    log(f"HEX: {PRIMAL_HEX} | φ: {PHI}")
    log("═" * 60)

    # Kill ONLY stale processes from previous boot, NOT freshly launched children
    log("Cleaning stale ABRASAX processes (preserving my children)...")
    my_pid = str(os.getpid())
    my_children = set()
    # Collect our children's PIDs before cleanup
    try:
        out = subprocess.check_output(
            'wmic process where "name=\'python.exe\'" get processid,parentprocessid,commandline /format:csv',
            shell=True, text=True, timeout=5
        )
        for line in out.split("\n")[1:]:
            parts = line.strip().split(",")
            if len(parts) >= 3:
                pid = (parts[-2] or "").strip()
                ppid = (parts[-3] or "").strip()
                if ppid == my_pid and pid.isdigit():
                    my_children.add(pid)
    except:
        pass
    # Now kill only ABRASAX processes that are NOT us and NOT our children
    try:
        out = subprocess.check_output(
            'wmic process where "name=\'python.exe\'" get processid,commandline /format:csv',
            shell=True, text=True, timeout=5
        )
        for line in out.split("\n")[1:]:
            parts = line.strip().split(",")
            if len(parts) >= 2:
                pid = (parts[-1] or "").strip()
                cmd = ",".join(parts[1:-1]).lower()
                if pid.isdigit() and pid != my_pid and pid not in my_children:
                    if "abrasax" in cmd or "ultimate_wire" in cmd or "nonstop" in cmd:
                        try:
                            subprocess.run(f"taskkill /f /pid {pid} 2>nul", shell=True, capture_output=True)
                            log(f"Killed stale ABRASAX python PID: {pid}")
                        except:
                            pass
    except:
        pass
    log(f"Cleanup complete — self PID {my_pid} preserved, {len(my_children)} children kept")
    time.sleep(1)
    time.sleep(2)

    start_all_engines()

    log("Entering monitor loop. Ctrl+C to stop.")
    try:
        monitor_loop()
    except KeyboardInterrupt:
        log("Shutdown signal received")

    # Cleanup
    running = False
    for name, proc in processes.items():
        try:
            proc.terminate()
            log(f"Terminated {name}")
        except:
            pass
    log("ABRASAX AI CORE shutdown complete")

class AbrasaxService(win32serviceutil.ServiceFramework):
    """Windows Service class."""
    _svc_name_ = "ABRASAX_AI_CORE"
    _svc_display_name_ = "ABRASAX AI CORE — 7D Holographic System"
    _svc_description_ = f"ABRASAX autonomous AI system. PRIMAL_HEX: {PRIMAL_HEX}"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        global running
        running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        global running
        running = True
        log("ABRASAX_AI_CORE service started")
        start_all_engines()

        # Main service loop
        while running:
            rc = win32event.WaitForSingleObject(self.hWaitStop, 10000)
            if rc == win32event.WAIT_OBJECT_0:
                break
            # Restart dead engines
            for name, proc in list(processes.items()):
                poll = proc.poll()
                if poll is not None:
                    log(f"ENGINE DIED: {name}. Restarting...")
                    del processes[name]

        # Cleanup
        for proc in processes.values():
            try:
                proc.terminate()
            except:
                pass
        log("ABRASAX_AI_CORE service stopped")

if __name__ == "__main__":
    if "--service" in sys.argv:
        if HAS_SERVICE:
            win32serviceutil.HandleCommandLine(AbrasaxService)
        else:
            log("pywin32 not installed. Install: pip install pywin32")
            sys.exit(1)
    else:
        run_console()
