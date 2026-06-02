# Extending qldpc-discovery

How to grow the knowledge base and the pipeline. Keep same-kind files together (see layout below);
keep discovery **catalog-blind** (only `src/qcode_discovery/validation.py` may read a paper catalog).

## Directory layout (one kind per folder)

```
src/qcode_discovery/   one module per pipeline component
tests/                 one test_*.py per layer (kernel, discovery)
scripts/               runnable entry points (run / validate / audit)
results/
  ├── discovery_timeline.md     canonical human-readable timeline (root)
  ├── runs/                     raw blind-run outputs (*.json)
  └── validation/               post-hoc validation reports (*.md)
ref-paper/arxiv-<id>/  read-only tex mirror + PROVENANCE.md + chunk_index.md + digest/
reformulate/qldpc-discovery/paper_<id>/   decomposition (theorem/file dependency DAGs, ...)
progress/qldpc-discovery/   RESEARCH_NOTE.md, loop_notes/, medium_term.md, agentic_lean_state.md, external_axioms.md
ref-code/              cloned reference repos (read-only mirror; gitignored)
```

## Add a new reference paper (escalation / pipeline-0)

1. `curl -sL https://arxiv.org/e-print/<id> -o ref-paper/arxiv-<id>/eprint.tar.gz` then extract to `src/`.
2. Write `ref-paper/arxiv-<id>/PROVENANCE.md` (sha256, title, role in Σ).
3. Decompose (pipeline-0): `ref-paper/arxiv-<id>/chunk_index.md` + `digest/chunk_NNN_*.md` (verbatim,
   typed entries: context · claim · modality · deps · status). Optionally a Workflow fan-out
   (inject `phys-agentic-loop/alignment.md` + `_common/agentic_lean_contract.md` into each sub-agent).
4. `reformulate/qldpc-discovery/paper_<id>/`: `theorem_dependency_plan.md` + `file_dependency_plan.md`
   (+ summary/convention/...). Add Σ row to `progress/qldpc-discovery/RESEARCH_NOTE.md` and any new
   `external_axioms.md` entry.

## Add a new kernel component (module)

1. `src/qcode_discovery/<name>.py` — module docstring carries the **paper anchor** (`arXiv:NNNN.NNNNN sec X`)
   and **risk tier** (R0–R4). Import only the kernel (no catalog) if it is a discovery-path module.
2. Add to `__init__.py.__all__`. Add `tests/test_*.py` with a closed-loop assertion (verify against an
   independent method where possible — e.g. MILP ↔ enumeration).
3. Gate: `python -m pytest -q` green AND `python scripts/code_quality_audit.py` PASS (0 blocking).

## Run discovery + validate (the loop)

```bash
PYTHONPATH=src python scripts/run_blind_discovery.py --type css --distance-method bposd --stage3-verify
PYTHONPATH=src python scripts/validate_against_paper.py --type css      # post-hoc, reads results/runs/
```
- `--type {css,pbb}` · `--distance-method {milp,bposd}` · `--stage3-verify` (MILP-certify survivors).
- Runs write `results/runs/blind_<type>_discovery.json`; validation writes `results/validation/`.
- Log every discovered `[[n,k,d]]` to `results/discovery_timeline.md` with its modality/status
  **before** any paper comparison. Optional deps (`ldpc`, `python-igraph`) unlock BP-OSD + exact BLISS.

## Tracking cadence (per ralph iteration)

Update `progress/qldpc-discovery/`: `loop_notes/current_iter.md` (overwrite each iter),
`RESEARCH_NOTE.md` (extend-in-place; refresh the formalization snapshot ~every 5 iters),
`medium_term.md` (10-iter window / bundle DAG / simplification cycle), `external_axioms.md`,
`agentic_lean_state.md`. Commit per substage on `bbc`; do not push unless asked.
