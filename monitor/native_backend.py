"""
Native backend support for high-performance monitoring
Automatically uses Rust or C implementations if available, falls back to Python
"""

import json
import subprocess
from pathlib import Path

_BASE_PATH = Path(__file__).parent / "native"
_RUST_LIB = _BASE_PATH / "rust" / "target" / "release" / "libsysguard_monitor.so"
_C_PROCESS = _BASE_PATH / "c" / "process_watcher"
_C_CPU = _BASE_PATH / "c" / "cpu_monitor"

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


def get_metrics_c(limit=5):
    """Get metrics using C backend"""
    if not (_C_PROCESS.exists() and _C_CPU.exists()):
        return None
    
    try:
        proc_result = subprocess.run(
            [str(_C_PROCESS), '-n', str(limit), '-s', 'cpu'],
            capture_output=True, text=True, timeout=5
        )
        cpu_result = subprocess.run(
            [str(_C_CPU), '1'],
            capture_output=True, text=True, timeout=3
        )
        
        if proc_result.returncode == 0 and cpu_result.returncode == 0:
            return {'cpu': cpu_result.stdout, 'processes': proc_result.stdout}
        return None
    except Exception:
        return None


def use_native_backend():
    """Check if native backend is available"""
    return _init_rust() or (_C_PROCESS.exists() and _C_CPU.exists())
