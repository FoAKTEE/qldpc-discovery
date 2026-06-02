---
active: true
iteration: 3
session_id: ""
max_iterations: 300
completion_promise: "QLDPC_JULIA_GPU_MIGRATION_COMPLETE"
started_at: "2026-06-02T22:40:00Z"
role: Ralph-loop local state for qldpc-discovery — FULL JULIA + GPU MIGRATION mission
scope: .claude/ralph-loop.local.md — surfaced on SessionStart by inject_infra.sh, gated on Stop by ralph_stop_guard.sh (native)
mission: "Migrate the entire qcode_discovery package AND its C/C++ external dependencies to pure Julia, GPU-parallel runnable"
branch: main
pua_flavor: "musk"
orchestration:
  ultracode: true
  rule: |
    Ultracode is ON. Author and run a Workflow for every substantive migration step (port a
    subsystem, design the scalable solver, build the GPU layer). Fan out agents to port modules
    in parallel; each port MUST cross-validate its Julia output against the Python package
    (src/qcode_discovery/ = source of truth) on concrete landmarks before being accepted.
    Adversarially verify correctness. Solo only for trivial/mechanical edits and tracking.
discipline:
  - ../phys-agentic-loop/alignment.md (binding operational rules; MUSK mode always on)
  - ../phys-agentic-loop/code_quality_policy.md (R0-R4 risk tiers, KISS/DRY/AHA, FINDING SCHEMA)
  - ../phys-agentic-loop/_common/agentic_lean_contract.md (typed-ledger admission gates)
  - ../phys-agentic-loop/_common/progress_principles.md (promise-tag rule, per-substage commits)
  - ../phys-agentic-loop/_common/markers.md (HYPOTHESIS/PRELIMINARY/SOLID/BLOCKING/FUTURE/HOLE/AXIOM)
parity_policy:
  policy: "BINDING — Julia must reproduce Python"
  rule: |
    The Python package src/qcode_discovery/ is the SOURCE OF TRUTH and stays in the repo until the
    Julia port reaches full parity. Every ported Julia module ships a test that matches the Python
    result on concrete landmarks (gross k=12 & d=12; [[72,12,6]] d=6; thm:ab_d2 d=2; lem:crt_k k=8l/3;
    PBB commutation/k; dedup canonical-hash equalities; LC verdicts; a blind-search run). No C/C++
    dependency in the Julia package: HiGHS->pure-Julia exact solver, ldpc BP-OSD->pure-Julia decoder,
    igraph BLISS->pure-Julia colored-graph canonicalization. Honest markers; never fake a certificate.
gpu_policy:
  policy: "BINDING — parallel + GPU"
  rule: |
    Everything must be parallel-runnable on GPUs. Use CUDA.jl for the data-parallel kernels (batched
    GF(2) rank for k-screening; batched BP decoding), Julia threads/@distributed for the search fan-out.
    Provide a CPU fallback when no GPU/CUDA.jl is present (the package must still load + test on CPU).
tracking_files:
  canonical: "progress/julia-migration/RESEARCH_NOTE.md"
  per_iter: "progress/julia-migration/loop_notes/current_iter.md"
  port_plan: "progress/julia-migration/port_plan.md"
---

# Ralph loop — qldpc-discovery FULL JULIA + GPU MIGRATION

**Holy grail.** Migrate the entire `qcode_discovery` Python package — *including its C/C++ external
dependencies* (HiGHS MILP, `ldpc` BP-OSD, `igraph` BLISS) — to a **pure-Julia** package under
`julia/`, with **everything parallel-runnable on GPUs** (CUDA.jl + Julia threads). The Python package
is the validation reference; the Julia port must reproduce it on every landmark. Branch `main`.
Commit per substage; do NOT push. Ultracode: drive substantive steps with Workflows + adversarial verify.

Canonical state: `progress/julia-migration/RESEARCH_NOTE.md` and `port_plan.md` (read at the start of
every iteration; pick the single highest-leverage unported/`[HOLE]`/`[BLOCKING]` module).

## Each iteration (7 steps; PLAN/EDIT/VERIFY/COMMIT/UPDATE/ESCALATE/DO-NOT-STOP)

1. **PLAN** — read RESEARCH_NOTE + port_plan; pick the highest-leverage module to port/finish.
   State it as a typed node (component, Julia target file, Python reference, risk tier R0-R4).
2. **EDIT** — port it to `julia/src/` (idiomatic Julia, no C/C++). Docstring carries the Python
   anchor + risk tier. Add a parity test cross-validated against `src/qcode_discovery/`.
3. **VERIFY** — `julia --project=julia julia/test/runtests.jl` green; the parity test matches Python
   numerically. Tee a `code_quality_policy_pass:` line (each new decl: PROVEN/PARTIAL/PLACEHOLDER).
   No faked certificate; honest markers for staged pieces.
4. **COMMIT (no push)** on `main`; paste the verifier tail in the body.
5. **UPDATE** — RESEARCH_NOTE (move ported modules to [SOLID]), port_plan, current_iter.md.
6. **ESCALATE** — if a node stalls 3 iters / 30 min, or needs design: run a Workflow (judge-panel /
   multi-agent port + adversarial verify) per the ultracode orchestration rule.
7. **DO NOT STOP.** Output the completion promise ONLY when ALL hold:
   - Every Python subsystem has a pure-Julia equivalent under `julia/` (GF2, ring/circulant, BB+PBB,
     metrics, exact distance + scalable solver, BP-OSD, enumeration, BLISS dedup, LC equivalence,
     evaluation cascade, search/GA/evolve, CLI).
   - NO C/C++ dependency remains in the Julia package (HiGHS/ldpc/igraph all reimplemented in Julia).
   - GPU + parallel: CUDA.jl data-parallel kernels + threaded search, with a CPU fallback; benchmarked.
   - `julia/test/runtests.jl` green AND every parity landmark matches Python (gross k=12 & d=12;
     [[72,12,6]] d=6; thm:ab_d2 d=2; lem:crt_k k=8l/3; PBB; dedup; LC; a blind-search run).
   - port_plan.md has no `[HOLE]`/`[BLOCKING]` module.

Completion promise (output ONLY when unequivocally TRUE):
<promise>QLDPC_JULIA_GPU_MIGRATION_COMPLETE</promise>
