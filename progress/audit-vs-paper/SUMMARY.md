# SUMMARY — audit of blind-zero vs the paper (arXiv:2606.02418) + pipeline improvements

Capstone consolidating iterations 9–14. Full detail in `AUDIT.md`, `BROADENED_VS_PAPER.md`,
`HIGHK_VS_PAPER.md`, and `../blind-search-8gpu/RESEARCH_NOTE.md`.

## What was asked
Compare the `blind-zero` blind-discovery pipeline to the `bbc` branch (the paper + its catalog), audit
the gap, write it to `progress/`, then change the Julia and Python pipelines accordingly. Then (follow-up)
add large-n exact certification (#2), then a high-k campaign (#1).

## The gap (AUDIT.md)
The paper reaches SOTA via VARYING check weight (Campaign 4: weight 4–6), structured polynomial patterns
(XY/MX/SD), evolutionary campaigns, a PBB non-CSS family (368/465 codes), BLISS dedup, and MILP-exact +
multi-decoder certification. The blind run was fixed weight-3, uniform-random, BB-only, single BP-OSD —
so it structurally could not reach the weight-7/8/10 records or the high-k / PBB families.

## What was built (all committed on blind-zero AND main; flag-gated to reproduce the prior run)
- **Search** (`scripts/search/blind_search.jl`): varying check weight (WMIN/WMAX), PBB search (MODE),
  structured-ansatz seeding (ANSATZ), GA refinement (GENS), dedup (DEDUP), deep single-lattice (FIXLM),
  and a high-k campaign mode (OBJECTIVE=k) with univariate/factored/mixed structural seeds.
- **Certify** (`scripts/search/certify.jl`): multi-seed BP-OSD + spread, ISD-primary tightening,
  Brouwer–Zimmermann exact where it completes, enum gated by a tractable budget, PBB symplectic exact.
- **Package**: `julia/src/distance/isd.jl` (Lee–Brickell ISD — tight large-n upper bound / overestimate
  refuter); allocation-free BZ/enum kernels; Python `weights=`/`dedup=` parity.

## Results (honest)
- **Weight axis closed the high-distance gap**: the broadened search reached `[[360,8,30]]` (paper's
  FOM-20 weight-7 code) and `[[144,8,12]]` (weight-6 MX) — impossible at fixed weight-3.
- **ISD (#2)** finds the gross `[[144,12,12]]` d=12 that exact BZ cannot certify, and demotes the
  overestimate `[[288,12,30]]` → d=16 (the paper's exact value). It is an UPPER bound (refuter), not a
  lower-bound certificate.
- **High-k campaign (#1)** recovered the k-axis (k=24…160; was capped at 20). Factored/mixed seeds lifted
  high-k distance from d=2 → d=5 (`[[294,78,5]]`, `[[336,72,5]]`, `[[288,48,5]]`). Three generic families
  tested (univariate d2, factored/mixed d5, cross-factored d4) — high-k distance caps at d=4–5 blind.
- **PBB family** exercised (MODE=pbb): 12 EXACT non-CSS codes found, but blind random (A,B,C,D) seeding is
  far too sparse (~0.07% commute+nontrivial) to reach the paper's 32 structured PBB points (`PBB_VS_PAPER.md`).
- **One solid blind landmark throughout**: the independent rediscovery of `[[144,12,12]]` (gross-code
  parameters) from random seeds.

## Consistent cross-axis finding
Across high-distance (weight), high-k (3 structural families), and PBB: **blind generic search recovers
the code families and the rate–distance frontier shape, but the paper's specific high-FOM optima**
(weight-7 d=30, high-k d=8–14, PBB FOM-44) **require structured/catalog-derived constructions** — beyond
generic blind seeds within pure-Julia.

## Two package bugs found + fixed (root-caused, regression-tested, ported)
1. BZ closure-boxing OOM (uncatchable crash on high-weight codes) → allocation-free kernels.
2. DEDUP per-checkpoint `canonical_hash` stall → cheap representation-level distinct signature.

## Honest limits / open frontier (research decisions for the user)
- **No certified beat of the paper on its own block lengths.** Our large-n high-FOM codes are BP-OSD/ISD
  UPPER bounds; the EXACT-certified codes are small-n.
- **MILP-grade large-n EXACT lower-bound certification** (the paper's HiGHS role) is beyond pure-Julia —
  needs relaxing the pure-Julia constraint or a major Tulip+branch-and-bound build.
- **The paper's d=8–14 high-k codes** use targeted weight-8 cross-factored algebra; generic structural
  search reaches the right k at d=4–5 but not their distance (brute-force d≥6 search timed out).

## Blind discipline
Every search change broadens reach with RANDOM/parametric seeds (weight sampling, ansatz, PBB
perturbations, univariate/factored families) — no paper polynomial or catalog value is ever injected.
Certification changes add proof/refutation, not catalog knowledge. Paper comparison is strictly post-hoc.
