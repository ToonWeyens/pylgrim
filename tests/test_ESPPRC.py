# test using ESSPRC on the simple test graph.
# Note: The results can be different compared to test_ESSP because here resources are taken into account.
import networkx as nx
import matplotlib.pyplot as plt
import pylgrim
import logging
import tools as testtools

# possible values are: WARNING, INFO, DEBUG, ...
# (see https://docs.python.org/3/library/logging.html#logging-levels)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# optional keywords that should also work without using them
res_name = 'res_cost'

# create test graph
G = testtools.create_test_graph(add_nodes_to_0=True)
source = 0
print('Testing with {} nodes'.format(len(G)))
print('')

# move source in-edges to a new node
source_in = 'source_in'
pylgrim.tools.decouple_source(G, source, source_in=source_in)

# profiling: use `python -m cProfile -o test_ESPPRC.prof test_ESPPRC.py`,
# followed, for example, by opening up a python notebook and running
#   import pstats
#   p = pstats.Stats('test_ESPPRC.prof')
#   p.sort_stats('cumtime')
#   p.print_stats(100)
profiling = False

if profiling:
    n_runs = 100
else:
    n_runs = 1

for _ in range(n_runs):
    # solve using ESSPRC
    #target = 4
    target = source_in
    max_res = list([1.0,1.0])
    G_pre, res_min = pylgrim.ESPPRC.preprocess(G, source, target, max_res, res_name=res_name)
    shortest_path, shortest_path_label = pylgrim.ESPPRC.GSSA(G_pre, source, target, max_res, res_min, res_name=res_name)

    if profiling:
        continue
    
    print('shortest path found: {} with label {}'.format(shortest_path, shortest_path_label))
    print('')

    while True:
        try:
            e = shortest_path.__next__()
            print('{} ⇨ {} : {}'.format(*e))
            print('')
        except StopIteration:
            # last element reached
            break

# visualize
#testtools.visualize_path(G, shortest_path)

# move source in-edges back from new node
pylgrim.tools.undecouple_source(G, source, source_in=source_in)
