"""Exhaustive low-weight logical-operator enumeration (independent distance verifier).

Tier-1 of the paper's distance pipeline (arXiv:2606.02418 sec V.C): for small codes,
search all weight-w operators to certify d = w exactly. Here used as an INDEPENDENT
cross-check against the MILP solver (two-method agreement = the paper's 'trusted'
standard). O(C(n,w)) — intended for small n / small w only. R2.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np

from . import gf2


def _min_weight_one_type(check: np.ndarray, stab_rows: np.ndarray, n: int, max_weight: int):
    """Smallest weight of a nontrivial logical of one type, searching weights 1..max_weight.

    A candidate support set S gives x = 1_S; it is a logical iff check x = 0 (mod2)
    and x not in rowspace(stab_rows). Returns the weight, or None if none <= max_weight.
    """
    check = gf2.as_f2(check)
    for w in range(1, max_weight + 1):
        for combo in combinations(range(n), w):
            x = np.zeros(n, dtype=np.uint8)
            x[list(combo)] = 1
            if ((check @ x) & 1).any():
                continue
            if not gf2.in_rowspace(stab_rows, x):
                return w
    return None


def css_distance_enum(code, max_weight: int = 4):
    """Brute-force CSS distance up to max_weight. Returns dict d_X, d_Z, d, exhausted.

    'exhausted' is True if both types found a logical at or below max_weight (so d is
    exact); otherwise d is only a statement that d > max_weight on the unfound type.
    """
    n = code.n
    dX = _min_weight_one_type(code.HZ, code.HX, n, max_weight)   # X-logicals: ker(HZ)\rowspace(HX)
    dZ = _min_weight_one_type(code.HX, code.HZ, n, max_weight)   # Z-logicals: ker(HX)\rowspace(HZ)
    cand = [v for v in (dX, dZ) if v is not None]
    d = min(cand) if cand else None
    return {"d_X": dX, "d_Z": dZ, "d": d, "exhausted": (dX is not None and dZ is not None)}
