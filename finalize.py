#!/usr/bin/env python3
"""Merge all archives into results/_archive.json, dedup by (lattice, A, B),
keep the FOM-ranked list, and print a per-lattice best summary.  Used to
assemble the final findings.
"""

import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "results")


def load(name):
    p = os.path.join(R, name)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return []


def key(c):
    return (c["l"], c["m"], tuple(map(tuple, c["A"])), tuple(map(tuple, c["B"])))


def main():
    merged = {}
    for name in ("_archive_n72.json", "_big_lattice.json", "_certified.json"):
        for c in load(name):
            # normalise certified.json shape (uses 'tag' not 'verify', no l/m)
            if "verify" not in c and "tag" in c:
                c = dict(c, verify=c["tag"])
            if "l" not in c or "m" not in c:
                # certified.json: infer lattice from n (all certified are n=72 => 6x6)
                if c.get("n") == 72:
                    c = dict(c, l=6, m=6)
                else:
                    # cannot place safely; skip to avoid a wrong key
                    continue
            if "n" not in c:
                c = dict(c, n=2 * c["l"] * c["m"])
            merged.setdefault(key(c), c)
    final = sorted(merged.values(), key=lambda c: (c.get("fom") or 0), reverse=True)
    with open(os.path.join(R, "_archive.json"), "w") as f:
        json.dump(final, f, indent=2)

    print(f"merged archive: {len(final)} unique codes")
    by_l = defaultdict(list)
    for c in final:
        by_l[(c["l"], c["m"])].append(c)
    print("\nper-lattice best (FOM):")
    for lm in sorted(by_l):
        b = max(by_l[lm], key=lambda c: (c.get("fom") or 0))
        print(f"  ({lm[0]},{lm[1]}) n={2*lm[0]*lm[1]}: "
              f"[[{b['n']},{b['k']},{b['d']}]] FOM={b.get('fom'):.3f} "
              f"[{b.get('verify')}]  count={len(by_l[lm])}")
    print("\noverall top 12:")
    for c in final[:12]:
        print(f"  [[{c['n']},{c['k']},{c['d']}]] FOM={c.get('fom'):.3f} "
              f"({c['l']},{c['m']}) [{c.get('verify')}]")
    # best CERTIFIED (exact) code
    exact = [c for c in final
             if ("enum-exact" in (c.get("verify") or ""))
             or ("milp-exact" in (c.get("verify") or ""))]
    if exact:
        be = max(exact, key=lambda c: (c.get("fom") or 0))
        print(f"\nBEST CERTIFIED: [[{be['n']},{be['k']},{be['d']}]] "
              f"FOM={be.get('fom'):.3f} ({be['l']},{be['m']}) [{be.get('verify')}]")


if __name__ == "__main__":
    main()
