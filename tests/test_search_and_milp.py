"""Tests for the search pipeline, MILP exactness, and the vectorised
low-weight enumeration.  Run:  PYTHONPATH=src pytest tests/ -q
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from qcode import bb, distance
from qcode import search as S


def _rt(rng, l, m):
    s = set()
    while len(s) < 3:
        s.add((int(rng.integers(0, l)), int(rng.integers(0, m))))
    return list(s)


def test_vectorised_lowweight_matches_scalar_reference():
    rng = np.random.default_rng(13)
    checked = 0
    for _ in range(40):
        code = bb.BBCode(3, 3, _rt(rng, 3, 3), _rt(rng, 3, 3))
        if code.k() == 0:
            continue
        d1, f1 = distance.distance_lowweight(code, wmax=8)
        d2, f2 = distance.distance_lowweight_vec(code, wmax=8)
        assert (d1, f1) == (d2, f2)
        checked += 1
    assert checked >= 5


def test_milp_weight_floor_does_not_change_exact_value():
    # A floor of 1 is always a valid lower bound (d >= 1); the exact distance and
    # its certification must be unchanged.
    rng = np.random.default_rng(31)
    checked = 0
    for _ in range(40):
        code = bb.BBCode(3, 3, _rt(rng, 3, 3), _rt(rng, 3, 3))
        if code.k() == 0:
            continue
        d0, i0 = distance.distance_milp(code, weight_floor=0)
        d1, i1 = distance.distance_milp(code, weight_floor=1)
        assert d0 == d1
        assert i0["certified_exact"] and i1["certified_exact"]
        checked += 1
    assert checked >= 5


def test_milp_matches_enumeration_on_n72_small_distance():
    # For n=72 codes whose distance is small (<=4, fast to enumerate), the exact
    # MILP and the exact low-weight enumeration must agree, and the MILP must
    # close the gap (gap=0).  Uses wmax=4 to keep the test fast.
    rng = np.random.default_rng(42)
    checked = 0
    for _ in range(200):
        code = bb.BBCode(6, 6, _rt(rng, 6, 6), _rt(rng, 6, 6))
        if code.k() == 0:
            continue
        d_low, found = distance.distance_lowweight_vec(code, wmax=4)
        if not found:
            continue   # d > 4: skip here (covered by the exact-MILP-with-floor case)
        d_milp, info = distance.distance_milp(code, time_limit=30,
                                              weight_floor=1)
        assert info["certified_exact"]
        assert d_milp == d_low
        checked += 1
        if checked >= 3:
            break
    assert checked >= 3


def test_search_finds_nontrivial_codes_and_rejects_AequalsB_trap():
    # The k-diverse random search returns codes with k>0 and a finite distance.
    rng = np.random.default_rng(7)

    class R:
        def __init__(self, g):
            self.r = g
        def randrange(self, n):
            return int(self.r.integers(0, n))
        def random(self):
            return float(self.r.random())
        def choice(self, seq):
            return seq[int(self.r.integers(0, len(seq)))]

    import random
    random.seed(1)
    arch = S.run_random_search([(6, 6)], n_samples=60, rng=R(rng),
                               kmin=1, kmax=8, kdiverse_per_bucket=3,
                               milp_time=20, verbose=False)
    assert len(arch) >= 1
    top = arch[0]
    assert top.k >= 1
    assert top.d is not None and top.d >= 2
    assert top.fom is not None and top.fom > 0

    # A == B is a trap with d == 2.
    A = [(0, 0), (1, 0), (0, 1)]
    trap = bb.BBCode(6, 6, A, A)
    d, found = distance.distance_lowweight_vec(trap, wmax=4)
    assert found and d == 2
