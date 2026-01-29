# SysGuard Architecture

## System Overview

SysGuard follows a modular, layered architecture designed for extensibility and real-time performance.

```
┌─────────────────────────────────────────────────────┐
│            User Interface Layer                      │
│  ┌──────────────────┐      ┌──────────────────┐    │
│  │   CLI (Click)    │      │  Web Dashboard   │    │
│  │   sysguard.sh    │      │  (FastAPI+JS)    │    │
│  └──────────────────┘      └──────────────────┘    │
└─────────────────────────────────────────────────────┘
           │                          │
           ▼                          ▼
┌─────────────────────────────────────────────────────┐
│         Application Logic Layer                      │
│  ┌──────────────────────────────────────────────┐  │
│  │    Auto-Fix Engine (rules + actions)         │  │
│  │    - Condition evaluation                    │  │
│  │    - Action execution (dry-run safe)         │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────┐
│         Metrics Collection Layer                     │
│  ┌──────────────┐ ┌──────────┐ ┌──────────┐        │
│  │   CPU        │ │ Memory   │ │  Disk    │        │
│  ├──────────────┤ ├──────────┤ ├──────────┤        │
│  │ Processes    │                                   │
│  └──────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────┐
│       System Interface Layer (psutil)                │
│       Operating System (Linux/Unix/Windows)          │
└─────────────────────────────────────────────────────┘
```

## Components

### 1. **CLI Interface** (`cli/main.py`)
- Entry point for command-line usage
- Built with Click framework for robust command handling
- Commands:
  - `status`: One-time system snapshot
  - `monitor --watch`: Live real-time monitoring
  - `top`: Top resource-consuming processes
  - `history`: Alert history from database
  - `web`: Start the web dashboard
  
**Design Pattern**: Command Router

### 2. **Monitoring Engine** (`monitor/`)
- Collects raw system metrics via `psutil`
- Modules:
  - `cpu.py`: Usage %, core count, load average
  - `memory.py`: RAM usage in MB and %
  - `disk.py`: Storage usage per partition
  - `process.py`: Process listing with filtering/sorting

**Design Pattern**: Data Collector

### 3. **Auto-Fix Engine** (`autofix/`)

#### Components:
- **engine.py**: Orchestrator
  - Loads rules from config
  - Collects metrics
  - Evaluates conditions
  - Executes actions (safe in dry-run mode)
  
- **rules.py**: Condition Evaluator
  - Parses trigger strings (e.g., "cpu_percent > 95")
  - Flattens nested metrics for easy access
  - Safe evaluation (restricted builtins)
  
- **actions.py**: Action Executors
  - `kill_process(pid)`: Send SIGKILL
  - `restart_service(name)`: Systemd integration
  - `clear_cache()`: Drop page cache

**Design Pattern**: Rules Engine + Command Pattern

### 4. **Web API** (`api/server.py`)
- FastAPI-based REST + WebSocket server
- Endpoints:
  - `GET /`: Serve dashboard HTML
  - `GET /health`: Current system metrics (JSON)
  - `WebSocket /ws`: Stream metrics at 1Hz
  
**Design Pattern**: Real-time Data Stream

### 5. **Storage Layer** (`storage/db.py`)
- SQLite for historical data
- Tables:
  - `alerts`: Timestamp, type, message
  - `metrics`: Timestamp, CPU%, Memory%, Disk%
  
**Design Pattern**: Repository Pattern

### 6. **Configuration** (`config/sysguard.yaml`)
- YAML-based configuration
- Sections:
  - `monitoring`: Intervals & thresholds
  - `autofix`: Rules & execution mode
  - `logging`: File path & level

**Design Pattern**: Configuration as Code

## Data Flow

### Live Monitoring Flow
```
CLI/Web → Monitor Loop → Collect Metrics → Evaluate Rules → Execute Actions → Log Results → Display
                              ↓
                        Storage (History)
```

### Web Dashboard Flow
```
Browser → WebSocket /ws → Stream Metrics (1Hz) → JavaScript Charts → Real-time Visualization
```

## Key Design Decisions

1. **Dry-Run by Default**: Safety first - auto-fix requires explicit config change
2. **Modular Metrics**: Each metric type in separate file for easy extension
3. **YAML Configuration**: Human-readable, no code changes needed
4. **SQLite Storage**: Lightweight, no external dependencies
5. **WebSocket Streaming**: Real-time updates without polling
6. **psutil Abstraction**: Works across Linux, macOS, Windows

## Extension Points

### Adding a New Metric
1. Create `monitor/newmetric.py`
2. Implement `get_newmetric_metrics()`
3. Import in `cli/main.py`
4. Use in monitoring loops

### Adding a New Action
1. Implement in `autofix/actions.py`
2. Register in `autofix/engine.execute_action()`
3. Add to YAML rules

### Adding a New Threshold
1. Add to `config/sysguard.yaml`
2. Reference in rule conditions
3. Use in auto-fix engine

## Performance Considerations

- **Metrics Collection**: ~10ms per call (psutil optimized)
- **Web Updates**: 1Hz WebSocket for real-time feel without overload
- **Database**: Append-only inserts for fast logging
- **Auto-Fix**: Rule evaluation in ms, actions async-ready

## Security Considerations

- **Dry-Run Mode**: Default prevents accidental system changes
- **Safe Evaluation**: Rule conditions use restricted Python eval
- **Logging**: All actions logged for audit trail
- **Privilege Escalation**: Certain actions require root (cache clear, service restart)
