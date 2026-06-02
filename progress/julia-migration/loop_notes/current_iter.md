# current_iter — Julia+GPU migration, iter 2 (overwrite-mode)

## Anchor
Wave-1 migration via Workflow (ultracode): port 6 subsystems to pure Julia, each cross-validated
against the Python source of truth, then integrate + adversarially re-verify.

## Done this iter
- Workflow wmof8y3vf (6 agents, 178k tok): ported pbb, tanner, dedup, clifford(lc), bposd, gpu →
  julia/src/. All 6 cross-validated vs Python.
- Integrated into QCodeDiscovery.jl (includes + exports); added SHA stdlib dep; wrote parity_tests.jl.
- Adversarial re-verification (integrated module, my own tests incl. extra cases): **46 tests pass**.
  - PBB: n=72,k=4 commuting tuple; non-commuting rejected.
  - Tanner: gross=1 component; decomposable example=4.
  - dedup (igraph→pure Julia): canonical_hash invariant over 4 relabel seeds; gross≡blind[[144,12,12]];
    ≠ other codes.
  - LC: CSS_GROUP verdict.
  - BP-OSD (ldpc→pure Julia): gross d_bound=12 == Python (d_X=12; per-sector d_Z is a looser UB — honest).
  - GPU: batched_rank==serial gf2_rank; batched_css_k==css_k; 256 threads; CUDA.jl absent → CPU path.
- All three C/C++ deps now have working pure-Julia replacements (HiGHS→BZ, ldpc→BP+OSD, igraph→IR).

## Next (highest leverage)
1. PBB symplectic distance (exact, on the symplectic matrix).
2. evaluation cascade + search/GA → end-to-end blind discovery in Julia.
3. Install CUDA.jl + write/benchmark the actual GPU batched-rank kernel + threaded search fan-out.
4. Scalable exact solver (overlapping-info-set BZ) to certify gross d=12 in Julia.

## Verifier
julia --project=julia -t auto julia/test/runtests.jl -> 46 pass (11 testsets), exit 0.
code_quality_policy_pass: R2 (6 subsystems ported + cross-validated) — PROVEN.
