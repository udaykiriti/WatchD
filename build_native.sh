#!/bin/bash

# Build script for native components

set -e

echo "=== Building Native Components ==="
echo ""

# Build Rust components
if command -v cargo >/dev/null 2>&1; then
    echo "Building Rust monitor..."
    cd rust_monitor
    cargo build --release
    cd ..
    echo "✓ Rust monitor built successfully"
else
    echo "⚠ Cargo not found. Skipping Rust build."
    echo "  Install Rust: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
fi

echo ""

# Build C components
if command -v gcc >/dev/null 2>&1; then
    echo "Building C monitors..."
    cd c_monitor
    make clean
    make
    cd ..
    echo "✓ C monitors built successfully"
else
    echo "⚠ GCC not found. Skipping C build."
    echo "  Install: sudo dnf install gcc make"
fi

echo ""
echo "=== Build Complete ==="
echo ""
echo "Test the components:"
echo "  Rust: ./rust_monitor/target/release/monitor 5"
echo "  C:    ./c_monitor/process_watcher -n 10"
echo "  C:    ./c_monitor/cpu_monitor 1"
echo ""
echo "Use native_bridge.py for automatic fallback:"
echo "  python3 native_bridge.py 5 rust"
