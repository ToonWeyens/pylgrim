# Tools.
#
# Author:
#   Toon Weyens

def print_path(path, max_path_len_for_print = None):
    """Pretty-print a path given as an iterable of strings.
    Optionally trim if longer than max_path_len_for_print
    """
    path_short = str(path[0])
    if max_path_len_for_print is None:
        max_path_len_for_print = len(path)
    if len(path) > max_path_len_for_print + 1:
        for p in range(1,max_path_len_for_print-1):
            path_short += ' ⇨ ' + str(path[p])
        path_short += ' ⇨  …  ⇨ ' + str(path[len(path)-1])
    else:
        for p in range(1,len(path)):
            path_short += ' ⇨ ' + str(path[p])
    return path_short

def count_elems(path):
    """Count elements in a path and return a dictionary keyed with label"""
    res = dict()
    for n in path:
        res[n] = res.get(n,0)+1
    return res
