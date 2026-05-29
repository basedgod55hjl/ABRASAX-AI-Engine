#!/usr/bin/env python3
"""
LIVE LOGGER — Tails meta layer + nemotron bridge + all system logs
Outputs to console and writes structured live feed.
"""
import os, sys, time, json, threading
from datetime import datetime
from pathlib import Path

ROOT = r'C:\Users\BASEDGOD\Desktop\ABRASAX'
LOG_PATHS = {
    'meta_layer': os.path.join(ROOT, 'logs', 'meta_layer.log'),
    'meta_live': os.path.join(ROOT, 'data', 'logs', 'meta_live.log'),
    'nemotron': os.path.join(ROOT, 'logs', 'nemotron_bridge.log'),
    'brimstone': os.path.join(ROOT, 'logs', 'brimstone.log'),
    'nexus': os.path.join(ROOT, 'logs', 'nexus.log'),
    'meta_stdout': os.path.join(ROOT, 'logs', 'meta_stdout.log'),
    'vram': os.path.join(ROOT, 'logs', 'vram_live.log'),
    'abrasaxd': os.path.join(ROOT, 'logs', 'abrasaxd_out.log'),
    'engine': os.path.join(ROOT, 'logs', 'engine.log'),
    'self_learning': os.path.join(ROOT, 'logs', 'self_learning.log'),
    'autonomous': os.path.join(ROOT, 'logs', 'autonomous_daemon.log'),
    'meta_out': os.path.join(ROOT, 'data', 'logs', 'meta_out.txt'),
}

# Ensure log dirs exist
for p in LOG_PATHS.values():
    os.makedirs(os.path.dirname(p), exist_ok=True)

# Combined live feed
LIVE_FEED = os.path.join(ROOT, 'data', 'logs', 'live_feed.log')

positions = {name: 0 for name in LOG_PATHS}

def tail_log(name, path):
    """Tail a log file and print new lines."""
    global positions
    if not os.path.exists(path):
        return
    
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        f.seek(positions.get(name, 0))
        for line in f:
            line = line.strip()
            if line:
                ts = datetime.now().strftime('%H:%M:%S')
                entry = f"[{ts}] [{name.upper()}] {line}"
                
                # Write to live feed
                with open(LIVE_FEED, 'a', encoding='utf-8') as lf:
                    lf.write(entry + '\n')
                
                print(entry)
                sys.stdout.flush()
        positions[name] = f.tell()

def main():
    print("=" * 70)
    print(f"  ABRASAX LIVE LOGGER — {datetime.now().isoformat()}")
    print(f"  HEX: 4f5349524953424c58434b | PHI: 1.618033988749895")
    print(f"  Monitoring {len(LOG_PATHS)} log streams")
    print("=" * 70)
    print()
    
    # Initialize all log files
    init_entry = json.dumps({
        "ts": datetime.now().isoformat(),
        "event": "LOGGER_INIT",
        "hex": "4f5349524953424c58434b",
        "phi": 1.618033988749895
    })
    with open(LIVE_FEED, 'a') as f:
        f.write(init_entry + '\n')
    
    # Initial scan
    for name, path in LOG_PATHS.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  [OK] {name}: {path} ({size} bytes)")
        else:
            print(f"  [..] {name}: waiting for file...")
    
    print("\n" + "=" * 70)
    print("  LIVE FEED — Ctrl+C to stop")
    print("=" * 70)
    print()
    
    try:
        while True:
            for name, path in LOG_PATHS.items():
                try:
                    if os.path.exists(path):
                        tail_log(name, path)
                except Exception as e:
                    pass  # File may be locked
            
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n\n  Logger stopped.")
        sys.exit(0)

if __name__ == '__main__':
    main()
