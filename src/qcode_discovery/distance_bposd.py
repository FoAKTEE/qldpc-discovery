"""BP-OSD stochastic distance UPPER bound (component 7; the paper's fast in-loop estimator).

arXiv:2606.02418 sec V.A/C: form H_eff = (H_check ; L) (checks stacked above logicals), fix the
stabilizer syndrome to zero, pick a random nontrivial logical coset lambda, decode (0, lambda),
and record the decoded weight. The minimum over trials/configs is an UPPER bound on d (the paper
shows it can overestimate by up to 12x for high-rate codes — hence MILP for exact). Modality:
StatisticalInference (upper bound), never promoted to exact. Requires the `ldpc` library. R3.
"""
from __future__ import annotations

import random

import numpy as np

from .metrics import css_logicals

# (bp_method, osd_method, osd_order) — the paper's multi-decoder protocol.
_DEFAULT_CONFIGS = (("product_sum", "osd_cs", 10), ("minimum_sum", "osd_cs", 10))


def _bposd_one_type(check, logicals, n, trials, configs, seed):
    from ldpc import BpOsdDecoder           # imported lazily (optional dependency)
    check = (np.asarray(check, np.uint8) & 1)
    logicals = (np.asarray(logicals, np.uint8) & 1)
    m, k = check.shape[0], logicals.shape[0]
    if k == 0:
        return None
    Heff = np.vstack([check, logicals]).astype(np.uint8)
    rng = random.Random(seed)
    best = None
    for (bp_method, osd_method, osd_order) in configs:
        try:
            dec = BpOsdDecoder(Heff, error_rate=0.05, bp_method=bp_method, max_iter=n,
                               osd_method=osd_method, osd_order=osd_order)
        except Exception:
            continue
        for _ in range(trials):
            lam = np.array([rng.randint(0, 1) for _ in range(k)], np.uint8)
            if not lam.any():
                continue
            s = np.concatenate([np.zeros(m, np.uint8), lam])
            e = dec.decode(s)
            if np.array_equal((Heff @ e) & 1, s):
                w = int(e.sum())
                best = w if best is None else min(best, w)
    return best


def bposd_distance(code, trials: int = 200, configs=_DEFAULT_CONFIGS, seed: int = 0) -> dict:
    """BP-OSD upper bound on the CSS distance d = min(d_X, d_Z). Stochastic; an UPPER bound only."""
    X, Z = css_logicals(code.HX, code.HZ)
    dX = _bposd_one_type(code.HZ, X, code.n, trials, configs, seed)        # X-logicals: H_Z x = 0
    dZ = _bposd_one_type(code.HX, Z, code.n, trials, configs, seed + 1)    # Z-logicals: H_X z = 0
    cand = [v for v in (dX, dZ) if v is not None]
    return {"d_bound": min(cand) if cand else None, "d_X": dX, "d_Z": dZ,
            "modality": "StatisticalInference(upper-bound)"}
