# test using ESPP on a simple test graph.
# Note: The results can be different compared to test_ESPPRC because here resources are not taken into account.
import pylgrim
import logging
import tools as testtools

# possible values are: WARNING, INFO, DEBUG, ...
# (see https://docs.python.org/3/library/logging.html#logging-levels)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def test_ESPP_run():
    # create test graph
    # G = testtools.create_test_graph(add_nodes_to_0=True)
    G = testtools.create_test_graph(add_nodes_to_0=False)
    source = 0
    print('Testing with {} nodes'.format(len(G)))
    print('')

    # move source in-edges to a new node
    source_in = 'source_in'
    pylgrim.tools.decouple_source(G, source, source_in=source_in)

    # solve for min_K number of paths
    min_K = 1
    paths, costs = pylgrim.ESPP.DLA(G, source, min_K, log_summary=True)

    print('solution paths:')
    for node in paths:
        print('    ending in node {}:'.format(node))
        for path in paths[node]:
            print('        '+str(path)+' with cost '+str(costs[node][paths[node].index(path)]))
            
            # visualize
            # testtools.visualize_path(G, path)

    # move source in-edges back from new node
    pylgrim.tools.undecouple_source(G, source, source_in=source_in)


if __name__ == "__main__":
    test_ESPP_run() 