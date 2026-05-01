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
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

class LFUPolicy(CachePolicy):
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.freq = {}

    def get(self, key: str) -> Any:
        if key not in self.cache: return None
        self.freq[key] += 1
        return self.cache[key]

    def put(self, key: str, value: Any) -> None:
        if len(self.cache) >= self.capacity and key not in self.cache:
            lfu_key = min(self.freq, key=self.freq.get)
            del self.cache[lfu_key]
            del self.freq[lfu_key]
        self.cache[key] = value
        self.freq[key] = self.freq.get(key, 0) + 1

POLICIES = {
    'lru': LRUPolicy,
    'lfu': LFUPolicy
}
