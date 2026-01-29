import logging
from typing import Dict, Any

logger = logging.getLogger("sysguard.rules")

def evaluate_condition(metrics: Dict[str, Any], condition: str) -> bool:
    """
    Evaluates a simple string condition against metrics.
    Example: "cpu_percent > 80" with metrics={"cpu_percent": 90} -> True
    """
    # This is a basic evaluator. For production, a safer parser is better.
    # We will support basic comparisons: >, <, >=, <=, ==
    
    try:
        # 1. Parse keys from metrics
        # For simplicity, we assume the condition uses keys present in the flattened metrics
        
        # Flatten metrics for easier access
        flat_metrics = {}
        for k, v in metrics.items():
            if isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    flat_metrics[f"{k}_{sub_k}"] = sub_v
            else:
                flat_metrics[k] = v
        
        # 2. Check which key is in the condition
        target_key = None
        for key in flat_metrics.keys():
            if key in condition:
                target_key = key
                break
        
        if not target_key:
            return False

        # 3. Safe evaluation
        # Replace the key with its value and evaluate
        value = flat_metrics[target_key]
        eval_string = condition.replace(target_key, str(value))
        
        return eval(eval_string, {"__builtins__": None}, {})
        
    except Exception as e:
        logger.error(f"Error evaluating rule '{condition}': {e}")
        return False
