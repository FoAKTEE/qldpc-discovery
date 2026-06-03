---
active: true
iteration: 17
session_id: ""
max_iterations: 300
completion_promise: "QLDPC_BLINDZERO_8GPU_SEARCH_COMPLETE"
started_at: "2026-06-03T00:00:00Z"
role: Ralph-loop local state for qldpc-discovery — 8-GPU BLIND BB-CODE SEARCH (blind-zero)
scope: .claude/ralph-loop.local.md — surfaced on SessionStart by inject_infra.sh, gated on Stop by ralph_stop_guard.sh
mission: "Run + manage a from-scratch, catalog-BLIND search for BB quantum LDPC codes within [[n<=1000, k<=300, d<=300]] using the pure-Julia QCodeDiscovery package on 8x A100 GPUs + 256 cores, maximally parallel; record + certify the discovered frontier"
branch: blind-zero
pua_flavor: "musk"
orchestration:
  ultracode: true
  rule: |
    Ultracode is ON. Drive substantive steps with Workflows + adversarial verification. The GPU
    search driver, large search runs, and code-certification are the fan-out/verify units. Solo only
    for trivial edits, tracking, and launching/monitoring background runs.
discipline:
  - ../phys-agentic-loop/alignment.md (binding operational rules; MUSK mode always on)
  - ../phys-agentic-loop/code_quality_policy.md (R0-R4 risk tiers, KISS/DRY/AHA, FINDING SCHEMA)
  - ../phys-agentic-loop/_common/agentic_lean_contract.md (typed-ledger admission gates)
  - ../phys-agentic-loop/_common/markers.md (HYPOTHESIS/PRELIMINARY/SOLID/BLOCKING/FUTURE/HOLE/AXIOM)
blind_discovery_policy:
  policy: "BINDING — search is catalog-blind"
  rule: |
    The search rediscovers codes from ZERO: naive random weight-3 polynomial seeds, FOM fitness,
    kernel-admitted distances. NO paper data, NO hardcoded [[n,k,d]], NO catalog read during search.
    Every discovered [[n,k,d]] is logged to the frontier with its evidence modality + verifier status
    BEFORE any paper comparison. Comparison to known codes (gross family, Bravyi catalog) is POST-HOC
    only. Distances are honest: BP-OSD = UPPER bound; min_distance_bz gap=0 = certified exact.
gpu_policy:
  policy: "BINDING — 8 GPUs + max parallel"
  rule: |
    The k-screening (GF(2) rank) runs batched on ALL 8 A100s in parallel (CUDA.device! per device,
    concurrent tasks); the distance oracle (BP-OSD) runs across all 256 CPU threads. Verify GPU rank
    == CPU rank on each device (0 mismatches) before trusting a run. Report devices actually used.
package_debug_policy:
  policy: "BINDING — fix bugs in the package, never work around them"
  rule: |
    Whenever a bug/crash/error/incorrect-result is encountered ANYWHERE (driver, run, test), ROOT-CAUSE
    it and FIX IT IN THE JULIA PACKAGE (julia/src or julia/ext) with a regression test in julia/test,
    BEFORE proceeding. Do NOT paper over it: no thread-count reduction, no silent try/catch swallowing,
    no "skip the bad case" without first understanding + fixing the underlying defect. Reproduce ->
    instrument to the exact failing input + package function -> fix at the root -> add a regression
    test -> verify the original failure is gone. Only then resume. A blanket guard may be added AFTER
    the root cause is fixed (defense in depth), never instead of it.
search_space:
  rule: "BB codes, n = 2*l*m <= 1000 (l*m <= 500), weight-3 polynomials; report k<=300, d<=300."
tracking_files:
  canonical: "progress/blind-search-8gpu/RESEARCH_NOTE.md"
  per_iter: "progress/blind-search-8gpu/loop_notes/current_iter.md"
  frontier: "progress/blind-search-8gpu/frontier.md"
  driver: "scripts/search/gpu_blind_search.jl"
---

# Ralph loop — qldpc-discovery 8-GPU BLIND BB-CODE SEARCH (blind-zero)

**Holy grail.** From ZERO and from SCRATCH, run a catalog-BLIND search for bivariate-bicycle (BB)
quantum LDPC codes within `[[n<=1000, k<=300, d<=300]]` using the pure-Julia `QCodeDiscovery`
package, **maximally parallel on 8x A100 GPUs + 256 CPU cores**. Record the discovered rate--distance
frontier; certify the best codes (exact distance where feasible). Branch `blind-zero`. Commit per
substage; do NOT push unless asked. Ultracode: Workflows + adversarial verify for substantive steps.

Canonical state: `progress/blind-search-8gpu/RESEARCH_NOTE.md` + `frontier.md` (read at the start of
every iteration).

## Each iteration (7 steps; PLAN/EDIT/VERIFY/COMMIT/UPDATE/ESCALATE/DO-NOT-STOP)

1. **PLAN** — read RESEARCH_NOTE + frontier; pick the highest-leverage step (driver correctness,
   larger/longer search, broader lattice coverage, certify a frontier code). State it as a typed node.
2. **EDIT** — implement it (the GPU driver under `scripts/search/`, or a certification step). Keep the
   search BLIND (naive seeds; no paper data). Don't edit the `julia/` package's own deps (CUDA = weakdep).
3. **VERIFY** — run it; paste evidence: GPU rank == CPU on each device; #devices used; candidates
   screened; the frontier rows with modality (BP-OSD upper bound / MILP-BZ certified). A
   `code_quality_policy_pass:` line per new declaration. No faked numbers.
4. **COMMIT (no push)** on `blind-zero`; paste the verifier tail.
5. **UPDATE** — RESEARCH_NOTE, frontier.md (append/refresh discovered codes), current_iter.md.
6. **ESCALATE** — if a node stalls 3 iters / 30 min, run a Workflow (multi-agent build/verify) or
   spawn a deep-research agent per the ultracode rule.
7. **DO NOT STOP.** Output the completion promise ONLY when ALL hold:
   - `scripts/search/gpu_blind_search.jl` runs the blind search on ALL 8 GPUs (k-screen) + 256 CPU
     threads (distance), with GPU rank == CPU rank verified on every device.
   - A substantial from-scratch BLIND run is recorded: candidates screened, distance evals, and the
     MAP-Elites frontier (by (n,k), best FOM) over BB codes with n<=1000 — in `progress/blind-search-8gpu/`.
   - The best frontier codes carry honest verifier status (BP-OSD upper bound, or MILP-BZ certified
     exact where feasible); blind discipline upheld (any paper comparison is post-hoc).
   - `frontier.md` has no `[HOLE]`/`[BLOCKING]` certified-claim.

Completion promise (output ONLY when unequivocally TRUE):
<promise>QLDPC_BLINDZERO_8GPU_SEARCH_COMPLETE</promise>
