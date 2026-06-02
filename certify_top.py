#!/usr/bin/env python3
"""Re-certify a list of candidate codes with BOTH methods at high budget and
print a clean table for the results write-up.

For each code:
  - exact low-weight enumeration up to a per-n weight budget (certified lower
    bound; if it finds a logical, that IS the exact distance);
  - exact MILP (gap 0 => exact; else incumbent upper bound).
The two are reconciled; the printed verification tag states precisely what is
proven.

Usage:  PYTHONPATH=src python3 certify_top.py
The CODES list is filled in by the search driver (edited in) or passed inline.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from qcode import bb, distance


def certify(l, m, A, B, enum_wmax, milp_time=180):
    code = bb.BBCode(l, m, A, B)
    assert code.css_commute_ok()
    n, k = code.params()
    t0 = time.time()
    d_enum, found = distance.distance_lowweight_vec(code, wmax=enum_wmax)
    enum_t = time.time() - t0
    if found:
        return dict(n=n, k=k, d=d_enum, fom=k * d_enum * d_enum / n,
                    tag=f"enum-exact (d={d_enum} <= {enum_wmax}, {enum_t:.1f}s)",
                    A=A, B=B, exact=True)
    # d > enum_wmax certified by exhaustive scan; run MILP with that lower-bound
    # cut for the exact value.
    t1 = time.time()
    d_milp, info = distance.distance_milp(code, time_limit=milp_time,
                                          weight_floor=enum_wmax + 1)
    milp_t = time.time() - t1
    exact = info.get("certified_exact")
    tag = (f"MILP {'exact(gap=0)' if exact else 'UPPER-BOUND'} d={d_milp}; "
           f"enum certifies d>{enum_wmax}; {milp_t:.1f}s")
    return dict(n=n, k=k, d=d_milp, fom=k * d_milp * d_milp / n, tag=tag,
                A=A, B=B, exact=exact)


if __name__ == "__main__":
    # Codes to certify are appended here by the driver after search.
    import json
    path = sys.argv[1] if len(sys.argv) > 1 else "results/_top_codes.json"
    with open(path) as f:
        codes = json.load(f)
    print(f"certifying {len(codes)} codes")
    out = []
    for c in codes:
        l, m = c["l"], c["m"]
        n = 2 * l * m
        wmax = 4 if n <= 108 else 3
        r = certify(l, m, [tuple(t) for t in c["A"]],
                    [tuple(t) for t in c["B"]], enum_wmax=wmax)
        out.append(r)
        print(f"[[{r['n']},{r['k']},{r['d']}]] FOM={r['fom']:.3f}  {r['tag']}")
        print(f"    A={r['A']}  B={r['B']}")
    out.sort(key=lambda r: r["fom"], reverse=True)
    with open("results/_certified.json", "w") as f:
        json.dump(out, f, indent=2)
