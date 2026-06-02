"""Deduplication of discovered BB codes by lattice-symmetry equivalence (BLISS fallback).

arXiv:2606.02418 sec VI.A dedups by colored-Tanner-graph canonical form via BLISS (python-igraph,
absent here). A cheap 1-WL histogram is USELESS for these graphs: BB Tanner graphs are bi-regular,
so 1-WL collapses to the trivial type-coloring and rates all same-shape codes equal (verified
over-merge). Instead we canonicalize under the explicit lattice-symmetry group of BB codes:
  - exponent re-indexing x -> x^a (a coprime l), y -> y^b (b coprime m)  [the "x->x^a" symmetry the paper notes];
  - x <-> y swap (when l = m);
  - A <-> B swap (qubit-block swap: BB(A,B) ~ BB(B,A)).
Same canonical signature  <=>  equivalent under this group (SOUND). This group is a SUBSET of
full Tanner permutation equivalence, so the distinct-count is a conservative UPPER bound (the
paper frames its 465 the same way). Full BLISS canonical labeling via python-igraph is [FUTURE]. R3.
"""
from __future__ import annotations

from math import gcd


def _units(n: int) -> list[int]:
    """Multiplicative units mod n (a with gcd(a,n)=1): the bijective exponent re-indexings."""
    return [a for a in range(1, n + 1) if gcd(a, n) == 1]


def canonical_poly_signature(l: int, m: int, A_terms, B_terms):
    """Canonical (lattice-symmetry-invariant) signature of a BB code's polynomial pair.

    Two BB codes share this signature iff they are related by x->x^a, y->y^b, x<->y (if l=m),
    or A<->B. SOUND for equivalence (a hash difference certifies distinctness).
    """
    A = {(i % l, j % m) for (i, j) in A_terms}
    B = {(i % l, j % m) for (i, j) in B_terms}
    best = None
    for a in _units(l):
        for b in _units(m):
            Ag = frozenset(((a * i) % l, (b * j) % m) for (i, j) in A)
            Bg = frozenset(((a * i) % l, (b * j) % m) for (i, j) in B)
            forms = [(Ag, Bg), (Bg, Ag)]                       # A<->B qubit-block swap
            if l == m:
                At = frozenset((j, i) for (i, j) in Ag)
                Bt = frozenset((j, i) for (i, j) in Bg)
                forms += [(At, Bt), (Bt, At)]                  # x<->y swap
            for (P, Q) in forms:
                key = (tuple(sorted(P)), tuple(sorted(Q)))
                if best is None or key < best:
                    best = key
    return best


def dedup_bb(codes) -> dict:
    """Group BB codes by lattice-symmetry equivalence. codes: objects with .l/.m/.A_terms/.B_terms.

    Returns {representatives, classes (signature -> [indices]), n_distinct}. n_distinct is a
    conservative UPPER bound on the true permutation-distinct count (see module docstring).
    """
    classes: dict = {}
    for i, c in enumerate(codes):
        sig = canonical_poly_signature(c.l, c.m, c.A_terms, c.B_terms)
        classes.setdefault(sig, []).append(i)
    reps = sorted(idxs[0] for idxs in classes.values())
    return {"representatives": reps, "classes": classes, "n_distinct": len(classes)}
