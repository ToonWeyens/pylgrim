# Tools for pylgrim:
#   * create_test_graph to create a test graph.
#   * decouple_source and undecouple_source to move all in-edges from a source node to a duplicate and vice versa.
#   * print_path to pretty print a path.
#   * count_elems to count the number of elements in a path and return a dictionary keyed with a label.
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

def decouple_source(G, source, source_in="source_in", atts={'weight'}):
    """Decouple the source {source} of a graph {G}, by duplicating the node, called {source_in} and moving all the in-edges to it.
    Attributes described in {atts} are also copied.
    Returns the number of edges displaced."""
    
    in_edges_source = tuple(G.in_edges(source))
    n_in_edges_source = len(in_edges_source)
    if n_in_edges_source > 0:
        logger.debug('displace {} in-edges ⇨ {}'.format(n_in_edges_source,source))
        
        for e in in_edges_source:
            logger.debug('  move edge {}'.format(e))
            G.add_edge(e[0],source_in)
            for att in atts:
                G[e[0]][source_in][att] = G.get_edge_data(*e)[att]
            G.remove_edge(*e)

    return n_in_edges_source

def undecouple_source(G, source, source_in="source_in", atts={'weight'}):
    """Invert the decoupling of the source {source} of a graph {G} done in decouple_source by moving all the edges to {source_in} back to {source}.
    Attributes described in {atts} are also copied back.
    Returns the number of edges displaced."""
    
    in_edges_source = tuple(G.in_edges(source_in))
    n_in_edges_source = len(in_edges_source)
    if n_in_edges_source > 0:
        logger.debug('place back {} in-edges  {}'.format(n_in_edges_source,source))
        
        for e in in_edges_source:
            logger.debug('  move edge {}'.format(e))
            G.add_edge(e[0],source)
            for att in atts:
                G[e[0]][source][att] = G.get_edge_data(e[0],source_in)[att]
            G.remove_edge(e[0],source_in)
        G.remove_node(source_in)

    return n_in_edges_source

def print_path(path, max_path_len_for_print = None):
    """Pretty-print a path given as an iterable of strings.
    Optionally trim if longer than max_path_len_for_print
    """
    path_short = str(path[0])
    if max_path_len_for_print is None:
        max_path_len_for_print = len(path)
    if len(path) > max_path_len_for_print + 1:
        for p in range(1,max_path_len_for_print-1):
            path_short += ' ⇨ ' + str(path[p])
        path_short += ' ⇨  …  ⇨ ' + str(path[len(path)-1])
    else:
        for p in range(1,len(path)):
            path_short += ' ⇨ ' + str(path[p])
    return path_short

def count_elems(path):
    """Count elements in a path and return a dictionary keyed with label"""
    res = dict()
    for n in path:
        res[n] = res.get(n,0)+1
    return res
