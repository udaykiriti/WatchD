#!/usr/bin/env python3
"""
SysGuard API Server - Python Wrapper
Launches native C web server for better performance.
For Python-only mode, use: uvicorn api.server:app_fallback
"""
import subprocess
import sys
import os

def main():
    native_server = os.path.join(os.path.dirname(__file__), "native/webserver")
    
    if os.path.exists(native_server):
        print("[OK] Starting native C web server...")
        try:
            subprocess.run([native_server], check=True)
        except KeyboardInterrupt:
            print("\n[OK] Server stopped")
        return 0
    else:
        print("[ERROR] Native server not found. Build it first:")
        print("  ./buildnative.sh")
        return 1

if __name__ == "__main__":
    sys.exit(main())

# Fallback FastAPI server for Python-only environments
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
from monitor.cpu import get_cpu_metrics
from monitor.memory import get_memory_metrics
from monitor.disk import get_disk_metrics
from monitor.process import get_process_metrics

app_fallback = FastAPI()

static_dir = os.path.join(os.path.dirname(__file__), "../web")
app_fallback.mount("/static", StaticFiles(directory=static_dir), name="static")

@app_fallback.get("/")
async def read_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app_fallback.get("/dashboard.js")
async def read_js():
    return FileResponse(os.path.join(static_dir, "dashboard.js"))

@app_fallback.get("/health")
def health():
    return {
        "cpu": get_cpu_metrics(),
        "memory": get_memory_metrics(),
        "disk": get_disk_metrics(),
        "processes": get_process_list()[:10]
    }

@app_fallback.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            await ws.send_json({
                "cpu": get_cpu_metrics(),
                "memory": get_memory_metrics(),
                "disk": get_disk_metrics(),
                "processes": get_process_list()[:10]
            })
            await asyncio.sleep(1)
    except Exception:
        pass