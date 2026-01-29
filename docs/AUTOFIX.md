# 🤖 Auto-Fix Rules Guide

This guide explains how to create and manage auto-fix rules in SysGuard.

## Overview

Auto-Fix is a rules engine that automatically takes actions when system conditions are met.

**Key Features**:
- Condition-based triggers
- Predefined remediation actions
- Dry-run mode for safe testing
- Comprehensive logging

## Rule Anatomy

```yaml
- name: "Descriptive Rule Name"
  trigger: "condition_expression"
  action: "action_name"
```

### Components

#### `name` (String)
A human-readable identifier for the rule.

```yaml
name: "High CPU Usage Alert"
name: "Emergency Memory Clearance"
name: "Service Recovery - Web"
```

#### `trigger` (String Expression)
Condition that must evaluate to `true` for the rule to fire.

```yaml
trigger: "cpu_percent > 80"
trigger: "memory_percent >= 90"
trigger: "disk_percent > 85"
```

#### `action` (String)
The action to execute when the rule triggers.

```yaml
action: "notify"           # Log notification
action: "clear_cache"      # Clear page cache
action: "restart_nginx"    # Restart service
```

## Available Variables

### Basic Metrics
```yaml
cpu_percent       # CPU usage (0-100)
memory_percent    # Memory usage (0-100)
disk_percent      # Disk usage (0-100)
```

### Nested Metrics (Advanced)
```yaml
cpu_usage_percent         # CPU usage percentage
cpu_cores_logical         # Number of logical cores
cpu_cores_physical        # Number of physical cores
memory_used_mb            # RAM used (megabytes)
memory_total_mb           # Total RAM (megabytes)
memory_available_mb       # Available RAM (megabytes)
disk_used_gb              # Disk used (gigabytes)
disk_total_gb             # Total disk (gigabytes)
disk_free_gb              # Free disk (gigabytes)
```

## Triggers

### Basic Comparisons

**Greater Than**
```yaml
trigger: "cpu_percent > 90"
trigger: "memory_percent > 85"
```

**Less Than**
```yaml
trigger: "cpu_percent < 20"
trigger: "memory_percent < 50"
```

**Greater Than or Equal**
```yaml
trigger: "disk_percent >= 90"
```

**Less Than or Equal**
```yaml
trigger: "memory_percent <= 50"
```

**Equal**
```yaml
trigger: "cpu_percent == 100"
```

**Not Equal**
```yaml
trigger: "cpu_percent != 0"
```

### Complex Conditions

**AND (both conditions true)**
```yaml
trigger: "cpu_percent > 80 and memory_percent > 80"
```

**OR (either condition true)**
```yaml
trigger: "cpu_percent > 95 or memory_percent > 95"
```

**Nested Logic**
```yaml
trigger: "(cpu_percent > 90 and memory_percent > 85) or disk_percent > 95"
```

## Available Actions

### 1. `notify`
Log a notification (non-destructive).

```yaml
action: "notify"
```

**When to use**: 
- Testing rules before enabling execution
- Alert conditions you want to monitor
- Dry-run mode

**Effect**: Logs the alert; no system changes

### 2. `clear_cache`
Clear system page cache to free memory.

```yaml
action: "clear_cache"
```

**When to use**:
- High memory usage
- Cache buildup causing slowness

**Requirements**: Root privileges
**Effect**: Executes `sync; echo 1 > /proc/sys/vm/drop_caches`

### 3. `restart_<service>`
Restart a systemd service.

```yaml
action: "restart_nginx"
action: "restart_postgres"
action: "restart_docker"
action: "restart_apache2"
```

**When to use**:
- Service crashes or hangs
- High CPU from specific service
- Recovery from resource exhaustion

**Requirements**: Root privileges, valid service name
**Effect**: Executes `systemctl restart <service>`

## Rule Examples

### Example 1: Basic CPU Alert
```yaml
- name: "CPU High"
  trigger: "cpu_percent > 90"
  action: "notify"
```
Logs when CPU exceeds 90%.

### Example 2: Memory Clearance
```yaml
- name: "Emergency Memory Cleanup"
  trigger: "memory_percent > 95"
  action: "clear_cache"
```
Clears cache when memory is critically low.

### Example 3: Service Recovery
```yaml
- name: "Restart Web Server"
  trigger: "cpu_percent > 95"
  action: "restart_nginx"
```
Restarts Nginx when CPU is maxed out.

### Example 4: Multiple Conditions
```yaml
- name: "Disk and Memory Emergency"
  trigger: "disk_percent > 90 and memory_percent > 90"
  action: "notify"
```
Alerts only when both disk and memory are critical.

### Example 5: Escalating Actions
```yaml
rules:
  - name: "Memory Warning"
    trigger: "memory_percent > 85"
    action: "notify"
  
  - name: "Memory Critical - Clear Cache"
    trigger: "memory_percent > 92"
    action: "clear_cache"
  
  - name: "Memory Emergency - Restart Service"
    trigger: "memory_percent > 98"
    action: "restart_memcached"
```

## Testing Rules

### Step 1: Enable with Dry-Run
```yaml
autofix:
  enabled: true
  dry_run: true  # Safe mode
```

### Step 2: Create Test Rules
```yaml
rules:
  - name: "Test Rule"
    trigger: "cpu_percent > 0"  # Always true
    action: "notify"
```

### Step 3: Monitor Logs
```bash
tail -f sysguard.log
```

Watch for:
```
[DRY RUN] Would execute: notify
[DRY RUN] Would execute: clear_cache
```

### Step 4: Verify Conditions
Adjust the trigger to match your actual thresholds:
```yaml
trigger: "cpu_percent > 50"  # Check if this fires
```

### Step 5: Enable Execution
Once confident, change:
```yaml
dry_run: false
```

## Workflow Examples

### Development Environment
```yaml
autofix:
  enabled: true
  dry_run: true
  rules:
    - name: "All High CPU"
      trigger: "cpu_percent > 50"  # Lower threshold for testing
      action: "notify"
    - name: "All High Memory"
      trigger: "memory_percent > 60"
      action: "notify"
```

### Staging Environment
```yaml
autofix:
  enabled: true
  dry_run: true
  rules:
    - name: "High Memory"
      trigger: "memory_percent > 85"
      action: "clear_cache"
    - name: "High CPU"
      trigger: "cpu_percent > 85"
      action: "notify"
```

### Production Environment
```yaml
autofix:
  enabled: true
  dry_run: false  # ACTUAL EXECUTION
  rules:
    - name: "Memory Critical"
      trigger: "memory_percent > 95"
      action: "clear_cache"
    - name: "Service Recovery"
      trigger: "cpu_percent > 95"
      action: "restart_app"
    - name: "Disk Critical"
      trigger: "disk_percent > 95"
      action: "notify"
```

## Common Issues

### Rule Not Firing?

**Check 1**: Is autofix enabled?
```yaml
autofix:
  enabled: true  # Must be true
```

**Check 2**: Does condition match reality?
```bash
# Check actual values
python3 run.py status
```

**Check 3**: Is trigger syntax correct?
```yaml
# Good
trigger: "cpu_percent > 80"

# Bad (missing comparison operator)
trigger: "cpu_percent"
```

### Action Not Executing?

**Check 1**: Is dry_run disabled?
```yaml
dry_run: false  # Must be false for execution
```

**Check 2**: Is service name correct?
```bash
# List available services
systemctl list-units --type=service
```

**Check 3**: Do you have permissions?
```bash
# Try as root
sudo python3 run.py monitor --watch
```

### Debug Mode

Enable debug logging:
```yaml
logging:
  level: "DEBUG"
```

Then watch logs:
```bash
tail -f sysguard.log | grep -i rule
```

## Best Practices

1. **Start with `notify`**: Test trigger conditions safely
2. **Use escalation**: Multiple rules with increasing severity
3. **Conservative thresholds**: 85-95% range for production
4. **Document reasoning**: Add comments explaining rule intent
5. **Test in dry-run**: Always verify before enabling execution
6. **Monitor results**: Check logs after enabling execution
7. **Adjust gradually**: Fine-tune thresholds based on results
8. **Review periodically**: Revisit rules quarterly

## Advanced

### Rule Precedence
Rules are evaluated in order. Earlier rules execute first:

```yaml
rules:
  - name: "First"
    trigger: "cpu_percent > 80"
    action: "notify"
  
  - name: "Second"
    trigger: "cpu_percent > 90"
    action: "clear_cache"
```

### Performance
- Rule evaluation: <1ms per rule
- Action execution: Variable (cache clear ~100ms, service restart ~1s)
- Minimal system impact

### Limitations
- Conditions must be simple comparisons
- Complex logic not yet supported
- No state tracking between evaluations
