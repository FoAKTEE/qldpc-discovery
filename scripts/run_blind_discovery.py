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
from qcode_discovery.search import blind_search_css, blind_search_pbb   # noqa: E402

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
    ap.add_argument("--type", choices=("css", "pbb"), default="css")
    ap.add_argument("--distance-method", choices=("milp", "bposd"), default="milp",
                    help="in-loop Stage-2 distance: milp (exact, slow) or bposd (fast upper bound)")
    ap.add_argument("--stage3-verify", action="store_true",
                    help="after the search, recompute EXACT MILP distance for archive elites (Stage 3)")
    args = ap.parse_args()
    lattices = [tuple(int(v) for v in s.split("x")) for s in args.lattices.split(",")]

    print(f"BLIND {args.type.upper()} discovery — lattices={lattices} seed={args.seed} "
          f"n_random={args.n_random} budget={args.budget} gens={args.gens}")
    print("(catalog-blind: no paper polynomials, no reported [[n,k,d]] consulted)\n")
    search_fn = blind_search_pbb if args.type == "pbb" else blind_search_css
    kwargs = dict(n_random=args.n_random, distance_budget=args.budget, generations=args.gens,
                  time_limit=args.time_limit, max_logicals=args.max_logicals, seed=args.seed, log=print)
    if args.type == "css":
        kwargs["distance_method"] = args.distance_method
    out = search_fn(lattices, **kwargs)
    elites = out["archive_elites"]

    if args.stage3_verify and args.type == "css" and elites:
        from qcode_discovery.search import verify_elites_milp   # noqa: E402
        print("\n=== Stage 3: MILP verification of elites (logical cap keeps n=144 tractable) ===")
        elites = verify_elites_milp(elites, time_limit=max(5.0, args.time_limit * 3),
                                    max_logicals=args.max_logicals, log=print)

    # Deduplicate distance-evaluated CSS representations by lattice-symmetry equivalence
    # (component 11) -> "N representations -> M distinct codes", mirroring the paper.
    n_distinct = None
    if args.type == "css" and out.get("evaluated"):
        from qcode_discovery.bb_codes import BBCode          # noqa: E402
        from qcode_discovery.dedup import dedup_bb, dedup_bliss  # noqa: E402
        reps = [BBCode(r["l"], r["m"], r["A"], r["B"]) for r in out["evaluated"]]
        try:
            import igraph  # noqa: F401
            dd, method = dedup_bliss(reps), "BLISS (exact)"
        except Exception:
            dd, method = dedup_bb(reps), "lattice-symmetry (upper bound)"
        n_distinct = dd["n_distinct"]
        print(f"\ndedup [{method}]: {len(reps)} representations -> {n_distinct} distinct")

    print(f"\n=== BLIND DISCOVERIES (k-screened={out['n_evaluated']}, distance-evals={out['n_distance_evals']}) ===")
    print(f"{'code':>18}  {'FOM':>6}  {'exact':>5}  pattern")
    for r in elites:
        tag = "exact" if r["exact"] else "<=ub"
        print(f"  [[{r['n']},{r['k']},{r['d']}]]".rjust(18) + f"  {r['fom']:6.2f}  {tag:>5}")

    payload = {
        "policy": "blind — no paper knowledge used in discovery",
        "type": args.type, "seed": args.seed, "lattices": lattices,
        "n_k_screened": out["n_evaluated"], "n_distance_evals": out["n_distance_evals"],
        "n_commuting": out.get("n_commuting"),
        "n_representations": len(out.get("evaluated", [])), "n_distinct": n_distinct,
        "discoveries": [
            {"n": r["n"], "k": r["k"], "d": r["d"], "fom": round(r["fom"], 3),
             "exact": r["exact"], "l": r["l"], "m": r["m"], "A": r["A"], "B": r["B"]}
            for r in elites
        ],
    }
    out_path = ROOT / "results" / f"blind_{args.type}_discovery.json"
    out_path.write_text(json.dumps(payload, indent=2))
    print(f"\nwrote {out_path}  ({len(elites)} codes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
