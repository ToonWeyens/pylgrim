# test using ESSPRC.
# Note: The results can be different compared to test_ESSP because here resources are taken into account.
import networkx as nx
import matplotlib.pyplot as plt
import pylgrim
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# optional keywords that should also work without using them
res_name = 'res_cost'

# create test graph
G = nx.DiGraph(n_res=2)
pylgrim.tools.create_test_graph(G,add_nodes_to_0=True)
source = 0
print('Testing with {} nodes'.format(len(G)))
print('')

# move source in-edges to a new node
source_in = 'source_in'
pylgrim.tools.decouple_source(G, source, source_in=source_in)

#nx.draw_circular(G,with_labels=True)
#plt.show()

# solve using ESSPRC
#target = 4
target = source_in
max_res = list([1.0,1.0])
G_pre, res_min = pylgrim.ESPPRC.preprocess(G, source, target, max_res, res_name=res_name)
shortest_path, shortest_path_label = pylgrim.ESPPRC.GSSA(G_pre, source, target, max_res, res_min, res_name=res_name)

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

# move source in-edges back from new node
pylgrim.tools.undecouple_source(G, source, source_in=source_in)

#nx.draw_circular(G,with_labels=True)
#plt.show()
