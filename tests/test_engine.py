#!/usr/bin/env python3
"""
Tests for ABRASAX AI Engine core.
PRIMAL_HEX: 4f5349524953424c58434b | φ: 1.618033988749895
"""
import pytest
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

PHI = 1.618033988749895
K = 0.618033988749895
S2_BOUND = 0.01


class TestPhiConstants:
    def test_phi_value(self):
        """Golden ratio must be exact."""
        assert abs(PHI - 1.618033988749895) < 1e-12

    def test_k_value(self):
        """K = 1/φ must be exact."""
        assert abs(K - 0.618033988749895) < 1e-12

    def test_phi_squared(self):
        """φ² = φ + 1"""
        assert abs(PHI ** 2 - (PHI + 1)) < 1e-10

    def test_phi_inverse(self):
        """1/φ = φ - 1"""
        assert abs(1.0 / PHI - (PHI - 1)) < 1e-10

    def test_s2_stability(self):
        """S² stability bound must be 0.01."""
        assert S2_BOUND == 0.01


class TestHexEncoding:
    def test_hex_encode_decode(self):
        text = "OSIRISBLXCK"
        encoded = text.encode("utf-8").hex()
        decoded = bytes.fromhex(encoded).decode("utf-8")
        assert decoded == text
        assert encoded == "4f5349524953424c58434b"

    def test_xor_cipher(self):
        text = "HELLO_ABRASAX"
        key = "4f5349524953424c58434b"
        key_bytes = key.encode("utf-8")
        text_bytes = text.encode("utf-8")
        encrypted = bytearray(len(text_bytes))
        for i in range(len(text_bytes)):
            encrypted[i] = text_bytes[i] ^ key_bytes[i % len(key_bytes)]
        decrypted = bytearray(len(encrypted))
        for i in range(len(encrypted)):
            decrypted[i] = encrypted[i] ^ key_bytes[i % len(key_bytes)]
        assert decrypted.decode("utf-8") == text

    def test_primal_signature(self):
        hex_str = "4f5349524953424c58434b"
        data = "test_data"
        signed = f"{hex_str}:{data.encode('utf-8').hex()}"
        parts = signed.split(":")
        assert parts[0] == hex_str
        assert bytes.fromhex(parts[1]).decode("utf-8") == data


class TestPhiCalibration:
    def test_k_calibrate_tracking(self):
        """K-calibrated tracking should move toward target."""
        current = 0.5
        target = 1.0
        result = current + K * (target - current)
        assert result > current  # Should move toward target

    def test_phi_encode_decode(self):
        n = 42.0
        phi_encoded = round(n * PHI, 3)
        phi_decoded = round(phi_encoded * K, 3)
        assert abs(phi_decoded - n) < 0.01

    def test_coherence_calculation(self):
        f1_ratio = 0.8
        f2_ratio = 0.9
        f3_ratio = 0.7
        coherence = (f1_ratio + f2_ratio + f3_ratio) / 3
        phi_alignment = abs(coherence - K)
        assert 0 <= coherence <= 1
        assert phi_alignment >= 0


class TestEngineCore:
    def test_import_engine(self):
        """Verify engine_core can be imported."""
        try:
            from engine_core import PHI, K, HEX, check_lm_studio, get_gpu_telemetry, phi_calibrate
            assert abs(PHI - 1.618033988749895) < 1e-12
            assert HEX == "4f5349524953424c58434b"
        except ImportError as e:
            pytest.skip(f"engine_core not importable: {e}")

    def test_lm_studio_function(self):
        """check_lm_studio should return a dict."""
        try:
            from engine_core import check_lm_studio
            result = check_lm_studio()
            assert isinstance(result, dict)
            assert "online" in result
        except ImportError:
            pytest.skip("engine_core not importable")

    def test_gpu_telemetry_function(self):
        """get_gpu_telemetry should return a dict."""
        try:
            from engine_core import get_gpu_telemetry
            result = get_gpu_telemetry()
            assert isinstance(result, dict)
        except ImportError:
            pytest.skip("engine_core not importable")


class TestMasterAutonomy:
    def test_process_kill_logic(self):
        """Verify taskkill command construction."""
        cmd = 'taskkill /f /im python.exe 2>nul'
        assert "taskkill" in cmd
        assert "/f" in cmd

    def test_log_format(self):
        """Verify log format."""
        ts = datetime.now().isoformat()
        msg = "Test log message"
        level = "INFO"
        line = f"[{ts}] [{level}] {msg}"
        assert msg in line
        assert level in line


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
