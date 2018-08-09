# Elementary Shortest Path Problem with or without Resource Constraint
This module solves the shortest elementary path problem, by which it is meant that each node in a path can only be visited once.
The edge weights do not need to be nonnegative.

A general algorithm to solve this problem works by solving the *k-paths* problem, i.e. by solving the nonelementary problem repeatedly and requiring that for the nodes that are present in nonelementary paths multiple (k) paths need to be found.
The resulting algorithm finds the elementary shortest paths (ESPP) from a **single source to all destinations** [1].
However, it can be very slow if very large graphs are considered.
Especially because the algorithm in [1] is intrinsically flawed and the fix for this makes it much less efficient than expected: See note in ESPP.py.

A more powerful algorithm can be used when additionally there are positive resources associated to each edge in the graph, though this requirement can be relaxed to nonnegative resources if not too many edges have zero resource cost associated to them.
The resulting Elementary Resource Constrained Shortest Path Problem (ESPPRC) can then be solved by an algorithm that starts by first preprocessing the graph [2].
During preprocessing, the graph is first pruned by discarding all nodes that cannot be reached from the origin or reach the target without violating the resource limits.
Subsequently, for each pair in the resulting pruned graph, the least-cost path is sought, which will be used later to incrase so-called *dominance* of paths by other paths.

After preprocessing, the ESPPRC is solved by introducing *node-resources* that count how many times a node has been used in a certain path, so that elementarity can be enforced.
As this problem can quickly become exponential in nature, it is critical that the numer of resource nodes that have to be introdcuced kept as low as possible.
In the algorithm this is done by using a two-fold dominance strategy:
On the one hand, paths are only added to the list of possible shortest possible paths, if their resource consumption is not dominated by another path.
Also, when a path is added, the other possible paths that are dominated by it, are discarded.
On the other hand, *strong dominance* is a mathematical trick that is used to speed up convergence to the shortest path, by artificially incrementing possible node resources of nodes that cannot be reached [2].
The resulting algorithm seeks the ESPPRC for **single source to single destination** problems.


## Installation
* Clone this repository
* `pip install -e pylgrim`

### Dependencies
* numpy
* networkx
* logging
* copy
* collections
* matplotlib (for testing)
* random (for testing)
* timeit (for testing)

## Usage

### Getting started
First of all, the directed graph ([`networkx.digraph`](https://networkx.github.io/documentation/stable/reference/classes/digraph.html)) `G` on which to use pylgrim needs to have a attribute `n_res` set through, for example
```python
G = nx.DiGraph(n_res=1)
```
or
```python
G.graph['n_res'] = 1
```
if the graph already exists.

Also, each of the graph edges should have an attribute `weight`, which is what will be minimized along the paths.

Furthermore,
```python
from pylgrim import tools
```
should be used to *decouple* the directed graph to make sure that the source node from which to calculate elementary shortest paths is certain not to have any in-edges, as this is not allowed by the algorithms:
```python
tools.decouple_source(G, source, source_in='source_in')
```
duplicates the `source` node to `source_in` and moves all the in-edges to the new node.
This operation happens in situ.

Afterwards, the graph can be reverted to its original state using
```python
tools.undecouple_source(G, source, source_in=`source_in`)
```

Apart from this,
```python
from pylgrim import Path
```
should be used to import the `Path` class that inherits from the `networkx.digraph` and that represents a path that can be cyclic, so it contains the information of source node.
Among other things, the class provides an iterator for the next edge in the path, pretty printing, etc.

Furthermore it is used to represent the solution path(s) from ESPP and ESPPRC.

### Elementary shortest path
Elementary shortest path can be used by first importing the module through
```python
from pylgrim import ESPP
```

The *Dynamic labelling algorithm* is implemented [1]:
```python
return paths, costs = DLA(G, source, min_K=1, output_pos = False, max_path_len = -1)
```
where `G` si the directed graph for which to find the shortest path from the `source` to all other nodes. 

Optionally, through `min_K` the minimum number of paths to be returned for every node can be changed, with `output_pos` also positive costs can be returned and through `max_path_len`, the maximum length of a path can be limited, so that the problem becomes easier to solve.

`DLA` outputs in `paths` a dictionary where the keys are the target nodes and for every one of these, a list is returned with the best paths of type `Path`, ordered by lowest cost, of length at least `min_K`. The cost itself is returned in a matching dictionary `costs`.

Note, however, that ESPP should no be used for graphs other than very small ones.
The following algorithm should be much faster.

### Elementary shortest path with resource constraints
Elementary shortest path with resource constraints can be used by first importing the module through
```python
from pylgrim import ESPPRC
```

The *General State Space Augmenting Algorithm*, `GSSA` is implemented [2]:
```python
best_path, best_path_label = GSSA(G, source, target, max_res, res_min, res_name='res_cost')
```
where `G` is the directed graph for which to find the shortest path between `source` and `target` subject to maximum resource usage given in `max_res`, the array of maximum resources that can be consumed on any path, where a value should be given for every resource.

Note, furthermore, the graph `G` must have been preprocessed first so that it is reduced and has the minimal resource information that is to be passed into `res_min`
```python
G_pre, res_min = ESSPRC.preprocess(G, source, target, max_res, res_name='res_cost')
```

Finally, in these functions, `res_name` can be used to specify the name of the resource that is to be used internally for the edges in the graph.

The output of `GSSA` is a `best_path` of the `Path` type and a corresponding `best_path_label` that is a 2-tuple with the first element equal to the cost of the best path and the second equal to the array of the resources consumed, less than or equal to `res_max`.

## Testing
* Run the tests in `/tests` using `python test_[NAME].py` where `[NAME]` is the name of the test.
* Plot(s) will appear as well as textual output.
* To debug, change `WARNING` to `INFO` or possibly `DEBUG` in `logging.basicConfig(level=logging.WARNING)` present at the top of the python files.


## References
[1] *On the shortest path problem with negative cost cycles* by Di Puglia Pugliese, Luigi (DOI: 10.1007/s10589-015-9773-1)

[2] *Accelerated label setting algorithms for the elementary resource constrained shortest path problem* by Boland, Natashia (DOI: 10.1016/j.orl.2004.11.011)

## Copyright
Copyright 2018 Toon Weyens, Daan van Vugt
