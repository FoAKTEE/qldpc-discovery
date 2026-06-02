"""Kernel verification suite for the arXiv:2606.02418 reproduction.

Every test is a closed-loop verifier (TRF-R): it admits a scientific claim only on
runnable evidence. Landmarks: gross code k=12, [[72,12,6]] k=12, the two theorems
(thm:ab_d2, lem:crt_k), MILP<->enumeration distance agreement, direct-sum detection,
and PBB non-CSS construction.
"""
import numpy as np
import pytest

from qcode_discovery import gf2
from qcode_discovery.bb_codes import BBCode
from qcode_discovery.pbb_codes import PBBCode
from qcode_discovery.metrics import css_k, css_logicals, fom
from qcode_discovery.distance_milp import css_distance_milp
from qcode_discovery.distance_enum import css_distance_enum
from qcode_discovery.tanner import is_decomposable, qubit_components
from qcode_discovery.theorems import verify_ab_d2, verify_crt_k


# ----------------------------- GF(2) algebra -----------------------------
def test_gf2_rank_nullspace():
    M = np.array([[1, 1, 0], [0, 1, 1], [1, 0, 1]], np.uint8)  # rows sum to 0 => rank 2
    assert gf2.rank(M) == 2
    ns = gf2.nullspace(M)
    assert ns.shape[0] == 3 - 2
    assert not ((M @ ns.T) & 1).any()           # M x = 0 for every basis vector


# ----------------------------- k via rank -----------------------------
def test_gross_code_k12():
    gross = BBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2")
    assert gross.n == 144
    assert css_k(gross.HX, gross.HZ) == 12
    assert gross.stabilizer_weight == 6
    assert fom(144, 12, 12) == 12.0


def test_72_12_6_k12():
    c = BBCode(6, 6, "y+y^2+x^3", "y^3+x+x^2")
    assert c.n == 72
    assert css_k(c.HX, c.HZ) == 12


def test_logicals_count_and_commute():
    gross = BBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2")
    X, Z = css_logicals(gross.HX, gross.HZ)
    assert len(X) == 12 and len(Z) == 12
    assert not ((gross.HX @ Z.T) & 1).any()       # Z-logicals commute with X-stabs
    assert not ((gross.HZ @ X.T) & 1).any()       # X-logicals commute with Z-stabs


# ----------------------------- Theorem thm:ab_d2 -----------------------------
@pytest.mark.parametrize("l,m,A", [(6, 6, "1+x+y"), (12, 6, "x^4+1+y^2"), (6, 6, "y+y^2+x^3")])
def test_ab_d2_constructive_witness(l, m, A):
    r = verify_ab_d2(l, m, A)
    assert r["k"] > 0
    assert r["in_ker_HZ"] and r["nontrivial"]      # weight-2 logical exhibited
    assert r["d_ge_2"]
    assert r["d"] == 2


def test_ab_d2_milp_confirms_small():
    # Independent MILP confirmation of d=2 on a small A=B code.
    code = BBCode(6, 6, "1+x+y", "1+x+y")
    res = css_distance_milp(code, time_limit=30.0)
    assert res["d"] == 2 and res["exact"]


# ----------------------------- Theorem lem:crt_k (k = 8l/3) -----------------------------
@pytest.mark.parametrize("l,m,expect", [(3, 3, 8), (6, 3, 16), (6, 6, 16), (9, 3, 24), (12, 6, 32)])
def test_crt_k_formula(l, m, expect):
    r = verify_crt_k(l, m)
    assert r["expected"] == expect
    assert r["match"], f"k={r['k']} != 8l/3={expect}"


# ----------------------------- MILP <-> enumeration agreement -----------------------------
def test_milp_enum_agree_small():
    # A small code where exhaustive enumeration is feasible; both methods must agree.
    code = BBCode(3, 3, "1+x+y", "1+x^2+y^2")
    enum = css_distance_enum(code, max_weight=4)
    milp = css_distance_milp(code, time_limit=30.0)
    assert enum["d"] is not None
    assert milp["d"] == enum["d"], f"MILP {milp['d']} != enum {enum['d']}"
    assert milp["exact"]


# ----------------------------- decomposability (direct-sum detection) -----------------------------
def test_decomposable_288_24_12():
    # [[288,24,12]] at (12,12), A=x^6+y+y^2, B=y^3+x^2+x^4 = direct sum of two gross codes.
    code = BBCode(12, 12, "x^6+y+y^2", "y^3+x^2+x^4")
    assert css_k(code.HX, code.HZ) == 24
    assert qubit_components(code.HX, code.HZ) == 2
    assert is_decomposable(code)


def test_gross_indecomposable():
    gross = BBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2")
    assert not is_decomposable(gross)


# ----------------------------- PBB non-CSS construction -----------------------------
def test_pbb_144_12_12_noncss():
    # [[144,12,12]] PBB (Table II): A=y+y^2+x^3, B=y^3+x+x^2, C=y+x^3 y, D=y^3+x^3 y^3
    code = PBBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2", "y+x^3*y", "y^3+x^3*y^3")
    assert code.n == 144
    assert code.reduced_condition_symmetric()      # A C^T + B D^T symmetric
    assert code.symplectic_gram_zero()             # all generators commute
    assert code.k == 12
    assert code.has_mixed_generator()              # genuinely non-CSS at generator level
    assert not code.is_css_group()


def test_pbb_reduces_to_css_when_CD_zero():
    pbb = PBBCode(6, 6, "y+y^2+x^3", "y^3+x+x^2", "", "")
    bb = BBCode(6, 6, "y+y^2+x^3", "y^3+x+x^2")
    assert pbb.is_pure_css()
    assert pbb.k == css_k(bb.HX, bb.HZ)
