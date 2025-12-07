# Experiments and debugging notes

## ESPP dynamic-K reuse issue

Context: `tests/test_random.py` with the hard-coded `seed = -1213136599`, `graph_size = 15` and `max_path_len = 15` prints a warning because ESPPRC and ESPP disagree on the best path. ESPPRC finds the true optimum cost `-8.110616...`, while ESPP with `min_K=1` reports a suboptimal cost `-6.258301...`.

What happens:
- ESPP’s `DLA` reuses `paths/costs` across K bumps (commit `7f22451`). When an NCC is detected, K is incremented and empty slots are appended for the NCC nodes, and those nodes are re-enqueued.
- However, any alternative prefixes discarded when K was small are gone. The resume logic only extends the labels still stored; it never recreates the pruned prefixes.
- On this seed, the optimal path requires a second-best prefix to an intermediate node. With `min_K=1`, that prefix is discarded. Later K bumps leave the new slots empty; re-enqueuing nodes (even the source) can only regenerate the already-kept prefix, so the optimal path never appears.

Implication: Simply increasing K and re-queueing nodes is not sufficient when reusing state; correctness can be lost because discarded prefixes are unrecoverable.

Options suggested to fix while retaining reuse:
- Maintain a per-node backlog of candidate labels that were skipped only because the node was saturated. When K grows for that node, populate the new slots from the backlog and enqueue the node.
- Or rerun TLAdynK from scratch after a K increase (simpler, loses reuse but correct).

Key observation: Re-seeding `L` (including the source) without restoring discarded candidates does not recover the missing optimal path on this seed. A mechanism to bring back pruned prefixes is required.
