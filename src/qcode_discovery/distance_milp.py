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

from .metrics import css_logicals, symplectic_logicals


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
        options={"time_limit": time_limit, "mip_rel_gap": 0.0, "disp": False},
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


def _min_weight_symplectic(SX, SZ, Lj, n, time_limit):
    """min symplectic weight |{i: a_i or b_i}| over Pauli (a|b) that commutes with all
    stabilizers and anticommutes with logical Lj=(aL|bL). Returns (weight, optimal)."""
    SX = (np.asarray(SX, np.int64) & 1)
    SZ = (np.asarray(SZ, np.int64) & 1)
    aL = (np.asarray(Lj[:n], np.int64) & 1)
    bL = (np.asarray(Lj[n:], np.int64) & 1)
    R = SX.shape[0]
    V = 3 * n + R + 1                       # a(n) b(n) w(n) slacks(R) t(1)
    a0, b0, w0, s0, t0 = 0, n, 2 * n, 3 * n, 3 * n + R
    c = np.zeros(V)
    c[w0:w0 + n] = 1.0                       # minimize sum of symplectic-weight indicators

    # Equality block: commutation (SZ a + SX b - 2s = 0) and anticommute (bL.a + aL.b - 2t = 1).
    Aeq = np.zeros((R + 1, V))
    Aeq[:R, a0:a0 + n] = SZ
    Aeq[:R, b0:b0 + n] = SX
    for r in range(R):
        Aeq[r, s0 + r] = -2
    Aeq[R, a0:a0 + n] = bL
    Aeq[R, b0:b0 + n] = aL
    Aeq[R, t0] = -2
    rhs = np.concatenate([np.zeros(R), [1.0]])

    # OR encoding w_i = a_i v b_i : w>=a, w>=b, w<=a+b  (all as A x >= 0).
    I = np.eye(n)
    Aor = np.zeros((3 * n, V))
    Aor[0 * n:1 * n, w0:w0 + n] = I;  Aor[0 * n:1 * n, a0:a0 + n] = -I       # w - a >= 0
    Aor[1 * n:2 * n, w0:w0 + n] = I;  Aor[1 * n:2 * n, b0:b0 + n] = -I       # w - b >= 0
    Aor[2 * n:3 * n, a0:a0 + n] = I;  Aor[2 * n:3 * n, b0:b0 + n] = I
    Aor[2 * n:3 * n, w0:w0 + n] = -I                                        # a + b - w >= 0

    lb = np.zeros(V)
    ub = np.concatenate([np.ones(3 * n), np.full(R + 1, n)])
    res = milp(
        c,
        integrality=np.ones(V),
        bounds=Bounds(lb, ub),
        constraints=[LinearConstraint(Aeq, rhs, rhs), LinearConstraint(Aor, 0, np.inf)],
        options={"time_limit": time_limit, "mip_rel_gap": 0.0, "disp": False},
    )
    if res.x is None:
        return None, False
    weight = int(round(res.x[w0:w0 + n].sum()))
    return weight, (res.status == 0)


def symplectic_distance_milp(code, time_limit: float = 60.0, max_logicals=None):
    """Exact (or upper-bound) non-CSS distance of a PBBCode via symplectic-weight MILP.

    Minimizes symplectic weight over the 2k logical generators; d = min. exact iff every
    solved logical proves MIP gap = 0. Paper anchor: arXiv:2606.02418 SM non-CSS formulation. R3.
    """
    S, n = code.S, code.n
    SX, SZ = S[:, :n], S[:, n:]
    L = symplectic_logicals(S, n)
    used = L if max_logicals is None else L[:max_logicals]
    best, exact = None, True
    for Lj in used:
        w, opt = _min_weight_symplectic(SX, SZ, Lj, n, time_limit)
        if w is not None:
            best = w if best is None else min(best, w)
        if not opt:
            exact = False
    if max_logicals is not None and max_logicals < len(L):
        exact = False
    return {"d": best, "exact": exact, "n_logicals": len(L)}
