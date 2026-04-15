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
            record.update(data_dict)
            print(formatter(record))

        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    process_log(level, {"args": args, "result": result, "execution_time": time.time() - start_time})
                    return result
                except Exception as e:
                    process_log("ERROR", {"args": args, "error": str(e)})
                    raise
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
