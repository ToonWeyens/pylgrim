# test using ESSP.
# Note: The results can be different compared to test_ESSPRC because here resources are not taken into account.
import networkx as nx
import matplotlib.pyplot as plt
import pylgrim
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

# solve for min_K number of paths
min_K = 2
pylgrim.ESPP.DLA(G, source, min_K, remove_excess_paths = True, max_path_len = 6)

# move source in-edges back from new node
pylgrim.tools.undecouple_source(G, source, source_in=source_in)

#nx.draw_circular(G,with_labels=True)
#plt.show()
