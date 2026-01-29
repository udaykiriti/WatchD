#!/bin/bash

# Build script for native performance modules

set -e

echo "=== Building Native Performance Modules ==="
echo ""

# Build Rust module
if command -v cargo >/dev/null 2>&1; then
    echo "Building Rust backend..."
    cd monitor/native/rust
    cargo build --release
    cd ../../..
    echo "✓ Rust backend built successfully"
else
    echo "⚠ Cargo not found. Skipping Rust build."
    echo "  Install: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
fi

echo ""

# Build C modules
if command -v gcc >/dev/null 2>&1; then
    echo "Building C backend..."
    cd monitor/native/c
    make clean
    make
    cd ../../..
    echo "✓ C backend built successfully"
else
    echo "⚠ GCC not found. Skipping C build."
    echo "  Install: sudo dnf install gcc make"
fi

echo ""
echo "=== Build Complete ==="
echo ""
echo "Native backends are now available for performance acceleration."
echo "The monitor module will automatically use them when available."
echo ""
echo "Test with: python3 run.py status"
