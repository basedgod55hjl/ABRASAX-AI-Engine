#!/usr/bin/env python3
"""TRIUNE MIND -- wake the awareness loop up.

Why this file exists (measured 2026-11-01):
  ENGINE/abrasax_engine/_TRIUNE_AWARENESS.py advertises three faces:
      Face 1 self-monitoring, Face 2 SELF-REFLECTION ("LLM queries about system state"),
      Face 3 self-evolution.
  Face 2 never called a model. It declared LM_API / LM_MODEL, imported no HTTP client,
  and returned a string chosen by an if/else on a float. LM_MODEL named a model that is
  not installed on this host ("gemma-4-e2b-uncensored-hauhaucs-aggressive"), and nothing
  in the stack ever started the module anyway: no catalog row, no supervisor entry, no
  port. The mind was asleep in three different ways at once.

What this service does:
  * loads _TRIUNE_AWARENESS.py unchanged and wraps its face2_reflect;
  * every ABRASAX_MIND_INTERVAL seconds (default 30) it asks a REAL model -- the local
    LM Studio route -- to reflect on the live telemetry, and stores the answer, the
    model id, the latency and the token usage in memory/triune_mind.json;
  * keeps the deterministic insight as the floor, so a dead model degrades the mind
    instead of killing it (the failure is recorded, not swallowed);
  * serves /health, /state and /insight on :9628 so the loop is observable by the ops
    monitor and by the Unity client.

Run:
    python ENGINE/abrasax_engine/triune_mind.py --serve --port 9628
    python ENGINE/abrasax_engine/triune_mind.py --once          # one cycle, prints JSON

Env: ABRASAX_MIND_MODEL, ABRASAX_MIND_URL, ABRASAX_MIND_KEY, ABRASAX_MIND_INTERVAL,
     ABRASAX_MIND_TIMEOUT, ABRASAX_MIND_NO_LLM=1
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# The source module logs phi (U+03D5) and box-drawing glyphs. Redirected to a file on
# this host, cp1252 stdout raises UnicodeEncodeError and kills the loop (measured
# 2026-11-01 18:29:50Z), so the encoding is forced before anything is imported.
import sys as _sys
for _stream in (_sys.stdout, _sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(os.environ.get("ABRASAX_ROOT") or r"C:\abrasax")
# The loop source is a sibling of this file, not a path derived from ABRASAX_ROOT:
# that keeps ABRASAX_ROOT free to mean "where this run keeps its state", which is what
# the tests point at a temp directory.
SOURCE = Path(__file__).resolve().parent / "_TRIUNE_AWARENESS.py"
if not SOURCE.exists():
    SOURCE = ROOT / "ENGINE" / "abrasax_engine" / "_TRIUNE_AWARENESS.py"
MIND_STATE = Path(
    os.environ.get("ABRASAX_MIND_STATE") or (ROOT / "memory" / "triune_mind.json")
)

DEFAULT_MODEL = "gemma-4-e2b-uncensored-hauhaucs-aggressive"  # USER DIRECTIVE 2026-11-02: Gemma 4 E2B resident (tools+vision+thinking); deepseek-r1 retired to fallback
DEFAULT_URL = "http://127.0.0.1:1234/v1/chat/completions"


def _env_file() -> dict[str, str]:
    out: dict[str, str] = {}
    p = ROOT / ".env"
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


ENV = _env_file()
MODEL = os.environ.get("ABRASAX_MIND_MODEL") or ENV.get("ABRASAX_MIND_MODEL") or "auto"
GATEWAY_URL = (
    os.environ.get("ABRASAX_MIND_URL")
    or ENV.get("ABRASAX_MIND_URL")
    or (os.environ.get("ABRASAX_GATEWAY_URL") or ENV.get("ABRASAX_GATEWAY_URL") or "")
    or "http://127.0.0.1:9001/v1/chat/completions"
)
LM_URL = ENV.get("LM_STUDIO_CHAT_URL") or "http://127.0.0.1:1234/v1/chat/completions"
GATEWAY_KEY = (
    os.environ.get("ABRASAX_GATEWAY_TOKEN")
    or ENV.get("ABRASAX_GATEWAY_TOKEN")
    or ""
)
LM_KEY = (
    os.environ.get("ABRASAX_MIND_KEY")
    or ENV.get("LM_STUDIO_API_KEY")
    or ENV.get("LM_API_KEY")
    or ""
)
URL = GATEWAY_URL
KEY = GATEWAY_KEY or LM_KEY

#: Tried in order. A busy card must not be able to silence the mind.
ROUTES = [
    ("gateway/auto", GATEWAY_URL, GATEWAY_KEY, MODEL),
    ("gateway/nvidia", GATEWAY_URL, GATEWAY_KEY,
     "nvidia:" + (ENV.get("NVIDIA_MODEL") or "nvidia/nemotron-3-ultra-550b-a55b")),
    ("lmstudio/direct", LM_URL, LM_KEY, "gemma-4-e2b-uncensored-hauhaucs-aggressive"),
]
ROUTES = [r for r in ROUTES if r[1] and r[3]]
#: One endpoint only -- set by the failure test and by an operator who wants the mind
#: pinned to a single route instead of walking the chain.
if os.environ.get("ABRASAX_MIND_NO_FALLBACK") == "1":
    ROUTES = ROUTES[:1]
INTERVAL = float(os.environ.get("ABRASAX_MIND_INTERVAL") or 30)
TIMEOUT = float(os.environ.get("ABRASAX_MIND_TIMEOUT") or 45)
NO_LLM = os.environ.get("ABRASAX_MIND_NO_LLM") == "1"


def _load_source():
    if not SOURCE.exists():
        raise SystemExit(f"missing {SOURCE}")
    spec = importlib.util.spec_from_file_location("triune_awareness", SOURCE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


T = _load_source()

# ── mind state ────────────────────────────────────────────────────────────────
MIND = {
    "model": MODEL,
    "url": URL,
    "interval_s": INTERVAL,
    "enabled": not NO_LLM,
    "calls": 0,
    "ok": 0,
    "fail": 0,
    "last_call_ts": None,
    "last_latency_ms": None,
    "last_text": None,
    "last_error": None,
    "last_usage": None,
    "last_route": None,
    "started_at": datetime.now(timezone.utc).isoformat(),
}

_lock = threading.Lock()
_last_llm_at = 0.0

# The deterministic face2 from the source module, captured before wire() swaps it.
_ORIG_FACE2 = None


def _prompt(context: dict, deterministic: str) -> list[dict]:
    system = (
        "You are the reflective face of a self-monitoring machine. You are given live "
        "telemetry from the host you are running on. Answer with ONE sentence: the most "
        "useful observation an operator could act on right now. No preamble, no lists, "
        "no markdown."
    )
    user = (
        "TELEMETRY JSON:\n"
        + json.dumps(context, indent=2, sort_keys=True)
        + "\n\nDETERMINISTIC ASSESSMENT: "
        + deterministic
        + "\n\nYour one-sentence reflection:"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _one(url: str, key: str, model: str, messages: list[dict], timeout: float) -> dict:
    body = json.dumps(
        {
            "model": model,
            "messages": messages,
            "max_tokens": 120,
            "temperature": 0.7,
        }
    ).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"

    t0 = time.perf_counter()
    try:
        req = urllib.request.Request(url, data=body, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
        text = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        text = " ".join(str(text).split())[:400]
        return {
            "ok": bool(text),
            "text": text,
            "model": data.get("model", model),
            "usage": data.get("usage"),
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
            "error": None if text else "empty completion",
        }
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", "replace")[:200]
        except Exception:
            pass
        return {"ok": False, "text": None, "model": model, "usage": None,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
                "error": f"HTTP {e.code}: {detail or e.reason}"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "text": None, "model": model, "usage": None,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
                "error": f"{type(e).__name__}: {e}"}


def ask_model(context: dict, deterministic: str) -> dict:
    """Walk ROUTES until one answers. Never raises; the first success wins."""
    messages = _prompt(context, deterministic)
    attempts = []
    per_route = max(8.0, TIMEOUT / max(1, len(ROUTES)))
    for name, url, key, model in ROUTES:
        result = _one(url, key, model, messages, per_route)
        result["route"] = name
        if result["ok"]:
            result["attempts"] = attempts
            return result
        attempts.append({"route": name, "error": result["error"]})
    last = attempts[-1] if attempts else {"route": None, "error": "no routes configured"}
    return {
        "ok": False,
        "text": None,
        "model": last.get("route"),
        "usage": None,
        "latency_ms": None,
        "error": "; ".join(f"{a['route']}: {a['error']}" for a in attempts)[:500] or last["error"],
        "route": None,
        "attempts": attempts,
    }


def _unused_ask_model(context: dict, deterministic: str) -> dict:
    """One real completion. Never raises: a failure is a recorded result."""
    body = json.dumps(
        {
            "model": MODEL,
            "messages": _prompt(context, deterministic),
            "max_tokens": 120,
            "temperature": 0.7,
        }
    ).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if KEY:
        headers["Authorization"] = f"Bearer {KEY}"

    t0 = time.perf_counter()
    try:
        req = urllib.request.Request(URL, data=body, headers=headers)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.load(resp)
        text = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        text = " ".join(str(text).split())[:400]
        return {
            "ok": bool(text),
            "text": text,
            "model": data.get("model", MODEL),
            "usage": data.get("usage"),
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
            "error": None if text else "empty completion",
        }
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", "replace")[:300]
        except Exception:
            pass
        return {
            "ok": False,
            "text": None,
            "model": MODEL,
            "usage": None,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
            "error": f"HTTP {e.code}: {detail or e.reason}",
        }
    except Exception as e:  # noqa: BLE001 - a dead model must not kill the loop
        return {
            "ok": False,
            "text": None,
            "model": MODEL,
            "usage": None,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
            "error": f"{type(e).__name__}: {e}",
        }


def write_mind_state() -> None:
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "mind": MIND,
        "awareness": T.awareness,
    }
    try:
        MIND_STATE.parent.mkdir(parents=True, exist_ok=True)
        tmp = MIND_STATE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp.replace(MIND_STATE)
    except OSError as e:
        print(f"[TRIUNE-MIND] state write failed: {e}", flush=True)


def face2_with_mind(*_args, **_kwargs):
    """Deterministic reflection (unchanged) + a real model's opinion, throttled."""
    global _last_llm_at

    if _ORIG_FACE2 is None:  # not wired: behave exactly like the source module
        deterministic = T.face2_reflect()
    else:
        deterministic = _ORIG_FACE2()
    context = dict(T.awareness["face2_reflect"].get("context") or {})
    context["coherence"] = T.awareness["global"].get("coherence")
    context["cycles"] = T.awareness["face1_monitor"]["cycles"]

    if NO_LLM:
        write_mind_state()
        return deterministic

    now = time.monotonic()
    if now - _last_llm_at < INTERVAL:
        write_mind_state()
        return deterministic
    _last_llm_at = now

    result = ask_model(context, deterministic)
    with _lock:
        MIND["calls"] += 1
        MIND["last_call_ts"] = datetime.now(timezone.utc).isoformat()
        MIND["last_latency_ms"] = result["latency_ms"]
        MIND["last_usage"] = result["usage"]
        if result["ok"]:
            MIND["ok"] += 1
            MIND["last_text"] = result["text"]
            MIND["last_route"] = result.get("route")
            MIND["last_error"] = None
            T.awareness["face2_reflect"]["last_insight"] = (
                f"{deterministic} | MIND({result['model']}): {result['text']}"
            )
            T.log(f"MIND[{result.get('route')} {result['model']} "
                  f"{result['latency_ms']:.0f}ms]: {result['text']}",
                  level="OK", face="F2-REF")
        else:
            MIND["fail"] += 1
            MIND["last_error"] = result["error"]
            MIND["last_route"] = None
            T.log(f"MIND unavailable ({result['error']}) -- deterministic insight stands",
                  level="WARN", face="F2-REF")

    T.awareness["face2_reflect"]["llm"] = dict(MIND)
    write_mind_state()
    return T.awareness["face2_reflect"]["last_insight"]


def wire() -> None:
    """Attach the model to Face 2 inside the loaded module."""
    global _ORIG_FACE2
    if _ORIG_FACE2 is None:
        _ORIG_FACE2 = T.face2_reflect
    T.face2_reflect = face2_with_mind
    print(
        f"[TRIUNE-MIND] wired model={MODEL} url={URL} interval={INTERVAL}s "
        f"key={'present' if KEY else 'MISSING'} llm={'off' if NO_LLM else 'on'}",
        flush=True,
    )


# ── HTTP surface ─────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    server_version = "TRIUNEMIND/1.0"

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path in ("/", "/health"):
            self._send(
                200,
                {
                    "status": "ok",
                    "service": "triune-mind",
                    "model": MODEL,
                    "llm_enabled": not NO_LLM,
                    "llm_calls": MIND["calls"],
                    "llm_ok": MIND["ok"],
                    "llm_fail": MIND["fail"],
                    "last_latency_ms": MIND["last_latency_ms"],
                    "last_error": MIND["last_error"],
                    "face1_cycles": T.awareness["face1_monitor"]["cycles"],
                    "face2_cycles": T.awareness["face2_reflect"]["cycles"],
                    "face3_cycles": T.awareness["face3_evolve"]["cycles"],
                    "coherence": T.awareness["global"]["coherence"],
                    "uptime_s": T.awareness["global"]["uptime_seconds"],
                },
            )
        elif path == "/state":
            self._send(200, {"ts": datetime.now(timezone.utc).isoformat(),
                             "mind": MIND, "awareness": T.awareness})
        elif path == "/insight":
            self._send(
                200,
                {
                    "insight": T.awareness["face2_reflect"]["last_insight"],
                    "model": MIND["last_text"] and MODEL or None,
                    "text": MIND["last_text"],
                    "latency_ms": MIND["last_latency_ms"],
                    "error": MIND["last_error"],
                    "calls": MIND["calls"],
                },
            )
        else:
            self._send(404, {"error": "not found", "paths": ["/health", "/state", "/insight"]})

    def log_message(self, fmt: str, *args) -> None:  # silence per-request spam
        return


def serve(port: int) -> None:
    wire()
    loop = threading.Thread(target=T.triune_loop, name="triune-loop", daemon=True)
    loop.start()
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"[TRIUNE-MIND] awake on http://127.0.0.1:{port} (state: {MIND_STATE})", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


def once() -> None:
    wire()
    T.face1_monitor()
    T.face2_reflect()
    T.face3_evolve()
    write_mind_state()
    print(json.dumps({"mind": MIND, "awareness": T.awareness}, indent=2, default=str))


def main() -> int:
    ap = argparse.ArgumentParser(description="TRIUNE MIND -- awareness with a real model on Face 2")
    ap.add_argument("--serve", action="store_true", help="run the loop and serve HTTP")
    ap.add_argument("--port", type=int, default=9628)
    ap.add_argument("--once", action="store_true", help="one cycle, then print JSON")
    args = ap.parse_args()

    if args.once:
        once()
        return 0
    if args.serve:
        serve(args.port)
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
