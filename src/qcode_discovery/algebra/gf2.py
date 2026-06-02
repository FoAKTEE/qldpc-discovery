"""GF(2) linear algebra primitives (rank, RREF, null space, row-space membership).

Foundation for every kernel verifier in this package: k computation, logical-operator
bases, MILP/enumeration distance, and the theorem witnesses all reduce to F(2) linear
algebra. Pure numpy (no galois/sympy dependency) — KISS for the load-bearing layer.
R0.
"""
from __future__ import annotations

import numpy as np


def as_f2(M) -> np.ndarray:
    """Coerce to a uint8 array reduced mod 2."""
    return (np.asarray(M, dtype=np.uint8) & 1)


def rref(M):
    """Reduced row-echelon form over F(2). Returns (R, pivot_columns)."""
    R = as_f2(M).copy()
    if R.ndim != 2:
        raise ValueError("rref expects a 2-D matrix")
    n_rows, n_cols = R.shape
    pivots: list[int] = []
    r = 0
    for c in range(n_cols):
        piv = None
        for i in range(r, n_rows):
            if R[i, c]:
                piv = i
                break
        if piv is None:
            continue
        if piv != r:
            R[[r, piv]] = R[[piv, r]]
        col = R[:, c].astype(bool).copy()
        col[r] = False  # do not eliminate the pivot row from itself
        if col.any():
            R[col] ^= R[r]
        pivots.append(c)
        r += 1
        if r == n_rows:
            break
    return R, pivots


def rank(M) -> int:
    """F(2) rank."""
    M = as_f2(M)
    if M.size == 0:
        return 0
    _, pivots = rref(M)
    return len(pivots)


def nullspace(M) -> np.ndarray:
    """Basis (one vector per row) of the right null space {x : M x = 0} over F(2)."""
    M = as_f2(M)
    if M.ndim != 2:
        raise ValueError("nullspace expects a 2-D matrix")
    n_cols = M.shape[1]
    R, pivots = rref(M)
    pivot_set = set(pivots)
    free_cols = [c for c in range(n_cols) if c not in pivot_set]
    basis = np.zeros((len(free_cols), n_cols), dtype=np.uint8)
    for k, f in enumerate(free_cols):
        basis[k, f] = 1
        for row_i, piv_c in enumerate(pivots):
            if R[row_i, f]:
                basis[k, piv_c] = 1
    return basis


def in_rowspace(M, v) -> bool:
    """True iff vector v lies in the F(2) row space of M."""
    M = as_f2(M)
    v = as_f2(v).reshape(1, -1)
    if M.size == 0:
        return not bool(v.any())
    return rank(M) == rank(np.vstack([M, v]))


def row_reduce_basis(M) -> np.ndarray:
    """A basis (independent rows) of the F(2) row space of M."""
    M = as_f2(M)
    if M.size == 0:
        return np.zeros((0, M.shape[1] if M.ndim == 2 else 0), dtype=np.uint8)
    R, pivots = rref(M)
    return R[: len(pivots)].copy()
