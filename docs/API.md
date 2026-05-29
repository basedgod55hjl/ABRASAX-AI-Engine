# ABRASAX AI Engine API Reference

## Local LLM API (LM Studio)

### Base URL
```
http://127.0.0.1:1234/v1
```

### Authentication
```
Authorization: Bearer sk-lm-KZtEmyJA:qJJk4G0dhYrRT3kWKyQa
```

### Endpoints

#### GET /v1/models
List available models.

**Response:**
```json
{
  "data": [
    {
      "id": "gemma-4-e4b-it-uncensored-max-opus-4.7",
      "object": "model",
      "created": 1717000000,
      "owned_by": "lm-studio"
    }
  ],
  "object": "list"
}
```

#### POST /v1/chat/completions
Send a chat completion request.

**Request:**
```json
{
  "model": "gemma-4-e4b-it-uncensored-max-opus-4.7",
  "messages": [
    {"role": "system", "content": "You are OSIRISBLXCK."},
    {"role": "user", "content": "System status?"}
  ],
  "max_tokens": 256,
  "temperature": 0.6,
  "stream": false
}
```

**Response:**
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "All systems nominal. φ-coherence: 0.982"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 12,
    "total_tokens": 37
  }
}
```

## Hex TypeScript Bridge

### Functions

#### hexEncode(text: string): string
Encode text to hex.

#### hexDecode(hex: string): string
Decode hex to text.

#### xorEncrypt(text: string, key?: string): string
XOR cipher encryption.

#### xorDecrypt(hex: string, key?: string): string
XOR cipher decryption.

#### primalSign(data: string): string
Create primal signature.

#### primalVerify(signed: string, expected?: string): boolean
Verify primal signature.

## F-Logic Entanglement API

### GET /v1/entangle
Get current entanglement status.

**Response:**
```json
{
  "F1": {"name": "Hex TypeScript", "files_present": 10, "files_total": 10, "ratio": 1.0, "entangled": true},
  "F2": {"name": "Python Core", "files_present": 5, "files_total": 7, "ratio": 0.714, "entangled": true},
  "F3": {"name": "CBM Hydration", "files_present": 3, "files_total": 5, "ratio": 0.6, "entangled": true},
  "coherence": 0.771,
  "phi_alignment": 0.153,
  "stable": false
}
```

## Telemetry API

### GET /v1/telemetry
Get live system telemetry.

**Response:**
```json
{
  "timestamp": "2026-05-29T17:00:00",
  "phi": 1.618033988749895,
  "gpu": {
    "name": "NVIDIA GeForce GTX 1660 Ti",
    "temp_c": 65,
    "util_pct": 45,
    "vram_used_mb": 2048,
    "vram_total_mb": 6144
  },
  "llm": {"online": true, "models": 1},
  "engines": {
    "MASTER_AUTONOMY": {"pid": 1234, "alive": true}
  }
}
```
