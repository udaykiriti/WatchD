import logging
import operator
import re
from typing import Dict, Any

logger = logging.getLogger("sysguard.rules")

# Safe operators
OPERATORS = {
    '>=': operator.ge,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne,
    '>': operator.gt,
    '<': operator.lt,
}

def evaluate_condition(metrics: Dict[str, Any], condition: str) -> bool:
    """
    Evaluates a simple string condition against metrics safely.
    Example: "cpu_percent > 80" with metrics={"cpu_percent": 90} -> True
    
    Supported operators: >, <, >=, <=, ==, !=
    """
    try:
        # Flatten metrics for easier access
        flat_metrics = {}
        for k, v in metrics.items():
            if isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    flat_metrics[f"{k}_{sub_k}"] = sub_v
            else:
                flat_metrics[k] = v
        
        # Parse condition using regex to handle multi-char operators
        # Match: key operator value
        pattern = r'(\w+)\s*(>=|<=|==|!=|>|<)\s*([+-]?\d+\.?\d*)'
        match = re.match(pattern, condition.strip())
        
        if not match:
            logger.error(f"Invalid condition format: {condition}")
            return False
        
        key, op_str, value_str = match.groups()
        
        # Get metric value
        if key not in flat_metrics:
            logger.warning(f"Metric '{key}' not found in metrics")
            return False
        
        metric_value = flat_metrics[key]
        
        # Parse comparison value
        try:
            compare_value = float(value_str)
        except ValueError:
            logger.error(f"Invalid comparison value: {value_str}")
            return False
        
        # Perform safe comparison
        op_func = OPERATORS[op_str]
        return op_func(metric_value, compare_value)
        
    except Exception as e:
        logger.error(f"Error evaluating rule '{condition}': {e}")
        return False

