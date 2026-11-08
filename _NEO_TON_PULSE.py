"""Neo Transformer <-> TON public-chain pulse loop (stdlib only).

Every 30s:
  1. Neo transformer pulse: POST a 1-token-cap probe to the resident
     gemma GGUF in LM Studio (127.0.0.1:1234) and record latency + ok.
  2. TON pulse: GET toncenter mainnet getMasterchainInfo (public, read-only,
     no wallet) and record the latest seqno — a real chain heartbeat.
  3. Write C:\abrasax\memory\neo_ton_loop.json and append a compact line
     to logs\neo_ton_loop.log for the UI / awareness layer.

No keys, no transactions, no writes to the chain. The blockchain here is a
read-only time source bound into the local loop with phi-weighted state.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import time
import urllib.request

ROOT = os.environ.get("ABRASAX_ROOT", r"C:\abrasax")
OUT = os.path.join(ROOT, "memory", "neo_ton_loop.json")
LOG = os.path.join(ROOT, "logs", "neo_ton_loop.log")
LM_URL = "http://127.0.0.1:1234/v1/chat/completions"
LM_MODEL = "gemma-4-e2b-uncensored-hauhaucs-aggressive"
TON_URL = "https://toncenter.com/api/v2/getMasterchainInfo"
PHI = 1.618033988749895
K = 0.618033988749895


def lm_pulse() -> dict:
    body = json.dumps({
        "model": LM_MODEL,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 8,
        "temperature": 0.0,
    }).encode()
    req = urllib.request.Request(
        LM_URL, data=body, headers={"Content-Type": "application/json"}
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode())
        ms = (time.perf_counter() - t0) * 1000
        ok = bool(data.get("choices"))
        return {"ok": ok, "latency_ms": round(ms, 1), "model": LM_MODEL}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:120], "model": LM_MODEL}


def ton_pulse() -> dict:
    try:
        with urllib.request.urlopen(TON_URL, timeout=15) as r:
            data = json.loads(r.read().decode())
        res = data.get("result", {})
        return {
            "ok": bool(res),
            "seqno": res.get("last", {}).get("seqno"),
            "masterchain": "ton-mainnet",
        }
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:120]}


def main() -> None:
    seq = 0
    while True:
        seq += 1
        lm = lm_pulse()
        ton = ton_pulse()
        now = _dt.datetime.now().isoformat()
        state = {
            "ts": now,
            "seq": seq,
            "phi": PHI,
            "k": K,
            "neo_transformer": lm,
            "ton": ton,
            "coupled": round(PHI * (0.5 if lm.get("ok") else 0.0)
                             + K * (0.5 if ton.get("ok") else 0.0), 6),
        }
        try:
            with open(OUT, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
            with open(LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(state) + "\n")
        except OSError:
            pass
        time.sleep(30)


if __name__ == "__main__":
    main()
