"""Certify a LOWER BOUND d >= T for a CSS code via MILP infeasibility.

Idea: a nontrivial X-logical is x with H_Z x = 0 (mod2) and <dual_j, x>=1 for
some dual rep j.  d_X = min over such x of |x|.  To PROVE d_X >= T it suffices to
show, for every dual rep j, that the system

    H_Z x = 0 (mod 2)            [integer slacks]
    <dual_j, x> = 1 (mod 2)
    sum(x) <= T-1

is INFEASIBLE.  HiGHS returning status==2 (infeasible) is a rigorous certificate
(no logical of that type lighter than T exists).  This is a pure feasibility
query with a tight weight cap, which HiGHS often resolves far faster than the
full minimisation.  We do it for both types; if every sub-problem is infeasible,
d >= T is certified.  If any is feasible (status 0 with a solution), we have an
explicit logical of weight <= T-1, so d <= that weight (an upper bound witness).

This complements distance_milp: distance_milp tries to find the exact value;
this routine cheaply CERTIFIES d >= T which is exactly what 'd>=10' needs.
"""
import sys
import time

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

from qcode import bb, distance
from qcode.distance import _logical_basis


def _type_geq_T(Hperp, Hstab, T, time_limit, deadline):
    """Return ('certified', None) if d_type >= T proven; ('witness', (w,x)) if a
    logical of weight w<=T-1 found; ('unknown', None) if a subproblem timed out
    without resolving."""
    n = Hperp.shape[1]
    dual_reps, _ = _logical_basis(Hstab, Hperp)
    if dual_reps.shape[0] == 0:
        return ("certified", None)  # k=0, no logicals -> vacuously d>=T
    Hperp = np.asarray(Hperp, dtype=np.int64)
    nr = Hperp.shape[0]
    import time as _t
    all_infeasible = True
    for j in range(dual_reps.shape[0]):
        if deadline is not None and _t.time() > deadline:
            return ("unknown", None)
        dvec = dual_reps[j].astype(np.int64)
        n_slack = nr + 1
        nvar = n + n_slack
        c = np.zeros(nvar)            # feasibility: no real objective (min sum x)
        c[:n] = 1.0
        lb = np.zeros(nvar); ub = np.ones(nvar); ub[n:] = np.inf
        bounds = Bounds(lb, ub)
        integrality = np.ones(nvar)
        rows = []; lo = []; hi = []
        for i in range(nr):
            row = np.zeros(nvar); row[:n] = Hperp[i]; row[n + i] = -2.0
            rows.append(row); lo.append(0.0); hi.append(0.0)
        row = np.zeros(nvar); row[:n] = dvec; row[n + nr] = -2.0
        rows.append(row); lo.append(1.0); hi.append(1.0)
        # weight cap sum(x) <= T-1
        row = np.zeros(nvar); row[:n] = 1.0
        rows.append(row); lo.append(0.0); hi.append(float(T - 1))
        cons = LinearConstraint(np.array(rows), lo, hi)
        opts = {}
        eff = time_limit
        if deadline is not None:
            rem = max(0.5, deadline - _t.time())
            eff = rem if eff is None else min(eff, rem)
        if eff is not None:
            opts["time_limit"] = eff
        res = milp(c=c, constraints=cons, integrality=integrality,
                   bounds=bounds, options=opts)
        if res.status == 2:
            continue  # infeasible -> this subproblem has no logical < T
        if res.status == 0 and res.x is not None:
            w = int(round(res.x[:n].sum()))
            return ("witness", (w, res.x[:n].astype(np.uint8)))
        # time limit / other -> unresolved
        all_infeasible = False
    return ("certified" if all_infeasible else "unknown", None)


def certify_geq(l, m, A, B, T, time_limit=60, total_budget=600):
    c = bb.BBCode(l, m, A, B)
    deadline = time.time() + total_budget
    rX = _type_geq_T(c.HZ, c.HX, T, time_limit, deadline)
    rZ = _type_geq_T(c.HX, c.HZ, T, time_limit, deadline)
    return c, rX, rZ


if __name__ == "__main__":
    l = int(sys.argv[1]); m = int(sys.argv[2])
    # exponents: a1 b1 a2 b2 c1 d1 c2 d2
    e = list(map(int, sys.argv[3:11]))
    T = int(sys.argv[11])
    tl = int(sys.argv[12]) if len(sys.argv) > 12 else 60
    tb = int(sys.argv[13]) if len(sys.argv) > 13 else 600
    A = [(0, 0), (e[0], e[1]), (e[2], e[3])]
    B = [(0, 0), (e[4], e[5]), (e[6], e[7])]
    t = time.time()
    c, rX, rZ = certify_geq(l, m, A, B, T, tl, tb)
    print("code [[%d,%d,?]] A=%s B=%s  target d>=%d" % (c.n, c.k(), A, B, T))
    print("  X-type:", rX[0], ("" if rX[0] != "witness" else "w=%d" % rX[1][0]))
    print("  Z-type:", rZ[0], ("" if rZ[0] != "witness" else "w=%d" % rZ[1][0]))
    if rX[0] == "certified" and rZ[0] == "certified":
        print("  => CERTIFIED d >= %d" % T)
    elif "witness" in (rX[0], rZ[0]):
        ws = [r[1][0] for r in (rX, rZ) if r[0] == "witness"]
        print("  => found logical of weight %d  (d <= %d, so d < %d)"
              % (min(ws), min(ws), T))
    else:
        print("  => UNRESOLVED within budget (no certificate)")
    print("  %.1fs" % (time.time() - t))
