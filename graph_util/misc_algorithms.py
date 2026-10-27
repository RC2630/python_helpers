from helpers.graph_util.graph import *
from helpers.misc_util import mark_requirements
from heapq import *
from typing import NamedTuple
import itertools as it

# ------------------------------------------------------------------

@mark_requirements("undirected", "connected")
def spanning_tree[V, E](graph: Graph[V, E]) -> set[tuple[Node[V, E], Node[V, E]]]:
    if len(graph.nodes) <= 1:
        return set()
    expected_tree_size: int = len(graph.nodes) - 1
    tree_edges: set[tuple[Node[V, E], Node[V, E]]] = set()
    start: Node[V, E] = graph.nodes[0]
    visited: set[Node[V, E]] = {start}
    frontier: list[Node[V, E]] = [start]
    while True:
        curr: Node[V, E] = frontier.pop()
        for dest in curr.edges:
            if dest not in visited:
                tree_edges.add((curr, dest))
                if len(tree_edges) == expected_tree_size:
                    return tree_edges
                visited.add(dest)
                frontier.append(dest)

# ------------------------------------------------------------------

class DistPrev[V, E](NamedTuple):

    distance: float
    previous: Node[V, E] | None

    @staticmethod
    def infinite() -> DistPrev[V, E]:
        return DistPrev(float("inf"), None)

# ------------------------------------------------------------------

@mark_requirements("non-negative edge distances")
def shortest_dists_from_start[V, E](start: Node[V, E]) -> dict[Node[V, E], DistPrev[V, E]]:
    distances: dict[Node[V, E], DistPrev[V, E]] = {start: DistPrev(0, None)}
    visited: set[Node[V, E]] = set()
    incrementer: it.count[int] = it.count()
    frontier: list[tuple[float, int, Node[V, E]]] = [(0, next(incrementer), start)]
    infinite: DistPrev[V, E] = DistPrev.infinite()
    while len(frontier) > 0:
        curr_dist, _, curr_node = heappop(frontier)
        if curr_node in visited:
            continue
        visited.add(curr_node)
        for neighbour, (dist, payload) in curr_node.edges.items():
            new_dist: float = curr_dist + dist
            if new_dist < distances.get(neighbour, infinite).distance:
                distances[neighbour] = DistPrev(new_dist, curr_node)
                heappush(frontier, (new_dist, next(incrementer), neighbour))
    return distances

@mark_requirements("target is a key in dist_prevs")
def reconstruct_path[V, E](
    target: Node[V, E], dist_prevs: dict[Node[V, E], DistPrev[V, E]]
) -> list[Node[V, E]]:
    path: list[Node[V, E]] = [target]
    curr: Node[V, E] = target
    while (prev := dist_prevs[curr].previous) is not None:
        path.append(prev)
        curr = prev
    return list(reversed(path))