"""
Quick plotting helper for the failing random seed without rerunning ESPP/ESPPRC.

It rebuilds the random graph for seed -1213136599 and draws:
- ESPPRC best path (hardcoded from prior run) in green.
- ESPP (min_K=1) best path (hardcoded from prior run) in red.
"""

import random
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pylgrim


def plot_hardcoded_seed():
    seed = -1213136599
    graph_size = 15
    max_path_len = 15
    max_res = [1.0]
    source = 0
    weight_lims = (-1.0, 1.0)

    # Recreate the exact random graph/weights used in the failing run
    random.seed(seed)
    G = nx.gnp_random_graph(graph_size, p=0.2, directed=True, seed=seed)
    target = G.number_of_nodes()
    G.add_node(target)
    G.graph["n_res"] = 1
    for u, v in G.edges():
        G[u][v]["res_cost"] = [float(r) / (max_path_len - 0.9) for r in max_res]
        G[u][v]["weight"] = random.uniform(*weight_lims)

    # Match test setup: decouple source in-edges onto the target node
    pylgrim.tools.decouple_source(G, source, source_in=target)

    # Hardcoded paths from earlier ESPPRC/ESPP runs (iterables of node IDs)
    espprc_nodes = [0, 10, 4, 11, 3, 2, 9, 12, 7, 14, 13, 5, 15]
    espp_nodes = [0, 10, 4, 14, 13, 3, 2, 9, 12, 6, 5, 15]

    def path_to_edges(nodes):
        return [(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)]

    def path_cost(nodes):
        return sum(G[u][v]["weight"] for u, v in path_to_edges(nodes))

    print(f"ESPPRC cost: {path_cost(espprc_nodes)} path: {espprc_nodes}")
    print(f"ESPP   cost: {path_cost(espp_nodes)} path: {espp_nodes}")

    # spring_layout needs a non-negative seed; keep graph seed but wrap for layout
    layout_seed = seed % (2**32)
    pos = nx.spring_layout(G, seed=layout_seed)
    plt.figure(figsize=(10, 8))
    nx.draw_networkx_nodes(G, pos, node_size=300, node_color="#dddddd")
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, edge_color="#cccccc", arrows=True, alpha=0.3)

    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=path_to_edges(espprc_nodes),
        edge_color="blue",
        width=2.5,
        arrows=True,
    )
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=path_to_edges(espp_nodes),
        edge_color="red",
        width=2.5,
        style="dashed",
        arrows=True,
    )

    legend_handles = [
        Line2D([0], [0], color="blue", lw=2.5, label="ESPPRC"),
        Line2D([0], [0], color="red", lw=2.5, linestyle="--", label="ESPP"),
    ]
    plt.legend(handles=legend_handles)
    plt.title(f"Seed {seed} (blue=ESPPRC, red=ESPP)")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_hardcoded_seed()
