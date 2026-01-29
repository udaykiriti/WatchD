from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import os
from monitor.cpu import get_cpu_metrics
from monitor.memory import get_memory_metrics
from monitor.disk import get_disk_metrics

app = FastAPI()

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "../web")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/dashboard.js")
async def read_js():
    return FileResponse(os.path.join(static_dir, "dashboard.js"))

@app.get("/health")
def health():
    return {
        "cpu": get_cpu_metrics(),
        "memory": get_memory_metrics(),
        "disk": get_disk_metrics(),
    }

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = {
                "cpu": get_cpu_metrics(),
                "memory": get_memory_metrics(),
                "disk": get_disk_metrics(),
            }
            await ws.send_json(data)
            await asyncio.sleep(1)
    except Exception:
        pass # Handle disconnect