"""Batch rigorous certification of the top n=144 candidates (d>=7 survivors).

Each is probed at the target T: prove d>=T (all sub-problems weight<=T-1
infeasible, both types) and search for a witness of weight<=T (proves d<=that).
Verdict is one of EXACT d=T / d in [T, w] / d>=T (no witness) / d<=w / UNRESOLVED.
"""
import sys
import time
import json

from qcode import bb
from exp_certlb import _type_geq_T

CODES = [
    # l, m, A, B, target T
    (12, 6, [(0, 0), (4, 3), (11, 3)], [(0, 0), (5, 5), (10, 1)], 8),
    (6, 12, [(0, 0), (1, 8), (2, 1)], [(0, 0), (3, 10), (3, 11)], 8),
]


def full_certify(l, m, A, B, T, time_limit=120, total_budget=1500):
    c = bb.BBCode(l, m, A, B)
    out = dict(l=l, m=m, n=c.n, k=c.k(), css=c.css_commute_ok(), A=A, B=B, T=T)
    dl = time.time() + total_budget
    t = time.time()
    geqX = _type_geq_T(c.HZ, c.HX, T, time_limit, dl)
    geqZ = _type_geq_T(c.HX, c.HZ, T, time_limit, dl)
    out["geq_X"] = geqX[0]; out["geq_Z"] = geqZ[0]
    out["geq_time"] = round(time.time() - t, 1)
    t = time.time(); dl2 = time.time() + total_budget
    witX = _type_geq_T(c.HZ, c.HX, T + 1, time_limit, dl2)
    witZ = _type_geq_T(c.HX, c.HZ, T + 1, time_limit, dl2)
    wit_w = None
    for r in (witX, witZ):
        if r[0] == "witness":
            wit_w = r[1][0] if wit_w is None else min(wit_w, r[1][0])
    out["witness_weight"] = wit_w
    out["wit_time"] = round(time.time() - t, 1)
    geq_ok = (geqX[0] == "certified" and geqZ[0] == "certified")
    if geq_ok and wit_w == T:
        out["verdict"] = "EXACT d=%d" % T
    elif geq_ok and wit_w is not None:
        out["verdict"] = "d in [%d,%d]" % (T, wit_w)
    elif geq_ok:
        out["verdict"] = "d >= %d" % T
    elif wit_w is not None:
        out["verdict"] = "d <= %d (LB unresolved)" % wit_w
    else:
        out["verdict"] = "UNRESOLVED"
    return out


if __name__ == "__main__":
    results = []
    for (l, m, A, B, T) in CODES:
        print("certifying (l,m)=(%d,%d) A=%s B=%s target d=%d"
              % (l, m, A, B, T), flush=True)
        r = full_certify(l, m, A, B, T)
        print(json.dumps(r), flush=True)
        print("  => %s (geq %.0fs wit %.0fs)"
              % (r["verdict"], r["geq_time"], r["wit_time"]), flush=True)
        results.append(r)
    with open("results/_certified_n144_batch.json", "w") as f:
        json.dump(results, f, indent=2)
    print("# wrote results/_certified_n144_batch.json", flush=True)
