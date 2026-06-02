"""GF(2) linear algebra primitives, built from scratch.

Everything operates on numpy uint8 arrays whose entries are 0/1, interpreted
mod 2.  We implement row reduction (Gaussian elimination over F2), rank, a
basis for the row space, and a basis for the (right) null space.

These are the bedrock of the whole discovery: code dimension k and the logical
operator subspaces are all defined in terms of ranks and null spaces over F2.
"""

from __future__ import annotations

import numpy as np


def _as_f2(M) -> np.ndarray:
    """Coerce to a 2-D uint8 array with entries in {0,1}."""
    A = np.asarray(M, dtype=np.uint8) & 1
    if A.ndim == 1:
        A = A.reshape(1, -1)
    return A.copy()


def row_reduce(M):
    """Reduced row echelon form over F2.

    Returns (R, pivots) where R is the RREF matrix (uint8) and ``pivots`` is the
    list of pivot column indices in order.  Pure F2 Gaussian elimination: the
    only arithmetic is XOR.
    """
    R = _as_f2(M)
    nrows, ncols = R.shape
    pivots = []
    r = 0
    for c in range(ncols):
        if r >= nrows:
            break
        # find a row at or below r with a 1 in column c
        pivot_row = -1
        for i in range(r, nrows):
            if R[i, c]:
                pivot_row = i
                break
        if pivot_row == -1:
            continue
        # swap into place
        if pivot_row != r:
            R[[r, pivot_row]] = R[[pivot_row, r]]
        # eliminate this column from every other row (XOR)
        for i in range(nrows):
            if i != r and R[i, c]:
                R[i, :] ^= R[r, :]
        pivots.append(c)
        r += 1
    return R, pivots


def rank(M) -> int:
    """F2 rank = number of pivots in RREF."""
    A = _as_f2(M)
    if A.size == 0:
        return 0
    _, pivots = row_reduce(A)
    return len(pivots)


def row_space_basis(M):
    """Basis (rows) for the row space of M over F2 = nonzero RREF rows."""
    R, pivots = row_reduce(M)
    return R[: len(pivots)].copy()


def null_space(M):
    """Basis for the right null space {x : M x = 0 (mod 2)} over F2.

    Standard RREF construction: free columns give basis vectors.  Returned as a
    matrix whose ROWS are the basis vectors (shape (nullity, ncols)).
    """
    A = _as_f2(M)
    nrows, ncols = A.shape
    R, pivots = row_reduce(A)
    pivot_set = set(pivots)
    free_cols = [c for c in range(ncols) if c not in pivot_set]
    basis = []
    # map pivot column -> the RREF row index that owns it
    pivot_row_of_col = {c: i for i, c in enumerate(pivots)}
    for fc in free_cols:
        v = np.zeros(ncols, dtype=np.uint8)
        v[fc] = 1
        # for each pivot row, its pivot column entry must satisfy the equation:
        # pivot_var + sum(free entries in that row) = 0  -> pivot_var = R[row, fc]
        for c in pivots:
            row = pivot_row_of_col[c]
            v[c] = R[row, fc]
        basis.append(v)
    if not basis:
        return np.zeros((0, ncols), dtype=np.uint8)
    return np.array(basis, dtype=np.uint8)


def in_row_space(v, M) -> bool:
    """Is vector v in the F2 row space of M?  Test via rank invariance."""
    M = _as_f2(M)
    v = _as_f2(v).reshape(1, -1)
    if M.shape[0] == 0:
        return not v.any()
    stacked = np.vstack([M, v])
    return rank(stacked) == rank(M)


def matmul_f2(A, B):
    """Matrix product over F2."""
    A = _as_f2(A)
    B = _as_f2(B)
    return (A.astype(np.int64) @ B.astype(np.int64)) & 1
