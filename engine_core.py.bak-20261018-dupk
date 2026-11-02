#!/usr/bin/env python3
"""
ABRASAX AI Engine Core — Unified entry point.
PRIMAL_HEX: 4f5349524953424c58434b | φ: 1.618033988749895
"""
import json, os, sys, subprocess, time, urllib.request
from datetime import datetime
from pathlib import Path

PHI = 1.618033988749895
K = 0.618033988749895
HEX = "4f5349524953424c58434b"
ROOT = Path(__file__).resolve().parent.parent.parent

LM_URL = "http://127.0.0.1:1234/v1"
LM_KEY = "sk-lm-KZtEmyJA:qJJk4G0dhYrRT3kWKyQa"

def check_lm_studio():
    """Verify LM Studio is online."""
    try:
        req = urllib.request.Request(f"{LM_URL}/models",
            headers={"Authorization": f"Bearer {LM_KEY}", "Content-Type": "application/json"})
        data = json.loads(urllib.request.urlopen(req, timeout=5).read())
        models = [m["id"] for m in data.get("data", [])]
        return {"online": True, "models": models}
    except Exception as e:
        return {"online": False, "error": str(e)}

def get_gpu_telemetry():
    """Query GPU status via nvidia-smi."""
    try:
        out = subprocess.check_output(
            "nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw --format=csv,noheader,nounits",
            shell=True, text=True, timeout=5).strip().split(", ")
        return {"name": out[0], "temp_c": int(out[1]), "util_pct": int(out[2]),
                "vram_used_mb": int(out[3]), "vram_total_mb": int(out[4]), "power_w": float(out[5])}
    except:
        return {"error": "nvidia-smi unavailable"}

def phi_calibrate(current, target, lr=0.01):
    """K-damped phi-calibration."""
    tracking = current + K * (target - current)
    return tracking - lr * 0.001

if __name__ == "__main__":
    print(f"ABRASAX AI Engine Core | HEX: {HEX} | φ: {PHI}")
    llm = check_lm_studio()
    gpu = get_gpu_telemetry()
    print(f"LM Studio: {'ONLINE' if llm.get('online') else 'OFFLINE'}")
    print(f"GPU: {gpu.get('name', 'N/A')} @ {gpu.get('temp_c', '?')}°C")
