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

def evaluate_condition(flat_metrics: Dict[str, Any], condition: str) -> bool:
    """
    Evaluates a condition against pre-flattened metrics dict.
    Example: "cpu_usage_percent > 80" with flat_metrics={"cpu_usage_percent": 90} -> True
    
    Supported operators: >, <, >=, <=, ==, !=
    Note: Expects flat_metrics already processed by AutoFixEngine._flatten_metrics()
    """
    try:
        pattern = r'(\w+)\s*(>=|<=|==|!=|>|<)\s*([+-]?\d+\.?\d*)'
        match = re.match(pattern, condition.strip())
        
        if not match:
            logger.error(f"Invalid condition format: {condition}")
            return False
        
        key, op_str, value_str = match.groups()
        
        if key not in flat_metrics:
            logger.warning(f"Metric '{key}' not found in metrics")
            return False
        
        metric_value = flat_metrics[key]
        
        try:
            compare_value = float(value_str)
        except ValueError:
            logger.error(f"Invalid comparison value: {value_str}")
            return False
        
        op_func = OPERATORS[op_str]
        return op_func(metric_value, compare_value)
        
    except Exception as e:
        logger.error(f"Error evaluating rule '{condition}': {e}")
        return False
