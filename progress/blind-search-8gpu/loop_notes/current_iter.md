# current_iter — iter 9: audit vs paper + pipeline broadening + BZ-boxing crash fix

## Anchor
User: compare blind-zero vs the bbc branch (paper arXiv:2606.02418 catalog + SOTA), audit the gap,
write it to progress/, then make changes to the Julia AND Python pipelines accordingly.

## PLAN
Audit coverage + methodology + pipeline gaps via a 10-agent Workflow; implement the blind-safe,
env-gated reach/certification changes the audit prioritizes.

## EDIT
- AUDIT (progress/audit-vs-paper/AUDIT.md): paper does varying check weight (Campaign 4: weight 4-6),
  structured patterns (XY/MX/SD), evolutionary campaigns, PBB (368/465 codes), BLISS dedup, MILP exact +
  multi-decoder. We were fixed weight-3, uniform-random, BB-only, single BP-OSD. Honest: our high-FOM
  large-n codes are UNCERTIFIED BP-OSD UBs; one solid claim = blind [[144,12,12]] rediscovery.
- blind_search.jl: WMIN/WMAX (varying weight), MODE css|pbb|both, ANSATZ structured seeding, GENS GA
  refinement, DEDUP canonical-hash distinct count, FIXLM deep single-lattice. ALL default to the
  original fixed-weight-3 CSS random scan (prior run reproduces).
- certify.jl: multi-seed BP-OSD + spread column, BZ-primary tightening, ENUM gated by ENUM_BUDGET, PBB
  (symplectic exact) handling, 12-col TSV (back-compat with 8-col).
- python/src/discovery/search.py (agent): weights= + dedup= parity on blind_search_css/_pbb. pytest 51
  passed / 3 skipped (paper-catalog-gated).

## PACKAGE BUG (package_debug_policy) — ROOT-CAUSED + FIXED
Certifier OOM-crashed (exit 144, ~14e9 allocs, uncatchable C abort) on the new high-weight (8/9),
high-κ (=80) n=144 codes. ROOT CAUSE: _bz_min_logical / _bz_min_symplectic / min_weight_logical ran
their hot loops in `do`-block closures that captured-and-reassigned best/enumerated -> Julia BOXES
them -> ~4.8 heap allocs PER COMBINATION (measured). `cap` bounded combinations, NOT memory -> GC death.
FIX: extracted allocation-free kernels (_bz_scan_weight!, _bz_scan_weight_symp!) + inline F(2) parity
in min_weight_logical (no per-combo matvec). Regression test julia/test/distance_alloc_regression_tests.jl
(3 captured crashers; pins <0.5 allocs/combination + sane d). NOT a thread/cap workaround — root fix.

## VERIFY (in flight: bg task b2i66o3dh)
(A) full runtests.jl — correctness (BZ d=4 @ [[18,4,4]], certified d=6 @ [[72,12,6]] must still hold)
+ new alloc regression. (B) re-certify the 8 OOM-crashers — must complete + demote (d0~13-21 -> ~6).
Default + all-flags search smoke already PASS (TEST1 reproduces weight-3 CSS; TEST2 shows wt 8/9, GA,
distinct=8). PENDING: paste green test tail -> COMMIT blind-zero -> port package fix to main.

## STATUS
Not complete — verification pending; then commit + port to main. completion_promise NOT emitted
(extension scope active). code_quality_policy_pass: R2 (package hot-loop fix + regression) -> PENDING VERIFY.
