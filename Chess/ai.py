import random
from Chess.memo import memoize
from Chess.queue import BiPriorityQueue

WEIGHTS = {"K": 0, "Q": 900, "R": 500, "B": 330, "N": 320, "p": 100}
INFINITY = 999999
SEARCH_DEPTH = 3

def get_random(actions: list) -> object:
    return random.choice(actions)

def _sort_moves_with_queue(actions: list) -> list:
    pq = BiPriorityQueue()
    for action in actions:
        if action.captured != '--':
            priority = WEIGHTS.get(action.captured[1], 0)
        else:
            priority = 0 
        pq.enqueue(action, priority)
    
    sorted_actions = []
    while not pq.is_empty():
        best_action = pq.dequeue_highest()
        sorted_actions.append(best_action)
        
    return sorted_actions

def compute_best_action(state, actions: list, queue) -> None:
    global optimal_action
    optimal_action = random.choice(actions)
    sorted_actions = _sort_moves_with_queue(actions)
    multiplier = 1 if state.active_color == 'w' else -1
    _ab_pruning(state, sorted_actions, SEARCH_DEPTH, -INFINITY, INFINITY, multiplier)
    queue.put(optimal_action)

def _ab_pruning(state, actions, depth, alpha, beta, color_sign) -> int:
    global optimal_action
    if depth == 0:
