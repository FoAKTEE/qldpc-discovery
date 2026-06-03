"""Polynomials over the bivariate quotient ring R = F2[x,y]/(x^l-1, y^m-1).

A monomial x^a y^b acts on F(2)^{lm} as the commuting tensor product of cyclic
shifts S_l^a (x) and S_m^b (y); a polynomial is the mod-2 sum of its monomial
matrices. Index convention: group element (i in Z_l, j in Z_m) -> i*m + j, i.e.
kron(shift_l, shift_m). Paper anchor: arXiv:2606.02418 sec II.A. R1.
"""
from __future__ import annotations

import re
import numpy as np

Term = tuple[int, int]          # (a, b) for the monomial x^a y^b
Poly = list[Term]               # a polynomial is a list of monomial terms


def shift_matrix(size: int, power: int) -> np.ndarray:
    """The size x size cyclic-shift permutation S^power: (S^p)[i,j] = 1 iff i == (j+p) mod size."""
    p = power % size
    M = np.zeros((size, size), dtype=np.uint8)
    for j in range(size):
        M[(j + p) % size, j] = 1
    return M


def monomial_matrix(l: int, m: int, a: int, b: int) -> np.ndarray:
    """The (l*m) x (l*m) matrix of x^a y^b = S_l^a (x) kron S_m^b (y)."""
    return np.kron(shift_matrix(l, a), shift_matrix(m, b)).astype(np.uint8)


def poly_matrix(l: int, m: int, terms: Poly) -> np.ndarray:
    """Circulant matrix of a polynomial (mod-2 sum of its monomial matrices)."""
    M = np.zeros((l * m, l * m), dtype=np.uint8)
    for (a, b) in terms:
        M ^= monomial_matrix(l, m, a, b)
    return M


def normalize_terms(terms: Poly, l: int, m: int) -> Poly:
    """Reduce exponents mod (l, m) and drop terms that cancel mod 2; sorted, deduped."""
    counts: dict[Term, int] = {}
    for (a, b) in terms:
        key = (a % l, b % m)
        counts[key] = counts.get(key, 0) + 1
    return sorted(t for t, c in counts.items() if c % 2 == 1)


def parse_poly(expr: str, l: int | None = None, m: int | None = None) -> Poly:
    """Parse a polynomial string like '1+y+y^2+x^3' or 'x^6+y+y^2' into terms.

    Accepts '+' separated monomials; each monomial is a product of x^a / y^b /
    bare x,y / constant 1. '^' optional ('x3' == 'x^3'). If l,m given, normalizes.
    """
    terms: Poly = []
    for raw in expr.replace("{", "").replace("}", "").split("+"):
        token = raw.strip().replace(" ", "")
        if not token:
            continue
        a = b = 0
        for var, exp in re.findall(r"([xy])\^?(\d*)", token):
            e = int(exp) if exp else 1
            if var == "x":
                a += e
            else:
                b += e
        terms.append((a, b))
    if l is not None and m is not None:
        return normalize_terms(terms, l, m)
    return terms


def poly_weight(terms: Poly, l: int, m: int) -> int:
    """Number of distinct monomials after mod-2 reduction (the polynomial Hamming weight)."""
    return len(normalize_terms(terms, l, m))
