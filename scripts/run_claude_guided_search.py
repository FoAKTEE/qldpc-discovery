#!/usr/bin/env python3
"""Claude-guided generator-ansatz search — Claude Code IS the LLM mutation operator.

The paper drives ansatz mutation with an LLM (litellm + paid API). Here the operator is Claude
Code itself: the agent proposes each ansatz (a generator program) from the FOM feedback, BLIND to
the paper catalog (blind_discovery_policy); this driver only EVALUATES the proposal with the kernel
cascade and records the lineage. One generation per invocation:

  python scripts/run_claude_guided_search.py --gen <label> --propose '<ansatz-json>' [--lattices 6x6,12x6] [--stage3]

`--propose` is a JSON GeneratorAnsatz spec, e.g.:
  {"strategies":[{"kind":"custom","params":{"A":[["l//3",0],[0,1],[0,2]],"B":[[0,"l//3"],[1,0],[2,0]]}}]}
Records to results/runs/claude_guided_trajectory.json (append). `--stage3` MILP-certifies the codes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from qcode_discovery.discovery.evolve import GeneratorAnsatz, ansatz_fitness   # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TRAJ = ROOT / "results" / "runs" / "claude_guided_trajectory.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True, help="generation label (e.g. g0_seed, g1, ...)")
    ap.add_argument("--propose", required=True, help="JSON GeneratorAnsatz spec (the LLM mutation)")
    ap.add_argument("--lattices", default="6x6,12x6")
    ap.add_argument("--time-limit", type=float, default=1.5)
    ap.add_argument("--max-logicals", type=int, default=6)
    ap.add_argument("--stage3", action="store_true", help="MILP-certify the proposed ansatz's codes")
    args = ap.parse_args()
    lattices = [tuple(int(v) for v in s.split("x")) for s in args.lattices.split(",")]
    spec = json.loads(args.propose)
    ansatz = GeneratorAnsatz(spec["strategies"])

    fit = ansatz_fitness(ansatz, lattices, time_limit=args.time_limit, max_logicals=args.max_logicals)
    codes = fit["codes"]
    print(f"[{args.gen}] BP-OSD fitness score={fit['score']:.2f} over {fit['n_lattices_with_code']} lattices "
          f"(catalog-blind). Codes (BP-OSD upper bounds):")
    for c in sorted(codes, key=lambda r: r["fom"], reverse=True):
        print(f"   [[{c['n']},{c['k']},{c['d']}]] FOM={c['fom']:.2f} d/sqrtn={c['d_over_sqrt_n']:.2f}")

    if args.stage3 and codes:
        from qcode_discovery.discovery.search import verify_elites_milp
        print(f"[{args.gen}] Stage-3 MILP certification:")
        certified = verify_elites_milp(codes, time_limit=max(5.0, args.time_limit * 3),
                                       max_logicals=args.max_logicals, log=print)
        fit["certified"] = [{"n": c["n"], "k": c["k"], "d": c["d"], "exact": c["exact"],
                             "fom": round(c["fom"], 3)} for c in certified]

    TRAJ.parent.mkdir(parents=True, exist_ok=True)
    log = json.loads(TRAJ.read_text()) if TRAJ.exists() else {"policy": "claude-guided, catalog-blind",
                                                               "lattices": lattices, "generations": []}
    log["generations"].append({
        "gen": args.gen, "score": round(fit["score"], 3),
        "n_lattices_with_code": fit["n_lattices_with_code"], "spec": spec,
        "codes": [{"n": c["n"], "k": c["k"], "d_bposd": c["d"], "fom": round(c["fom"], 3)} for c in codes],
        **({"certified": fit["certified"]} if "certified" in fit else {}),
    })
    TRAJ.write_text(json.dumps(log, indent=2))
    print(f"[{args.gen}] recorded -> {TRAJ.relative_to(ROOT)}  (generation {len(log['generations'])})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
