#!/usr/bin/env python3
"""Run a BLIND CSS BB-code discovery campaign and log results.

Catalog-blind (blind_discovery_policy): seeds are naive random trinomials; the only signal
is FOM via the kernel. Writes results/blind_css_discovery.json. Run validation SEPARATELY
(scripts/validate_against_paper.py) AFTER this — never during. Usage:
  python scripts/run_blind_discovery.py [--seed N] [--budget N] [--gens N]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from qcode_discovery.search import blind_search_css   # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--n-random", type=int, default=500)
    ap.add_argument("--budget", type=int, default=8, help="distance evals per lattice (k-diverse)")
    ap.add_argument("--gens", type=int, default=3)
    ap.add_argument("--time-limit", type=float, default=2.0)
    ap.add_argument("--max-logicals", type=int, default=10)
    ap.add_argument("--lattices", default="6x3,3x6,6x6")
    args = ap.parse_args()
    lattices = [tuple(int(v) for v in s.split("x")) for s in args.lattices.split(",")]

    print(f"BLIND CSS discovery — lattices={lattices} seed={args.seed} "
          f"n_random={args.n_random} budget={args.budget} gens={args.gens}")
    print("(catalog-blind: no paper polynomials, no reported [[n,k,d]] consulted)\n")
    out = blind_search_css(
        lattices, n_random=args.n_random, distance_budget=args.budget, generations=args.gens,
        time_limit=args.time_limit, max_logicals=args.max_logicals, seed=args.seed, log=print,
    )
    elites = out["archive_elites"]
    print(f"\n=== BLIND DISCOVERIES (k-screened={out['n_evaluated']}, distance-evals={out['n_distance_evals']}) ===")
    print(f"{'code':>18}  {'FOM':>6}  {'exact':>5}  pattern")
    for r in elites:
        tag = "exact" if r["exact"] else "<=ub"
        print(f"  [[{r['n']},{r['k']},{r['d']}]]".rjust(18) + f"  {r['fom']:6.2f}  {tag:>5}")

    payload = {
        "policy": "blind — no paper knowledge used in discovery",
        "seed": args.seed, "lattices": lattices,
        "n_k_screened": out["n_evaluated"], "n_distance_evals": out["n_distance_evals"],
        "discoveries": [
            {"n": r["n"], "k": r["k"], "d": r["d"], "fom": round(r["fom"], 3),
             "exact": r["exact"], "l": r["l"], "m": r["m"], "A": r["A"], "B": r["B"]}
            for r in elites
        ],
    }
    out_path = ROOT / "results" / "blind_css_discovery.json"
    out_path.write_text(json.dumps(payload, indent=2))
    print(f"\nwrote {out_path}  ({len(elites)} codes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
