import functools
from collections import OrderedDict
from typing import Callable, Any

class CachePolicy:
    def get(self, key: str) -> Any: pass
    def put(self, key: str, value: Any) -> None: pass

class LRUPolicy(CachePolicy):
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: str) -> Any:
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: str, value: Any) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
