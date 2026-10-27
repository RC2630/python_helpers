from helpers.graph_util.graph import *
from typing import Any, NamedTuple
from collections import deque
from collections.abc import Collection
import heapq

# ----------------------------------------------------------

def generalized_dfs[V, E](graph: Graph[V, E], node_func: Callable[[Node[V, E]], Any]) -> None:
    if len(graph.nodes) == 0:
        return
    frontier: list[Node[V, E]] = [graph.nodes[0]]
    visited: set[Node[V, E]] = set()
    while len(frontier) > 0:
        curr: Node[V, E] = frontier.pop()
        if curr in visited:
            continue
        visited.add(curr)
        node_func(curr)
        for neighbour in curr.edges:
            frontier.append(neighbour)

def generalized_dfs_with_path[V, E](
    graph: Graph[V, E], path_func: Callable[[list[Node[V, E]]], Any]
) -> None:
    if len(graph.nodes) == 0:
        return
    frontier: list[list[Node[V, E]]] = [[graph.nodes[0]]]
    visited: set[Node[V, E]] = set()
    while len(frontier) > 0:
        curr_path: list[Node[V, E]] = frontier.pop()
        curr_node: Node[V, E] = curr_path[-1]
        if curr_node in visited:
            continue
        visited.add(curr_node)
        path_func(curr_path)
        for neighbour in curr_node.edges:
            frontier.append(curr_path + [neighbour])

def generalized_dfs_with_custom_element[T, V, E](
    graph: Graph[V, E],
    start_node_element: Callable[[Node[V, E]], T],
    on_visit_func: Callable[[T, Node[V, E]], Any],
    neighbour_element: Callable[[T, Node[V, E], Node[V, E]], T]
) -> None:
    if len(graph.nodes) == 0:
        return
    frontier: list[tuple[T, Node[V, E]]] = [(start_node_element(graph.nodes[0]), graph.nodes[0])]
    visited: set[Node[V, E]] = set()
    while len(frontier) > 0:
        curr_element, curr_node = frontier.pop()
        if curr_node in visited:
            continue
        visited.add(curr_node)
        on_visit_func(curr_element, curr_node)
        for neighbour in curr_node.edges:
            frontier.append((
                neighbour_element(curr_element, curr_node, neighbour),
                neighbour
            ))

# ----------------------------------------------------------

type FrontierSpecType[T] = FrontierSpec[T, Collection[tuple[T, Node[Any, Any]]]]

class FrontierSpec[T, DS](NamedTuple):
    init: Callable[[], DS]
    insert: Callable[[DS, tuple[T, Node[Any, Any]]], None]
    remove: Callable[[DS], tuple[T, Node[Any, Any]]]

STACK_FRONTIER: FrontierSpecType[Any] = FrontierSpec(
    init = list,
    insert = list.append,
    remove = list.pop
)

QUEUE_FRONTIER: FrontierSpecType[Any] = FrontierSpec(
    init = deque,
    insert = deque.append,
    remove = deque.popleft
)

MIN_HEAP_FRONTIER: FrontierSpecType[Any] = FrontierSpec(
    init = list,
    insert = heapq.heappush,
    remove = heapq.heappop
)

# ----------------------------------------------------------

def generalized_traversal[T, V, E](
    graph: Graph[V, E],
    frontier_spec: FrontierSpecType[T],
    start_node_element: Callable[[Node[V, E]], T],
    on_visit_func: Callable[[T, Node[V, E]], Any],
    neighbour_element: Callable[[T, Node[V, E], Node[V, E]], T]
) -> None:
    if len(graph.nodes) == 0:
        return
    frontier: Collection[tuple[T, Node[V, E]]] = frontier_spec.init()
    frontier_spec.insert(frontier, (start_node_element(graph.nodes[0]), graph.nodes[0]))
    visited: set[Node[V, E]] = set()
    while len(frontier) > 0:
        curr_element, curr_node = frontier_spec.remove(frontier)
        if curr_node in visited:
            continue
        visited.add(curr_node)
        on_visit_func(curr_element, curr_node)
        for neighbour in curr_node.edges:
            frontier_spec.insert(
                frontier,
                (neighbour_element(curr_element, curr_node, neighbour), neighbour)
            )