from helpers.graph_util.graph import Graph, Node
from helpers.misc_util import mark_requirements
import helpers.random_util as ru
from typing import Callable
from collections import defaultdict
from collections.abc import Container

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
def get_incoming_neighbours[V, E](
    node: Node[V, E], ignore: Container[Node[V, E]] = ()
) -> dict[Node[V, E], list[Node[V, E]]]:
    outgoing_component: set[Node[V, E]] = node.all_reachable_nodes(ignore)
    incoming_neighbours: dict[Node[V, E], list[Node[V, E]]] = defaultdict(list)
    for curr in outgoing_component:
        for dest in curr.edges:
            if dest not in ignore:
                incoming_neighbours[dest].append(curr)
    return incoming_neighbours

@mark_requirements("directed")
def strongly_connected_component[V, E](
    node: Node[V, E], ignore: Container[Node[V, E]] = ()
) -> set[Node[V, E]]:
    if node in ignore:
        return set()
    incoming_neighbours: dict[Node[V, E], list[Node[V, E]]] = get_incoming_neighbours(node, ignore)
    incoming_component: set[Node[V, E]] = {node}
    to_iterate_over: list[Node[V, E]] = [node]
    while True:
        next_to_iterate_over: list[Node[V, E]] = []
        for curr in to_iterate_over:
            to_add: list[Node[V, E]] = [
                neighbour for neighbour in incoming_neighbours[curr]
                if neighbour not in incoming_component
            ]
            next_to_iterate_over.extend(to_add)
            incoming_component.update(to_add)
        if len(next_to_iterate_over) == 0:
            break
        to_iterate_over = next_to_iterate_over
    return incoming_component

# ------------------------------------------------------------------

def dfs_finishing_order[V, E](start_node: Node[V, E]) -> list[Node[V, E]]:
    call_stack: list[Node[V, E]] = [start_node]
    visited: set[Node[V, E]] = set()
    finishing_order: list[Node[V, E]] = []
    node_to_unprocessed_neighbours: dict[Node[V, E], list[Node[V, E]]] = {}
    while len(call_stack) > 0:
        curr: Node[V, E] = call_stack[-1]
        if curr not in visited:
            visited.add(curr)
            node_to_unprocessed_neighbours[curr] = list(curr.edges)
        if len(node_to_unprocessed_neighbours[curr]) == 0:
            finishing_order.append(curr)
            call_stack.pop()
        else:
            neighbour: Node[V, E] = node_to_unprocessed_neighbours[curr].pop()
            if neighbour not in visited:
                call_stack.append(neighbour)
    return finishing_order

# ------------------------------------------------------------------

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