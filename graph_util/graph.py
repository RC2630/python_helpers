from typing import Callable, NamedTuple
import helpers.random_util as ru

class EdgeValue[E](NamedTuple):
    cost: float
    payload: E

# -------------------------------------------

class Node[V, E]:

    def __init__(self, name: str | None = None, payload: V = None) -> None:
        self.name: str = name if name is not None else f"node_{id(self)}"
        self.payload: V = payload
        self.edges: dict[Node[V, E], EdgeValue[E]] = {}

    def create_edge(
        self, dest: Node[V, E], cost: float = 1, undirected: bool = True,
        payload: E = None, reversed_payload: E = None, symmetric_payload: bool = False
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
            f"{dest.name}: {cost}" for dest, cost in self.edges.items()
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

# -------------------------------------------

class Graph[V, E]:

    def __init__(self, nodes: list[Node[V, E]]) -> None:
        self.nodes: list[Node[V, E]] = nodes.copy()

    def __repr__(self) -> str:
        if len(self.nodes) == 0:
            return "(empty graph)"
        return "\n".join(str(node) for node in self.nodes)

    def find_connected_components_undirected(self) -> list[list[Node[V, E]]]:
        remaining_nodes: set[Node[V, E]] = set(self.nodes)
        connected_components: list[set[Node[V, E]]] = []
        while len(remaining_nodes) > 0:
            arbitrary_node: Node[V, E] = next(iter(remaining_nodes))
            connected_component: set[Node[V, E]] = arbitrary_node.all_connected_nodes()
            connected_components.append(connected_component)
            remaining_nodes.difference_update(connected_component)
        return [list(component) for component in connected_components]

    def make_connected_undirected(
        self, cost_distribution: Callable[[], float], default_payload: E = None
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
        raise NotImplementedError("connected components for directed graphs are not supported yet")

    def make_connected_directed(
        self, cost_distribution: Callable[[], float], default_payload: E = None
    ) -> None:
        connected_components: list[list[Node[V, E]]] = self.find_connected_components_directed()
        raise NotImplementedError("make connected for directed graphs is not supported yet")