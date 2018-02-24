# Tools.
#
# TODO:
#   add license.
#
# Author:
#   Toon Weyens

# prints a path with pretty formatting
def print_path(path, max_path_len_for_print = 4):
    # it depends on whether we trim or not
    path_short = str(path[0])
    if len(path) > max_path_len_for_print + 1:
        for p in range(1,max_path_len_for_print-1):
            path_short += ' ⇨ ' + str(path[p])
        path_short += ' ⇨  …  ⇨ ' + str(path[len(path)-1])
    else:
        for p in range(1,len(path)):
            path_short += ' ⇨ ' + str(path[p])
    return path_short

# counts elements in a path and returns them in a dictionary
def count_elems(path):
    res = dict()
    for n in path:
        res[n] = res.get(n,0)+1
    return res
