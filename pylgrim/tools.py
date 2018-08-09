# Tools for pylgrim:
#   * decouple_source and undecouple_source to move all in-edges from a source node to a duplicate and vice versa.
#   * print_path to pretty print a path.
#   * count_elems to count the number of elements in a path and return a dictionary keyed with a label.
#
# Author:
#   Toon Weyens

import logging

#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def decouple_source(G, source, source_in="source_in"):
    """Decouple the source {source} of a graph {G}, by duplicating the node, called {source_in} and moving all the in-edges to it.
    Returns the number of edges displaced."""
    
    in_edges_source = tuple(G.in_edges(source))
    n_in_edges_source = len(in_edges_source)
    if n_in_edges_source > 0:
        logger.debug('displace {} in-edges ⇨ {}'.format(n_in_edges_source,source))
        
        for e in in_edges_source:
            logger.debug('  move edge {}'.format(e))
            G.add_edge(e[0],source_in)
            for attr in G[e[0]][e[1]]:
                G[e[0]][source_in][attr] = G[e[0]][e[1]][attr]
            G.remove_edge(*e)

    return n_in_edges_source


def undecouple_source(G, source, source_in="source_in"):
    """Invert the decoupling of the source {source} of a graph {G} done in decouple_source by moving all the edges to {source_in} back to {source}.
    Returns the number of edges displaced."""
    
    in_edges_source = tuple(G.in_edges(source_in))
    n_in_edges_source = len(in_edges_source)
    if n_in_edges_source > 0:
        logger.debug('place back {} in-edges {} - {}'.format(n_in_edges_source,source, in_edges_source))
        
        for e in in_edges_source:
            G.add_edge(e[0],source)
            for attr in G[e[0]][e[1]]:
                G[e[0]][source][attr] = G[e[0]][e[1]][attr]
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
