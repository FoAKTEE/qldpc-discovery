#!/usr/bin/env python3
"""Render the best certified codes into a markdown table fragment for
results/blind_zero_findings.md.  Reads results/_certified.json (from
certify_top.py) and results/_archive.json (full FOM-ranked archive).
Prints a markdown block to stdout.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    p = os.path.join(HERE, "results", name)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def main():
    cert = load("_certified.json") or []
    arch = load("_archive.json") or []

    print("## Best codes found (FOM-ranked)\n")
    print("| rank | [[n,k,d]] | FOM | A (monomials) | B (monomials) | distance verification |")
    print("|---|---|---|---|---|---|")
    rows = cert if cert else []
    for i, r in enumerate(sorted(rows, key=lambda r: r["fom"], reverse=True), 1):
        A = [list(t) for t in r["A"]]
        B = [list(t) for t in r["B"]]
        print(f"| {i} | [[{r['n']},{r['k']},{r['d']}]] | {r['fom']:.3f} "
              f"| `{A}` | `{B}` | {r['tag']} |")

    if arch:
        best = max(arch, key=lambda c: (c["fom"] or 0))
        print(f"\nHighest FOM in archive: **{best['fom']:.3f}** "
              f"= [[{best['n']},{best['k']},{best['d']}]] ({best['verify']}).")
        print(f"\nArchive size: {len(arch)} unique codes.")


if __name__ == "__main__":
    main()
