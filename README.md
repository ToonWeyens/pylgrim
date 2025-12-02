# Elementary Shortest Path Problem with or without Resource Constraint
This module solves the shortest elementary path problem, by which it is meant that each node in a path can only be visited once.
The edge weights do not need to be nonnegative.

Two main algorithms are provided:
1.  **ESPP (`DLA`)**: Solves the Elementary Shortest Path Problem from a single source to all other nodes. This algorithm is based on solving the *k-paths* problem repeatedly [1].
2.  **ESPPRC (`GSSA`)**: Solves the Elementary Shortest Path Problem with Resource Constraints from a single source to a single target. This uses a two-phase approach: preprocessing and state-space augmentation [2]. This is the recommended algorithm for most use cases.

## Installation
*   **PyPI**: `pip install pylgrim`
*   **From source** (recommended with `uv`):
    *   Clone this repository
    *   `uv sync --group dev` (installs runtime + dev/test deps)
    *   `uv run python -m pylgrim` or `uv run python your_script.py`

**Requirements:**
*   Python >= 3.11
*   NetworkX
*   NumPy

## Usage

### Getting Started: Graph Preparation
Before running any algorithm, your `networkx.DiGraph` must be prepared.

1.  **Set Number of Resources**: The graph must have a `n_res` attribute specifying the number of resources.
    ```python
    import networkx as nx

    G = nx.DiGraph(n_res=1)
    # or if the graph already exists:
    # G.graph['n_res'] = 1
    ```

2.  **Define Edge Attributes**:
    *   `weight`: All edges must have a `weight` attribute, representing the cost to be minimized.
    *   `res_cost` (for ESPPRC): For the resource-constrained algorithm, each edge must also have a `res_cost` attribute. This must be a **list or NumPy array** of length `n_res`.

3.  **Decouple the Source Node**: The algorithms require that the source node has no incoming edges. The `tools.decouple_source` function handles this by creating a temporary duplicate of the source node and redirecting all in-edges to it. This operation is done in-place.
    ```python
    from pylgrim import tools

    source_node = 'A'
    temp_source_in = 'source_in' # Temporary node name
    tools.decouple_source(G, source_node, source_in=temp_source_in)
    ```
    After finding a path, you can revert the graph to its original state:
    ```python
    tools.undecouple_source(G, source_node, source_in=temp_source_in)
    ```

### Recommended: Elementary Shortest Path with Resource Constraints (ESPPRC)
This algorithm finds the shortest path between a **single source and single target** while respecting resource limits. It is a two-step process.

First, import the necessary modules:
```python
from pylgrim import ESPPRC, tools
import networkx as nx
import numpy as np
```

**Step 1: Preprocessing**
The `ESPPRC.preprocess` function prunes the graph, discarding nodes that cannot be part of a valid path (e.g., due to resource limits) and pre-calculates minimal resource paths. This is a mandatory first step.

**Step 2: GSSA Algorithm**
The `ESPPRC.GSSA` (General State Space Augmenting) algorithm then searches the preprocessed graph for the optimal path.

#### Complete Example:
```python
from pylgrim import ESPPRC, tools
import networkx as nx
import numpy as np

# 1. Create a directed graph with resource information
G = nx.DiGraph(n_res=1)
edges = [
    ('A', 'B', {'weight': 1, 'res_cost': [1]}),
    ('B', 'C', {'weight': 1, 'res_cost': [1]}),
    ('A', 'D', {'weight': 0, 'res_cost': [3]}),
    ('D', 'C', {'weight': 3, 'res_cost': [1]}),
]
G.add_edges_from(edges)

source, target = 'A', 'C'
max_res = np.array([3]) # Maximum resource consumption allowed

# 2. Decouple the source node
temp_source_in = 'source_in'
tools.decouple_source(G, source, source_in=temp_source_in)

# 3. Preprocess the graph
# This returns a reduced graph and minimum resource costs.
G_reduced, res_min = ESPPRC.preprocess(
    G, source, target, max_res, res_name='res_cost'
)

# 4. Run the GSSA algorithm
best_path, best_path_label = ESPPRC.GSSA(
    G_reduced, source, target, max_res, res_min, res_name='res_cost'
)

# 5. Process the result
if best_path:
    print(f"Shortest path found: {best_path}")
    print(f"Cost: {best_path_label[0]}")
    print(f"Resources consumed: {best_path_label[1]}")

    # The 'best_path' object is a pylgrim.Path, which can be iterated over
    print("Edges in path:")
    for u, v, data in best_path.edges(data=True):
        print(f"  - ({u} -> {v}), Weight: {data['weight']}")
else:
    print("No path found.")

# Expected output:
# Shortest path found: A -> B -> C
# Cost: 2
# Resources consumed: [2]
# Edges in path:
#   - (A -> B), Weight: 1
#   - (B -> C), Weight: 1
```

### Advanced Usage: Finding a Tour/Cycle
You can use the ESPPRC algorithm to find a shortest path that **returns to the origin** (a tour or cycle). To do this, set the `target` of the `GSSA` function to the temporary `source_in` node created by `decouple_source`.

```python
# To find a path from 'A' back to 'A'
# The target is the temporary node created during decoupling
tour_target = temp_source_in 

# Preprocess and run GSSA as before, but with the new target
G_reduced_tour, res_min_tour = ESPPRC.preprocess(G, source, tour_target, max_res)
tour_path, tour_label = ESPPRC.GSSA(G_reduced_tour, source, tour_target, max_res, res_min_tour)

if tour_path:
    print(f"Shortest tour found: {tour_path}")
```


### Legacy: Elementary Shortest Path (ESPP)
This algorithm finds the shortest elementary paths from a **single source to all other nodes**. Due to its performance issues and the flaw described above, its use is discouraged for all but very small graphs.

```python
from pylgrim import ESPP

# Ensure graph is decoupled as shown above
paths, costs = ESPP.DLA(G, source)

# 'paths' is a dictionary mapping target nodes to a list of Path objects
for destination, path_list in paths.items():
    print(f"Paths to {destination}:")
    for p in path_list:
        print(f"  - Path: {p}, Cost: {p.get_cost()}")
```

## The `Path` Object
Both algorithms return results using the `pylgrim.Path` class, which inherits from `networkx.DiGraph`. It provides useful methods for inspecting the path, such as:
*   `path.edges(data=True)`: Iterate over edges and their data.
*   `path.get_cost()`: Get the total cost (sum of `weight` attributes).
*   Pretty-printing via `str(path)`.


## Testing
* With uv (recommended): `uv run pytest`
* With pip: install dev deps yourself (`matplotlib`, `pytest`) and run `pytest`.
* Plots may be generated during tests. To debug, change `logging.WARNING` to `INFO` or `DEBUG` at the top of the relevant Python files.

## Algorithms explained
See the full explanation of the DLA with TLAdynK algorithm and other details in [Algorithms Explained](./algorithms_explained.md]]).

## References
[1] Di Puglia Pugliese, L. (2015). *On the shortest path problem with negative cost cycles*. DOI: 10.1007/s10589-015-9773-1

[2] Boland, N., et al. (2006). *Accelerated label setting algorithms for the elementary resource constrained shortest path problem*. DOI: 10.1016/j.orl.2004.11.011

## Copyright
Copyright 2018-2025 Toon Weyens, Daan van Vugt
