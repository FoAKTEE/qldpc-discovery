"""Local-Clifford CSS-equivalence checks for non-CSS (PBB) codes.

Post-campaign verifier (arXiv:2606.02418 App. E): decide whether a non-CSS code is secretly
CSS under single-qubit Cliffords, so the search does not over-count CSS-equivalent codes.
This module implements the two fully-derived, polynomial-time pieces:
  - Hadamard 2-coloring (generator-level): some per-qubit H pattern makes every supplied
    generator pure-X or pure-Z  iff  no generator has Y support AND the parity constraint
    graph is 2-colorable (decided by union-find with parity).
  - the group-CSS rank condition (Lemma 7.4): rank[X|Z] = rankX + rankZ (in pbb_codes.is_css_group).
The full per-qubit {I,S}/{H,HS} affine enumeration and the (a)/(b) coverage gaps are [FUTURE]. R3.
"""
from __future__ import annotations

import numpy as np

from . import gf2


class _ParityUF:
    """Union-find with parity: tracks each node's bit relative to its component root."""

    def __init__(self, size: int):
        self.parent = list(range(size))
        self.par = [0] * size                       # parity relative to parent

    def find(self, x: int):
        """Return (root, parity_of_x_relative_to_root)."""
        if self.parent[x] == x:
            return x, 0
        root, p = self.find(self.parent[x])
        self.parent[x] = root
        self.par[x] ^= p
        return root, self.par[x]

    def union(self, x: int, y: int, parity: int) -> bool:
        """Constrain bit(x) XOR bit(y) = parity. Return False on contradiction."""
        rx, px = self.find(x)
        ry, py = self.find(y)
        if rx == ry:
            return (px ^ py) == parity
        self.parent[rx] = ry
        self.par[rx] = px ^ py ^ parity
        return True


def hadamard_two_coloring(SX: np.ndarray, SZ: np.ndarray) -> dict:
    """Decide if some single-qubit-Hadamard pattern H_J makes every supplied generator pure-X/pure-Z.

    SX, SZ: (#generators x n) binary X- and Z-support of each generator. Returns
    {feasible, y_obstruction, H_pattern}. Constraint per (gen r, qubit j in supp): with local
    type t = SZ[r,j] (0=X,1=Z) and unknown generator target c_r and unknown qubit-flip s_j,
    s_j XOR c_r = t  (App. E). Union-find with parity over (qubits + generators) decides it.
    """
    SX = (np.asarray(SX, np.uint8) & 1)
    SZ = (np.asarray(SZ, np.uint8) & 1)
    R, n = SX.shape
    if ((SX & SZ).any()):                            # some generator has Y on some qubit
        return {"feasible": False, "y_obstruction": True, "H_pattern": None}
    uf = _ParityUF(n + R)                            # nodes 0..n-1 qubits, n..n+R-1 generators
    for r in range(R):
        for j in np.flatnonzero(SX[r] | SZ[r]):
            t = int(SZ[r, j])                        # 1 if Z on (r,j), 0 if X
            if not uf.union(int(j), n + r, t):       # s_j XOR c_r = t
                return {"feasible": False, "y_obstruction": False, "H_pattern": None}
    # Recover an H pattern: each component's root := 0; qubit's bit is its parity-to-root.
    pattern = np.array([uf.find(j)[1] for j in range(n)], dtype=np.uint8)
    return {"feasible": True, "y_obstruction": False, "H_pattern": pattern}


def lc_css_classify(code) -> dict:
    """Classify a PBBCode's CSS-equivalence under the tested single-qubit-Clifford families.

    Returns {verdict, ...}: 'CSS_GROUP' (already CSS via rank condition), 'HADAMARD_CSS'
    (a per-qubit H pattern makes the generators CSS), or 'CSS_INEQUIVALENT_TESTED' (neither;
    residual {S}/{SH,HSH} non-uniform families are [FUTURE], so this is "within tested families").
    """
    n = code.n
    SX, SZ = code.S[:, :n], code.S[:, n:]
    if code.is_css_group():
        return {"verdict": "CSS_GROUP", "hadamard": None}
    had = hadamard_two_coloring(SX, SZ)
    if had["feasible"]:
        return {"verdict": "HADAMARD_CSS", "hadamard": had, "H_weight": int(had["H_pattern"].sum())}
    return {"verdict": "CSS_INEQUIVALENT_TESTED", "hadamard": had}
