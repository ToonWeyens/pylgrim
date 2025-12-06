# Tools for pylgrim:
#   * decouple_source and undecouple_source to move all in-edges from a source node to a duplicate and vice versa.
#   * print_path to pretty print a path.
#   * count_elems to count the number of elements in a path and return a dictionary keyed with a label.
#   * print_dynamic_k to dynamically print K values as bars in the terminal.
#
# Author:
#   Toon Weyens

import logging
import sys
import shutil

#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def decouple_source(G, source, source_in="source_in"):
    """Decouple the source {source} of a graph {G}, by duplicating the node, called {source_in} and moving all the in-edges to it.
    Returns the number of edges displaced."""
    
    in_edges_source = tuple(G.in_edges(source))
    n_in_edges_source = len(in_edges_source)
    if n_in_edges_source > 0:
        logger.debug('displace {} in-edges ⇨ {}'.format(n_in_edges_source,source))
        
        for e in in_edges_source:
            logger.debug('  move edge {}'.format(e))
            G.add_edge(e[0],source_in)
            for attr in G[e[0]][e[1]]:
                G[e[0]][source_in][attr] = G[e[0]][e[1]][attr]
            G.remove_edge(*e)

    return n_in_edges_source


def undecouple_source(G, source, source_in="source_in"):
    """Invert the decoupling of the source {source} of a graph {G} done in decouple_source by moving all the edges to {source_in} back to {source}.
    Returns the number of edges displaced."""
    
    in_edges_source = tuple(G.in_edges(source_in))
    n_in_edges_source = len(in_edges_source)
    if n_in_edges_source > 0:
        logger.debug('place back {} in-edges {} - {}'.format(n_in_edges_source,source, in_edges_source))
        
        for e in in_edges_source:
            G.add_edge(e[0],source)
            for attr in G[e[0]][e[1]]:
                G[e[0]][source][attr] = G[e[0]][e[1]][attr]
            G.remove_edge(e[0],source_in)
        G.remove_node(source_in)

    return n_in_edges_source


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


# Unicode blocks representing 1/8th increments for high-resolution bars
_BLOCKS = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]


def print_dynamic_k(K, previous_lines_printed=0, label="K Values", div_factor=1):
    """
    Visualizes K by padding lines with physical spaces to overwrite old text.
    No weird ANSI reset codes.
    """
    
    # 1. Clear previous output
    if previous_lines_printed > 0:
        # Move cursor up
        sys.stdout.write(f"\033[{previous_lines_printed}F")

    sorted_nodes = sorted(K.keys())
    
    # Get current terminal width
    term_width = shutil.get_terminal_size((80, 20)).columns 
    
    # Reserve space for text like "Node XX: " and " (123)"
    # We subtract a bit extra to be safe from auto-wrapping
    max_bar_width = term_width - 25 
    
    max_val = max(K.values()) if K else 1
    if max_val == 0: max_val = 1
    
    lines_to_print = []
    
    # Header: Pad with spaces to fill the width
    header = f"--- {label} Monitor ---"
    padding = " " * (term_width - len(header) - 1)
    lines_to_print.append(header + padding)

    for n in sorted_nodes:
        val = K[n]
        
        # --- SCALING LOGIC ---
        val_scaled = val / div_factor

        # If scaled value fits, use it. If not, scale down relative to max.
        if (max_val / div_factor) > max_bar_width:
             display_val = (val_scaled / (max_val / div_factor)) * max_bar_width
        else:
            display_val = val_scaled

        # Build the bar
        full_blocks = int(display_val)
        remainder = int((display_val - full_blocks) * 8)
        bar = ("█" * full_blocks) + _BLOCKS[remainder]
        
        # --- THE FIX: MANUAL PADDING ---
        # 1. Build the content
        content = f"Node {n:>3}: {bar} ({val})"
        
        # 2. Calculate how many spaces we need to reach the edge of the terminal
        # We use -1 to ensure we don't accidentally trigger a newline wrap
        spaces_needed = term_width - len(content) - 1
        
        if spaces_needed > 0:
            padding = " " * spaces_needed
        else:
            padding = ""
            
        # 3. Append content + physical spaces
        lines_to_print.append(content + padding)

    # Print block
    sys.stdout.write("\n".join(lines_to_print) + "\n")
    sys.stdout.flush()

    return len(lines_to_print)