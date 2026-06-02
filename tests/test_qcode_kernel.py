"""Tests for the from-scratch qcode kernel.

Run with:  PYTHONPATH=src pytest tests/test_qcode_kernel.py -q
"""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from qcode import gf2, bb, distance


# --------------------------------------------------------------------------
# GF(2) linear algebra
# --------------------------------------------------------------------------
def test_rank_matches_independent_bitvector_impl():
    rng = np.random.default_rng(0)
    for _ in range(100):
        r = rng.integers(1, 8)
        c = rng.integers(1, 8)
        M = rng.integers(0, 2, size=(r, c)).astype(np.uint8)
        # independent F2 rank via bit-vector greedy basis
        rows = [int("".join(map(str, row)), 2) for row in M]
        basis = []
        for x in rows:
            cur = x
            for b in basis:
                cur = min(cur, cur ^ b)
            if cur:
                basis.append(cur)
        assert gf2.rank(M) == len(basis)


def test_nullspace_is_kernel_and_correct_dimension():
    rng = np.random.default_rng(1)
    for _ in range(100):
        r = rng.integers(1, 8)
        c = rng.integers(1, 9)
        M = rng.integers(0, 2, size=(r, c)).astype(np.uint8)
        N = gf2.null_space(M)
        # dimension theorem: nullity = ncols - rank
        assert N.shape[0] == c - gf2.rank(M)
        if N.shape[0]:
            assert not gf2.matmul_f2(M, N.T).any()  # M N^T = 0
            assert gf2.rank(N) == N.shape[0]          # basis independent


def test_in_row_space():
    M = np.array([[1, 1, 0], [0, 1, 1]], dtype=np.uint8)
    assert gf2.in_row_space([1, 0, 1], M)   # = row0 ^ row1
    assert gf2.in_row_space([0, 0, 0], M)   # zero always in
    assert not gf2.in_row_space([1, 0, 0], M)


# --------------------------------------------------------------------------
# BB construction
# --------------------------------------------------------------------------
def test_shift_matrix_is_permutation_with_period_n():
    for n in (3, 5, 6, 9):
        S = bb.shift_matrix(n)
        assert (S.sum(axis=0) == 1).all() and (S.sum(axis=1) == 1).all()
        assert np.array_equal(bb._power(S, n), np.eye(n, dtype=np.uint8))


def test_monomial_multiplication_respects_ring():
    l, m = 6, 6
    for (a1, b1, a2, b2) in [(1, 2, 3, 4), (5, 5, 2, 3), (4, 1, 4, 5)]:
        M1 = bb.monomial(l, m, a1, b1)
        M2 = bb.monomial(l, m, a2, b2)
        prod = gf2.matmul_f2(M1, M2)
        expect = bb.monomial(l, m, (a1 + a2) % l, (b1 + b2) % m)
        assert np.array_equal(prod, expect)


def test_css_commutation_for_random_codes():
    rng = np.random.default_rng(2)

    def rt(l, m):
        s = set()
        while len(s) < 3:
            s.add((int(rng.integers(0, l)), int(rng.integers(0, m))))
        return list(s)

    for (l, m) in [(6, 6), (12, 6), (9, 6), (6, 12)]:
        for _ in range(15):
            code = bb.BBCode(l, m, rt(l, m), rt(l, m))
            assert code.css_commute_ok()
            assert code.n == 2 * l * m


def test_k_formula_consistency():
    # k = n - rank(HX) - rank(HZ), and must be even-ish nonnegative; also
    # ker dimensions are consistent with logical-basis sizes.
    rng = np.random.default_rng(5)

    def rt(l, m):
        s = set()
        while len(s) < 3:
            s.add((int(rng.integers(0, l)), int(rng.integers(0, m))))
        return list(s)

    for _ in range(20):
        code = bb.BBCode(6, 6, rt(6, 6), rt(6, 6))
        k = code.k()
        assert k >= 0
        xlog, _ = distance._logical_basis(code.HZ, code.HX)
        zlog, _ = distance._logical_basis(code.HX, code.HZ)
        # number of X-logical reps == number of Z-logical reps == k
        assert xlog.shape[0] == k
        assert zlog.shape[0] == k


# --------------------------------------------------------------------------
# Distance: cross-check the three independent methods
# --------------------------------------------------------------------------
def test_distance_methods_agree_small():
    rng = np.random.default_rng(7)

    def rt(l, m):
        s = set()
        while len(s) < 3:
            s.add((int(rng.integers(0, l)), int(rng.integers(0, m))))
        return list(s)

    checked = 0
    for _ in range(40):
        code = bb.BBCode(3, 3, rt(3, 3), rt(3, 3))
        if code.k() == 0:
            continue
        try:
            d_enum, _ = distance.distance_enum(code, max_kplus_s=20)
        except ValueError:
            continue
        d_low, found = distance.distance_lowweight(code, wmax=18)
        d_milp, info = distance.distance_milp(code)
        assert found
        assert d_enum == d_low == d_milp
        assert info["certified_exact"]
        checked += 1
    assert checked >= 5  # ensure the test actually exercised codes


def test_lowweight_finds_known_weight2_logical():
    # A code with A == B is a known trap with a weight-2 logical (the task
    # states d=2 for A=B). Verify low-weight enumeration detects d<=2.
    A = [(0, 0), (1, 0), (0, 1)]
    code = bb.BBCode(6, 6, A, A)
    d, found = distance.distance_lowweight(code, wmax=4)
    assert found
    assert d == 2
