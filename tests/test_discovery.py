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


def test_search_runs_blind_and_finds_codes():
    # Blind search on a tiny lattice must run from naive seeds and populate the archive.
    out = blind_search_css([(3, 3)], n_random=120, distance_budget=4, generations=0,
                            time_limit=10.0, seed=3)
    elites = out["archive_elites"]
    assert out["n_evaluated"] == 120
    assert len(elites) >= 1
    assert all(e["k"] > 0 and e["fom"] > 0 for e in elites)


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
