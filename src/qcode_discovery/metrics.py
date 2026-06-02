"""Code parameters: encoding dimension k (via GF(2) rank), logical operators, FOM.

k = n - rank(H_X) - rank(H_Z) (= 2lm - 2 rank(H_X) for BB codes, since the
involution x->x^-1,y->y^-1 gives rank(H_X)=rank(H_Z)). FOM = k d^2 / n.
Paper anchor: arXiv:2606.02418 sec II.A, II.C. R2.
"""
from __future__ import annotations

import numpy as np

from . import gf2


def css_k(HX: np.ndarray, HZ: np.ndarray) -> int:
    """Encoding dimension of a CSS code with checks H_X, H_Z (n columns each)."""
    n = HX.shape[1]
    return n - gf2.rank(HX) - gf2.rank(HZ)


def _independent_mod(span_basis: np.ndarray, candidates: np.ndarray) -> np.ndarray:
    """Subset of candidate rows that are independent modulo the span of span_basis."""
    cur = span_basis.copy()
    r0 = gf2.rank(cur) if cur.size else 0
    chosen = []
    for v in candidates:
        stacked = np.vstack([cur, v.reshape(1, -1)]) if cur.size else v.reshape(1, -1)
        r1 = gf2.rank(stacked)
        if r1 > r0:
            chosen.append(v.copy())
            cur, r0 = stacked, r1
    width = candidates.shape[1] if candidates.size else (span_basis.shape[1] if span_basis.size else 0)
    return np.array(chosen, dtype=np.uint8) if chosen else np.zeros((0, width), np.uint8)


def css_logicals(HX: np.ndarray, HZ: np.ndarray):
    """Return (X_logicals, Z_logicals): bases of length-n logical-operator representatives.

    Z-logicals lie in ker(H_X) modulo rowspace(H_Z); X-logicals in ker(H_Z) mod rowspace(H_X).
    Each returned as rows over F(2). |X_logicals| = |Z_logicals| = k.
    """
    Z = _independent_mod(gf2.row_reduce_basis(HZ), gf2.nullspace(HX))
    X = _independent_mod(gf2.row_reduce_basis(HX), gf2.nullspace(HZ))
    return X, Z


def fom(n: int, k: int, d: int) -> float:
    """Figure of merit k d^2 / n (gross code [[144,12,12]] -> 12.0)."""
    return k * d * d / n
