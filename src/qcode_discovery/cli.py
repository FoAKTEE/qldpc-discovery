"""Command-line interface for qcode_discovery.

Installed entry points (see pyproject [project.scripts]):
  qcode-discover   blind CSS/PBB discovery (Stage-1 k -> Stage-2 distance -> optional Stage-3 MILP) + dedup
  qcode-validate   POST-HOC validation of a blind run vs the paper catalog (held-out)
  qcode-audit      static code-quality audit of the package (R0-R4 policy)

Discovery is catalog-blind; validation is the only catalog reader and runs separately, after.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

from . import (blind_search_css, blind_search_pbb, verify_elites_milp,
               dedup_bb, dedup_bliss, BBCode, validate)


def _lattices(s: str):
    return [tuple(int(v) for v in part.split("x")) for part in s.split(",")]


# --------------------------------------------------------------------------- discover
def discover_cmd(argv=None) -> int:
    """Run a catalog-blind BB/PBB discovery campaign and write the results JSON."""
    p = argparse.ArgumentParser(prog="qcode-discover", description="Blind BB/PBB code discovery (catalog-blind).")
    p.add_argument("--type", choices=("css", "pbb"), default="css")
    p.add_argument("--lattices", default="6x6,12x6")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--n-random", type=int, default=400)
    p.add_argument("--budget", type=int, default=8)
    p.add_argument("--gens", type=int, default=2)
    p.add_argument("--distance-method", choices=("milp", "bposd"), default="milp")
    p.add_argument("--max-logicals", type=int, default=8)
    p.add_argument("--time-limit", type=float, default=2.0)
    p.add_argument("--stage3-verify", action="store_true")
    p.add_argument("--out", default="results/runs/blind_%(type)s_discovery.json")
    a = p.parse_args(argv)
    lat = _lattices(a.lattices)
    kw = dict(n_random=a.n_random, distance_budget=a.budget, generations=a.gens,
              time_limit=a.time_limit, max_logicals=a.max_logicals, seed=a.seed, log=print)
    if a.type == "css":
        kw["distance_method"] = a.distance_method
        out = blind_search_css(lat, **kw)
    else:
        out = blind_search_pbb(lat, **kw)
    elites = out["archive_elites"]
    if a.stage3_verify and a.type == "css" and elites:
        print("Stage-3 MILP verification ...")
        elites = verify_elites_milp(elites, time_limit=max(5.0, a.time_limit * 3),
                                    max_logicals=a.max_logicals, log=print)
    n_distinct = None
    if a.type == "css" and out.get("evaluated"):
        reps = [BBCode(r["l"], r["m"], r["A"], r["B"]) for r in out["evaluated"]]
        try:
            import igraph  # noqa: F401
            n_distinct = dedup_bliss(reps)["n_distinct"]; method = "BLISS"
        except Exception:
            n_distinct = dedup_bb(reps)["n_distinct"]; method = "lattice-symmetry"
        print(f"dedup [{method}]: {len(reps)} representations -> {n_distinct} distinct")
    print("\nbest discoveries (FOM-ranked):")
    for r in elites:
        print(f"  [[{r['n']},{r['k']},{r['d']}]] FOM={r['fom']:.2f} exact={r['exact']}")
    out_path = Path(a.out % {"type": a.type})
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "policy": "blind — no paper knowledge in discovery", "type": a.type, "seed": a.seed,
        "lattices": lat, "n_distinct": n_distinct,
        "discoveries": [{"n": r["n"], "k": r["k"], "d": r["d"], "fom": round(r["fom"], 3),
                         "exact": r["exact"], "l": r["l"], "m": r["m"], "A": r["A"], "B": r["B"]}
                        for r in elites],
    }, indent=2))
    print(f"wrote {out_path}")
    return 0


# --------------------------------------------------------------------------- validate
def validate_cmd(argv=None) -> int:
    """Validate a blind run against the held-out paper catalog (post-hoc)."""
    p = argparse.ArgumentParser(prog="qcode-validate", description="Post-hoc validation vs the paper catalog (held-out).")
    p.add_argument("--type", choices=("css", "pbb"), default="css")
    p.add_argument("--run", default="results/runs/blind_%(type)s_discovery.json")
    p.add_argument("--catalog", default="",
                   help="path to the paper catalog .tex (held-out, not bundled); "
                        "omitted -> validate against built-in landmark codes only")
    p.add_argument("--out", default="results/validation/validation_report_%(type)s.md")
    a = p.parse_args(argv)
    run = Path(a.run % {"type": a.type})
    if not run.exists():
        print(f"no run at {run}; run `qcode-discover --type {a.type}` first", file=sys.stderr)
        return 1
    payload = json.loads(run.read_text())
    catalog = Path(a.catalog % {"type": a.type}) if a.catalog else None
    rep = validate(payload["discoveries"], catalog if (catalog and catalog.exists()) else None, kind=a.type)
    print(f"reference codes: {rep['n_reference_codes']}  (catalog is a HELD-OUT test set)")
    for r in rep["results"]:
        print(f"  {r['discovery']:>16}  {r['verdict']:<22} {r['matched_ref'] or ''}")
    print("summary:", rep["summary"])
    out_path = Path(a.out % {"type": a.type})
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# Validation ({a.type}) vs arXiv:2606.02418 (post-hoc)", "",
             f"Reference codes: {rep['n_reference_codes']} (held-out).", "",
             "| discovery | verdict | matched |", "|---|---|---|"]
    lines += [f"| {r['discovery']} | {r['verdict']} | {r['matched_ref'] or '—'} |" for r in rep["results"]]
    lines += ["", f"Summary: {rep['summary']}"]
    out_path.write_text("\n".join(lines) + "\n")
    print(f"wrote {out_path}")
    return 0


# --------------------------------------------------------------------------- audit
_RISK = ("R0", "R1", "R2", "R3", "R4")


def _audit_file(path: Path):
    findings = []
    tree = ast.parse(path.read_text(), filename=str(path))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if node.name.startswith("_") and not isinstance(node, ast.ClassDef):
            continue
        doc = ast.get_docstring(node) or ""
        loc = f"{path}:{node.lineno} {node.name}"
        if not doc:
            findings.append(("MEDIUM", loc, "missing docstring"))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body = [s for s in node.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
            stub = (not body) or (len(body) == 1 and isinstance(body[0], ast.Pass)) or \
                any(p in ast.dump(node).lower() for p in ("notimplementederror", "todo", "fixme"))
            if stub and "[future" not in doc.lower():
                findings.append(("HIGH", loc, "stub body without a [FUTURE ...] marker"))
    return findings


def audit_cmd(argv=None) -> int:
    """Run the static code-quality audit; exit nonzero on any CRITICAL/HIGH finding."""
    p = argparse.ArgumentParser(prog="qcode-audit", description="Static code-quality audit (code_quality_policy).")
    p.add_argument("paths", nargs="*", default=[str(Path(__file__).parent)])
    a = p.parse_args(argv)
    files = []
    for t in a.paths:
        tp = Path(t)
        files += sorted(tp.rglob("*.py")) if tp.is_dir() else [tp]
    findings = [f for fp in files for f in _audit_file(fp)]
    by = {s: [x for x in findings if x[0] == s] for s in ("CRITICAL", "HIGH", "MEDIUM", "LOW")}
    print(f"code_quality_audit: {len(files)} files, {len(findings)} findings "
          f"(CRITICAL={len(by['CRITICAL'])} HIGH={len(by['HIGH'])} MEDIUM={len(by['MEDIUM'])})")
    for sev in ("CRITICAL", "HIGH", "MEDIUM"):
        for _, loc, msg in by[sev]:
            print(f"  [{sev}] {loc} — {msg}")
    blocking = len(by["CRITICAL"]) + len(by["HIGH"])
    print(f"code_quality_policy_pass: {'PASS' if blocking == 0 else 'FAIL'} ({blocking} blocking)")
    return 0 if blocking == 0 else 1


def main(argv=None) -> int:
    """Dispatcher: `qcode-discovery <discover|validate|audit> ...`."""
    argv = list(sys.argv[1:] if argv is None else argv)
    cmds = {"discover": discover_cmd, "validate": validate_cmd, "audit": audit_cmd}
    if not argv or argv[0] not in cmds:
        print(f"usage: qcode-discovery <{'|'.join(cmds)}> [options]", file=sys.stderr)
        return 2
    return cmds[argv[0]](argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
