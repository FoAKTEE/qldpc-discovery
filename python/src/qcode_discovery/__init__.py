"""qcode_discovery — a verified reproduction of arXiv:2606.02418 (LLM-guided
evolutionary discovery of bivariate-bicycle quantum LDPC codes).

The LLM/search proposes generator ansaetze; this kernel ADMITS them. Discovery is
catalog-blind; the paper catalog is consulted only post-hoc (`validation`).

Subpackages
-----------
- ``algebra``   GF(2) linear algebra + the ring R = F2[x,y]/(x^l-1, y^m-1).
- ``codes``     BB (CSS) and PBB (non-CSS) construction, parameters (k, FOM), theorem witnesses.
- ``distance``  minimum-distance verifiers: CSS/symplectic MILP, exhaustive enumeration, BP-OSD.
- ``structure`` Tanner-graph decomposability, BLISS dedup, local-Clifford CSS-equivalence.
- ``discovery`` catalog-blind evaluation cascade, GA/generator-ansatz search, post-hoc validation.

The names below form the stable public API: ``from qcode_discovery import BBCode, css_distance_milp, ...``.
"""
from __future__ import annotations

__version__ = "0.1.0"

from .algebra import gf2, polynomials
from .codes.bb_codes import BBCode
from .codes.pbb_codes import PBBCode
from .codes.metrics import css_k, css_logicals, symplectic_logicals, fom
from .codes.theorems import verify_ab_d2, verify_crt_k
from .distance.distance_milp import css_distance_milp, symplectic_distance_milp
from .distance.distance_enum import css_distance_enum
from .distance.distance_bposd import bposd_distance
from .structure.tanner import qubit_components, is_decomposable
from .structure.dedup import dedup_bb, dedup_bliss, bliss_canonical_hash, canonical_poly_signature
from .structure.clifford_equiv import hadamard_two_coloring, lc_css_classify, uniform_clifford_lc_css
from .discovery.evaluation import evaluate_css, evaluate_pbb, screen_k_css
from .discovery.search import blind_search_css, blind_search_pbb, verify_elites_milp
from .discovery.evolve import (GeneratorAnsatz, ansatz_fitness, evolve_ansaetze,
                               random_ansatz, mutate_ansatz, llm_mutation)
from .discovery.validation import validate, landmark_codes, parse_css_catalog, parse_pbb_catalog

__all__ = [
    "gf2", "polynomials",
    "BBCode", "PBBCode", "css_k", "css_logicals", "symplectic_logicals", "fom",
    "verify_ab_d2", "verify_crt_k",
    "css_distance_milp", "symplectic_distance_milp", "css_distance_enum", "bposd_distance",
    "qubit_components", "is_decomposable",
    "dedup_bb", "dedup_bliss", "bliss_canonical_hash", "canonical_poly_signature",
    "hadamard_two_coloring", "lc_css_classify", "uniform_clifford_lc_css",
    "evaluate_css", "evaluate_pbb", "screen_k_css",
    "blind_search_css", "blind_search_pbb", "verify_elites_milp",
    "GeneratorAnsatz", "ansatz_fitness", "evolve_ansaetze", "random_ansatz", "mutate_ansatz", "llm_mutation",
    "validate", "landmark_codes", "parse_css_catalog", "parse_pbb_catalog",
]
