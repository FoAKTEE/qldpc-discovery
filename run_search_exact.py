#!/usr/bin/env python3
"""Focused EXACT search on the fully-certifiable lattices (6,6) n=72 and
(9,6) n=108.  Every distance here is closed by MILP gap=0 (with an enum-derived
lower-bound cut), so every reported [[n,k,d]] is exact.  Used as the rigorous
core result; n=144 is explored separately and reported only as upper bounds.

Usage:  PYTHONPATH=src python3 run_search_exact.py
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import numpy as np

from qcode import search as S


class RngAdapter:
    def __init__(self, g):
        self.r = g
    def randrange(self, n):
        return int(self.r.integers(0, n))
    def random(self):
        return float(self.r.random())
    def choice(self, seq):
        return seq[int(self.r.integers(0, len(seq)))]


def fmt(c):
    return (f"[[{c.n},{c.k},{c.d}]] FOM={c.fom:.3f}  A={list(c.A)} B={list(c.B)}"
            f"  [{c.verify}]")


def main():
    t0 = time.time()
    rng = RngAdapter(np.random.default_rng(7))
    import random
    random.seed(99)

    lattices = [(6, 6), (9, 6)]
    print("EXACT search on", lattices, " (every distance MILP-certified gap=0)")
    archive = S.run_random_search(lattices=lattices, n_samples=400, rng=rng,
                                  kmin=1, kmax=10, kdiverse_per_bucket=8,
                                  wmax_screen=None, milp_time=60, verbose=True)
    seeds = [c for c in archive[:10] if c.fom and c.fom > 0]
    improved = S.hill_climb(seeds, rng, iters=60, wmax_screen=None,
                            milp_time=60, verbose=True)
    by_key = {}
    for c in archive + improved:
        by_key[c.key()] = c
    final = sorted(by_key.values(), key=lambda c: (c.fom or 0), reverse=True)
    print("\n=== TOP 25 (exact) ===")
    for c in final[:25]:
        print("  ", fmt(c))

    os.makedirs("results", exist_ok=True)
    with open("results/_archive_exact.json", "w") as f:
        json.dump([dict(l=c.l, m=c.m, n=c.n, k=c.k, d=c.d, fom=c.fom,
                        A=[list(t) for t in c.A], B=[list(t) for t in c.B],
                        verify=c.verify) for c in final], f, indent=2)
    print(f"saved {len(final)} codes; elapsed {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
