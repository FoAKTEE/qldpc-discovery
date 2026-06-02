"""Test the 'diagonal mixing' hypothesis and search for high distance.

Refined structural hypothesis (formed from data, not external reference):
  * univariate-split A(x),B(y): code factors -> d small (<=4).  [rejected]
  * axis-aligned canonical A=1+x^i+y^j: each generator splits along the two
    cyclic axes; a logical can hug one axis -> d caps at 4 (n=72).  [weak]
  * fully MIXED/DIAGONAL trinomials, where the two non-constant monomials BOTH
    carry nonzero x AND y exponents (x^a y^b with a,b != 0), force logicals to
    wind diagonally across the torus -> highest d (6,8 at n=72).  [promising]

We parameterize A = 1 + x^{a1} y^{b1} + x^{a2} y^{b2},
                B = 1 + x^{c1} y^{d1} + x^{c2} y^{d2},
with the constant term 1 fixed (WLOG up to monomial multiplication) and the
other two monomials having both exponents nonzero ("diagonal").

Screen: exact wmax-enum (proven d<=wmax or d>wmax), then MILP on survivors.
"""
import sys
import time
import json
import itertools
import random

from qcode import bb, distance


def make(a1, b1, a2, b2, c1, d1, c2, d2):
    A = [(0, 0), (a1, b1), (a2, b2)]
    B = [(0, 0), (c1, d1), (c2, d2)]
    return A, B


def exact_screen(l, m, A, B, wmax=3):
    c = bb.BBCode(l, m, A, B)
    if not c.css_commute_ok():
        return c, None, None
    k = c.k()
    if k == 0:
        return c, 0, None
    if len(set(A)) != 3 or len(set(B)) != 3:
        return c, None, None
    d, found = distance.distance_lowweight_vec(c, wmax=wmax)
    return c, k, (d if found else None)


def diagonal_search(l, m, wmax=3, n_random=4000, kmin=4, seed=0, out=None):
    """Random search over DIAGONAL trinomial pairs; keep d>wmax survivors.

    Diagonal: the two non-constant monomials of each of A,B have both exponents
    nonzero (a,b in 1..l-1 x 1..m-1).
    """
    rng = random.Random(seed)
    print("=== diagonal search (l,m)=(%d,%d) wmax=%d n_random=%d kmin=%d ==="
          % (l, m, wmax, n_random, kmin), flush=True)
    seen = set()
    survivors = []  # (k, A, B)
    t0 = time.time()
    ntested = 0
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
        ntested += 1
        d, found = distance.distance_lowweight_vec(c, wmax=wmax)
        if not found:  # d > wmax
            survivors.append((k, list(A), list(B)))
    print(" tested %d diagonal codes (k>=%d) in %.1fs; %d survivors d>%d"
          % (ntested, kmin, time.time() - t0, len(survivors), wmax), flush=True)
    # rank survivors by k (FOM proxy; certify distance next)
    survivors.sort(key=lambda s: -s[0])
    for (k, A, B) in survivors[:40]:
        print("   k=%d A=%s B=%s" % (k, A, B), flush=True)
    if out:
        with open(out, "w") as f:
            json.dump(dict(l=l, m=m, wmax=wmax,
                           survivors=[[k, [list(t) for t in A],
                                       [list(t) for t in B]]
                                      for (k, A, B) in survivors]), f)
        print("# wrote", out, flush=True)
    return survivors


if __name__ == "__main__":
    l = int(sys.argv[1]); m = int(sys.argv[2])
    wmax = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    nr = int(sys.argv[4]) if len(sys.argv) > 4 else 4000
    kmin = int(sys.argv[5]) if len(sys.argv) > 5 else 4
    out = sys.argv[6] if len(sys.argv) > 6 else None
    diagonal_search(l, m, wmax, nr, kmin, out=out)
