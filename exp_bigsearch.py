"""High-distance search on big lattices using diagonal-mixing structure.

Lean, checkpointed pipeline:
  Stage A+B  random DIAGONAL pairs; keep k>=kmin and d>2 (proven via wmax=2 enum).
  Stage C    short-budget MILP distance ESTIMATE per candidate (incumbent is a
             valid upper bound; with the proven d>2 floor it brackets d).  Rank
             by estimated FOM = k*d_est^2/n.  Checkpointed after every code.
  (certification of the top codes is done separately with exp_certlb.certify_geq,
   which rigorously proves d>=T via MILP infeasibility.)

Diagonal = the two non-constant monomials of A and of B each carry nonzero x AND
y exponents (the structural family the data shows reaches the highest distance).
"""
import sys
import time
import json
import random

from qcode import bb, distance


def run(l, m, n_random=4000, kmin=8, seed=0, milp_time=12, total_budget=40,
        out=None, max_eval=200):
    n = 2 * l * m
    print("=== big diagonal search (l,m)=(%d,%d) n=%d kmin=%d seed=%d "
          "milp_time=%d ===" % (l, m, n, kmin, seed, milp_time), flush=True)
    rng = random.Random(seed)
    seen = set()
    cands = []
    t0 = time.time()
    # Stage A+B
    for _ in range(n_random):
        def mono():
            return (rng.randrange(1, l), rng.randrange(1, m))
        A = tuple(sorted({(0, 0), mono(), mono()}))
        B = tuple(sorted({(0, 0), mono(), mono()}))
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
    print("# stageAB: %d diagonal codes k>=%d d>2 (from %d unique, %.1fs)"
          % (len(cands), kmin, len(seen), time.time() - t0), flush=True)
    # Stage C: short MILP estimate, ranked, checkpointed
    cands.sort(key=lambda s: -s[0])  # high k first
    results = []
    for idx, (k, A, B) in enumerate(cands[:max_eval]):
        c = bb.BBCode(l, m, A, B)
        t = time.time()
        d, info = distance.distance_milp(c, time_limit=milp_time,
                                         weight_floor=3,
                                         total_time_budget=total_budget)
        exact = bool(info.get("certified_exact"))
        fom = (k * d * d / n) if d else 0.0
        rec = dict(n=n, k=k, d=d, fom=fom, exact=exact, A=A, B=B,
                   X=info.get("X"), Z=info.get("Z"))
        results.append(rec)
        print("  [%d/%d] [[%d,%d,%s]] FOM=%.3f %s (%.1fs) A=%s B=%s"
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
