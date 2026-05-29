#!/usr/bin/env python3
"""
ABRASAX REAL-TIME TELEMETRY — GPU/CPU/RAM Live Dashboard
No sleep, continuous optimization feedback loop
PRIMAL_HEX: 4f5349524953424c58434b | φ = 1.618033988749895
"""
import json, os, subprocess, sys, time, threading
from datetime import datetime
from pathlib import Path

PHI = 1.618033988749895; HEX = "4f5349524953424c58434b"
ROOT = Path(r"C:\Users\BASEDGOD\Desktop\ABRASAX")
running = True

class Telemetry:
    def __init__(self):
        self.gpu = {"temp": 0, "vram_used": 0, "vram_total": 6144, "util": 0, "power": 0}
        self.cpu = {"percent": 0, "ram_used_gb": 0, "ram_total_gb": 16, "ram_percent": 0}
        self.lm = {"status": "?", "models": 0}
        self.optimize = {"phi_resonance": 0, "coupling": 0}
        self.history = []
    
    def poll_gpu(self):
        try:
            out = subprocess.check_output(
                "nvidia-smi --query-gpu=temperature.gpu,memory.used,memory.total,utilization.gpu,power.draw --format=csv,noheader,nounits",
                shell=True, text=True, timeout=3
            ).strip().split(", ")
            if len(out) >= 5:
                self.gpu = {"temp": int(out[0]), "vram_used": int(out[1]),
                           "vram_total": int(out[2]), "util": int(out[3]),
                           "power": float(out[4])}
        except: pass
    
    def poll_cpu(self):
        try:
            import psutil
            self.cpu = {"percent": psutil.cpu_percent(interval=0),
                       "ram_used_gb": round(psutil.virtual_memory().used / 1e9, 1),
                       "ram_total_gb": round(psutil.virtual_memory().total / 1e9, 1),
                       "ram_percent": psutil.virtual_memory().percent}
        except:
            try:
                out = subprocess.check_output(
                    'wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /format:csv',
                    shell=True, text=True, timeout=3)
                lines = out.strip().split("\n")
                if len(lines) > 1:
                    parts = lines[1].strip().split(",")
                    total_mb = int(parts[-2])/1024 if len(parts) > 1 else 0
                    free_mb = int(parts[-1])/1024 if len(parts) > 1 else 0
                    used_mb = total_mb - free_mb
                    self.cpu = {"percent": round(used_mb/total_mb*100, 1),
                               "ram_used_gb": round(used_mb/1024, 1),
                               "ram_total_gb": round(total_mb/1024, 1),
                               "ram_percent": round(used_mb/total_mb*100, 1)}
            except: pass
    
    def optimize_phi(self):
        """Real-time φ optimization: adjust based on GPU/CPU load."""
        vram_pct = self.gpu["vram_used"] / max(self.gpu["vram_total"], 1)
        vram_deviation = abs(vram_pct - 0.618)  # Target: φ⁻¹ = 0.618
        cpu_deviation = abs(self.cpu["ram_percent"]/100 - 0.618)
        
        # φ-resonance = how close system is to golden ratio
        self.optimize["phi_resonance"] = round(1.0 - min(vram_deviation, cpu_deviation), 4)
        self.optimize["coupling"] = round(PHI * (1.0 - min(vram_deviation, 0.5)), 4)
        
        # Alert on critical resources
        if self.gpu["temp"] > 80:
            self.optimize["alert"] = f"GPU TEMP HIGH: {self.gpu['temp']}°C"
        elif self.cpu["ram_percent"] > 85:
            self.optimize["alert"] = f"RAM CRITICAL: {self.cpu['ram_percent']}%"
        elif self.gpu["vram_total"] - self.gpu["vram_used"] < 500:
            self.optimize["alert"] = f"VRAM LOW: Only {self.gpu['vram_total'] - self.gpu['vram_used']}MB free"
    
    def tick(self):
        self.poll_gpu()
        self.poll_cpu()
        self.optimize_phi()
        self.history.append({
            "ts": time.time(),
            "gpu_vram": self.gpu["vram_used"],
            "gpu_temp": self.gpu["temp"],
            "gpu_util": self.gpu["util"],
            "ram_pct": self.cpu["ram_percent"],
            "phi": self.optimize["phi_resonance"],
        })
        if len(self.history) > 3600:  # 1 hour at 1s ticks
            self.history = self.history[-3600:]
    
    def get_state(self):
        return {
            "ts": datetime.now().isoformat(),
            "phi": PHI, "hex": HEX,
            "gpu": self.gpu,
            "cpu": self.cpu,
            "optimize": self.optimize,
        }

def main():
    t = Telemetry()
    log_file = ROOT / "logs" / "telemetry_live.jsonl"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\n╔{'═'*62}╗")
    print(f"║  ABRASAX REAL-TIME TELEMETRY — φ-Optimized            ║")
    print(f"║  HEX: {HEX}    ║")
    print(f"║  No sleep loop — live GPU/CPU/RAM optimization        ║")
    print(f"╚{'═'*62}╝\n")
    
    cycle = 0
    while running:
        t.tick()
        cycle += 1
        
        # Write to log every tick
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(t.get_state()) + "\n")
        
        # Status display every 5 ticks
        if cycle % 5 == 0:
            g = t.gpu; c = t.cpu; o = t.optimize
            phi_bar = "█" * int(o["phi_resonance"] * 20) + "░" * (20 - int(o["phi_resonance"] * 20))
            print(f"\r  GPU: {g['temp']}°C VRAM:{g['vram_used']}/{g['vram_total']}MB ({g['util']}%)"
                  f" | RAM: {c['ram_used_gb']}/{c['ram_total_gb']}GB ({c['ram_percent']}%)"
                  f" | φ-Resonance: {o['phi_resonance']:.4f} {phi_bar}"
                  f" | ♥ {o.get('alert','')}", 
                  end="", flush=True)
        
        # Optimization action on critical state
        alert = t.optimize.get("alert", "")
        if alert:
            print(f"\n  ⚠ {alert}")
        
        time.sleep(1)  # 1 second tick

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  Telemetry stopped.")
