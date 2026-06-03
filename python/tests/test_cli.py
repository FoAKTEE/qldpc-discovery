"""Smoke tests for the CLI entry points (qcode-discover / qcode-validate / qcode-audit).

These exercise the command wiring, not the science (which test_kernel/test_discovery cover):
the dispatcher routes, a tiny blind run writes a results JSON, validate refuses a missing run,
and the audit returns PASS on the package itself.
"""
import json
from pathlib import Path

from qcode_discovery import cli


def test_main_dispatcher_rejects_unknown():
    assert cli.main([]) == 2
    assert cli.main(["bogus"]) == 2


def test_audit_passes_on_package():
    # The package must keep a clean static audit (0 CRITICAL/HIGH -> exit 0).
    assert cli.audit_cmd([]) == 0


def test_discover_writes_results_json(tmp_path):
    out = tmp_path / "run_%(type)s.json"
    rc = cli.discover_cmd(["--type", "css", "--lattices", "3x3", "--n-random", "30",
                           "--budget", "4", "--gens", "0", "--distance-method", "milp",
                           "--time-limit", "2.0", "--seed", "1", "--out", str(out)])
    assert rc == 0
    payload = json.loads((tmp_path / "run_css.json").read_text())
    assert payload["type"] == "css" and "blind" in payload["policy"]
    for d in payload["discoveries"]:
        assert d["n"] == 18 and d["k"] >= 0          # (3,3) -> n = 2*l*m = 18


def test_validate_refuses_missing_run(tmp_path):
    missing = tmp_path / "nope_%(type)s.json"
    assert cli.validate_cmd(["--type", "css", "--run", str(missing)]) == 1


def test_validate_on_discovered_run(tmp_path):
    run = tmp_path / "run_%(type)s.json"
    cli.discover_cmd(["--type", "css", "--lattices", "3x3", "--n-random", "30", "--budget", "4",
                      "--gens", "0", "--time-limit", "2.0", "--seed", "1", "--out", str(run)])
    rep = tmp_path / "val_%(type)s.md"
    rc = cli.validate_cmd(["--type", "css", "--run", str(run),
                           "--catalog", "/nonexistent.tex", "--out", str(rep)])
    assert rc == 0
    assert (tmp_path / "val_css.md").exists()
