"""Bivariate bicycle (BB) CSS code construction.

A BB code over R = F2[x,y]/(x^l-1, y^m-1) is the CSS code with parity checks
H_X = (A | B), H_Z = (B^T | A^T) for polynomials A, B in R; n = 2*l*m physical
qubits. CSS condition H_X H_Z^T = A B + B A = 0 holds automatically because the
monomial (shift) matrices commute. Paper anchor: arXiv:2606.02418 sec II.A. R2.
"""
from __future__ import annotations

import numpy as np

from . import gf2
from .polynomials import Poly, parse_poly, poly_matrix, poly_weight


class BBCode:
    """CSS bivariate-bicycle code [[2lm, k, d]] from trinomials (or general polys) A, B."""

    def __init__(self, l: int, m: int, A: Poly | str, B: Poly | str):
        self.l, self.m = l, m
        self.A_terms: Poly = parse_poly(A, l, m) if isinstance(A, str) else A
        self.B_terms: Poly = parse_poly(B, l, m) if isinstance(B, str) else B
        self.A = poly_matrix(l, m, self.A_terms)
        self.B = poly_matrix(l, m, self.B_terms)
        self.HX = np.hstack([self.A, self.B]).astype(np.uint8)
        self.HZ = np.hstack([self.B.T, self.A.T]).astype(np.uint8)
        self.n = 2 * l * m
        self._validate_css()

    def _validate_css(self) -> None:
        prod = (self.HX @ self.HZ.T) & 1
        if prod.any():
            raise ValueError("CSS condition H_X H_Z^T = 0 violated (A,B do not commute)")

    @property
    def stabilizer_weight(self) -> int:
        """Max stabilizer weight = |A| + |B| (weight-6 for trinomials)."""
        return poly_weight(self.A_terms, self.l, self.m) + poly_weight(self.B_terms, self.l, self.m)

    def is_AB_equal(self) -> bool:
        """True iff A == B as polynomials (the d=2 distance trap, Thm thm:ab_d2)."""
        return set(self.A_terms) == set(self.B_terms)

    def __repr__(self) -> str:
        return f"BBCode(l={self.l}, m={self.m}, |A|={len(self.A_terms)}, |B|={len(self.B_terms)}, n={self.n})"
