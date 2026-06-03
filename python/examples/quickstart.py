#!/usr/bin/env python3
"""qcode_discovery quickstart — run with:  PYTHONPATH=src python examples/quickstart.py

Shows the kernel (construct + verify) and a tiny BLIND discovery. The catalog is NEVER read here;
validation against the paper is a separate, post-hoc step (`qcode-validate`).
"""
from qcode_discovery import (BBCode, css_k, fom, css_distance_milp, verify_ab_d2,
                             blind_search_css)


def main() -> None:
    # 1. Construct the gross code [[144,12,12]] and verify its encoding dimension.
    gross = BBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2")
    k = css_k(gross.HX, gross.HZ)
    print(f"gross code: n={gross.n}, k={k}, stabilizer weight={gross.stabilizer_weight}, FOM(d=12)={fom(144,12,12)}")

    # 2. A theorem witness: every A=B code has distance exactly 2 (thm:ab_d2).
    w = verify_ab_d2(6, 6, "1+x+y")
    print(f"thm:ab_d2 witness on a (6,6) A=B code: k={w['k']}, exhibited weight-2 logical, d={w['d']}")

    # 3. An exact distance via MILP on a small code.
    small = BBCode(3, 3, "1+x+y", "1+x^2+y^2")
    res = css_distance_milp(small, time_limit=20.0)
    print(f"[[18,4,?]] (3,3): MILP distance d={res['d']} (exact={res['exact']})")

    # 4. A tiny BLIND discovery run (naive seeds, FOM fitness; NO paper knowledge).
    print("\nblind discovery at (6,6) (catalog-blind):")
    out = blind_search_css([(6, 6)], n_random=150, distance_budget=4, generations=0,
                           time_limit=10.0, seed=1)
    for r in out["archive_elites"][:4]:
        print(f"  found [[{r['n']},{r['k']},{r['d']}]] FOM={r['fom']:.2f} exact={r['exact']}")
    print("\n(Discovery used only the kernel. Compare to the paper afterward with `qcode-validate`.)")


if __name__ == "__main__":
    main()
