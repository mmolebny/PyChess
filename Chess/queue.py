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
        while self.order_queue and self.order_queue[0][3]:
            self.order_queue.popleft()

    def _clean_deleted_newest(self):
        while self.order_queue and self.order_queue[-1][3]:
            self.order_queue.pop()

    def _clean_deleted_min(self):
        while self.min_heap and self.min_heap[0][2][3]:
            heapq.heappop(self.min_heap)

    def _clean_deleted_max(self):
        while self.max_heap and self.max_heap[0][2][3]:
            heapq.heappop(self.max_heap)

    def dequeue_oldest(self) -> Any:
        self._clean_deleted_oldest()
        if not self.order_queue: return None
        node = self.order_queue.popleft()
        node[3] = True
        return node[0]

    def dequeue_newest(self) -> Any:
        self._clean_deleted_newest()
        if not self.order_queue: return None
        node = self.order_queue.pop()
        node[3] = True
        return node[0]

    def dequeue_highest(self) -> Any:
        self._clean_deleted_max()
        if not self.max_heap: return None
        _, _, node = heapq.heappop(self.max_heap)
        node[3] = True
        return node[0]

    def dequeue_lowest(self) -> Any:
        self._clean_deleted_min()
        if not self.min_heap: return None
        _, _, node = heapq.heappop(self.min_heap)
        node[3] = True
        return node[0]
        
    def is_empty(self) -> bool:
        self._clean_deleted_oldest()
        return len(self.order_queue) == 0