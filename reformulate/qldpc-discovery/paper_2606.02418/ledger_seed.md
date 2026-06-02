# Ledger Seed — arXiv:2606.02418 "Evolutionary Discovery of Bivariate Bicycle Codes with LLM-Guided Search"

Typed-ledger seed for pipeline-0 (source-import) -> pipeline-1 (elaboration).
Each entry follows the Accepted Object Schema of `_common/agentic_lean_contract.md`:
`id | type | context | claim | modality | evidence | dependencies | assumptions | status | provenance`.
Modalities per the contract; status in {checked, conditional, approximate, empirical, conjectural, refuted, unsafe, noncomputable}.
Markers ([HOLE]/[FUTURE]/[BLOCKING]/[AXIOM]) per `_common/markers.md`.

Provenance format: `P.l.NNN` = paper.tex line N; `S.l.NNN` = supplemental.tex line N; tex labels preserved VERBATIM.

Ground-truth algebra (shared `Sigma`/`Gamma`, asserted, not re-derived here):
ring `R = F2[x,y]/(x^l-1, y^m-1)`; `n = 2*l*m`; BB `H_X=(A|B)`, `H_Z=(B^T|A^T)`;
PBB `H = [[A,B,C,D],[0,0,B^T,A^T]]`; `k = 2lm - 2*rank_F2(H_X)`; `FOM = k d^2 / n`.

---

## A. Pipeline components (13 typed entries)

### PC-01 — Generator-ansatz evolution (OpenEvolve MAP-Elites)

- **type**: method/search-operator
- **context**: Evolve a generator program `G(l,m) -> {(A_i,B_i)}` (4-tuples for PBB) via LLM-proposed
  code diffs; 4-6 islands, migration every 12-25 iters; MAP-Elites dims = (#lattices with k>=8 codes,
  total such codes); Campaign-4 uses (term-count, monomial-structure) dims. 5 campaigns, ~1650 iters,
  ~2e5 candidates, ~140h, ~US$400 (per-row sum ~US$237; remainder = ablation + exploratory runs).
- **claim**: The LLM-guided evolutionary loop is the proposal mechanism; it carries NO admission authority —
  every candidate is admitted only by the downstream scientific kernel (Stages 1-3 / Tiers 1-3).
- **modality**: LiteratureGrounded (method description; no formal guarantee of output validity)
- **evidence**: P.l.217-282 (sec:framework, sec:campaigns), tab:campaigns P.l.288-300
- **dependencies**: PC-02..PC-13 (all admission gates)
- **assumptions**: openevolve + litellm available (MISSING locally); ansatz outputs not guaranteed valid codes
- **status**: empirical
- **provenance**: P.l.217-300; libs P.l.280-282

### PC-02 — Stage-1 screen: k-only via F2 rank

- **type**: pipeline/filter
- **context**: Screen each ansatz on lattices (6,6) and (12,6), computing only `k = 2lm - 2*rank_F2(H_X)`;
  discard ansatze with no k>0 code at both (~30% of mutants). ~2s. Both lattices have 3|l (possible
  divisibility-by-3 bias).
- **claim**: `k` from F2 rank is EXACT (zero stochasticity); used as deterministic ablation metric Σ_k too.
- **modality**: ExactProof (exact linear algebra over F2) — re-verifiable numerically
- **evidence**: P.l.247-248 (sec:cascade); exactness asserted P.l.706-707
- **dependencies**: ground-truth k formula; qldpc v1.0.1 (MISSING locally)
- **assumptions**: rank computed over F2
- **status**: checked
- **provenance**: P.l.246-248

### PC-03 — Stage-2 distance estimate: BP-OSD (in-loop, Campaigns 1-3)

- **type**: pipeline/estimator
- **context**: On 8 lattices {(12,6),(6,12),(12,12),(24,6),(15,12),(30,6),(16,9),(18,8)}, top-10 by k-diversity
  get BP-OSD 1000 OSD_0 trials (~30-60s); promising (FOM>=6) get +3 batches of 500. ldpc v2.2.0.
- **claim**: BP-OSD yields a stochastic UPPER bound `d_true <= d_reported`; reliable only as a ranking signal,
  NOT as ground-truth distance (see PC-12, TH-AXIOM dependency on overestimation).
- **modality**: StatisticalInference (Monte-Carlo upper bound)
- **evidence**: P.l.249-251, P.l.309-311 (sec:bposd_limits)
- **dependencies**: PC-12 (overestimation measurement), ldpc v2.2.0 (MISSING locally)
- **assumptions**: random logical-coset sampling; ldpc defaults (max_iter=n, no damping)
- **status**: approximate
- **provenance**: P.l.249-251, P.l.306-317

### PC-04 — Stage-3 MILP exact distance (CSS, Hamming weight)

- **type**: pipeline/verifier (exact)
- **context**: Per logical j: `min Σ x_i` s.t. `H_Z x ≡ 0 (mod 2)` [eq:milp_commute],
  `<x, Zbar_j> ≡ 1 (mod 2)` [eq:milp_anticommute], `x_i ∈ {0,1}` [eq:milp_binary]; objective [eq:milp_obj].
  mod-2 linearized via integer slack `Σ a_i x_i - 2s = b`. d = min(d_X, d_Z); for BB d_X=d_Z by involution.
  Solve 2k instances. HiGHS via `scipy.optimize.milp`. Timeouts 120-600s (3000s C4 top, 14400s C5 deep).
  In-loop for C4-5, post-hoc for C1-3.
- **claim**: Distance is EXACT iff all 2k logical MILP instances reach MIP gap = 0; otherwise the incumbent is
  a valid upper bound `d <= d_incumbent` with lower bound `d >= d_LB`.
- **modality**: NumericalSimulation (exact when MIP gap = 0; certified optimization)
- **evidence**: P.l.319-336 (sec:milp), S.l.659-674 (CSS formulation), eq labels VERBATIM
- **dependencies**: ground-truth H_X,H_Z; HiGHS/scipy (scipy 1.17.1 present locally); TH-CSS-COMMUTE
- **assumptions**: HiGHS gap=0 certificate trusted; lower bound d>=2 from column weights for d=2 codes
- **status**: checked (for gap=0 codes) / conditional (incumbent upper-bound codes)
- **provenance**: P.l.319-336; S.l.659-674; eq:milp_obj/commute/anticommute/binary S.l.663-666

### PC-05 — MILP exact distance (non-CSS PBB, symplectic weight) — Tier 2

- **type**: pipeline/verifier (exact)
- **context**: Per logical j of 2k: `min Σ w_i` s.t. `H (a|b)^T ≡ 0`, `<(a|b),Lbar_j>_symp ≡ 1`,
  `w_i>=a_i, w_i>=b_i, w_i<=a_i+b_i` (binary-OR convex hull), `a_i,b_i,w_i ∈ {0,1}`.
  H = symplectic-flipped row order `(s_Z|s_X)` (X-first vector convention). 3n binary vars; ~4x slower than CSS.
  Adaptive timeouts: 15s (n<=108), 30s (n<=216), 60s (n>216); deep up to 14400s.
- **claim**: Minimum symplectic weight = exact non-CSS distance when MIP gap=0; partial results are valid
  upper bounds. Deep MILP of 149 PBB entries -> 63 exact, 33 downward corrections (22% rate), largest d=24->16 at n=360.
- **modality**: NumericalSimulation (exact when gap=0)
- **evidence**: P.l.348-351 (Tier 2), S.l.676-691 (symplectic formulation), P.l.364, S.l.711
- **dependencies**: TH-PBB-COMMUTE; HiGHS/scipy; qldpc symplectic Gaussian elim (MISSING locally)
- **assumptions**: binary-OR encoding tight at integer points; gap=0 certificate trusted
- **status**: checked (gap=0) / conditional (incumbent)
- **provenance**: P.l.348-351; S.l.676-691, S.l.711

### PC-06 — Tier-1 exhaustive weight-w enumeration (non-CSS)

- **type**: pipeline/verifier (exact, small codes)
- **context**: Enumerate all Pauli operators up to weight w via syndrome lookup table (XOR lookups);
  if a weight-w nontrivial logical found, d=w exactly. Reach: d<=6 at n<=216; d<=4 at n>216 (~89GB at n=360).
- **claim**: For codes within reach, enumeration is EXACT (complete search of the weight band).
- **modality**: NumericalSimulation (exhaustive => exact within band)
- **evidence**: P.l.344-346 (Tier 1)
- **dependencies**: none beyond stabilizer matrix
- **assumptions**: memory budget bounds reachable n,w
- **status**: checked (within band) / [FUTURE] beyond memory bound at large n
- **provenance**: P.l.344-346

### PC-07 — Tier-3 BP-OSD with achievable-syndrome sampling (non-CSS)

- **type**: pipeline/estimator (non-CSS)
- **context**: H_eff = (H_check; L); set stabilizer syndrome 0, pick random logical coset λ, decode (0,λ).
  Naive random sampling hits ~0% success on many PBB codes (achievable subspace can be exponentially small;
  random vectors not in im(H)). Fix: compute per-channel achievable subspace (GF(2) null-space projection on
  channel-restricted stabilizer matrix) and sample only from it -> restored ~0% to ~100% decode success.
- **claim**: With per-channel achievable-subspace sampling, BP-OSD yields valid stochastic upper bounds on
  non-CSS distance; the per-channel achievable dimension = k within the 2k logical space was observed for
  [[144,12,12]] PBB (Z- and Y-channels) but NOT proven general.
- **modality**: StatisticalInference (upper bound); subspace-dimension claim is EmpiricalMeasurement
- **evidence**: P.l.353-360 (Tier 3, sec:noncss_pipeline)
- **dependencies**: PC-03 BP-OSD machinery; ldpc v2.2.0 (MISSING locally)
- **assumptions**: "achievable subspace = half" observed not proven [HOLE: prove or refute generality of dim-k achievable subspace per channel]
- **status**: approximate
- **provenance**: P.l.353-360 ("we have not proved this is general", P.l.359)

### PC-08 — Trust filter d/sqrt(n) (Campaigns 1-4)

- **type**: pipeline/filter (heuristic)
- **context**: `d/sqrt(n) <= 1.3` fully trusted; `>= 2.0` discarded; linear interpolation between.
  Operates on BP-OSD estimates. Campaign-5 bypasses it (uses verified distances; rejects d<=4).
- **claim**: Heuristic guard against low-d high-k codes dominating fitness; KNOWN-IMPERFECT — operates on the
  same unreliable BP-OSD estimates it should catch. Counterexample: [[360,40,2]] passed with d_BP/sqrt(n)=1.26
  despite true d/sqrt(n)=0.11.
- **modality**: EmpiricalMeasurement (with documented Counterexample)
- **evidence**: P.l.366-371 (sec:trust)
- **dependencies**: PC-03 (BP-OSD), PC-04 (MILP exposes the failure)
- **assumptions**: d_BP a usable proxy for d (violated for high-rate codes)
- **status**: approximate (refuted as a reliable filter; retained only as a soft heuristic)
- **provenance**: P.l.366-371 (counterexample P.l.370)

### PC-09 — BLISS dedup (colored Tanner-graph canonical labeling)

- **type**: pipeline/equivalence (permutation)
- **context**: Colored bipartite Tanner graph — qubits c0, X-checks c1, Z-checks c2 (CSS);
  non-CSS: per-stabilizer X-support + Z-support vertices with a tying edge (3 colors). python-igraph BLISS
  canonical form. CSS: 225 reps -> 97 distinct (2.3:1, up to 14:1 univariate); non-CSS: 720 -> 368 (1.96:1).
- **claim**: Two codes are permutation-equivalent IFF colored-Tanner-graph canonical forms are identical
  (sound AND complete for permutation equivalence under the coloring). 465 distinct total = 97 CSS + 368 PBB;
  this is a CONSERVATIVE upper bound — broader equivalences (LC, full Clifford) can only reduce the count.
- **modality**: SymbolicDerivation (canonical-form equality is exact for the stated equivalence)
- **evidence**: P.l.380-394 (sec:families)
- **dependencies**: python-igraph + BLISS (MISSING locally)
- **assumptions**: BLISS canonical form correct (GI quasi-poly worst case; efficient in practice here)
- **status**: checked (for permutation equivalence) / conditional (as upper bound on broader equivalence)
- **provenance**: P.l.380-394

### PC-10 — Tanner-graph decomposability (direct-sum detection)

- **type**: pipeline/structural
- **context**: Connectivity of combined Tanner graph (H_X + H_Z); disconnected => direct sum.
  Landmark: [[288,24,12]] (A=x^6+y+y^2, B=y^3+x^2+x^4, even x-exponents) decomposes into two cosets
  (even/odd x-index), each ~ gross code under x->x/2 and x<->y swap, so [[288,24,12]] ≅ [[144,12,12]] ⊕ [[144,12,12]].
- **claim**: If the Tanner graph disconnects, the code is a direct sum: a logical supported on multiple
  components restricts to a logical on each (stabilizers on other components act trivially). Decomposable
  [[288,24,12]] offers no EC advantage over two gross codes (p_L matches at every rate).
- **modality**: ExactProof (graph-connectivity argument; re-verifiable) + NumericalSimulation (p_L match)
- **evidence**: P.l.423-434 (x/y-swap codes paragraph)
- **dependencies**: PC-09 (BLISS confirms same direct sum at (24,6) and (12,12))
- **assumptions**: connectivity computed on combined H_X+H_Z
- **status**: checked
- **provenance**: P.l.426-434

### PC-11 — LC-CSS equivalence test for PBB (App E)

- **type**: pipeline/equivalence (local Clifford)
- **context**: Per-qubit single-qubit Clifford; 6 coset reps {I,S,H,HS,SH,HSH}. Group-CSS IFF
  `rank[X|Z] = rank X + rank Z` over GF(2) (Lemma 7.4 cross2025small, [AXIOM]). Three tests:
  (1) 36 uniform per-block assignments; (2) non-uniform {I,S} and {H,HS} via exact GF(2) affine system;
  (3) Hadamard 2-coloring (parity union-find) for non-uniform {I,H}, requires no Y support + bipartite constraint graph.
- **claim**: 11/368 PBB codes are CSS-equivalent under TESTED LC families (10 via non-uniform Hadamard,
  1 = [[36,4,6]] via uniform S on both blocks); 357 are CSS-INEQUIVALENT WITHIN TESTED FAMILIES.
  Residual gaps: non-uniform {SH,HSH} on block 1, and cross-class non-uniform patterns (NOT brute-forced).
- **modality**: SymbolicDerivation (GF(2) rank/affine + 2-coloring exact) conditional on Lemma 7.4 [AXIOM]
- **evidence**: P.l.185-194 (sec:pbb), P.l.1026-1087 (app:lc), Lemma 7.4 P.l.1036
- **dependencies**: TH-AXIOM-L74 (Lemma 7.4 cross2025small); BLISS-distinct catalog PC-09
- **assumptions**: coverage gaps (a),(b) unresolved [HOLE: decide LC-CSS for non-uniform {SH,HSH} / cross-class patterns]
- **status**: conditional (357-count holds only "within tested LC families"; explicit gaps documented)
- **provenance**: P.l.185-194, P.l.1026-1087

### PC-12 — Multi-decoder BP-OSD verification protocol (post-hoc, 150k trials)

- **type**: pipeline/verifier (statistical bound)
- **context**: 3 configs — OSD_0/sum-product BP, OSD-CS_10/sum-product BP, OSD-CS_10/minimum-sum BP — each
  10 batches x 5000 trials = 150k/code; verified bound = global min over 30 batches. Extended runs 1.5e6 trials.
- **claim**: Provides verified stochastic UPPER bound on d. 147/154 (95.5%) of C1-3 reps tightened (mean ~8.4 pts);
  OSD-CS_10/min-sum found global min for 100/154 (65%) vs OSD_0 49/154 (32%). Even so, large overestimates persist.
- **modality**: StatisticalInference (multi-decoder Monte-Carlo upper bound)
- **evidence**: P.l.306-317 (sec:bposd_limits), P.l.670-701 (sec:bposd_findings), S.l.111-211
- **dependencies**: ldpc v2.2.0 (MISSING locally); PC-04 (MILP ground truth for comparison)
- **assumptions**: ldpc library defaults; 30-batch global min as the reported bound
- **status**: approximate
- **provenance**: P.l.306-317, P.l.670-701

### PC-13 — Figure-of-merit ranking (FOM = k d^2 / n)

- **type**: pipeline/objective
- **context**: `FOM = k d^2 / n`, motivated by BPT bound `k d^2 = O(n)` (bravyi2010tradeoffs); gross code
  [[144,12,12]] has FOM=12. Used to rank/benchmark BB codes against each other; BPT applies to 2D-local codes.
- **claim**: FOM is the comparison benchmark; for 2D-local qLDPC it is bounded by a constant as n grows, but
  for general qLDPC it is not. Surface code FOM=1; gross code FOM=12.
- **modality**: DimensionalConsistency (definitional metric) on top of LiteratureGrounded BPT motivation
- **evidence**: P.l.198-203 (sec:fom)
- **dependencies**: PC-02 (k), PC-04/05/06 (d)
- **assumptions**: BPT bound (bravyi2010tradeoffs) cited, not re-derived
- **status**: checked (as a defined metric)
- **provenance**: P.l.198-203

---

## B. Theorems and core claims (5 typed entries)

### TH-01 — `thm:ab_d2` (A=B distance trap)

- **type**: theorem (paper-proven)
- **context**: App D. Every BB code with `A = B` and `k > 0` has `d = 2` exactly. Extends to PBB
  (lm weight-2 Z-operators (0|e_i+e_{i+lm}) in normalizer; d=2 whenever any is not a stabilizer, verified by MILP).
  Holds for ANY check weight >= 2.
- **claim**: A=B, k>0 => d=2 exactly. Proof: H_X rows (A_r|A_r) lie in diagonal subspace S; v_i=(e_i,e_i) ∈ ker(H_Z);
  is X-stab iff e_i ∈ rowspace(A); k>0 => rank(A)<lm => some e_i outside => weight-2 X-logical => d<=2 (sym. d_Z<=2);
  polynomials with >=2 terms force column weight >=2 => d>=2; hence d=2.
- **modality**: ExactProof (paper-proven) — TO BE RE-VERIFIED NUMERICALLY on catalog A=B codes
- **evidence**: P.l.956-980 (app:ab_trap, thm:ab_d2); PBB extension P.l.975-980; MILP confirmation P.l.196, P.l.332, S.l.698
- **dependencies**: TH-CSS-COMMUTE; PC-04 (MILP d=2 in <1s corroborates)
- **assumptions**: polynomial weight >= 2 (so column weight >= 2 for the d>=2 lower bound)
- **status**: checked (proof complete in paper; numerical re-verification target)
- **provenance**: P.l.959-980; label `thm:ab_d2` VERBATIM

### TH-02 — `lem:crt_k` (univariate / HGP encoding dimension)

- **type**: theorem (paper-proven)
- **context**: App C. A(y)=1+y+y^2, B(x)=A(x^c) with c=l/3, 3|l, 3|m. The BB code is a hypergraph product
  code encoding k = 8l/3 logical qubits (independent of m).
- **claim**: k = 8l/3. Proof: BB(A,B) ~ HGP(H_B, H_A^T); HGP dim k=k1 k2 + k1^T k2^T (tillich2014quantum);
  dim ker H = deg gcd(f, z^N-1) (macwilliams1977theory); (y-1)A=y^3-1 | y^m-1 => k_A=k_A^T=deg A=2;
  (x^c-1)B=x^l-1 => k_B=k_B^T=deg B=2c=2l/3; k = 2 k_B k_A^T = 2·(2l/3)·2 = 8l/3.
- **modality**: ExactProof (paper-proven) — RE-VERIFIED numerically by authors on 1680 combos lm<=250; re-verification target
- **evidence**: P.l.982-1024 (app:crt, lem:crt_k); 1680-combo verification P.l.421
- **dependencies**: TH-AXIOM-TZ (tillich2014quantum HGP dim formula); macwilliams1977theory cyclic-code identity (cited)
- **assumptions**: 3|l and 3|m; cited HGP dimension formula and cyclic kernel identity treated as given
- **status**: checked (proof complete; numerically verified for 1680 combos)
- **provenance**: P.l.985-1024; label `lem:crt_k` VERBATIM

### TH-03 — `css-commute` (CSS commutation condition)

- **type**: claim (algebraic identity)
- **context**: CSS condition for BB codes from commutativity of R.
- **claim**: `H_X H_Z^T = AB + BA = 0` over F2 (follows from commutativity of R).
- **modality**: ExactProof (immediate from ring commutativity) — re-verifiable
- **evidence**: P.l.166 (sec:bb)
- **dependencies**: ground-truth ring R
- **assumptions**: R commutative (F2[x,y]/(x^l-1,y^m-1))
- **status**: checked
- **provenance**: P.l.166

### TH-04 — `pbb-commute` (PBB commutation condition)

- **type**: claim (algebraic / computational)
- **context**: Non-CSS PBB rows commute condition. Unlike CSS, must be verified computationally per tuple
  (~10% of random weight-3 4-tuples at (6,6) satisfy it).
- **claim**: All PBB rows commute IFF `(A C^T + B D^T) mod 2` is symmetric over F2 (the only nontrivial
  commutativity condition; block-1/block-2 commutativity automatic from BB ring commutativity).
- **modality**: SymbolicDerivation (algebraic condition) with EmpiricalMeasurement of ~10% satisfaction rate
- **evidence**: P.l.180-181 (sec:pbb), S.l.690
- **dependencies**: TH-CSS-COMMUTE; ground-truth PBB H
- **assumptions**: per-tuple computational check required (no closed-form selection)
- **status**: checked (as a stated necessary-and-sufficient condition)
- **provenance**: P.l.180-181, S.l.690

### TH-AXIOM-TZ — tillich-zemor HGP distance (CITED, [AXIOM])

- **type**: imported postulate ([AXIOM])
- **context**: HGP distance formula and univariate-distance corollary; CITED, not reproduced.
- **claim**: HGP distance `d = min(d1, d2, d1^T, d2^T)` (tillich2014quantum); univariate BB codes (separated
  variables) all have d ∈ {2,4} — the rate-distance tradeoff envelope's high-k extreme.
- **modality**: LiteratureGrounded (cited result; treat as [AXIOM] — final univariate-distance claims remain
  conditional on it)
- **evidence**: P.l.408-411 (sec:families), P.l.553; HGP dim companion in TH-02
- **dependencies**: feeds TH-02 (lem:crt_k) and the d∈{2,4} catalog observation (MILP-confirmed case-by-case)
- **assumptions**: tillich2014quantum distance formula accepted without reproduction
- **status**: conditional ([AXIOM]; d∈{2,4} corroborated by MILP case-by-case but the formula itself is imported)
- **provenance**: P.l.408-411, P.l.553; cite tillich2014quantum

---

## C. Empirical / conjectural cross-cutting claims

### CL-01 — Rate-distance tradeoff (CONJECTURAL)

- **type**: claim (empirical pattern)
- **context**: Across all 5 campaigns, all structural families, all polynomial term counts, and the CSS/non-CSS
  boundary, a sharp k-vs-d tradeoff persists (Fig. pareto). Among weight-6, k>24 => d<=4; weight-8 reaches k=50 at d=8.
- **claim**: Whether the tradeoff is a STRUCTURAL constraint of the BB construction or an ARTIFACT of the
  (incomplete) search is OPEN; consistent with `d = O(sqrt(n))` (postema2025existence). No discovered
  indecomposable code exceeds the prior highest FOM at its own block length.
- **modality**: Conjectural (open question; observed over a finite searched catalog)
- **evidence**: P.l.533-560 (sec:tradeoff)
- **dependencies**: PC-04/05 (distances), PC-09 (distinctness), PC-13 (FOM)
- **assumptions**: search is incomplete; C5 excluded (12,12) and (15,12) [FUTURE: extend PBB to these lattices]
- **status**: conjectural
- **provenance**: P.l.549-560

### CL-02 — BP-OSD overestimation (EmpiricalMeasurement)

- **type**: finding (empirical measurement)
- **context**: MILP ground truth vs BP-OSD on high-rate codes.
- **claim**: BP-OSD systematically and severely overestimates d for high-rate codes (k/n > 0.1): [[360,40,2]]
  reported d_BP<=24 @150k, <=6 @1.5M, true d=2 (MILP) — a 12x overestimate no feasible trial budget resolves.
  [[288,32,4]] (MILP d=4): OSD_0 median 39, OSD-CS_10/min-sum median 26 (4.5-11x). A=B [[144,32,2]]: 29/30
  batches @150k found NO weight-2 logical despite 16 independent ones. Gross code [[144,12,12]]: d=12 in all
  30 batches, zero variance. Implication: distance claims for k/n>0.1 from <~1e5 trials / single decoder are untrustworthy.
- **modality**: EmpiricalMeasurement (measured gaps against MILP exact)
- **evidence**: P.l.670-701 (sec:bposd_findings), P.l.211 (sec:ab_trap), S.l.111-211
- **dependencies**: PC-04 (MILP ground truth), PC-12 (multi-decoder protocol), TH-01 (A=B 16 logicals)
- **assumptions**: ldpc defaults; specific configs/budgets as stated
- **status**: empirical
- **provenance**: P.l.670-701

### CL-03 — Catalog distance status convention (NumericalSimulation / incumbent)

- **type**: convention (admission gate for catalog rows)
- **context**: How catalog d-values are labeled.
- **claim**: A code's distance is "exact" (E) ONLY when all 2k logical MILP instances reach MIP gap=0
  (NumericalSimulation, MILP-exact); otherwise reported as an upper-bound "incumbent" (I), `d <= d_incumbent`,
  with `d >= d_LB`. Non-CSS also: "trusted" = valid upper bound from >=2 independent methods. Catalog totals:
  CSS 97 distinct; PBB 368 = 78 (n,k,d) sets, 251 exact rows + 117 upper-bound (110 TRUSTED + 7 PARTIAL with d/sqrt(n)>=1.5).
  Landmarks: [[288,16,12]] E (highest-k indecomposable wt6 @d=12), [[288,24,12]] E but decomposable,
  [[288,50,8]] E wt8 cross-factored, [[144,54,<=4]], [[360,16,<=14]] I, PBB [[144,12,12]] FOM=12,
  PBB [[360,12,<=24]] FOM<=19.2 (highest PBB, upper bound).
- **modality**: NumericalSimulation (E rows) / conditional upper-bound (I rows)
- **evidence**: P.l.319-336 (sec:milp), P.l.362-364, P.l.454, P.l.580-594, S.l.693-711
- **dependencies**: PC-04, PC-05, PC-06, PC-09
- **assumptions**: gap=0 certificate trusted; incumbent rows remain conditional [FUTURE: close I -> E]
- **status**: checked (E rows) / conditional (I rows)
- **provenance**: P.l.319-336, P.l.454, S.l.693-711

---

## Open obligations (markers summary)

- [HOLE] PC-07: prove or refute that the per-channel achievable subspace has dimension k (half of 2k) in
  general for non-CSS codes; currently observed only for [[144,12,12]] PBB (Z- and Y-channels). (P.l.359)
- [HOLE] PC-11: decide LC-CSS-equivalence for the uncovered Clifford classes — non-uniform {SH,HSH} on
  block 1, and cross-class non-uniform patterns; the "357 CSS-inequivalent" count is conditional on these gaps. (P.l.1069-1076)
- [AXIOM] TH-AXIOM-TZ: tillich2014quantum HGP distance formula imported, not reproduced; downstream
  univariate-distance and lem:crt_k results remain conditional on it. (P.l.408-411)
- [AXIOM] PC-11 Lemma 7.4 (cross2025small): group-CSS rank condition imported; LC-CSS results conditional on it. (P.l.1036)
- [FUTURE] CL-01: extend PBB evolution to (12,12)/(15,12) to test whether non-CSS escapes the CSS envelope. (P.l.559)
- [FUTURE] CL-03: 117 PBB upper-bound rows (and CSS incumbents like [[360,16,<=14]]) remain I; deep MILP / SAT
  / Brouwer-Zimmermann could close to E. (P.l.331, P.l.454)
- [BLOCKING for local numerical re-verification] qldpc, ldpc, igraph, openevolve, litellm are MISSING in the
  local env (numpy/scipy/sympy present). Re-verifying PC-04/PC-05 (MILP exact) is feasible with scipy.optimize.milp;
  PC-02 (F2 rank) and TH-01/TH-02/TH-03/TH-04 algebra are feasible with numpy/sympy. PC-03/PC-07/PC-12 (BP-OSD)
  and PC-09 (BLISS) require installing ldpc and python-igraph. Owner: pipeline-1 elaboration. Unblocks: numerical
  re-verification of theorems and catalog distances.
