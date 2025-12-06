## Algorithms explained

### DLA with TLAdynK

This stands for **Dynamic Labeling Approach** [1, algorithm 4] with **Truncated labelling algorithm for dynamic kSPP** [1, algorithm 3].

#### Core idea
- The strategy of the Dynamic Labeling Approach (DLA) can be thought of as an extension of the Bellman-Ford (BF) algorithm
- To deal with the fact that BF cannot handle negative sum cycles (NCC), DLA uses memory to store multiple paths per node, ranked by cost
- When the algorithm is considering extending a path to a neighboring node, therefore, it can discard the NCCs and try another one of the paths in its memory
- If the memory is large enough this ensures that we can always bypass NCCs and still find the optimal elementary path
- However storing many paths per node comes at a steep cost:
  - increased compute: Need to iterate over more potential paths. In worst case this leads to $\mathcal{O} (n^2K^4)$ scaling [1, Lemma 2]
  - increased memory: Need to store more paths. This is not typically a problem
- It is therefore crucial to limit the memory of each each node
- The DLA handles this judiciously, starting with only allowing minimal memory for each node and lazily increases memory per node when NCCs are detected that cannot be bypassed with the current memory

#### Concepts
- **Path**: We consider paths from the source $s$ to a node $i$, denoted $\pi_{si}$ as the succession of individual arcs $(a,b)$ that connect $s$ to $i$
- **Truncation**: We store up to $K_i$ paths per node $i$ with $k=1\ldots K_i$, indicated by superscript $k$ as $\pi_{si}^k$ 
- **Cost**: Every such path also has a cost associated $c(\pi_{si}^k)$ that is the sum of all the individual arc costs $\sum c_{ab}$ for the arcs in the path
- **Dynamic programming**: We use a dynamic programming algorithm to explore new paths as extensions of the current end point of a path
- **Node list**: We keep track of all nodes that are still good candidates for extension in a list $L$
- **neighbor**: By neighbor we will consider all nodes that can be reached from a certain node, i.e. only out-edges

#### High level steps
- Initialization:
  - Set number of paths $K_i=1$ for all nodes $i$
  - Set cost $c(\pi_{si}^1) = \infty$ for (the only path $1$ in) node $i$, making sure that each path found will be lower in cost
  - Set $L=[s]$: We'll start exploring with the souce node $s$
- First iteration
  - Pop the first node in our list $L$, which is at this moment also the only node $s$ and explore its neighbors $i$
  - This first iteration all paths $\pi_{si}^k$ will automatically be best paths with cost equal to $c_{si}$
  - Add all nodes $i$ that have new paths found to the list $L$
- Subsequent iterations
  - Go through the first node $u$ on the list $L$
    - Start exploring its neighbors $v$
      - Iterate over all current paths $\pi_{su}^k$ to $u$ and see if we can extend any of them to $v$ in an elementary way (i.e. without creating a cycle)
        - If this new path $\pi_{sv}^{k'} = \pi_{su}^k + (u,v)$ is cheaper than the worst currently stored path to $v$ (i.e. $c(\pi_{sv}^{k'}) < c(\pi_{sv}^{K_v})$):
          - We add it to the list of paths to $v$
          - We evict the worst path if necessary to keep only $K_v$ paths
          - We also add $v$ to the list $L$ to make sure we will explore it later
        - If we detect a NCC when trying to extend to $v$:
          - If we can bypass it using another path to $u$ we just skip
          - If we cannot bypass it because we have run out of memory in $u$:
            - We increase $K_u$ by 1
            - We restart the algorithm with the new memory limit (see below for details)
      - We continue this process for all paths to $u$
    - We continue this process for all neighbors $v$ of $u$
  - We continue for all nodes in the list $L$
- At this point, we have found the best elementary paths from $s$ to all other nodes

#### Condition for increasing Memory $K_u$
- The algorithm deals with NCCs by taking the next possible path down the list of paths to a node stored in the memory
- However, when the memory is full and we still detect a NCC that cannot be bypassed, we need to increase the memory $K_u$ for some nodes $u$ in the NCC
- The criteria to determine this situation are as follows:
  - We have found a negative cycle
  - We cannot avoid it using the current paths because every path we know involves this cycle
  - We have no room left in memory to look for other paths that might bypass this cycle
- More formally (and in reverse order):
  1. **Saturation Check** - $c(\pi_{su}^k) < \infty, \forall k \in \{1, \dots, K_{u}\}$: There are no free slots in the memory for node $u$
  2. **Elementarity/Cycle Check** - $\nexists \hat{k} : v \notin \pi_{su}^{\hat{k}}$: Node $v$ is present in all currently stored paths to node $u$
  3. **Negative Cost Check** - $\exists \bar{k} : v \in \pi_{su}^{\bar{k}}$ such that $c(\pi_{su}^{\bar{k}}) + c_{uv} < c(\pi_{sv}^1)$: There exist a negative cost path better than current best path to $v$
- In this case we need to increase $K_l$ for each $l$ in the NCC that we just identified

Notes on condition 3, to make this crystal clear:
- Assuming condition 2 was met, we know that all paths to $u$ go through $v$
- If we denote this by $s \rightarrow A \rightarrow v \rightarrow B \rightarrow u$, which we are considering extending to $v$, forming a cycle $s \rightarrow A \rightarrow v \rightarrow B \rightarrow u \rightarrow v$
- We will now call $s \rightarrow A \rightarrow v$ a prefix of the path to $u$ and $s \rightarrow A \rightarrow v \rightarrow B \rightarrow u \rightarrow v$ the extended path to $v$
- The resulting situation is summarized in the following table:
    |                                                | Extended path is better than current best path to $v$ | Extended path is worse than current best path to $v$ |
    | ---------------------------------------------- | ----- | ----- |
    | current best path to $v$ is prefix             | NCC: We should increase $K$  | We can skip safely |
    | current best path to $v$ is better than prefix | Certainly NCC, as it was even able to overcome the advantage of path over prefix: We should increase $K$ | Might be a NCC that we can only detect with fair comparison, replacing prefix by best path to $v$. This will certainly happen as due the propagation mechanism of the algorithm, the node $v$ is waiting in the queue $L$: We can skip safely |
    | current best path to $v$ is worse than prefix  | Logical impossibility | Logical impossibility |
- The last row is a logical impossibility because:
  - It is possible for new paths to have been found to $v$ that have not yet ended up in $u$'s paths, but they would have been equal or better
  - All paths to $u$ that have gone through $v$ must necessarily be worse or equal to the best path to $v$
  

#### Restarting the Algorithm with increased memory
- We need to restart the algorithm when we increase the memory $K_l$ for all nodes $l$ that were part of the NCC
- However, we do not need to start working from scratch again. This is a major advantage of the DLA approach
- We can keep all the paths we have already found so far, as they are still valid
- We just need to make sure we re-explore the nodes that may be affected by the increased memory
- Therefore we add all the nodes in the NCC to the list $L$ to make sure we will re-explore them
- In practice we don't really need to even restart the algorithm, we can just continue from where we left off after adding the NCC nodes to $L$


## References
[1] Di Puglia Pugliese, L. (2015). *On the shortest path problem with negative cost cycles*. DOI: 10.1007/s10589-015-9773-1

[2] Boland, N., et al. (2006). *Accelerated label setting algorithms for the elementary resource constrained shortest path problem*. DOI: 10.1016/j.orl.2004.11.011

## Copyright
Copyright 2018-2025 Toon Weyens, Daan van Vugt