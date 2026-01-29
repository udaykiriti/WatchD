# SysGuard - Advanced System Health & Auto-Fix Tool

A powerful, real-time system monitoring and automated remediation tool with a modern web dashboard, CLI interface, and intelligent auto-fix engine.

## Features

- **Real-Time Monitoring**: Track CPU, Memory, Disk, and Process metrics in real-time
- **Live Dashboard**: Beautiful web-based dashboard with WebSocket streaming
- **Auto-Fix Engine**: Automated rules-based system remediation (dry-run mode by default)
- **CLI Interface**: Full-featured command-line interface with Rich formatting
- **Alert History**: Persistent SQLite database for monitoring historical data
- **Process Management**: Identify and manage resource-hungry processes
- **System Snapshots**: Quick health check of your system
- **Configuration-Driven**: YAML-based configuration for easy customization
- **Native Performance**: Optional Rust & C backends for 10-100x speed improvement
- **Smart Fallback**: Automatically uses native backends when available

## Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- **Optional**: Rust & GCC for native performance backends

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd sysguard

# Install Python dependencies
pip install -r requirements.txt

# Optional: Build native backends for 10-100x better performance
chmod +x buildnative.sh
./buildnative.sh
```

### Basic Usage

**Interactive Menu (Recommended)**
```bash
bash sysguard.sh
```

**Direct Commands**
```bash
# System status snapshot
python3 run.py status

# Live monitoring (real-time terminal UI)
python3 run.py monitor --watch

# Top processes by resource usage
python3 run.py top

# Alert history
python3 run.py history

# Web dashboard
python3 run.py web --host 0.0.0.0 --port 8000
```

## Web Dashboard

Start the web server:
```bash
python3 run.py web
```

Access at: `http://localhost:8000`

Features:
- Real-time CPU & Memory charts
- Disk usage visualization
- Live WebSocket updates (1Hz refresh)
- Connection status indicator

## Auto-Fix Engine

Automated rules trigger predefined actions when conditions are met.

### Configuration

Edit `config/sysguard.yaml`:
```yaml
autofix:
  enabled: false          # Set to true to enable auto-fix
  dry_run: true           # Set to false for actual execution
  rules:
    - name: "High CPU Usage"
      trigger: "cpu_percent > 95"
      action: "notify"
    - name: "High Memory Usage"
      trigger: "memory_percent > 95"
      action: "clear_cache"
```

### Available Actions
- `clear_cache`: Clear system page cache (requires root)
- `restart_<service>`: Restart a systemd service
- `kill_process`: Terminate a process by PID

## Project Structure

```
sysguard/
├── cli/                 # Command-line interface
│   └── main.py         # Click CLI commands
├── monitor/            # System metrics collection (Python)
│   ├── cpu.py          # CPU metrics
│   ├── memory.py       # Memory metrics
│   ├── disk.py         # Disk metrics
│   └── process.py      # Process metrics
├── rustmonitor/          # High-performance Rust implementation
│   ├── src/
│   │   ├── lib.rs       # Core monitoring library
│   │   └── main.rs      # Standalone binary
│   └── Cargo.toml       # Rust dependencies
├── cmonitor/            # Lightweight C implementation
│   ├── process_watcher.c  # Fast process monitoring
│   ├── cpu_monitor.c   # CPU usage tracking
│   └── Makefile        # Build configuration
├── api/                # FastAPI backend
│   └── server.py       # WebSocket & REST endpoints
├── autofix/            # Auto-fix engine
│   ├── engine.py       # Rule evaluation & execution
│   ├── rules.py        # Condition evaluator
│   └── actions.py      # Executable actions
├── storage/            # Data persistence
│   └── db.py          # SQLite database management
├── web/                # Frontend assets
│   └── dashboard.js    # Chart.js visualization
├── config/             # Configuration
│   └── sysguard.yaml   # Settings & thresholds
├── docs/                # Documentation
├── nativebridge.py     # Python-Rust-C integration layer
├── buildnative.sh      # Native components build script
├── run.py              # Entry point
├── cleanup.sh          # Fedora system cleanup utility
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Dependencies

- **psutil**: System and process utilities
- **click**: CLI framework
- **fastapi**: Modern async web framework
- **uvicorn**: ASGI server
- **pyyaml**: YAML configuration parsing
- **rich**: Beautiful terminal formatting
- **aiofiles**: Async file operations
- **jinja2**: Template engine

## Configuration

### Thresholds (`config/sysguard.yaml`)
```yaml
monitoring:
  interval: 2            # Check interval (seconds)
  thresholds:
    cpu_percent: 85.0
    memory_percent: 90.0
    disk_percent: 90.0
```

### Logging
```yaml
logging:
  file: "sysguard.log"
  level: "INFO"
```

## Security Notes

- Default: Auto-fix runs in **dry-run mode** (no actual modifications)
- Requires elevated privileges for: cache clearing, service restart, process termination
- Rule conditions use safe evaluation (no arbitrary code execution)
- All actions are logged

## Performance Optimization

SysGuard includes optional native backends for performance-critical operations:

### Native Backends (Optional)
Build with: `./buildnative.sh`

**Rust Backend** (10-100x faster)
- Memory-safe, zero-cost abstractions
- Automatic integration when built
- Located in `monitor/native/rust/`

**C Backend** (10-50x faster)
- Minimal overhead, direct system calls
- Automatic integration when built
- Located in `monitor/native/c/`

**Python Backend** (Default)
- Always available, no compilation needed
- Automatic fallback if native backends not built

The monitor module automatically detects and uses native backends when available. No code changes needed!

## Documentation

See `docs/` for detailed guides:
- [Architecture](docs/ARCHITECTURE.md)
- [Configuration Guide](docs/CONFIG.md)
- [Auto-Fix Rules](docs/AUTOFIX.md)
- [API Reference](docs/API.md)

## Troubleshooting

### Dashboard not connecting
```bash
# Check if server is running
curl http://localhost:8000/health
```

### Permission denied errors
```bash
# Some features require root
sudo python3 run.py monitor --watch
```

### Database errors
```bash
# Database is auto-initialized on first run
rm storage/sysguard.db
python3 run.py status
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Built for system administrators and DevOps engineers**
