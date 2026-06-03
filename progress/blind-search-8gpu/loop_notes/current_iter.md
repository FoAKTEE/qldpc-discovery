# current_iter — 8-GPU blind search, iter 7 (overwrite-mode)

## Anchor
User: output intermediate results continuously to frontier. Add live checkpointing, then launch the run.

## EDIT (scripts/search/blind_search.jl)
- Reworked to a SHARED MAP-Elites archive (lock-protected; workers touch it only on an improvement ->
  negligible contention) + atomic SCREENED/DISTEVALS counters.
- MONITOR task on the :interactive threadpool (so it is NOT starved by the CPU-bound default-pool
  workers) rewrites frontier.md + prints a progress line every CHECKPOINT seconds (default 20s).
  Authoritative final write at the end. Run with `julia -t 200,2` (2 interactive threads).

## VERIFY (TRF-R)
- Continuous output confirmed (-t 48,2, CHECKPOINT=6): checkpoints fire DURING the run —
  [t=6s] screened=992 cells=28 ... [t=20s] screened=2755 cells=93 topFOM=38.4 [[180,12,24]] ... DONE.
  frontier.md is rewritten live (header has running screened/dist_evals/cells/elapsed + top-40 table).
- (Earlier -t 48 default-pool attempt: monitor starved until end -> fixed via :interactive.)

## Status
Live-checkpoint driver verified. FULL run launched: -t 200,2, NMAX=1000, WALL=600, CHECKPOINT=20,
OUT=progress/blind-search-8gpu/frontier.md (streams live). Watch: cat progress/blind-search-8gpu/frontier.md.
Honest: frontier d's are BP-OSD UPPER bounds (uncertified); best small-n codes to be MILP/BZ-certified post-run.
code_quality_policy_pass: R1 (continuous checkpointing via :interactive monitor) -> PROVEN.
