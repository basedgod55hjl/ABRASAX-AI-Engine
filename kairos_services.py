#!/usr/bin/env python3
"""KAIROS SERVICES — supervised restarter for the ABRASAX service layer.

Keeps two services alive permanently (stdlib only, Windows-safe):
  node_hub  : SOURCE/sdk/node-agents/hub.mjs     -> :8811 (agent fan-out)
  tg_bot    : SYSTEMS/telegram/abrasax_tg_bot.py -> :8798 (Telegram, /health)

(gateway :2645 is supervised by wake_all.py LOOPS["neotron"] — one owner per
port; a duplicate here caused bind flapping on 2026-11-08.)

Spawned by wake_all.py (LOOPS["kairos"]) and/or the ABRASAX-KAIROS logon task;
the lock file guarantees a single supervisor instance. Added by Kairos
2026-11-08. Logs: logs/kairos_services.log and LOGS/subagents/kairos_*.
"""
import os
import sys
import time
import msvcrt
import subprocess
from datetime import datetime

ROOT = r"C:\abrasax"
LOG = os.path.join(ROOT, "logs", "kairos_services.log")
LOCK = os.path.join(ROOT, "memory", "kairos_services.lock")
OUT_DIR = os.path.join(ROOT, "LOGS", "subagents")
RESTART_DELAY_S = 5.0

NODE_EXE = r"C:\Program Files\nodejs\node.exe"
PY = sys.executable

SERVICES = {
    # gateway (:2645) is supervised by wake_all.py LOOPS["neotron"] — one owner
    # per port. Kairos layer keeps the hub and the Telegram bot only.
    "node_hub": (
        "node",
        ["--env-file-if-exists=" + os.path.join(ROOT, ".env"),
         os.path.join(ROOT, "SOURCE", "sdk", "node-agents", "hub.mjs")],
    ),
    "tg_bot": (
        "py",
        [os.path.join(ROOT, "SYSTEMS", "telegram", "abrasax_tg_bot.py"),
         "--serve", "--port", "8798"],
    ),
}


def log(msg: str) -> None:
    line = f"[{datetime.now().isoformat()}] {msg}"
    try:
        print(line, flush=True)
    except OSError:
        pass
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def acquire_lock() -> bool:
    try:
        os.makedirs(os.path.dirname(LOCK), exist_ok=True)
        f = open(LOCK, "a+")
        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        f.truncate(0)
        f.write(str(os.getpid()))
        f.flush()
        return True
    except OSError:
        return False


def spawn(name: str):
    kind, argv = SERVICES[name]
    os.makedirs(OUT_DIR, exist_ok=True)
    tag = name if name != "tg_bot" else "bot"
    out = open(os.path.join(OUT_DIR, f"kairos_{tag}.out.log"), "a", encoding="utf-8")
    err = open(os.path.join(OUT_DIR, f"kairos_{tag}.err.log"), "a", encoding="utf-8")
    cmd = ([NODE_EXE] if kind == "node" else [PY]) + argv
    env = dict(os.environ)
    env.setdefault("ABRASAX_ROOT", ROOT)
    env.setdefault("ABRASAX_GATEWAY_URL", "http://127.0.0.1:2645")
    return subprocess.Popen(cmd, cwd=ROOT, stdout=out, stderr=err, env=env)


def main() -> None:
    if not acquire_lock():
        log("another kairos_services instance holds the lock — exiting")
        return
    log("KAIROS SERVICES supervisor online")
    procs = {}
    for name in SERVICES:
        log(f"starting {name}")
        procs[name] = spawn(name)
    try:
        while True:
            for name, p in list(procs.items()):
                rc = p.poll()
                if rc is not None:
                    log(f"{name} exited rc={rc} — restarting in {RESTART_DELAY_S:.0f}s")
                    time.sleep(RESTART_DELAY_S)
                    procs[name] = spawn(name)
                    log(f"{name} restarted pid={procs[name].pid}")
            time.sleep(3.0)
    except KeyboardInterrupt:
        log("shutdown requested — killing services")
        for p in procs.values():
            p.kill()
        log("KAIROS SERVICES stopped")


if __name__ == "__main__":
    main()
