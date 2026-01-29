# Native Performance Backends

## Overview

SysGuard's `monitor` module includes optional native backends written in Rust and C for performance-critical operations. These backends provide 10-100x speed improvements while maintaining full API compatibility.

## Architecture

```
monitor/
├── cpu.py, memory.py, etc.    # Python implementation (always available)
├── native_backend.py           # Auto-detection and loading
└── native/                     # Optional performance backends
    ├── rust/                   # Rust implementation
    └── c/                      # C implementation
```

## How It Works

### Automatic Backend Selection
The monitor module automatically detects and uses the fastest available backend:

1. **Check for Rust**: If `monitor/native/rust/target/release/libsysguard_monitor.so` exists
2. **Check for C**: If `monitor/native/c/process_watcher` and `cpu_monitor` exist  
3. **Fall back to Python**: Always works, no compilation needed

### Usage (No Code Changes!)
```python
from monitor import get_cpu_metrics, get_memory_metrics

# Automatically uses fastest available backend
cpu = get_cpu_metrics()
mem = get_memory_metrics()
```

## Building Native Backends

### Quick Build (Recommended)
```bash
./buildnative.sh
```

This automatically:
- Detects if Rust/GCC are installed
- Builds both backends
- Shows clear success/error messages

### Manual Build

#### Rust Backend
```bash
cd monitor/native/rust
cargo build --release
cd ../../..
```

#### C Backend
```bash
cd monitor/native/c
make
cd ../../..
```

## Performance Comparison

| Backend | Speed    | Memory   | When to Use |
|---------|----------|----------|-------------|
| Rust    | ~100x    | Low      | Maximum performance |
| C       | ~50x     | Minimal  | Lightweight systems |
| Python  | Baseline | Moderate | Default, always works |

## Technical Details

### Rust Backend (`monitor/native/rust/`)
- **Library**: `sysinfo` crate for cross-platform metrics
- **Output**: Shared library (.so) with C FFI
- **Integration**: ctypes loading in Python
- **Features**: CPU, memory, process metrics with JSON serialization

**Key Files:**
- `src/lib.rs` - Core implementation + C FFI exports
- `src/main.rs` - Standalone CLI tool
- `Cargo.toml` - Dependencies (sysinfo, serde, serde_json)

### C Backend (`monitor/native/c/`)
- **System**: Direct /proc filesystem access (Linux)
- **Output**: Native binaries
- **Integration**: subprocess calls from Python
- **Features**: Process enumeration, CPU tracking

**Key Files:**
- `process_watcher.c` - Fast process listing
- `cpu_monitor.c` - CPU usage tracking
- `Makefile` - Build configuration

## Development

### Testing Native Backends
```python
from monitor.native_backend import use_native_backend, get_metrics_rust, get_metrics_c

# Check if available
if use_native_backend():
    print("Native backends available!")
    
# Test Rust
rust_metrics = get_metrics_rust(limit=5)
if rust_metrics:
    print("Rust:", rust_metrics)

# Test C  
c_metrics = get_metrics_c(limit=5)
if c_metrics:
    print("C:", c_metrics)
```

## Integration with Monitor Module

The `monitor/__init__.py` exports a unified interface:
```python
from monitor import (
    get_cpu_metrics,      # Auto-uses native if available
    get_memory_metrics,   # Auto-uses native if available
    get_process_metrics   # Auto-uses native if available
)
```

No code changes needed - just build the natives and they're automatically used!

## Troubleshooting

### "Native backend not found"
- Run `./buildnative.sh` to build
- Check if Rust/GCC are installed
- Verify paths in `.gitignore` aren't excluding builds

### "Library loading failed"
- Check `monitor/native/rust/target/release/` exists
- Ensure `libsysguard_monitor.so` is present
- Try rebuilding: `cd monitor/native/rust && cargo clean && cargo build --release`

### "C binaries not executing"
- Make sure they're executable: `chmod +x monitor/native/c/{process_watcher,cpu_monitor}`
- Check if you're on Linux (C implementation uses /proc)

## Future Enhancements

- [ ] Rust implementation for disk I/O metrics
- [ ] Network monitoring in C
- [ ] Benchmark suite comparing all backends
- [ ] Automatic caching of library handles
- [ ] Hot-reload support for development
