# Tools for pylgrim tests:
#   * create_test_graph to create a test graph.
#
# Author:
#   Toon Weyens

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def create_test_graph(add_nodes_to_0=False):
    """create test based on graph from [1]
    (see 'testgraph.png')
    With the flag {add_nodes_to_0} the graph can be extended with two nodes to 0"""
    G = nx.DiGraph(n_res=2)
    G.add_edge(0, 1, weight=2, res_cost=np.array([0.1,0.2]))
    G.add_edge(0, 2, weight=-4, res_cost=np.array([0.1,0.2]))
    G.add_edge(1, 2, weight=-7, res_cost=np.array([0.1,0.2]))
    G.add_edge(1, 4, weight=5, res_cost=np.array([0.1,0.3]))
    G.add_edge(2, 3, weight=3, res_cost=np.array([0.1,0.2]))
    G.add_edge(3, 1, weight=1, res_cost=np.array([0.1,0.2]))
    G.add_edge(2, 5, weight=-2, res_cost=np.array([0.1,0.2]))
    G.add_edge(5, 6, weight=2, res_cost=np.array([0.1,0.2]))
    G.add_edge(5, 4, weight=-2, res_cost=np.array([0.1,0.2]))
    G.add_edge(4, 2, weight=3, res_cost=np.array([0.1,0.2]))
    G.add_edge(4, 6, weight=3, res_cost=np.array([0.1,0.3]))
    if add_nodes_to_0:
        # add nodes to 0 for test
        G.add_edge(6, 0, weight=-1, res_cost=np.array([0.1,0.2]))
        G.add_edge(1, 0, weight=-2, res_cost=np.array([0.1,0.2]))

    return G

def lighter(color, percent):
    """Makes a color lighter. Adapted from https://stackoverflow.com/a/28033054.
    Assumes color is rgb between (0, 0, 0) and (255, 255, 255)"""
    color = np.array(hex2RGB(color))
    white = np.array([255, 255, 255])
    vector = white-color
    if percent < 0.0 or percent > 100.0:
        raise ValueError('percent must be between 0 and 100')
    
    return RGB2hex(color + vector * percent/100.0)

def hex2RGB(h):
    """Returns an RGB tuple for a hex string.
    Adapted from https://stackoverflow.com/a/29643643."""
    if h[0] != '#' or len(h) !=7 :
        raise ValueError('not a hex string')
    
    return tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2 ,4))

def RGB2hex(rgb):
    """Returns an hex string for an RGB tuple.
    Adapted from from https://stackoverflow.com/a/214657."""
    if len(rgb) != 3 or np.amax(rgb) > 255 or np.amin(rgb) < 0:
        raise ValueError('not a rgb tuple')
    
    return '#%02x%02x%02x' % (int(rgb[0]), int(rgb[1]), int(rgb[2]))

def visualize_path(G, path):
    """Visualize a path"""
    pos = nx.circular_layout(G)
    colors = list()
    weights = list()
    max_weight = np.amax([abs(sublist[-1]) for sublist in G.edges.data('weight', default=0.0)])
    
    # colors for positive (0) and negative (1) edges
    #max_colors = tuple(['#B1D877', '#ADD9FE'])
    max_colors = tuple(['#FF0000', '#0000FF'])
    
    # set up widths and colors
    for u, v in G.edges():
        if path.has_edge(u,v):
            colors.append('black')
            weights.append(3)
        else:
            if G[u][v]['weight'] > 0:
                colors.append(lighter(max_colors[0], 100*((max_weight-abs(G[u][v]['weight']))/max_weight)))
            else:
                colors.append(lighter(max_colors[1], 100*((max_weight-abs(G[u][v]['weight']))/max_weight)))
            weights.append(2)
    
    nx.draw(G, pos, edgelist=G.edges(), edge_color=colors, node_color = '#8CDCDA', width=weights)
    nx.draw_networkx_labels(G, pos, labels=None, font_size=12, font_color='k', font_family='sans-serif', font_weight='normal', alpha=1.0)
    plt.show()
    
    return
