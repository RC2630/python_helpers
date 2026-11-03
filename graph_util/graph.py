from typing import Callable, NamedTuple, Any
from collections import defaultdict
from collections.abc import Iterable
import helpers.random_util as ru

NONE: Any = None

# -------------------------------------------

class EdgeValue[E](NamedTuple):

    cost: float
    payload: E

    def update_cost(self, new_cost: float) -> EdgeValue[E]:
        return EdgeValue(new_cost, self.payload)

    def update_payload(self, new_payload: E) -> EdgeValue[E]:
        return EdgeValue(self.cost, new_payload)

# -------------------------------------------

class Node[V, E]:

    def __init__(self, name: str | None = None, payload: V = NONE) -> None:
        self.name: str = name if name is not None else f"node_{id(self)}"
        self.payload: V = payload
        self.edges: dict[Node[V, E], EdgeValue[E]] = {}

    def create_edge(
        self, dest: Node[V, E], cost: float = 1, undirected: bool = True,
        payload: E = NONE, reversed_payload: E = NONE, symmetric_payload: bool = False
    ) -> None:
        self.edges[dest] = EdgeValue(cost, payload)
        if undirected:
            dest.edges[self] = (
                EdgeValue(cost, payload) if symmetric_payload
                else EdgeValue(cost, reversed_payload)
            )

    def __repr__(self) -> str:
        if len(self.edges) == 0:
            return f"{self.name} -> (no edges)"
        return self.name + " -> " + ", ".join(
            f"{dest.name}: {cost}" for dest, (cost, payload) in self.edges.items()
        )

    def all_connected_nodes(self) -> set[Node[V, E]]:
        result: set[Node[V, E]] = {self}
        frontier: list[Node[V, E]] = [self]
        while len(frontier) > 0:
            curr: Node[V, E] = frontier.pop()
            for neighbour in curr.edges:
                if neighbour not in result:
                    result.add(neighbour)
                    frontier.append(neighbour)
        return result

    def strongly_connected_component(self) -> set[Node[V, E]]:
        outgoing_component: set[Node[V, E]] = self.all_connected_nodes()
        incoming_neighbours: dict[Node[V, E], list[Node[V, E]]] = defaultdict(list)
        for node in outgoing_component:
            for dest in node.edges:
                incoming_neighbours[dest].append(node)
        incoming_component: set[Node[V, E]] = {self}.union(incoming_neighbours[self])
        to_iterate_over: list[Node[V, E]] = incoming_neighbours[self]
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

# -------------------------------------------

class Graph[V, E]:

    def __init__(self, nodes_or_node: Iterable[Node[V, E]] | Node[V, E] = ()) -> None:
        if isinstance(nodes_or_node, Node):
            self.nodes: list[Node[V, E]] = list(nodes_or_node.all_connected_nodes())
        else:
            self.nodes = list(nodes_or_node)

    def __repr__(self) -> str:
        if len(self.nodes) == 0:
            return "(empty graph)"
        return "\n".join(str(node) for node in self.nodes)

    def find_connected_components(
        self, cc_func: Callable[[Node[V, E]], set[Node[V, E]]]
    ) -> list[list[Node[V, E]]]:
        remaining_nodes: set[Node[V, E]] = set(self.nodes)
        connected_components: list[set[Node[V, E]]] = []
        while len(remaining_nodes) > 0:
            arbitrary_node: Node[V, E] = remaining_nodes.pop()
            connected_component: set[Node[V, E]] = cc_func(arbitrary_node)
            connected_components.append(connected_component)
            remaining_nodes.difference_update(connected_component)
        return [list(component) for component in connected_components]

    def find_connected_components_undirected(self) -> list[list[Node[V, E]]]:
        return self.find_connected_components(Node.all_connected_nodes)

    def make_connected_undirected(
        self, cost_distribution: Callable[[], float] = lambda: 1,
        default_payload: E = NONE
    ) -> None:
        connected_components: list[list[Node[V, E]]] = self.find_connected_components_undirected()
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
                random_node_2, cost_distribution(), undirected = True,
                payload = default_payload, reversed_payload = default_payload
            )
            if len(cc1) < len(cc2):
                cc1, cc2 = cc2, cc1
            cc1.extend(cc2)
            connected_components.append(cc1)

    def find_connected_components_directed(self) -> list[list[Node[V, E]]]:
        return self.find_connected_components(Node.strongly_connected_component)

    def make_connected_directed(
        self, cost_distribution: Callable[[], float] = lambda: 1,
        default_payload: E = NONE, require_strong: bool = False
    ) -> None:
        
        if len(self.nodes) == 0:
            return
        still_unconnected: list[list[Node[V, E]]] = self.find_connected_components_directed()
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