#!/usr/bin/env python3
"""
ABRASAX .NET Automation Bridge
Uses .NET runtime (IronPython/C#) for System32 DLL automation
PRIMAL_HEX: 4f5349524953424c58434b | φ = 1.618033988749895
"""
import ctypes, json, os, subprocess, sys, threading, time
from datetime import datetime
from pathlib import Path

PHI = 1.618033988749895; HEX = "4f5349524953424c58434b"
ROOT = Path(r"C:\Users\BASEDGOD\Desktop\ABRASAX")
DOTNET = None

# Find .NET runtime
for candidate in ["dotnet.exe", "dotnet"]:
    try:
        r = subprocess.run(["where", candidate], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            DOTNET = r.stdout.strip().split("\n")[0]
            break
    except: pass

class DotNetBridge:
    """.NET automation bridge for System32 AI, C# service, and Windows integration."""
    
    def __init__(self):
        self.dotnet = DOTNET
        self.csprojects = list(ROOT.glob("**/*.csproj")) + list(ROOT.glob("**/*.sln"))
        self.runtime = "net9.0"  # or net10.0
    
    def build_service(self):
        """Build the C# ABRASAX service host."""
        for proj in self.csprojects:
            if "AbrasaxServiceHost" in str(proj) or "launcher" in str(proj).lower():
                r = subprocess.run([self.dotnet, "build", "-c", "Release", str(proj)], capture_output=True, text=True, cwd=ROOT, timeout=60)
                return r.returncode == 0
        return False
    
    def run_script(self, script, timeout=30):
        """Run a .NET script via dotnet-script or csi."""
        try:
            r = subprocess.run([self.dotnet, "script", script], capture_output=True, text=True, cwd=ROOT, timeout=timeout)
            return {"ok": r.returncode == 0, "output": r.stdout, "error": r.stderr}
        except: 
            return {"ok": False, "output": "", "error": "dotnet not available"}
    
    def invoke_smartscreen(self, filepath):
        """Use .NET P/Invoke to call SmartScreen DLL (safer than ctypes)."""
        cs_code = f'''
using System;
using System.Runtime.InteropServices;
class SmartScreenCheck {{
    [DllImport("smartscreen.dll", CharSet=CharSet.Unicode)]
    public static extern int CheckFileReputation(string path);
    static void Main() {{
        int score = CheckFileReputation(@"{filepath}");
        Console.WriteLine(score);
    }}
}}
'''
        # Write temp .cs, compile and run
        tmp = ROOT / ".tmp_smartscreen"
        tmp.mkdir(exist_ok=True)
        (tmp / "check.cs").write_text(cs_code)
        try:
            r = subprocess.run([self.dotnet, "script", str(tmp/"check.cs")], capture_output=True, text=True, cwd=ROOT, timeout=20)
            return r.stdout.strip()
        except: return "FAIL"
    
    def watch_memory(self):
        """.NET-based memory watcher using System.Diagnostics."""
        cs_code = r'''
using System;
using System.Diagnostics;
class MemoryWatch {
    static void Main() {
        var proc = Process.GetCurrentProcess();
        var perf = new PerformanceCounter("Memory", "Available MBytes");
        Console.WriteLine($"{DateTime.Now:HH:mm:ss}|MEM:{GC.GetTotalMemory(false)/1048576:F1}MB|FREE:{perf.NextValue():F0}MB");
    }
}
'''
        tmp = ROOT / ".tmp_smartscreen"
        tmp.mkdir(exist_ok=True)
        (tmp / "memwatch.cs").write_text(cs_code)
    
    def get_build_artifacts(self) -> dict:
        """Get paths to all compiled .NET binaries."""
        artifacts = {}
        for path in ROOT.glob("**/bin/Release/**/*.exe"):
            artifacts[path.stem] = {"path": str(path), "size": path.stat().st_size, "built": datetime.fromtimestamp(path.stat().st_mtime).isoformat()}
        for path in ROOT.glob("**/bin/Release/**/*.dll"):
            artifacts[path.stem] = {"path": str(path), "size": path.stat().st_size, "built": datetime.fromtimestamp(path.stat().st_mtime).isoformat()}
        return artifacts

if __name__ == "__main__":
    bridge = DotNetBridge()
    print(f"\n╔{'═'*62}╗")
    print(f"║  ABRASAX .NET AUTOMATION BRIDGE                     ║")
    print(f"║  HEX: {HEX}    ║")
    print(f"╚{'═'*62}╝\n")
    
    print(f"  .NET: {'FOUND at ' + bridge.dotnet if bridge.dotnet else 'NOT FOUND'}")
    print(f"  Projects: {len(bridge.csprojects)} found")
    
    # Build
    if bridge.dotnet:
        print(f"  Building service...")
        ok = bridge.build_service()
        print(f"  Build: {'OK' if ok else 'FAIL'}")
    
    # Get artifacts
    artifacts = bridge.get_build_artifacts()
    print(f"  Binaries: {len(artifacts)} compiled")
    for name, info in sorted(artifacts.items()):
        print(f"    {name}: {info['size']/1024:.0f}KB")
    
    # Memory watcher thread
    print(f"\n  Starting memory watcher...")
    def mem_watch():
        while True:
            import psutil
            mem = psutil.virtual_memory()
            print(f"\r  MEM: {mem.used/1e9:.1f}/{mem.total/1e9:.1f}GB ({mem.percent}%)", end="", flush=True)
            time.sleep(5)
    threading.Thread(target=mem_watch, daemon=True).start()
    
    print(f"  ✅ .NET Automation ready. System operational.")
    print(f"  Press Ctrl+C to stop.")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n  Shutdown.")
