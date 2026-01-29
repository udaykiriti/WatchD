"""
Python bindings for Rust and C monitoring components
Provides fallback to pure Python if compiled modules aren't available
"""

import json
import subprocess
import os
from pathlib import Path

# Try to load Rust library
RUST_LIB_PATH = Path(__file__).parent / "rust_monitor" / "target" / "release"
C_BIN_PATH = Path(__file__).parent / "c_monitor"

def use_rust_monitor(limit=5):
    """
    Use Rust-based monitoring (fastest, memory-safe)
    Returns None if not available
    """
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
    except Exception as e:
        print(f"Rust monitor unavailable: {e}")
        return None

def use_c_process_watcher(limit=5, sort_by='cpu'):
    """
    Use C-based process watcher (very fast, minimal overhead)
    Returns None if not available
    """
    try:
        watcher_path = C_BIN_PATH / "process_watcher"
        
        if not watcher_path.exists():
            return None
            
        result = subprocess.run(
            [str(watcher_path), '-n', str(limit), '-s', sort_by],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return result.stdout
        return None
    except Exception as e:
        print(f"C process watcher unavailable: {e}")
        return None

def use_c_cpu_monitor(interval=1):
    """
    Use C-based CPU monitor (lightweight)
    Returns None if not available
    """
    try:
        monitor_path = C_BIN_PATH / "cpu_monitor"
        
        if not monitor_path.exists():
            return None
            
        result = subprocess.run(
            [str(monitor_path), str(interval)],
            capture_output=True,
            text=True,
            timeout=interval + 2
        )
        
        if result.returncode == 0:
            return result.stdout
        return None
    except Exception as e:
        print(f"C CPU monitor unavailable: {e}")
        return None

def get_metrics_auto(limit=5, prefer='rust'):
    """
    Automatically choose the best available monitoring method
    
    Args:
        limit: Number of top processes to return
        prefer: 'rust', 'c', or 'python' for preference order
    
    Returns:
        Dictionary with metrics or falls back to Python implementation
    """
    if prefer == 'rust':
        # Try Rust first
        metrics = use_rust_monitor(limit)
        if metrics:
            return {'source': 'rust', 'data': metrics}
    
    if prefer in ['c', 'rust']:
        # Try C implementation
        cpu_data = use_c_cpu_monitor(1)
        proc_data = use_c_process_watcher(limit)
        if cpu_data and proc_data:
            return {
                'source': 'c',
                'data': {
                    'cpu': cpu_data,
                    'processes': proc_data
                }
            }
    
    # Fallback to Python
    from monitor.cpu import get_cpu_metrics
    from monitor.memory import get_memory_metrics
    from monitor.process import get_process_metrics
    
    return {
        'source': 'python',
        'data': {
            'cpu': get_cpu_metrics(),
            'memory': get_memory_metrics(),
            'processes': get_process_metrics(limit=limit)
        }
    }

if __name__ == "__main__":
    import sys
    
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    prefer = sys.argv[2] if len(sys.argv) > 2 else 'rust'
    
    result = get_metrics_auto(limit, prefer)
    print(f"\n=== Using {result['source'].upper()} implementation ===\n")
    print(json.dumps(result['data'], indent=2))
