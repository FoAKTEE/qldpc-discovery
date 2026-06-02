"""Structural reasoning experiments for high-distance BB codes.

Reason from first principles about WHICH algebraic structure of the trinomial
pair (A,B) over R = F2[x,y]/(x^l-1, y^m-1) yields high minimum distance.

Budget-aware screening:
  - k from two F2 ranks (cheap).
  - randomized UPPER BOUND distance (distance_ub_random) for the grid screen.
    It NEVER underestimates the true d, is fully vectorised over trials, and is
    fast even at n=144.  We use it to RANK families and find the structures whose
    UB is large (meaning the true distance is at least... no -- a large UB only
    says we failed to find a light logical; combined with the structural argument
    and later exact checks it points us to the promising region).  Crucially a
    SMALL UB is a hard fact: it certifies d is small.  So the screen reliably
    REJECTS low-distance families.
  - exact low-weight enum + MILP reserved for the handful of best survivors.

Run as:  PYTHONPATH=src python3 -u exp_structure.py <experiment> [args]
"""
import sys
import time
from collections import Counter

from qcode import bb, distance


def screen_ub(l, m, A, B, ub_trials=20000):
    """k + randomized UB on distance.  Returns dict or None if css fails."""
    c = bb.BBCode(l, m, A, B)
    if not c.css_commute_ok():
        return None
    k = c.k()
    if k == 0:
        return dict(n=c.n, k=0, ub=None)
    ub, _ = distance.distance_ub_random(c, n_trials=ub_trials, seed=1)
    return dict(n=c.n, k=k, ub=ub)


# ---------------------------------------------------------------------------
def exp_univariate():
    l, m = 6, 6
    print("=== H1: univariate split  A(x) only, B(y) only  (l,m)=(6,6) ===")
    As = [[(0, 0), (1, 0), (2, 0)], [(0, 0), (1, 0), (3, 0)],
          [(0, 0), (2, 0), (4, 0)]]
    Bs = [[(0, 0), (0, 1), (0, 2)], [(0, 0), (0, 1), (0, 3)],
          [(0, 0), (0, 2), (0, 4)]]
    for A in As:
        for B in Bs:
            print(" A", A, "B", B, "->", screen_ub(l, m, A, B), flush=True)


def exp_mixed_grid(l=6, m=6, ub_trials=20000, topn=30):
    """H3: canonical mixed form A=1+x^i+y^j, B=1+x^p+y^q.

    Each polynomial couples both cyclic directions.  Scan exponents; report the
    distribution of randomized-UB distance and the highest-UB survivors.
    """
    print("=== H3: canonical mixed A=1+x^i+y^j, B=1+x^p+y^q  (l,m)=(%d,%d)  "
          "ub_trials=%d ===" % (l, m, ub_trials))
    rows = []   # (ub, k, i,j,p,q)
    hist = Counter()
    nseen = 0
    for i in range(1, l):
        for j in range(1, m):
            for p in range(1, l):
                for q in range(1, m):
                    A = [(0, 0), (i, 0), (0, j)]
                    B = [(0, 0), (p, 0), (0, q)]
                    s = screen_ub(l, m, A, B, ub_trials)
                    if s is None or s["k"] == 0:
                        continue
                    nseen += 1
                    ub = s["ub"]
                    hist[ub] += 1
                    rows.append((ub, s["k"], i, j, p, q))
    print(" screened %d nontrivial codes; UB histogram (ub:count): %s"
          % (nseen, dict(sorted(hist.items()))), flush=True)
    rows.sort(reverse=True)
    print(" top %d by randomized-UB distance (ub, k, A=1+x^i+y^j, B=1+x^p+y^q):"
          % topn)
    for (ub, k, i, j, p, q) in rows[:topn]:
        print("   ub=%2d k=%d  A=1+x^%d+y^%d  B=1+x^%d+y^%d  fom_ub=%.2f"
              % (ub, k, i, j, p, q, k * ub * ub / (2 * l * m)), flush=True)
    return rows


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "all"
    args = sys.argv[2:]
    t0 = time.time()
    if name == "univariate":
        exp_univariate()
    elif name == "mixed":
        l = int(args[0]) if args else 6
        m = int(args[1]) if len(args) > 1 else 6
        tr = int(args[2]) if len(args) > 2 else 20000
        exp_mixed_grid(l, m, tr)
    print("# elapsed %.1fs" % (time.time() - t0))
