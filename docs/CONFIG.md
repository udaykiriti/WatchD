# Configuration Guide

SysGuard is configured via `config/sysguard.yaml`. This guide covers all configuration options.

## File Location
```
sysguard/config/sysguard.yaml
```

## Complete Configuration Template

```yaml
monitoring:
  interval: 2
  thresholds:
    cpu_percent: 85.0
    memory_percent: 90.0
    disk_percent: 90.0

autofix:
  enabled: false
  dry_run: true
  rules:
    - name: "Rule Name"
      trigger: "condition"
      action: "action_name"

logging:
  file: "sysguard.log"
  level: "INFO"
```

## Monitoring Section

### `interval` (integer, seconds)
How often to collect and evaluate metrics.

```yaml
monitoring:
  interval: 2  # Check every 2 seconds
```

**Recommended values**: 1-5 seconds
- Lower = more responsive but higher CPU
- Higher = lower overhead but less responsive

### `thresholds` (float, percent 0-100)
Alert thresholds for triggering auto-fix rules.

```yaml
thresholds:
  cpu_percent: 85.0      # Alert when CPU > 85%
  memory_percent: 90.0   # Alert when Memory > 90%
  disk_percent: 90.0     # Alert when Disk > 90%
```

**Usage**: These values are available in rule conditions:
```yaml
trigger: "cpu_percent > 85"
```

## Auto-Fix Section

### `enabled` (boolean)
Enable/disable the entire auto-fix engine.

```yaml
autofix:
  enabled: false  # Set to true to activate
```

### `dry_run` (boolean)
**IMPORTANT**: When true, actions are logged but NOT executed.

```yaml
autofix:
  dry_run: true   # Safe mode - no actual changes
  dry_run: false  # Actual execution (requires careful configuration)
```

**Workflow**:
1. Start with `dry_run: true`
2. Test rules in monitoring
3. Verify logs show expected actions
4. Change to `dry_run: false` when confident

### `rules` (array of objects)
Array of auto-fix rules.

```yaml
rules:
  - name: "High CPU Usage"
    trigger: "cpu_percent > 95"
    action: "notify"
    
  - name: "High Memory Usage"
    trigger: "memory_percent > 95"
    action: "clear_cache"
    
  - name: "Service Recovery"
    trigger: "cpu_percent > 90"
    action: "restart_webserver"
```

#### Rule Properties

**`name`** (string)
Human-readable rule identifier.

```yaml
name: "High CPU Usage"
```

**`trigger`** (string)
Condition that must be true to fire the rule.

Available variables:
- `cpu_percent`: CPU usage percentage
- `memory_percent`: Memory usage percentage
- `disk_percent`: Disk usage percentage
- Full metric dictionaries (e.g., `cpu_usage_percent`)

Examples:
```yaml
trigger: "cpu_percent > 95"
trigger: "memory_percent >= 90"
trigger: "disk_percent > 85"
trigger: "cpu_percent > 80 and memory_percent > 85"  # AND conditions
```

**Operators**: `>`, `<`, `>=`, `<=`, `==`, `!=`

**`action`** (string)
Action to execute when rule triggers.

Available actions:
- `notify`: Log notification (safe, no-op)
- `clear_cache`: Drop system page cache
- `restart_<service>`: Restart systemd service

Examples:
```yaml
action: "notify"
action: "clear_cache"
action: "restart_nginx"
action: "restart_postgres"
action: "restart_docker"
```

## Logging Section

### `file` (string)
Log file path (relative to project root).

```yaml
logging:
  file: "sysguard.log"
```

### `level` (string)
Logging verbosity.

```yaml
logging:
  level: "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

**Recommended**:
- `DEBUG`: Development, verbose output
- `INFO`: Production, standard logging
- `WARNING`: Minimal, errors only
- `ERROR`: Silent except critical failures

## Example Configurations

### Minimal (Monitoring Only)
```yaml
monitoring:
  interval: 2
  thresholds:
    cpu_percent: 85.0
    memory_percent: 90.0
    disk_percent: 90.0

autofix:
  enabled: false

logging:
  file: "sysguard.log"
  level: "INFO"
```

### Development (With Dry-Run Testing)
```yaml
monitoring:
  interval: 1  # Faster checks
  thresholds:
    cpu_percent: 80.0
    memory_percent: 85.0
    disk_percent: 85.0

autofix:
  enabled: true
  dry_run: true  # Test mode
  rules:
    - name: "High CPU"
      trigger: "cpu_percent > 80"
      action: "notify"
    - name: "High Memory"
      trigger: "memory_percent > 85"
      action: "clear_cache"

logging:
  file: "sysguard.log"
  level: "DEBUG"
```

### Production (Auto-Fix Enabled)
```yaml
monitoring:
  interval: 3
  thresholds:
    cpu_percent: 85.0
    memory_percent: 90.0
    disk_percent: 90.0

autofix:
  enabled: true
  dry_run: false  # ACTUAL EXECUTION
  rules:
    - name: "High Memory Clear Cache"
      trigger: "memory_percent > 95"
      action: "clear_cache"
    - name: "Restart Web Service"
      trigger: "cpu_percent > 95"
      action: "restart_nginx"
    - name: "Disk Warning"
      trigger: "disk_percent > 95"
      action: "notify"

logging:
  file: "sysguard.log"
  level: "INFO"
```

### High-Performance (Web Dashboard)
```yaml
monitoring:
  interval: 1  # 1Hz update rate matches dashboard
  thresholds:
    cpu_percent: 85.0
    memory_percent: 90.0
    disk_percent: 90.0

autofix:
  enabled: false

logging:
  file: "sysguard.log"
  level: "WARNING"
```

## Configuration Best Practices

1. **Start Conservative**: High thresholds (85-95%) before tuning
2. **Test in Dry-Run**: Always test rules before enabling execution
3. **Log Everything**: Keep `level: "INFO"` initially
4. **Monitor Logs**: Review `sysguard.log` after changes
5. **Use Intervals**: Set monitoring `interval` based on your needs
6. **Rule Order**: Rules are evaluated in order; order them logically
7. **Service Names**: Use exact systemd service names for `restart_<service>`

## Reloading Configuration

Configuration is loaded at startup. To apply changes:

```bash
# Restart the monitoring
python3 run.py monitor --watch  # Ctrl+C then restart

# Or restart the web server
python3 run.py web  # Ctrl+C then restart
```

No need to restart the entire application between configuration edits.

## Troubleshooting

### Rules not triggering?
1. Check thresholds - are they being exceeded?
2. Enable `DEBUG` logging to see rule evaluations
3. Verify trigger syntax is correct

### Actions not executing?
1. Check `dry_run` setting (should be `false`)
2. Check `enabled` setting (should be `true`)
3. Review logs for permission errors
4. Verify service names are correct for `restart_` actions

### Performance issues?
1. Increase `interval` (less frequent checks)
2. Reduce number of rules
3. Disable features not in use

### Permission denied errors?
```bash
# Some actions require root privileges
sudo python3 run.py monitor --watch
```
