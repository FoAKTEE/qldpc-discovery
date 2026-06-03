# current_iter — Julia+GPU migration, iter 4 (overwrite-mode)

## Anchor
"Pack the Julia package logically in a few subfolders + one usage example notebook." Plus a
releasability fix surfaced while testing the notebook's load path.

## Done this iter
- Reorganized julia/src/ (was flat) into 6 logical subpackages (git mv, mirrors the Python layout):
  algebra/ (gf2,polynomials) · codes/ (codes,pbb,theorems) · distance/ (distance,distance_exact,
  bposd,pbb_distance) · structure/ (tanner,dedup,clifford) · discovery/ (evaluation,search,evolve,
  validation) · parallel/ (gpu,gpu_cuda). Updated QCodeDiscovery.jl include paths (dependency order
  preserved). README layout section updated.
- Added julia/examples/demo.ipynb — a 17-cell Jupyter (Julia kernel) demo: construct+verify, BZ exact
  distance, theorems, blind discovery + validation, dedup (blind==gross), BP-OSD, GPU/parallel. Valid
  JSON; code cells run end-to-end.
- RELEASABILITY FIX: `using QCodeDiscovery` (precompile path) failed — search.jl `import Random` needs
  Random declared as a [deps] (worked under include() in tests, not under `using`). Added Random to
  Project.toml; package now precompiles cleanly (944ms) and loads via `using`. Added a "using" load
  step to julia-ci.yml so this is guarded in CI.

## Status
55 Julia tests pass (14 testsets) after the reorg; package loads via both include() and `using`.
Subfoldered, notebook-demoed, releasable. Python kept as reference (per user) until the gross-d=12
exact-certificate gap closes.

## Verifier
julia --project=julia -t auto julia/test/runtests.jl -> 55 pass (14 testsets), no failures.
julia --project=julia -e 'using QCodeDiscovery' -> precompiles + loads OK.
demo.ipynb code cells run end-to-end.
code_quality_policy_pass: R1 (reorg + notebook + dep fix) — PROVEN.
