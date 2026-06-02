#!/usr/bin/env python3
"""POST-HOC validation of blind discoveries against arXiv:2606.02418 (held-out test set).

Runs AFTER scripts/run_blind_discovery.py. Reads results/blind_css_discovery.json (produced
blind) and compares to the paper's CSS catalog + landmark codes. Writes results/validation_report.md.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from qcode_discovery.validation import validate   # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", choices=("css", "pbb"), default="css")
    args = ap.parse_args()
    disc_path = ROOT / "results" / "runs" / f"blind_{args.type}_discovery.json"
    if not disc_path.exists():
        print(f"no blind results at {disc_path}; run scripts/run_blind_discovery.py --type {args.type} first",
              file=sys.stderr)
        return 1
    payload = json.loads(disc_path.read_text())
    catalog = ROOT / "ref-paper" / "arxiv-2606.02418" / "src" / f"{args.type}_catalog_tables.tex"
    report = validate(payload["discoveries"], catalog, kind=args.type)

    lines = [f"# Validation report ({args.type.upper()}) — blind discoveries vs arXiv:2606.02418 (post-hoc)", "",
             f"Reference codes: {report['n_reference_codes']} ({args.type} catalog + landmarks). "
             "The catalog is a HELD-OUT TEST SET — never consulted during the blind search.", "",
             f"Blind seed: {payload.get('seed')}  ·  k-screened: {payload.get('n_k_screened')}  ·  "
             f"distance-evals: {payload.get('n_distance_evals')}", "",
             "| blind discovery | FOM | exact | verdict | matched paper code |",
             "|---|---|---|---|---|"]
    for r in report["results"]:
        lines.append(f"| {r['discovery']} | {r['fom']} | {r['exact']} | {r['verdict']} | "
                     f"{r['matched_ref'] or '—'} |")
    lines += ["", "## Summary", ""]
    for v, c in sorted(report["summary"].items()):
        lines.append(f"- **{v}**: {c}")
    lines += ["", "Verdict key: MATCH = same (n,k,d) exact vs an exact reference; "
              "POLY_MATCH = identical (A,B) polynomial sets; UB_CONSISTENT = same (n,k), our d "
              "(upper bound) consistent with the reference d; NOVEL_AT_N = no reference code at "
              "this block length (the CSS catalog starts at n=144)."]
    out = ROOT / "results" / "validation" / f"validation_report_{args.type}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")

    print("\n".join(lines))
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
