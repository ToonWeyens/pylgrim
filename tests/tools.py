# Tools for pylgrim tests:
#   * create_test_graph to create a test graph.
#
# Author:
#   Toon Weyens

import numpy as np
import logging

#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_test_graph(G, add_nodes_to_0=False):
    """create test based on graph from [1]
    (see 'testgraph.png')
    The graph should be initialized using::
        
        G = nx.DiGraph(n_res=2)
        
    With the flag {add_nodes_to_0} the graph can be extended with two nodes to 0"""
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
