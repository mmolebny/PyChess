import time
import inspect
from datetime import datetime, timezone
from functools import wraps

def text_formatter(record):
    return f"[{record['timestamp']}] [{record['level']}] {record['func_name']} | args={record.get('args')} | result: {record.get('result')} | time: {record.get('execution_time', 0):.4f}s"

def log(level="INFO", formatter=text_formatter):
    def decorator(func):
        def process_log(current_level, data_dict):
            if level == "ERROR" and current_level != "ERROR":
                return

            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": current_level,
                "func_name": func.__name__,
            }
