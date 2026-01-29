import psutil

def get_disk_metrics(path="/"):
    """Returns a dictionary of Disk metrics."""
    try:
        disk = psutil.disk_usage(path)
        return {
            "total_gb": disk.total // (1024 * 1024 * 1024),
            "used_gb": disk.used // (1024 * 1024 * 1024),
            "free_gb": disk.free // (1024 * 1024 * 1024),
            "percent": disk.percent
        }
    except Exception as e:
        return {"error": str(e)}

def disk_info():
    metrics = get_disk_metrics()
    if "error" in metrics:
        return f"Disk Error: {metrics['error']}"
    return f"Disk: {metrics['used_gb']}GB / {metrics['total_gb']}GB ({metrics['percent']}%)"