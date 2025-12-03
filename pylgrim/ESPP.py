# Solve Elementary Shortest Path Problem without resource constraints.
# The algorithm is based on [1].
# Features:
#   * single source / all targets
#   * no resources
#   * elementary paths are sought by requesting more and more paths for nodes which have been found to form part of a NCC (negative cost cycle), when there is no alternative.
##
# Author:
#   Toon Weyens
#
# References: 
#   [1]: "On the shortest path problem with negative cost cycles" by Di Puglia Pugliese, Luigi (DOI: 10.1007/s10589-015-9773-1)
from collections import deque, OrderedDict
import logging
from . import tools as pt
from . import path as pth

logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.INFO)
logging.getLogger("matplotlib.font_manager").setLevel(logging.INFO)

logger = logging.getLogger(__name__)



def TLAdynK(G, source, K, max_path_len = -1):
    """Truncated labelling algorithm for dynamic kSPP
    (based on algorithm 3 from [1])"""
    
    # 1. Initialization
    inf = float('inf')

    paths = {n: [None] * K[n] for n in G.nodes()}
    costs = {n: [inf] * K[n] for n in G.nodes()}
    paths[source][0] = [source]
    costs[source][0] = 0

    # list of nodes to treat and deque to store FIFO
    L = set([source])
    L_q = deque([source])
    
    # 2. main loop for selected node
    while L_q:
        # select element FIFO
        u = L_q.popleft()
        L.remove(u)
        logger.debug(f'  Popping element {u} with current paths')
        for n in range(K[u]):
            if paths[u][n] is None:
                break
            logger.debug(f'    {n}: {pt.print_path(paths[u][n])} ({costs[u][n]})')

        # extend label for each child
        for v, e in G.succ[u].items():
            logger.debug(f'    treating extension to {v}, weight = {e["weight"]} with current paths:')
            for n in range(K[v]):
                if paths[v][n] is None:
                    break
                logger.debug(f'      {n}: {pt.print_path(paths[v][n])} ({costs[v][n]})')
            logger.debug('')

            # error if the source is a child. The in-edges of the source need to be separated from the out-edges.
            if v == source:
                log_str = 'ERROR: source cannot be a child'
                print(log_str)
                logger.critical(log_str)
                quit()
            
            # Set up check for NCC:
            #   1. Saturation check: We are out of memory for node u
            #   2. Elementarity/Cycle Check: Not possible to generate at least one elementary path
            #   3. Negative Cost Check: Extending u to v leads to lower cost than current best to v
            # For efficiency, we first perform test 1, and only if that is true, we perform 3, and then 2.
            NCC_conds = [False]*3
        
            # test 1: Saturation Check
            # We have filled up the entire memory for node u
            NCC_conds[0] = all(c < inf for c in costs[u])
            # if NCC_conds[0]:
            #     logger.debug(f'      test 0 (saturation): {NCC_conds[0]} because memory filled up')

            # if first test indicates possible NCC, perform tests 3 and then 2
            if NCC_conds[0]:
                # We only need to test for the first path to u, which has lowest cost.
                # If this path doesn't give a NCC, the later paths will not either.
                NCC_conds[2] = costs[u][0] + e['weight'] < costs[v][0] 
                # logger.debug(f'      test 2 (NCC): {NCC_conds[2]} because lower cost')
                
            # if tests 1 and 3 indicate possible NCC, perform test 2 (elementarity)
            if NCC_conds[2]:
                NCC_conds[1] = True
                for ku in range(0,K[u]):
                    if paths[u][ku] is None: 
                        break
                    if v not in paths[u][ku]:
                        # logger.debug('        {} not in {}'.format(v,pt.print_path(paths[u][ku])))
                        # logger.debug('          -> at least one elementary path {}'.format(ku))
                        NCC_conds[1] = False
                        break
                # logger.debug(f'      test 1 (elementarity): {NCC_conds[1]} because no elementary path')

            # unavoidable NCC detected
            if all(NCC_conds):
                # return all the nodes involved in the NCC
                pos_v_in_u = paths[u][0].index(v)
                NCC = paths[u][0][pos_v_in_u:]

                logger.debug(f'      unavoidable NCC found with nodes {NCC}:')             
                return paths, costs, NCC
                    
            else:
                # Loop over all paths of u.
                for ku in range(K[u]):
                    logger.debug(f'      extending from path {ku} of node {u}')

                    path_u = paths[u][ku]
                    if path_u is None: 
                        break
                    cost_u = costs[u][ku]

                    # abandon this iteration if invalid path
                    if v in path_u:
                        logger.debug(f'        skipping extension to {v} as it creates a cycle')
                        continue
                                        
                    # Loop over all paths of v.
                    for kv in range(K[v]):
                        path_v = paths[v][kv]
                        cost_v = costs[v][kv]

                        path_v_new = list(path_u) # lists makes a shallow copy
                        path_v_new.append(v)
                        cost_v_new = cost_u + e['weight']

                        if path_v_new in paths[v]:
                            continue # potential path already present in paths[v]

                        logger.debug(f'        comparing potential new cost {cost_v_new} to cost {cost_v} of path {kv}')
                        add_new_path = False
                        if cost_v_new < cost_v:
                            add_new_path = True
                        elif cost_v_new == cost_v:
                            add_new_path = path_v_new != path_v # equal cost is OK if we have a new path
                            
                        if (add_new_path):
                            # insert new path and shift all next down as well
                            logger.debug(f'          inserting path with cost {cost_v_new} in path[{v}] at position {kv}')
                            for kv2 in range(K[v]-1, kv, -1):
                                costs[v][kv2] = costs[v][kv2-1]
                                paths[v][kv2] = paths[v][kv2-1]
                                
                            costs[v][kv] = cost_v_new
                            paths[v][kv] = path_v_new

                            # possibly add node v to L
                            if v not in L:
                                logger.debug('          add node {} to set L'.format(v))
                                L.add(v)
                                L_q.append(v)
                            
                            # skip all following kv to next path ku
                            break
                        else:
                            logger.debug(f'          not inserting path with cost {cost_v_new} in path[{v}] at position {kv}')

            
            logger.debug('    resulting paths to {}:'.format(v))
            for n in range(0,len(paths[v])):
                if paths[v][n] is None:
                    break
                logger.debug('      {}({})'.format(pt.print_path(paths[v][n]),costs[v][n]))
            logger.debug('')
        logger.debug('  {} elements in queue'.format(len(L)))
        logger.debug('')
        #print('  ------------------------------------------------------')
        #input("  Press Enter to continue...")
        #print('  ------------------------------------------------------')
        #print('')
    
    return paths, costs, []


def DLA(G, source, min_K=1, output_pos = False, max_path_len=-1, log_summary=False):
    """Dynamic labelling algorithm
    (based on algorithm 4 from [1])"""
    
    logger.info('source: {}'.format(source))
    
    # initialize K label to minimal value and not done
    K = {}
    for n in G.nodes():
        K[n] = min_K
    DLA_done = False

    while not DLA_done:
        # Run truncated labelling algorithm for dynamic kSPP
        paths, costs, NCC = TLAdynK(G, source, K, max_path_len)
        
        # output for tests
        if log_summary:
            logger.info('')
            logger.info('costs summary of this level:')
            costs_tot = dict()
            for n in G.nodes():
                for p in range(0,len(paths.get(n,[]))):
                    if paths[n][p] is not None:
                        costs_tot[tuple(paths[n][p])] = costs[n][p]
            
            # sort (from https://stackoverflow.com/a/15179418/3229162)
            costs_sorted = OrderedDict(sorted(costs_tot.items(), key=lambda t: t[1]))
            c_id = 0
            for c in costs_sorted:
                c_id += 1
                if costs_sorted[c] < 0 or output_pos:
                    path_short = pt.print_path(c)
                    logger.info('  {}: {} for {}'.format(c_id,costs_sorted[c],path_short))
            logger.info('')
        
        # check for absence negative cost cycles
        if NCC == []:
            break
        else:
            logger.debug('updating K:')
            for n in NCC:
                K[n] += 1
                logger.debug('  K[{}] -> {}:'.format(n,K[n]))
            logger.debug('')
            #print('========================================================')
            #input("Press Enter to continue...")
            #print('========================================================')
            #print('')
    
    # return
    rpaths = dict()
    for node in paths:
        rpaths[node] = list()
        for path in paths[node]:
            if path is not None:
                rpaths[node].append(pth.Path(G, path))
    return rpaths, costs
