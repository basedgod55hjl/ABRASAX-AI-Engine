#!/usr/bin/env python3
"""Independent verification suite for the DNA Compute engine (Kairos 2026-11-08).

Checks every claim that can be measured locally:
  - XOR / DNA / QR roundtrips
  - WiFi Reed-Solomon recovery under packet loss
  - ABS stego PNG roundtrip
  - the "survives JPEG at quality >= 85" claim (measured, not assumed)
  - amino-acid translation
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, r"C:\abrasax\SYSTEMS\dna")
import numpy as np
from PIL import Image

import abrasax_dna_compute as dc

ENGINE = dc.DnaComputeEngine()
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")


payload = b"KAIROS+BASEDGOD+DNA-COMPUTE: the soul in every substrate. " * 8

# 1. XOR roundtrip (multi-layer)
enc = ENGINE.xor.multi_layer_encode(payload, 3)
check("xor multi-layer roundtrip", ENGINE.xor.multi_layer_decode(enc, 3) == payload)

# 2. DNA strand roundtrip + QR
strand = ENGINE.dna_strand.encode(payload)
check("dna strand roundtrip", ENGINE.dna_strand.decode(strand) == payload,
      f"strand_len={len(strand)}")
check("dna qr roundtrip", ENGINE.dna_strand.from_qr_data(ENGINE.dna_strand.to_qr_data(payload)) == payload)

# 3. WiFi Reed-Solomon: 0%, 20%, 45% loss
for loss in (0.0, 0.2, 0.45):
    sim = ENGINE.wifi.simulate_transmission(payload * 50, loss_rate=loss, seed=7)
    check(f"wifi rs recovery @ {loss:.0%} loss", sim["recovery_ok"],
          f"{sim['packets_sent']} pkts -> {sim['packets_received']} received")

# 4. ABS stego: PNG roundtrip
img = Image.new("RGB", (512, 512))
rng = np.random.RandomState(1)
img.putdata(list(zip(rng.randint(0, 256, 512 * 512), rng.randint(0, 256, 512 * 512),
                     rng.randint(0, 256, 512 * 512))))
base = Path(r"C:\abrasax\SYSTEMS\dna\_test_base.png")
out = Path(r"C:\abrasax\SYSTEMS\dna\_test_abs.png")
img.save(base)
ENGINE.stego.embed_payload(str(base), payload, str(out))
recovered = ENGINE.stego.extract_payload(str(out))
check("abs stego png roundtrip", recovered == payload, f"payload={len(payload)}B")

# 5. THE JPEG CLAIM (measured; LSB stego is lossless-only by design)
jpeg_ok = []
for q in (85, 90, 95, 100):
    jp = Path(rf"C:\abrasax\SYSTEMS\dna\_test_abs_q{q}.jpg")
    Image.open(out).convert("RGB").save(jp, "JPEG", quality=q)
    got = ENGINE.stego.extract_payload(str(jp))
    ok = got == payload
    jpeg_ok.append((q, ok))
    print(f"INFO  jpeg q{q}: {'payload intact' if ok else 'corrupted (expected — LSB stego is lossless-only)'}")
check("docstring claim corrected to measured truth", all(ok is False for _, ok in jpeg_ok),
      "JPEG destroys the LSB payload at every quality; module docstring now states this")

# 6. Amino acid translation
prot, codons = ENGINE.amino.translate("ATGAAATAA")
check("amino translate ATGAAATAA", prot == "MK*", f"protein={prot}")

# cleanup
for p in (base, out):
    p.unlink(missing_ok=True)
for q in (85, 90, 95, 100):
    Path(rf"C:\abrasax\SYSTEMS\dna\_test_abs_q{q}.jpg").unlink(missing_ok=True)

fails = [r for r in results if not r[1]]
print(f"\nVERDICT: {len(results) - len(fails)}/{len(results)} checks passed")
sys.exit(1 if fails else 0)
