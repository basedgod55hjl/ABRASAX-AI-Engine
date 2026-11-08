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
import urllib.request, urllib.error
from datetime import datetime
from pathlib import Path
from collections import deque

# ── PRIMAL CONSTANTS ──
PHI = 1.618033988749895
K = 0.618033988749895
PRIMAL_HEX = "4f5349524953424c58434b"
LM_BASE = os.environ.get("ABRASAX_LM_URL", "http://127.0.0.1:1234/v1")
LM_API = LM_BASE.rstrip("/") + "/chat/completions"
LM_MODEL = os.environ.get("ABRASAX_LM_MODEL", "gemma-4-e2b-uncensored-hauhaucs-aggressive")
LM_TIMEOUT = float(os.environ.get("ABRASAX_LM_TIMEOUT", "25"))
# Face 2 only claims "LLM awareness" when it can actually reach a model.
LM_ENABLED = True
# φ-balance target: the VRAM ratio the loop treats as resonant. 0.618 is the
# theoretical optimum; a 6 GB card idling at 1.3 GB sits ~0.22 and therefore
# reads as "unstable" forever, so this is overridable per host.
TARGET_RATIO = float(os.environ.get("ABRASAX_TARGET_VRAM_RATIO", str(K)))

ROOT = Path(os.environ.get("ABRASAX_ROOT") or r"C:\abrasax")
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
#  LM STUDIO BRIDGE — makes Face 2 a real LLM reflection, not a rule
# ═════════════════════════════════════════════════════════════════════

def _lm_api_key() -> str:
    """LM Studio key from the environment, else from <ROOT>/.env."""
    key = os.environ.get("LM_STUDIO_API_KEY") or os.environ.get("LM_API_KEY") or ""
    if key:
        return key
    try:
        for line in (ROOT / ".env").read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            if name.strip() in {"LM_STUDIO_API_KEY", "LM_API_KEY"}:
                return value.strip().strip("\"'")
    except OSError:
        pass
    return ""


def lm_resident_model(timeout: float = 5.0) -> str | None:
    """Return the first model LM Studio reports as resident, or None."""
    url = LM_BASE.rstrip("/")
    if url.endswith("/v1"):
        url = url[:-3]
    url += "/api/v1/models"
    req = urllib.request.Request(url)
    key = _lm_api_key()
    if key:
        req.add_header("Authorization", f"Bearer {key}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
    except (urllib.error.URLError, OSError, ValueError):
        return None
    for model in data.get("models", []):
        if model.get("loaded_instances"):
            return model.get("key")
    return None


def lm_chat(prompt: str, system: str, model: str | None = None,
            timeout: float | None = None, max_tokens: int = 160) -> dict:
    """One non-streaming chat completion against LM Studio.

    Returns {"ok", "text", "model", "latency_s", "error"}. Never raises: a dead
    model is a recorded condition, not a crashed loop.
    """
    model = model or LM_MODEL
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": prompt}],
        "temperature": 0.4,
        "max_tokens": max_tokens,
        "stream": False,
    }).encode()
    req = urllib.request.Request(LM_API, data=payload,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    key = _lm_api_key()
    if key:
        req.add_header("Authorization", f"Bearer {key}")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout or LM_TIMEOUT) as r:
            data = json.loads(r.read())
    except Exception as exc:  # noqa: BLE001 - report, never crash the face
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}",
                "model": model, "text": "", "latency_s": round(time.time() - t0, 3)}
    text = ""
    try:
        text = data["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError):
        return {"ok": False, "error": "unexpected response shape",
                "model": data.get("model", model), "text": "",
                "latency_s": round(time.time() - t0, 3)}
    return {"ok": bool(text.strip()), "text": text.strip(),
            "model": data.get("model", model), "error": None,
            "latency_s": round(time.time() - t0, 3)}


def lm_reflect(context: dict, rule_insight: str) -> dict:
    """Ask the resident model for one operational insight about the state."""
    model = lm_resident_model() or LM_MODEL
    system = ("You are ABRASAX TRIUNE, the awareness layer of a local AI stack. "
              "Given measured telemetry, reply with ONE operational insight and ONE "
              "concrete next action. Maximum two sentences. No preamble.")
    prompt = ("Measured state:\n" + json.dumps(context, indent=2, ensure_ascii=False)
              + f"\n\nRule baseline: {rule_insight}\n\nYour reflection:")
    out = lm_chat(prompt, system, model=model, max_tokens=160)
    out["model_used"] = model
    return out


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
    """Per-image count, PIDs and working set for python/node runners.

    `wmic` is deprecated (absent on recent Windows images) and its CSV layout
    shifts between builds, so this reads `tasklist`, which is stable. Memory is
    reported in KiB as tasklist prints it.
    """
    import csv as _csv

    processes: dict[str, dict] = {}
    try:
        out = subprocess.check_output(
            "tasklist /fo csv /nh",
            shell=True, timeout=8, stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        ).decode("utf-8", "replace")
    except Exception:  # noqa: BLE001 - telemetry is best-effort
        return processes

    for row in _csv.reader(out.splitlines()):
        if len(row) < 5:
            continue
        name = row[0].strip().lower()
        if not any(tag in name for tag in ("python", "node", "abrasax")):
            continue
        entry = processes.setdefault(name, {"count": 0, "pids": [], "mem_kb": 0})
        entry["count"] += 1
        entry["pids"].append(row[1].strip())
        try:
            entry["mem_kb"] += int(row[4].split()[0].replace(",", ""))
        except (ValueError, IndexError):
            pass
    return processes


def face1_monitor() -> dict:
    """Face 1: Gather telemetry — VRAM, CPU, processes, logs."""
    vram = get_gpu_telemetry()
    procs = get_process_telemetry()

    # Compute phi variance from VRAM ratio
    if vram["vram_total_mb"] > 0:
        vram_ratio = vram["vram_used_mb"] / vram["vram_total_mb"]
        # Ideal: TARGET_RATIO of VRAM used for optimal φ resonance (0.618 by
        # default; override per host with ABRASAX_TARGET_VRAM_RATIO).
        phi_variance = abs(vram_ratio - TARGET_RATIO)
        phi_history.append(phi_variance)
    else:
        phi_variance = 0.5

    awareness["face1_monitor"]["active"] = True
    awareness["face1_monitor"]["cycles"] += 1
    awareness["face1_monitor"]["last_vram"] = vram
    awareness["face1_monitor"]["last_cpu"] = {
        "processes": sum(v["count"] for v in procs.values()),
        "by_image": {k: v["count"] for k, v in procs.items()},
    }
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

    rule_insight = insight
    llm = None
    source = "rule"
    if LM_ENABLED:
        llm = lm_reflect(context, rule_insight)
        if llm.get("ok"):
            insight = llm["text"]
            source = "llm"

    awareness["face2_reflect"]["active"] = True
    awareness["face2_reflect"]["cycles"] += 1
    awareness["face2_reflect"]["last_insight"] = insight
    awareness["face2_reflect"]["rule_insight"] = rule_insight
    awareness["face2_reflect"]["insight_source"] = source
    awareness["face2_reflect"]["llm"] = llm
    awareness["face2_reflect"]["context"] = context

    if source == "llm":
        tag = f"LLM:{llm.get('model_used')}({llm.get('latency_s')}s)"
    else:
        tag = "RULE"
        if llm and not llm.get("ok"):
            tag += f" (LLM unavailable: {str(llm.get('error'))[:60]})"
    log(f"ϕ-REFLECTION [{context['phi_resonance']}] ({tag}): {insight}",
        level="OK", face="F2-REF")
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
    sample = list(phi_history)[-5:]
    f1_coherence = 1.0 - min(sum(sample) / max(len(sample), 1), 1.0)
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
    elapsed = 0.0

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
    global LM_ENABLED, LM_MODEL, LM_API, LM_BASE, TARGET_RATIO, LM_TIMEOUT
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
    parser.add_argument("--no-llm", action="store_true",
                        help="Skip the LM Studio reflection and stay rule-based")
    parser.add_argument("--model", default=None,
                        help="LM Studio model id (default: resident model, else ABRASAX_LM_MODEL)")
    parser.add_argument("--lm-url", default=None,
                        help="LM Studio base URL, e.g. http://127.0.0.1:1234/v1")
    parser.add_argument("--target-ratio", type=float, default=None,
                        help="VRAM ratio treated as phi-balanced (default 0.618)")
    args = parser.parse_args()

    LM_ENABLED = not args.no_llm
    if args.lm_url:
        LM_BASE = args.lm_url.rstrip("/")
        LM_API = LM_BASE + "/chat/completions"
    if args.model:
        LM_MODEL = args.model
    if args.target_ratio is not None:
        TARGET_RATIO = args.target_ratio

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
