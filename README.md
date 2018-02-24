# Elementary Shortest Path Problem with Resource Constraint
This module solves the shortes path problem with constraints.
A version for solving without constraints (ESPP) is also included.

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

## Copyright
Copyright 2018 Toon Weyens, Daan van Vugt
