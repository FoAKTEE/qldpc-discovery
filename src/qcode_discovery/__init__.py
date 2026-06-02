"""qcode_discovery — reproduction of arXiv:2606.02418 (LLM-guided evolutionary
discovery of bivariate-bicycle quantum LDPC codes).

Kernel layer (the scientific verifiers that admit a discovery): GF(2) algebra,
BB/PBB construction, k, CSS/symplectic MILP distance, enumeration, Tanner-graph
structure, and numeric theorem witnesses. The LLM proposes ansaetze; this kernel admits.
"""
from __future__ import annotations

__all__ = [
    "gf2", "polynomials", "bb_codes", "pbb_codes", "metrics",
    "distance_milp", "distance_enum", "tanner", "theorems",
    "evaluation", "search", "validation", "clifford_equiv",
]
__version__ = "0.1.0"
