"""Tanner-graph structure: connectivity and decomposability (direct-sum detection).

A code whose combined (H_X, H_Z) Tanner graph disconnects into independent
components is a DIRECT SUM of sub-codes and offers no error-correction advantage
over them (arXiv:2606.02418 sec VI.A). The pipeline uses this to exclude codes
like the [[288,24,12]] = [[144,12,12]] (+) [[144,12,12]]. Union-find, no external
graph dependency. R2.
"""
from __future__ import annotations

import numpy as np


class _UnionFind:
    """Disjoint-set with path halving; used to count Tanner-graph qubit components."""

    def __init__(self, size: int):
        self.parent = list(range(size))

    def find(self, a: int) -> int:
        """Representative of a's set (with path halving)."""
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]
            a = self.parent[a]
        return a

    def union(self, a: int, b: int) -> None:
        """Merge the sets containing a and b."""
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def qubit_components(HX: np.ndarray, HZ: np.ndarray) -> int:
    """Number of connected components on the qubit set of the combined Tanner graph.

    Qubits and check-vertices are nodes; an edge joins a check to each qubit in its
    support. Two qubits are in the same component iff a path of shared checks links
    them. Returns the count of distinct qubit components.
    """
    HX = (np.asarray(HX, np.uint8) & 1)
    HZ = (np.asarray(HZ, np.uint8) & 1)
    n = HX.shape[1]
    checks = np.vstack([HX, HZ])
    uf = _UnionFind(n)
    for row in checks:
        support = np.flatnonzero(row)
        for q in support[1:]:
            uf.union(int(support[0]), int(q))
    roots = {uf.find(q) for q in range(n)}
    return len(roots)


def is_decomposable(code) -> bool:
    """True iff the code's Tanner graph splits into >= 2 qubit components (direct sum)."""
    return qubit_components(code.HX, code.HZ) > 1
