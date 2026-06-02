"""Structured search for high-distance BB codes, driven by structural reasoning.

Pipeline (calibrated timings at n=72: wmax=3 exact enum ~0.4s/code; MILP with a
proven d>3 lower-bound cut closes fast at n=72):

  1. k from two F2 ranks (cheap).
  2. EXACT low-weight enumeration to wmax: separates d<=wmax from d>wmax with a
     PROVEN lower bound (first hit IS the exact distance).
  3. For d>wmax survivors, EXACT MILP with the enum lower-bound cut.  gap=0 ->
     certified exact; else honest upper bound.

We test the structural hypothesis that the fully-mixed canonical form
A = 1 + x^i + y^j, B = 1 + x^p + y^q (each polynomial couples BOTH cyclic
directions) reaches the highest distance, versus the univariate-split and
shared-structure families which collapse to small d.
"""
import sys
import time
import json
from collections import Counter

from qcode import bb, distance


def exact_screen(l, m, A, B, wmax=3):
    """Return (n, k, d_exact_or_None_if_gt_wmax)."""
    c = bb.BBCode(l, m, A, B)
    if not c.css_commute_ok():
        return c, None, None
    k = c.k()
    if k == 0:
        return c, 0, None
    d, found = distance.distance_lowweight_vec(c, wmax=wmax)
    return c, k, (d if found else None)


def canonical_grid(l, m, wmax=3):
    """Scan A=1+x^i+y^j, B=1+x^p+y^q; classify by exact d-vs-wmax.

    Returns survivors = list of (k, i,j,p,q) with d>wmax (the promising ones),
    plus a histogram of the exact small distances.
    """
    print("=== canonical-grid A=1+x^i+y^j B=1+x^p+y^q (l,m)=(%d,%d) wmax=%d ==="
          % (l, m, wmax), flush=True)
    hist = Counter()
    survivors = []
    nseen = 0
    t0 = time.time()
    for i in range(1, l):
        for j in range(1, m):
            for p in range(1, l):
                for q in range(1, m):
                    A = [(0, 0), (i, 0), (0, j)]
                    B = [(0, 0), (p, 0), (0, q)]
                    c, k, d = exact_screen(l, m, A, B, wmax)
                    if k is None or k == 0:
                        continue
                    nseen += 1
                    if d is None:
                        hist[">%d" % wmax] += 1
                        survivors.append((k, i, j, p, q))
                    else:
                        hist["d=%d" % d] += 1
    print(" screened %d nontrivial codes in %.1fs; exact-d histogram: %s"
          % (nseen, time.time() - t0, dict(hist)), flush=True)
    print(" %d survivors with d>%d (k, A=1+x^i+y^j, B=1+x^p+y^q):"
          % (len(survivors), wmax), flush=True)
    for (k, i, j, p, q) in survivors:
        print("   k=%d  A=1+x^%d+y^%d  B=1+x^%d+y^%d" % (k, i, j, p, q),
              flush=True)
    return survivors


def milp_certify(l, m, A, B, wmax_lb=3, time_limit=20, total_budget=120):
    """Exact MILP distance with proven enum lower bound; honest tagging."""
    c = bb.BBCode(l, m, A, B)
    k = c.k()
    d, info = distance.distance_milp(c, time_limit=time_limit,
                                     weight_floor=wmax_lb + 1,
                                     total_time_budget=total_budget)
    tag = ("milp-exact(LB>%d)" % wmax_lb) if info.get("certified_exact") \
        else ("milp-upper(LB>%d)" % wmax_lb)
    fom = (k * d * d / c.n) if d else 0.0
    return dict(n=c.n, k=k, d=d, fom=fom, tag=tag, info_X=info.get("X"),
                info_Z=info.get("Z"))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "grid":
        l = int(sys.argv[2]); m = int(sys.argv[3])
        wmax = int(sys.argv[4]) if len(sys.argv) > 4 else 3
        survivors = canonical_grid(l, m, wmax)
        out = sys.argv[5] if len(sys.argv) > 5 else None
        if out:
            with open(out, "w") as f:
                json.dump(dict(l=l, m=m, wmax=wmax,
                               survivors=[list(s) for s in survivors]), f)
            print("# wrote", out)
    elif cmd == "milp":
        # milp l m  i j p q   (canonical form)
        l = int(sys.argv[2]); m = int(sys.argv[3])
        i, j, p, q = map(int, sys.argv[4:8])
        A = [(0, 0), (i, 0), (0, j)]
        B = [(0, 0), (p, 0), (0, q)]
        t = time.time()
        r = milp_certify(l, m, A, B)
        print("A=1+x^%d+y^%d B=1+x^%d+y^%d -> [[%d,%d,%s]] FOM=%.3f %s  (%.1fs)"
              % (i, j, p, q, r["n"], r["k"], r["d"], r["fom"], r["tag"],
                 time.time() - t), flush=True)
        print("  per-type X=%s Z=%s" % (r["info_X"], r["info_Z"]), flush=True)
