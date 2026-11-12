from helpers.graph_util.graph import Graph, Node, EdgeValue
from helpers.misc_util import mark_requirements
import helpers.random_util as ru
from heapq import heappush, heappop
from typing import NamedTuple, Literal, Any, Callable
from collections import defaultdict
from collections.abc import Container, Iterable
import itertools as it
from operator import lt

# ------------------------------------------------------------------

@mark_requirements("undirected")
def find_connected_components_undirected[V, E](graph: Graph[V, E]) -> list[list[Node[V, E]]]:
    remaining_nodes: set[Node[V, E]] = set(graph.nodes)
    connected_components: list[set[Node[V, E]]] = []
    while len(remaining_nodes) > 0:
        arbitrary_node: Node[V, E] = remaining_nodes.pop()
        connected_component: set[Node[V, E]] = arbitrary_node.all_reachable_nodes()
        connected_components.append(connected_component)
        remaining_nodes.difference_update(connected_component)
    return [list(component) for component in connected_components]

@mark_requirements("undirected")
def make_connected_undirected[V, E](
    graph: Graph[V, E], cost_distribution: Callable[[], float] = lambda: 1,
    default_payload: E = None
) -> None:
    connected_components: list[list[Node[V, E]]] = find_connected_components_undirected(graph)
    while len(connected_components) > 1:
        cc1, cc2 = ru.fast_rejection_sample(
            connected_components,
            count = 2,
            remove = True,
            mode = "distinct_indices"
        )
        random_node_1: Node[V, E] = ru.random_element(cc1)
        random_node_2: Node[V, E] = ru.random_element(cc2)
        random_node_1.create_edge(
            random_node_2, cost_distribution(),
            undirected = True, payload = default_payload
        )
        if len(cc1) < len(cc2):
            cc1, cc2 = cc2, cc1
        cc1.extend(cc2)
        connected_components.append(cc1)

# ------------------------------------------------------------------

@mark_requirements("directed")
def strongly_connected_component[V, E](
    node: Node[V, E], ignore: Container[Node[V, E]] = ()
) -> set[Node[V, E]]:
    if node in ignore:
        return set()
    outgoing_component: set[Node[V, E]] = node.all_reachable_nodes(ignore)
    incoming_neighbours: dict[Node[V, E], list[Node[V, E]]] = defaultdict(list)
    for node in outgoing_component:
        for dest in node.edges:
            if dest not in ignore:
                incoming_neighbours[dest].append(node)
    incoming_component: set[Node[V, E]] = {node}
    to_iterate_over: list[Node[V, E]] = [node]
    while True:
        next_to_iterate_over: list[Node[V, E]] = []
        for node in to_iterate_over:
            to_add: list[Node[V, E]] = [
                neighbour for neighbour in incoming_neighbours[node]
                if neighbour not in incoming_component
            ]
            next_to_iterate_over.extend(to_add)
            incoming_component.update(to_add)
        if len(next_to_iterate_over) == 0:
            break
        to_iterate_over = next_to_iterate_over
    return incoming_component

@mark_requirements("directed")
def find_strongly_connected_components[V, E](graph: Graph[V, E]) -> list[list[Node[V, E]]]:
    raise NotImplementedError

# ------------------------------------------------------------------

@mark_requirements("directed")
def make_connected_directed[V, E](
    graph: Graph[V, E], cost_distribution: Callable[[], float] = lambda: 1,
    default_payload: E = None, require_strong: bool = True
) -> None:
    
    if len(graph.nodes) == 0:
        return
    still_unconnected: list[list[Node[V, E]]] = find_strongly_connected_components(graph)
    connected_so_far: list[list[Node[V, E]]] = [
        ru.random_element(still_unconnected, remove = True)
    ]

    def make_directed_edge_if_not_present(node_1: Node[V, E], node_2: Node[V, E]) -> None:
        if node_2 not in node_1.edges:
            node_1.create_edge(
                node_2, cost_distribution(),
                undirected = False, payload = default_payload
            )

    while len(still_unconnected) > 0:
        unconnected_component: list[Node[V, E]] = (
            ru.random_element(still_unconnected, remove = True)
        )
        connected_component: list[Node[V, E]] = ru.random_element(connected_so_far)
        make_directed_edge_if_not_present(
            ru.random_element(connected_component),
            ru.random_element(unconnected_component)
        )
        if require_strong:
            make_directed_edge_if_not_present(
                ru.random_element(unconnected_component),
                ru.random_element(connected_component)
            )
        connected_so_far.append(unconnected_component)

# ------------------------------------------------------------------

@mark_requirements("undirected", "connected", "root is in the graph")
def spanning_tree[V, E](
    graph: Graph[V, E], root: Node[V, E] | None = None
) -> set[tuple[Node[V, E], Node[V, E]]]:
    if len(graph.nodes) <= 1:
        return set()
    expected_tree_size: int = len(graph.nodes) - 1
    tree_edges: set[tuple[Node[V, E], Node[V, E]]] = set()
    start: Node[V, E] = graph.nodes[0] if root is None else root
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

# ------------------------------------------------------------------

class DisjointSets:

    def __init__(self, num_items: int) -> None:
        self.data: list[int] = num_items * [-1]

    def find(self, i: int) -> int:
        data: list[int] = self.data
        cursor: int = i
        while (cursor := data[cursor]) >= 0:
            parent: int = cursor
            if (cursor := data[parent]) < 0:
                return parent
            data[i] = cursor
            i = cursor
        return i

    def union(self, i: int, j: int) -> bool:
        data: list[int] = self.data
        root_i: int = self.find(i)
        root_j: int = self.find(j)
        if root_i == root_j:
            return False
        neg_size_i: int = data[root_i]
        neg_size_j: int = data[root_j]
        if neg_size_i <= neg_size_j: # size(i) >= size(j)
            data[root_i] += neg_size_j
            data[root_j] = root_i
        else: # size(i) < size(j)
            data[root_j] += neg_size_i
            data[root_i] = root_j
        return True

# ------------------------------------------------------------------

def get_sorted_edges[V, E](
    graph: Graph[V, E],
    optimum_type: Literal["minimum", "maximum"] = "minimum",
    undirected: bool = True
) -> list[tuple[Node[V, E], Node[V, E]]]:
    edges: dict[tuple[Node[V, E], Node[V, E]], float] = {}
    seen: set[Node[V, E]] = set()
    for node in graph.nodes:
        for dest, (cost, payload) in node.edges.items():
            if dest not in seen:
                edges[(node, dest)] = cost
        if undirected:
            seen.add(node)
    return sorted(
        edges,
        key = lambda edge: edges[edge],
        reverse = (optimum_type == "maximum")
    )

@mark_requirements("undirected", "connected", "root is in the graph")
def optimal_spanning_tree[V, E](
    graph: Graph[V, E],
    optimum_type: Literal["minimum", "maximum"] = "minimum",
    perform_orientation_repair: bool = True,
    root: Node[V, E] | None = None
) -> set[tuple[Node[V, E], Node[V, E]]]:
    if len(graph.nodes) <= 1:
        return set()
    expected_tree_size: int = len(graph.nodes) - 1
    tree_edges: set[tuple[Node[V, E], Node[V, E]]] = set()
    disjoint_sets = DisjointSets(len(graph.nodes))
    node_to_index: dict[Node[V, E], int] = {node: i for i, node in enumerate(graph.nodes)}
    for node_1, node_2 in get_sorted_edges(graph, optimum_type):
        if disjoint_sets.union(node_to_index[node_1], node_to_index[node_2]):
            tree_edges.add((node_1, node_2))
            if len(tree_edges) == expected_tree_size:
                if perform_orientation_repair:
                    tree_edges = spanning_tree_orientation_repair(
                        tree_edges,
                        tree_root = graph.nodes[0] if root is None else root
                    )[0]
                return tree_edges
    raise ValueError("the input graph does not have a valid spanning tree")

# ------------------------------------------------------------------

@mark_requirements("tree_root is contained in at least 1 edge in undirected_edges")
def spanning_tree_orientation_repair[V, E](
    undirected_edges: set[tuple[Node[V, E], Node[V, E]]], tree_root: Node[V, E] | None = None
) -> tuple[set[tuple[Node[V, E], Node[V, E]]], Node[V, E] | None]:
    if len(undirected_edges) == 0:
        return (set(), tree_root)
    root: Node[V, E] = tree_root if tree_root is not None else next(iter(undirected_edges))[0]
    eligible: set[Node[V, E]] = {root}
    tree_edges: set[tuple[Node[V, E], Node[V, E]]] = set()
    node_to_edges: dict[Node[V, E], set[tuple[Node[V, E], Node[V, E]]]] = defaultdict(set)
    for node_1, node_2 in undirected_edges:
        node_to_edges[node_1].add((node_1, node_2))
        node_to_edges[node_2].add((node_1, node_2))
    while len(tree_edges) < len(undirected_edges):
        arbitrary_eligible_node: Node[V, E] = eligible.pop()
        edges: set[tuple[Node[V, E], Node[V, E]]] = node_to_edges[arbitrary_eligible_node].copy()
        no_longer_eligible: set[Node[V, E]] = set()
        for node_1, node_2 in edges:
            node_to_edges[node_1].remove((node_1, node_2))
            node_to_edges[node_2].remove((node_1, node_2))
            if len(node_to_edges[node_1]) == 0:
                no_longer_eligible.add(node_1)
            if len(node_to_edges[node_2]) == 0:
                no_longer_eligible.add(node_2)
            if node_1 is arbitrary_eligible_node:
                tree_edges.add((node_1, node_2))
                if len(node_to_edges[node_2]) > 0:
                    eligible.add(node_2)
            else:
                tree_edges.add((node_2, node_1))
                if len(node_to_edges[node_1]) > 0:
                    eligible.add(node_1)
        for node_to_remove in no_longer_eligible:
            eligible.discard(node_to_remove)
    return (tree_edges, root)

# ------------------------------------------------------------------

@mark_requirements("directed", "acyclic", "applies to only selected edges")
def topological_sort[V, E](
    graph: Graph[V, E],
    use_edge: Callable[[EdgeValue[E], Node[V, E], Node[V, E]], bool] = (
        lambda edge, from_node, to_node: True
    )
) -> list[Node[V, E]]:
    in_degrees: dict[Node[V, E], int] = defaultdict(int)
    for node in graph.nodes:
        for dest, edge in node.edges.items():
            if use_edge(edge, node, dest):
                in_degrees[dest] += 1
    frontier: list[Node[V, E]] = [node for node in graph.nodes if in_degrees[node] == 0]
    sorted_nodes: list[Node[V, E]] = []
    while len(frontier) > 0:
        curr: Node[V, E] = frontier.pop()
        sorted_nodes.append(curr)
        for dest, edge in curr.edges.items():
            if use_edge(edge, curr, dest):
                in_degrees[dest] -= 1
                if in_degrees[dest] == 0:
                    frontier.append(dest)
    if len(sorted_nodes) < len(graph.nodes):
        raise ValueError("selected edges contain at least 1 cycle")
    return sorted_nodes

@mark_requirements("directed", "acyclic", "applies to only selected edges")
def topologically_reorder_nodes[V, E](
    graph: Graph[V, E],
    use_edge: Callable[[EdgeValue[E], Node[V, E], Node[V, E]], bool] = (
        lambda edge, from_node, to_node: True
    )
) -> None:
    graph.nodes = topological_sort(graph, use_edge)

@mark_requirements("acyclic precedence relation")
def topological_sort_elements[T](
    elements: Iterable[T], must_appear_before: Callable[[T, T], bool] = lt
) -> list[T]:
    graph: Graph[T, None] = Graph(
        Node[T, None](payload = element) for element in elements
    )
    for node_1, node_2 in it.combinations(graph.nodes, 2):
        one_before_two: bool = must_appear_before(node_1.payload, node_2.payload)
        two_before_one: bool = must_appear_before(node_2.payload, node_1.payload)
        if one_before_two and two_before_one:
            raise ValueError(
                f"invalid precedence relation: must_appear_before returned True "
                f"for {node_1.payload} and {node_2.payload} in both directions"
            )
        elif one_before_two:
            node_1.create_edge(node_2, undirected = False)
        elif two_before_one:
            node_2.create_edge(node_1, undirected = False)
    return [node.payload for node in topological_sort(graph)]