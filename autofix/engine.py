import logging
from monitor.cpu import get_cpu_metrics
from monitor.memory import get_memory_metrics
from monitor.disk import get_disk_metrics
from autofix.rules import evaluate_condition
from autofix.actions import clear_cache, restart_service

logger = logging.getLogger("sysguard.engine")

class AutoFixEngine:
    def __init__(self, config):
        self.config = config
        self.enabled = config.get("autofix", {}).get("enabled", False)
        self.dry_run = config.get("autofix", {}).get("dry_run", True)
        self.rules = config.get("autofix", {}).get("rules", [])

    def run_check(self):
        if not self.enabled:
            return []

        metrics = {
            "cpu": get_cpu_metrics(),
            "memory": get_memory_metrics(),
            "disk": get_disk_metrics()
        }
        
        flat_metrics = self._flatten_metrics(metrics)
        triggered_actions = []

        for rule in self.rules:
            if evaluate_condition(flat_metrics, rule["trigger"]):
                action_name = rule["action"]
                triggered_actions.append(f"Rule '{rule['name']}' triggered: {action_name}")
                
                if not self.dry_run:
                    self.execute_action(action_name)
                else:
                    logger.info(f"[DRY RUN] Would execute: {action_name}")

        return triggered_actions
    
    def _flatten_metrics(self, metrics):
        """Flatten nested metrics once for all rule evaluations"""
        flat = {}
        for k, v in metrics.items():
            if isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    flat[f"{k}_{sub_k}"] = sub_v
            else:
                flat[k] = v
        return flat

    def execute_action(self, action_name):
        logger.info(f"Executing action: {action_name}")
        if action_name == "clear_cache":
            clear_cache()
        elif action_name.startswith("restart_"):
            svc = action_name.replace("restart_", "")
            restart_service(svc)
