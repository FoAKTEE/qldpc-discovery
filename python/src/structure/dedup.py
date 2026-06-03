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


def bliss_canonical_hash(HX, HZ) -> str:
    """Exact colored-Tanner-graph canonical hash via igraph/BLISS (the paper's dedup method).

    Vertices: qubits (color 0), X-checks (color 1), Z-checks (color 2); edges check->qubit.
    Two CSS codes are permutation-equivalent (qubit relabeling preserving X/Z-check roles) iff
    their canonical hashes match — SOUND and COMPLETE for that equivalence. Requires python-igraph.
    """
    import hashlib
    import igraph
    import numpy as np
    HX = (np.asarray(HX, np.uint8) & 1)
    HZ = (np.asarray(HZ, np.uint8) & 1)
    n, rx, rz = HX.shape[1], HX.shape[0], HZ.shape[0]
    N = n + rx + rz
    colors = [0] * n + [1] * rx + [2] * rz
    edges = []
    for c in range(rx):
        for q in np.flatnonzero(HX[c]):
            edges.append((n + c, int(q)))
    for c in range(rz):
        for q in np.flatnonzero(HZ[c]):
            edges.append((n + rx + c, int(q)))
    g = igraph.Graph(n=N, edges=edges)
    perm = g.canonical_permutation(color=colors)      # BLISS color-respecting canonical labeling
    g2 = g.permute_vertices(perm)
    new_colors = [0] * N
    for i, c in enumerate(colors):
        new_colors[perm[i]] = c
    sig = (tuple(new_colors), tuple(sorted(g2.get_edgelist())))
    return hashlib.sha256(repr(sig).encode()).hexdigest()[:32]


def dedup_bliss(codes) -> dict:
    """Exact permutation-equivalence dedup via igraph/BLISS. codes: objects with .HX/.HZ.

    Returns {representatives, classes (hash -> [indices]), n_distinct}. Unlike dedup_bb (a sound
    lattice-symmetry UNDER-approximation giving an upper bound), this is the exact distinct-count.
    """
    classes: dict = {}
    for i, c in enumerate(codes):
        h = bliss_canonical_hash(c.HX, c.HZ)
        classes.setdefault(h, []).append(i)
    reps = sorted(idxs[0] for idxs in classes.values())
    return {"representatives": reps, "classes": classes, "n_distinct": len(classes)}


def dedup_bb(codes) -> dict:
    """Group BB codes by lattice-symmetry equivalence. codes: objects with .l/.m/.A_terms/.B_terms.

    Returns {representatives, classes (signature -> [indices]), n_distinct}. n_distinct is a
    conservative UPPER bound on the true permutation-distinct count (see module docstring).
    """
    classes: dict = {}
    for i, c in enumerate(codes):
        # key includes (l,m): identical polynomials at different lattices are DIFFERENT codes
        # (different n). Cross-lattice Tanner isomorphism is caught by dedup_bliss, not here.
        sig = (c.l, c.m, canonical_poly_signature(c.l, c.m, c.A_terms, c.B_terms))
        classes.setdefault(sig, []).append(i)
    reps = sorted(idxs[0] for idxs in classes.values())
    return {"representatives": reps, "classes": classes, "n_distinct": len(classes)}
