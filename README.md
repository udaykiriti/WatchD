# SysGuard - Advanced System Health & Auto-Fix Tool

A powerful, real-time system monitoring and automated remediation tool with native Rust/C performance, modern web dashboard, CLI interface, and intelligent auto-fix engine.

## Features

- **Native Performance**: Rust and C implementations for system monitoring (10-100x faster than Python)
- **Real-Time Monitoring**: Track CPU, Memory, Disk, and Process metrics with minimal overhead
- **Live Dashboard**: Beautiful web-based dashboard with WebSocket streaming
- **Auto-Fix Engine**: Automated rules-based system remediation (dry-run mode by default)
- **CLI Interface**: Full-featured command-line interface with Rich formatting
- **Alert History**: Persistent SQLite database for monitoring historical data
- **Process Management**: Identify and manage resource-hungry processes
- **System Snapshots**: Quick health check of your system
- **Configuration-Driven**: YAML-based configuration for easy customization

## Quick Start

### Prerequisites
- Python 3.8+
- Rust (cargo)
- GCC and make
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd sysguard

# Build native backends (REQUIRED)
chmod +x buildnative.sh
./buildnative.sh

# Install Python dependencies
pip install -r requirements.txt
```

**Important**: This project requires native Rust/C backends to be built before use. All system monitoring is performed by these native implementations for maximum performance.

### Basic Usage

**Interactive Menu (Recommended)**
```bash
bash watchD.sh
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

## Architecture

SysGuard uses a hybrid architecture with native performance:

- **Monitor Module**: Thin Python wrappers around native Rust/C implementations
- **Native Backends**: High-performance system monitoring in Rust with C supplements
- **Web Dashboard**: FastAPI server with WebSocket for real-time updates
- **CLI**: Rich-formatted command-line interface
- **Auto-Fix Engine**: Rule-based automated system remediation
- **Storage**: SQLite for persistent alert history

All system metrics (CPU, memory, disk, processes) are collected by native Rust/C code for maximum performance and minimal overhead.

## Project Structure

```
sysguard/
├── monitor/            # System monitoring module
│   ├── cpu.py          # CPU metrics (Rust wrapper)
│   ├── memory.py       # Memory metrics (Rust wrapper)
│   ├── disk.py         # Disk metrics (Rust wrapper)
│   ├── process.py      # Process metrics (Rust wrapper)
│   ├── native_backend.py  # Native backend loader
│   └── native/         # Native implementations (REQUIRED)
│       ├── rust/       # Rust implementation (primary)
│       │   ├── src/lib.rs   # Core monitoring + FFI
│       │   └── Cargo.toml
│       └── c/          # C implementation (supplementary)
│           ├── process_watcher.c
│           └── cpu_monitor.c
├── api/                # FastAPI backend
├── autofix/            # Auto-fix engine
├── cli/                # Command-line interface
├── config/             # YAML configuration
├── docs/               # Documentation
├── storage/            # SQLite database
├── web/                # Dashboard assets
├── buildnative.sh      # Build script (REQUIRED)
├── cleanup.sh          # System cleanup utility
├── run.py              # Main entry point
└── watchD.sh           # Interactive menu
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

## Dependencies

### Native (Required)
- Rust toolchain (cargo)
- GCC compiler
- make

### Python
- **fastapi**: Modern async web framework
- **uvicorn**: ASGI server
- **click**: CLI framework
- **rich**: Beautiful terminal formatting
- **pyyaml**: YAML configuration parsing
- **aiofiles**: Async file operations
- **jinja2**: Template engine
- **websockets**: WebSocket support

Note: psutil is NOT used. All system monitoring is done natively in Rust/C.

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

- Default: Auto-fix runs in dry-run mode (no actual modifications)
- Requires elevated privileges for: cache clearing, service restart, process termination
- Rule conditions use safe evaluation (no arbitrary code execution)
- All actions are logged

## Documentation

See `docs/` for detailed guides:
- [Architecture](docs/ARCHITECTURE.md)
- [Configuration Guide](docs/CONFIG.md)
- [Auto-Fix Rules](docs/AUTOFIX.md)
- [API Reference](docs/API.md)
- [Native Backends](docs/NATIVE_BACKENDS.md)

## Troubleshooting

### Native backends not built
```bash
# Build the backends
./buildnative.sh

# Verify build
ls monitor/native/rust/target/release/libsysguard_monitor.so
ls monitor/native/c/process_watcher
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
**Powered by Rust for maximum performance**
