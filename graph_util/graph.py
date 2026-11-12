from typing import NamedTuple
from collections.abc import Iterable, Container

# -------------------------------------------

class EdgeValue[E](NamedTuple):

    cost: float
    payload: E

    def update_cost(self, new_cost: float) -> EdgeValue[E]:
        return EdgeValue(new_cost, self.payload)

    def update_payload(self, new_payload: E) -> EdgeValue[E]:
        return EdgeValue(self.cost, new_payload)

    def display_form(self) -> str:
        if self.payload is None:
            return str(self.cost)
        else:
            return f"{self.cost} [{self.payload}]"

# -------------------------------------------

class Node[V, E]:

    SYMMETRIC = sentinel("SYMMETRIC") # using python 3.15+ built-in sentinel

    def __init__(self, name: str | None = None, payload: V = None) -> None:
        self.name: str = name if name is not None else f"node_{id(self)}"
        self.payload: V = payload
        self.edges: dict[Node[V, E], EdgeValue[E]] = {}

    def create_edge(
        self, dest: Node[V, E], cost: float = 1, undirected: bool = True,
        payload: E = None, reversed_payload: E | SYMMETRIC = SYMMETRIC
    ) -> None:
        self.edges[dest] = EdgeValue(cost, payload)
        if undirected:
            if reversed_payload is Node.SYMMETRIC:
                dest.edges[self] = EdgeValue(cost, payload)
            else:
                dest.edges[self] = EdgeValue(cost, reversed_payload)

    def display_form(self) -> str:
        if self.payload is None:
            return self.name
        else:
            return f"{self.name} [{self.payload}]"

    def __repr__(self) -> str:
        base: str = f"{self.display_form()} -> "
        if len(self.edges) == 0:
            return base + "(no edges)"
        else:
            return base + ", ".join(
                f"{dest.name}: {edge.display_form()}"
                for dest, edge in self.edges.items()
            )

    def all_reachable_nodes(self, ignore: Container[Node[V, E]] = ()) -> set[Node[V, E]]:
        if self in ignore:
            return set()
        result: set[Node[V, E]] = {self}
        frontier: list[Node[V, E]] = [self]
        while len(frontier) > 0:
            curr: Node[V, E] = frontier.pop()
            for neighbour in curr.edges:
                if neighbour not in result and neighbour not in ignore:
                    result.add(neighbour)
                    frontier.append(neighbour)
        return result

# -------------------------------------------

class Graph[V, E]:

    def __init__(self, nodes_or_node: Iterable[Node[V, E]] | Node[V, E] = ()) -> None:
        if isinstance(nodes_or_node, Node):
            self.nodes: list[Node[V, E]] = list(nodes_or_node.all_reachable_nodes())
        else:
            self.nodes = list(nodes_or_node)

    def __repr__(self) -> str:
        if len(self.nodes) == 0:
            return "(empty graph)"
        return "\n".join(str(node) for node in self.nodes)