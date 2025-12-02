## Algorithms explained

### DLA with TLAdynK

This stands for **Dynamic Labeling Approach** (algorithm 4 in [1]) with **Truncated labelling algorithm for dynamic kSPP** (algorithm 3 in [1]).

Core idea:
- The strategy of the Dynamic Labeling Approach (DLA) can be thought of as an extension of the Bellman-Ford (BF) algorithm
- To deal with the fact that BF cannot handle negative sum cycles (NCC), DLA is able to use memory to store multiple paths per node, ranked by cost
- When the algorithm is considering extending a path to a neighboring node it can discard the NCCs and try another one of its paths
- This tradeoff between memory for the ability to bypass negative cost cycles and enforce elementarity comes at the cost of
  - increased compute: Need to iterate over more potential paths
  - increased memory: Need to store more paths
- It is therefore crucial to limit the number of potential paths to store at each node
- The DLA has a clever approach that handles this well: It starts with only allowing minimal memory and then selectively increases this per node when certain criteria are met, which will be explained below

Concepts:
- **Truncation**: We store up to $K_i$ paths maximum to get to each node $i$ from the source $s$ as $\pi_{si}^k$ with $k=0\ldots K_i$
- Every such path also has a cost associated $c(\pi_{si}^k)$ that is the sum of all the individual arc costs $\sum c_{ab}$ for the arcs in the path
- $K_i$ refers to the finite memory to store multiple paths to a node and is initialized at 1 for each node $i$ and then increased if required
- We try keeping it as low as possible to avoid an explosion in computational requirements
- We use a dynamic programing algorithm to explore new paths as extensions of the current end point of a path
- We keep track of all nodes that are still good candidates for extension in a list $L$

High level steps:
- Initialize the algorithm by setting $L=[s]$ and giving each node $i$ an infinite cost $c(\pi_{si}^k) = \infty$ for each path $k$.
- As we are in the first iteration the memory is of size $K_i=1$ for all nodes $i$
- Pop the first node in our list $L$, which is at this moment also the only node $s$ and explore its out-edges
- This first time all out-edges $i$ will automatically become the best paths $\pi_{si}^k$ currently available as they are the only such paths, and their cost will be equal to the cost $c_{si}$ of the arc between $s$ and $i$
- Every node that has its paths changed, i.e. all these $i$, are now also added to the list $L$
- Go through the first node on the list $L$ and start exploring its neighbors $v$
  - If $v$ can be reached from $u$ in an elementary way using one of the currently stored paths $\pi_{su}^k$ (i.e. $v \notin \pi_{su}^k$), we consider adding the new path $\pi_{sv}^{k'} = \pi_{su}^k + (u,v)$ to the list of paths to $v$
    - That is, if this new path has a cost $c(\pi_{sv}^{k'})$ that is better than the worst currently stored path to $v$ (i.e. $c(\pi_{sv}^{k'}) < c(\pi_{sv}^{K_v})$), we add it to the list of paths to $v$, evicting the worst path if necessary to keep only $K_v$ paths
    - We also add $v$ to the list $L$ to make sure we will explore it later
  - If we find out that with the current number of paths stored at $u$ we have no possible way to reach $v$ in an elementary way but consider the extension promising (see conditions below):
    - We increase $K_u$ by 1
    - We restart the algorithm with the new memory limit (see below for details)
  - We continue this process for all neighbors $v$ of $u$
- We then move on to the next node in the list $L$
- This continues until we have explored all nodes in the list $L$
- At this point, we have found the best elementary paths from $s$ to all other nodes

Increasing Memory $K_u$:
- Sometimes when we are considering extending to a neighbor $v$ from a node $u$ we realize that we cannot do this in an elementary way because $v$ is in all the paths $\pi_{su}^k$ stored currently at $u$
- However if the NCC is strong enough it might still be beneficial to try and bypass it by looking for other paths to $u$ that do not involve $v$, that can then be extended to $v$ in an elementary way
- To investigate this we would need to store at least one more path $\pi_{su}^k$ at node $u$
- We should use our judgement to only increase $K_u$ when it is really necessary, however, as this quickly increases the computational requirements of the algorithm because at worst it is proportional to $\mathcal{O} (n^2K^4)$
- Therefore we use a triple condition to decide when to increase $K_u$:
  - We have found a negative cycle (Condition 3 below)
  - We cannot avoid it using the current paths because every path we know involves this cycle (Condition 2 below)
  - We have no room left in memory to look for other paths that might bypass this cycle (Condition 1 below)
- More formally:
  1. **Saturation Check** - $c(\pi_{su}^k) < \infty, \forall k \in \{1, \dots, K_{u}\}$: There are no free slots in the memory for node $u$
  2. **Elementarity/Cycle Check** - $\nexists \hat{k} : v \notin \pi_{su}^{\hat{k}}$: Node $v$ is present in all currently stored paths to node $u$
  3. **Negative Cost Check** - $\exists \bar{k} : v \in \pi_{su}^{\bar{k}}$ such that $c(\pi_{su}^{\bar{k}}) + c_{uv} < c(\pi_{sv}^0)$: There exist a negative cost path better than current best path to $v$
- In this case we need to increase $K_l$ for each $l$ in the NCC that we just identified

Restarting the Algorithm with increased memory:
- We need to restart the algorithm when we increase the memory $K_l$ for all nodes $l$ that were part of the NCC
- However, we do not need to start working from scratch again. This is a major advantage of the DLA approach
- We can keep all the paths we have already found so far, as they are still valid
- We just need to make sure we re-explore the nodes that may be affected by the increased memory
- Therefore we add all the nodes in the NCC to the list $L$ to make sure we will re-explore them
- In practice we don't really need to even restart the algorithm, we can just continue from where we left off after adding the NCC nodes to $L$
