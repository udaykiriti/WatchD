import psutil

def get_memory_metrics():
    """Returns a dictionary of Memory metrics."""
    mem = psutil.virtual_memory()
    return {
        "total_mb": mem.total // (1024 * 1024),
        "used_mb": mem.used // (1024 * 1024),
        "available_mb": mem.available // (1024 * 1024),
        "percent": mem.percent
    }

def memory_info():
    metrics = get_memory_metrics()
    return f"Memory: {metrics['used_mb']}MB / {metrics['total_mb']}MB ({metrics['percent']}%)"