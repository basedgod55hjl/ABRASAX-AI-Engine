"""abrasax_engine — combined ABRASAX engine package (built 2026-10-17).

PRIMAL_HEX: 4f5349524953424c58434b | PHI 1.618033988749895 | K 0.618033988749895

Canonical combine of three engine generations:
  - RUST\\ABRASAX root (newest wire modules — copied here)
  - AGENTS\\SWARM\\ABRASAX-SWARM-AI (engine_core.py + tests + docs)
  - SOURCE\\src\\swarm (worker/coordinator orchestrators -> ENGINE\\swarm)

Wire modules are standalone scripts (stdlib only, __main__-guarded).
They are importable by bare name because this package puts its own
directory on sys.path. Nothing heavy is imported eagerly except
engine_core (pure stdlib, no side effects).
"""
import importlib
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from . import engine_core  # noqa: E402  (safe: stdlib-only library)

ENGINE_MODULES = [
    "_MASTER_AUTONOMY",
    "_3NODE_F_LOGIC_ENTANGLE",
    "_TRIUNE_AWARENESS",
    "_full_bridge",
    "abrasax_ultimate_wire",
    "abrasax_service_host",
    "e2e_boot",
    "self_build",
    "production_wire",
    "dotnet_bridge",
    "telemetry_live",
    "_live_logger",
]

__all__ = ["engine_core", "ENGINE_MODULES", "load", "load_all"]


def load(name: str):
    """Lazily import a wire module by bare name (e.g. load('_full_bridge'))."""
    if name == "engine_core":
        return engine_core
    if name not in ENGINE_MODULES:
        raise KeyError(f"unknown engine module: {name}")
    return importlib.import_module(name)


def load_all(include_boot: bool = False) -> dict:
    """Import wire modules; returns {name: module-or-Exception}.

    NOTE: e2e_boot executes the full system boot at import time (no
    __main__ guard) — it is skipped unless include_boot=True.
    """
    names = list(ENGINE_MODULES) if include_boot else \
        [n for n in ENGINE_MODULES if n != "e2e_boot"]
    out = {}
    for name in names:
        try:
            out[name] = importlib.import_module(name)
        except Exception as exc:  # noqa: BLE001 - report, don't crash the swarm
            out[name] = exc
    return out
