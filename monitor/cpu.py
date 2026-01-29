"""
CPU monitoring - Native backend wrapper
Requires Rust/C native backends to be built
"""

from .native_backend import get_metrics_rust

def get_cpu_metrics():
    """Returns a dictionary of CPU metrics from native Rust backend."""
    metrics = get_metrics_rust()
    if metrics and 'cpu' in metrics:
        cpu = metrics['cpu']
        return {
            "usage_percent": cpu['usage_percent'],
            "cores_logical": cpu['cores_logical'],
            "cores_physical": cpu.get('cores_physical', cpu['cores_logical'] // 2),
            "load_avg": [cpu['load_avg_1'], cpu['load_avg_5'], cpu['load_avg_15']]
        }
    raise RuntimeError("Native backend not available. Run: ./scripts/buildnative.sh")

def cpu_info():
    """Returns a formatted string for CPU info."""
    metrics = get_cpu_metrics()
    return f"CPU Usage: {metrics['usage_percent']:.1f}% | Cores: {metrics['cores_logical']}"
