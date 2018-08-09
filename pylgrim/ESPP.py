# Solve Elementary Shortest Path Problem without resource constraints.
# The algorithm is based on [1], but improved by the author.
# Features:
#   * single source / all targets
#   * no resources
#   * elementary paths are sought by requesting more and more paths for nodes which have been found to form part of a NCC (negative cost cycle), when there is no alternative.
#
# Note: The strategy in [1] is intrinsically flawed. Consider the following situation:
#   * Node 2 has a path 0->1->2.
#   * Node 3 has a path 0->3.
#   * A path from node 3 can be extended to node 2, say 0->3->2.
#   * If this path has lower cost than path 2, it replaces it.
#   * To find a path to node 3, now, by extending node 2, the only possible option is 0->3, in order not to have cycles.
#   * However, it is perfectly possible that 0->1->2->3 is better than 0->3, but 0->1->2 was thrown away.
#
# The solution to this problem is to keep more paths. The algorithm, however, then becomes very slow.
# It is therefore no advised to be used for anything but very small graphs.
#
# Author:
#   Toon Weyens
#
# References: 
#   [1]: "On the shortest path problem with negative cost cycles" by Di Puglia Pugliese, Luigi (DOI: 10.1007/s10589-015-9773-1)
from collections import deque, OrderedDict
import networkx as nx
import logging
from . import tools as pt
from . import path as pth

#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def TLAdynK(G, source, K, max_path_len = -1, retry_paths = False):
    """Truncated labelling algorithm for dynamic kSPP
    (based on algorithm 3 from [1])"""
    
    # 1. Initialization
    inf = float('inf')
    # paths for each node
    paths = {source: list()}
    paths[source].append([source])
    # costs for each path
    costs = {source: list()}
    costs[source].append(0)
    # list of nodes to treat and deque to store FIFO
    L = set([source])
    L_q = deque([source])
    # first node that has been put again in the back of the queue to retry later because it gave a NCC
    L_first_retry = None
    
    # 2. main loop for selected node
    while L_q:
        # select element FIFO
        u = L_q.popleft()
        L.remove(u)
        logger.debug('  element {}'.format(u))
        
        # Set up check for NCC:
        #   1. All requested paths K_i have been determined to node i.
        #   2. It is not possible to generate at least one elementary path.
        #   3. There is at least one NCC.
        # Test 1 is done here for all children, while the other 2 are done
        # inside the children loop.
        NCC_conds = [False]*3
        # There should not be more than K[u] costs, so == should be fine.
        NCC_conds[0] = len(costs[u]) >= K[u]
        
        # extend label for each child
        for v, e in G.succ[u].items():
            logger.debug('    treating edge {} -> {}, weight = {} with current paths:'.format(u,v,e['weight']))
            first_elem_path = 0
            for n in range(0,min(len(paths.get(v,[])),K[v])):
                logger.debug('      {} ({})'.format(pt.print_path(paths[v][n]),costs[v][n]))
            logger.debug('')
            
            # error if the source is a child. The in-edges of the source need to be separated from the out-edges.
            if v == source:
                log_str = 'ERROR: source cannot be a child'
                print(log_str)
                logger.critical(log_str)
                quit()
            
            # if first test indicates possible NCC, perform test 2 and 3
            if NCC_conds[0]:
                # Initialize test 2 to true (all paths are elementary) and then
                # check whether there is not at least one non-elementary one.
                # Also initialize test 3 to False (no NCC) and then check whether
                # there is not at least one NCC.
                NCC_conds[1] = True
                NCC_conds[2] = False
                NCCs = []
                logger.debug('      testing because test 0 was not negative')
                for ku in range(0,len(costs.get(u,[]))):
                    if not (v in paths[u][ku]):
                        logger.debug('        {} not in {}'.format(v,pt.print_path(paths[u][ku])))
                        logger.debug('          -> at least one elementary path {}'.format(ku))
                        NCC_conds[1] = False
                        first_elem_path = ku
                        break
                    else:
                        logger.debug('        {} in {}'.format(v,pt.print_path(paths[u][ku])))
                        logger.debug('        NCC criterion: {} + {} ?< {}'.format(costs[u][ku],e['weight'],costs.get(v,[inf])[0]))
                        if (costs[u][ku] + e['weight'] < costs.get(v,[inf])[0]):
                            NCC_conds[2] = True
                            for n in paths[u][ku]:
                                if not (n in NCCs):
                                    NCCs.append(n)
            
            # check for all tests
            if all(NCC_conds):
                if retry_paths and not u == L_first_retry:
                    logger.debug('      putting node {} back in the queue to retry later'.format(u))
                    
                    # put it back in queue if this is the first
                    if L_first_retry == None:
                        L_first_retry = u
                    L.add(u)
                    L_q.append(u)
                    logger.debug('  {} elements in queue'.format(len(L)))
                    
                    # skip current node
                    break
                else:
                    logger.debug('      returning {} NCC(s)'.format(len(NCCs)))
                    for i in range(0,len(NCCs)):
                        logger.debug('        {}'.format(NCCs[i]))
                    return paths, costs, NCCs
                    
            else:
                # initialize path with cost for v if not yet done
                if (costs.get(v) == None):
                    costs[v] = list()
                    paths[v] = list()
                
                # Loop over all paths of u.
                # Note that the lower boundary is possibly given by the first elementary path,
                # found in the check for NCC. The upper boundary is not taken to be equal to
                # K[u], but instead to the number of paths to that have been set up. Each of
                # these can potentially give a lower result.
                for ku in range(first_elem_path,len(paths[u])):
                    # abandon this iteration if invalid path
                    if v in paths[u][ku]:
                        continue
                    
                    logger.debug('      from node {} trying to extend path {}: {} -> {}'.format(u,ku,pt.print_path(paths[u][ku],max_path_len_for_print=3),v))
                    
                    # Loop over all paths of v.
                    # Note that even though only K[v] paths are sought ultimately, it can very well
                    # be that a number of these paths are eliminated when extending it further to other
                    # nodes, so that paths that are more costly to the current node could be needed
                    # for the extensions.
                    for kv in range(0,max(K[v],len(paths[v]))):
                        # sets up possible new path, as well as costs
                        path_v = list(paths[u][ku])
                        path_v.append(v)
                        cost_u = costs.get(u,[inf])
                        cost_v = costs.get(v,[inf])
                        cost_ku = cost_u[ku] if ku < len(cost_u) else inf
                        cost_kv = cost_v[kv] if kv < len(cost_v) else inf
                        logger.debug('        ku = {}/{}, kv = {}/{}'.format(ku,K[u]-1,kv,K[v]-1))
                        logger.debug('          current cost of path {}: {}'.format(kv,cost_kv))
                        logger.debug('          cost of potential new path = {}'.format(cost_ku+e['weight']))
                        #if (cost_ku + e['weight'] < cost_kv) or \
                            #(cost_ku + e['weight'] == cost_kv and not path_v == paths[v][kv] and not kv >= len(paths[v])):
                        # by default add path if not higher cost
                        add_new_path = cost_ku + e['weight'] <= cost_kv
                        # but check for duplicates all previous paths up to kv, as long as they have been initialized
                        for kv2 in range(0,min(kv,len(paths[v])-1)+1):
                            if path_v == paths[v][kv2]:
                                logger.debug('          path already existed in paths[{}][{}]'.format(v,kv2))
                                add_new_path = False
                                break
                        
                        # check maximum path length if positive
                        if max_path_len > 0 and len(path_v) > max_path_len:
                            logger.debug('          maximum path length {} reached'.format(max_path_len))
                            add_new_path = False
                            break
                            
                        if (add_new_path):
                            # possibly empty the variable containing first retry
                            L_first_retry = None
                            
                            # insert new path with cost
                            logger.debug('          inserting path {}({}) in path[{}] at position {}'.format(path_v,cost_ku + e['weight'],v,kv))
                            costs[v].insert(kv,cost_ku + e['weight'])
                            paths[v].insert(kv,path_v)
                            
                            # possibly add node v to L
                            if not (v in L):
                                logger.debug('          add node {} to set L'.format(v))
                                L.add(v)
                                L_q.append(v)
                            
                            # skip all following kv to next path ku
                            break
                        else:
                            logger.debug('          this path was not inserted')
            
            logger.debug('    resulting paths to {}:'.format(v))
            for n in range(0,len(paths[v])):
                logger.debug('      {}({})'.format(pt.print_path(paths[v][n]),costs[v][n]))
            logger.debug('')
        logger.debug('  {} elements in queue'.format(len(L)))
        logger.debug('')
        #print('  ------------------------------------------------------')
        #input("  Press Enter to continue...")
        #print('  ------------------------------------------------------')
        #print('')
    
    return paths, costs, []


def DLA(G, source, min_K=1, output_pos = False, max_path_len=-1):
    """Dynamic labelling algorithm
    (based on algorithm 4 from [1])"""
    
    logger.info('source: {}'.format(source))
    
    # initialize K label to minimal value and not done
    K = {}
    for n in G.nodes:
        K[n] = min_K
    DLA_done = False

    while not DLA_done:
        # Run truncated labelling algorithm for dynamic kSPP
        paths, costs, NCCs = TLAdynK(G, source, K, max_path_len)
        
        # output for tests
        logger.info('')
        logger.info('costs summary of this level:')
        costs_tot = dict()
        for n in G.nodes():
            for p in range(0,len(paths.get(n,[]))):
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
        if NCCs == []:
            break
        else:
            logger.debug('updating K:')
            for n in NCCs:
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
            rpaths[node].append(pth.Path(G, path))
    return rpaths, costs
