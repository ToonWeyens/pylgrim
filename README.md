# Elementary Shortest Path Problem with or without Resource Constraint
This module solves the shortest elementary path problem, by which it is meant that each node in a path can only be visited once.
The edge weights do not need to be nonnegative.

A general algorithm to solve this problem works by solving the *k-paths* problem, i.e. by solving the nonelementary problem repeatedly and requiring that for the nodes that are present in nonelementary paths multiple (*k*) paths need to be found.
The resulting algorithm finds the elementary shortest paths (ESPP) from a **single source to all destinations** [1].
However, it can be very slow if very large graphs are considered.

A more powerful algorithm can be used when additionally there are positive resources associated to each edge in the graph, though this requirement can be relaxed to nonnegative resources if not too many edges have zero resource cost associated to them.
The resulting Elementary Resource Constrained Shortest Path Problem (ESPPRC) can then be solved by the following algorithm that starts by first preprocessing the graph [2].
During preprocessing, the graph is first pruned by discarding all nodes that cannot be reached from the origin or reach the target without violating the resource limits.
Subsequently, for each pair in the resulting pruned graph, the least-cost path is sought, which will be used later to incrase so-called *dominance* of paths by other paths.

After preprocessing, the ESPPRC is solved by introducing *node-resources* that count how many times a node has been used in a certain path, so that elementarity can be enforced.
As this problem can quickly become exponential in nature, it is critical that the numer of resource nodes that have to be introdcuced kept as low as possible.
In the algorithm this is done by using a two-fold dominance strategy:
On the one hand, paths are only added to the list of possible shortest possible paths, if their resource consumption is not dominated by another path.
Also, when a path is added, the other possible paths that are dominated by it, are discarded.
On the other hand, *strong dominance* is a mathematical trick that is used to speed up convergence to the shortest path, by artificially incrementing possible node resources of nodes that cannot be reached [2].
The resulting algorithm seaks the ESPPRC for **single source to single destination** problems.

## References
   [1]: "On the shortest path problem with negative cost cycles" by Di Puglia Pugliese, Luigi (DOI: 10.1007/s10589-015-9773-1)
   [2]: "Accelerated label setting algorithms for the elementary resource constrained shortest path problem" by Boland, Natashia (DOI: 10.1016/j.orl.2004.11.011)


## Installation
* Clone this repository
* `pip install -e pylgrim`

### Dependencies
* networkx
* numpy

## Usage
```python
from pylgrim import ESPPRC
from pylgrim import ESPP
```


## Testing
TODO


## Changelog

V0.1:
* Changed K to dictionary to be compatible with general grids that might have non-integer node labels.

V0.2:
* Put ESSP in separate module.

v0.3:
* Improved output of results.
* Added possible flag "output_pos" to also output positive paths.
* Added option to trim paths when more than K are found. This is off by default. It can be turned on when the graphs are getting too large.
* Added restore of nodes to G at end of ESPP.
* Added option to retry paths in ESPP.
* Implemented pre-processing of ESPPRC.
* Started with rest of ESPPRC.

v0.4:
* Implemented ESPPRC.
* Many bugfixes.
* Updated test_ESPPRC.

v0.5:
* Migrated ESPP ESPPRC to Pylgrim and tests elsewhere.

v0.6:
* Logging is much better now.
* Migrated tests back and adapted them.
* "path_tools" now is renamed to "tools" and contains three new tools: two to decouple the source and back, and one to create a test graph.

v0.7:
* Changed names of routines.
* "decouple_source" and "undecouple_source" now give back the number of edges displaced.

## Copyright
Copyright 2018 Toon Weyens, Daan van Vugt
