"""
Memory monitoring - Native backend wrapper
Requires Rust/C native backends to be built
"""

from .native_backend import get_metrics_rust

def get_memory_metrics():
    """Returns a dictionary of Memory metrics from native Rust backend."""
    metrics = get_metrics_rust()
    if metrics and 'memory' in metrics:
        return metrics['memory']
    raise RuntimeError("Native backend not available. Run: ./scripts/buildnative.sh")

def memory_info():
    """Returns a formatted string for memory info."""
    metrics = get_memory_metrics()
    return f"Memory: {metrics['used_mb']}MB / {metrics['total_mb']}MB ({metrics['percent']:.1f}%)"
