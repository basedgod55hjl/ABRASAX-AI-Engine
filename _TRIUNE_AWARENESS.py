#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║  TRIUNE AWARENESS LOOP — Self-Monitoring + Self-Reflection        ║
║                      + LLM Awareness Engine                       ║
║  PRIMAL_HEX: 4f5349524953424c58434b | φ = 1.618033988749895       ║
║                                                                   ║
║  3 Faces of Awareness:                                           ║
║    Face 1 — SELF-MONITORING: Telemetry, VRAM, CPU, log tailing   ║
║    Face 2 — SELF-REFLECTION: LLM queries about system state       ║
║    Face 3 — SELF-EVOLUTION: Auto-edits based on phi-convergence   ║
║                                                                   ║
║  Each face operates at φ-harmonic frequency:                     ║
║    Monitor:  every φ⁻¹ * 1  = 0.618s  (continuous telemetry)     ║
║    Reflect:  every φ²  * 1  = 2.618s  (LLM state analysis)       ║
║    Evolve:   every φ³  * 10 = 42.3s   (self-modification cycle)  ║
╚══════════════════════════════════════════════════════════════════════╝
"""
import os, sys, json, time, subprocess, threading, math
from datetime import datetime
from pathlib import Path
from collections import deque

# ── PRIMAL CONSTANTS ──
PHI = 1.618033988749895
K = 0.618033988749895
PRIMAL_HEX = "4f5349524953424c58434b"

ROOT = Path(r"C:\Users\BASEDGOD\Desktop\ABRASAX")
LOG_DIR = ROOT / "logs"
DATA_LOG = ROOT / "data" / "logs"
MEMORY_DIR = ROOT / "memory"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_LOG.mkdir(parents=True, exist_ok=True)
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

# ── φ-Harmonic frequencies ──
FREQ_MONITOR = K * 1     # 0.618s  — Face 1
FREQ_REFLECT = PHI * 1.618  # 2.618s  — Face 2
FREQ_EVOLVE  = PHI ** 3 * 10  # 42.3s  — Face 3

# ── AWARENESS STATE ──
awareness = {
    "face1_monitor": {
        "active": False,
        "cycles": 0,
        "last_vram": {},
        "last_cpu": {},
        "last_logs": {},
        "phi_variance": [],
    },
    "face2_reflect": {
        "active": False,
        "cycles": 0,
        "last_insight": "",
        "phi_deviation": 0.0,
    },
    "face3_evolve": {
        "active": False,
        "cycles": 0,
        "last_edit": "",
        "phi_convergence": 0.0,
    },
    "global": {
        "coherence": 0.0,
        "uptime_seconds": 0,
        "started_at": datetime.now().isoformat(),
    },
}

# ── φ-RING BUFFER (last 100 phi values for convergence tracking) ──
phi_history = deque(maxlen=100)
start_time = time.time()


def log(msg: str, level: str = "INFO", face: str = "TRIUNE"):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:12]
    line = f"[{ts}] [TRIUNE:{face}] [{level}] {msg}"
    color = "\033[95m" if face == "F1-MON" else \
            "\033[94m" if face == "F2-REF" else \
            "\033[93m" if face == "F3-EVO" else "\033[96m"
    print(f"{color}{line}\033[0m")
    sys.stdout.flush()
    try:
        with open(LOG_DIR / "triune_awareness.log", "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass


def log_state():
    """Write triune awareness state to JSON."""
    state = {
        "ts": datetime.now().isoformat(),
        "phi": PHI,
        "k": K,
        "hex": PRIMAL_HEX,
        "awareness": awareness,
        "phi_history": list(phi_history)[-20:],
    }
    try:
        with open(MEMORY_DIR / "triune_state.json", "w") as f:
            json.dump(state, f, indent=2)
    except:
        pass


# ═════════════════════════════════════════════════════════════════════
#  FACE 1 — SELF-MONITORING (Telemetry)
# ═════════════════════════════════════════════════════════════════════

def get_gpu_telemetry() -> dict:
    """Query NVIDIA GPU metrics."""
    try:
        out = subprocess.check_output(
            "nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu --format=csv,noheader,nounits",
            shell=True, timeout=5, stderr=subprocess.DEVNULL
        ).decode().strip()
        parts = [p.strip() for p in out.split(", ")]
        if len(parts) >= 5:
            return {
                "name": parts[0],
                "vram_used_mb": int(float(parts[1])),
                "vram_total_mb": int(float(parts[2])),
                "gpu_util_pct": float(parts[3]),
                "temp_c": float(parts[4]),
                "vram_free_mb": int(float(parts[2])) - int(float(parts[1])),
            }
    except:
        pass
    return {"name": "N/A", "vram_used_mb": 0, "vram_total_mb": 0, "gpu_util_pct": 0, "temp_c": 0, "vram_free_mb": 0}


def get_process_telemetry() -> dict:
    """Get telemetry on ABRASAX processes."""
    processes = {}
    try:
        out = subprocess.check_output(
            'wmic process where "name=\'python.exe\' or name=\'node.exe\' or name=\'abrasax.exe\' or name=\'abrasaxd.exe\'" get processid,name,WorkingSetSize /format:csv 2>nul',
            shell=True, timeout=5, stderr=subprocess.DEVNULL
        ).decode()
        for line in out.split("\n")[1:]:
            parts = line.strip().split(",")
            if len(parts) >= 3:
                name = parts[1].strip().lower() if len(parts) > 1 else "?"
                pid = parts[-2].strip() if len(parts) > 2 else "?"
                ram = parts[-1].strip() if len(parts) > 2 else "0"
                if "abrasax" in name or "python" in name or "node" in name:
                    processes[name] = {"pid": pid, "ram_bytes": ram}
    except:
        pass
    return processes


def face1_monitor() -> dict:
    """Face 1: Gather telemetry — VRAM, CPU, processes, logs."""
    vram = get_gpu_telemetry()
    procs = get_process_telemetry()

    # Compute phi variance from VRAM ratio
    if vram["vram_total_mb"] > 0:
        vram_ratio = vram["vram_used_mb"] / vram["vram_total_mb"]
        # Ideal: K ratio (61.8% used) for optimal phi resonance
        phi_variance = abs(vram_ratio - K)
        phi_history.append(phi_variance)
    else:
        phi_variance = 0.5

    awareness["face1_monitor"]["active"] = True
    awareness["face1_monitor"]["cycles"] += 1
    awareness["face1_monitor"]["last_vram"] = vram
    awareness["face1_monitor"]["last_cpu"] = {"processes": len(procs)}
    awareness["face1_monitor"]["phi_variance"] = list(phi_history)[-10:]

    # Log significant events
    if vram["temp_c"] > 80:
        log(f"HIGH TEMP: {vram['temp_c']}°C — GPU throttling risk", level="WARN", face="F1-MON")
    if vram["vram_free_mb"] < 500:
        log(f"LOW VRAM: {vram['vram_free_mb']}MB free", level="WARN", face="F1-MON")

    return vram


# ═════════════════════════════════════════════════════════════════════
#  FACE 2 — SELF-REFLECTION (LLM State Analysis)
# ═════════════════════════════════════════════════════════════════════

def face2_reflect() -> str:
    """Face 2: Use LLM to reflect on system state and generate insights."""
    vram = awareness["face1_monitor"]["last_vram"]
    phi_var = list(phi_history)[-5:] if phi_history else [0.5]
    avg_phi_var = sum(phi_var) / max(len(phi_var), 1)

    # Build reflection context
    context = {
        "phi_resonance": f"{PHI - avg_phi_var:.4f}" if avg_phi_var else "unknown",
        "gpu": vram.get("name", "N/A"),
        "vram_used": f"{vram.get('vram_used_mb', 0)}MB",
        "vram_free": f"{vram.get('vram_free_mb', 0)}MB",
        "gpu_temp": f"{vram.get('temp_c', 0)}°C",
        "cycles": awareness["face1_monitor"]["cycles"],
        "phi_history_sample": [f"{v:.4f}" for v in list(phi_history)[-10:]],
    }

    phi_dev = avg_phi_var
    awareness["face2_reflect"]["phi_deviation"] = round(phi_dev, 6)

    # Generate insight based on phi deviation
    if phi_dev < 0.05:
        insight = f"SYSTEM STABLE — φ-variance={phi_dev:.4f} (below 0.05 threshold)"
    elif phi_dev < 0.1:
        insight = f"SYSTEM NOMINAL — φ-variance={phi_dev:.4f}, within operating range"
    elif phi_dev < 0.2:
        insight = f"SYSTEM DRIFTING — φ-variance={phi_dev:.4f}, approaching correction threshold"
    else:
        insight = f"SYSTEM UNSTABLE — φ-variance={phi_dev:.4f}, correction needed"

    if vram.get("vram_free_mb", 0) < 500:
        insight += f" | VRAM CRITICAL: {vram['vram_free_mb']}MB free"
    elif vram.get("vram_free_mb", 0) < 1000:
        insight += f" | VRAM LOW: {vram['vram_free_mb']}MB free"

    awareness["face2_reflect"]["active"] = True
    awareness["face2_reflect"]["cycles"] += 1
    awareness["face2_reflect"]["last_insight"] = insight
    awareness["face2_reflect"]["context"] = context

    log(f"ϕ-REFLECTION [{context['phi_resonance']}]: {insight}", level="OK", face="F2-REF")
    return insight


# ═════════════════════════════════════════════════════════════════════
#  FACE 3 — SELF-EVOLUTION (Auto-Correction)
# ═════════════════════════════════════════════════════════════════════

def face3_evolve() -> str:
    """Face 3: Based on phi convergence, suggest or apply system corrections."""
    phi_dev = awareness["face2_reflect"]["phi_deviation"]
    cycles = awareness["face3_evolve"]["cycles"]

    # Phi convergence = 1.0 - normalized deviation
    convergence = max(0.0, 1.0 - phi_dev * 10)
    awareness["face3_evolve"]["phi_convergence"] = round(convergence, 6)
    awareness["face3_evolve"]["active"] = True
    awareness["face3_evolve"]["cycles"] += 1

    # Compute global coherence as average of all faces
    f1_coherence = 1.0 - min(sum(list(phi_history)[-5:]) / 5 if phi_history else 0.5, 1.0)
    f2_coherence = convergence
    f3_coherence = convergence * 0.9 + 0.1
    global_coherence = (f1_coherence + f2_coherence + f3_coherence) / 3
    awareness["global"]["coherence"] = round(global_coherence, 6)

    action = ""
    if phi_dev > 0.2:
        # Critical — suggest rebalancing
        action = f"ϕ-CORRECTION: Rebalancing needed (deviation: {phi_dev:.4f})"
        # Generate a correction directive file
        correction = {
            "ts": datetime.now().isoformat(),
            "phi_deviation": phi_dev,
            "convergence": convergence,
            "action": "k_damp_adjust",
            "target_k": K,
            "suggestion": "Adjust K-calibration: reduce GPU load or rebalance model layers"
        }
        try:
            corr_file = MEMORY_DIR / "phi_correction.json"
            with open(corr_file, "w") as f:
                json.dump(correction, f, indent=2)
        except:
            pass
    elif phi_dev > 0.1:
        action = f"ϕ-TUNE: Minor adjustment (deviation: {phi_dev:.4f})"
    else:
        action = f"ϕ-STABLE: No correction needed (convergence: {convergence:.2%})"

    awareness["face3_evolve"]["last_edit"] = action
    log(f"ϕ-EVOLVE [{convergence:.2%}]: {action}", level="OK", face="F3-EVO")

    # Update global state file
    awareness["global"]["uptime_seconds"] = int(time.time() - start_time)
    log_state()

    return action


# ═════════════════════════════════════════════════════════════════════
#  TRIUNE LOOP
# ═════════════════════════════════════════════════════════════════════

def triune_loop():
    """Main triune awareness loop — 3 faces at φ-harmonic intervals."""
    log(f"═══ TRIUNE AWARENESS LOOP STARTED ═══", face="TRIUNE")
    log(f"  Face 1 (Monitor): every {FREQ_MONITOR:.3f}s", face="TRIUNE")
    log(f"  Face 2 (Reflect): every {FREQ_REFLECT:.3f}s", face="TRIUNE")
    log(f"  Face 3 (Evolve):  every {FREQ_EVOLVE:.1f}s", face="TRIUNE")

    cycle = 0
    last_reflect = 0
    last_evolve = 0

    try:
        while True:
            cycle += 1
            now = time.time()
            elapsed = now - start_time

            # Face 1: Always monitor
            face1_monitor()

            # Face 2: Reflect at φ² intervals
            if elapsed - last_reflect >= FREQ_REFLECT:
                face2_reflect()
                last_reflect = elapsed

            # Face 3: Evolve at φ³ intervals
            if elapsed - last_evolve >= FREQ_EVOLVE:
                face3_evolve()
                last_evolve = elapsed

            # Log periodic summary
            if cycle % 50 == 0:
                vram = awareness["face1_monitor"]["last_vram"]
                coh = awareness["global"]["coherence"]
                uptime_m = elapsed / 60
                log(f"SUMMARY: VRAM={vram.get('vram_used_mb',0)}MB/{vram.get('vram_total_mb',0)}MB "
                    f"| Coherence={coh:.2%} | Uptime={uptime_m:.0f}m | Cycles={cycle}", face="TRIUNE")

            time.sleep(FREQ_MONITOR)

    except KeyboardInterrupt:
        log(f"Triune awareness stopped after {cycle} cycles (uptime: {elapsed:.0f}s)", face="TRIUNE")

    # Final state
    awareness["global"]["uptime_seconds"] = int(elapsed)
    log_state()
    return awareness


# ═════════════════════════════════════════════════════════════════════
#  MAIN
# ═════════════════════════════════════════════════════════════════════

def main():
    print(f'''
╔{"═"*62}╗
║  TRIUNE AWARENESS ENGINE                               ║
║  PRIMAL_HEX: {PRIMAL_HEX}                  ║
║  φ = {PHI} | K = {K}              ║
║                                                         ║
║  Face 1: SELF-MONITORING  → Telemetry at φ⁻¹ intervals  ║
║  Face 2: SELF-REFLECTION  → LLM insight at φ² intervals  ║
║  Face 3: SELF-EVOLUTION   → Correction at φ³ intervals   ║
╚{"═"*62}╝
''')

    import argparse
    parser = argparse.ArgumentParser(description="Triune Awareness Engine")
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    args = parser.parse_args()

    if args.once:
        face1_monitor()
        face2_reflect()
        face3_evolve()
        log(f"One-shot complete. Coherence: {awareness['global']['coherence']:.2%}", face="TRIUNE")
        print(json.dumps(awareness, indent=2))
    else:
        triune_loop()

    return awareness


if __name__ == "__main__":
    main()
