from helpers.graph_util.graph import *

class CannotGenerateGraphError(Exception): pass

# -------------------------------------------

def generate_graph_attempt(
    num_nodes: int,
    num_edges_distribution: Callable[[], int],
    cost_distribution: Callable[[], float],
    ensure_connected: bool,
    undirected: bool
) -> Graph[None, None]:
    
    nodes: list[Node[None, None]] = [Node(f"n{i}") for i in range(num_nodes)]
    for node in nodes:

        num_edges: int = num_edges_distribution()
        available: int = len(nodes) - len(node.edges) - 1

        if num_edges < 0:
            raise ValueError("num_edges_distribution() generated a negative number")
        if num_edges > available:
            raise ru.NotEnoughElementsError
        if num_edges == 0:
            continue

        dests: list[Node[None, None]] = (
            ru.fast_rejection_sample(
                nodes,
                count = num_edges,
                exclude = set(node.edges) | {node},
                mode = "distinct_indices"
            )
            if num_edges / available < 0.9 and available / len(nodes) > 0.1
            else ru.sample_from_sequence(
                nodes,
                count = num_edges,
                exclude = ru.Exclusion(set(node.edges) | {node}),
                mode = "distinct_indices",
                use_coarse_hashability_check = True,
                validation_options = ru.ValidationOptions()
            )
        )

        for dest in dests:
            cost: float = cost_distribution()
            node.create_edge(dest, cost, undirected)

    g: Graph[None, None] = Graph(nodes)
    if ensure_connected:
        if undirected:
            g.make_connected_undirected(cost_distribution)
        else:
            g.make_connected_directed(cost_distribution)

    return g

# -------------------------------------------

def generate_graph(
    num_nodes: int,
    num_edges_distribution: Callable[[], int],
    cost_distribution: Callable[[], float],
    ensure_connected: bool = True,
    max_attempts: int = 1000,
    undirected: bool = True
) -> Graph[None, None]:
    attempts: int = 0
    while attempts < max_attempts:
        try:
            return generate_graph_attempt(
                num_nodes, num_edges_distribution, cost_distribution,
                ensure_connected, undirected
            )
        except (ru.EmptySequenceError, ru.NotEnoughElementsError):
            attempts += 1
    raise CannotGenerateGraphError