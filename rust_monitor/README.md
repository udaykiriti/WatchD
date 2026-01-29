# Rust System Monitor

Fast, memory-safe system metrics collector written in Rust.

## Build

```bash
cargo build --release
```

## Usage

### As standalone binary:
```bash
./target/release/monitor [limit]
```

### As library (from Python):
```python
import ctypes
import json

lib = ctypes.CDLL('./target/release/libsysguard_monitor.so')
lib.rust_get_metrics_json.restype = ctypes.c_char_p
lib.rust_free_string.argtypes = [ctypes.c_char_p]

json_str = lib.rust_get_metrics_json(5)
metrics = json.loads(json_str.decode('utf-8'))
lib.rust_free_string(json_str)
print(metrics)
```

## Features

- Fast CPU metrics collection
- Memory usage tracking
- Top process monitoring
- Zero-copy JSON serialization
- Thread-safe operations
