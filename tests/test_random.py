# test using EPSPRC on a random graph.
# Note: The results can be different compared to test_ESPP because here resources are taken into account.
import networkx as nx
import matplotlib.pyplot as plt
import logging
import pylgrim
import random
import tools as testtools
import timeit

def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped

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

# possible values are: WARNING, INFO, DEBUG, ...
# (see https://docs.python.org/3/library/logging.html#logging-levels)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# parameters
graph_size = 30
max_path_len = 6
max_res = list([1.0])
source = 0
weight_lims = (-1.0, 1.0)

# set seed and target
seed = random.randint(-2**31-1, 2**31)
target = random.randint(1, graph_size)

# OVERWRITE WITH FAILING EXAMPLE
#seed = -555578251
#target = 9

print('source = {}, target = {}'.format(source, target))
print('maximum length of path: {}'.format(max_path_len))
print('')

# create test graph: inverted gnc_graph or gnp random graph
#G = nx.generators.gnc_graph(graph_size).reverse(copy=False)
G = nx.gnp_random_graph(graph_size, p=0.2, directed=True, seed=seed)

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
wrapped_ESPPRC = wrapper(pylgrim.ESPPRC.GSSA, G_pre, source, target, max_res, res_min)
time_ESPPRC = timeit.timeit(wrapped_ESPPRC, number=1)
shortest_path, shortest_path_label = wrapped_ESPPRC()

# ESPP
wrapped_ESPP = wrapper(pylgrim.ESPP.DLA, G, source, min_K=1, max_path_len=max_path_len)
time_ESPP = timeit.timeit(wrapped_ESPP, number=1)
paths, costs = wrapped_ESPP()
node = target
path = paths[node][0]
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

    pos = nx.circular_layout(G)
    nx.draw(G, pos)
    edge_labels = nx.get_edge_attributes(G,'weight')
    for key in edge_labels:
        edge_labels[key] = round(edge_labels[key], 2)
    nx.draw_networkx_edge_labels(G, pos, edge_labels)
    nx.draw_networkx_labels(G, pos, labels=None, font_size=12, font_color='k', font_family='sans-serif', font_weight='normal', alpha=1.0)
    plt.show()
