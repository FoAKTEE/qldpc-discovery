"""Exact CSS code distance via mixed-integer linear programming (HiGHS / scipy).

Reproduces the Bravyi-et-al. / arXiv:2606.02418 SM formulation: the minimum-weight
X-logical anticommuting with the j-th Z-logical is

    min  sum_i x_i
    s.t. H_Z x = 0  (mod 2)          # commute with Z-stabilizers
         <x, Zbar_j> = 1 (mod 2)      # act as logical X on qubit j
         x_i in {0,1}

mod-2 constraints are linearized with nonnegative integer slacks (sum a_i x_i - 2 s = b).
d_X = min over the k Z-logical generators; d = min(d_X, d_Z). A logical is EXACT when
HiGHS proves optimality (MIP gap = 0). Paper anchor: arXiv:2606.02418 sec V.B + SM. R3.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

from .metrics import css_logicals


def _min_weight_logical(check: np.ndarray, target: np.ndarray, time_limit: float):
    """min |x| s.t. check x = 0 (mod2) and <x,target>=1 (mod2), x binary.

    Returns (weight, optimal) where optimal is True iff HiGHS proved MIP gap 0.
    """
    check = (np.asarray(check, np.int64) & 1)
    target = (np.asarray(target, np.int64) & 1)
    R, n = check.shape
    n_slack = R + 1                      # one slack per check row + one for anticommute
    V = n + n_slack
    c = np.concatenate([np.ones(n), np.zeros(n_slack)])

    # Equality rows: [check | -2 I | 0] = 0 ; [target | 0 | -2] = 1
    A = np.zeros((R + 1, V))
    A[:R, :n] = check
    for r in range(R):
        A[r, n + r] = -2
    A[R, :n] = target
    A[R, n + R] = -2
    rhs = np.concatenate([np.zeros(R), [1.0]])
    con = LinearConstraint(A, rhs, rhs)

    lb = np.zeros(V)
    ub = np.concatenate([np.ones(n), np.full(n_slack, n)])  # slacks bounded by n (safe)
    res = milp(
        c,
        integrality=np.ones(V),
        bounds=Bounds(lb, ub),
        constraints=[con],
        options={"time_limit": time_limit, "mip_rel_gap": 0.0},
    )
    if res.x is None:
        return None, False
    weight = int(round(res.x[:n].sum()))
    optimal = (res.status == 0)          # 0 = converged to proven optimum
    return weight, optimal


def _distance_one_type(check: np.ndarray, logicals: np.ndarray, time_limit: float, max_logicals):
    best = None
    exact = True
    used = logicals if max_logicals is None else logicals[:max_logicals]
    for z in used:
        w, opt = _min_weight_logical(check, z, time_limit)
        if w is not None:
            best = w if best is None else min(best, w)
        if not opt:
            exact = False
    if max_logicals is not None and max_logicals < len(logicals):
        exact = False
    return best, exact


def css_distance_milp(code, time_limit: float = 60.0, which: str = "both", max_logicals=None):
    """Exact (or upper-bound) CSS distance of a BBCode via MILP.

    which: 'X', 'Z', or 'both'. Returns dict with d, d_X, d_Z, exact, and the
    per-type optimality. For BB codes d_X = d_Z (involution symmetry).
    """
    X_log, Z_log = css_logicals(code.HX, code.HZ)
    out = {"d_X": None, "d_Z": None, "exact": True}
    if which in ("X", "both"):
        dX, eX = _distance_one_type(code.HZ, Z_log, time_limit, max_logicals)
        out["d_X"], out["exact"] = dX, out["exact"] and eX
    if which in ("Z", "both"):
        dZ, eZ = _distance_one_type(code.HX, X_log, time_limit, max_logicals)
        out["d_Z"], out["exact"] = dZ, out["exact"] and eZ
    cand = [v for v in (out["d_X"], out["d_Z"]) if v is not None]
    out["d"] = min(cand) if cand else None
    return out
