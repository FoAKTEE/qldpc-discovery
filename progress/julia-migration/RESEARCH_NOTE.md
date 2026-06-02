# RESEARCH NOTE — qldpc-discovery FULL JULIA + GPU MIGRATION (canonical)

**Mission.** Migrate the entire `qcode_discovery` Python package + its C/C++ external dependencies
(HiGHS, ldpc, igraph) to a pure-Julia package (`julia/`), GPU-parallel runnable. Python =
source of truth; the Julia port must reproduce it on every landmark. Branch `main`; ultracode ON.

## Status snapshot
- **Ported + cross-validated (✅):** GF(2) algebra, ring/circulants, BB construction + k + FOM,
  theorems (thm:ab_d2, lem:crt_k), enumeration distance, **Brouwer–Zimmermann certified exact
  distance** (matches HiGHS MILP; certifies [[72,12,6]] d=6 in 0.22 s, pure Julia). 28 Julia tests pass.
- **Staged (🟡/🔴):** PBB + symplectic distance, BP-OSD (ldpc), Tanner decomposability, BLISS dedup
  (igraph), LC equivalence, evaluation cascade, search/GA/evolve, validation, CLI, the GPU+parallel
  layer (CUDA.jl), and the scalable exact solver for d=12 @ n=144. See `port_plan.md`.

## Honest scope
A complete, correct, GPU-parallel pure-Julia reimplementation — including from-scratch replacements
for a world-class MIP solver and a compiled BP-OSD decoder — is a large effort driven by the ralph
loop + Workflows over many iterations. Each step is admitted only on a parity test vs Python. No
faked certificates; the Python package stays until Julia reaches parity.

## Next tactics (highest leverage first)
1. PBB (non-CSS) + symplectic distance → unblocks dedup/LC parity tests on PBB codes.
2. BLISS dedup (pure-Julia canonical form) → enables "is the blind code the gross code" in Julia.
3. BP-OSD (pure-Julia BP+OSD) → the fast Stage-2 oracle; unblocks the search cascade.
4. evaluation cascade + search/GA → end-to-end blind discovery in Julia.
5. GPU layer (CUDA.jl batched GF(2) rank + threaded search) + benchmark.
6. Scalable exact solver (overlapping-info-set BZ) → certify gross d=12 in Julia.

## Cross-validation landmarks (Python = truth)
gross [[144,12,12]] k=12 & d=12 · blind [[144,12,12]] k=12 (rediscovered + MILP-certified this session)
· [[72,12,6]] d=6 · thm:ab_d2 d=2 · lem:crt_k k=8l/3 (16@(6,6), 24@(9,9)) · [[36,2,6]] PBB · dedup
canonical-hash equalities · LC verdicts.
