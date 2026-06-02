"""Bivariate bicycle (BB) CSS code construction, built from scratch.

Ring R = F2[x,y]/(x^l - 1, y^m - 1).  A monomial x^a y^b is represented by the
(l*m) x (l*m) binary matrix kron(S_l^a, S_m^b), where S_n is the n x n cyclic
shift permutation matrix.  A polynomial is the mod-2 sum of its monomial
matrices.

Given weight-3 polynomials A, B (each a list of (a, b) exponent pairs), we form
    H_X = [A | B]          shape (l*m) x (2 l m)
    H_Z = [B^T | A^T]      shape (l*m) x (2 l m)
These satisfy H_X H_Z^T = 0 (mod 2) because the constituent monomial matrices
all commute (S_l and S_m act on different tensor factors and shifts commute).

Physical qubits  n = 2 l m.
Encoded qubits   k = n - rank_F2(H_X) - rank_F2(H_Z).
"""

from __future__ import annotations

import numpy as np

from . import gf2


def shift_matrix(n: int) -> np.ndarray:
    """n x n cyclic shift permutation S: (S v)[i] = v[i-1 mod n].

    Concretely S[i, j] = 1 iff i == (j+1) mod n, i.e. S has 1's on the
    sub/super-cyclic diagonal.  S^a is then the shift-by-a permutation.
    """
    S = np.zeros((n, n), dtype=np.uint8)
    for j in range(n):
        S[(j + 1) % n, j] = 1
    return S


def _power(S: np.ndarray, p: int) -> np.ndarray:
    n = S.shape[0]
    p %= n
    out = np.eye(n, dtype=np.uint8)
    base = S.copy()
    while p:
        if p & 1:
            out = gf2.matmul_f2(out, base)
        base = gf2.matmul_f2(base, base)
        p >>= 1
    return out


def monomial(l: int, m: int, a: int, b: int) -> np.ndarray:
    """Matrix for x^a y^b = kron(S_l^a, S_m^b)."""
    Sl = shift_matrix(l)
    Sm = shift_matrix(m)
    return np.kron(_power(Sl, a), _power(Sm, b)).astype(np.uint8)


def poly_matrix(l: int, m: int, terms) -> np.ndarray:
    """Mod-2 sum of monomial matrices for a polynomial given as [(a,b), ...]."""
    dim = l * m
    M = np.zeros((dim, dim), dtype=np.uint8)
    for (a, b) in terms:
        M ^= monomial(l, m, a, b)
    return M


class BBCode:
    """A bivariate bicycle CSS code for fixed (l, m) and polynomials A, B."""

    def __init__(self, l: int, m: int, A_terms, B_terms):
        self.l = l
        self.m = m
        self.A_terms = list(A_terms)
        self.B_terms = list(B_terms)
        self.A = poly_matrix(l, m, A_terms)
        self.B = poly_matrix(l, m, B_terms)
        # H_X = [A | B],  H_Z = [B^T | A^T]
        self.HX = np.hstack([self.A, self.B]).astype(np.uint8)
        self.HZ = np.hstack([self.B.T, self.A.T]).astype(np.uint8)
        self.n = 2 * l * m

    # ---- structural quantities -------------------------------------------
    def css_commute_ok(self) -> bool:
        """Verify H_X H_Z^T = 0 (mod 2)."""
        return not gf2.matmul_f2(self.HX, self.HZ.T).any()

    def rank_HX(self) -> int:
        return gf2.rank(self.HX)

    def rank_HZ(self) -> int:
        return gf2.rank(self.HZ)

    def k(self) -> int:
        """Number of encoded qubits."""
        return self.n - self.rank_HX() - self.rank_HZ()

    # ---- logical operator spaces -----------------------------------------
    def x_logical_space(self):
        """Basis for X-logicals: ker(H_Z) modulo rowspace(H_X).

        Returns (ker_basis, HX_rowspace) so callers can test membership.
        An X-logical is x with H_Z x = 0 and x NOT in rowspace(H_X).
        """
        ker = gf2.null_space(self.HZ)        # rows = basis of ker H_Z
        return ker

    def z_logical_space(self):
        """Basis for Z-logicals: ker(H_X) modulo rowspace(H_Z)."""
        ker = gf2.null_space(self.HX)
        return ker

    def params(self):
        return (self.n, self.k())
