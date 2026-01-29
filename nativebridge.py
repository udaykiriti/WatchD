"""
Unified monitoring interface with automatic backend selection
Integrates Rust, C, and Python implementations with intelligent fallback
"""

import json
import subprocess
from pathlib import Path

RUST_LIB_PATH = Path(__file__).parent / "rustmonitor" / "target" / "release"
C_BIN_PATH = Path(__file__).parent / "cmonitor"


def use_rust_monitor(limit=5):
    """Use Rust-based monitoring (fastest, memory-safe)"""
    try:
        import ctypes
        lib_path = RUST_LIB_PATH / "libsysguard_monitor.so"
        
        if not lib_path.exists():
            return None
            
        lib = ctypes.CDLL(str(lib_path))
        lib.rust_get_metrics_json.restype = ctypes.c_char_p
        lib.rust_free_string.argtypes = [ctypes.c_char_p]
        
        json_str = lib.rust_get_metrics_json(limit)
        metrics = json.loads(json_str.decode('utf-8'))
        lib.rust_free_string(json_str)
        
        return metrics
    except Exception:
        return None


def use_c_monitor(limit=5, sort_by='cpu'):
    """Use C-based monitors (very fast, minimal overhead)"""
    try:
        watcher = C_BIN_PATH / "process_watcher"
        cpu_mon = C_BIN_PATH / "cpu_monitor"
        
        if not (watcher.exists() and cpu_mon.exists()):
            return None
        
        proc_result = subprocess.run([str(watcher), '-n', str(limit), '-s', sort_by],
                                    capture_output=True, text=True, timeout=5)
        cpu_result = subprocess.run([str(cpu_mon), '1'],
                                   capture_output=True, text=True, timeout=3)
        
        if proc_result.returncode == 0 and cpu_result.returncode == 0:
            return {'cpu': cpu_result.stdout, 'processes': proc_result.stdout}
        return None
    except Exception:
        return None


def use_python_monitor(limit=5):
    """Use Python implementation (always available)"""
    from monitor.cpu import get_cpu_metrics
    from monitor.memory import get_memory_metrics
    from monitor.process import get_process_metrics
    
    return {
        'cpu': get_cpu_metrics(),
        'memory': get_memory_metrics(),
        'processes': get_process_metrics(limit=limit)
    }


def get_metrics(limit=5, backend=None):
    """
    Get system metrics using the best available backend
    
    Args:
        limit: Number of top processes to return
        backend: Force specific backend ('rust', 'c', 'python') or None for auto
    
    Returns:
        Dictionary with 'source' and 'data' keys
    """
    if backend == 'python':
        return {'source': 'python', 'data': use_python_monitor(limit)}
    
    # Try Rust first (unless explicitly C)
    if backend != 'c':
        metrics = use_rust_monitor(limit)
        if metrics:
            return {'source': 'rust', 'data': metrics}
    
    # Try C second
    if backend != 'rust':
        metrics = use_c_monitor(limit)
        if metrics:
            return {'source': 'c', 'data': metrics}
    
    # Fallback to Python
    return {'source': 'python', 'data': use_python_monitor(limit)}


if __name__ == "__main__":
    import sys
    
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    backend = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = get_metrics(limit, backend)
    print(f"\n=== Using {result['source'].upper()} backend ===\n")
    print(json.dumps(result['data'], indent=2, default=str))

