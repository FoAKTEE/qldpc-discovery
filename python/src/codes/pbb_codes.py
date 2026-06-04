"""Perturbed bivariate bicycle (PBB) non-CSS code construction.

A PBB code augments a BB pair with perturbation polynomials (C, D):
symplectic stabilizer matrix S = [X | Z] with
    top  rows:  X = (A | B),  Z = (C | D)     # mixed X/Z generators
    bot  rows:  X = (0 | 0),  Z = (B^T | A^T)  # pure-Z generators
over n = 2*l*m qubits. All rows commute iff (A C^T + B D^T) is symmetric over F(2);
C = D = 0 recovers the CSS BB code. k = n - rank(S). Paper anchor: arXiv:2606.02418
sec III.B + SM symplectic formulation. R3.
"""
from __future__ import annotations

import numpy as np

from ..algebra import gf2
from ..algebra.polynomials import parse_poly, poly_matrix


class PBBCode:
    """Non-CSS perturbed bivariate-bicycle code [[2lm, k, d]] from (A, B, C, D)."""

    def __init__(self, l, m, A, B, C, D):
        self.l, self.m = l, m
        p = lambda P: parse_poly(P, l, m) if isinstance(P, str) else P
        self.A_terms, self.B_terms, self.C_terms, self.D_terms = p(A), p(B), p(C), p(D)
        A_ = poly_matrix(l, m, self.A_terms)
        B_ = poly_matrix(l, m, self.B_terms)
        C_ = poly_matrix(l, m, self.C_terms)
        D_ = poly_matrix(l, m, self.D_terms)
        self.A, self.B, self.C, self.D = A_, B_, C_, D_
        lm = l * m
        Z = np.zeros((lm, lm), dtype=np.uint8)
        SX = np.vstack([np.hstack([A_, B_]), np.hstack([Z, Z])]).astype(np.uint8)
        SZ = np.vstack([np.hstack([C_, D_]), np.hstack([B_.T, A_.T])]).astype(np.uint8)
        self.SX, self.SZ = SX, SZ
        self.S = np.hstack([SX, SZ]).astype(np.uint8)   # symplectic (2lm) x (4lm), order (X|Z)
        self.n = 2 * lm
        self._validate_commute()

    # --- commutativity ---
    def reduced_condition_symmetric(self) -> bool:
        """The non-trivial commutativity condition: A C^T + B D^T symmetric over F(2)."""
        M = (self.A @ self.C.T + self.B @ self.D.T) & 1
        return bool((M == M.T).all())

    def symplectic_gram_zero(self) -> bool:
        """All generators pairwise commute: S_X S_Z^T + S_Z S_X^T = 0 (mod 2)."""
        G = (self.SX @ self.SZ.T + self.SZ @ self.SX.T) & 1
        return not bool(G.any())

    def _validate_commute(self) -> None:
        if not self.symplectic_gram_zero():
            raise ValueError("PBB generators do not commute (A C^T + B D^T not symmetric)")

    # --- parameters / structure ---
    @property
    def k(self) -> int:
        """Encoding dimension k = n - (number of independent stabilizer generators)."""
        return self.n - gf2.rank(self.S)

    def is_pure_css(self) -> bool:
        """True iff C = D = 0 (reduces to a CSS BB code)."""
        return not self.C_terms and not self.D_terms

    def has_mixed_generator(self) -> bool:
        """True iff some generator has both X- and Z-support (non-CSS at generator level)."""
        xany = self.SX.any(axis=1)
        zany = self.SZ.any(axis=1)
        return bool((xany & zany).any())

    def is_css_group(self) -> bool:
        """Group-CSS rank condition (Lemma 7.4, cross2025small): rank[X|Z] == rankX + rankZ."""
        return gf2.rank(self.S) == gf2.rank(self.SX) + gf2.rank(self.SZ)

    def __repr__(self) -> str:
        return f"PBBCode(l={self.l}, m={self.m}, n={self.n}, |C|={len(self.C_terms)}, |D|={len(self.D_terms)})"
