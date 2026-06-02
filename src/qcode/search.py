"""Search over trinomial pairs (A, B) to maximise FOM = k * d^2 / n.

Pipeline:
  1. Sample random trinomial pairs over a lattice (l, m).
  2. Fast screen on k (just two F2 ranks) -- cheap, no distance.
  3. Keep a k-diverse candidate pool (so we don't only test highest-k traps).
  4. Evaluate distance with a budget: cheap low-weight enumeration up to a small
     wmax to reject d<=2 traps instantly, then exact MILP for promising ones.
  5. Maintain a FOM-ranked archive.
  6. Optional hill-climb that perturbs exponents of the best codes.

All distance values stored in the archive carry a verification tag.
"""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field

import numpy as np

from . import bb, distance


@dataclass
class Candidate:
    l: int
    m: int
    A: tuple
    B: tuple
    n: int
    k: int
    d: int | None = None
    fom: float | None = None
    verify: str = ""        # how distance was established

    def key(self):
        return (self.l, self.m, tuple(sorted(self.A)), tuple(sorted(self.B)))


def random_trinomial(l, m, rng, allow_identity=True):
    """A weight-3 polynomial: 3 distinct monomials over the lattice."""
    pts = set()
    while len(pts) < 3:
        a = rng.randrange(l)
        b = rng.randrange(m)
        pts.add((a, b))
    return tuple(sorted(pts))


def screen_k(l, m, A, B):
    code = bb.BBCode(l, m, A, B)
    return code, code.k()


def _enum_budget(n):
    """Per-lattice EXACT-enumeration weight budget for the fast screen.

    Measured timings: a no-hit vectorised scan to weight w costs ~C(n,w) heavy
    ops.  A no-hit scan at w<=4 is a few seconds even at n=144, whereas w>=5 at
    n=72 already costs tens of seconds.  So we screen exactly to w<=4 (cheap) and
    delegate everything above to the MILP, which receives a proven lower-bound
    cut (sum(x) >= budget+1) that makes HiGHS fast.
    """
    if n <= 72:
        return 4
    if n <= 108:
        return 4
    return 3


def evaluate_distance(code, wmax_screen=None, milp_time=30):
    """Establish distance with an honest verification tag.

    Step 1: vectorised EXACT low-weight enumeration up to a small per-lattice
            budget.  Because enumeration runs from w=1 upward, the first weight at
            which a logical appears IS the exact distance -> 'enum-exact(w<=W)'.
    Step 2: if nothing up to the budget (so d > budget, a CERTIFIED lower bound),
            run the exact MILP with that lower bound as a cut.  gap=0 ->
            'milp-exact'; otherwise the incumbent is an UPPER bound -> 'milp-upper'.
    """
    n = code.n
    if wmax_screen is None:
        wmax_screen = _enum_budget(n)
    d_low, found = distance.distance_lowweight_vec(code, wmax=wmax_screen)
    if found:
        return d_low, "enum-exact(w<=%d)" % wmax_screen
    # d > wmax_screen is certified by the exhaustive scan; refine with MILP,
    # passing the proven lower bound as a cut to speed up HiGHS.  For large n the
    # MILP rarely closes the gap, so cap each sub-problem's time tightly there to
    # keep the search moving (the result is then an honest upper bound).
    eff_time = milp_time if n <= 108 else min(milp_time, 8)
    # Hard global cap per code so no single hard instance stalls the search.
    total_budget = 45 if n <= 108 else 30
    d_milp, info = distance.distance_milp(code, time_limit=eff_time,
                                          weight_floor=wmax_screen + 1,
                                          total_time_budget=total_budget)
    if d_milp is None:
        return None, "no-logicals"
    if info.get("certified_exact"):
        return d_milp, "milp-exact(enum-LB>%d)" % wmax_screen
    return d_milp, "milp-upper(enum-LB>%d)" % wmax_screen


def run_random_search(lattices, n_samples, rng, kmin=1, kmax=None,
                      kdiverse_per_bucket=6, wmax_screen=None, milp_time=30,
                      verbose=True, checkpoint=None):
    """Random search + k-diverse selection + distance evaluation.

    If ``checkpoint`` is a path, the evaluated archive is written there as JSON
    after every candidate so partial progress survives an interruption.
    """
    import json as _json
    pool = {}   # key -> Candidate (screened, no distance yet)
    for (l, m) in lattices:
        for _ in range(n_samples):
            A = random_trinomial(l, m, rng)
            B = random_trinomial(l, m, rng)
            code, k = screen_k(l, m, A, B)
            if k < kmin:
                continue
            if kmax is not None and k > kmax:
                continue
            cand = Candidate(l=l, m=m, A=A, B=B, n=code.n, k=k)
            pool[cand.key()] = cand
    if verbose:
        print(f"[screen] {len(pool)} unique candidates with k in "
              f"[{kmin},{kmax}] across lattices {lattices}")

    # k-diverse selection: bucket by (lattice, k), take up to N per bucket
    buckets = {}
    for cand in pool.values():
        buckets.setdefault((cand.l, cand.m, cand.k), []).append(cand)
    selected = []
    for key, cands in buckets.items():
        random.Random(hash(key) & 0xffffffff).shuffle(cands)
        selected.extend(cands[:kdiverse_per_bucket])
    if verbose:
        ks = sorted(set(c.k for c in selected))
        print(f"[select] {len(selected)} candidates selected; k values present: {ks}")

    archive = []
    for i, cand in enumerate(selected):
        code = bb.BBCode(cand.l, cand.m, cand.A, cand.B)
        d, tag = evaluate_distance(code, wmax_screen=wmax_screen,
                                   milp_time=milp_time)
        cand.d = d
        cand.verify = tag
        if d is not None and d > 0:
            cand.fom = cand.k * d * d / cand.n
        else:
            cand.fom = 0.0
        archive.append(cand)
        if verbose:
            print(f"  [{i+1}/{len(selected)}] (l,m)=({cand.l},{cand.m}) "
                  f"[[{cand.n},{cand.k},{d}]] FOM={cand.fom:.3f} {tag}",
                  flush=True)
        if checkpoint:
            with open(checkpoint, "w") as _f:
                _json.dump([dict(l=c.l, m=c.m, n=c.n, k=c.k, d=c.d, fom=c.fom,
                                 A=[list(t) for t in c.A],
                                 B=[list(t) for t in c.B], verify=c.verify)
                            for c in sorted(archive,
                                            key=lambda c: (c.fom or 0),
                                            reverse=True)], _f, indent=2)
    archive.sort(key=lambda c: (c.fom or 0.0), reverse=True)
    return archive


def neighbors(cand, rng, n_neigh=8):
    """Generate neighbour trinomial pairs by perturbing one exponent."""
    out = []
    for _ in range(n_neigh):
        A = list(cand.A)
        B = list(cand.B)
        which = rng.choice(["A", "B"])
        target = A if which == "A" else B
        idx = rng.randrange(3)
        a, b = target[idx]
        if rng.random() < 0.5:
            a = (a + rng.choice([-1, 1])) % cand.l
        else:
            b = (b + rng.choice([-1, 1])) % cand.m
        new_term = (a, b)
        if new_term in target:
            continue
        target[idx] = new_term
        if len(set(target)) != 3:
            continue
        out.append((tuple(sorted(A)), tuple(sorted(B))))
    return out


def hill_climb(seeds, rng, iters=40, wmax_screen=None, milp_time=30, verbose=True):
    """Greedy hill-climb on FOM starting from seed candidates."""
    best_by_key = {}
    frontier = list(seeds)
    for s in seeds:
        best_by_key[s.key()] = s
    for it in range(iters):
        if not frontier:
            break
        # expand the current best frontier candidate not yet expanded
        frontier.sort(key=lambda c: (c.fom or 0.0), reverse=True)
        cur = frontier.pop(0)
        for (A, B) in neighbors(cur, rng):
            code, k = screen_k(cur.l, cur.m, A, B)
            if k < 1:
                continue
            cand = Candidate(l=cur.l, m=cur.m, A=A, B=B, n=code.n, k=k)
            if cand.key() in best_by_key:
                continue
            d, tag = evaluate_distance(code, wmax_screen=wmax_screen,
                                       milp_time=milp_time)
            cand.d = d
            cand.verify = tag
            cand.fom = (k * d * d / code.n) if (d and d > 0) else 0.0
            best_by_key[cand.key()] = cand
            frontier.append(cand)
            if verbose and cand.fom and cur.fom and cand.fom > cur.fom:
                print(f"  [hc it{it}] improved -> [[{cand.n},{cand.k},{cand.d}]] "
                      f"FOM={cand.fom:.3f} {tag}")
    res = list(best_by_key.values())
    res.sort(key=lambda c: (c.fom or 0.0), reverse=True)
    return res
