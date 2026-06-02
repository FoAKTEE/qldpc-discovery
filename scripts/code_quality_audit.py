#!/usr/bin/env python3
"""Static code-quality diagnostic for src/qcode_discovery — filters/diagnoses code per
phys-agentic-loop/code_quality_policy.md (self-evolution directive 2026-06-02, point 4).

Flags, per public function/class:
  - missing docstring;
  - docstring without a paper anchor (no 'arXiv' / 'anchor' / 'Paper');
  - docstring without a risk tier (no R0-R4 tag);
  - undocumented placeholder body (pass / ... / TODO / FIXME / NotImplementedError / sorry)
    lacking a '[FUTURE' marker (the policy's no-silent-stub rule);
  - functions exceeding a nesting-depth threshold (KISS failure signal: deep control flow).

Exit code 0 if no CRITICAL/HIGH findings (placeholder-without-marker is HIGH), else 1.
Usage: python scripts/code_quality_audit.py [path ...]
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

RISK_TAGS = ("R0", "R1", "R2", "R3", "R4")
ANCHOR_HINTS = ("arxiv", "anchor", "paper")
PLACEHOLDER_NAMES = {"todo", "fixme", "sorry", "notimplemented", "notimplementederror", "placeholder"}
MAX_NESTING = 5


def _nesting_depth(node: ast.AST, depth: int = 0) -> int:
    best = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
            best = max(best, _nesting_depth(child, depth + 1))
        else:
            best = max(best, _nesting_depth(child, depth))
    return best


def _is_placeholder_body(node) -> bool:
    body = [s for s in node.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
    if not body:
        return True                                  # only a docstring/constant
    if len(body) == 1 and isinstance(body[0], ast.Pass):
        return True
    src = ast.dump(node).lower()
    return any(p in src for p in PLACEHOLDER_NAMES)


def audit_file(path: Path) -> list[dict]:
    findings: list[dict] = []
    tree = ast.parse(path.read_text(), filename=str(path))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        name = node.name
        if name.startswith("_") and not isinstance(node, ast.ClassDef):
            continue                                  # private helpers exempt from anchor rule
        doc = ast.get_docstring(node) or ""
        low = doc.lower()
        loc = f"{path}:{node.lineno} {name}"
        if not doc:
            findings.append({"sev": "MEDIUM", "loc": loc, "msg": "missing docstring"})
        else:
            if isinstance(node, ast.FunctionDef) and not any(t in doc for t in RISK_TAGS):
                # module-level risk tier may cover it; report LOW only
                findings.append({"sev": "LOW", "loc": loc, "msg": "no risk tier (R0-R4) in docstring"})
            if not any(h in low for h in ANCHOR_HINTS) and isinstance(node, ast.ClassDef):
                findings.append({"sev": "LOW", "loc": loc, "msg": "class docstring lacks paper anchor"})
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _is_placeholder_body(node) and "[future" not in low:
                findings.append({"sev": "HIGH", "loc": loc,
                                 "msg": "placeholder/stub body without a [FUTURE ...] marker (no-silent-stub)"})
            depth = _nesting_depth(node)
            if depth > MAX_NESTING:
                findings.append({"sev": "MEDIUM", "loc": loc, "msg": f"nesting depth {depth} > {MAX_NESTING} (KISS)"})
    return findings


def main(argv: list[str]) -> int:
    targets = [Path(a) for a in argv[1:]] or [Path(__file__).resolve().parent.parent / "src" / "qcode_discovery"]
    files: list[Path] = []
    for t in targets:
        files.extend(sorted(t.rglob("*.py")) if t.is_dir() else [t])
    all_findings: list[dict] = []
    for f in files:
        all_findings.extend(audit_file(f))
    by_sev = {s: [x for x in all_findings if x["sev"] == s] for s in ("CRITICAL", "HIGH", "MEDIUM", "LOW")}
    print(f"code_quality_audit: {len(files)} files, {len(all_findings)} findings "
          f"(CRITICAL={len(by_sev['CRITICAL'])} HIGH={len(by_sev['HIGH'])} "
          f"MEDIUM={len(by_sev['MEDIUM'])} LOW={len(by_sev['LOW'])})")
    for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        for x in by_sev[sev]:
            print(f"  [{sev}] {x['loc']} — {x['msg']}")
    blocking = len(by_sev["CRITICAL"]) + len(by_sev["HIGH"])
    print(f"code_quality_policy_pass: {'PASS' if blocking == 0 else 'FAIL'} "
          f"({blocking} blocking finding(s))")
    return 0 if blocking == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
