"""Tests for the BLIND discovery layer: evaluation cascade, search, post-hoc validation.

These exercise the apparatus (cascade wiring, search runs blind and finds k>0 codes, the
validator classifies correctly). The search seeds are naive random polynomials — no paper
data — per the blind_discovery_policy.
"""
from qcode_discovery.bb_codes import BBCode
from qcode_discovery.metrics import css_k
from qcode_discovery.distance_milp import css_distance_milp
from qcode_discovery.evaluation import evaluate_css, screen_k_css
from qcode_discovery.search import (blind_search_css, blind_search_pbb,
                                     random_polynomial, mutate_polynomial)
from qcode_discovery.validation import validate, landmark_codes, parse_pbb_catalog
from pathlib import Path
import random

PBB_CATALOG = Path(__file__).resolve().parent.parent / "ref-paper" / "arxiv-2606.02418" / "src" / "pbb_catalog_tables.tex"


def test_evaluation_cascade_matches_kernel():
    # The cascade must reproduce the kernel's k and distance (it just wires them together).
    l, m, A, B = 3, 3, "1+x+y", "1+x^2+y^2"
    code = BBCode(l, m, A, B)
    res = evaluate_css(l, m, A, B, time_limit=30.0)
    assert res["k"] == css_k(code.HX, code.HZ) == 4
    assert res["d"] == css_distance_milp(code, time_limit=30.0)["d"]
    assert res["fom"] == res["k"] * res["d"] ** 2 / res["n"]


def test_screen_k_rejects_zero():
    assert screen_k_css(3, 3, "1+x+y", "1+x+y^2") == 0   # this pair gives k=0


def test_stage3_milp_verification():
    # Stage-3 must recompute exact MILP distance for an elite (here a small (3,3) code).
    from qcode_discovery.search import verify_elites_milp
    from qcode_discovery.distance_milp import css_distance_milp
    elite = {"l": 3, "m": 3, "A": "1+x+y", "B": "1+x^2+y^2", "k": 4, "n": 18, "d": 99,
             "exact": False, "fom": 0.0}
    out = verify_elites_milp([elite], time_limit=30.0)
    code = BBCode(3, 3, "1+x+y", "1+x^2+y^2")
    assert out[0]["d"] == css_distance_milp(code, time_limit=30.0)["d"] and out[0]["exact"]


def test_search_runs_blind_and_finds_codes():
    # Blind search on a tiny lattice must run from naive seeds and populate the archive.
    out = blind_search_css([(3, 3)], n_random=120, distance_budget=4, generations=0,
                            time_limit=10.0, seed=3)
    elites = out["archive_elites"]
    assert out["n_evaluated"] == 120
    assert len(elites) >= 1
    assert all(e["k"] > 0 and e["fom"] > 0 for e in elites)
    assert "evaluated" in out and all(r.get("d") for r in out["evaluated"])  # reps retained for dedup


def test_mutation_preserves_weight():
    rng = random.Random(0)
    p = random_polynomial(6, 6, 3, rng)
    for _ in range(20):
        p = mutate_polynomial(p, 6, 6, rng)
        assert len(set(p)) == 3                       # weight preserved, no collisions


def test_validation_matches_gross_landmark():
    # A synthetic exact [[144,12,12]] discovery must MATCH the gross-code landmark.
    disc = [{"n": 144, "k": 12, "d": 12, "exact": True, "l": 12, "m": 6,
             "A": "y+y^2+x^3", "B": "y^3+x+x^2", "fom": 12.0}]
    rep = validate(disc, catalog_tex=None)            # landmarks only (no catalog needed)
    v = rep["results"][0]["verdict"]
    assert v in ("MATCH", "POLY_MATCH")


def test_validation_upper_bound_consistent():
    # An upper-bound [[72,12,6]] (d<=6) is consistent with the exact landmark [[72,12,6]].
    disc = [{"n": 72, "k": 12, "d": 6, "exact": False, "l": 6, "m": 6,
             "A": "?", "B": "?", "fom": 6.0}]
    rep = validate(disc, catalog_tex=None)
    assert rep["results"][0]["verdict"] in ("UB_CONSISTENT", "MATCH", "POLY_MATCH")
    assert any("72,12,6" in (r["matched_ref"] or "") for r in rep["results"])


# ----------------------------- PBB (non-CSS) discovery layer -----------------------------
def test_pbb_catalog_parses():
    cat = parse_pbb_catalog(PBB_CATALOG)
    assert len(cat) >= 300                              # 368 PBB codes in the catalog
    n36 = {(c["k"], c["d"]) for c in cat if c["n"] == 36}
    assert (2, 6) in n36 and (4, 6) in n36


def test_validation_pbb_exact_match():
    # A blind [[36,2,6]] exact discovery must MATCH the PBB catalog entry of the same (n,k,d).
    disc = [{"n": 36, "k": 2, "d": 6, "exact": True, "l": 6, "m": 3, "A": "?", "B": "?", "fom": 2.0}]
    rep = validate(disc, PBB_CATALOG, kind="pbb")
    assert rep["results"][0]["verdict"] == "MATCH"


def test_blind_pbb_runs_and_is_noncss():
    # Blind PBB search must run from naive seeds and find genuinely non-CSS (mixed) codes.
    out = blind_search_pbb([(6, 3)], n_random=80, distance_budget=2, time_limit=6.0,
                           max_logicals=8, seed=4)
    assert out["n_commuting"] >= 1                       # commutativity filter found valid tuples
    assert all(e["k"] > 0 for e in out["archive_elites"])


# ----------------------------- LC-CSS equivalence (Hadamard 2-coloring) -----------------------------
import numpy as np
from qcode_discovery.pbb_codes import PBBCode
from qcode_discovery.clifford_equiv import hadamard_two_coloring, lc_css_classify, _ParityUF


def _H_makes_css(SX, SZ, patt):
    """Apply H on the flagged qubits and check every generator becomes pure-X or pure-Z."""
    SX, SZ = SX.copy(), SZ.copy()
    J = np.flatnonzero(patt)
    SX[:, J], SZ[:, J] = SZ[:, J].copy(), SX[:, J].copy()
    return bool(((~SZ.any(axis=1)) | (~SX.any(axis=1))).all())


def test_parity_union_find_detects_conflict():
    uf = _ParityUF(3)
    assert uf.union(0, 1, 0)            # bit0 == bit1
    assert uf.union(1, 2, 0)            # bit1 == bit2  => bit0 == bit2
    assert uf.union(0, 2, 1) is False   # but bit0 XOR bit2 = 1 contradicts => conflict


def test_hadamard_css_pattern_is_constructive():
    css = PBBCode(6, 6, "1+x+y", "1+x^2+y^2", "", "")   # C=D=0 => genuinely CSS
    n = css.n
    SX, SZ = css.S[:, :n], css.S[:, n:]
    had = hadamard_two_coloring(SX, SZ)
    assert had["feasible"] and _H_makes_css(SX, SZ, had["H_pattern"])
    assert lc_css_classify(css)["verdict"] == "CSS_GROUP"


def test_hadamard_y_obstruction():
    SX = np.array([[1, 0]], np.uint8)
    SZ = np.array([[1, 0]], np.uint8)                    # generator 0 has Y on qubit 0
    assert hadamard_two_coloring(SX, SZ)["y_obstruction"] is True


def test_genuine_noncss_is_css_inequivalent():
    p = PBBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2", "y+x^3*y", "y^3+x^3*y^3")
    assert not p.is_css_group()
    assert lc_css_classify(p)["verdict"] == "CSS_INEQUIVALENT_TESTED"


def test_uniform_clifford_H_preserves_S_breaks_css():
    # H swaps X<->Z (preserves CSS); S maps X->Y (breaks CSS) — symplectic-exact behavior.
    from qcode_discovery.clifford_equiv import _clifford_symplectic_mats, _apply_block, _is_css
    css = PBBCode(6, 6, "1+x+y", "1+x^2+y^2", "", "")
    n = css.n
    SX, SZ = css.S[:, :n], css.S[:, n:]
    M = _clifford_symplectic_mats()
    assert _is_css(*_apply_block(SX, SZ, M["H"]))          # H preserves CSS
    assert not _is_css(*_apply_block(SX, SZ, M["S"]))      # S breaks CSS


def test_ansatz_generalizes_across_lattices():
    # The paper's key representation property: ONE generator ansatz emits valid codes at MANY lattices.
    from qcode_discovery.evolve import GeneratorAnsatz
    from qcode_discovery.metrics import css_k
    a = GeneratorAnsatz([{"kind": "xyswap", "params": {"a": 3, "b": 1, "c": 2, "d": 3, "e": 1, "f": 2}}])
    for (l, m) in [(6, 6), (12, 6), (15, 12)]:
        gens = a.generate(l, m)
        assert gens, f"ansatz produced nothing at ({l},{m})"
        A, B = gens[0]
        code = BBCode(l, m, A, B)                    # builds + CSS-validates
        assert css_k(code.HX, code.HZ) >= 0


def test_mutate_ansatz_stays_valid_and_llm_is_gated():
    import random
    from qcode_discovery.evolve import random_ansatz, mutate_ansatz, llm_mutation
    rng = random.Random(0)
    a = random_ansatz(rng)
    for _ in range(15):
        a = mutate_ansatz(a, rng)
        assert a.generate(6, 6) is not None          # still a runnable program
    # LLM mutation (the paper's headline) is credential-gated -> must refuse cleanly.
    try:
        llm_mutation(a, "feedback")
        assert False, "llm_mutation should be blocked without credentials"
    except NotImplementedError as e:
        assert "credential" in str(e).lower() or "API key" in str(e)


def test_uniform_clifford_detects_S_equivalence():
    # A CSS code transformed by uniform-S is non-CSS but must be DETECTED as uniform-Clifford-CSS.
    from types import SimpleNamespace
    from qcode_discovery.clifford_equiv import (_clifford_symplectic_mats, _apply_block,
                                                uniform_clifford_lc_css)
    import numpy as np
    css = PBBCode(6, 6, "1+x+y", "1+x^2+y^2", "", "")
    n = css.n
    xb, zb = _apply_block(css.S[:, :n], css.S[:, n:], _clifford_symplectic_mats()["S"])
    mock = SimpleNamespace(S=np.hstack([xb, zb]), n=n, l=6, m=6)
    assert uniform_clifford_lc_css(mock)["css"] is True    # uniform-S recovers CSS


# ----------------------------- BP-OSD distance bound (component 7; needs ldpc) -----------------------------
import pytest


def test_bposd_matches_milp_on_gross():
    pytest.importorskip("ldpc")
    from qcode_discovery.distance_bposd import bposd_distance
    g = BBCode(6, 6, "y+y^2+x^3", "y^3+x+x^2")        # [[72,12,6]]
    assert bposd_distance(g, trials=300, seed=0)["d_bound"] == 6   # matches MILP exact


def test_bposd_gross_144_d12():
    # Regression for the coset-logical bug: the gross [[144,12,12]] (d=12, low-rate) must give
    # BP-OSD bound 12, NOT 6. (Stacking same-type logicals in H_eff wrongly returned 6.)
    pytest.importorskip("ldpc")
    from qcode_discovery.distance_bposd import bposd_distance
    g = BBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2")
    assert bposd_distance(g, trials=400, seed=0)["d_bound"] == 12


def test_bposd_overestimates_high_rate_ab_code():
    # Reproduce the paper's headline finding: BP-OSD grossly overestimates d for high-rate codes.
    pytest.importorskip("ldpc")
    from qcode_discovery.distance_bposd import bposd_distance
    ab = BBCode(12, 6, "x^4+1+y^2", "x^4+1+y^2")      # A=B [[144,32,2]], TRUE d=2 (thm:ab_d2)
    bound = bposd_distance(ab, trials=100, seed=0)["d_bound"]
    assert bound is not None and bound > 2             # overestimate vs the proven exact d=2


# ----------------------------- dedup (lattice-symmetry equivalence) -----------------------------
from qcode_discovery.dedup import canonical_poly_signature, dedup_bb


def test_dedup_merges_equivalent_separates_distinct():
    gross  = BBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2")
    relab  = BBCode(12, 6, "y+y^2+x^3", "y^3+x^5+x^10")    # x->x^5 (coprime 12): equivalent
    swapAB = BBCode(12, 6, "y^3+x+x^2", "y+y^2+x^3")        # A<->B: equivalent
    diff   = BBCode(12, 6, "y+y^2+x^4", "y^3+x+x^2")        # distinct (3a=4 mod12 unsolvable)
    ab     = BBCode(12, 6, "x^4+1+y^2", "x^4+1+y^2")        # A=B distinct code
    sg = lambda c: canonical_poly_signature(c.l, c.m, c.A_terms, c.B_terms)
    assert sg(gross) == sg(relab) == sg(swapAB)
    assert sg(gross) != sg(diff) and sg(gross) != sg(ab)
    res = dedup_bb([gross, relab, swapAB, diff, ab])
    assert res["n_distinct"] == 3


def test_bliss_dedup_exact_and_cross_lattice():
    # igraph/BLISS is the exact method; it also catches cross-lattice isomorphism that the
    # lattice-symmetry canonicalization (within fixed (l,m)) cannot.
    pytest.importorskip("igraph")
    from qcode_discovery.dedup import dedup_bliss, bliss_canonical_hash
    gross = BBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2")
    relab = BBCode(12, 6, "y+y^2+x^3", "y^3+x^5+x^10")
    diff  = BBCode(12, 6, "y+y^2+x^4", "y^3+x+x^2")
    assert bliss_canonical_hash(gross.HX, gross.HZ) == bliss_canonical_hash(relab.HX, relab.HZ)
    assert bliss_canonical_hash(gross.HX, gross.HZ) != bliss_canonical_hash(diff.HX, diff.HZ)
    # [[288,24,12]] = gross (+) gross, appearing at (12,12) and (24,6): BLISS merges (paper);
    # lattice-symmetry dedup cannot (different lattices).
    c1212 = BBCode(12, 12, "x^6+y+y^2", "y^3+x^2+x^4")
    c246  = BBCode(24, 6, "x^6+y+y^2", "y^3+x^2+x^4")
    assert dedup_bb([c1212, c246])["n_distinct"] == 2       # lattice-symmetry: distinct
    assert dedup_bliss([c1212, c246])["n_distinct"] == 1    # BLISS: same Tanner graph
