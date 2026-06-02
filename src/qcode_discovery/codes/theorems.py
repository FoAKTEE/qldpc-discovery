"""Numeric witnesses for the paper's two proved theorems.

Re-verify the ExactProof results of arXiv:2606.02418 against the construction kernel:
  - thm:ab_d2 (App. D): every BB code with A = B and k > 0 has d = 2 exactly.
  - lem:crt_k (App. C): the univariate code A=1+y+y^2, B=A(x^{l/3}) encodes k = 8l/3.
The d=2 witness is CONSTRUCTIVE (it exhibits the weight-2 logical from the proof),
not a search, so it certifies the theorem rather than one instance's distance. R2.
"""
from __future__ import annotations

import numpy as np

from ..algebra import gf2
from .bb_codes import BBCode
from .metrics import css_k


def verify_ab_d2(l: int, m: int, A) -> dict:
    """Construct the A=B code and exhibit the proof's weight-2 X-logical (Thm thm:ab_d2)."""
    code = BBCode(l, m, A, A)
    lm = l * m
    k = css_k(code.HX, code.HZ)
    # Find e_i not in rowspace(A): exists because k>0 => rank(A) < lm.
    witness_i = None
    for i in range(lm):
        e = np.zeros(lm, dtype=np.uint8)
        e[i] = 1
        if not gf2.in_rowspace(code.A, e):
            witness_i = i
            break
    v = np.zeros(code.n, dtype=np.uint8)
    if witness_i is not None:
        v[witness_i] = 1
        v[witness_i + lm] = 1
    in_ker_HZ = not bool(((code.HZ @ v) & 1).any())
    nontrivial = (witness_i is not None) and (not gf2.in_rowspace(code.HX, v))
    # d >= 2: every column of the stacked check matrix has weight >= 2.
    stacked = np.vstack([code.HX, code.HZ])
    min_col_weight = int(stacked.sum(axis=0).min())
    d_le_2 = in_ker_HZ and nontrivial          # exhibited a nontrivial weight-2 logical
    d_ge_2 = min_col_weight >= 2
    return {
        "l": l, "m": m, "n": code.n, "k": k,
        "witness_qubits": (witness_i, witness_i + lm) if witness_i is not None else None,
        "logical_weight": 2,
        "in_ker_HZ": in_ker_HZ, "nontrivial": nontrivial,
        "min_col_weight": min_col_weight,
        "d_le_2": d_le_2, "d_ge_2": d_ge_2,
        "d": 2 if (d_le_2 and d_ge_2 and k > 0) else None,
    }


def verify_crt_k(l: int, m: int) -> dict:
    """Construct the univariate code A=1+y+y^2, B=A(x^{l/3}) and check k = 8l/3 (Thm lem:crt_k)."""
    if l % 3 or m % 3:
        raise ValueError("lem:crt_k requires 3 | l and 3 | m")
    c = l // 3
    A = "1+y+y^2"
    B = f"1+x^{c}+x^{2 * c}"
    code = BBCode(l, m, A, B)
    k = css_k(code.HX, code.HZ)
    expected = 8 * l // 3
    return {"l": l, "m": m, "n": code.n, "k": k, "expected": expected, "match": k == expected}
