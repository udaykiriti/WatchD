import click
import yaml
import os
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from monitor.cpu import get_cpu_metrics
from monitor.memory import get_memory_metrics
from monitor.disk import get_disk_metrics
from monitor.process import get_process_metrics
from autofix.engine import AutoFixEngine
from storage.db import init_db, log_metrics, get_recent_alerts

console = Console()
_config_cache = None

def load_config():
    """Load configuration with caching to avoid repeated YAML parsing"""
    global _config_cache
    if _config_cache is None:
        config_path = os.path.join(os.path.dirname(__file__), "../config/sysguard.yaml")
        with open(config_path, "r") as f:
            _config_cache = yaml.safe_load(f)
    return _config_cache

def build_metrics_table(cpu, mem, disk, title="System Status"):
    """Build reusable metrics display table"""
    table = Table(title=title)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("CPU Usage", f"{cpu['usage_percent']}% ({cpu['cores_logical']} cores)")
    table.add_row("Memory", f"{mem['used_mb']}MB / {mem['total_mb']}MB ({mem['percent']}%)")
    if "error" not in disk:
        table.add_row("Disk", f"{disk['used_gb']}GB / {disk['total_gb']}GB ({disk['percent']}%)")
    else:
        table.add_row("Disk", f"[red]{disk['error']}[/red]")
    return table

def fetch_all_metrics():
    """Fetch all metrics in one call to reduce system overhead"""
    return {
        'cpu': get_cpu_metrics(),
        'memory': get_memory_metrics(),
        'disk': get_disk_metrics()
    }

@click.group()
def sysguard():
    """System Health & Auto-Fix Tool"""
    init_db()

@sysguard.command()
def status():
    """Show system status snapshot"""
    metrics = fetch_all_metrics()
    console.print(build_metrics_table(metrics['cpu'], metrics['memory'], metrics['disk']))

@sysguard.command()
def top():
    """Show top processes"""
    procs = get_process_metrics(limit=10)
    table = Table(title="Top Processes (by CPU)")
    table.add_column("PID", style="dim")
    table.add_column("Name", style="green")
    table.add_column("User")
    table.add_column("CPU %", justify="right")
    table.add_column("Mem %", justify="right")
    
    for p in procs:
        table.add_row(
            str(p['pid']), 
            p['name'], 
            p['username'], 
            f"{p['cpu_percent']:.1f}", 
            f"{p['memory_percent']:.1f}"
        )
    console.print(table)

@sysguard.command()
@click.option("--watch", is_flag=True, help="Keep running and updating")
def monitor(watch):
    """Monitor system health with Autofix"""
    config = load_config()
    engine = AutoFixEngine(config)
    
    if not watch:
        alerts = engine.run_check()
        status()
        if alerts:
            console.print("[bold red]Autofix Alerts:[/bold red]\n" + "\n".join(f"- {a}" for a in alerts))
        return

    # Live Watch Mode
    import time
    with Live(console=console, refresh_per_second=1) as live:
        while True:
            metrics = fetch_all_metrics()
            cpu, mem, disk = metrics['cpu'], metrics['memory'], metrics['disk']
            
            log_metrics(cpu['usage_percent'], mem['percent'], disk.get('percent', 0))
            alerts = engine.run_check()
            
            table = Table(title="Live System Monitor")
            table.add_column("Metric")
            table.add_column("Value")
            table.add_row("CPU", f"{cpu['usage_percent']:.1f}%")
            table.add_row("Memory", f"{mem['percent']:.1f}%")
            table.add_row("Disk", f"{disk.get('percent', 0):.1f}%")
            
            proc_table = Table(title="Top Processes")
            proc_table.add_column("Name")
            proc_table.add_column("CPU%")
            for p in get_process_metrics(limit=5):
                proc_table.add_row(p['name'], f"{p['cpu_percent']:.1f}")
                
            alert_panel = Panel(
                "\n".join(alerts) if alerts else "No active alerts",
                title="Autofix Status",
                border_style="red" if alerts else "green"
            )
            
            grid = Table.grid()
            grid.add_row(table)
            grid.add_row(proc_table)
            grid.add_row(alert_panel)
            
            live.update(grid)
            time.sleep(config['monitoring']['interval'])

@sysguard.command()
def history():
    """Show alert history"""
    alerts = get_recent_alerts()
    table = Table(title="Alert History")
    table.add_column("Time", style="dim")
    table.add_column("Type", style="red")
    table.add_column("Message")
    
    for a in alerts:
        table.add_row(a[0], a[1], a[2])
    console.print(table)

@sysguard.command()
@click.option("--host", default="0.0.0.0", help="Host to bind")
@click.option("--port", default=8000, help="Port to bind")
def web(host, port):
    """Start the Web Dashboard"""
    import uvicorn
    console.print(f"[green]Starting SysGuard Web Dashboard at http://{host}:{port}[/green]")
    uvicorn.run("api.server:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    sysguard()