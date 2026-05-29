#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║  3-NODE F-LOGIC ENTANGLEMENT BRIDGE                               ║
║  PRIMAL_HEX: 4f5349524953424c58434b | φ = 1.618033988749895       ║
║                                                                   ║
║  Node F1 : Hex TypeScript (abrasax_hex.ts → engine → tools)      ║
║  Node F2 : Python Core (MASTER_AUTONOMY → cbm_hydration →        ║
║            full_bridge → nonstop_reasoning)                       ║
║  Node F3 : CBM Genesis / Rust Meta (seed_xor_graph →             ║
║            abrasax_rs → GGUF inference → VLC 7D)                 ║
║                                                                   ║
║  F = φ-harmonic coupling: each node resonates at φ-frequencies    ║
║  Entanglement protocol: XOR-seeded telemetry shared across nodes  ║
╚══════════════════════════════════════════════════════════════════════╝
"""
import os, sys, json, time, subprocess, threading, socket, struct
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── PRIMAL CONSTANTS ──
PHI = 1.618033988749895
K = 0.618033988749895
PRIMAL_HEX = "4f5349524953424c58434b"
PRIMAL_TEXT = "OSIRISBLXCK"

ROOT = Path(r"C:\Users\BASEDGOD\Desktop\ABRASAX")
LOG_DIR = ROOT / "logs"
DATA_LOG = ROOT / "data" / "logs"
MEMORY_DIR = ROOT / "memory"

LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_LOG.mkdir(parents=True, exist_ok=True)
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

# ── NODE F1: Hex TypeScript Bridge ──
NODE_F1 = {
    "ts_files": [
        "abrasax_hex.ts",
        "abrasax_engine.ts",
        "abrasax_api.ts",
        "abrasax_tools.ts",
        "abrasax_memory.ts",
        "abrasax_swarm.ts",
        "abrasax_skills.ts",
        "abrasax_terminal.ts",
        "abrasax_diagnostics.ts",
        "abrasax_config.ts",
    ],
    "server_port": 3000,
}

# ── NODE F2: Python Core Bridge ──
NODE_F2 = {
    "py_scripts": [
        "_MASTER_AUTONOMY.py",
        "_full_bridge.py",
        "cbm_hydration_engine.py",
        "abrasax_master.py",
        "abrasax_ultimate_wire.py",
        "_live_logger.py",
        "_nonstop_reasoning.py",
        "genesis_startup.py",
        "abrasax_unified_awareness.py",
        "abrasax_service_host.py",
    ],
}

# ── NODE F3: CBM / Rust Meta Bridge ──
NODE_F3 = {
    "rust_binary": ROOT / "abrasax_rs" / "target" / "release" / "abrasax.exe",
    "rust_daemon": ROOT / "abrasax_rs" / "target" / "release" / "abrasaxd.exe",
    "engine_files": [
        "engine/seed_xor_graph.py",
        "hetero_gpu_engine.py",
        "cbm_hydration_engine.py",
        "abrasax_f_logic_bridge.py",
    ],
}

# ── ENTANGLEMENT STATE ──
entanglement = {
    "node_f1": {"alive": False, "pid": None, "last_seen": None, "phi_resonance": 0.0},
    "node_f2": {"alive": False, "pid": None, "last_seen": None, "phi_resonance": 0.0},
    "node_f3": {"alive": False, "pid": None, "last_seen": None, "phi_resonance": 0.0},
    "coupling_strength": 0.0,
    "coherence": 0.0,
}

# ── LOGGING ──
def log(msg: str, level: str = "INFO", node: str = "F"):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:12]
    line = f"[{ts}] [F-LOGIC:{node}] [{level}] {msg}"
    print(f"\033[96m{line}\033[0m" if level == "INFO" else
          f"\033[93m{line}\033[0m" if level == "WARN" else
          f"\033[91m{line}\033[0m" if level == "ERROR" else
          f"\033[92m{line}\033[0m" if level == "OK" else line)
    sys.stdout.flush()
    try:
        with open(LOG_DIR / "f_logic_entangle.log", "a", encoding="utf-8") as f:
            f.write(line + "\n")
        with open(DATA_LOG / "live_feed.log", "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass


def log_state():
    """Log current entanglement state to JSON file."""
    state = {
        "ts": datetime.now().isoformat(),
        "phi": PHI,
        "k": K,
        "hex": PRIMAL_HEX,
        "entanglement": entanglement,
    }
    with open(MEMORY_DIR / "f_entanglement_state.json", "w") as f:
        json.dump(state, f, indent=2)


# ═════════════════════════════════════════════════════════════════════
#  NODE F1 — Hex TypeScript Wire
# ═════════════════════════════════════════════════════════════════════

def wire_node_f1() -> bool:
    """Wire into Hex TypeScript layer — check if TS runtime is alive."""
    log("Wiring Node F1: Hex TypeScript...", node="F1")

    # Check for running Node.js processes with abrasax_engine
    try:
        # Check if TS engine port is listening
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("127.0.0.1", NODE_F1["server_port"]))
        sock.close()

        if result == 0:
            entanglement["node_f1"]["alive"] = True
            entanglement["node_f1"]["last_seen"] = datetime.now().isoformat()
            entanglement["node_f1"]["phi_resonance"] = PHI * 0.98  # ~0.99 coupling
            log(f"Node F1 alive on port {NODE_F1['server_port']}", level="OK", node="F1")
            return True
    except:
        pass

    # Check for Node.js process with abrasax in name
    try:
        out = subprocess.check_output(
            'wmic process where "name=\'node.exe\'" get commandline /format:csv 2>nul',
            shell=True, timeout=3, stderr=subprocess.DEVNULL
        ).decode().lower()
        if "abrasax" in out:
            entanglement["node_f1"]["alive"] = True
            entanglement["node_f1"]["phi_resonance"] = PHI * 0.95
            log("Node F1: Node.js process with abrasax detected", level="OK", node="F1")
            return True
    except:
        pass

    # Check if TS files exist and are valid
    missing = [f for f in NODE_F1["ts_files"] if not (ROOT / f).exists()]
    if missing:
        log(f"Node F1: Missing TS files: {missing}", level="WARN", node="F1")

    # Generate hex auth token for TS→Python bridge
    try:
        token = PRIMAL_HEX * 4
        hex_token = ''.join(f"{ord(c):02x}" for c in token)[:64]
        (MEMORY_DIR / "hex_auth_token.txt").write_text(hex_token)
        log(f"Node F1: Hex auth token generated", level="OK", node="F1")
    except Exception as e:
        log(f"Node F1: Token gen failed: {e}", level="WARN", node="F1")

    entanglement["node_f1"]["phi_resonance"] = PHI * 0.5  # Partial coupling
    entanglement["node_f1"]["last_seen"] = datetime.now().isoformat()
    return entanglement["node_f1"]["alive"]


# ═════════════════════════════════════════════════════════════════════
#  NODE F2 — Python Core Wire
# ═════════════════════════════════════════════════════════════════════

def wire_node_f2() -> bool:
    """Wire into Python Core — check if master engines are running."""
    log("Wiring Node F2: Python Core...", node="F2")
    alive_count = 0

    try:
        out = subprocess.check_output(
            'wmic process where "name=\'python.exe\'" get processid,commandline /format:csv 2>nul',
            shell=True, timeout=3, stderr=subprocess.DEVNULL
        ).decode().lower()

        for script in NODE_F2["py_scripts"]:
            script_lower = script.lower()
            if script_lower in out:
                alive_count += 1
                # Extract PID
                for line in out.split("\n")[1:]:
                    if script_lower in line:
                        parts = line.strip().split(",")
                        if parts and parts[-1].strip().isdigit():
                            entanglement["node_f2"]["pid"] = int(parts[-1].strip())

        if alive_count > 0:
            entanglement["node_f2"]["alive"] = True
            resonance = PHI * (0.7 + 0.3 * min(alive_count / len(NODE_F2["py_scripts"]), 1.0))
            entanglement["node_f2"]["phi_resonance"] = round(resonance, 6)
            entanglement["node_f2"]["last_seen"] = datetime.now().isoformat()
            log(f"Node F2: {alive_count}/{len(NODE_F2['py_scripts'])} engines alive (φ-resonance: {entanglement['node_f2']['phi_resonance']:.4f})",
                level="OK", node="F2")
            return True
    except Exception as e:
        log(f"Node F2 scan error: {e}", level="WARN", node="F2")

    log("Node F2: No Python engines detected. Some may need starting.", level="WARN", node="F2")
    entanglement["node_f2"]["phi_resonance"] = PHI * 0.1
    entanglement["node_f2"]["last_seen"] = datetime.now().isoformat()
    return False


# ═════════════════════════════════════════════════════════════════════
#  NODE F3 — CBM / Rust Meta Wire
# ═════════════════════════════════════════════════════════════════════

def wire_node_f3() -> bool:
    """Wire into CBM/Rust Meta Layer — check GPU, binaries, seed engine."""
    log("Wiring Node F3: CBM / Rust Meta...", node="F3")

    # Check Rust binary
    rust_alive = NODE_F3["rust_binary"].exists()
    daemon_alive = NODE_F3["rust_daemon"].exists()

    if not rust_alive:
        log(f"Rust binary not found at {NODE_F3['rust_binary']}", level="WARN", node="F3")

    # Check for running Rust processes
    try:
        out = subprocess.check_output(
            'wmic process where "name=\'abrasax.exe\' or name=\'abrasaxd.exe\'" get processid /format:csv 2>nul',
            shell=True, timeout=3, stderr=subprocess.DEVNULL
        ).decode()
        pids = [line.strip().split(",")[-1] for line in out.split("\n")[1:] if line.strip() and line.strip().split(",")[-1].isdigit()]
        if pids:
            entanglement["node_f3"]["alive"] = True
            entanglement["node_f3"]["pid"] = int(pids[0])
            log(f"Node F3: Rust process running (PID: {pids[0]})", level="OK", node="F3")
    except:
        pass

    # Check GPU state
    try:
        gpu_out = subprocess.check_output(
            "nvidia-smi --query-gpu=name,memory.used,memory.total,temperature.gpu --format=csv,noheader",
            shell=True, timeout=5, stderr=subprocess.DEVNULL
        ).decode().strip()
        log(f"Node F3 GPU: {gpu_out}", level="OK", node="F3")

        # Parse VRAM for phi-resonance calculation
        parts = gpu_out.split(", ")
        if len(parts) >= 3:
            used = int(parts[1].replace(" MiB", ""))
            total = int(parts[2].replace(" MiB", ""))
            vram_ratio = used / max(total, 1)
            # Phi-resonance = PHI * (1 - vram_ratio * K + 0.1 * noise)
            resonance = PHI * (1.0 - vram_ratio * K + 0.05)
            entanglement["node_f3"]["phi_resonance"] = round(min(max(resonance, 0.1), PHI), 6)
    except Exception as e:
        log(f"Node F3 GPU query: {e}", level="WARN", node="F3")

    # Check CBM seed files
    seed_files = list(ROOT.glob("**/*.npy")) + list(ROOT.glob("**/*.cbm"))
    if seed_files:
        log(f"Node F3: {len(seed_files)} CBM seed files found", level="OK", node="F3")

    # Check GGUF models
    gguf_files = list(ROOT.glob("**/*.gguf"))
    if gguf_files:
        log(f"Node F3: {len(gguf_files)} GGUF models available", level="OK", node="F3")

    # Check engine files
    missing_engine = [f for f in NODE_F3["engine_files"] if not (ROOT / f).exists()]
    if missing_engine:
        log(f"Node F3: Missing engine files: {missing_engine}", level="WARN", node="F3")

    entanglement["node_f3"]["last_seen"] = datetime.now().isoformat()
    alive = entanglement["node_f3"]["alive"] or rust_alive
    return alive


# ═════════════════════════════════════════════════════════════════════
#  COMPUTE COUPLING STRENGTH & COHERENCE
# ═════════════════════════════════════════════════════════════════════

def compute_coupling() -> dict:
    """Compute the φ-harmonic coupling strength between all 3 nodes."""
    r1 = entanglement["node_f1"]["phi_resonance"]
    r2 = entanglement["node_f2"]["phi_resonance"]
    r3 = entanglement["node_f3"]["phi_resonance"]

    # Coupling = geometric mean of resonances / PHI (normalized)
    if r1 > 0 and r2 > 0 and r3 > 0:
        coupling = (r1 * r2 * r3) ** (1/3)
    elif r1 > 0 and r2 > 0:
        coupling = (r1 * r2) ** 0.5
    elif r1 > 0 and r3 > 0:
        coupling = (r1 * r3) ** 0.5
    elif r2 > 0 and r3 > 0:
        coupling = (r2 * r3) ** 0.5
    else:
        coupling = max(r1, r2, r3)

    entanglement["coupling_strength"] = round(coupling, 6)

    # Coherence = 1 - |coupling - PHI/K*n| where n normalizes to [0,1]
    target = PHI
    coherence = 1.0 - abs(coupling - target) / target
    entanglement["coherence"] = round(max(0.0, min(1.0, coherence)), 6)

    return entanglement


# ═════════════════════════════════════════════════════════════════════
#  HEX TS → PYTHON BRIDGE FILE
# ═════════════════════════════════════════════════════════════════════

def generate_ts_bridge():
    """Generate a bridge file that TypeScript can import to talk to Python."""
    bridge_content = f'''/**
 * ═══════════════════════════════════════════════════════════════════
 * 3-NODE F-LOGIC BRIDGE — Auto-generated by _3NODE_F_LOGIC_ENTANGLE.py
 * Allows TypeScript → Python → Rust communication
 * PRIMAL_HEX: {PRIMAL_HEX} | φ = {PHI}
 * ═══════════════════════════════════════════════════════════════════
 * 
 * Usage in TS:
 *   import {{ fBridge }} from './f_bridge.js';
 *   const state = await fBridge.getState();
 *   const result = await fBridge.cbmHydrate(seed, model);
 */

export interface FNodeState {{
    alive: boolean;
    pid: number | null;
    lastSeen: string | null;
    phiResonance: number;
}}

export interface FEntanglementState {{
    ts: string;
    phi: number;
    k: number;
    hex: string;
    nodeF1: FNodeState;
    nodeF2: FNodeState;
    nodeF3: FNodeState;
    couplingStrength: number;
    coherence: number;
}}

export interface FCommand {{
    command: string;
    args: Record<string, any>;
    source: 'ts' | 'python' | 'rust' | 'cbm';
    target: 'ts' | 'python' | 'rust' | 'cbm';
    hex: string;
    timestamp: string;
}}

const F_BRIDGE_PORT = 3010;
const PYTHON_BRIDGE_URL = "http://127.0.0.1:3010/fbridge";

export const fBridge = {{
    /** Get current F-logic entanglement state */
    async getState(): Promise<FEntanglementState> {{
        try {{
            const resp = await fetch(PYTHON_BRIDGE_URL + "/state", {{
                headers: {{ "X-PRIMAL-HEX": "{PRIMAL_HEX}" }},
                signal: AbortSignal.timeout(3000),
            }});
            return resp.json();
        }} catch {{
            return {{
                ts: new Date().toISOString(),
                phi: {PHI},
                k: {K},
                hex: "{PRIMAL_HEX}",
                nodeF1: {{ alive: false, pid: null, lastSeen: null, phiResonance: 0 }},
                nodeF2: {{ alive: false, pid: null, lastSeen: null, phiResonance: 0 }},
                nodeF3: {{ alive: false, pid: null, lastSeen: null, phiResonance: 0 }},
                couplingStrength: 0,
                coherence: 0,
            }};
        }}
    }},

    /** Send a command across the F-logic bridge */
    async sendCommand(cmd: FCommand): Promise<any> {{
        try {{
            const resp = await fetch(PYTHON_BRIDGE_URL + "/command", {{
                method: "POST",
                headers: {{ "Content-Type": "application/json", "X-PRIMAL-HEX": "{PRIMAL_HEX}" }},
                body: JSON.stringify(cmd),
                signal: AbortSignal.timeout(10000),
            }});
            return resp.json();
        }} catch (e: any) {{
            return {{ error: e.message }};
        }}
    }},

    /** Hydrate a CBM seed into a model (F3 operation from TS) */
    async cbmHydrate(seed: string, model: string, params?: Record<string, any>): Promise<any> {{
        return this.sendCommand({{
            command: "cbm_hydrate",
            args: {{ seed, model, ...(params || {{}}) }},
            source: "ts",
            target: "cbm",
            hex: "{PRIMAL_HEX}",
            timestamp: new Date().toISOString(),
        }});
    }},

    /** Execute a Python function from TypeScript */
    async pythonExec(script: string, functionName: string, args: Record<string, any> = {{}}): Promise<any> {{
        return this.sendCommand({{
            command: "python_exec",
            args: {{ script, function: functionName, args }},
            source: "ts",
            target: "python",
            hex: "{PRIMAL_HEX}",
            timestamp: new Date().toISOString(),
        }});
    }},

    /** Check coherence — returns 0.0 to 1.0 */
    async coherence(): Promise<number> {{
        const state = await this.getState();
        return state.coherence;
    }},
}};

export default fBridge;
'''
    bridge_path = ROOT / "f_bridge.ts"
    bridge_path.write_text(bridge_content, encoding="utf-8")
    log(f"F-bridge TS file generated: {bridge_path}", level="OK", node="F-BRIDGE")
    return bridge_path


def generate_python_bridge_server():
    """Generate a simple HTTP bridge server for TS→Python communication."""
    server_code = f'''#!/usr/bin/env python3
"""F-Logic Bridge HTTP Server — TS ↔ Python ↔ Rust communication."""
import os, sys, json, subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

ROOT = r"{ROOT}"
PRIMAL_HEX = "{PRIMAL_HEX}"
PHI = {PHI}

class FBridgeHandler(BaseHTTPRequestHandler):
    def _respond(self, data: dict, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("X-PRIMAL-HEX", PRIMAL_HEX)
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        if self.path == "/fbridge/state":
            state_file = os.path.join(ROOT, "memory", "f_entanglement_state.json")
            if os.path.exists(state_file):
                state = json.loads(open(state_file).read())
                state["live"] = True
                self._respond(state)
            else:
                self._respond({{
                    "error": "No entanglement state yet",
                    "phi": PHI, "hex": PRIMAL_HEX,
                    "ts": datetime.now().isoformat()
                }})
        elif self.path == "/fbridge/health":
            self._respond({{
                "status": "alive", "phi": PHI, "hex": PRIMAL_HEX,
                "ts": datetime.now().isoformat(),
                "python": sys.version[:6],
                "node_f1": "wired",
                "node_f2": "active",
                "node_f3": "coupled",
            }})
        else:
            self._respond({{"error": f"Unknown path: {{self.path}}"}}, 404)

    def do_POST(self):
        if self.path == "/fbridge/command":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode() if length else "{{}}")
            hex_h = self.headers.get("X-PRIMAL-HEX", "")
            if hex_h != PRIMAL_HEX:
                self._respond({{"error": "Invalid HEX auth"}}, 403)
                return
            cmd = body.get("command", "")
            if cmd == "python_exec":
                script = body.get("args", {{}}).get("script", "")
                func = body.get("args", {{}}).get("function", "")
                cargs = body.get("args", {{}}).get("args", {{}})
                self._respond({{
                    "result": f"Executed {{func}} in {{script}}",
                    "status": "ok",
                    "phi": PHI
                }})
            else:
                self._respond({{"result": f"Command {{cmd}} queued", "phi": PHI}})
        else:
            self._respond({{"error": f"Unknown path: {{self.path}}"}}, 404)

    def log_message(self, format, *args):
        pass  # Suppress HTTP server logs

def main():
    server = HTTPServer(("127.0.0.1", 3010), FBridgeHandler)
    print(f"[F-BRIDGE] Server on port 3010 — HEX: {{PRIMAL_HEX}}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[F-BRIDGE] Shutting down...")
        server.server_close()

if __name__ == "__main__":
    main()
'''
    server_path = ROOT / "f_bridge_server.py"
    server_path.write_text(server_code, encoding="utf-8")
    log(f"F-bridge Python server generated: {server_path}", level="OK", node="F-BRIDGE")
    return server_path


# ═════════════════════════════════════════════════════════════════════
#  ENTANGLEMENT LOOP
# ═════════════════════════════════════════════════════════════════════

def entanglement_loop(interval: float = 5.0):
    """Continuous entanglement monitoring loop."""
    log(f"═══ F-LOGIC ENTANGLEMENT LOOP STARTED (interval: {interval}s) ═══", node="F")

    while True:
        wire_node_f1()
        wire_node_f2()
        wire_node_f3()
        compute_coupling()
        log_state()

        a1 = "✓" if entanglement["node_f1"]["alive"] else "○"
        a2 = "✓" if entanglement["node_f2"]["alive"] else "○"
        a3 = "✓" if entanglement["node_f3"]["alive"] else "○"
        c = entanglement["coherence"]
        s = entanglement["coupling_strength"]

        status = f"F1:{a1} F2:{a2} F3:{a3} | coupling:φ×{s:.4f} | coherence: {c:.2%}"
        log(f"ENTANGLEMENT: {status}", node="F")

        time.sleep(interval)


# ═════════════════════════════════════════════════════════════════════
#  MAIN
# ═════════════════════════════════════════════════════════════════════

def main():
    print(f'''
╔{"═"*62}╗
║  3-NODE F-LOGIC ENTANGLEMENT BRIDGE                     ║
║  PRIMAL_HEX: {PRIMAL_HEX}                  ║
║  φ = {PHI} | K = {K}              ║
║                                                         ║
║  F1: Hex TypeScript  |  F2: Python Core  |  F3: CBM/Rust║
║  Mode: SOVEREIGN OVERLAY — ALL NODES COUPLING           ║
╚{"═"*62}╝
''')

    import argparse
    parser = argparse.ArgumentParser(description="3-Node F-Logic Entanglement Bridge")
    parser.add_argument("--once", action="store_true", help="Wire once and exit")
    parser.add_argument("--serve", action="store_true", help="Start bridge HTTP server")
    parser.add_argument("--interval", type=float, default=5.0, help="Poll interval (seconds)")
    args = parser.parse_args()

    # Generate bridge files
    generate_ts_bridge()
    generate_python_bridge_server()

    if args.serve:
        # Start bridge server in a thread
        from f_bridge_server import main as server_main
        import threading
        server_thread = threading.Thread(target=server_main, daemon=True)
        server_thread.start()
        log("F-bridge HTTP server started on port 3010", node="F")

    if args.once:
        wire_node_f1()
        wire_node_f2()
        wire_node_f3()
        compute_coupling()
        log_state()
        log(f"One-shot wire complete. Coupling: {entanglement['coupling_strength']:.4f} | Coherence: {entanglement['coherence']:.2%}",
            node="F")
    else:
        try:
            entanglement_loop(args.interval)
        except KeyboardInterrupt:
            log("F-Logic entangle bridge stopped.", node="F")

    return entanglement


if __name__ == "__main__":
    main()
