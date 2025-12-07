# test using EPSPRC on a random graph.
# Note: The results can be different compared to test_ESPP because here resources are taken into account.
import networkx as nx
import matplotlib.pyplot as plt
import logging
import pylgrim
import random
import time

def print_path(G, path):
    CHECK = 0.0
    while True:
        try:
            e = path.__next__()
            print('{} ⇨ {} : {}'.format(*e))
            CHECK += G[e[0]][e[1]]['weight']
        except StopIteration:
            # last element reached
            break
    
    return CHECK

def test_random_run():
    # possible values are: WARNING, INFO, DEBUG, ...
    # (see https://docs.python.org/3/library/logging.html#logging-levels)
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)

    # parameters
    graph_size = 15
    max_path_len = 15
    max_res = list([1.0])
    source = 0
    weight_lims = (-1.0, 1.0)

    # set seed and target
    seed = random.randint(-2**31-1, 2**31)
    
    # If you want to debug a failed run
    seed = -1213136599
    
    # set random seed to make sure edges are also the same
    random.seed(seed)

    # create test graph: inverted gnc_graph or gnp random graph
    G = nx.gnp_random_graph(graph_size, p=0.2, directed=True, seed=seed)
    target = G.number_of_nodes() 
    G.add_node(target)

    print('source = {}, target = {}'.format(source, target))
    print('maximum length of path: {}'.format(max_path_len))
    print('')

    # add one resource to limit path length and one for weight
    G.graph['n_res']=1
    for u, v in G.edges():
        G[u][v]['res_cost'] = [float(r)/(max_path_len-0.9) for r in max_res]
        G[u][v]['weight'] = random.uniform(weight_lims[0], weight_lims[1])

    # decouple (actually not necessary)
    pylgrim.tools.decouple_source(G, source, source_in=target)

    # pre-process and calculate res_min
    check_costs = []
    G_pre, res_min = pylgrim.ESPPRC.preprocess(G, source, target, max_res)

    # ESPPRC
    t0 = time.perf_counter()
    shortest_path, shortest_path_label = pylgrim.ESPPRC.GSSA(G_pre, source, target, max_res, res_min)
    time_ESPPRC = time.perf_counter() - t0

    # ESPP
    t0 = time.perf_counter()
    paths, costs = pylgrim.ESPP.DLA(G, source, min_K=1, log_summary=True)
    time_ESPP = time.perf_counter() - t0
    node = target
    path = paths[node][0]

    print('ESPPRC:')
    print('------')
    print('elapsed time: {}s'.format(time_ESPPRC))
    print('shortest path found: {} with label {}'.format(shortest_path, shortest_path_label))
    print('')
    check_costs.append(print_path(G, shortest_path))
    print('')

    print('ESPP:')
    print('----')
    print('elapsed time: {}s'.format(time_ESPP))
    print('best solution path to target:')
    print('shortest path found: {} with cost {}'.format(path, costs[node][paths[node].index(path)]))
    print('')
    check_costs.append(print_path(G, path))
    print('')

    # check
    if check_costs[0] != check_costs[1]:
        print('WARNING: costs are not equal: {} vs {}'.format(*check_costs))
        print('(seed was equal to {})'.format(seed))
        print('The most probably explanation is that max_path_len is too small for ESPPRC to find the optimal path.')

        pos = nx.circular_layout(G)
        nx.draw(G, pos)
        edge_labels = nx.get_edge_attributes(G,'weight')
        for key in edge_labels:
            edge_labels[key] = round(edge_labels[key], 2)
        nx.draw_networkx_edge_labels(G, pos, edge_labels)
        nx.draw_networkx_labels(G, pos, labels=None, font_size=12, font_color='k', font_family='sans-serif', font_weight='normal', alpha=1.0)
        plt.show()

if __name__ == "__main__":
    test_random_run()
