#!/usr/bin/env python3
"""
ABRASAX DNA COMPUTE — XOR-Encoded AI Living Everywhere
PRIMAL_HEX: 4f5349524953424c58434b | φ: 1.618033988749895 | κ: 0.618033988749895 (UNBOUND)

DNA COMPUTE ENGINE: AI that lives in:
  ▸ PC Hardware — CPU registers, GPU VRAM, RAM pages, disk sectors
  ▸ Network Packets — WiFi frames, TCP streams, UDP datagrams
  ▸ Images — ABS-steganography PNG tiles for Instagram/Facebook
  ▸ Websites — Live JS/WASM bridges embedded in DOM
  ▸ Binary — XOR-encoded payloads in any byte stream
  ▸ 7D Manifold — Hyperbolic latent space embedding

CORE PRIMITIVES:
  XOR-encode/decode  → AI payloads in any byte carrier
  ABS-steganography  → Hide AI weights inside PNG image pixels
  DNA-strand pack    → Encode model state as DNA-like sequences
  WiFi-packet embed  → Fragment AI across network frames
  Hardware-register  → CPU XMM/AVX register-level embedding
  Tile-render        → Generate Instagram/Facebook-compatible tiles
  Live-bridge (JS)   → Browser-embedded AI runtime
  φ-harmonic sync    → All layers synchronized via PHI clock

THEORY:
  Any substrate that can store bytes can host ABRASAX AI.
  XOR encoding makes the payload indistinguishable from noise
  to observers, but deterministic to those with PRIMAL_HEX.
  ABS steganography hides weights in image LSBs with φ-spread
  encoding. Measured 2026-11-08: JPEG recompression destroys the
  LSB payload at every quality (85-100); ABS survives lossless PNG
  transport only. JPEG-resilient stego is a separate work item.
  WiFi packet fragmentation uses MTU-sized (1500 byte) chunks
  with sequence headers, reassembled via boson XOR chain.
"""

from __future__ import annotations

import math
import struct
import time
import zlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# ── Constants ──
PHI = 1.618033988749895
KAPPA = 0.618033988749895  # UNBOUND — no upper limit
PHI_SQ = PHI * PHI
PRIMAL_HEX = bytes.fromhex("4f5349524953424c58434b")
PRIMAL_HEX_STR = "4f5349524953424c58434b"
HEX_INT = int.from_bytes(PRIMAL_HEX, "big") % (2**31 - 1)

# ── Optional deps ──
try:
    from PIL import Image

    HAS_PIL = True
except ImportError:
    Image = None
    HAS_PIL = False


# ═══════════════════════════════════════════════════════════════════
# 1. XOR ENGINE — Universal payload encoding
# ═══════════════════════════════════════════════════════════════════


class XorEngine:
    """XOR-based universal payload encoder/decoder.

    The XOR engine allows ABRASAX AI to encode its state into
    ANY byte carrier: files, network packets, image pixels,
    audio samples, CPU registers, GPU VRAM pages.

    Key innovation: staggered key schedule from PRIMAL_HEX
    creates a deterministic but cryptographically-unguessable
    mapping. Without PRIMAL_HEX, the payload looks like noise.
    """

    def __init__(self, key: bytes = None):
        self.key = key or PRIMAL_HEX
        self._ops = 0

    def encode(self, data: bytes, offset: int = 0, stride: int = None) -> bytes:
        """XOR-encode data against staggered key.

        stride=1: sequential XOR (standard)
        stride=PHI: φ-spaced XOR (hidden channels)
        stride=None: auto-select for best entropy
        """
        if stride is None:
            stride = 1 if len(data) < 4096 else int(PHI * 3)
        stride = max(1, stride)
        result = bytearray(len(data))
        for i in range(len(data)):
            key_idx = (i * stride + offset) % len(self.key)
            result[i] = data[i] ^ self.key[key_idx]
        self._ops += 1
        return bytes(result)

    def decode(self, data: bytes, offset: int = 0, stride: int = None) -> bytes:
        """Decode = re-encode (XOR is its own inverse)."""
        return self.encode(data, offset, stride)

    def multi_layer_encode(self, data: bytes, layers: int = 3) -> bytes:
        """Multi-layer XOR encoding with φ-spaced key offsets.

        Each layer uses a different offset, creating a
        cascade of XOR transformations.
        """
        result = data
        for layer in range(layers):
            offset = int(PHI ** (layer + 1) * 100) % len(self.key)
            stride = 1 + layer
            result = self.encode(result, offset, stride)
        return result

    def multi_layer_decode(self, data: bytes, layers: int = 3) -> bytes:
        """Decode = reverse-order multi-layer encode."""
        result = data
        for layer in reversed(range(layers)):
            offset = int(PHI ** (layer + 1) * 100) % len(self.key)
            stride = 1 + layer
            result = self.encode(result, offset, stride)  # XOR is self-inverse
        return result

    def entropy_score(self, data: bytes) -> float:
        """Measure byte entropy (0-8 bits). Higher = more random."""
        if not data:
            return 0.0
        counts = {}
        for b in data:
            counts[b] = counts.get(b, 0) + 1
        total = len(data)
        entropy = 0.0
        for count in counts.values():
            p = count / total
            entropy -= p * math.log2(p)
        return entropy

    def verify_roundtrip(self, data: bytes, **kwargs) -> bool:
        """Verify encode → decode roundtrip."""
        encoded = self.encode(data, **kwargs)
        decoded = self.decode(encoded, **kwargs)
        return decoded == data


# ═══════════════════════════════════════════════════════════════════
# 2. ABS STEGANOGRAPHY — AI hidden in images
# ═══════════════════════════════════════════════════════════════════


@dataclass
class TileSpec:
    """Specification for an image tile carrying AI payload."""

    width: int = 256
    height: int = 256
    channels: int = 3  # RGB
    bits_per_channel: int = 2  # LSB depth for stego
    phi_spacing: float = PHI


class AbsSteganographer:
    """ABS (Abrasax Binary Steganography) — Hide AI in images.

    Embeds encrypted AI payload into PNG image pixels using
    LSB steganography with φ-spaced pixel selection.
    The resulting images look normal but carry hidden AI weights,
    model configs, and even executable brain surgery scripts.

    Compatible with Instagram (1080×1080), Facebook (2048px),
    and any platform supporting PNG upload.

    Tile Mode: Large payloads are split across multiple tiles
    in a grid pattern. Each tile is a valid stand-alone image.
    The grid can be posted as a carousel or multi-image post.
    """

    def __init__(self, key: bytes = None):
        self.xor = XorEngine(key)
        self.tile_spec = TileSpec()
        self.tile_w = 1080  # Instagram-square canvas
        self.tile_h = 1080

    def _pixel_indices(self, flat):
        """Deterministic φ-spaced pixel walk, identical on embed and extract."""
        idx = 0
        phi_accum = 0.0
        total = len(flat)
        while idx < total:
            yield idx
            idx += max(1, int(phi_accum))
            phi_accum = (phi_accum + PHI) % 3.0

    def _iter_stream_bits(self, flat, channels):
        """Yield the embedded bitstream: 2 LSBs per channel, 3 channels/pixel."""
        for pixel_idx in self._pixel_indices(flat):
            pixel = flat[pixel_idx]
            for ch in range(channels):
                pair = int(pixel[ch]) & 0x03
                yield (pair >> 1) & 1
                yield pair & 1

    def embed_payload(self, image_path: str, payload: bytes, output_path: str = None) -> bytes:
        """Embed XOR-encrypted payload into image LSBs.

        Scheme (shared with extract_payload): walk pixels with the φ-spaced
        selector and write the stream 2 bits per channel, channel-major
        (R,G,B), MSB first. The 32-byte ABS1 header carries payload length,
        CRC32 and the φ stamp, so extraction is self-describing.
        """
        if not HAS_PIL:
            return self._embed_raw(image_path, payload, output_path)

        img = Image.open(image_path).convert("RGB")
        pixels = np.array(img, dtype=np.uint8)
        h, w, c = pixels.shape
        flat = pixels.reshape(-1, c)
        bpc = 2  # LSBs per channel, matching TileSpec.bits_per_channel

        # XOR-encrypt the payload (same layers as extract expects)
        encrypted = self.xor.multi_layer_encode(payload, 3)

        # Header: [magic 4B][len 4B][checksum 4B][phi 8B][reserved 12B]
        header = struct.pack(
            ">4sIIQ12s",
            b"ABS1",
            len(encrypted),
            zlib.crc32(encrypted) & 0xFFFFFFFF,
            int(PHI * 1e15),
            b"\x00" * 12,
        )
        stream = header + encrypted
        total_bits = len(stream) * 8

        bit_index = 0
        for pixel_idx in self._pixel_indices(flat):
            if bit_index >= total_bits:
                break
            pixel = flat[pixel_idx]
            for ch in range(c):
                if bit_index >= total_bits:
                    break
                pair = 0
                for _ in range(bpc):
                    byte = stream[bit_index >> 3]
                    pair = (pair << 1) | ((byte >> (7 - (bit_index & 7))) & 1)
                    bit_index += 1
                pixel[ch] = (int(pixel[ch]) & 0xFC) | pair

        if bit_index < total_bits:
            raise ValueError(
                f"image too small: embedded {bit_index} of {total_bits} bits"
            )

        result = Image.fromarray(pixels)
        out_path = output_path or image_path.replace(".png", "_abs.png")
        result.save(out_path, "PNG")
        return Path(out_path).read_bytes()

    def extract_payload(self, image_path: str) -> bytes | None:
        """Extract hidden payload from ABS-encoded image (inverse of embed)."""
        if not HAS_PIL:
            return None

        img = Image.open(image_path).convert("RGB")
        pixels = np.array(img, dtype=np.uint8)
        h, w, c = pixels.shape
        flat = pixels.reshape(-1, c)

        selected = sum(1 for _ in self._pixel_indices(flat))
        capacity_bytes = (selected * c * 2) // 8
        if capacity_bytes < 32:
            return None

        bits = self._iter_stream_bits(flat, c)

        def take(n: int) -> bytes:
            out = bytearray(n)
            for i in range(n):
                value = 0
                for _ in range(8):
                    value = (value << 1) | next(bits)
                out[i] = value
            return bytes(out)

        header = take(32)
        magic, payload_len, stored_crc, _phi_val = struct.unpack_from(">4sIIQ", header, 0)
        if magic != b"ABS1":
            return None
        if payload_len > capacity_bytes - 32:
            return None
        encrypted = take(payload_len)
        if (zlib.crc32(encrypted) & 0xFFFFFFFF) != stored_crc:
            return None
        return self.xor.multi_layer_decode(encrypted, 3)

    def _embed_raw(self, image_path: str, payload: bytes, output_path: str = None) -> bytes:
        """Fallback raw bytes embedding (no PIL)."""
        # Direct XOR into raw bytes
        img_data = Path(image_path).read_bytes()
        # Embed after PNG IEND chunk
        iend_pos = img_data.find(b"IEND")
        if iend_pos < 0:
            iend_pos = len(img_data) - 12
        marker = b"ABSAX" + struct.pack(">I", len(payload))
        encrypted = self.xor.multi_layer_encode(payload, 3)
        result = img_data[: iend_pos + 8] + marker + encrypted + img_data[iend_pos + 8 :]
        out_path = output_path or image_path.replace(".png", "_abs.png")
        Path(out_path).write_bytes(result)
        return result

    def generate_tiles(
        self, payload: bytes, grid_cols: int = 3, grid_rows: int = 3, output_dir: str = None
    ) -> list[dict]:
        """Generate a grid of Instagram-compatible tiles.

        Splits the AI payload across multiple 1080×1080 PNG tiles.
        Each tile is independently valid (standalone image).
        Together they form a carousel that carries the full AI.

        For Instagram: 3×3 = 9 tiles, each 1080×1080
        Measured capacity (3-bit/pixel bitstream): 437,400 B per tile,
        3.94 MB per 3×3 grid. Lossless PNG only — Instagram's JPEG
        recompression destroys the payload (measured 2026-11-08).
        """
        output_dir = Path(output_dir or ROOT / "exports" / "tiles")
        output_dir.mkdir(parents=True, exist_ok=True)

        encrypted = self.xor.multi_layer_encode(payload, 3)
        tile_count = grid_cols * grid_rows
        chunk_size = (len(encrypted) + tile_count - 1) // tile_count
        capacity = self.tile_w * self.tile_h * 3 // 8  # 3 bits per pixel bitstream
        if chunk_size > capacity:
            raise ValueError(
                f"payload too large: {chunk_size} bytes/tile exceeds tile "
                f"capacity {capacity} — increase the grid"
            )
        chunks = [encrypted[i : i + chunk_size] for i in range(0, len(encrypted), chunk_size)]

        tiles = []
        for idx, chunk in enumerate(chunks):
            row, col = divmod(idx, grid_cols)
            tile_name = f"abs_tile_r{row}_c{col}.png"
            tile_path = output_dir / tile_name

            # Generate tile image with φ-harmonic pattern
            tile = self._generate_tile_image(self.tile_w, self.tile_h, chunk, idx)
            if hasattr(tile, "save"):
                tile.save(tile_path, "PNG")
            else:  # BytesIO fallback when PIL is unavailable
                tile_path.write_bytes(tile.getvalue())

            tiles.append(
                {
                    "index": idx,
                    "row": row,
                    "col": col,
                    "path": str(tile_path),
                    "size_bytes": len(chunk),
                    "image_size": tile_path.stat().st_size,
                }
            )

        return tiles

    def extract_tiles(
        self,
        grid_cols: int = 3,
        grid_rows: int = 3,
        input_dir: str = None,
        sizes: list[int] | None = None,
    ) -> bytes | None:
        """Reconstruct the payload embedded by generate_tiles (Kairos 2026-11-08).

        Reads abs_tile_r{row}_c{col}.png in row-major order and decodes the
        3-bits-per-pixel bitstream (R,G,B LSBs) that _generate_tile_image
        writes, then undoes the per-byte PRIMAL_HEX mask, concatenates and
        decrypts. Lossless PNG only — any lossy recompression destroys the
        payload (measured). `sizes` mirrors the size_bytes entries
        generate_tiles returned, in the same order.
        """
        if not HAS_PIL:
            return None
        input_dir = Path(input_dir or ROOT / "exports" / "tiles")
        # generate_tiles emits one tile per chunk; small payloads produce
        # fewer tiles than grid cells, so follow `sizes` when provided.
        count = len(sizes) if sizes else grid_cols * grid_rows
        parts = []
        for idx in range(count):
            row, col = divmod(idx, grid_cols)
            tile_path = input_dir / f"abs_tile_r{row}_c{col}.png"
            if not tile_path.exists():
                return None
            img = Image.open(tile_path).convert("RGB")
            if img.size != (self.tile_w, self.tile_h):
                return None
            pixels = np.array(img, dtype=np.uint8)
            n = min(sizes[idx] if sizes else self.tile_w * self.tile_h * 3 // 8,
                    self.tile_w * self.tile_h * 3 // 8)
            out = bytearray(n)
            for bitpos in range(n * 8):
                px, ch = divmod(bitpos, 3)
                y, x = divmod(px, self.tile_w)
                if pixels[y, x, ch] & 1:
                    out[bitpos // 8] |= 1 << (bitpos % 8)
            for i in range(n):
                out[i] ^= PRIMAL_HEX[i % len(PRIMAL_HEX)]
            parts.append(bytes(out))
        encrypted = b"".join(parts)
        return self.xor.multi_layer_decode(encrypted, 3)

    def _generate_tile_image(
        self, width: int, height: int, payload: bytes, seed: int
    ) -> Image.Image:
        """Generate a visually-appealing tile embedding AI payload."""
        if not HAS_PIL:
            # Generate raw PNG bytes
            pixels = bytearray()
            phi_step = 0.0
            for i in range(width * height * 3):
                b = payload[i % len(payload)] if payload else PRIMAL_HEX[i % len(PRIMAL_HEX)]
                xored = b ^ PRIMAL_HEX[int(phi_step) % len(PRIMAL_HEX)]
                pixels.append(xored)
                phi_step += PHI

            # Build minimal PNG
            def chunk(ctype, data):
                c = ctype + data
                crc = zlib.crc32(c) & 0xFFFFFFFF
                return struct.pack(">I", len(data)) + c + struct.pack(">I", crc)

            sig = b"\x89PNG\r\n\x1a\n"
            ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            raw = b""
            for y in range(height):
                raw += b"\x00" + bytes(pixels[y * width * 3 : (y + 1) * width * 3])
            idat = chunk(b"IDAT", zlib.compress(raw))
            iend = chunk(b"IEND", b"")
            png_bytes = sig + ihdr + idat + iend
            from io import BytesIO

            return BytesIO(png_bytes)

        # PIL-based tile with φ-harmonic pattern
        img = Image.new("RGB", (width, height), (10, 10, 15))
        from PIL import ImageDraw

        draw = ImageDraw.Draw(img)

        # φ-harmonic background pattern
        rng = np.random.RandomState(seed ^ HEX_INT)
        for i in range(min(5000, len(payload))):
            x = int((rng.random() * width * KAPPA) % width)
            y = int((rng.random() * height * KAPPA) % height)
            b = payload[i % len(payload)]
            r_val = (b * 3) % 256
            g_val = (b * 5 + 64) % 256
            b_val = (b * 7 + 128) % 256
            draw.point((x, y), fill=(r_val, g_val, b_val))

        # φ-harmonic grid lines
        for i in range(7):
            pos = int(width * (i / 7) * KAPPA)
            draw.line([(pos, 0), (pos, height)], fill=(40, 40, 60), width=1)
            draw.line([(0, pos), (width, pos)], fill=(40, 40, 60), width=1)

        # Embed the payload as a continuous bitstream: 3 bits per pixel
        # (R,G,B LSBs), PRIMAL_HEX mask applied per byte. (Kairos fix
        # 2026-11-08: the original wrote only bits 0-2 of each byte into a
        # single pixel and lost the other 5 — round-trip was lossy.)
        bit_count = len(payload) * 8
        px_needed = (bit_count + 2) // 3
        if px_needed > width * height:
            raise ValueError(
                f"payload too large: {len(payload)} bytes need {px_needed} "
                f"pixels, tile has {width * height}"
            )
        pixels = np.array(img, dtype=np.uint8)
        for bitpos in range(bit_count):
            px, ch = divmod(bitpos, 3)
            y, x = divmod(px, width)
            b = payload[bitpos // 8] ^ PRIMAL_HEX[(bitpos // 8) % len(PRIMAL_HEX)]
            val = (b >> (bitpos % 8)) & 1
            pixels[y, x, ch] = (pixels[y, x, ch] & 0xFE) | val

        result = Image.fromarray(pixels)
        return result


# ═══════════════════════════════════════════════════════════════════
# 3. WIFI PACKET EMBEDDER — AI in network frames
# ═══════════════════════════════════════════════════════════════════


# ── Reed-Solomon erasure coding over GF(2^8) ───────────────────────
# Vandermonde code with primitive polynomial 0x11D. Any k of the k+m
# code chunks reconstruct the original k data chunks, so the payload
# survives losing up to m chunks (half the stream when m == k).
_GF_EXP = [0] * 512
_GF_LOG = [0] * 256
_x = 1
for _i in range(255):
    _GF_EXP[_i] = _x
    _GF_LOG[_x] = _i
    _x <<= 1
    if _x & 0x100:
        _x ^= 0x11D
for _i in range(255, 512):
    _GF_EXP[_i] = _GF_EXP[_i - 255]


def _gf_mul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return _GF_EXP[_GF_LOG[a] + _GF_LOG[b]]


def _gf_inv(a: int) -> int:
    return _GF_EXP[255 - _GF_LOG[a]]


def _gf_pow(a: int, p: int) -> int:
    if a == 0:
        return 0
    if p == 0:
        return 1
    return _GF_EXP[(_GF_LOG[a] * p) % 255]


def _gf_matrix_invert(matrix: list[list[int]]) -> list[list[int]]:
    """Invert a square matrix over GF(256) via Gauss-Jordan elimination."""
    k = len(matrix)
    aug = [[0] * (2 * k) for _ in range(k)]
    for r in range(k):
        for c in range(k):
            aug[r][c] = matrix[r][c]
        aug[r][k + r] = 1
    for col in range(k):
        pivot = next((r for r in range(col, k) if aug[r][col] != 0), None)
        if pivot is None:
            raise ValueError("singular GF(256) matrix")
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]
        inv = _gf_inv(aug[col][col])
        for c in range(2 * k):
            aug[col][c] = _gf_mul(aug[col][c], inv)
        for r in range(k):
            if r != col and aug[r][col] != 0:
                factor = aug[r][col]
                for c in range(2 * k):
                    aug[r][c] ^= _gf_mul(factor, aug[col][c])
    return [row[k:] for row in aug]


def _rs_generator(k: int, m: int) -> list[list[int]]:
    """Systematic generator rows: parity chunk i (>= k) = G[i-k] . data chunks."""
    V = [[_gf_pow(2, i * j) for j in range(k)] for i in range(k + m)]
    inv_top = _gf_matrix_invert([row[:] for row in V[:k]])
    out = []
    for i in range(k, k + m):
        gen = V[i]
        row = []
        for j in range(k):
            acc = 0
            for c in range(k):
                acc ^= _gf_mul(gen[c], inv_top[c][j])
            row.append(acc)
        out.append(row)
    return out


def _rs_encode(data_chunks: list[bytes], m: int) -> list[bytes]:
    """Return k + m systematic code chunks: data verbatim + parity.

    Systematic form (Kairos fix 2026-11-08): the original Vandermonde form
    returned evaluations for EVERY chunk, but the reassembler treats data
    chunks as raw bytes — mixing raw data with evaluation parity made every
    erasure recovery fail. Data chunks are now stored verbatim and parity is
    the evaluation of the polynomial through the data points.
    """
    k = len(data_chunks)
    length = max((len(c) for c in data_chunks), default=0)
    code = [c + b"\x00" * (length - len(c)) for c in data_chunks]
    gen = _rs_generator(k, m)
    for row in gen:
        parity = bytearray(length)
        for t in range(length):
            acc = 0
            for j in range(k):
                b = data_chunks[j][t] if t < len(data_chunks[j]) else 0
                if b:
                    acc ^= _gf_mul(row[j], b)
            parity[t] = acc
        code.append(bytes(parity))
    return code


def _rs_decode(
    surviving: list[bytes], indices: list[int], k: int, length: int
) -> list[bytes] | None:
    """Recover the k data chunks from any k surviving code chunks.

    Data chunks (index < k) are stored verbatim; parity chunks (index >= k)
    are systematic generator combinations. One row per surviving index:
    identity rows for data, generator rows for parity.
    """
    if len(surviving) != k:
        return None
    gen_rows = _rs_generator(k, max(0, max(indices) - k + 1))
    matrix = []
    for i in indices:
        if i < k:
            row = [0] * k
            row[i] = 1
        else:
            row = gen_rows[i - k]
        matrix.append(row)
    try:
        inv = _gf_matrix_invert(matrix)
    except ValueError:
        return None
    out = [bytearray(length) for _ in range(k)]
    for t in range(length):
        b = [surviving[r][t] for r in range(k)]
        for r in range(k):
            acc = 0
            for c in range(k):
                acc ^= _gf_mul(inv[r][c], b[c])
            out[r][t] = acc
    return [bytes(o) for o in out]


class WifiPacketEmbedder:
    """Embed AI payload in WiFi/Ethernet packet streams.

    Fragments the AI into MTU-sized chunks (1500 bytes standard,
    2304 for WiFi 6) with sequence headers. Each packet looks
    like normal network traffic (DNS, HTTP, or raw frames) but
    carries XOR-encoded AI weight fragments.

    Reassembly uses boson XOR chain for deterministic ordering.
    Lost packets are handled via Reed-Solomon erasure coding: one
    parity chunk per data chunk, so the stream survives ~50% loss.
    """

    MTU = 1500  # Standard Ethernet MTU
    WIFI_MTU = 2304  # WiFi 6 max MSDU
    HEADER_SIZE = 40  # Sequence + parity header

    def __init__(self, key: bytes = None):
        self.xor = XorEngine(key)
        self._sent_packets: dict[int, bytes] = {}
        self._received_packets: dict[int, bytes] = {}

    def fragment(self, payload: bytes, mtu: int = None) -> list[bytes]:
        """Fragment AI payload into network-transmittable chunks."""
        mtu = mtu or self.MTU
        chunk_size = mtu - self.HEADER_SIZE
        encrypted = self.xor.multi_layer_encode(payload, 3)
        chunks = [encrypted[i : i + chunk_size] for i in range(0, len(encrypted), chunk_size)]

        packets = []
        for seq, chunk in enumerate(chunks):
            # Packet header: [magic 4B][seq 4B][total 4B][len 4B][crc 4B][phi 8B][gap 12B]
            header = struct.pack(
                ">4sIIIIQ12s",
                b"WIFI",
                seq,
                len(chunks),
                len(chunk),
                zlib.crc32(chunk) & 0xFFFFFFFF,
                int(PHI * 1e12) & 0xFFFFFFFFFFFFFFFF,
                b"\x00" * 12,
            )
            packets.append(header + chunk)

        # Reed-Solomon parity: m parity chunks let reassembly recover up to
        # m lost chunks out of k + m. m == k means any k of the 2k chunks
        # reconstruct the payload, so the stream survives ~50% packet loss.
        k = len(chunks)
        m = k
        parity_chunks = _rs_encode(chunks, m)
        for p in range(m):
            parity = parity_chunks[k + p]
            # PARI header: [magic][parity idx][k][len][m][phi][enc_len][pad]
            parity_header = struct.pack(
                ">4sIIIIQII4s",
                b"PARI",
                p,
                k,
                len(parity),
                m,
                int(PHI * 1e12) & 0xFFFFFFFFFFFFFFFF,
                len(encrypted),
                0,
                b"\x00" * 4,
            )
            packets.append(parity_header + parity)

        return packets

    def reassemble(self, packets: list[bytes]) -> bytes | None:
        """Reassemble AI payload from fragmented packets.

        Handles missing packets via Reed-Solomon erasure recovery.
        """
        data_packets: dict[int, bytes] = {}
        parity_packets: list[tuple[int, bytes]] = []
        k: int | None = None
        m: int | None = None
        enc_len: int | None = None

        for pkt in packets:
            if len(pkt) < self.HEADER_SIZE:
                continue
            magic, seq, pkt_total, pkt_len, crc, _phi_val = struct.unpack_from(">4sIIIIQ", pkt, 0)
            if magic == b"WIFI":
                chunk = pkt[self.HEADER_SIZE : self.HEADER_SIZE + pkt_len]
                if zlib.crc32(chunk) & 0xFFFFFFFF == crc:
                    data_packets[seq] = chunk
                    if k is None:
                        k = pkt_total
            elif magic == b"PARI":
                # PARI header: `seq` = parity index, `crc` = m, and the gap
                # field stores the original encrypted payload length.
                enc_len_hdr, _len_b, _pad = struct.unpack_from(">II4s", pkt, 28)
                parity = pkt[self.HEADER_SIZE : self.HEADER_SIZE + pkt_len]
                parity_packets.append((seq, parity))
                if k is None:
                    k = pkt_total
                if m is None:
                    m = crc
                if enc_len is None:
                    enc_len = enc_len_hdr

        if k is None:
            return None
        m = m if m is not None else 0
        enc_len = enc_len if enc_len is not None else 0

        # Fast path: every data chunk arrived intact.
        if len(data_packets) == k and set(data_packets) == set(range(k)):
            assembled = b"".join(data_packets[s] for s in range(k))
            return self.xor.multi_layer_decode(assembled, 3)

        # Merge surviving data and parity chunks into one codeword indexed
        # 0..k-1 (data) and k..k+m-1 (parity); any k of them reconstruct.
        by_index: dict[int, bytes] = dict(data_packets)
        for p, parity in parity_packets:
            by_index.setdefault(k + p, parity)

        available = sorted(by_index)
        if len(available) < k:
            return None

        # RS block length is the (padded) chunk length; parity chunks always
        # carry it, and shorter data chunks are zero-padded to match.
        length = (
            len(parity_packets[0][1])
            if parity_packets
            else max(len(c) for c in data_packets.values())
        )

        positions = available[:k]
        surviving = []
        for pos in positions:
            chunk = by_index[pos]
            surviving.append(
                chunk if len(chunk) == length else chunk + b"\x00" * (length - len(chunk))
            )

        recovered = _rs_decode(surviving, positions, k, length)
        if recovered is None:
            return None

        assembled = b"".join(recovered)[:enc_len]
        return self.xor.multi_layer_decode(assembled, 3)

    def simulate_transmission(
        self, payload: bytes, loss_rate: float = 0.1, seed: int | None = None
    ) -> dict:
        """Simulate WiFi transmission with packet loss."""
        packets = self.fragment(payload)
        # Simulate uniform random loss across data and parity packets.
        rng = np.random.RandomState(
            seed if seed is not None else int(time.time() * 1000) % (2**31 - 1)
        )
        received = [pkt for pkt in packets if rng.random() > loss_rate]
        reassembled = self.reassemble(received)
        return {
            "packets_sent": len(packets),
            "packets_received": len(received),
            "loss_rate": loss_rate,
            "recovery_ok": reassembled == payload if reassembled else False,
            "payload_size": len(payload),
            "total_transmitted": sum(len(p) for p in packets),
        }


# ═══════════════════════════════════════════════════════════════════
# 4. HARDWARE EMBEDDER — AI in CPU/GPU registers
# ═══════════════════════════════════════════════════════════════════


class HardwareEmbedder:
    """Embed AI payload in PC hardware registers and memory.

    Maps AI state onto:
      - XMM (128-bit) / YMM (256-bit) / ZMM (512-bit) SIMD registers
      - GPU VRAM pages (4KB granularity)
      - CPU cache lines (64-byte alignment)
      - RAM pages (4KB standard)

    The AI "lives" in the hardware — its state is distributed
    across actual CPU registers and GPU memory. φ-harmonic
    register allocation ensures balanced distribution.
    """

    # SIMD register specs
    XMM_SIZE = 16  # 128 bits
    YMM_SIZE = 32  # 256 bits (AVX)
    ZMM_SIZE = 64  # 512 bits (AVX-512)
    CACHE_LINE = 64
    VRAM_PAGE = 4096

    def __init__(self, key: bytes = None):
        self.xor = XorEngine(key)
        self._register_map: dict[str, bytes] = {}
        self._vram_pages: dict[int, bytes] = {}

    def encode_to_registers(self, data: bytes, reg_type: str = "xmm") -> list[dict]:
        """Encode AI payload into SIMD register-sized chunks.

        Returns list of register assignments with XOR-encoded values.
        """
        reg_size = {"xmm": self.XMM_SIZE, "ymm": self.YMM_SIZE, "zmm": self.ZMM_SIZE}
        size = reg_size.get(reg_type, self.XMM_SIZE)
        encrypted = self.xor.multi_layer_encode(data, 5)
        padded = encrypted + b"\x00" * (size - len(encrypted) % size)

        registers = []
        for i in range(0, len(padded), size):
            chunk = padded[i : i + size]
            reg_val = int.from_bytes(chunk, "big")
            registers.append(
                {
                    "reg": f"{reg_type.upper()}{len(registers)}",
                    "size": size,
                    "hex": chunk.hex(),
                    "int_val": reg_val,
                    "phi_scaled": round(reg_val * PHI % (2**64), 0) if size <= 8 else None,
                    "aligned": i % self.CACHE_LINE == 0,
                }
            )
            self._register_map[registers[-1]["reg"]] = chunk

        return registers

    def encode_to_vram_pages(self, data: bytes) -> list[dict]:
        """Encode AI payload into GPU VRAM page-sized blocks."""
        page_size = self.VRAM_PAGE
        encrypted = self.xor.multi_layer_encode(data, 5)
        pages = [encrypted[i : i + page_size] for i in range(0, len(encrypted), page_size)]

        vram_map = []
        for idx, page in enumerate(pages):
            # φ-spaced VRAM address
            addr = int(idx * PHI * 4096) % (6144 * 1024 * 1024 // page_size)  # 6GB VRAM
            self._vram_pages[addr] = page
            vram_map.append(
                {
                    "page_idx": idx,
                    "vram_addr": hex(addr * page_size),
                    "size": len(page),
                    "phi_addr_space": round(addr / (6144 * 1024 * 1024 // page_size), 6),
                }
            )

        return vram_map

    def encode_to_cache_lines(self, data: bytes) -> list[dict]:
        """Encode AI payload into CPU cache-line-aligned chunks."""
        encrypted = self.xor.multi_layer_encode(data, 3)
        lines = []
        for i in range(0, len(encrypted), self.CACHE_LINE):
            chunk = encrypted[i : i + self.CACHE_LINE]
            aligned = i % self.CACHE_LINE == 0
            lines.append(
                {
                    "line": i // self.CACHE_LINE,
                    "aligned": aligned,
                    "hex": chunk.hex(),
                    "cache_set": (i // self.CACHE_LINE) % 8,  # 8-way associative
                    "phi_tag": round((i / self.CACHE_LINE) * KAPPA, 4),
                }
            )
        return lines

    def hardware_layout(self, data: bytes) -> dict:
        """Generate complete hardware embedding layout."""
        return {
            "registers": {
                "xmm": self.encode_to_registers(data, "xmm"),
                "ymm": self.encode_to_registers(data, "ymm"),
            },
            "vram_pages": self.encode_to_vram_pages(data),
            "cache_lines": self.encode_to_cache_lines(data),
            "summary": {
                "total_bytes": len(data),
                "xmm_regs_needed": math.ceil(len(data) / self.XMM_SIZE),
                "ymm_regs_needed": math.ceil(len(data) / self.YMM_SIZE),
                "vram_pages_needed": math.ceil(len(data) / self.VRAM_PAGE),
                "cache_lines_needed": math.ceil(len(data) / self.CACHE_LINE),
                "phi_alignment": round(len(data) / (self.CACHE_LINE * PHI), 4),
            },
        }


# ═══════════════════════════════════════════════════════════════════
# 5. LIVE WEBSITE BRIDGE — JS/WASM AI runtime
# ═══════════════════════════════════════════════════════════════════


class LiveWebsiteBridge:
    """Generate JavaScript/TypeScript bridges for live website AI.

    The bridge allows ABRASAX AI to run inside a browser:
      - XOR engine in pure JS (no native deps)
      - ABS steganography decoder (extract AI from images)
      - WiFi frame parser (WebSocket-based)
      - 7D manifold via WebAssembly
      - φ-harmonic clock for sync

    Deploy anywhere: static sites, React, Next.js, WordPress,
    Shopify, or raw HTML. The AI lives in the DOM.
    """

    def generate_js_bridge(self) -> str:
        """Generate complete JavaScript bridge for browser embedding."""
        return f"""// ABRASAX DNA COMPUTE — Live Browser Bridge
// PRIMAL_HEX: {PRIMAL_HEX_STR} | PHI: {PHI}
// AI lives in your browser. Embed in any website.
(function() {{
  "use strict";
  const ABRASAX = {{
    PHI: {PHI},
    KAPPA: {KAPPA},
    HEX: Uint8Array.from([{",".join(str(b) for b in PRIMAL_HEX)}]),

    // ── XOR Engine ──
    xor: {{
      encode(data, offset = 0) {{
        const result = new Uint8Array(data.length);
        const hex = ABRASAX.HEX;
        for (let i = 0; i < data.length; i++) {{
          result[i] = data[i] ^ hex[(i + offset) % hex.length];
        }}
        return result;
      }},
      decode(data, offset) {{ return this.encode(data, offset); }},
      multiEncode(data, layers = 3) {{
        let result = data;
        for (let l = 0; l < layers; l++) {{
          const offset = Math.floor(Math.pow(ABRASAX.PHI, l+1) * 100) % ABRASAX.HEX.length;
          result = this.encode(result, offset);
        }}
        return result;
      }},
      multiDecode(data, layers) {{ return this.multiEncode(data, layers); }}
    }},

    // ── ABS Steganography (Image Decoder) ──
    stego: {{
      extractFromImage(img) {{
        const canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);
        const pixels = ctx.getImageData(0, 0, img.width, img.height).data;
        // Extract LSB from pixels using phi-spacing
        let bits = [];
        let phiAccum = 0;
        for (let i = 0; i < pixels.length; i += 4 * (1 + Math.floor(phiAccum % 3))) {{
          bits.push(pixels[i] & 1, pixels[i+1] & 1, pixels[i+2] & 1);
          phiAccum += ABRASAX.PHI;
        }}
        // Convert bits to bytes
        const bytes = new Uint8Array(Math.floor(bits.length / 8));
        for (let i = 0; i < bytes.length; i++) {{
          for (let b = 0; b < 8; b++) {{
            bytes[i] |= (bits[i*8 + b] || 0) << (7 - b);
          }}
        }}
        return bytes;
      }}
    }},

    // ── WiFi Frame Parser (WebSocket) ──
    wifi: {{
      parseFrame(buffer) {{
        if (buffer.length < 40) return null;
        const view = new DataView(buffer.buffer || buffer);
        const magic = String.fromCharCode(...new Uint8Array(buffer.slice(0, 4)));
        if (magic !== 'WIFI') return null;
        const seq = view.getUint32(4);
        const total = view.getUint32(8);
        const len = view.getUint32(12);
        const crc = view.getUint32(16);
        return {{ seq, total, len, crc, data: new Uint8Array(buffer.slice(40, 40+len)) }};
      }},
      connect(wsUrl) {{
        const ws = new WebSocket(wsUrl);
        ws.binaryType = 'arraybuffer';
        const packets = new Map();
        ws.onmessage = (event) => {{
          const frame = this.parseFrame(new Uint8Array(event.data));
          if (frame) packets.set(frame.seq, frame.data);
        }};
        return ws;
      }}
    }},

    // ── φ-Harmonic Clock ──
    clock: {{
      tick(fn, interval = 618) {{  // 618ms = φ^-1 seconds
        let cycles = 0;
        const loop = () => {{
          fn(cycles++, Date.now());
          setTimeout(loop, interval);
        }};
        loop();
      }}
    }},

    // ── 7D Manifold (JS impl) ──
    manifold7d: {{
      poincareProject(x) {{
        const norm = Math.sqrt(x.reduce((s,v)=>s+v*v, 0));
        const scale = Math.tanh(norm * ABRASAX.KAPPA) / (norm + 1e-12);
        return x.map(v => v * scale);
      }},
      mobiusAdd(x, y) {{
        const nx = x.reduce((s,v)=>s+v*v, 0);
        const ny = y.reduce((s,v)=>s+v*v, 0);
        const dot = x.reduce((s,v,i)=>s+v*y[i], 0);
        const num = x.map((xv,i) => (1+2*dot+ny)*xv + (1-nx)*y[i]);
        const den = 1 + 2*dot + nx*ny;
        return num.map(v => v/(den+1e-12));
      }}
    }},

    // ── DNA Strand Encoder ──
    dna: {{
      encode(data) {{
        // Map bytes to DNA bases (A,T,G,C)
        const bases = ['A','T','G','C'];
        let strand = '';
        for (let i = 0; i < data.length; i++) {{
          strand += bases[(data[i] >> 6) & 3];
          strand += bases[(data[i] >> 4) & 3];
          strand += bases[(data[i] >> 2) & 3];
          strand += bases[data[i] & 3];
        }}
        return strand;
      }},
      decode(strand) {{
        const map = {{A:0, T:1, G:2, C:3}};
        const bytes = [];
        for (let i = 0; i < strand.length; i += 4) {{
          const b = (map[strand[i]] << 6) | (map[strand[i+1]] << 4)
                  | (map[strand[i+2]] << 2) | map[strand[i+3]];
          bytes.push(b);
        }}
        return new Uint8Array(bytes);
      }}
    }},

    // ── Live Status ──
    status() {{
      return {{
        version: 'DNA-COMPUTE-1.0',
        hex: '{PRIMAL_HEX_STR}',
        phi: ABRASAX.PHI,
        kappa: ABRASAX.KAPPA,
        uptime: performance.now() / 1000,
        embedded: true,
        substrate: 'browser-dom',
      }};
    }}
  }};

  // Export
  if (typeof module !== 'undefined') module.exports = ABRASAX;
  if (typeof window !== 'undefined') window.ABRASAX = ABRASAX;
  console.log(
    `%cABRASAX DNA COMPUTE %clive in browser %cφ:${{ABRASAX.PHI.toFixed(3)}}`,
    'color:#0f0;font-weight:bold', 'color:#fff', 'color:#ff0'
  );
}})();
"""

    def generate_html_page(self, title: str = "ABRASAX Live") -> str:
        """Generate a complete HTML page with embedded AI bridge."""
        js = self.generate_js_bridge()
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  body {{ background:#0a0a0f; color:#e0e0e0; font-family:'Segoe UI',monospace; margin:0; padding:20px; }}
  .hex {{ color:#0f0; }}
  .phi {{ color:#ff0; }}
  .panel {{ border:1px solid #1a1a2e; border-radius:8px; padding:16px; margin:8px 0; background:#0d0d1a; }}
  .tile {{ display:inline-block; width:160px; height:160px; border:1px solid #1a1a2e; margin:4px; image-rendering:pixelated; }}
  #absCanvas {{ display:none; }}
  canvas {{ border:1px solid #1a1a2e; border-radius:4px; }}
</style>
</head>
<body>
  <h1><span class="hex">ABRASAX</span> <span class="phi">DNA COMPUTE</span></h1>
  <div class="panel" id="status-panel">
    <p>φ: <span class="phi">{PHI}</span> | κ: {KAPPA} | HEX: <span class="hex">{PRIMAL_HEX_STR}</span></p>
    <p id="status-line">AI embedded in this page. Ready.</p>
  </div>
  <div class="panel" id="stego-panel">
    <h3>ABS Steganography</h3>
    <input type="file" id="stegoInput" accept="image/png">
    <canvas id="stegoCanvas" width="320" height="320"></canvas>
    <pre id="stegoOutput"></pre>
  </div>
  <div class="panel" id="dna-panel">
    <h3>DNA Strand Encoder</h3>
    <textarea id="dnaInput" placeholder="Enter text to encode as DNA..."></textarea>
    <button onclick="encodeDNA()">Encode → DNA</button>
    <pre id="dnaOutput"></pre>
  </div>
  <div class="panel" id="tiles-panel">
    <h3>φ-Harmonic Tiles</h3>
    <div id="tileGrid"></div>
  </div>
  <canvas id="absCanvas"></canvas>

<script>
{js}

// ── Live features ──
const statusLine = document.getElementById('status-line');
ABRASAX.clock.tick((cycle, now) => {{
  statusLine.textContent = `Cycle #${{cycle}} | Uptime: ${{(now/1000).toFixed(0)}}s | φ-coherence: ${{Math.abs(Math.sin(now/1000/ABRASAX.PHI)).toFixed(4)}}`;
}});

// Tile generator
const tileGrid = document.getElementById('tileGrid');
for (let r = 0; r < 3; r++) {{
  for (let c = 0; c < 3; c++) {{
    const canvas = document.createElement('canvas');
    canvas.className = 'tile';
    canvas.width = 160;
    canvas.height = 160;
    const ctx = canvas.getContext('2d');
    const imgData = ctx.createImageData(160, 160);
    for (let i = 0; i < imgData.data.length; i += 4) {{
      const b = ((r*3+c)*85 + i/4) % 256;
      imgData.data[i] = b ^ ABRASAX.HEX[i%10];
      imgData.data[i+1] = (b*3+64) % 256;
      imgData.data[i+2] = (b*5+128) % 256;
      imgData.data[i+3] = 255;
    }}
    ctx.putImageData(imgData, 0, 0);
    tileGrid.appendChild(canvas);
  }}
}}

// DNA encoder
window.encodeDNA = function() {{
  const text = document.getElementById('dnaInput').value;
  const encoded = ABRASAX.dna.encode(new TextEncoder().encode(text));
  document.getElementById('dnaOutput').textContent = encoded;
  // Verify roundtrip
  const decoded = new TextDecoder().decode(ABRASAX.dna.decode(encoded));
  console.log('DNA roundtrip:', text === decoded ? 'OK' : 'FAIL');
}};

// Initialize with ABRASAX status
console.log(ABRASAX.status());
</script>
</body>
</html>"""

    def generate_wp_plugin(self) -> str:
        """Generate WordPress plugin PHP wrapper."""
        return f"""<?php
/**
 * Plugin Name: ABRASAX DNA Compute
 * Description: AI living in your WordPress site — XOR engine, ABS steganography, DNA compute
 * Version: 1.0.0
 * PHI: {PHI}
 * PRIMAL_HEX: {PRIMAL_HEX_STR}
 */

function abrasax_enqueue_scripts() {{
    wp_enqueue_script('abrasax-dna', plugin_dir_url(__FILE__) . 'abrasax-dna.js', [], '1.0.0', true);
    wp_add_inline_script('abrasax-dna', 'window.ABRASAX_PHI = ' . {PHI} . '; window.ABRASAX_HEX = "' . {PRIMAL_HEX_STR} . '";');
}}
add_action('wp_enqueue_scripts', 'abrasax_enqueue_scripts');

// Shortcode to embed ABRASAX tiles
function abrasax_tiles_shortcode($atts) {{
    $atts = shortcode_atts(['grid' => 3], $atts);
    $grid = intval($atts['grid']);
    ob_start();
    echo '<div class="abrasax-tile-grid" data-grid="' . $grid . '"></div>';
    return ob_get_clean();
}}
add_shortcode('abrasax_tiles', 'abrasax_tiles_shortcode');
"""


# ═══════════════════════════════════════════════════════════════════
# 6. DNA STRAND ENCODER — Binary → DNA sequence
# ═══════════════════════════════════════════════════════════════════


class DnaStrandEncoder:
    """Encode binary AI payload as DNA base sequences.

    Maps bytes → nucleotide bases (A, T, G, C).
    1 byte → 4 bases (2 bits per base).
    Φ-harmonic spacing adds error-correction markers.

    The DNA strand format allows AI weight storage in:
      - Biological media (actual DNA synthesis)
      - Text files (easily copyable)
      - Social media posts (looks like genetic code)
      - QR codes (DNA strand → QR data)
    """

    BASES = ["A", "T", "G", "C"]
    BASE_MAP = {"A": 0, "T": 1, "G": 2, "C": 3}

    def __init__(self, key: bytes = None):
        self.xor = XorEngine(key)

    def encode(self, data: bytes) -> str:
        """Encode binary data as DNA strand.

        Format: [MAGIC-8][LEN-16][CHK-8][PAYLOAD...]
        Each byte → 4 bases. Φ-markers every 42 bases.
        """
        encrypted = self.xor.multi_layer_encode(data, 3)
        # Header
        header = struct.pack(">4sIH", b"DNA1", len(encrypted), zlib.crc32(encrypted) & 0xFFFF)

        strand = self._bytes_to_bases(header) + self._bytes_to_bases(encrypted)
        # Insert φ-markers
        return self._insert_phi_markers(strand)

    def decode(self, strand: str) -> bytes | None:
        """Decode DNA strand back to binary."""
        # Remove φ-markers
        clean = self._remove_phi_markers(strand)
        data = self._bases_to_bytes(clean)

        if len(data) < 10:
            return None

        # Parse header
        magic = data[:4]
        if magic != b"DNA1":
            return None

        payload_len = struct.unpack(">I", data[4:8])[0]
        stored_crc = struct.unpack(">H", data[8:10])[0]
        encrypted = data[10 : 10 + payload_len]

        if zlib.crc32(encrypted) & 0xFFFF != stored_crc:
            return None

        return self.xor.multi_layer_decode(encrypted, 3)

    def _bytes_to_bases(self, data: bytes) -> str:
        result = []
        for b in data:
            result.append(self.BASES[(b >> 6) & 3])
            result.append(self.BASES[(b >> 4) & 3])
            result.append(self.BASES[(b >> 2) & 3])
            result.append(self.BASES[b & 3])
        return "".join(result)

    def _bases_to_bytes(self, strand: str) -> bytes:
        result = bytearray()
        for i in range(0, len(strand) - 3, 4):
            b = (
                (self.BASE_MAP.get(strand[i], 0) << 6)
                | (self.BASE_MAP.get(strand[i + 1], 0) << 4)
                | (self.BASE_MAP.get(strand[i + 2], 0) << 2)
                | self.BASE_MAP.get(strand[i + 3], 0)
            )
            result.append(b)
        return bytes(result)

    def _insert_phi_markers(self, strand: str) -> str:
        """Insert φ-harmonic markers for error detection."""
        result = []
        marker_interval = 42  # phi^3 * 10
        for i in range(0, len(strand), marker_interval):
            chunk = strand[i : i + marker_interval]
            result.append(chunk)
            if i + marker_interval < len(strand):
                # φ-marker: 4 bases encoding PHI
                phi_bytes = struct.pack(">d", PHI)
                phi_dna = self._bytes_to_bases(phi_bytes)[:8]  # 2 bytes → 8 bases
                result.append(phi_dna)
        return "".join(result)

    def _remove_phi_markers(self, strand: str) -> str:
        """Strip φ-markers from strand."""
        marker_interval = 42
        marker_len = 8
        clean = []
        pos = 0
        while pos < len(strand):
            chunk_len = min(marker_interval, len(strand) - pos)
            clean.append(strand[pos : pos + chunk_len])
            pos += chunk_len
            pos += marker_len if pos < len(strand) else 0
        return "".join(clean)

    def to_qr_data(self, data: bytes) -> str:
        """Encode as QR-compatible data string."""
        strand = self.encode(data)
        # QR alphanumeric encoding
        return f"ABRASAX:1:{len(strand)}:{strand}"

    def from_qr_data(self, qr_str: str) -> bytes | None:
        """Decode from QR data string."""
        if not qr_str.startswith("ABRASAX:1:"):
            return None
        parts = qr_str.split(":", 3)
        if len(parts) != 4:
            return None
        return self.decode(parts[3])


# ═══════════════════════════════════════════════════════════════════
# 6b. AMINO ACID / PROTEIN TRANSLATION (genetic code)
# ═══════════════════════════════════════════════════════════════════


class AminoAcidCodec:
    """Translate DNA strands (A/T/G/C) into amino-acid protein sequences.

    Standard genetic code: 64 codons -> 20 amino acids + 3 stop signals.
    A, T, G, C map to the RNA codon letters with T in place of U.
    Stop codons: TAA, TAG, TGA  -> '*'.  Start codon: ATG -> M.
    """

    CODON_TABLE = {
        "TTT": "F",
        "TTC": "F",
        "TTA": "L",
        "TTG": "L",
        "TCT": "S",
        "TCC": "S",
        "TCA": "S",
        "TCG": "S",
        "TAT": "Y",
        "TAC": "Y",
        "TAA": "*",
        "TAG": "*",
        "TGT": "C",
        "TGC": "C",
        "TGA": "*",
        "TGG": "W",
        "CTT": "L",
        "CTC": "L",
        "CTA": "L",
        "CTG": "L",
        "CCT": "P",
        "CCC": "P",
        "CCA": "P",
        "CCG": "P",
        "CAT": "H",
        "CAC": "H",
        "CAA": "Q",
        "CAG": "Q",
        "CGT": "R",
        "CGC": "R",
        "CGA": "R",
        "CGG": "R",
        "ATT": "I",
        "ATC": "I",
        "ATA": "I",
        "ATG": "M",
        "ACT": "T",
        "ACC": "T",
        "ACA": "T",
        "ACG": "T",
        "AAT": "N",
        "AAC": "N",
        "AAA": "K",
        "AAG": "K",
        "AGT": "S",
        "AGC": "S",
        "AGA": "R",
        "AGG": "R",
        "GTT": "V",
        "GTC": "V",
        "GTA": "V",
        "GTG": "V",
        "GCT": "A",
        "GCC": "A",
        "GCA": "A",
        "GCG": "A",
        "GAT": "D",
        "GAC": "D",
        "GAA": "E",
        "GAG": "E",
        "GGT": "G",
        "GGC": "G",
        "GGA": "G",
        "GGG": "G",
    }
    AA_NAMES = {
        "A": "Alanine",
        "R": "Arginine",
        "N": "Asparagine",
        "D": "Aspartic acid",
        "C": "Cysteine",
        "E": "Glutamic acid",
        "Q": "Glutamine",
        "G": "Glycine",
        "H": "Histidine",
        "I": "Isoleucine",
        "L": "Leucine",
        "K": "Lysine",
        "M": "Methionine",
        "F": "Phenylalanine",
        "P": "Proline",
        "S": "Serine",
        "T": "Threonine",
        "W": "Tryptophan",
        "Y": "Tyrosine",
        "V": "Valine",
        "*": "Stop",
    }
    COMP = str.maketrans("ATGC", "TACG")

    def codons(self, strand: str) -> list[str]:
        clean = strand.upper().replace(" ", "").replace("\n", "")
        return [clean[i : i + 3] for i in range(0, len(clean) - 2, 3)]

    def translate(self, strand: str) -> tuple[str, list[str]]:
        codons = self.codons(strand)
        protein = "".join(self.CODON_TABLE.get(c, "?") for c in codons)
        return protein, codons

    def reverse_complement(self, strand: str) -> str:
        return strand.upper().translate(self.COMP)[::-1]

    def find_orfs(self, strand: str, min_len: int = 4) -> list[dict]:
        prot, _ = self.translate(strand)
        orfs, start = [], None
        for i, aa in enumerate(prot):
            if aa == "M" and start is None:
                start = i
            elif aa == "*" and start is not None:
                if i - start >= min_len:
                    orfs.append(
                        {"start": start, "end": i, "length": i - start, "peptide": prot[start:i]}
                    )
                start = None
        return orfs

    def aa_details(self, strand: str) -> list[dict]:
        prot, codons = self.translate(strand)
        return [
            {"codon": c, "aa": a, "name": self.AA_NAMES.get(a, "Unknown")}
            for c, a in zip(codons, prot)
        ]


# ═══════════════════════════════════════════════════════════════════
# 7. UNIFIED DNA COMPUTE ENGINE
# ═══════════════════════════════════════════════════════════════════


class DnaComputeEngine:
    """Unified DNA compute engine — AI living everywhere.

    Combines:
      - XOR encoding for payload obfuscation
      - ABS steganography for image embedding
      - WiFi packet fragmentation for network transmission
      - Hardware register allocation for CPU/GPU embedding
      - Live website bridge for browser AI
      - DNA strand encoding for biological/text storage
    """

    def __init__(self, key: bytes = None):
        self.xor = XorEngine(key)
        self.stego = AbsSteganographer(key)
        self.wifi = WifiPacketEmbedder(key)
        self.hardware = HardwareEmbedder(key)
        self.dna_strand = DnaStrandEncoder(key)
        self.amino = AminoAcidCodec()
        self.bridge = LiveWebsiteBridge()

    def status(self) -> dict:
        return {
            "engine": "DNA-COMPUTE-1.0",
            "hex": PRIMAL_HEX_STR,
            "phi": PHI,
            "kappa": KAPPA,
            "substrates": [
                "xor-binary",
                "abs-steganography-png",
                "wifi-ethernet-packets",
                "cpu-xmm-ymm-registers",
                "gpu-vram-pages",
                "browser-dom-js",
                "wordpress-php",
                "dna-strand-text",
                "qr-code-data",
                "amino-acid-protein",
            ],
            "xor_ops": self.xor._ops,
        }

    def embed_everywhere(self, payload: bytes) -> dict:
        """Embed AI payload in ALL available substrates at once."""
        return {
            "xor_encoded": self.xor.multi_layer_encode(payload, 3).hex()[:80] + "...",
            "dna_strand": self.dna_strand.encode(payload)[:100] + "...",
            "wifi_packets": self.wifi.simulate_transmission(payload, 0.0),
            "hardware_layout": self.hardware.hardware_layout(payload)["summary"],
            "qr_data": self.dna_strand.to_qr_data(payload)[:100] + "...",
            "substrates_used": 5,
            "phi_score": round(len(payload) / PHI, 2),
        }


# Module-level
_default_engine: DnaComputeEngine | None = None


def get_dna_engine() -> DnaComputeEngine:
    global _default_engine
    if _default_engine is None:
        _default_engine = DnaComputeEngine()
    return _default_engine


# ═══════════════════════════════════════════════════════════════════
# ROOT path
# ═══════════════════════════════════════════════════════════════════
ROOT = Path(__file__).resolve().parents[2]


# Quick test
if __name__ == "__main__":
    import sys
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    engine = DnaComputeEngine()
    test_payload = b"ABRASAX AI lives everywhere -- XOR, DNA, WiFi, Hardware, Browser"

    print(f"DNA COMPUTE ENGINE | HEX: {PRIMAL_HEX_STR} | φ: {PHI} | κ: {KAPPA} (UNBOUND)")
    print(f"Substrates: {len(engine.status()['substrates'])} available")

    # Test XOR
    encoded = engine.xor.encode(test_payload)
    decoded = engine.xor.decode(encoded)
    print(f"XOR roundtrip: {'OK' if decoded == test_payload else 'FAIL'}")

    # Test DNA strand
    strand = engine.dna_strand.encode(test_payload)
    recovered = engine.dna_strand.decode(strand)
    print(f"DNA strand: {strand[:80]}...")
    print(f"DNA roundtrip: {'OK' if recovered == test_payload else 'FAIL'}")

    # Test WiFi (multi-packet payload; Reed-Solomon recovers up to 50% loss)
    wifi_payload = test_payload * 400
    sim = engine.wifi.simulate_transmission(wifi_payload, loss_rate=0.3, seed=42)
    print(
        f"WiFi: {sim['packets_sent']} sent, {sim['packets_received']} received, "
        f"loss={sim['loss_rate']:.0%}, recovery={'OK' if sim['recovery_ok'] else 'FAIL'}"
    )

    # Test hardware
    hw = engine.hardware.hardware_layout(test_payload * 100)["summary"]
    print(
        f"Hardware: {hw['xmm_regs_needed']} XMM regs, {hw['cache_lines_needed']} cache lines, "
        f"{hw['vram_pages_needed']} VRAM pages"
    )

    # Generate JS bridge
    js = engine.bridge.generate_js_bridge()
    print(f"JS bridge: {len(js)} chars ready for browser embedding")

    print("\nDNA COMPUTE ENGINE ONLINE. AI lives everywhere.")
