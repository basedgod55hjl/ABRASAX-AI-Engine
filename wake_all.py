#!/usr/bin/env python3
"""WAKE ALL — supervised restarter for the ABRASAX live loops.

Keeps every loop alive permanently:
  entangle : _3NODE_F_LOGIC_ENTANGLE.py --interval 5   (F1/F2/F3/NEO wiring)
  neo_ton  : _NEO_TON_PULSE.py                         (neo transformer <-> TON)
  triune   : triune_mind.py --serve --port 9628        (reflective mind)
  ts_f1    : abrasax_ts_runtime.ts                     (Hex TS node on 4200)
  neotron  : neotron_gateway.py                        (Neotron A55 gateway 2645)

Any loop exits -> restarted after 5s. stdlib only, Windows-safe.
A lock file (memory/wake_all.lock) guarantees a single supervisor instance.
"""
import os
import sys
import time
import msvcrt
from datetime import datetime

ROOT = r"C:\abrasax"
ENG = os.path.join(ROOT, "ENGINE", "abrasax_engine")
LOG = os.path.join(ROOT, "logs", "wake_all.log")
LOCK = os.path.join(ROOT, "memory", "wake_all.lock")
RESTART_DELAY_S = 5.0

NODE_EXE = r"C:\Program Files\nodejs\node.exe"
ENTANGLE_PY = os.path.join(ENG, "_3NODE_F_LOGIC_ENTANGLE.py")
NEO_TON_PY = os.path.join(ENG, "_NEO_TON_PULSE.py")
TRIUNE_PY = os.path.join(ENG, "triune_mind.py")
TS_RUNTIME = os.path.join(
    ROOT, "AGENTS", "TS-SWARM", "ABRASAX-Agents", "src", "abrasax_ts_runtime.ts"
)
NEOTRON_PY = os.path.join(ROOT, "GATEWAY", "neotron_gateway.py")

# (kind, argv, extra env). kind "py" -> this interpreter; "node" -> system node.
LOOPS = {
    "entangle": ("py", [ENTANGLE_PY, "--interval", "5"], {}),
    "neo_ton": ("py", [NEO_TON_PY], {}),
    "triune": (
        "py",
        [TRIUNE_PY, "--serve", "--port", "9628"],
        {
            # Gateway on 9001 is down; pin the mind to the local LM Studio
            # route with the model that is actually resident (verified live).
            "ABRASAX_MIND_URL": "http://127.0.0.1:1234/v1/chat/completions",
            "ABRASAX_MIND_MODEL": "gemma-4-e2b-uncensored-hauhaucs-aggressive",
            "ABRASAX_MIND_NO_FALLBACK": "1",
        },
    ),
    "ts_f1": ("node", [TS_RUNTIME], {}),
    "neotron": ("py", [NEOTRON_PY], {}),
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
    """msvcrt byte-range lock; returns False if another instance holds it."""
    try:
        os.makedirs(os.path.dirname(LOCK), exist_ok=True)
        lock_f = open(LOCK, "a+")
        msvcrt.locking(lock_f.fileno(), msvcrt.LK_NBLCK, 1)
        lock_f.truncate(0)
        lock_f.write(str(os.getpid()))
        lock_f.flush()
        return True
    except OSError:
        return False


def subprocess_popen(cmd, env):
    import subprocess
    return subprocess.Popen(
        cmd, cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


def spawn(name: str):
    kind, argv, env_extra = LOOPS[name]
    if kind == "node":
        if not os.path.exists(NODE_EXE):
            raise FileNotFoundError(NODE_EXE)
        cmd = [NODE_EXE, *argv]
    else:
        cmd = [sys.executable, *argv]
    env = os.environ.copy()
    env.update(env_extra)
    return subprocess_popen(cmd, env)


def main() -> None:
    if not acquire_lock():
        log("another wake_all instance holds the lock — exiting")
        return
    log("WAKE ALL supervisor online")
    procs = {}
    for name in LOOPS:
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
        log("shutdown requested — killing loops")
        for p in procs.values():
            p.kill()
        log("WAKE ALL stopped")


if __name__ == "__main__":
    main()
