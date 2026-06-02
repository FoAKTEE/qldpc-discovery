"""Rigorous high-distance search at n=144 (and n=288) for BB CSS codes.

The randomized UB (distance_ub_random) is USELESS as a ranking tool here: on
random diagonal codes it returns 46-48 (it just fails to sample a light logical),
so a large UB says nothing about the true distance.  The reliable instrument is
the CAPPED-MILP FEASIBILITY query (exp_certlb._type_geq_T): for a target T it
either returns an explicit logical of weight <= T-1 (a PROVEN upper bound, hence
the true d < T) or proves every sub-problem infeasible (a PROVEN lower bound
d >= T).  HiGHS resolves these tight feasibility instances far faster than the
open minimisation, and they are rigorous either way.

Pipeline per lattice:
  Stage A   sample diagonal trinomial pairs (both non-constant monomials of A and
            of B carry nonzero x AND y exponents -- the structural family our own
            (6,6) data showed reaches the highest distance); screen k>=kmin by
            two F2 ranks; reject d<=2 by exhaustive w<=2 enumeration.  Cheap.
  Stage B   for each survivor, run the certification LADDER: probe d>=T for
            T = T_lo .. T_hi.  Stop early at the first T where a witness of
            weight <= T-1 appears (that weight is the exact distance if it equals
            the largest T already certified, else just an upper bound; we record
            both the proven LB d>=cert_lb and the witness weight as UB).  This
            brackets each code's distance HONESTLY:  cert_lb <= d <= witness_w.
  Stage C   checkpoint after every code; store l,m,A,B,k,cert_lb,ub,witness so a
            stronger certifier can re-load and tighten the best survivors.

Run:  PYTHONPATH=src python3 -u exp_n144.py <l> <m> [key=val ...]
"""
import sys
import time
import json
import random

from qcode import bb, distance
from exp_certlb import _type_geq_T


def bracket_distance(c, T_lo=3, T_hi=12, time_limit=20, total_budget=180):
    """Return (cert_lb, ub, info).

    cert_lb: largest T such that d >= T is PROVEN (every sub-problem infeasible).
    ub:      smallest witness weight found (PROVEN upper bound on d), or None if
             no witness was found up to the ladder top.
    Strategy: climb T = T_lo+1, T_lo+2, ...  At each T probe both types with the
    capped feasibility MILP.  A witness at weight w proves d <= w (and we can stop
    -- climbing higher T only re-finds it).  If both types are infeasible at T, we
    have proven d >= T; continue.  An 'unknown' (timeout) stops the climb with the
    current cert_lb (honest: we cannot claim higher).
    """
    deadline = time.time() + total_budget
    cert_lb = T_lo            # d > T_lo already known from the w<=T_lo enum screen
    ub = None
    witness = None
    for T in range(T_lo + 1, T_hi + 1):
        if time.time() > deadline:
            break
        rX = _type_geq_T(c.HZ, c.HX, T, time_limit, deadline)
        # if X already yields a witness < T we can stop the whole climb
        if rX[0] == "witness":
            ub = rX[1][0]
            witness = ("X", rX[1][1])
            break
        rZ = _type_geq_T(c.HX, c.HZ, T, time_limit, deadline)
        if rZ[0] == "witness":
            ub = rZ[1][0]
            witness = ("Z", rZ[1][1])
            break
        if rX[0] == "certified" and rZ[0] == "certified":
            cert_lb = T          # proven d >= T
            continue
        # unknown on at least one type: stop, cannot certify higher honestly
        break
    return cert_lb, ub, witness


def _sample_pair(rng, l, m, family):
    """Draw a trinomial pair (A, B) of the requested structural family.

    family='diag'  : both non-constant monomials of A and of B carry nonzero x
                     AND y exponents (strictly diagonal), plus the constant.
    family='free'  : the three monomials of each polynomial are unrestricted over
                     the whole l x m lattice (constant/axis-aligned terms allowed).
                     This is the broadest family; our best (6,6) code lives here.
    """
    if family == "free":
        def mono():
            return (rng.randrange(l), rng.randrange(m))
        A = tuple(sorted(set(mono() for _ in range(8)))[:3])
        B = tuple(sorted(set(mono() for _ in range(8)))[:3])
    else:  # 'diag'
        def mono():
            return (rng.randrange(1, l), rng.randrange(1, m))
        A = tuple(sorted({(0, 0), mono(), mono()}))
        B = tuple(sorted({(0, 0), mono(), mono()}))
    return A, B


def run(l, m, n_random=6000, kmin=8, seed=0, T_lo=3, T_hi=12,
        time_limit=20, total_budget=180, out=None, max_eval=60, kmax=None,
        family="diag"):
    n = 2 * l * m
    print("=== n=%d %s high-d search (l,m)=(%d,%d) kmin=%d kmax=%s seed=%d "
          "ladder T=%d..%d ===" % (n, family, l, m, kmin, kmax, seed,
                                   T_lo + 1, T_hi), flush=True)
    rng = random.Random(seed)
    seen = set()
    cands = []
    t0 = time.time()
    for _ in range(n_random):
        A, B = _sample_pair(rng, l, m, family)
        if len(A) != 3 or len(B) != 3:
            continue
        key = (A, B)
        if key in seen:
            continue
        seen.add(key)
        c = bb.BBCode(l, m, list(A), list(B))
        if not c.css_commute_ok():
            continue
        k = c.k()
        if k < kmin:
            continue
        if kmax is not None and k > kmax:
            continue
        d2, found = distance.distance_lowweight_vec(c, wmax=2)
        if found:
            continue
        cands.append((k, list(A), list(B)))
    print("# stageA: %d diagonal codes %s<=k%s d>2 (from %d unique, %.1fs)"
          % (len(cands), kmin, ("<=%d" % kmax) if kmax else "", len(seen),
             time.time() - t0), flush=True)
    # Prefer higher k first (higher FOM potential at fixed d).
    cands.sort(key=lambda s: -s[0])
    results = []
    best_lb = 0
    for idx, (k, A, B) in enumerate(cands[:max_eval]):
        c = bb.BBCode(l, m, A, B)
        t = time.time()
        cert_lb, ub, wit = bracket_distance(
            c, T_lo=T_lo, T_hi=T_hi, time_limit=time_limit,
            total_budget=total_budget)
        # FOM bracket: lower bound uses cert_lb, optimistic uses ub (or cert_lb)
        fom_lb = k * cert_lb * cert_lb / n
        d_for_ub = ub if ub is not None else (T_hi + 1)
        rec = dict(l=l, m=m, n=n, k=k, cert_lb=cert_lb, ub=ub,
                   fom_lb=fom_lb, A=A, B=B)
        results.append(rec)
        if cert_lb > best_lb:
            best_lb = cert_lb
        ubs = ("<=%d" % ub) if ub is not None else (">%d" % T_hi)
        print("  [%d/%d] [[%d,%d, d in [%d,%s] ]] FOM_lb=%.3f (%.0fs) A=%s B=%s"
              % (idx + 1, min(len(cands), max_eval), n, k, cert_lb,
                 (str(ub) if ub is not None else ">%d" % T_hi), fom_lb,
                 time.time() - t, A, B), flush=True)
        if out:
            with open(out, "w") as f:
                json.dump(sorted(results, key=lambda r: (r["cert_lb"], r["k"]),
                                 reverse=True), f, indent=2)
    print("# done; best certified LB d>=%d; wrote %s" % (best_lb, out),
          flush=True)
    return results


if __name__ == "__main__":
    l = int(sys.argv[1]); m = int(sys.argv[2])
    kw = {}
    for a in sys.argv[3:]:
        key, val = a.split("=")
        kw[key] = int(val) if val.lstrip("-").isdigit() else val
    run(l, m, **kw)
