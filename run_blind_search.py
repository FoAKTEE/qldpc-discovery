#!/usr/bin/env python3
"""FULL BLIND search for bivariate-bicycle CSS codes, using the qcode_discovery package.

Catalog-blind (blind_discovery_policy): naive random seeds, FOM-driven MAP-Elites/GA, and
kernel-admitted distances ONLY. No paper polynomial is ever seeded, no reported [[n,k,d]] is
hardcoded, and no catalog is read (none is even bundled). The search RANGE is deliberately set to
COVER lattice (12,6) with weight-3 polynomials — the home of the gross code [[144,12,12]] — so that
code is *reachable*; whatever distance the blind search actually reaches at n=144 is an honest result.

Pipeline (the package's 3-stage cascade):
  Stage 1  k via GF(2) rank (cheap screen)
  Stage 2  BP-OSD distance (fast UPPER bound; reliable at k/n<0.1, e.g. k=12 at n=144) + d/sqrt(n) trust
  Stage 3  MILP exact distance on the top elites (gap=0 certifies; catches BP-OSD overestimates)

Usage:
    PYTHONPATH=src python run_blind_search.py            # defaults below
    PYTHONPATH=src python run_blind_search.py --lattices 12x6 --n-random 8000 --gens 120
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from qcode_discovery import blind_search_css, verify_elites_milp


def parse_lattices(s: str):
    return [tuple(int(v) for v in part.split("x")) for part in s.split(",")]


def poly_str(terms) -> str:
    """Render a term list [(a,b),...] as a human-readable polynomial in x,y (for the findings)."""
    def mon(a, b):
        if a == 0 and b == 0:
            return "1"
        xs = "" if a == 0 else ("x" if a == 1 else f"x^{a}")
        ys = "" if b == 0 else ("y" if b == 1 else f"y^{b}")
        return xs + ys
    return "+".join(mon(a, b) for a, b in terms) or "0"


def row(e: dict | None) -> dict | None:
    if e is None:
        return None
    return {"n": e["n"], "k": e["k"], "d": e["d"], "exact": e.get("exact"),
            "fom": round(e["fom"], 3), "l": e["l"], "m": e["m"],
            "A": poly_str(e["A"]), "B": poly_str(e["B"])}


def main() -> None:
    ap = argparse.ArgumentParser(description="Full blind BB CSS search (range covers [[144,12,12]]).")
    ap.add_argument("--lattices", default="12x6,6x12,6x6",
                    help="LxM,... — MUST include 12x6 to cover the gross code [[144,12,12]]")
    ap.add_argument("--n-random", type=int, default=4000, help="naive random seeds screened per lattice")
    ap.add_argument("--budget", type=int, default=48, help="BP-OSD distance evals per lattice (k-diverse)")
    ap.add_argument("--gens", type=int, default=60, help="GA generations of FOM hill-climbing on elites")
    ap.add_argument("--weight", type=int, default=3, help="polynomial weight (gross code uses weight 3)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--bposd-time", type=float, default=5.0, help="-> BP-OSD trials = 100*this")
    ap.add_argument("--milp-time", type=float, default=120.0, help="Stage-3 MILP time limit per elite")
    ap.add_argument("--milp-top", type=int, default=10, help="number of top elites to MILP-certify")
    ap.add_argument("--out", default="results/blind_search_run.json")
    a = ap.parse_args()

    lat = parse_lattices(a.lattices)
    covers_gross = (12, 6) in lat or (6, 12) in lat
    t0 = time.time()
    print(f"[blind] lattices={lat}  n_random={a.n_random}  budget={a.budget}  gens={a.gens}  "
          f"weight={a.weight}  seed={a.seed}  method=bposd(trials={int(a.bposd_time*100)})")
    print(f"[blind] range covers (12,6) weight-3 [[144,12,12]]: {covers_gross}  "
          f"(seeds are naive random — gross code reachable, never seeded)")

    out = blind_search_css(lat, n_random=a.n_random, distance_budget=a.budget,
                           generations=a.gens, weight=a.weight, seed=a.seed,
                           distance_method="bposd", time_limit=a.bposd_time, log=print)
    elites = out["archive_elites"]
    print(f"[blind] phase1+2 done in {time.time()-t0:.0f}s: {out['n_evaluated']} screened, "
          f"{out['n_distance_evals']} distance-evald, {len(elites)} archive elites")

    # Stage-3: MILP-certify the top elites (BP-OSD distances above are upper bounds).
    top = sorted(elites, key=lambda e: (-e["fom"], -e["n"]))[:a.milp_top]
    print(f"[blind] Stage-3: MILP-certifying top {len(top)} elites (<= {a.milp_time}s each)...")
    certified = verify_elites_milp(top, time_limit=a.milp_time, log=print)

    n144 = [e for e in certified if e["n"] == 144]
    best144 = max(n144, key=lambda e: e["d"]) if n144 else None
    payload = {
        "policy": "FULL BLIND — naive seeds, FOM-driven, kernel-admitted; range covers (12,6) w3; NO paper data",
        "config": {"lattices": lat, "n_random": a.n_random, "budget": a.budget, "gens": a.gens,
                   "weight": a.weight, "seed": a.seed, "bposd_trials": int(a.bposd_time * 100)},
        "n_screened": out["n_evaluated"], "n_distance_evals": out["n_distance_evals"],
        "elapsed_s": round(time.time() - t0, 1),
        "archive_top": [row(e) for e in certified],
        "best_n144": row(best144),
        "reached_d12_at_n144": bool(best144 and best144["d"] >= 12),
    }
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(payload, indent=2))
    print(f"[blind] wrote {a.out}  (elapsed {payload['elapsed_s']}s)")
    if best144:
        print(f"[blind] BEST at n=144 (blind): [[144,{best144['k']},{best144['d']}]] "
              f"exact={best144['exact']} FOM={best144['fom']:.2f}  A={poly_str(best144['A']) if isinstance(best144['A'], list) else best144['A']}")
    print(f"[blind] reached d=12 at n=144? {'YES' if payload['reached_d12_at_n144'] else 'NO'}")


if __name__ == "__main__":
    main()
