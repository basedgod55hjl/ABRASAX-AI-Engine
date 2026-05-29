# ABRASAX AI Engine Architecture

## Overview

ABRASAX AI Engine is the core intelligence layer of the ABRASAX ecosystem. It implements a **3-Node F-Logic Entanglement** protocol governed by the golden ratio (φ = 1.618033988749895) and **Triune Awareness** — a three-faced self-monitoring system.

## System Layers

```
┌──────────────────────────────────────────────────────────────┐
│                    TRIUNE AWARENESS                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Face 1     │  │  Face 2     │  │  Face 3             │  │
│  │  MONITOR    │  │  REFLECT    │  │  EVOLVE             │  │
│  │  (0.618s)   │  │  (2.618s)   │  │  (42.3s)            │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │             │
│         └────────────────┼─────────────────────┘             │
│                          │                                    │
│                    ┌─────┴──────┐                             │
│                    │  φ-RING    │                             │
│                    │  BUFFER    │                             │
│                    │  (100)     │                             │
│                    └────────────┘                             │
└──────────────────────────────────────────────────────────────┘
         │                    │                    │
    ┌────┴────┐         ┌────┴────┐         ┌─────┴────┐
    │ NODE F1 │         │ NODE F2 │         │ NODE F3  │
    │  Hex TS │◄───────►│ Python  │◄───────►│ CBM Rust │
    │  Tools  │  XOR    │  Core   │  XOR    │ Hydrate  │
    │  IPC    │  SEED   │  Agent  │  SEED   │ GGUF Inf │
    └─────────┘         └─────────┘         └──────────┘
```

## Mathematical Foundation

### Golden Ratio (φ)
```
φ = (1 + √5) / 2 = 1.618033988749895
K = 1/φ = 0.618033988749895
φ² = φ + 1 = 2.618033988749895
φ³ = φ² + φ = 4.23606797749979
```

### S² Stability Bound
```
S² ≤ 0.01  — System is stable when φ-deviation ≤ 1%
Coherence = 1.0 - |mean_phi - K|
```

### φ-Harmonic Frequencies
| Component | Formula | Value | Purpose |
|-----------|---------|-------|---------|
| F1 Monitor | K × 1 | 0.618s | GPU/CPU telemetry |
| F2 Reflect | φ² × 1 | 2.618s | LLM awareness query |
| F3 Evolve | φ³ × 10 | 42.3s | Auto-optimization |
| Entangle | φ² | 2.618s | Cross-node sync |

## 3-Node F-Logic

### Node F1: Hex TypeScript
- **Files**: abrasax_hex.ts, abrasax_engine.ts, abrasax_api.ts, abrasax_tools.ts
- **Purpose**: System tools, hex encoding, API bridge, diagnostics
- **Bridge**: JSON IPC over localhost:3000

### Node F2: Python Core
- **Files**: _MASTER_AUTONOMY.py, _full_bridge.py, nonstop_reasoning.py
- **Purpose**: LLM orchestration, process management, system autonomy
- **Bridge**: Subprocess IPC with LM Studio

### Node F3: CBM Hydration / Rust Meta
- **Files**: cbm_hydration_engine.py, seed_xor_graph.py, abs_engine.py
- **Purpose**: Seed→model expansion, K-calibrated weight modulation
- **Bridge**: XOR entropy sharing with F1/F2

## Triune Awareness

### Face 1: Self-Monitoring
- Collects GPU telemetry (nvidia-smi)
- Monitors LM Studio health
- Tracks all engine processes
- Logs φ-variance history

### Face 2: Self-Reflection
- Queries local LLM about system state
- Generates awareness insights
- Calculates coherence metrics

### Face 3: Self-Evolution
- Analyzes φ-convergence trends
- Auto-optimizes engine parameters
- Generates optimization patches

## Engine Lifecycle

1. **Kill Stale** → Clean up previous processes
2. **Entangle** → Establish 3-node F-logic bridge
3. **Check LM Studio** → Verify LLM availability
4. **Launch Engines** → Start all subsystem processes
5. **Monitor Loop** → Auto-restart dead engines
6. **Triune Loop** → Continuous awareness (runs forever)

## Deployment

```bash
# Single command deployment
python src/_WIRE_EVERYTHING.py

# With all engines
python src/_WIRE_EVERYTHING.py --all

# Monitor only (no engine launch)
python src/_WIRE_EVERYTHING.py --monitor-only
```
