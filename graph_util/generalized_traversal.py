from helpers.graph_util.graph import *
from typing import Any, NamedTuple
from collections import deque
from collections.abc import Iterator
from helpers.random_util import random_element
import heapq

# ----------------------------------------------------------

class FrontierSpec[T, DS](NamedTuple):

    init: Callable[[], DS]
    insert: Callable[[DS, tuple[T, Node[Any, Any]]], None]
    remove: Callable[[DS], tuple[T, Node[Any, Any]]]
    has_items: Callable[[DS], bool] = bool

    def deduplicated(
        self, never_forget: bool = True, track_node_only: bool = False
    ) -> FrontierSpec[T, DeduplicatedFrontier[T, DS]]:
        return FrontierSpec[T, DeduplicatedFrontier[T, DS]](
            init = lambda: DeduplicatedFrontier[T, DS](self, never_forget, track_node_only),
            insert = DeduplicatedFrontier[T, DS].insert,
            remove = DeduplicatedFrontier[T, DS].remove,
            has_items = DeduplicatedFrontier[T, DS].has_items
        )

# ----------------------------------------------------------

class DeduplicatedFrontier[T, DS]:

    def __init__(
        self, frontier_spec: FrontierSpec[T, DS],
        never_forget: bool, track_node_only: bool
    ) -> None:
        self.frontier_spec: FrontierSpec[T, DS] = frontier_spec
        self.never_forget: bool = never_forget
        self.track_node_only: bool = track_node_only
        self.seen: set[tuple[T, Node[Any, Any]]] | set[Node[Any, Any]] = set()
        self.frontier: DS = frontier_spec.init()

    def item_to_tracked(self, item: tuple[T, Node[Any, Any]]) -> Any:
        return item[1] if self.track_node_only else item

    def insert(self, item: tuple[T, Node[Any, Any]]) -> None:
        tracked: Any = self.item_to_tracked(item)
        if tracked not in self.seen:
            self.frontier_spec.insert(self.frontier, item)
            self.seen.add(tracked)

    def remove(self) -> tuple[T, Node[Any, Any]]:
        item: tuple[T, Node[Any, Any]] = self.frontier_spec.remove(self.frontier)
        if not self.never_forget:
            self.seen.remove(self.item_to_tracked(item))
        return item

    def has_items(self) -> bool:
        return self.frontier_spec.has_items(self.frontier)

# ----------------------------------------------------------

STACK_FRONTIER = FrontierSpec[Any, list[Any]](
    init = list,
    insert = list.append,
    remove = list.pop
)

QUEUE_FRONTIER = FrontierSpec[Any, deque[Any]](
    init = deque,
    insert = deque.append,
    remove = deque.popleft
)

MIN_HEAP_FRONTIER = FrontierSpec[Any, list[Any]](
    init = list,
    insert = heapq.heappush,
    remove = heapq.heappop
)

MAX_HEAP_FRONTIER = FrontierSpec[Any, list[Any]](
    init = list,
    insert = heapq.heappush_max,
    remove = heapq.heappop_max
)

SET_FRONTIER = FrontierSpec[Any, set[Any]](
    init = set,
    insert = set.add,
    remove = set.pop
)

DICT_FRONTIER = FrontierSpec[Any, dict[Any, None]](
    init = dict,
    insert = lambda d, item: d.__setitem__(item, None),
    remove = lambda d: d.popitem()[0]
)

RANDOM_FRONTIER = FrontierSpec[Any, list[Any]](
    init = list,
    insert = list.append,
    remove = lambda l: random_element(l, remove = True)
)

# ----------------------------------------------------------

NO_VISITED_SET = sentinel("NO_VISITED_SET") # using python 3.15+ built-in sentinel

def generalized_traversal_iterator[T, V, E, DS, I, K](
    start_node: Node[V, E],
    start_node_element: T = None,
    node_yield_func: Callable[[T, Node[V, E]], I] = lambda element, node: (node, element),
    neighbour_element: Callable[[T, Node[V, E], Node[V, E]], T] = (
        lambda element, curr, neighbour: element
    ),
    visited_key: Callable[[T, Node[V, E]], K] | NO_VISITED_SET = lambda element, node: node,
    frontier_spec: FrontierSpec[T, DS] = STACK_FRONTIER
) -> Iterator[I]:
    frontier: DS = frontier_spec.init()
    frontier_spec.insert(frontier, (start_node_element, start_node))
    visited: set[K] = set()
    while frontier_spec.has_items(frontier):
        curr_element, curr_node = frontier_spec.remove(frontier)
        if visited_key is not NO_VISITED_SET:
            curr_key: K = visited_key(curr_element, curr_node)
            if curr_key in visited:
                continue
            visited.add(curr_key)
        yield node_yield_func(curr_element, curr_node)
        for neighbour in curr_node.edges:
            frontier_spec.insert(
                frontier,
                (neighbour_element(curr_element, curr_node, neighbour), neighbour)
            )

# ----------------------------------------------------------

'''
the functions below are older and simpler versions of generalized traversal,
which are generally less generalized than the canonical iterator version above.
however, they are all kept here for backward compatibility.
although not formally deprecated, users are recommended to use generalized_traversal_iterator().
'''

def generalized_traversal[T, V, E, DS](
    start_node: Node[V, E],
    start_node_element: T = None,
    on_visit_func: Callable[[T, Node[V, E]], Any] = lambda element, node: None,
    neighbour_element: Callable[[T, Node[V, E], Node[V, E]], T] = (
        lambda element, curr, neighbour: element
    ),
    frontier_spec: FrontierSpec[T, DS] = STACK_FRONTIER
) -> None:
    for _ in generalized_traversal_iterator(
        start_node, start_node_element, on_visit_func, neighbour_element,
        frontier_spec = frontier_spec
    ):
        pass

def generalized_dfs_with_custom_element[T, V, E](
    start_node: Node[V, E],
    start_node_element: T = None,
    on_visit_func: Callable[[T, Node[V, E]], Any] = lambda element, node: None,
    neighbour_element: Callable[[T, Node[V, E], Node[V, E]], T] = (
        lambda element, curr, neighbour: element
    )
) -> None:
    generalized_traversal(
        start_node, start_node_element, on_visit_func, neighbour_element, STACK_FRONTIER
    )

def generalized_dfs[V, E](
    start_node: Node[V, E],
    node_func: Callable[[Node[V, E]], Any] = lambda node: None
) -> None:
    generalized_dfs_with_custom_element(
        start_node,
        on_visit_func = lambda nothing, node: node_func(node)
    )

def generalized_dfs_with_path[V, E](
    start_node: Node[V, E],
    path_func: Callable[[list[Node[V, E]]], Any] = lambda path: None
) -> None:
    generalized_dfs_with_custom_element(
        start_node,
        start_node_element = [start_node],
        on_visit_func = lambda path, node: path_func(path),
        neighbour_element = lambda path, curr, neighbour: path + [neighbour]
    )