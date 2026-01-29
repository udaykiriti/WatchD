import psutil

def get_cpu_metrics():
    """Returns a dictionary of CPU metrics."""
    return {
        "usage_percent": psutil.cpu_percent(interval=0.1), # Short interval for responsiveness
        "cores_logical": psutil.cpu_count(logical=True),
        "cores_physical": psutil.cpu_count(logical=False),
        "load_avg": [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()] # Normalize load avg
    }

def cpu_info():
    """Returns a formatted string for CPU info (Legacy support)."""
    metrics = get_cpu_metrics()
    return f"CPU Usage: {metrics['usage_percent']}% | Cores: {metrics['cores_logical']}"