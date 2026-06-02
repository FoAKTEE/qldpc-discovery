"""Search the ALL-THREE-DIAGONAL trinomial family for high distance.

Structural motivation (from our own data): the (6,6) codes that reached the
highest distance (d=8) used trinomials whose THREE monomials are all fully
mixed (each x^a y^b with a,b possibly both nonzero, NO forced constant term and
NO axis-aligned term).  This is a richer family than '1 + diagonal + diagonal'.
We sample such pairs, keep k>=kmin and d>2, then MILP-estimate the distance with
a short budget (incumbent is a valid upper bound; with the proven d>2 floor it
brackets d).  Checkpointed, storing l,m,A,B so the certifier can re-load.
"""
import sys
import time
import json
import random

from qcode import bb, distance


def run(l, m, n_random=3000, kmin=8, seed=0, milp_time=12, total_budget=30,
        out=None, max_eval=80):
    n = 2 * l * m
    print("=== all-3-diagonal search (l,m)=(%d,%d) n=%d kmin=%d seed=%d ==="
          % (l, m, n, kmin, seed), flush=True)
    rng = random.Random(seed)
    seen = set()
    cands = []
    t0 = time.time()
    for _ in range(n_random):
        def mono():
            return (rng.randrange(l), rng.randrange(m))
        A = tuple(sorted(set(mono() for _ in range(6))))[:3]
        B = tuple(sorted(set(mono() for _ in range(6))))[:3]
        if len(A) != 3 or len(B) != 3:
            continue
        key = (A, B)
        if key in seen:
            continue
        seen.add(key)
        c = bb.BBCode(l, m, list(A), list(B))
        if not c.css_commute_ok():
            continue
        k = c.k()
        if k < kmin:
            continue
        d2, found = distance.distance_lowweight_vec(c, wmax=2)
        if found:
            continue
        cands.append((k, list(A), list(B)))
    print("# stageAB: %d codes k>=%d d>2 (from %d unique, %.1fs)"
          % (len(cands), kmin, len(seen), time.time() - t0), flush=True)
    cands.sort(key=lambda s: -s[0])
    results = []
    for idx, (k, A, B) in enumerate(cands[:max_eval]):
        c = bb.BBCode(l, m, A, B)
        t = time.time()
        d, info = distance.distance_milp(c, time_limit=milp_time,
                                         weight_floor=3,
                                         total_time_budget=total_budget)
        exact = bool(info.get("certified_exact"))
        fom = (k * d * d / n) if d else 0.0
        rec = dict(l=l, m=m, n=n, k=k, d=d, fom=fom, exact=exact,
                   A=[list(t) for t in A], B=[list(t) for t in B],
                   X=info.get("X"), Z=info.get("Z"))
        results.append(rec)
        print("  [%d/%d] [[%d,%d,%s]] FOM=%.3f %s (%.0fs) A=%s B=%s"
              % (idx + 1, min(len(cands), max_eval), n, k, d, fom,
                 "exact" if exact else "UB", time.time() - t, A, B), flush=True)
        if out:
            with open(out, "w") as f:
                json.dump(sorted(results, key=lambda r: r["fom"],
                                 reverse=True), f, indent=2)
    print("# done; wrote", out, flush=True)
    return results


if __name__ == "__main__":
    l = int(sys.argv[1]); m = int(sys.argv[2])
    kw = {}
    for a in sys.argv[3:]:
        key, val = a.split("=")
        kw[key] = int(val) if val.lstrip("-").isdigit() else val
    run(l, m, **kw)
