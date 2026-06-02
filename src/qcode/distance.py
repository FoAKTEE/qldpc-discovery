"""Distance computation for CSS codes, two independent methods.

The CSS code distance is the minimum Hamming weight of a nontrivial logical
operator.  For the X-type logicals:
    minimise |x|   over x in F2^n
    s.t.  H_Z x = 0  (mod 2)            [x is a Z-stabiliser-commuting X op]
          x not in rowspace(H_X)        [x is not itself a stabiliser]
and symmetrically for Z-type (swap X<->Z).  d = min over both types.

We provide:

1) ``distance_enum`` — exhaustive low-weight enumeration.  For each logical
   type we enumerate candidate supports of increasing weight w = 1, 2, ...
   and test the two conditions.  To make this tractable we DO NOT enumerate
   all C(n, w) supports directly; instead we use the coset structure: every
   logical is (stabiliser) + (one of the k logical-coset representatives).  We
   enumerate F2-combinations of a logical basis (2^k of them) XORed against a
   bounded number of low-weight stabiliser combinations.  For the small codes
   here (k small) this is exact when we can afford the full stabiliser sweep;
   otherwise we fall back to a guaranteed-correct meet-in-the-middle / coset
   leader search over the logical generators combined with stabiliser
   generators up to a weight bound.

   The robust, provably-exact variant we actually rely on for small n is
   ``distance_enum_bruteforce`` which enumerates information-set style: it walks
   all 2^k logical combinations and reduces each against the stabiliser group by
   a greedy + bounded search.  Because that is only a heuristic upper bound, we
   ALSO provide the MILP which is exact.

2) ``distance_milp`` — exact minimum distance via integer programming with
   HiGHS (scipy.optimize.milp).  Models the mod-2 constraints with integer
   slack variables.  Gap=0 from the solver certifies the exact distance.

The two are cross-checked against each other.
"""

from __future__ import annotations

import itertools

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

from . import gf2


# ----------------------------------------------------------------------------
# Exhaustive enumeration (exact for small n via coset-leader over logical basis)
# ----------------------------------------------------------------------------
def _logical_basis(H_perp, H_stab):
    """Basis of {x : H_perp x = 0} / rowspace(H_stab).

    Returns logical coset representatives (rows) that, together with
    rowspace(H_stab), span ker(H_perp).  Number of rows = k.
    """
    ker = gf2.null_space(H_perp)          # rows span ker(H_perp)
    stab = gf2.row_space_basis(H_stab)    # independent stabiliser rows
    n = H_perp.shape[1]
    # Greedily extend the stabiliser basis to a basis of ker(H_perp).
    # Vectors added beyond the stabilisers are the logical representatives.
    rows = [r.copy() for r in stab]
    cur_rank = gf2.rank(np.array(rows, dtype=np.uint8)) if rows else 0
    log_reps = []
    for v in ker:
        trial = rows + [v]
        new_rank = gf2.rank(np.array(trial, dtype=np.uint8))
        if new_rank > cur_rank:
            rows.append(v.copy())
            log_reps.append(v.copy())
            cur_rank = new_rank
    if not log_reps:
        return np.zeros((0, n), dtype=np.uint8), stab
    return np.array(log_reps, dtype=np.uint8), stab


def _min_weight_in_coset_bruteforce(log_reps, stab, max_stab_combo=None):
    """Exact min nonzero weight over all (logical combo) XOR (stabiliser combo).

    Enumerates all 2^k nonzero logical combinations and all 2^s stabiliser
    combinations (s = #stabiliser generators).  Exact but cost 2^(k+s).  Only
    use when k+s is small.
    """
    k = log_reps.shape[0]
    s = stab.shape[0]
    n = log_reps.shape[1] if k else (stab.shape[1] if s else 0)
    best = None
    # precompute stabiliser combinations as bit operations
    stab_combos = []
    for sc in range(1 << s):
        v = np.zeros(n, dtype=np.uint8)
        for i in range(s):
            if sc & (1 << i):
                v ^= stab[i]
        stab_combos.append(v)
    for lc in range(1, 1 << k):
        base = np.zeros(n, dtype=np.uint8)
        for i in range(k):
            if lc & (1 << i):
                base ^= log_reps[i]
        # logical combo is nontrivial by construction; minimise over stabilisers
        for sv in stab_combos:
            w = int(np.count_nonzero(base ^ sv))
            if best is None or w < best:
                best = w
    return best


def distance_ub_random(code, n_trials=4000, seed=0):
    """Fast randomized UPPER BOUND on the CSS distance.

    Idea (probabilistic / information-set style): every nontrivial logical is a
    coset element  logical_combo XOR stabiliser_combo.  We sample random nonzero
    logical combinations and random stabiliser combinations, XOR them, and track
    the minimum Hamming weight seen.  This NEVER underestimates the true distance
    (every sampled vector is a genuine nontrivial logical, so its weight >= d),
    so it is a valid upper bound, and with enough trials it tends to hit low.

    Vectorised over trials with numpy.  Returns (ub, info) where info records the
    best vector and its type.  Used only for screening/ranking; exactness comes
    from the MILP / low-weight enumeration.
    """
    rng = np.random.default_rng(seed)
    HZ = np.asarray(code.HZ, dtype=np.uint8)
    HX = np.asarray(code.HX, dtype=np.uint8)
    best = None
    best_info = None
    for label, log_reps, stab in [
        ("X", *(_logical_basis(HZ, HX))),
        ("Z", *(_logical_basis(HX, HZ))),
    ]:
        k = log_reps.shape[0]
        s = stab.shape[0]
        if k == 0:
            continue
        n = log_reps.shape[1]
        # random nonzero logical coefficient vectors (k-bit), trials x k
        Lc = rng.integers(0, 2, size=(n_trials, k)).astype(np.uint8)
        # ensure nonzero rows: where all-zero, set first bit
        zero_rows = ~Lc.any(axis=1)
        Lc[zero_rows, 0] = 1
        # random stabiliser coefficient vectors, trials x s
        if s > 0:
            Sc = rng.integers(0, 2, size=(n_trials, s)).astype(np.uint8)
        # vectors = Lc @ log_reps (mod2) XOR Sc @ stab (mod2)
        V = (Lc.astype(np.int64) @ log_reps.astype(np.int64)) & 1
        if s > 0:
            V ^= (Sc.astype(np.int64) @ stab.astype(np.int64)) & 1
        weights = V.sum(axis=1)
        idx = int(np.argmin(weights))
        w = int(weights[idx])
        if w > 0 and (best is None or w < best):
            best = w
            best_info = (label, V[idx].astype(np.uint8))
    return best, {"best": best_info}


def distance_lowweight(code, wmax, return_vector=False):
    """Independent exact low-weight search by enumerating supports directly.

    For weight w = 1, 2, ..., wmax we enumerate every support of size w (C(n,w)
    of them) and test whether the indicator vector x is a nontrivial logical of
    either type:
        X-type: H_Z x = 0 (mod 2) and x anticommutes with some Z-logical rep.
        Z-type: H_X x = 0 (mod 2) and x anticommutes with some X-logical rep.
    Returns (d, found) where found=True iff a logical of weight <= wmax exists.
    If found is False, d == wmax+1 sentinel meaning "distance > wmax".

    This is provably exact up to wmax and is INDEPENDENT of the MILP and of the
    coset-group enumeration, so it is our primary cross-check at larger n (for
    the small distances we expect).
    """
    n = code.n
    HZ = np.asarray(code.HZ, dtype=np.uint8)
    HX = np.asarray(code.HX, dtype=np.uint8)
    # dual logical reps for each type
    zlog, _ = _logical_basis(HX, HZ)   # Z-logicals (in ker H_X)
    xlog, _ = _logical_basis(HZ, HX)   # X-logicals (in ker H_Z)
    # For an X-type candidate x: need HZ x = 0 and exists zrep with <zrep,x>=1.
    # For a Z-type candidate x: need HX x = 0 and exists xrep with <xrep,x>=1.
    best = None
    best_vec = None
    cols = np.arange(n)
    for w in range(1, wmax + 1):
        for support in itertools.combinations(cols, w):
            x = np.zeros(n, dtype=np.uint8)
            x[list(support)] = 1
            # X-type
            if not (HZ @ x & 1).any():
                if zlog.shape[0] and ((zlog @ x) & 1).any():
                    best = w; best_vec = ("X", x.copy()); break
            # Z-type
            if not (HX @ x & 1).any():
                if xlog.shape[0] and ((xlog @ x) & 1).any():
                    best = w; best_vec = ("Z", x.copy()); break
        if best is not None:
            break
    if best is None:
        if return_vector:
            return wmax + 1, False, None
        return wmax + 1, False
    if return_vector:
        return best, True, best_vec
    return best, True


def distance_lowweight_vec(code, wmax, chunk=300000, return_vector=False):
    """Vectorised EXACT low-weight enumeration (same semantics as
    distance_lowweight, but batched with numpy so it scales to n=72..144 for
    small wmax).  For each weight w=1..wmax we enumerate all C(n,w) supports in
    chunks, build the indicator matrix, and test both logical-type conditions
    with batched F2 matrix products.  Provably exact up to wmax.

    Returns (d, found[, ("X"/"Z", vec)]).  If no logical of weight <= wmax,
    returns (wmax+1, False).
    """
    n = code.n
    HZ = np.asarray(code.HZ, dtype=np.int64)
    HX = np.asarray(code.HX, dtype=np.int64)
    zlog, _ = _logical_basis(HX, HZ)
    xlog, _ = _logical_basis(HZ, HX)
    zlog = zlog.astype(np.int64)
    xlog = xlog.astype(np.int64)
    for w in range(1, wmax + 1):
        combos = itertools.combinations(range(n), w)
        while True:
            batch = list(itertools.islice(combos, chunk))
            if not batch:
                break
            B = np.array(batch, dtype=np.int64)          # (m, w)
            m = B.shape[0]
            X = np.zeros((m, n), dtype=np.int64)
            X[np.arange(m)[:, None], B] = 1
            Xt = X.T                                     # (n, m)
            # X-type: HZ x = 0 and anticommute with some z-logical
            sZ = (HZ @ Xt) & 1
            okX = ~(sZ.any(axis=0))
            if zlog.shape[0]:
                antiX = ((zlog @ Xt) & 1).any(axis=0)
            else:
                antiX = np.zeros(m, dtype=bool)
            hitX = okX & antiX
            # Z-type
            sX = (HX @ Xt) & 1
            okZ = ~(sX.any(axis=0))
            if xlog.shape[0]:
                antiZ = ((xlog @ Xt) & 1).any(axis=0)
            else:
                antiZ = np.zeros(m, dtype=bool)
            hitZ = okZ & antiZ
            if hitX.any():
                i = int(np.argmax(hitX))
                if return_vector:
                    return w, True, ("X", X[i].astype(np.uint8))
                return w, True
            if hitZ.any():
                i = int(np.argmax(hitZ))
                if return_vector:
                    return w, True, ("Z", X[i].astype(np.uint8))
                return w, True
    if return_vector:
        return wmax + 1, False, None
    return wmax + 1, False


def distance_enum(code, max_kplus_s=22):
    """Exhaustive (exact) distance via coset enumeration, for small codes.

    Returns (d, info).  Feasible only when k + (#stab generators) <= max_kplus_s
    for BOTH logical types.  Raises if too large.
    """
    results = {}
    for label, Hperp, Hstab in [("X", code.HZ, code.HX), ("Z", code.HX, code.HZ)]:
        log_reps, stab = _logical_basis(Hperp, Hstab)
        k = log_reps.shape[0]
        s = stab.shape[0]
        if k + s > max_kplus_s:
            raise ValueError(
                f"enumeration too large: k+s={k+s} > {max_kplus_s} for type {label}"
            )
        d = _min_weight_in_coset_bruteforce(log_reps, stab)
        results[label] = d
    d = min(results["X"], results["Z"])
    return d, results


# ----------------------------------------------------------------------------
# Exact MILP minimum distance via HiGHS
# ----------------------------------------------------------------------------
def _milp_min_weight_one_type(Hperp, Hstab, time_limit=None, weight_floor=0,
                              deadline=None):
    """Exact minimum weight of a vector x with:
        Hperp x = 0 (mod 2)
        x not in rowspace(Hstab)   -- enforced by anticommuting with some dual
    Strategy: a logical X-operator must anticommute with at least one Z-logical
    representative.  We enumerate the k dual-logical representatives; for each we
    require <dual_j, x> = 1 (mod 2) AND Hperp x = 0 (mod 2), minimise |x|.  The
    minimum over j of these is the X-distance (a vector in ker(Hperp) is a
    nontrivial logical iff it anticommutes with at least one dual logical, and
    its weight is counted for the j it anticommutes with).

    Returns (best_value, certified_exact).  certified_exact = True iff every
    sub-MILP closed with gap 0.
    """
    n = Hperp.shape[1]
    # dual logical representatives = logical basis of the OPPOSITE type living
    # in ker(Hstab) mod rowspace(Hperp).
    dual_reps, _ = _logical_basis(Hstab, Hperp)
    if dual_reps.shape[0] == 0:
        return None, True  # k=0, no logicals
    best = None
    all_exact = True
    Hperp = np.asarray(Hperp, dtype=np.int64)
    nr = Hperp.shape[0]
    import time as _time

    for j in range(dual_reps.shape[0]):
        # Global wall-clock cap across sub-problems: if exceeded, stop refining
        # (the remaining sub-problems are not solved -> not certified exact).
        if deadline is not None and _time.time() > deadline:
            all_exact = False
            break
        dvec = dual_reps[j].astype(np.int64)
        # Variables: x (n binary), then integer slacks t for each mod-2 eq.
        # Constraints:
        #   Hperp x - 2 t = 0           (nr constraints, t integer >=0)
        #   dvec . x - 2 u = 1          (1 constraint, u integer >=0)
        # Objective: minimise sum x.
        n_slack = nr + 1
        nvar = n + n_slack
        c = np.zeros(nvar)
        c[:n] = 1.0
        # bounds
        lb = np.zeros(nvar)
        ub = np.ones(nvar)
        ub[n:] = np.inf  # slacks unbounded above
        bounds = Bounds(lb, ub)
        integrality = np.ones(nvar)  # all integer (x binary via 0/1 bounds)

        # Build constraint matrix
        rows = []
        lo = []
        hi = []
        for i in range(nr):
            row = np.zeros(nvar)
            row[:n] = Hperp[i]
            row[n + i] = -2.0
            rows.append(row)
            lo.append(0.0)
            hi.append(0.0)
        row = np.zeros(nvar)
        row[:n] = dvec
        row[n + nr] = -2.0
        rows.append(row)
        lo.append(1.0)
        hi.append(1.0)
        # Weight window cut  lo_w <= sum(x) <= hi_w.
        #   lo_w = weight_floor  (proven lower bound, sound when supplied);
        #   hi_w = best - 1      (incumbent sharing: this sub-problem only matters
        #          if it can beat the best found in earlier sub-problems, since the
        #          type distance is the MIN over sub-problems).  This prunes hard.
        lo_w = float(weight_floor) if (weight_floor and weight_floor > 0) else None
        hi_w = float(best - 1) if best is not None else None
        if lo_w is not None or hi_w is not None:
            row = np.zeros(nvar)
            row[:n] = 1.0
            rows.append(row)
            lo.append(lo_w if lo_w is not None else 0.0)
            hi.append(hi_w if hi_w is not None else np.inf)
            # If the window is empty (lo_w > hi_w) this sub-problem cannot beat
            # the incumbent; skip it (sound, and certified).
            if lo_w is not None and hi_w is not None and lo_w > hi_w:
                continue
        Acon = np.array(rows)
        cons = LinearConstraint(Acon, lo, hi)

        opts = {}
        # Effective per-sub-problem limit honours both the per-call time_limit and
        # the remaining global budget.
        eff_limit = time_limit
        if deadline is not None:
            remaining = max(0.5, deadline - _time.time())
            eff_limit = remaining if eff_limit is None else min(eff_limit, remaining)
        if eff_limit is not None:
            opts["time_limit"] = eff_limit
        res = milp(c=c, constraints=cons, integrality=integrality,
                   bounds=bounds, options=opts)
        # scipy/HiGHS status codes:
        #   0 = optimal (gap closed),
        #   2 = infeasible  -> with the hi_w cut this CERTIFIES "no logical lighter
        #       than the incumbent exists in this sub-problem" (exact information),
        #   1/4 = iteration/time limit or other  -> NOT closed (lose exactness).
        if res.status == 2:
            # certified: this sub-problem cannot improve the incumbent.
            continue
        if res.status != 0:
            all_exact = False
            if res.x is not None:
                val = int(round(res.x[:n].sum()))
                if best is None or val < best:
                    best = val
            continue
        if res.x is None:
            # optimal but no solution returned (shouldn't happen for feasible)
            continue
        val = int(round(res.x[:n].sum()))
        if best is None or val < best:
            best = val
    return best, all_exact


def distance_milp(code, time_limit=None, weight_floor=0, total_time_budget=None):
    """Exact CSS distance via MILP (HiGHS).  Returns (d, info_dict).

    info_dict has per-type value and whether it was certified exact (gap 0).
    ``weight_floor`` adds a sound lower-bound cut sum(x) >= weight_floor; only
    pass a value that is a PROVEN lower bound on the distance.
    ``total_time_budget`` (seconds) caps the total wall time across BOTH types so
    a single hard code cannot stall a search; if hit, the result is an honest
    upper bound (certified_exact=False).
    """
    import time as _time
    info = {}
    deadline = (_time.time() + total_time_budget) if total_time_budget else None
    dX, exX = _milp_min_weight_one_type(code.HZ, code.HX, time_limit,
                                        weight_floor=weight_floor,
                                        deadline=deadline)
    dZ, exZ = _milp_min_weight_one_type(code.HX, code.HZ, time_limit,
                                        weight_floor=weight_floor,
                                        deadline=deadline)
    info["X"] = (dX, exX)
    info["Z"] = (dZ, exZ)
    vals = [v for v in (dX, dZ) if v is not None]
    if not vals:
        return None, info
    d = min(vals)
    info["certified_exact"] = exX and exZ
    return d, info
