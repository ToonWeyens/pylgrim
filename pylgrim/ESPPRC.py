# Solve Elementary Shortest Path Problem with resource constraints.
# The algorithm is based on [1].
# Features:
#   * single source / single target
#   * with resources
#   * elementary paths are sought by intelligently adding node resources to nodes that have been found to be in a NCC (negative cost cycle).
#
# Author:
#   Toon Weyens
#
# References: 
#   [1]: "Accelerated label setting algorithms for the elementary resource constrained shortest path problem" by Boland, Natashia (DOI: 10.1016/j.orl.2004.11.011)
import networkx as nx
import numpy as np
import logging
from . import tools as pt
from . import path as pth

#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# global variables
_resource_nr = 0
_resource_name = 'res_cost'

def prune_graph(G, source, target, max_res, res_name='res_cost'):
    """first step of graph {G} preprocessing
    (based on algorithm 2.1, step 0, from [1])
    Prune the graph, reducing the number of nodes and arcs, by considering least resource paths from the path {source} node to each node in the graph and from each node in the graph to the path {target} node, for each resource subject to a maximum resource in {max_res}."""
    
    global _resource_nr, _resource_name
    
    _resource_name = res_name
    
    logger.debug('Pre-process graph')
    
    # to start with, all nodes are assumed to be reachable
    n_res = G.graph['n_res']
    reachable_nodes = set(G.nodes())
    
    # iterate over all resources and delete nodes that are not reachable
    logger.debug('Delete unreachable nodes')
    for res in range(0,n_res):
        logger.debug('Treating resource {}'.format(res))
        _resource_nr = res
        
        logger.debug('Calculate feasible paths from source for resource {}'.format(res))
        lengths_source = dict(nx.single_source_dijkstra_path_length(G, source, cutoff=max_res[res], weight=_res_cost_i))
        if target not in lengths_source:
            logger.error('target not reachable for resource {}'.format(res))
            exit()
        
        logger.debug('Calculate feasible paths to target for resource {}'.format(res))
        lengths_target = dict(nx.single_source_dijkstra_path_length(G.reverse(copy=True), target, cutoff=max_res[res], weight=_res_cost_i))
        if source not in lengths_target:
            logger.error('source not reachable for resource {}'.format(res))
            exit()
        
        nodes_to_remove = set()
        for node in reachable_nodes:
            if node not in lengths_source or node not in lengths_target:
                nodes_to_remove.add(node)
            elif lengths_source[node] + lengths_target[node] > max_res[res]:
                nodes_to_remove.add(node)
        
        logger.debug('Remove {} nodes due to violation of resource'.format(len(nodes_to_remove),res))
        for node in nodes_to_remove:
            reachable_nodes.remove(node)
    
    logger.debug('{} reachable nodes:'.format(len(reachable_nodes)))
    logger.debug('      {}'.format(reachable_nodes))
    
    # set up reduced graph
    logger.debug('Set up reduced graph')
    H = nx.DiGraph(n_res=n_res)
    for node in reachable_nodes:
        for node2 in reachable_nodes:
            if G.has_edge(node, node2) and not H.has_edge(node,node2): 
                H.add_edge(node, node2)
                for attr in G[node][node2]:
                    H[node][node2][attr] = G[node][node2][attr]
    #nx.draw_circular(H,with_labels=True)
    #plt.show()
    
    # return pruned graph
    return H

def setup_least_resource_paths_ESPPRC(G, res_name='res_cost'):
    """second step of graph {G} preprocessing
    (based on algorithm 2.1, step 0, from [1])
    Solve the all-pairs shortest path problem on the graph, with lengths set to {_res_cost_i} , for each resource r."""
    
    global _resource_nr, _resource_name
    
    _resource_name = res_name
    
    # iterate over all resources and calculate least-resource paths for all pairs
    n_res = G.graph['n_res']
    logger.debug('Calculate least-resource pairs')
    res_min = list()
    for res in range(0,n_res):
        logger.debug('Treating resource {}'.format(res))
        _resource_nr = res
        res_min.append(dict(nx.all_pairs_dijkstra_path_length(G, weight=_res_cost_i)))
    
    # return preprocessed network and least-resource paths
    return res_min

def preprocess(G, source, target, max_res, res_name='res_cost'):
    """preprocess graph {G}
    (based on algorithm 2.1, step 0, from [1])"""
    
    # 1. prune graph
    H = prune_graph(G, source, target, max_res, res_name=res_name)
    
    # 2. set up least resource paths
    res_min = setup_least_resource_paths_ESPPRC(H, res_name=res_name)
    
    # return preprocessed network and least-resource paths
    return H, res_min

def GLSA(G, S, source, target, max_res, res_min, res_name='res_cost'):
    """General Label Setting Algorithm
    (based on algorithm 2.1, step 1 and 2, from [1])"""
    
    # test
    if target == source:
        logger.error('target cannot be source')
        exit()
    
    # 1. Initialization
    inf = float('inf')
    n_res = G.graph['n_res']
    # paths for each node
    paths = {source: list()}
    paths[source].append([source])
    # labels for each path (cost, resources):
    labels = {source: list()}
    labels[source].append((0,np.zeros(n_res+len(S))))
    # labels to treat: start with 0th label of path ending at source
    L = set([(source,0)])
    
    # 2. select lexicographically minimal label
    logger.debug('Loop over labels to be extended')
    while L:
        # select lexicographically minimal label
        logger.debug('Select lexicographically minimal label:')
        LML_for_prev_res= L
        for res in range(0,n_res+len(S)):
            res_LML = inf
            LML_for_this_res = []
            for label in LML_for_prev_res:
                res_loc = labels[label[0]][label[1]][1][res]
                if res_loc <= res_LML:
                    # better or equivalent label
                    res_LML = res_loc
                    LML_for_this_res.append(label)
            # set u_label to first element found
            u_label = LML_for_this_res[0]
            u = u_label[0]
            l = u_label[1]
            if len(LML_for_this_res) == 1:
                # found lexicographically minimal label
                break
            else:
                # multiple labels equivalent for this res
                LML_for_prev_res = LML_for_this_res
        L.remove(u_label)
        
        logger.debug('{}th label of node {} chosen:'.format(l,u))
        logger.debug('{} (C {} | R {})'.format(pt.print_path(paths[u][l]),labels[u][l][0],labels[u][l][1]))
        
        # extend label for each child
        for v, e in G.succ[u].items():
            logger.debug('treating edge {} -> {} (C {} | R {})'.format(u,v,e['weight'],e[res_name]))
            if len(paths.get(v,[])) > 0: logger.debug('      with current paths:')
            for n in range(0,len(paths.get(v,[]))):
                logger.debug('{} (C {} | R {})'.format(pt.print_path(paths[v][n]),labels[v][n][0],labels[v][n][1]))
            
            # error if the source is a child. The in-edges of the source need to be separated from the out-edges.
            if v == source:
                logger.critical('ERROR: source cannot be a child')
                quit()
            
            # determine whether to create a new label on the child node
            e_loc = np.zeros(n_res+len(S))
            e_loc[0:n_res] = G[u][v][res_name]
            if v in S:
                e_loc[n_res+S.index(v)] = 1
            v_label = (labels[u][l][0] +  G[u][v]['weight'], labels[u][l][1] +  e_loc)
            add_label = True
            
            # check edge resources
            for res in range(0,n_res):
                if v_label[1][res] + res_min[res][v].get(target,0.0) > max_res[res]:
                    add_label = False
                    logger.debug('at least {} more of resource {} is needed to reach target'.format(res_min[res][v].get(target,0.0),res))
                    break
            
            # check node resources
            for res in range(0,len(S)):
                if v_label[1][n_res+res] > 1:
                    add_label = False
                    logger.debug('node {} was used twice'.format(S[res]))
                    break
            
            # add
            if add_label:
                # check subset of all labels that belong to the same node for domination
                label_dominated = False
                if len(labels.get(v,[])) > 0:
                    for label in labels.get(v,[]):
                        label_dominated = _is_dominated(v_label, label)
                        if label_dominated: break
                
                if label_dominated:
                    logger.debug('but label was dominated')
                else:
                    # setup label and path
                    if labels.get(v, None) == None:
                        paths[v] = list()
                        labels[v] = list()
                    v_path = list(paths[u][l])
                    v_path.append(v)
                    
                    logger.debug('add undominated label {} (C {} | R {})'.format(pt.print_path(v_path),v_label[0],v_label[1]))
                    
                    # strong dominance: set node resource to one for nodes in S that cannot
                    # be feasibly visited with edge resources
                    for n in S:
                        for res in range(0,n_res):
                            if v_label[1][res] + res_min[res][n].get(n,0.0) > max_res[res]:
                                if v_label[1][n_res+S.index(n)] == 0:
                                    logger.debug('set strong dominance for node resource {}'.format(S.index(n)))
                                    v_label[1][n_res+S.index(n)] = 1
                    
                    # remove dominated labels
                    # Note: It is possible that two labels are identical but have different paths.
                    # The iteration therefore has to be using i_label, and not, for example, using
                    #   for label in labels.get(v,[]):
                    i_label = 0
                    n_labels = len(labels.get(v,[]))
                    while i_label < n_labels:
                        label = labels[v][i_label]
                        if _is_dominated(label, v_label):
                            logger.debug('remove dominated label {} (C {} | R {})'.format(pt.print_path(paths[v][i_label]),label[0],label[1]))
                            labels[v].pop(i_label)
                            paths[v].pop(i_label)
                            L_rename = set()
                            if (v, i_label) in L:
                                L.remove((v, i_label))
                            for i in range(i_label+1, len(labels[v])+1):
                                if (v, i) in L:
                                    L_rename.add((v,i-1))
                                    L.remove((v,i))
                            L.update(L_rename)
                            i_label -= 1
                            n_labels -= 1
                        i_label += 1
                    
                    # add label and path
                    paths[v].append(v_path)
                    labels[v].append(v_label)
                    
                    # add to list L
                    L.add((v, len(labels[v])-1))
            else:
                logger.debug('therefore do not add unfeasible label {}'.format(v_label[1]))
            
    
    # return cheapest paths with label
    logger.debug('Select cheapest path to {}'.format(target))
    
    least_cost = inf
    for p in range(0,len(labels[target])):
        if labels[target][p][0] < least_cost:
            best_path = paths[target][p]
            best_label = labels[target][p]
            least_cost = best_label[0]
    return best_path, best_label

def GSSA(G, source, target, max_res, res_min, res_name='res_cost'):
    """General State Space Augmenting Algorithm
    (based on algorithm 2.2, from [1])
    Note: The graph must have been preprocessed so that it is reduced and has the minimal resource information in {res_min}."""
    
    logger.debug('Searching for shortest path {} -> {}'.format(source, target))
    
    # initialize node resources and not done
    S = list([])
    DLA_done = False

    while not DLA_done:
        # Run dynamic labelling algorithm
        path, label = GLSA(G, S, source, target, max_res, res_min, res_name=res_name)
        logger.debug('found path {} (C {} | R {})'.format(pt.print_path(path, max_path_len_for_print=len(path)), label[0], label[1]))
        path_elems = pt.count_elems(path)
        path_max_mult = max(path_elems.values())
        if path_max_mult == 1:
            logger.debug('it is elementary')
            DLA_done = True
        else:
            logger.debug('but is it not elementary')
            node_max_mult = max(path_elems, key=path_elems.get)
            S.append(node_max_mult)
            logger.debug('Incrementing node {}, which had multiplicity {}:'.format(node_max_mult, path_max_mult))
            logger.debug('S = {}'.format(S))
        #input('PAUSED')
    
    return pth.Path(G,path), label

def _is_dominated(a, b):
    """returns whether a label {a} is dominated by another label {b}"""
    
    logger.debug('check for domination of {} by {}'.format(a,b))
    if a[0] == b[0] and all(a[1] == b[1]):
        label_dominated = False
    else:
        label_dominated = True
        if a[0] < b[0]:
            label_dominated = False
        if any(a[1] < b[1]):
            label_dominated = False
    return label_dominated

def _res_cost_i(u,v,e):
    """returns weight of certain resource with index {_resource_nr} of edge {e} from node {u} to {v}, given by variable {_resource_name}.
    It is used by all_pairs_dijkstra_path_length:
        'The weight of an edge is the value returned by the function.
        The function must accept exactly three positional arguments: the two endpoints of an edge and the dictionary of edge attributes for that edge.
        The function must return a number.'"""
    
    global _resource_nr, _resource_name
    
    return e[_resource_name][_resource_nr]
