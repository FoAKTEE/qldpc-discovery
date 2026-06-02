"""Rigorous independent re-certification of the best n=144 candidate.

For each (l,m,A,B): prove d >= 8 by MILP infeasibility (every dual sub-problem,
both X and Z types, with weight cap sum(x) <= 7 infeasible), and find an explicit
weight-8 witness (a feasible logical of weight <= 8) to prove d <= 8.  Together =>
d = 8 EXACT.  Generous per-call and total budgets so the certificate is honest.
"""
import sys
import time
import json

from qcode import bb
from exp_certlb import _type_geq_T


CODES = [
    # (l, m, A, B, target)
    (6, 12, [(0, 0), (1, 3), (2, 3)], [(0, 0), (1, 4), (2, 11)], 8),
]


def full_certify(l, m, A, B, T, time_limit=120, total_budget=1800):
    c = bb.BBCode(l, m, A, B)
    out = dict(l=l, m=m, n=c.n, k=c.k(), css=c.css_commute_ok(), A=A, B=B, T=T)
    # (1) prove d >= T  (no logical of weight <= T-1, both types)
    dl = time.time() + total_budget
    t = time.time()
    geqX = _type_geq_T(c.HZ, c.HX, T, time_limit, dl)
    geqZ = _type_geq_T(c.HX, c.HZ, T, time_limit, dl)
    out["geq_X"] = geqX[0]
    out["geq_Z"] = geqZ[0]
    out["geq_time"] = round(time.time() - t, 1)
    # (2) find a witness of weight <= T (probe d >= T+1; a witness w<=T proves d<=w)
    t = time.time()
    dl2 = time.time() + total_budget
    witX = _type_geq_T(c.HZ, c.HX, T + 1, time_limit, dl2)
    witZ = _type_geq_T(c.HX, c.HZ, T + 1, time_limit, dl2)
    wit_w = None
    for r in (witX, witZ):
        if r[0] == "witness":
            w = r[1][0]
            wit_w = w if wit_w is None else min(wit_w, w)
    out["witness_weight"] = wit_w
    out["wit_X"] = witX[0] + (("(w=%d)" % witX[1][0]) if witX[0] == "witness" else "")
    out["wit_Z"] = witZ[0] + (("(w=%d)" % witZ[1][0]) if witZ[0] == "witness" else "")
    out["wit_time"] = round(time.time() - t, 1)
    # verdict
    geq_ok = (geqX[0] == "certified" and geqZ[0] == "certified")
    if geq_ok and wit_w == T:
        out["verdict"] = "EXACT d=%d" % T
    elif geq_ok and wit_w is not None:
        out["verdict"] = "d in [%d,%d]" % (T, wit_w)
    elif geq_ok:
        out["verdict"] = "d >= %d (no witness <= %d found)" % (T, T)
    elif wit_w is not None:
        out["verdict"] = "d <= %d (LB unresolved)" % wit_w
    else:
        out["verdict"] = "UNRESOLVED"
    return out


if __name__ == "__main__":
    results = []
    for (l, m, A, B, T) in CODES:
        print("certifying [[%d,?,?]] (l,m)=(%d,%d) A=%s B=%s target d=%d"
              % (2 * l * m, l, m, A, B, T), flush=True)
        r = full_certify(l, m, A, B, T)
        print(json.dumps(r), flush=True)
        print("  => %s  (geq %.0fs, wit %.0fs)"
              % (r["verdict"], r["geq_time"], r["wit_time"]), flush=True)
        results.append(r)
    with open("results/_certified_n144.json", "w") as f:
        json.dump(results, f, indent=2)
    print("# wrote results/_certified_n144.json", flush=True)
