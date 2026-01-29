import psutil

def get_process_metrics(limit=5, sort_by='cpu'):
    """
    Returns a list of top resource-consuming processes.
    sort_by: 'cpu' or 'memory'
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
        try:
            pinfo = proc.info
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Sort
    if sort_by == 'memory':
        processes.sort(key=lambda p: p['memory_percent'] or 0, reverse=True)
    else:
        processes.sort(key=lambda p: p['cpu_percent'] or 0, reverse=True)

    return processes[:limit]
