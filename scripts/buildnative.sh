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
    echo "[OK] Rust backend built successfully"
else
    echo "[Warning]: Cargo not found. Skipping Rust build."
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
    echo "[OK] C backend built successfully"
else
    echo "[Warning]: GCC not found. Skipping C build."
    echo "  Install: sudo dnf install gcc make"
fi

echo ""

# Build native web server
if command -v gcc >/dev/null 2>&1; then
    echo "Building native web server..."
    cd api/native
    make clean
    make
    cd ../..
    echo "[OK]: Native web server built successfully"
else
    echo "[Warning]: Skipping native web server build (no GCC)"
fi

echo ""
echo "<---- Build Complete ---->"
echo ""
echo "Native backends are now available for performance acceleration."
echo "The monitor module will automatically use them when available."
echo ""
echo "Start web server: python3 api/server.py"
echo "Or fallback mode: uvicorn api.server:app_fallback --port 8000"
echo "Test CLI: python3 run.py status"
