"""Staged evaluation cascade — the BLIND fitness function for code discovery.

Catalog-blind by construction: this module imports ONLY the kernel verifiers
(construction, k via GF(2) rank, MILP/enum distance, FOM). It NEVER reads the paper
catalog or any reported [[n,k,d]] (see blind_discovery_policy). A candidate's fitness
is computed from first principles, exactly as the paper's pipeline does:
  Stage 1 (cheap):   k via GF(2) rank — reject k = 0.
  Stage 2 (costly):  distance via MILP (exact at gap=0) or exhaustive enumeration.
  FOM = k d^2 / n;  d/sqrt(n) reported for the trust heuristic.
Paper anchor: arXiv:2606.02418 sec IV.B (cascade), sec II.C (FOM), sec V.D (trust). R2.
"""
from __future__ import annotations

import math

from .bb_codes import BBCode
from .pbb_codes import PBBCode
from .metrics import css_k, fom
from .distance_milp import css_distance_milp, symplectic_distance_milp
from .distance_enum import css_distance_enum


def screen_k_css(l: int, m: int, A, B) -> int:
    """Stage 1: encoding dimension k of the CSS BB code (GF(2) rank). 0 => discard."""
    code = BBCode(l, m, A, B)
    return css_k(code.HX, code.HZ)


def evaluate_css(l, m, A, B, distance_method: str = "milp", time_limit: float = 3.0,
                 enum_max_weight: int = 6, max_logicals=None) -> dict:
    """Full blind evaluation of a CSS BB candidate. Returns a typed result dict.

    distance_method: 'milp' (scipy/HiGHS; exact at gap=0) or 'enum' (exhaustive, small codes).
    No paper knowledge used; the candidate (A,B) is the only input.
    """
    code = BBCode(l, m, A, B)
    k = css_k(code.HX, code.HZ)
    res = {"l": l, "m": m, "n": code.n, "k": k, "A": list(code.A_terms), "B": list(code.B_terms),
           "stab_weight": code.stabilizer_weight, "d": None, "exact": False, "fom": 0.0,
           "d_over_sqrt_n": None, "stage": 1}
    if k == 0:
        return res                                    # Stage-1 reject
    res["stage"] = 2
    if distance_method == "enum":
        dres = css_distance_enum(code, max_weight=enum_max_weight)
        res["d"], res["exact"] = dres["d"], dres["exhausted"]
    elif distance_method == "bposd":                  # fast Stage-2 estimator (UPPER bound, not exact)
        from .distance_bposd import bposd_distance
        dres = bposd_distance(code, trials=int(time_limit * 100) or 100)
        res["d"], res["exact"] = dres["d_bound"], False
    else:
        dres = css_distance_milp(code, time_limit=time_limit, max_logicals=max_logicals)
        res["d"], res["exact"] = dres["d"], dres["exact"]
    if res["d"]:
        res["fom"] = fom(code.n, k, res["d"])
        res["d_over_sqrt_n"] = res["d"] / math.sqrt(code.n)
        res["trusted"] = res["d_over_sqrt_n"] < 2.0    # paper's trust filter (Sec V.D): >=2.0 discarded
    return res


def evaluate_pbb(l, m, A, B, C, D, time_limit: float = 5.0, max_logicals=None) -> dict:
    """Full blind evaluation of a non-CSS PBB candidate (symplectic distance). Returns typed dict.

    Returns {valid: False} if the 4-tuple fails the commutativity constraint (most random tuples do).
    """
    try:
        code = PBBCode(l, m, A, B, C, D)
    except ValueError:
        return {"valid": False, "reason": "non-commuting (A C^T + B D^T not symmetric)"}
    k = code.k
    res = {"valid": True, "l": l, "m": m, "n": code.n, "k": k, "d": None, "exact": False,
           "fom": 0.0, "d_over_sqrt_n": None, "non_css": code.has_mixed_generator()}
    if k == 0:
        return res
    dres = symplectic_distance_milp(code, time_limit=time_limit, max_logicals=max_logicals)
    res["d"], res["exact"] = dres["d"], dres["exact"]
    if res["d"]:
        res["fom"] = fom(code.n, k, res["d"])
        res["d_over_sqrt_n"] = res["d"] / math.sqrt(code.n)
    return res
