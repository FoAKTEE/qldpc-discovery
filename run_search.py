#!/usr/bin/env python3
"""Discovery driver: random search + k-diverse selection + hill-climb over BB
trinomial pairs, maximising FOM = k d^2 / n.

Distance handling (honest):
  * exact low-weight enumeration up to a per-lattice budget (fast; gives the
    EXACT distance whenever d <= budget);
  * exact MILP for codes whose distance exceeds the budget (gap=0 => exact;
    otherwise the incumbent is an upper bound, flagged as such).

Writes the FOM-ranked archive to results/_archive.json and the top codes to
results/_top_codes.json for the high-budget certification pass.

Usage:  PYTHONPATH=src python3 run_search.py
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import numpy as np

from qcode import bb
from qcode import search as S


def fmt(c):
    return (f"[[{c.n},{c.k},{c.d}]] FOM={c.fom:.3f}  A={list(c.A)} B={list(c.B)}"
            f"  [{c.verify}]")


class RngAdapter:
    """Adapt numpy Generator to the small interface search.py expects."""
    def __init__(self, np_rng):
        self.r = np_rng
    def randrange(self, n):
        return int(self.r.integers(0, n))
    def random(self):
        return float(self.r.random())
    def choice(self, seq):
        return seq[int(self.r.integers(0, len(seq)))]


def main():
    t0 = time.time()
    rng = RngAdapter(np.random.default_rng(20240602))
    import random as _random
    _random.seed(12345)

    # (6,6) n=72 and (9,6) n=108 are fully/largely exact-certifiable.
    # (12,6) and (6,12) n=144 are explored too but distances there may be only
    # upper bounds (flagged).
    lattices = [(6, 6), (9, 6), (12, 6), (6, 12)]

    print("=" * 70)
    print("BB code discovery -- random search + k-diverse + hill-climb")
    print("lattices:", lattices, "  FOM = k*d^2/n")
    print("=" * 70)

    os.makedirs("results", exist_ok=True)
    archive = S.run_random_search(
        lattices=lattices,
        n_samples=250,
        rng=rng,
        kmin=1, kmax=8,            # exclude the high-k / k=n/2 low-distance trap
        kdiverse_per_bucket=5,
        wmax_screen=None,          # per-lattice exact-enum budget (w<=4 / w<=3)
        milp_time=20,              # floor cut makes HiGHS fast at n=72/108
        verbose=True,
        checkpoint="results/_archive_ckpt.json",
    )

    print("\n--- top 20 after random search ---")
    for c in archive[:20]:
        print("  ", fmt(c))

    # Seed the hill-climb from the best CERTIFIABLE codes (n<=108), so we don't
    # spend the climb budget on slow n=144 MILPs.
    seeds = [c for c in archive if c.fom and c.fom > 0 and c.n <= 108][:8]
    print(f"\n--- hill-climb from {len(seeds)} seeds (n<=108) ---")
    improved = S.hill_climb(seeds, rng, iters=50, wmax_screen=None,
                            milp_time=20, verbose=True)

    by_key = {}
    for c in archive + improved:
        by_key[c.key()] = c
    final = sorted(by_key.values(), key=lambda c: (c.fom or 0.0), reverse=True)

    print("\n" + "=" * 70)
    print("FINAL FOM-RANKED ARCHIVE (top 30)")
    print("=" * 70)
    for c in final[:30]:
        print("  ", fmt(c))

    # persist
    os.makedirs("results", exist_ok=True)
    arch_json = [dict(l=c.l, m=c.m, n=c.n, k=c.k, d=c.d, fom=c.fom,
                      A=[list(t) for t in c.A], B=[list(t) for t in c.B],
                      verify=c.verify)
                 for c in final]
    with open("results/_archive.json", "w") as f:
        json.dump(arch_json, f, indent=2)

    # top codes for re-certification: take a FOM-diverse top set
    top = [c for c in final if c.fom and c.fom > 0][:12]
    top_json = [dict(l=c.l, m=c.m, A=[list(t) for t in c.A],
                     B=[list(t) for t in c.B]) for c in top]
    with open("results/_top_codes.json", "w") as f:
        json.dump(top_json, f, indent=2)

    print(f"\nsaved {len(arch_json)} codes to results/_archive.json")
    print(f"saved {len(top_json)} top codes to results/_top_codes.json")
    print(f"elapsed: {time.time()-t0:.1f}s")
    return final


if __name__ == "__main__":
    main()
