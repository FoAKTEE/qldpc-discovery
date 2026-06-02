# Contributing

## Dev setup

```bash
pip install -e ".[dev,decoders]"
python -m pytest -q          # must stay green (54 tests; CI runs this + audit)
qcode-audit                  # must be PASS (0 CRITICAL/HIGH)
```

## Ground rules

- **The kernel admits, not the LLM.** Every reported `[[n,k,d]]` carries an evidence modality +
  verifier status (MILP gap=0 / enumeration / BP-OSD upper bound). Never promote an incumbent
  upper bound to an exact distance.
- **Blind discovery.** Code under `discovery/{evaluation,search,evolve}` must import only the kernel —
  never the paper catalog or any reported code. `discovery/validation` is the *only* catalog reader,
  and runs strictly post-hoc.
- **Code quality** follows `phys-agentic-loop/code_quality_policy.md` (R0–R4 tiers, KISS/DRY/AHA).
  Module docstrings carry a paper anchor + risk tier; no stub bodies without a `[FUTURE ...]` marker.
- **Tests first.** Add a closed-loop test for every new component; cross-check against an independent
  method where possible (e.g. MILP ↔ enumeration). Run `qcode-audit` before committing.

## Adding a component or a reference paper

See [docs/EXTENDING.md](docs/EXTENDING.md). New library modules go under the matching subpackage
(`algebra/codes/distance/structure/discovery`) and are re-exported from `qcode_discovery/__init__.py`
if part of the public API.

## Commits

Small, verified, per-substage; paste the verifier output (`pytest` tail + audit line) in the body.
Do not push unless asked.
