# test using ESSPRC.
# Note: The results can be different compared to test_ESSP because here resources are taken into account.
import sqlite3
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pylgrim
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# optional keywords that should also work without using them
res_name = 'res_cost'
atts = {'weight', res_name}

# create test graph
G = nx.DiGraph(n_res=2)
pylgrim.tools.create_test_graph(G,add_nodes_to_0=True)
source = 0
print('Testing with {} nodes'.format(len(G)))
print('')

# move source in-edges to a new node
source_in = 'source_in'
pylgrim.tools.decouple_source(G, source, source_in=source_in, atts=atts)

#nx.draw_circular(G,with_labels=True)
#plt.show()

# solve using ESSPRC
#target = 4
target = source_in
max_res = list([1.0,1.0])
G_pre, res_min = pylgrim.ESPPRC.preprocess(G, source, target, max_res, res_name=res_name, atts=atts)
path, label = pylgrim.ESPPRC.GSSA(G_pre, source, target, max_res, res_min, res_name=res_name)
print('Resulting path:')
for p in range(0,len(path)):
    print('  ',path[p])
    if p < len(path)-1:
        print("      ⇩")
print('')
print('with cost 10^-({}) = {}'.format(label[0],10**(-label[0])))
print('')

# move source in-edges back from new node
pylgrim.tools.undecouple_source(G, source, source_in=source_in, atts=atts)

#nx.draw_circular(G,with_labels=True)
#plt.show()
