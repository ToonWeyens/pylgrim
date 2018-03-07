# Path for pylgrim result:
#   * Is an elementary simple digraph that inherits from nx.DiGraph.
#   * As it can be cyclic, it contains the information of source node.
#   * Iterator for next edge in path can be returned.
#
# Author:
#   Toon Weyens

import networkx as nx
from copy import deepcopy

class Path(nx.DiGraph):
    """Result path with source copied from graph G"""
    
    def __init__(self, G, nodes):
        super(Path, self).__init__(n_res=G.graph['n_res'])
        self.source = nodes[0]
        self.curr_node = nodes[0]
        for e_id in range(0,len(nodes)-1):
            n1, n2 = nodes[e_id:e_id+2]
            self.add_edge(n1, n2)
            for attr in G[n1][n2]:
                self[n1][n2][attr] = G[n1][n2][attr]
    
    def __str__(self):
        path_str = str(self.source)
        node = self.source
        while True:
            try:
                node = list(self.succ[node])[0]
                path_str += ' ⇨ ' + str(node)
            except IndexError:
                # last element reached
                break
            except KeyError:
                # first element had no successors
                break
        return path_str
    
    def __repr__(self):
        """identical to __str__ without the arrow."""
        path_str = str(self.source)
        node = self.source
        while True:
            try:
                node = list(self.succ[node])[0]
                path_str += ' ' + str(node)
            except IndexError:
                # last element reached
                break
            except KeyError:
                # first element had no successors
                break
        return path_str
    
    def __eq__(x,y):
        """Path considers only differences of the nodes variable."""
        return repr(x) == repr(y)
    
    def __hash__(self):
        """Path considers only differences of the nodes variable."""
        return hash(repr(self))
    
    def __iter__(self):
        # reset the counter to source when iterator is created
        self.curr_node = self.source
        return self

    def __next__(self):
        """Get next edge of path.
        Returns tuple with previous node, next node and edge attributes"""
        while True:
            prev_node = self.curr_node
            try:
                self.curr_node = list(self.succ[prev_node])[0]
                return (prev_node, self.curr_node, self[prev_node][self.curr_node])
            except IndexError:
                # last element reached
                raise StopIteration
            except KeyError:
                # first element had no successors
                raise StopIteration
