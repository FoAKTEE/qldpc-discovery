# RESEARCH NOTE — qldpc-discovery FULL JULIA + GPU MIGRATION (canonical)

**Mission.** Migrate the entire `qcode_discovery` Python package + its C/C++ external dependencies
(HiGHS, ldpc, igraph) to a pure-Julia package (`julia/`), GPU-parallel runnable. Python =
source of truth; the Julia port must reproduce it on every landmark. Branch `main`; ultracode ON.

## Status snapshot (after wave-2 + packaging, iter 3) — FUNCTIONALLY COMPLETE
- **Full pure-Julia package, no C/C++, releasable.** All 16 subsystems ported + cross-validated vs
  Python; the package runs blind discovery END-TO-END in Julia. All 3 C/C++ deps reimplemented
  natively (HiGHS→BZ; ldpc→BP-OSD; igraph→IR canonical form). GPU kernel **verified on the A100**
  (CUDA extension; bit-identical to CPU, 2–21×). 55 Julia tests pass. Professional packaging done:
  README, examples/quickstart.jl, bin/qcode-discover.jl CLI, julia-ci.yml, LICENSE, [weakdeps] CUDA ext.
- **Remaining (staged, honest):** certifying the gross code's d=12 *exactly* in Julia (BZ certifies
  moderate d; large-d needs the overlapping-info-set extension — BP-OSD already gives d_bound=12) and
  `.tex` catalog parsing (built-in landmark codes used instead). Python kept as reference until these close.

## (prior) Status snapshot (after wave-1 workflow, iter 2)
- **Ported + cross-validated (✅):** GF(2) algebra, ring/circulants, BB construction + k + FOM,
  theorems, enumeration distance, **Brouwer–Zimmermann certified exact distance** (HiGHS replacement;
  [[72,12,6]] d=6 in 0.22 s) · **PBB construction + k** · **Tanner decomposability** · **BLISS dedup →
  pure-Julia individualization-refinement canonical form** (igraph replacement; gross≡relabel≡blind) ·
  **LC-CSS equivalence** · **BP-OSD → pure-Julia BP+OSD** (ldpc replacement; gross d_bound=12==Python) ·
  **data-parallel GF(2)** (Threads; CUDA.jl path w/ CPU fallback). **46 Julia tests pass.**
  All three C/C++ deps (HiGHS, ldpc, igraph) now have working pure-Julia replacements.
- **Staged (🟡/🔴):** PBB symplectic distance; evaluation cascade; search/GA/evolve; validation; CLI;
  actual CUDA kernels (CUDA.jl not installed) + threaded search fan-out; the SCALABLE exact solver to
  certify the gross code's d=12 @ n=144 in Julia (overlapping-info-set BZ). See `port_plan.md`.

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
