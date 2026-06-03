# current_iter — 8-GPU blind search, iter 4 (overwrite-mode)

## Anchor
Directive: clean up scripts (keep only useful), then RUN the large parameter space on 200 CPU only,
managed by .claude + phys-agentic-loop.

## EDIT
- Cleaned scripts/search/: removed ~16 scratch files (bench_*, test_*, microbench, profile_dist,
  validate_gpu, gpu_kernel.jl [ported to package], broken gpu_blind_search.jl, CUDA env). Left ONE
  clean driver: scripts/search/blind_search.jl (CPU-only blind search, 200-thread MAP-Elites).
- Diagnosed 2 smoke failures (tool-verified): bposd_distance (a) ERRORED on some degenerate random
  codes -> per-candidate try/catch; (b) cost ~ n via hardcoded max_iter=n (0.45s@n72 -> 87s@n600).
- PACKAGE FIX (julia/src/distance/bposd.jl): added a tunable `max_iter` kwarg to bposd_distance
  (default code.n => backward-compatible; BP+OSD still returns a valid UPPER bound). The search caps
  it (max_iter=30) for tractable distance across n<=1000.
- Driver: BLIND (naive weight-3 seeds, no paper data), per-thread workers loop screen(css_k) ->
  bposd_distance(max_iter=30,trials=32) -> d/sqrt(n) trust filter (<2.0) -> MAP-Elites by (n,k);
  archives merged; frontier written to progress/blind-search-8gpu/frontier.md. Distances honestly
  labeled BP-OSD UPPER bounds (uncertified).

## VERIFY (TRF-R)
- bposd max_iter edit: gross d_bound=12 at default AND at max_iter=30 (unchanged + cap valid). Ref 12.
- smoke (16 threads, WALL=20): exit 0, no crash, frontier produced (e.g. [[810,8,44]], [[180,12,12]]).
- FULL RUN launched: 200 threads, NMAX=1000, WALL=600s, TRIALS=32, MAXITER=30 (background byl4g988p).

## Status
Apparatus PROVEN; full 200-CPU run in flight. Frontier + certification of best codes -> on completion.
code_quality_policy_pass: R2 (bposd max_iter param + clean CPU driver, verified) -> PROVEN.
Honest: frontier distances are BP-OSD upper bounds; headline high-d codes need MILP/BZ certification [FUTURE].
