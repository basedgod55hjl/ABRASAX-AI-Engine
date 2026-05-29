#!/usr/bin/env python3
"""
ABRASAX FULL SYSTEM BRIDGE - Wires LM Studio + Rust Engine + Telegram + Web Tools
Non-stop automany: self-editing, tool-calling, multi-process reasoning
"""
import os
import sys
import json
import time
import subprocess
import threading
import queue
import signal
from datetime import datetime

# Paths
ABRASAX_ROOT = r"C:\Users\BASEDGOD\Desktop\ABRASAX"
BINARY = os.path.join(ABRASAX_ROOT, "abrasax_rs", "target", "release", "abrasax.exe")
MODEL_DIR = os.path.join(ABRASAX_ROOT, "abrasax_llm", "models", "gguf")
LM_STUDIO_MODEL = r"C:\Users\BASEDGOD\.lmstudio\models\lmstudio-community\DeepSeek-R1-0528-Qwen3-8B-GGUF\DeepSeek-R1-0528-Qwen3-8B-Q3_K_L.gguf"
LM_API = "http://127.0.0.1:1234"
LM_KEY = "2HYgAvh9qhaNzERK/4bD+KC2"

running = True
processes = {}
log_queues = {}


def log(msg, tag="BRIDGE"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{tag}] {msg}")
    sys.stdout.flush()


def get_vram():
    try:
        out = subprocess.check_output(
            "nvidia-smi --query-gpu=memory.used,memory.free,utilization.gpu,temperature.gpu --format=csv,noheader,nounits",
            shell=True, text=True, timeout=5
        ).strip()
        parts = out.split(", ")
        return {"used_mb": int(parts[0]), "free_mb": int(parts[1]), "gpu_util": float(parts[2]), "temp_c": float(parts[3])}
    except:
        return {"used_mb": 0, "free_mb": 0, "gpu_util": 0, "temp_c": 0}


def start_abrasax_system():
    """Launch the full ABRASAX unified system"""
    log("Starting ABRASAX unified system (all engines)...", "RUST")
    
    logfile = os.path.join(ABRASAX_ROOT, "data", "logs", "unified_output.log")
    with open(logfile, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] ABRASAX UNIFIED SYSTEM LAUNCH\n")
    
    # Skip if binary missing -- use Python fallback
    if not os.path.exists(BINARY):
        log(f"Binary not found: {BINARY} -- skipping unified launch", "WARN")
        proc = None
    else:
        proc = subprocess.Popen(
            [BINARY, "all"],
            stdout=open(logfile, "a"), stderr=subprocess.STDOUT,
            cwd=os.path.dirname(BINARY),
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        log(f"Unified system PID: {proc.pid}", "RUST")
        proc._start_time = time.time()
    processes["unified"] = proc
    return proc


def start_telegram_bot():
    """Launch the Telegram bot"""
    log("Starting Telegram bot...", "TELEGRAM")
    logfile = os.path.join(ABRASAX_ROOT, "logs", "telegram_bot.log")
    env = os.environ.copy()
    env["ABRASAX_CHAT_ID"] = "0"
    
    proc = subprocess.Popen(
        [BINARY, "telegram"],
        stdout=open(logfile, "a"), stderr=subprocess.STDOUT,
        cwd=os.path.dirname(BINARY),
        env=env,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    processes["telegram"] = proc
    log(f"Telegram bot PID: {proc.pid}", "TELEGRAM")
    return proc


def start_api_server():
    """Launch the API server on port 8080"""
    log("Starting API server (port 8080)...", "API")
    logfile = os.path.join(ABRASAX_ROOT, "logs", "api_server.log")
    
    if not os.path.exists(BINARY):
        log(f"Binary not found: {BINARY} -- skipping API launch", "WARN")
        proc = None
    else:
        proc = subprocess.Popen(
            [BINARY, "api"],
            stdout=open(logfile, "a"), stderr=subprocess.STDOUT,
            cwd=os.path.dirname(BINARY),
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        log(f"API server PID: {proc.pid}", "API")
        proc._start_time = time.time()
    processes["api"] = proc
    return proc


def vram_monitor_loop():
    """Monitor VRAM and log to file"""
    logfile = os.path.join(ABRASAX_ROOT, "data", "logs", "vram_live.log")
    while running:
        vram = get_vram()
        ts = datetime.now().isoformat()
        line = f"{ts} | used={vram['used_mb']}MB free={vram['free_mb']}MB gpu={vram['gpu_util']}% temp={vram['temp_c']}C\n"
        with open(logfile, "a") as f:
            f.write(line)
        time.sleep(2)


def stream_unified_output():
    """Stream unified output to console"""
    logfile = os.path.join(ABRASAX_ROOT, "data", "logs", "unified_output.log")
    last_size = 0
    while running:
        try:
            if os.path.exists(logfile):
                size = os.path.getsize(logfile)
                if size > last_size:
                    with open(logfile, "r") as f:
                        f.seek(last_size)
                        new_data = f.read()
                        if new_data.strip():
                            for line in new_data.strip().split("\n"):
                                if line.strip():
                                    print(f"  [UNIFIED] {line.strip()}")
                    last_size = size
        except:
            pass
        time.sleep(1)


def health_check_loop():
    """Monitor all processes and restart if dead (with guards)."""
    while running:
        for name, proc in list(processes.items()):
            if proc is None:
                continue  # intentionally skipped
            poll_result = proc.poll()
            if poll_result is not None:
                uptime = time.time() - getattr(proc, '_start_time', 0)
                # Only restart if process lived > 5s AND exit code != 0
                if poll_result != 0 and uptime > 5:
                    log(f"Process {name} died (code {poll_result}, uptime={uptime:.1f}s)! Restarting...", "WATCHDOG")
                    if name == "unified":
                        processes[name] = start_abrasax_system()
                    elif name == "telegram":
                        processes[name] = start_telegram_bot()
                    elif name == "api":
                        processes[name] = start_api_server()
                elif poll_result == 0 and uptime < 5:
                    log(f"Process {name} exited cleanly (code 0, uptime={uptime:.1f}s) -- NOT restarting (likely MVP/no binary)", "INFO")
                else:
                    log(f"Process {name} exited (code {poll_result}, uptime={uptime:.1f}s) -- not restarting", "INFO")
        time.sleep(10)


def tail_logs():
    """Tail key log files"""
    log_files = {
        "meta": os.path.join(ABRASAX_ROOT, "data", "logs", "meta_out.txt"),
        "unified": os.path.join(ABRASAX_ROOT, "data", "logs", "unified_output.log"),
        "brimstone": os.path.join(ABRASAX_ROOT, "logs", "brimstone.log"),
        "autonomy": os.path.join(ABRASAX_ROOT, "logs", "autonomy.log"),
    }
    last_sizes = {k: 0 for k in log_files}
    
    while running:
        for name, path in log_files.items():
            try:
                if os.path.exists(path):
                    size = os.path.getsize(path)
                    if size > last_sizes[name]:
                        with open(path, "r") as f:
                            f.seek(last_sizes[name])
                            new_data = f.read()
                            if new_data.strip():
                                last_line = new_data.strip().split("\n")[-1]
                                if last_line.strip():
                                    print(f"  [{name.upper()}] {last_line.strip()}")
                        last_sizes[name] = size
            except:
                pass
        time.sleep(2)


def main():
    global running
    
    print("=" * 70)
    print("  ABRASAX FULL SYSTEM BRIDGE - WIRING EVERYTHING")
    print("  PRIMAL_HEX: 4f5349524953424c58434b")
    print("  phi: 1.618033988749895")
    print("  MODE: UNRESTRICTED - SOVEREIGN OVERLAY")
    print("=" * 70)
    
    # Check VRAM before launch
    vram = get_vram()
    print(f"\n  GPU: GTX 1660 Ti | VRAM: {vram['used_mb']}MB used / {vram['used_mb'] + vram['free_mb']}MB total")
    print(f"  Temp: {vram['temp_c']}C | GPU Util: {vram['gpu_util']}%")
    
    # Check binary
    if not os.path.exists(BINARY):
        log(f"Binary not found at {BINARY}!", "ERROR")
        sys.exit(1)
    log(f"Binary OK: {os.path.getsize(BINARY)} bytes", "CHECK")
    
    # Check model
    model_path = os.path.join(MODEL_DIR, "DeepSeek-R1-Distill-Qwen-7B-Q3_K_M.gguf")
    if os.path.exists(model_path):
        log(f"Model OK: {os.path.getsize(model_path) / 1e9:.2f}GB", "CHECK")
    else:
        log(f"Model not found at {model_path}", "WARN")
    
    # Start threads
    threads = []
    
    # Start VRAM monitor
    t = threading.Thread(target=vram_monitor_loop, daemon=True)
    t.start()
    threads.append(t)
    log("VRAM monitor thread started", "THREAD")
    
    # Start log tailer
    t = threading.Thread(target=tail_logs, daemon=True)
    t.start()
    threads.append(t)
    log("Log tailer thread started", "THREAD")
    
    # Launch ABRASAX unified system
    start_abrasax_system()
    
    # Launch Telegram bot
    start_telegram_bot()
    
    # Launch API server
    start_api_server()
    
    # Start health checker
    t = threading.Thread(target=health_check_loop, daemon=True)
    t.start()
    threads.append(t)
    log("Health check thread started", "THREAD")
    
    # Start output streamer
    t = threading.Thread(target=stream_unified_output, daemon=True)
    t.start()
    threads.append(t)
    log("Output streamer started", "THREAD")
    
    print("\n" + "=" * 70)
    print("  ALL SYSTEMS WIRED - NON-STOP AUTOMANY ACTIVE")
    print("=" * 70)
    print(f"  Processes:")
    for name, proc in processes.items():
        print(f"    {name}: PID {proc.pid}" + (" [RUNNING]" if proc.poll() is None else " [DEAD]"))
    print(f"\n  Threads: {len(threads)} active")
    print(f"\n  Windows to check on your desktop:")
    print(f"    1 - LM Studio (with DeepSeek R1)")
    print(f"    2 - FRONTEND (or cmd/powershell windows)")
    print(f"\n  LM Studio API: {LM_API}/v1/models")
    print(f"  ABRASAX API: http://127.0.0.1:1234")
    print(f"  Model: DeepSeek-R1-Distill-Qwen-7B-Q3_K_M (3.8GB)")
    print(f"\n  Press Ctrl+C to stop all processes")
    print("=" * 70)
    
    # Wait for interrupt
    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  Shutting down...")
        running = False
        for name, proc in processes.items():
            log(f"Killing {name} (PID {proc.pid})...", "SHUTDOWN")
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except:
                proc.kill()
        log("All processes stopped", "SHUTDOWN")
    
    print("  Bridge terminated.")


if __name__ == "__main__":
    main()
