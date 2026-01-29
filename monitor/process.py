"""
Process monitoring - Native backend wrapper
Requires Rust/C native backends to be built
"""

from .native_backend import get_metrics_rust

def get_process_metrics(limit=5, sort_by='cpu'):
    """
    Returns a list of top resource-consuming processes from native Rust backend.
    sort_by: 'cpu' or 'memory' (currently only 'cpu' is implemented in native)
    """
    metrics = get_metrics_rust(limit=limit)
    if metrics and 'top_processes' in metrics:
        processes = metrics['top_processes']
        total_memory = get_total_memory()
        
        return [
            {
                'pid': p['pid'],
                'name': p['name'],
                'cpu_percent': p['cpu_percent'],
                'memory_percent': (p['memory_mb'] / total_memory) * 100 if p.get('memory_mb') and total_memory > 0 else 0,
                'username': 'unknown'
            }
            for p in processes
        ]
    raise RuntimeError("Native backend not available. Run: ./scripts/buildnative.sh")

def get_total_memory():
    """Helper to get total memory for percentage calculation (cached)."""
    from .memory import get_memory_metrics
    mem = get_memory_metrics()
    return mem['total_mb']

_process_cache = []
_cache_timestamp = 0

def get_process_list(limit=10):
    """Alias for get_process_metrics for API compatibility"""
    return get_process_metrics(limit)
