from helpers.graph_util.graph import Node
from helpers.misc_util import mark_requirements
from heapq import heappush, heappop
from typing import NamedTuple, Any
import itertools as it

# ------------------------------------------------------------------

class DistPrev[V, E](NamedTuple):

    distance: float
    previous: Node[V, E] | None

    @staticmethod
    def infinite() -> DistPrev[Any, Any]:
        return DistPrev(float("inf"), None)

# ------------------------------------------------------------------

@mark_requirements("non-negative edge distances")
def shortest_dists_from_start[V, E](start: Node[V, E]) -> dict[Node[V, E], DistPrev[V, E]]:
    distances: dict[Node[V, E], DistPrev[V, E]] = {start: DistPrev(0, None)}
    visited: set[Node[V, E]] = set()
    incrementer: it.count[int] = it.count()
    frontier: list[tuple[float, int, Node[V, E]]] = [(0, next(incrementer), start)]
    infinite: DistPrev[Any, Any] = DistPrev.infinite()
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