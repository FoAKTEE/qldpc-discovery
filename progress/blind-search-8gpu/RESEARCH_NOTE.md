# RESEARCH NOTE — 8-GPU BLIND BB-CODE SEARCH (blind-zero, canonical)

**Mission.** From ZERO/scratch, run a catalog-BLIND search for BB quantum LDPC codes within
`[[n<=1000, k<=300, d<=300]]` using the pure-Julia `QCodeDiscovery` package, maximally parallel on
8x A100 GPUs + 256 CPU cores. Record + certify the discovered rate--distance frontier. Managed by the
ralph loop (.claude) + phys-agentic-loop methodology. Branch `blind-zero`; ultracode ON.

## Apparatus (all pure Julia, cross-validated vs the Python reference)
- GPU k-screen: batched GF(2) rank on all 8 A100s (CUDA extension), distributed per device.
- CPU distance: BP-OSD upper bound across 256 threads; MILP-BZ certified exact where feasible.
- Search: naive random weight-3 seeds (BLIND) -> k-screen -> distance -> MAP-Elites frontier by (n,k).

## Blind discipline (BINDING)
Naive seeds only; no paper data / no hardcoded codes / no catalog during search. Every [[n,k,d]] is
logged with modality (BP-OSD upper bound vs MILP-BZ certified) BEFORE any paper comparison; comparison
to the gross/Bravyi families is POST-HOC only.

## Status
- iter1: restored + audited + re-targeted `.claude` (was the finished Julia-migration mission) to this
  8-GPU blind-search mission; loop now manages it. Multi-GPU search driver being built by a Workflow.
- iter2: DIAGNOSED GPU 0% util — the package's batched GF(2) rank kernel was ONE-THREAD-PER-MATRIX
  (near-zero A100 occupancy, 0.22x the 256-core CPU). [SOLID, tool-verified]
- iter3: FIXED in the package — warp-per-matrix kernel (julia/ext/QCodeDiscoveryCUDAExt.jl) + threaded
  host packing (julia/src/parallel/gpu_cuda.jl). Correct (0 mismatches vs CPU incl. real BB), end-to-end
  1.1x the 256-core CPU (was 0.22x), kernel-isolated 98% util. Package tests green. [SOLID]
  KEY FINDING: nvidia-smi still ~0% during the SEARCH because GPU compute is only 3.1% of even the
  screen wall time (host-pack 325 ms >> GPU 10.5 ms), and the search's heavy cost is CPU BP-OSD distance.
  Screening cannot saturate 8 A100s. => to truly use the GPUs, move BP-OSD DISTANCE to GPU. [FUTURE]

- iter4: package CRASH (SIGSEGV/SIGABRT on high-nullity codes) root-caused to `_independent_mod` heap
  corruption (per-candidate growing-matrix vcat + full rref rebuild churned ~1MB arrays). FIXED in
  julia/src/distance/bposd.jl (single-pass incremental reduced basis) + tunable `max_iter` + regression
  test julia/test/bposd_regression_tests.jl (5 captured crashers, 35/35). Per package_debug_policy:
  root-caused IN the package, NOT worked around. [SOLID]
- iter5: continuous frontier checkpointing — monitor on :interactive threadpool (`-t 200,2`) rewrites
  frontier.md + frontier.md.tsv every CHECKPOINT s so intermediate results stream out. [SOLID]
- iter6: rate-aware trust filter (blind_search.jl) — cap d/sqrt(n) by k/n (1.8/1.4/1.1) to suppress
  BP-OSD high-rate overestimates (paper's signature); drops [[112,24,20]]. [SOLID]
- iter7: source + scripts ported to `main` (90816c8); runtests green there, regression 35/35. [SOLID]

## RESULTS — full scan + certification (DONE)
- **Scan** (-t 200,2, NMAX=1000, WALL=600s): screened=183151, dist_evals=10913, **418 frontier cells**,
  ~296 cand/s. Rate filter held: top frontier all low-rate (k/n<=0.06).
- **Certify** (-t 200, HITRIALS=300, HIMAXITER=120, BZ_NMAX=200): **418 certified, 39 EXACT**
  (min_distance_bz gap=0), 379 tightened-UB, 0 err. High-effort BP-OSD demoted scan overestimates
  (e.g. [[336,20,32]]->[[336,20,26]], [[528,16,40]]->[[528,16,28]], [[780,16,50]]->[[780,16,42]]).
- Top certified by FOM: [[840,16,46]] UB 40.30 · [[336,20,26]] UB 40.24 · [[600,16,38]] UB 38.51.
- Top EXACT certificates: [[56,6,8]] · [[70,6,8]] · [[42,6,6]] · [[84,12,6]] · [[60,8,6]] · [[72,8,6]].
- Files: progress/blind-search-8gpu/{frontier.md, frontier.md.tsv (all 418), certified.md (full table)}.

## POST-HOC VALIDATION (after recording — blind discipline honored)
**The blind search independently REDISCOVERED [[144,12,12]]** — the gross code's parameters — at (l,m)=(12,6)
with a DIFFERENT polynomial pair (A=x+x^4y^5+x^10y, B=x^4y^5+x^5y^3+x^9y^4) than the canonical
("y+y^2+x^3","y^3+x+x^2"); certifier tightened scan d0=14 -> d=12. Reached blind from naive random weight-3
seeds, no catalog. This is the held-out paper landmark recovered independently => apparatus validated.

## iter9 — AUDIT vs paper (arXiv:2606.02418) + pipeline broadening + package crash fix
- AUDIT (progress/audit-vs-paper/AUDIT.md, 10-agent workflow): the paper's SOTA needs VARYING check
  weight (Campaign 4: weight 4-6 -> stab weight 8-12), structured patterns (XY/MX/SD), evolutionary
  campaigns, the PBB non-CSS family (368/465 codes), BLISS dedup, MILP-exact + multi-decoder. Our blind
  run was fixed weight-3, uniform-random, BB-only, single cheap BP-OSD -> structurally cannot reach the
  weight-7/8/10 records or PBB. Honest: our high-FOM large-n codes are uncertified BP-OSD UBs; the one
  solid claim remains the blind [[144,12,12]] rediscovery.
- PIPELINE BROADENING (all env-gated; defaults reproduce the prior weight-3 CSS run). blind_search.jl:
  WMIN/WMAX, MODE css|pbb|both, ANSATZ, GENS, DEDUP, FIXLM. certify.jl: multi-seed BP-OSD + spread,
  BZ-primary tightening, ENUM gated by ENUM_BUDGET, PBB exact symplectic. python/src/discovery/search.py:
  weights= + dedup= parity (pytest 51 pass/3 skip). [SOLID]
- PACKAGE FIX (package_debug_policy): certify.jl OOM-crashed (exit 144, ~14e9 allocs, uncatchable) on
  the new high-weight/high-κ n=144 codes. ROOT CAUSE: _bz_min_logical/_bz_min_symplectic/min_weight_logical
  hot loops in `do`-closures boxed captured best/enumerated -> ~4.8 allocs/combination; `cap` bounded
  combinations not memory -> GC death. FIX: allocation-free extracted kernels + inline F(2) parity;
  regression test julia/test/distance_alloc_regression_tests.jl (3 captured crashers, <0.5 allocs/comb).
  Verified: runtests all PASS (exit 0); correctness landmarks preserved (enum d=4, BZ certified d=6 @
  [[72,12,6]]); certifier re-run on the 8 crashers completes + demotes ([[144,16,13]]->[[144,16,6]],
  3 EXACT). Committed blind-zero 5fc00aa; package fix ported to main. [SOLID]

## iter10 — broadened-search VALIDATION (n<=360) + a 2nd package fix
- 2nd package-discipline fix: DEDUP=1 made write_frontier run canonical_hash (0.1-1.3s/code) over all
  cells every checkpoint -> monitor stalled, no frontier written. Fixed: cheap representation-level
  distinct signature; rigorous BLISS dedup deferred post-hoc. (54d7dca; main a2b9f3e.)
- Broadened run (CSS n<=360, wt3-5, ansatz0.3, GA2, dedup): 177085 screened, 530 cells, stab-weight
  diversity 6/7/8/9/10 (was uniformly 6). Certifier: 530 certified, 99 EXACT, ZERO crashes — at-scale
  proof of the iter9 BZ allocation-free fix on exactly the high-weight code class that OOM-crashed before.
- Paper coverage (progress/audit-vs-paper/BROADENED_VS_PAPER.md): 10/28 catalog (n,k) present; reached
  paper d (UB) at 6. WINS unreachable at weight-3: [[360,8,30]] d=32 UB (paper FOM-20 weight-7),
  [[144,8,12]] d=12 (weight-6 MX), [[288,8,20]], [[288,16,12]]. OPEN gaps: (a) high-k codes (k=24-54)
  all missed — rate filter + FOM bias suppress them, needs a separate high-k campaign; (b) large-n d are
  uncertified BP-OSD UBs (some overestimates, e.g. [[288,12,16]] d=30 vs paper-exact 16 — needs MILP).
  Honest: weight axis closes the high-distance gap; NO certified beat on the paper's own block lengths. [SOLID]

## iter11-12 — user-requested gap work (#2 large-n cert, then #1 high-k campaign)
- #2 ISD (iter11, julia/src/distance/isd.jl): Lee-Brickell information-set decoding -> tight UPPER bound
  at large n. Finds low-weight logicals BP-OSD misses; a found logical of weight w PROVES d<=w (valid UB,
  not a lower-bound certificate). Verified: finds [[18,4,4]]=4, [[72,12,6]]=6, gross [[144,12,12]]=12 (2s;
  exact BZ CANNOT certify this), never below true d. Demotes the broadened overestimate [[288,12,30]]
  (BP-OSD d0=30) -> d=16 = the paper's exact (288,12) value. Committed b4f0b96, main 3065c2c. Honest:
  refutes overestimates; full MILP-grade large-n EXACT lower-bound cert remains the pure-Julia limit. [SOLID]
- #1 high-k campaign (iter12, blind_search.jl OBJECTIVE=k): univariate/CRT seeding (random params,
  lem:crt_k family) + filter off + k-sort. Recovers the k-AXIS (k=24..160 at n<=360; FOM mode maxed at
  k=20 with 0 cells k>=24). ISD certifies true d, demoting BP-OSD garbage ([[360,160,156]]->EXACT d=2).
  HONEST: pure univariate is d=2 at extreme k (k=24 reaches d=6-10 UB); the paper's high-k codes (d=4-8)
  use richer weight-8 cross-factored structure -> we reach the right (n,k) but lower d. progress/audit-vs-
  paper/HIGHK_VS_PAPER.md. Next lever (documented): higher-weight/factored high-k seeds. [SOLID]

- iter13 (high-k distance lever): added factored A=(1+y^a)(1+x^j) + mixed seed families to OBJECTIVE=k
  (generic algebraic, random params). Re-ran (934 cells, 344 EXACT) + ISD. LIFTED high-k distance d=2 ->
  d=5: now [[294,78,5]], [[336,72,5]], [[288,48,5]] (k=48..78 at d=5). vs paper [[288,50,8]] (right k,
  d=5<8). Honest: k-axis recovered + high-k d lifted 2->5; the paper's d=8-14 high-k codes use richer
  weight-8 cross-factored algebra beyond our generic seeds — documented open structural frontier. [SOLID]

- iter17 (PBB family): MODE=pbb exercised — 12 EXACT non-CSS codes (n<=168, d<=4), but blind random
  (A,B,C,D) seeding is too sparse (~0.07% commute+nontrivial) to reach the paper's 32 structured PBB
  points (headline [[360,10,40]] FOM44). progress/audit-vs-paper/PBB_VS_PAPER.md. [SOLID]
- iter18 (evolutionary method = paper's core): evolve_ansaetze exercised. UNIFYING FINDING — it functions
  but its BP-OSD FITNESS chases OVERESTIMATES (evolved "best" [[144,32,22]] FOM107 is a BP-OSD artifact,
  true d~2). This is precisely why the paper used MILP-exact distance IN THE LOOP. Concrete fix available:
  ISD-based fitness (iter11 tool) + parallelize evolve_ansaetze. progress/audit-vs-paper/EVOLUTION_FINDING.md.
  [SOLID]

## CROSS-AXIS CONCLUSION (iter9-18)
Blind generic/random search recovers the code families + the rate-distance frontier SHAPE; the paper's
specific high-FOM optima need STRUCTURED/catalog constructions (high-k d=8-14, PBB FOM-44) or MILP-grade
exact distance (large-n cert, AND trustworthy search fitness — the evolution finding). Open levers all
cross a user-set constraint (pure-Julia -> MILP; blind -> catalog-seeded; or the ISD-fitness build).

## Landmarks (post-hoc reference only; NOT used by the search)
gross [[144,12,12]] (k=12,d=12) · [[72,12,6]] · [[288,24,12]]=gross+gross.
