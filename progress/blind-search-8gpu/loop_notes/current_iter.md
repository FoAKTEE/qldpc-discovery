# current_iter — 8-GPU blind search, iter 1 (overwrite-mode)

## Anchor
Restore + audit + re-target the agentic management infra (.claude ralph loop + phys-agentic-loop) to
manage the from-scratch 8-GPU blind BB-code search on blind-zero.

## Done this iter
- Migrated the new parallel python/+julia/ package onto blind-zero (commit 7a014de).
- Restored .claude from git history (d3c0a2b, pre-publication-cleanup).
- AUDIT: the hook scripts (inject_infra.sh, inject_alignment.sh, ralph_stop_guard.sh, settings.json)
  are GENERIC infra (read phys-agentic-loop + ralph state; no hardcoded mission) -> kept. The only
  stale content was ralph-loop.local.md (held the finished Julia-migration mission, branch main,
  iter 4) -> rewrote it for the 8-GPU blind-search mission (active:true, branch blind-zero,
  promise QLDPC_BLINDZERO_8GPU_SEARCH_COMPLETE, blind_discovery_policy + gpu_policy).
- Created progress/blind-search-8gpu/{RESEARCH_NOTE, frontier, loop_notes}.

## In flight
- Workflow wl9x3o0ul (ultracode): building + validating the multi-GPU search driver on the 8 A100s
  (scripts/search/gpu_blind_search.jl) + a demonstrator run. Loop will manage runs once it lands.

## Next
1. Land + validate the driver (GPU rank==CPU on all 8 devices; all 8 used).
2. Run substantial blind search n<=1000; record frontier; certify best codes.

## Verifier
(infra-only iter) .claude audited + re-targeted; phys-agentic-loop present.
code_quality_policy_pass: R0 (infra restore/audit/re-target) — PROVEN.
