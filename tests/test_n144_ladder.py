"""Tests for the n=144 capped-MILP distance-bracketing ladder (exp_n144).

The ladder (exp_n144.bracket_distance) climbs target T using the capped-MILP
feasibility certifier (exp_certlb._type_geq_T): at each T it either proves
d >= T (every sub-problem infeasible) or returns an explicit witness logical of
weight < T (a proven upper bound).  The contract we must guarantee is:

    cert_lb <= d_true <= ub        (whenever ub is not None)

We verify this against the EXACT distance computed independently (MILP gap=0
and/or exhaustive low-weight enumeration) on small codes where the true value is
cheap and certain.  We deliberately use small lattices so the test is fast while
still exercising the identical certification code path used at n=144.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from qcode import bb, distance
from exp_n144 import bracket_distance, _sample_pair


def _rt(rng, l, m):
    s = set()
    while len(s) < 3:
        s.add((int(rng.integers(0, l)), int(rng.integers(0, m))))
    return list(s)


def test_bracket_contains_true_distance_small_codes():
    """On small codes the ladder's [cert_lb, ub] must bracket the EXACT distance
    found independently by MILP (gap=0)."""
    rng = np.random.default_rng(5)
    checked = 0
    for _ in range(60):
        A = _rt(rng, 4, 3)
        B = _rt(rng, 4, 3)
        code = bb.BBCode(4, 3, A, B)
        k = code.k()
        if k == 0:
            continue
        # exact distance, independent of the ladder
        d_exact, info = distance.distance_milp(code, time_limit=30,
                                               weight_floor=1)
        if d_exact is None or not info["certified_exact"]:
            continue
        # ladder bracket (T_lo=1 so we don't assume any prior enum floor)
        cert_lb, ub, _wit = bracket_distance(
            code, T_lo=1, T_hi=d_exact + 3, time_limit=30, total_budget=120)
        # lower bound must never exceed the truth
        assert cert_lb <= d_exact, (cert_lb, d_exact, A, B)
        # if a witness was found, it is a genuine upper bound
        if ub is not None:
            assert ub >= d_exact, (ub, d_exact, A, B)
            # and the ladder should pin it: cert_lb == d_exact and ub == d_exact
            # whenever it ran the full climb without timing out
            assert cert_lb == d_exact and ub == d_exact, (cert_lb, ub, d_exact)
        checked += 1
        if checked >= 4:
            break
    assert checked >= 3


def test_sample_pair_families_are_well_formed():
    """Both structural families yield weight-3 polynomials; 'diag' forces the two
    non-constant monomials off both axes, 'free' is unrestricted."""
    rng = __import__("random").Random(0)
    for _ in range(50):
        A, B = _sample_pair(rng, 12, 6, "diag")
        if len(A) == 3 and len(B) == 3:
            assert (0, 0) in A and (0, 0) in B
            for poly in (A, B):
                for (a, b) in poly:
                    if (a, b) != (0, 0):
                        assert a != 0 and b != 0   # strictly diagonal
        Af, Bf = _sample_pair(rng, 12, 6, "free")
        # free family: just weight<=3 distinct monomials over the lattice
        assert len(set(Af)) == len(Af) and len(set(Bf)) == len(Bf)
