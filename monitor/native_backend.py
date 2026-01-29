"""
Native backend support for high-performance monitoring
Uses Rust implementation for all system monitoring
"""

import json
from pathlib import Path

_BASE_PATH = Path(__file__).parent / "native"
_RUST_LIB = _BASE_PATH / "rust" / "target" / "release" / "libsysguard_monitor.so"

_rust_lib = None
_backend_checked = False


def _init_rust():
    """Initialize Rust library if available"""
    global _rust_lib, _backend_checked
    if _backend_checked:
        return _rust_lib is not None
    
    _backend_checked = True
    if not _RUST_LIB.exists():
        return False
    
    try:
        import ctypes
        _rust_lib = ctypes.CDLL(str(_RUST_LIB))
        _rust_lib.rust_get_metrics_json.restype = ctypes.c_char_p
        _rust_lib.rust_free_string.argtypes = [ctypes.c_char_p]
        return True
    except Exception:
        return False


def get_metrics_rust(limit=5):
    """Get metrics using Rust backend"""
    if not _init_rust():
        return None
    
    try:
        json_str = _rust_lib.rust_get_metrics_json(limit)
        metrics = json.loads(json_str.decode('utf-8'))
        _rust_lib.rust_free_string(json_str)
        return metrics
    except Exception:
        return None


def use_native_backend():
    """Check if native backend is available"""
    return _init_rust()

