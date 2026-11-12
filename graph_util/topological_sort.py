from helpers.graph_util.graph import Graph, Node, EdgeValue
from helpers.misc_util import mark_requirements
from typing import Callable
from collections import defaultdict
from collections.abc import Iterable
import itertools as it
from operator import lt

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