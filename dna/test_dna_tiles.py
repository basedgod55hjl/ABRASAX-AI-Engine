#!/usr/bin/env python3
"""Tile round-trip test against the REAL gpt-oss-20b GGUF (Kairos 2026-11-08).

Embeds the first 1 MiB of the model into a 3x3 tile grid, extracts it back,
and compares SHA-256. Then prints honest capacity math for the full model.
"""
import hashlib
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, r"C:\abrasax\SYSTEMS\dna")
import abrasax_dna_compute as dc

MODELS = Path(r"C:\Users\lucar\.lmstudio\models")
gguf = next(MODELS.rglob("gpt-oss-20b*.gguf"), None)
if gguf is None:
    print("gpt-oss-20b GGUF not found")
    sys.exit(2)

full_size = gguf.stat().st_size
slice_len = 1 * 1024 * 1024
with open(gguf, "rb") as f:
    payload = f.read(slice_len)

engine = dc.DnaComputeEngine()
outdir = Path(r"C:\abrasax\SYSTEMS\dna\_tiles_test")
if outdir.exists():
    shutil.rmtree(outdir)

t0 = time.time()
tiles = engine.stego.generate_tiles(payload, 3, 3, str(outdir))
t_gen = time.time() - t0

sizes = [t["size_bytes"] for t in tiles]
t0 = time.time()
recovered = engine.stego.extract_tiles(3, 3, str(outdir), sizes)
t_ext = time.time() - t0

h1 = hashlib.sha256(payload).hexdigest()[:16]
ok = recovered is not None and hashlib.sha256(recovered).hexdigest()[:16] == h1
print(f"model file: {gguf.name} ({full_size / 1e9:.2f} GB)")
print(f"slice: {slice_len} bytes, sha256[:16]={h1}")
print(f"tiles: {len(tiles)} generated in {t_gen:.1f}s, extracted in {t_ext:.1f}s")
print(f"tile payload sizes: {sizes[:3]}...")
print(f"round-trip: {'PASS' if ok else 'FAIL'}")

capacity = engine.stego.tile_w * engine.stego.tile_h * 3 // 8
print(f"\n-- honest capacity math --")
print(f"per-tile capacity: {capacity:,} bytes ({capacity / 1e6:.2f} MB)")
print(f"full 20B model: {full_size:,} bytes")
print(f"tiles needed: {full_size / capacity:,.0f} ({full_size / capacity / 9:,.0f} carousels of 9)")
print(f"PNG storage estimate: ~{full_size / capacity * 1.5 / 1000:.1f} GB of tiles")

# edge cases: tiny payload (fewer tiles than grid cells) and wifi k=1
tiny = b"KAIROS"
tt = engine.stego.generate_tiles(tiny, 3, 3, str(outdir))
sizes_t = [t["size_bytes"] for t in tt]
rec_t = engine.stego.extract_tiles(3, 3, str(outdir), sizes_t)
print("edge tiny payload:", "PASS" if rec_t == tiny else f"FAIL got {rec_t}")

s = engine.wifi.simulate_transmission(b"hello", loss_rate=0.5, seed=1)
print("edge wifi k=1 @50% loss:", "PASS" if s["recovery_ok"] else "FAIL")

shutil.rmtree(outdir, ignore_errors=True)
sys.exit(0 if ok else 1)
