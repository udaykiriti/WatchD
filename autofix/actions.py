import os
import subprocess
import logging

logger = logging.getLogger("sysguard.autofix")

def kill_process(pid: int) -> bool:
    """Kills a process by PID."""
    try:
        os.kill(pid, 9) # SIGKILL
        logger.info(f"Killed process {pid}")
        return True
    except PermissionError:
        logger.error(f"Permission denied killing process {pid}")
        return False
    except ProcessLookupError:
        logger.warning(f"Process {pid} not found")
        return False
    except Exception as e:
        logger.error(f"Error killing process {pid}: {e}")
        return False

def restart_service(service_name: str) -> bool:
    """Restarts a systemd service."""
    cmd = ["systemctl", "restart", service_name]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info(f"Restarted service {service_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to restart service {service_name}: {e}")
        return False
    except FileNotFoundError:
        logger.error("systemctl not found")
        return False

def clear_cache() -> bool:
    """Clears page cache (requires root)."""
    # sync; echo 1 > /proc/sys/vm/drop_caches
    try:
        subprocess.run(["sync"], check=True)
        with open("/proc/sys/vm/drop_caches", "w") as f:
            f.write("1")
        logger.info("Cleared system cache")
        return True
    except PermissionError:
        logger.error("Permission denied clearing cache (root required)")
        return False
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return False
