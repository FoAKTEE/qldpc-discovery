"""Probe whether the two PROVEN-d>=8 n=144 codes are actually d>=9 (or have a
weight-8/9 witness pinning them at d=8/9).  For each: probe target T=9 -- prove
d>=9 (all weight<=8 sub-problems infeasible) OR return a witness w<=8 (=> d<=8).
Generous budget.  This directly tests the high-distance question: is anything at
n=144 provably >= 9?
"""
import sys
import time
import json

from qcode import bb
from exp_certlb import _type_geq_T

CODES = [
    (12, 6, [(0, 0), (4, 3), (11, 3)], [(0, 0), (5, 5), (10, 1)]),
    (6, 12, [(0, 0), (1, 8), (2, 1)], [(0, 0), (3, 10), (3, 11)]),
    # also re-probe the EXACT d=8 code at T=9 as a control (must find w=8 witness)
    (6, 12, [(0, 0), (1, 3), (2, 3)], [(0, 0), (1, 4), (2, 11)]),
]
T = 9


def probe(l, m, A, B, time_limit=150, total_budget=2000):
    c = bb.BBCode(l, m, A, B)
    dl = time.time() + total_budget
    t = time.time()
    rX = _type_geq_T(c.HZ, c.HX, T, time_limit, dl)
    rZ = _type_geq_T(c.HX, c.HZ, T, time_limit, dl)
    wit = None
    for r in (rX, rZ):
        if r[0] == "witness":
            wit = r[1][0] if wit is None else min(wit, r[1][0])
    if rX[0] == "certified" and rZ[0] == "certified":
        v = "d >= %d" % T
    elif wit is not None:
        v = "witness w=%d (d <= %d)" % (wit, wit)
    else:
        v = "UNRESOLVED (X:%s Z:%s)" % (rX[0], rZ[0])
    return dict(l=l, m=m, n=c.n, k=c.k(), A=A, B=B, verdict=v,
                time=round(time.time() - t, 1))


if __name__ == "__main__":
    out = []
    for (l, m, A, B) in CODES:
        r = probe(l, m, A, B)
        print("(l,m)=(%d,%d) A=%s B=%s -> %s (%.0fs)"
              % (l, m, A, B, r["verdict"], r["time"]), flush=True)
        out.append(r)
        with open("results/_probe_d9.json", "w") as f:
            json.dump(out, f, indent=2)
    print("# wrote results/_probe_d9.json", flush=True)
