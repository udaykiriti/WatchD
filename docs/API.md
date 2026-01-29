# API Reference

SysGuard provides a FastAPI-based REST API and WebSocket for real-time metrics streaming.

## Server Setup

### Start the API Server
```bash
python3 run.py web --host 0.0.0.0 --port 8000
```

### Command Options
```bash
--host 0.0.0.0    # Bind to all interfaces (default: 0.0.0.0)
--port 8000       # Port to listen on (default: 8000)
```

### URL Patterns
- REST: `http://localhost:8000/api/*`
- WebSocket: `ws://localhost:8000/ws`
- Static Files: `http://localhost:8000/static/*`

## REST Endpoints

### `GET /health`
Get current system health metrics.

**Request**
```bash
curl http://localhost:8000/health
```

**Response** (JSON)
```json
{
  "cpu": {
    "usage_percent": 45.2,
    "cores_logical": 8,
    "cores_physical": 4,
    "load_avg": [25.0, 30.0, 35.0]
  },
  "memory": {
    "total_mb": 16384,
    "used_mb": 8192,
    "available_mb": 8192,
    "percent": 50.0
  },
  "disk": {
    "total_gb": 256,
    "used_gb": 128,
    "free_gb": 128,
    "percent": 50.0
  }
}
```

**Status Codes**
- `200 OK`: Metrics retrieved successfully
- `500 Internal Server Error`: System error

**Response Time**: ~50ms

### `GET /`
Serve the dashboard HTML.

**Request**
```bash
curl http://localhost:8000/
```

**Response**: HTML (index.html)

### `GET /dashboard.js`
Serve the dashboard JavaScript.

**Request**
```bash
curl http://localhost:8000/dashboard.js
```

**Response**: JavaScript file

## WebSocket Endpoint

### `WS /ws`
Stream system metrics in real-time.

**Connection**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

**Message Format** (JSON, sent every 1 second)
```json
{
  "cpu": {
    "usage_percent": 45.2,
    "cores_logical": 8,
    "cores_physical": 4,
    "load_avg": [25.0, 30.0, 35.0]
  },
  "memory": {
    "total_mb": 16384,
    "used_mb": 8192,
    "available_mb": 8192,
    "percent": 50.0
  },
  "disk": {
    "total_gb": 256,
    "used_gb": 128,
    "free_gb": 128,
    "percent": 50.0
  }
}
```

**Update Frequency**: 1 message per second (1 Hz)

**Example Handler** (JavaScript)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('CPU:', data.cpu.usage_percent + '%');
  console.log('Memory:', data.memory.percent + '%');
  console.log('Disk:', data.disk.percent + '%');
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected');
};
```

**Reconnection** (Recommended)
```javascript
function connect() {
  const ws = new WebSocket('ws://localhost:8000/ws');
  
  ws.onmessage = (event) => {
    // Handle message
  };
  
  ws.onclose = () => {
    // Reconnect after 3 seconds
    setTimeout(connect, 3000);
  };
}

connect();
```

## Data Models

### CPU Metrics
```json
{
  "usage_percent": 45.2,
  "cores_logical": 8,
  "cores_physical": 4,
  "load_avg": [25.0, 30.0, 35.0]
}
```

**Fields**:
- `usage_percent` (float): CPU usage as percentage (0-100)
- `cores_logical` (int): Number of logical cores (including hyperthreading)
- `cores_physical` (int): Number of physical cores
- `load_avg` (array): 1, 5, 15-minute load averages (normalized to %)

### Memory Metrics
```json
{
  "total_mb": 16384,
  "used_mb": 8192,
  "available_mb": 8192,
  "percent": 50.0
}
```

**Fields**:
- `total_mb` (int): Total RAM in megabytes
- `used_mb` (int): Used RAM in megabytes
- `available_mb` (int): Available RAM in megabytes
- `percent` (float): Usage percentage (0-100)

### Disk Metrics
```json
{
  "total_gb": 256,
  "used_gb": 128,
  "free_gb": 128,
  "percent": 50.0
}
```

**Fields**:
- `total_gb` (int): Total disk in gigabytes
- `used_gb` (int): Used disk in gigabytes
- `free_gb` (int): Free disk in gigabytes
- `percent` (float): Usage percentage (0-100)

## Example Use Cases

### 1. Build a Custom Dashboard
```html
<!DOCTYPE html>
<html>
<head>
  <title>SysGuard Dashboard</title>
</head>
<body>
  <h1>System Metrics</h1>
  <div id="metrics"></div>
  
  <script>
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      document.getElementById('metrics').innerHTML = `
        <p>CPU: ${data.cpu.usage_percent.toFixed(1)}%</p>
        <p>Memory: ${data.memory.percent.toFixed(1)}%</p>
        <p>Disk: ${data.disk.percent.toFixed(1)}%</p>
      `;
    };
  </script>
</body>
</html>
```

### 2. Monitor via Curl
```bash
# Single query
curl http://localhost:8000/health | jq '.cpu.usage_percent'

# Continuous monitoring (Linux)
watch -n 1 'curl -s http://localhost:8000/health | jq'
```

### 3. Python Client
```python
import asyncio
import websockets
import json

async def monitor():
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        while True:
            data = json.loads(await ws.recv())
            print(f"CPU: {data['cpu']['usage_percent']:.1f}%")
            print(f"Memory: {data['memory']['percent']:.1f}%")
            print(f"Disk: {data['disk']['percent']:.1f}%")
            print("---")

asyncio.run(monitor())
```

### 4. Node.js Client
```javascript
const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:8000/ws');

ws.on('open', () => {
  console.log('Connected');
});

ws.on('message', (data) => {
  const metrics = JSON.parse(data);
  console.log(`CPU: ${metrics.cpu.usage_percent.toFixed(1)}%`);
  console.log(`Memory: ${metrics.memory.percent.toFixed(1)}%`);
  console.log(`Disk: ${metrics.disk.percent.toFixed(1)}%`);
});

ws.on('close', () => {
  console.log('Disconnected');
  setTimeout(() => ws.connect(), 3000);
});
```

## Performance

### Response Times
- `/health`: ~50ms
- WebSocket message: <1ms (1Hz update rate)

### Network Usage
- REST: ~500 bytes per request
- WebSocket: ~200 bytes per second (1Hz)

### System Impact
- <1% CPU overhead
- <5MB memory footprint

## Error Handling

### WebSocket Disconnection
Implement automatic reconnection:
```javascript
function connect() {
  const ws = new WebSocket('ws://localhost:8000/ws');
  ws.onclose = () => setTimeout(connect, 3000);
  return ws;
}
```

### API Errors
REST endpoints return standard HTTP status codes:
```
200 OK
500 Internal Server Error
```

## CORS

Currently, CORS is **not enabled**. For cross-origin access, use:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Rate Limiting

Not currently implemented. For production, consider:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

## Authentication

Not currently implemented. For production:
```python
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

@app.get("/health")
async def health(credentials: HTTPAuthCredentials = Depends(security)):
    # Verify token
    return metrics
```

## Documentation

Live API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
