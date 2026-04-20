import heapq
from collections import deque
from typing import Any

class BiPriorityQueue:
    def __init__(self):
        self.counter = 0
        self.min_heap = []
        self.max_heap = []
        self.order_queue = deque()

    def enqueue(self, item: Any, priority: float) -> None:
        node = [item, priority, self.counter, False]
        self.order_queue.append(node)
        heapq.heappush(self.min_heap, (priority, self.counter, node))
        heapq.heappush(self.max_heap, (-priority, self.counter, node))
        self.counter += 1

    def _clean_deleted_oldest(self):
