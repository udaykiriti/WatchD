"""
Disk monitoring - Native backend wrapper
Requires Rust/C native backends to be built
"""

from .native_backend import get_metrics_rust

def get_disk_metrics(path="/"):
    """Returns a dictionary of Disk metrics from native Rust backend."""
    metrics = get_metrics_rust()
    if metrics and 'disk' in metrics:
        return metrics['disk']
    raise RuntimeError("Native backend not available. Run: ./buildnative.sh")

def disk_info():
    """Returns a formatted string for disk info."""
    metrics = get_disk_metrics()
    if "error" in metrics:
        return f"Disk Error: {metrics['error']}"
    return f"Disk: {metrics['used_gb']}GB / {metrics['total_gb']}GB ({metrics['percent']:.1f}%)"
