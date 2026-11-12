from helpers.graph_util.graph import Graph, Node
from helpers.misc_util import mark_requirements
from typing import Literal
from collections import defaultdict

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