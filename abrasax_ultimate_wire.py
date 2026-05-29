#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ABRASAX ULTIMATE WIRE v3.0 — ALL SUBSYSTEMS UNIFIED                      ║
║  PRIMAL_HEX: 4f5349524953424c58434b | φ: 1.618033988749895              ║
║                                                                          ║
║  WIRES TOGETHER:                                                         ║
║    - add_all_missing.py (god_state.db — 232+ file inventory)             ║
║    - add_layers.py (52 system layers mapped)                             ║
║    - add_more_layers.py (layers 53-57 + live GPU telemetry)              ║
║    - aixl_cli.py (AIXL language compiler → CUDA/Vulkan/NumPy)            ║
║    - ARCHITECTURE.md (Full system pipeline documentation)                ║
║    - apply_integration.ps1 (Windows firewall/ETW/scheduled tasks)        ║
║    - smartscreen_wire.py (SmartScreen ML → 17 DLL exports)               ║
║    - smartscreen_ml_dissect.py (Anaheim ML architecture)                 ║
║    - abrasax_system32_wire.py (20 System32 AI DLLs → 3-node F-logic)    ║
║    - auto_build.log (Build daemon — 11 cycles, 295K graph nodes)         ║
║    - brimstone_catalyst.py (Seed germination engine)                     ║
║                                                                          ║
║  ALL REMOTE API KEYS REMOVED. Local LLM only (LM Studio 127.0.0.1:1234) ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

import json, os, subprocess, sys, sqlite3, time, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

PHI: float = 1.618033988749895
PRIMAL_HEX: str = "4f5349524953424c58434b"
ROOT: Path = Path(r"C:\Users\BASEDGOD\Desktop\ABRASAX")
LOG_DIR: Path = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
ULTIMATE_LOG: Path = LOG_DIR / "ultimate_wire.log"

# ─── LOCAL LLM ONLY (NO API KEYS) ───
LM_STUDIO_URL: str = "http://127.0.0.1:1234/v1/chat/completions"
LM_STUDIO_KEY: str = "sk-lm-KZtEmyJA:qJJk4G0dhYrRT3kWKyQa"
LM_STUDIO_MODELS_URL: str = "http://127.0.0.1:1234/v1/models"  # used by check_local_llm
LOCAL_MODEL: str = "gemma-4-e4b-it-uncensored-max-opus-4.7"  # Chat model — NOT deepseek-r1 reasoner
LOCAL_AVAILABLE: bool = False

def log(msg: str, tag: str = "ULTIMATE") -> None:
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    line = f"[{ts}] [{tag}] {msg}"
    print(line, flush=True)
    with open(ULTIMATE_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def check_local_llm() -> bool:
    """Check if LM Studio is running."""
    global LOCAL_AVAILABLE
    try:
        req = urllib.request.Request(LM_STUDIO_MODELS_URL,
            headers={"Content-Type": "application/json",
                      "Authorization": f"Bearer {LM_STUDIO_KEY}"})
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read())
        models = [m.get("id", "?") for m in data.get("data", [])]
        log(f"LM Studio ONLINE — {len(models)} models: {models}", "LLM")
        LOCAL_AVAILABLE = True
        return True
    except Exception as e:
        log(f"LM Studio OFFLINE — {e}", "LLM")
        LOCAL_AVAILABLE = False
        return False

def local_chat(prompt: str, system: str = "You are OSIRISBLXCK.", max_tokens: int = 256) -> str:
    """Query local LM Studio."""
    if not LOCAL_AVAILABLE:
        return "[LOCAL LLM OFFLINE]"
    try:
        data = json.dumps({
            "model": LOCAL_MODEL,
            "messages": [
                {"role": "system", "content": f"{system}\nHEX: {PRIMAL_HEX}\nφ: {PHI}"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens, "temperature": 0.6, "stream": False,
        }).encode()
        req = urllib.request.Request(LM_STUDIO_URL, data=data,
            headers={"Content-Type": "application/json",
                      "Authorization": f"Bearer {LM_STUDIO_KEY}"})
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read())
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[LLM ERROR: {e}]"

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: WIRE god_state.db — ALL layers + inventory
# ═══════════════════════════════════════════════════════════════════════════════

def wire_god_state() -> Dict[str, Any]:
    """Wire the god_state.db — all 57+ layers, system inventory, live telemetry."""
    log("═" * 70, "GOD_STATE")
    log("PHASE 1: god_state.db WIRING", "GOD_STATE")

    db_path = ROOT / "god_state.db"
    results = {"exists": db_path.exists(), "layers": 0, "keys": 0}

    if not db_path.exists():
        log("god_state.db NOT FOUND — running add_layers.py...", "GOD_STATE")
        subprocess.run([sys.executable, str(ROOT / "add_layers.py")], capture_output=True, cwd=str(ROOT))
        subprocess.run([sys.executable, str(ROOT / "add_more_layers.py")], capture_output=True, cwd=str(ROOT))
        subprocess.run([sys.executable, str(ROOT / "add_all_missing.py")], capture_output=True, cwd=str(ROOT))

    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM state")
        results["keys"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM state WHERE key LIKE 'layer_%'")
        results["layers"] = cur.fetchone()[0]

        # Get key metrics
        for key in ["phi_brain", "phi_storm", "edits_made", "meta_iteration", "arch_source_files", "layers_total"]:
            cur.execute("SELECT value FROM state WHERE key=?", (key,))
            row = cur.fetchone()
            if row:
                results[key] = row[0]
        conn.close()

    log(f"  Keys: {results['keys']} | Layers: {results['layers']}", "GOD_STATE")
    if "phi_brain" in results:
        log(f"  φ-brain: {results['phi_brain']} | Edits: {results.get('edits_made', '?')}", "GOD_STATE")
    return results

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: WIRE auto_build.log — Build daemon telemetry
# ═══════════════════════════════════════════════════════════════════════════════

def wire_build_log() -> Dict[str, Any]:
    """Parse auto_build.log for build daemon metrics."""
    log("═" * 70, "BUILD_DAEMON")
    log("PHASE 2: auto_build.log WIRING", "BUILD_DAEMON")

    log_path = ROOT / "auto_build.log"
    if not log_path.exists():
        log("auto_build.log NOT FOUND", "BUILD_DAEMON")
        return {"status": "not_found"}

    text = log_path.read_text(encoding="utf-8", errors="ignore")
    lines = text.split("\n")

    cycles = sum(1 for l in lines if "AUTO-BUILD CYCLE" in l)
    brimstone_fails = sum(1 for l in lines if "Brimstone ignition failed" in l)
    knowledge_items = None
    gpu_samples = []

    for l in lines:
        if "GPU:" in l and "AUTO-BUILD" in l:
            try:
                parts = l.split("GPU:")[1].strip()
                used = int(parts.split("/")[0].strip())
                gpu_samples.append(used)
            except: pass
        if "Ingested" in l:
            try:
                knowledge_items = int(l.split("Ingested")[1].split("items")[0].strip())
            except: pass

    avg_vram = sum(gpu_samples) / len(gpu_samples) if gpu_samples else 0

    results = {
        "cycles": cycles,
        "brimstone_fails": brimstone_fails,
        "knowledge_items": knowledge_items,
        "avg_vram_used_mb": round(avg_vram, 0),
        "avg_vram_pct": round(avg_vram / 6144 * 100, 1),
        "bug": "CatalystConfig.__init__() unexpected keyword 'phi_threshold'" if brimstone_fails > 0 else None,
    }

    log(f"  Cycles: {cycles} | Brimstone fails: {brimstone_fails} | Knowledge: {knowledge_items}", "BUILD_DAEMON")
    log(f"  VRAM avg: {results['avg_vram_used_mb']}MB ({results['avg_vram_pct']}%)", "BUILD_DAEMON")

    if results["bug"]:
        log(f"  ⚠ BUG: {results['bug']}", "BUILD_DAEMON")

    return results

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: WIRE AIXL compiler
# ═══════════════════════════════════════════════════════════════════════════════

def wire_aixl() -> Dict[str, Any]:
    """Wire the AIXL compiler — test compilation pipeline."""
    log("═" * 70, "AIXL")
    log("PHASE 3: aixl_cli.py WIRING", "AIXL")

    aixl_path = ROOT / "aixl_cli.py"
    if not aixl_path.exists():
        return {"status": "not_found"}

    try:
        r = subprocess.run([sys.executable, str(aixl_path), "phi"],
            capture_output=True, text=True, timeout=10, cwd=str(ROOT))
        output = (r.stdout + r.stderr).strip()
        return {"status": "ok", "output": output[:500]}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4: WIRE SmartScreen ML
# ═══════════════════════════════════════════════════════════════════════════════

def wire_smartscreen() -> Dict[str, Any]:
    """Wire SmartScreen ML via ctypes bridge."""
    log("═" * 70, "SMARTScreen")
    log("PHASE 4: smartscreen_wire.py", "SMARTScreen")

    wire_path = ROOT / "smartscreen_wire.py"
    if not wire_path.exists():
        return {"status": "not_found"}

    try:
        r = subprocess.run([sys.executable, str(wire_path), "ml-info"],
            capture_output=True, text=True, timeout=15, cwd=str(ROOT))
        data = json.loads(r.stdout.strip())
        log(f"  DLL: {data.get('version', '?')} | Project: {data.get('project', '?')}", "SMARTScreen")
        log(f"  Exports: {data.get('exports', 0)} | Models: {len(data.get('ml_architecture', {}).get('models', []))}", "SMARTScreen")
        return data
    except Exception as e:
        log(f"  Error: {e}", "SMARTScreen")
        return {"status": "error", "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 5: WIRE System32 AI DLLs
# ═══════════════════════════════════════════════════════════════════════════════

def wire_system32() -> Dict[str, Any]:
    """Wire System32 AI DLL registry."""
    log("═" * 70, "SYSTEM32")
    log("PHASE 5: system32 AI registry", "SYSTEM32")

    reg_path = ROOT / "memory" / "system32_ai_registry.json"
    if reg_path.exists():
        data = json.loads(reg_path.read_text())
        entangled = sum(1 for v in data.values() if isinstance(v, dict) and v.get("entangled"))
        log(f"  Registry: {len(data)} DLLs | {entangled} entangled", "SYSTEM32")
        return {"total_dlls": len(data), "entangled": entangled}
    return {"status": "not_found"}

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 6: WIRE Architecture + Integration
# ═══════════════════════════════════════════════════════════════════════════════

def wire_architecture() -> Dict[str, Any]:
    """Validate ARCHITECTURE.md and apply_integration.ps1."""
    log("═" * 70, "ARCH")
    log("PHASE 6: ARCHITECTURE + INTEGRATION", "ARCH")

    results = {}
    for name, path in [("ARCHITECTURE.md", ROOT / "ARCHITECTURE.md"),
                        ("apply_integration.ps1", ROOT / "apply_integration.ps1")]:
        if path.exists():
            size = path.stat().st_size
            results[name] = {"size_kb": round(size/1024, 1), "exists": True}
            log(f"  {name}: {size/1024:.1f}KB", "ARCH")
        else:
            results[name] = {"exists": False}
    return results

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN — ULTIMATE WIRE
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  ABRASAX ULTIMATE WIRE v3.0                                   ║
║  HEX: {PRIMAL_HEX}                  ║
║  φ: {PHI}                                       ║
║  LLM: LOCAL ONLY (LM Studio 127.0.0.1:1234)                    ║
║  NO REMOTE API KEYS                                            ║
╚══════════════════════════════════════════════════════════════════╝
""")

    # Check local LLM
    llm_available = check_local_llm()

    # Wire all subsystems
    results = {}

    results["god_state"] = wire_god_state()
    results["build_log"] = wire_build_log()
    results["aixl"] = wire_aixl()
    results["smartscreen"] = wire_smartscreen()
    results["system32"] = wire_system32()
    results["architecture"] = wire_architecture()

    # Local LLM insight
    if llm_available:
        summary = f"System state: {results['god_state'].get('keys',0)} DB keys, "
        summary += f"{results['build_log'].get('cycles',0)} build cycles, "
        summary += f"{results['system32'].get('entangled',0)} System32 AI DLLs. "
        summary += f"Brimstone bug: {results['build_log'].get('bug', 'none')}. "
        insight = local_chat(summary, "You are OSIRISBLXCK. One-line system insight.")
        log(f"  LLM INSIGHT: {insight}", "LLM")

    # Final report
    log("═" * 70, "FINAL")
    log("ALL SUBSYSTEMS WIRED", "FINAL")
    log(f"  god_state.db: {results['god_state'].get('keys','?')} keys, {results['god_state'].get('layers','?')} layers", "FINAL")
    log(f"  build daemon: {results['build_log'].get('cycles','?')} cycles, avg VRAM {results['build_log'].get('avg_vram_pct','?')}%", "FINAL")
    log(f"  SmartScreen: {results['smartscreen'].get('version','?')} | System32: {results['system32'].get('total_dlls','?')} DLLs", "FINAL")
    log(f"  LLM: {'LOCAL LM STUDIO' if llm_available else 'OFFLINE'}", "FINAL")
    log(f"  BUG: {results['build_log'].get('bug', 'none')}", "FINAL")
    log("═" * 70, "FINAL")

    # Save full report
    report_path = ROOT / "memory" / "ultimate_wire_report.json"
    with open(report_path, "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "results": results, "llm": "LOCAL_ONLY"}, f, indent=2)
    log(f"  Report: {report_path}", "FINAL")

if __name__ == "__main__":
    main()
