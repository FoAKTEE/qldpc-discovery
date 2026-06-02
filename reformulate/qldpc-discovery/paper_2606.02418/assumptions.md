# Modeling Assumptions and Regimes — arXiv:2606.02418

Source: Cruz-Benito, Cross, Kremer, Faro, "Evolutionary Discovery of Bivariate
Bicycle Codes with LLM-Guided Search" (IBM Research; PRX Quantum).
tex: `ref-paper/arxiv-2606.02418/src/{paper.tex, supplemental.tex}`.

Scope of this file: enumerated modeling assumptions, search-scope restrictions,
and decoder/benchmark caveats that condition every parameter claim in the paper.
Each is a TYPED entry: context, claim, evidence modality, dependencies, status.
Default modality `LiteratureGrounded` unless the paper supplies a proof/derivation.
`[AXIOM]` = explicit modeling postulate the results stay conditional on;
`[HOLE]` = unresolved obligation with stated expected type;
`[FUTURE]`/`[BLOCKING]` per `_common/markers.md`.

All `[AXIOM]` entries are *scoping/modeling choices the authors made*, not
imported external theorems (those live in `theorems.md` / `dependencies`). The
final catalog parameters are conditional on this entire set.

---

## A1. Trinomial restriction (Campaigns 1-3) vs 4-6-term polynomials (Campaign 4)

- **id**: `asm:trinomial_scope`
- **context**: Ring `R = F2[x,y]/(x^l-1, y^m-1)`; BB code from `A,B in R`,
  `H_X=(A|B)`, `H_Z=(B^T|A^T)`; stabilizer weight = (#terms in A) + (#terms in B).
- **claim**: Campaigns 1-3 search *only* trinomial (weight-3) `A,B`, yielding
  weight-6 stabilizers and matching the original BB definition of `bravyi2024high`.
  Campaign 4 relaxes this to 4-6-term polynomials (weight-8 to weight-12
  stabilizers, stabilizer weight = sum of terms in A and B; "e.g., 3+3 = weight-6,
  4+4 = weight-8, 5+5 = weight-10"), including mixed monomials `x^a y^b` (`a,b>0`).
- **evidence**: `LiteratureGrounded` (definitional choice). paper.tex l.158, l.165,
  l.168; supplemental.tex l.61-62.
- **dependencies**: `bravyi2024high` (BB definition) [AXIOM, cited]; the four
  algebraic families (UV/HGP, XY-swap, MX mixed-monomial, PBB).
- **assumptions**: "the landscape of code parameters depends on check weight, so we
  separate claims accordingly" (paper.tex l.165) — i.e. weight-6 and weight-8/+
  claims must NOT be conflated.
- **status**: [AXIOM] — search-scope restriction. All Campaign 1-3 "weight-6"
  records are conditional on the trinomial restriction; weight-2 binomial
  `1+y` (toric code, linearly growing d) lies *outside* the C1-3 space
  (paper.tex l.412).

## A2. PBB non-CSS ansatz scope (Campaign 5) — perturbation restricted to weight-3 bases

- **id**: `asm:pbb_scope`
- **context**: PBB 4-tuple `(A,B,C,D) in R`; `H = [[A,B,C,D],[0,0,B^T,A^T]]`;
  block-1 mixed X(A,B)+Z(C,D), block-2 pure Z. Reduces to CSS when `C=D=0`.
- **claim**: All 368 catalog PBB codes use **trinomial bases** (`|A|=|B|=3`); the
  non-CSS character comes *entirely* from `C,D`. Optimal perturbation size is
  `|C|=|D|=2` (56% of codes, highest avg FOM=6.4); heavy perturbations
  `|C|+|D|>=6` cap distance at `d<=8`.
- **evidence**: `EmpiricalMeasurement` over the catalog. paper.tex l.173-184,
  l.484-486.
- **dependencies**: `pbb-commute` (rows commute iff `A C^T + B D^T` symmetric over
  F2; "must be verified computationally for each tuple", paper.tex l.180);
  `asm:trinomial_scope`.
- **assumptions**: ~10% of random weight-3 4-tuples at lattice (6,6) satisfy the
  commutativity constraint (paper.tex l.181) — empirical admissibility rate, not a
  guarantee any output is a valid/good code.
- **status**: [AXIOM] — ansatz-scope restriction. PBB records conditional on
  trinomial-base + small-perturbation regime.

## A3. 3|l screening bias (Stage-1 cascade)

- **id**: `asm:div3_screen_bias`
- **context**: Cascade Stage 1 (~2s) screens each ansatz on two small lattices
  computing only `k` via F2 rank; ansatze with no `k>0` at both are discarded
  (~30% of mutants).
- **claim**: The two Stage-1 screening lattices are `(6,6)` and `(12,6)`, **both
  with `3 | l`**, "which may bias the search toward divisibility-by-3 structures;
  the failure of all evolved ansatze at `(16,9)` and `(18,8)` ... may partly
  reflect this."
- **evidence**: `LiteratureGrounded` + `StatisticalInference` (authors' own
  hypothesis about a self-inflicted bias, corroborated by ablation Sec VI.F where
  the exponent-tuple GA *does* find genuine d>=3 codes at (16,9),(18,8) while all
  LLM-evolved ansatze fail there). paper.tex l.247-248, l.713, l.743.
- **dependencies**: `lem:crt_k` (the HGP `k=8l/3` family requires `3|l`, `3|m` —
  the search may have over-concentrated on this divisibility regime).
- **status**: [AXIOM] — a screening-induced sampling bias the authors flag as a
  Limitation (paper.tex l.743: "CSS campaigns required `3 | l` at Stage 1,
  missing lattices `(16,9)` and `(18,8)`"). Coverage of non-`3|l` factorizations
  is [HOLE]: expected type = "do evolved ansatze yield k>0, d>=6 codes at lattices
  with 3 not dividing l?" — unresolved; partly probed only by the GA ablation arm.

## A4. Lattices searched (Stage-2 and Campaign-5 lattice sets)

- **id**: `asm:lattice_set`
- **context**: Surviving ansatze evaluated on a fixed lattice list per campaign.
- **claim**:
  - CSS Stage 2 (Campaigns 1-4): 8 lattices spanning `n in {144,288,360}` —
    `(12,6),(6,12),(12,12),(24,6),(15,12),(30,6),(16,9),(18,8)`.
  - Campaign 5 (PBB): 7 lattices `n=36..360`, **all with `m<=6`** —
    `(3,6),(6,3)` @ n=36, `(6,6)` @ 72, `(9,6)` @ 108, `(12,6)` @ 144,
    `(15,6)` @ 180, `(30,6)` @ 360.
- **evidence**: `LiteratureGrounded`. paper.tex l.249, l.252;
  supplemental.tex l.76.
- **dependencies**: `asm:milp_runtime_m6` (the `m<=6` restriction is forced by MILP
  symplectic runtime, see A8).
- **status**: [AXIOM] — fixed evaluation lattice set. Any lattice off these lists is
  unsearched; "Different seeds, larger populations, or alternative representations
  could access unexplored regions" (paper.tex l.744).

## A5. n <= 360 scope ceiling

- **id**: `asm:n_le_360`
- **context**: All discovered codes are reported at block lengths `n = 2*l*m`.
- **claim**: The entire catalog (465 distinct = 97 CSS + 368 PBB) is at `n <= 360`.
  BB codes are positioned as attractive for near-term hardware "at practical block
  lengths (`n <~ 1000`)", but the search itself does not exceed `n=360`.
- **evidence**: `LiteratureGrounded`. paper.tex l.65 (`n<~1000` framing), l.76,
  l.98, l.757.
- **dependencies**: `asm:milp_runtime_m6`; scaling PBB beyond n=360 is named
  [FUTURE] (paper.tex l.750: "scaling PBB evolution to `n>360` with improved MILP
  solvers").
- **status**: [AXIOM] — scope ceiling. No claim is made about `n>360`; asymptotic
  rate-distance behavior is out of scope.

## A6. Weight-6 vs weight-8 regime separation (rate-distance envelope)

- **id**: `asm:weight_regime`
- **context**: The empirical rate-distance tradeoff is the paper's central
  structural finding; it is asserted *per check-weight regime*.
- **claim**: Among **weight-6** codes, `k>24 => d<=4`, and indecomposable `d=12`
  codes are limited to `k<=16`. **Weight-8** mixed-monomial codes access new
  `(k,d)` points (e.g. `k=50` at `d=8`, the `[[288,50,8]]`) "but do not escape
  this envelope." The tradeoff "persists across polynomial term counts and check
  weights within the CSS family."
- **evidence**: `EmpiricalMeasurement` (MILP distances over the searched catalog),
  explicitly NOT a proof: "though we do not prove this is a structural constraint
  of the construction" (paper.tex l.78). paper.tex l.80, l.102, l.545, l.555-557,
  l.761-763.
- **dependencies**: MILP exactness (Stage-3) for the d-values underpinning the
  envelope; `thm:ab_d2` (the `A=B` `d=2` trap is the one proven structural fact);
  decomposability check (the `[[288,24,12]]` `k=24` endpoint is a direct sum of two
  gross codes, not indecomposable — paper.tex l.80, l.622).
- **status**: [AXIOM]/empirical regularity, NOT a theorem. The envelope claim is
  conditional on (i) the searched catalog only and (ii) the weight-6/weight-8
  regime separation. Whether *any* construction over the same ring escapes it is
  [HOLE] (open question, paper.tex l.87, l.559, l.763): expected type = "exhibit a
  (P)BB code over R with FOM exceeding the weight-6 envelope at its block length,
  or prove none exists." Weight-8 carries a separate hardware caveat (A9).

## A7. FOM = k d^2 / n as benchmark; BPT bound is geometric-2D-local-only

- **id**: `asm:fom_bpt`
- **context**: Figure of merit used to rank/compare all codes.
- **claim**: `FOM = k d^2 / n`, "motivated by the Bravyi-Poulin-Terhal (BPT) bound
  `kd^2 = O(n)`" and standard in the BB literature. **Caveat (verbatim,
  paper.tex l.202)**: "The BPT bound applies to geometrically 2D-local stabilizer
  codes. Therefore, for qLDPC codes that are 2D-local, the FOM is bounded above by a
  constant as `n` increases, but for general qLDPC codes this is not the case. For
  example, the rotated surface code has FOM = 1 whereas the gross code has FOM = 12.
  We use the FOM as a benchmark for comparing BB codes against each other."
- **evidence**: `LiteratureGrounded`. paper.tex l.201-203;
  `bravyi2010tradeoffs` (BPT). Gross code `[[144,12,12]]` => FOM = 12.
- **dependencies**: `bravyi2010tradeoffs` [AXIOM, cited]. The "highest PBB FOM" and
  "matches gross-code FOM" claims all reduce to this metric.
- **assumptions**: BB codes are generally NOT geometrically 2D-local, so a constant
  FOM ceiling does NOT apply to them; FOM is used only as a *relative* benchmark
  among BB codes, never as an absolute physical bound.
- **status**: [AXIOM] — benchmark definition + its non-applicability regime. Every
  "FOM=12.0 / FOM<=19.2" record is a benchmark comparison, not a bound-saturation
  claim. Note many high-FOM values are *upper bounds* (`<=`) from MILP-incumbent or
  trusted-BP-OSD distances, not exact (paper.tex l.491, Table tab:useful note
  l.592: the `[[360,12,<=24]]` FOM tie "is a tie of upper bounds, not a record").

## A8. MILP symplectic-runtime restriction forces m <= 6 for PBB (Campaign 5)

- **id**: `asm:milp_runtime_m6`
- **context**: Stage-3 exact distance via MILP (HiGHS through scipy.optimize.milp).
  Non-CSS symplectic formulation has 3n binary vars, ~4x slower per logical than
  the CSS formulation.
- **claim**: "The symplectic formulation is ~4x slower per logical than the CSS
  formulation, making the `(12,12)` and `(15,12)` lattices (which produced the
  highest-FOM CSS codes) impractical." Campaign 5 was therefore confined to the
  `m<=6` lattice set, **excluding** the large-m lattices where the best CSS codes
  live.
- **evidence**: `LiteratureGrounded` (runtime-budget engineering constraint).
  paper.tex l.277, l.559; supplemental.tex l.579.
- **dependencies**: `asm:lattice_set` (A4); the MILP symplectic formulation
  (3n binary vars, `w_i = a_i OR b_i`, row-flip `(s_Z|s_X)`).
- **status**: [AXIOM] — a computational-budget restriction that directly bounds the
  conclusions. "Whether non-CSS constructions over the same polynomial ring can
  escape the CSS rate-distance envelope remains open" (paper.tex l.87) is partly
  *unfalsified because of this exclusion*: [HOLE] — expected type = "extend PBB
  evolution to `(12,12)`/`(15,12)` and measure whether FOM exceeds the CSS
  envelope." Named [FUTURE] at paper.tex l.559.

## A9. Weight-8 hardware-cost caveat (FOM ignores circuit depth)

- **id**: `asm:weight8_depth`
- **context**: FOM (A7) is a purely combinatorial metric; it does not price in
  syndrome-extraction circuit depth.
- **claim**: All trinomial (weight-6) BB codes have degree-6 qubit connectivity
  (Konig: 6 CNOT rounds per check type; Bravyi depth-7 interleaved). Campaign-4
  weight-8 (4-term) codes require degree-8 connectivity (8 CNOT rounds, ~33% more
  depth per cycle) — "a different hardware-complexity regime." "Whether the FOM
  advantage of weight-8 codes compensates for the increased circuit depth is
  hardware-dependent."
- **evidence**: `LiteratureGrounded`. paper.tex l.736, l.739;
  supplemental.tex l.543-546.
- **dependencies**: `asm:weight_regime` (A6); `asm:fom_bpt` (A7).
- **status**: [AXIOM] — the FOM benchmark deliberately omits circuit cost.
  Weight-8 FOM gains (e.g. Symons `[[144,14,14]]` FOM=19.1, 1.6x the weight-6 FOM)
  are conditional on accepting deeper circuits; a full circuit-level comparison is
  [FUTURE] (supplemental.tex l.546).

## A10. Code-capacity decoder mismatch — iid X/Z BP-OSD prior on depolarizing channel

- **id**: `asm:depol_decoder_mismatch`
- **context**: Code-capacity simulations (Sec VI.D) use BP-OSD (ldpc lib;
  OSD-CS order 7, 20 BP iterations; 100,000 shots/point). Two channels:
  (i) X-only bit-flip at rate p, decoded on `H_z` with iid prior marginal rate p;
  (ii) depolarizing (each qubit X/Y/Z at p/3), decoded on symplectic
  `[H_z | H_x]` with iid bit-flip priors at marginal rate `2p/3` on each of `2n`
  columns.
- **claim** (verbatim core, footnote `fn:depolarizing-decoder`, paper.tex l.635):
  "For the depolarizing channel this iid prior is mismatched: under depolarizing
  noise `P(e_x=1, e_z=1) = p/3` (induced by Y errors) versus the iid prediction
  `(2p/3)^2`, so BP-OSD with iid bit priors does not model the X/Z correlation.
  The depolarizing-channel results ... are therefore values attainable under this
  specific (sub-optimal) decoder configuration — a lower bound on the depolarizing
  threshold under an optimal correlated decoder (e.g. quaternary BP over GF(4)) —
  not the optimal depolarizing threshold itself. CSS-vs.-PBB comparisons under
  depolarizing noise are likewise decoder-dependent."
- **evidence**: `SymbolicDerivation` of the mismatch (`p/3` vs `(2p/3)^2`) +
  `NumericalSimulation` for the reported LERs. paper.tex l.635 (footnote), l.639,
  l.665, l.767; supplemental.tex l.322, l.326-328, l.478-481.
- **dependencies**: BP-OSD as upper-bound decoder (`roffe2020decoding`,
  `panteleev2021degenerate`); the X-only vs depolarizing LER tables
  (`tab:threshold_css`, `tab:threshold_noncss`).
- **assumptions**: ldpc-library defaults elsewhere (max_iter = n BP iters, no
  damping, depolarizing error-rate placeholder 1e-3, paper.tex l.316) for the
  distance-estimation path — distinct from the capacity-sim decoder config above.
- **status**: [AXIOM] — decoder-mismatch caveat binding on ALL depolarizing-channel
  results. Specifically: the CSS-vs-PBB `[[144,12,12]]` parity under depolarizing
  noise (9.4% vs 9.3% LER at p=8%) is **decoder-dependent** and "a
  correlation-aware decoder could change this comparison" (paper.tex l.665). All
  depolarizing LERs are a *lower bound* on the optimal correlated-decoder threshold,
  not the optimal threshold. [HOLE]: expected type = "re-run under GF(4)/quaternary
  BP and report whether the CSS/PBB depolarizing comparison flips."

## A11. LC-CSS-equivalence coverage gaps (App E, gaps (a)-(b))

- **id**: `asm:lc_coverage_gaps`
- **context**: App E (`app:lc`) decides which PBB codes are local-Clifford-
  equivalent to CSS, replacing the infeasible `6^n` Clifford enumeration with
  polynomial-time tests over three structured families: Hadamard 2-coloring
  (non-uniform `{I,H}`), affine GF(2) systems (non-uniform `{I,S}` and `{H,HS}`),
  plus the 36 uniform per-block assignments. Result: 11/368 CSS-equivalent
  (10 Hadamard, 1 uniform-S `[[36,4,6]]`), 357 CSS-inequivalent.
- **claim**: Two classes of LC patterns lie **outside** the tested coverage
  (paper.tex l.1071-1073, verbatim):
  - **(a)** "Non-uniform patterns within `{SH, HSH}` on block 1." (On block 2,
    whose stabilizer rows have zero X-part, SH and HSH act identically on pure-Z
    input, so block-2 non-uniformity here collapses to a uniform choice already
    handled by Step 1.)
  - **(b)** "Non-uniform patterns whose per-qubit Cliffords are not all drawn from
    a single one of the three covered families `{I,S}`, `{H,HS}`, or `{I,H}` —
    e.g., S on some qubits and H on others, or any pattern using SH or HSH
    alongside other Cliffords."
- **evidence**: `LiteratureGrounded` (App E construction + `cross2025small`
  Lemma 7.4 / Sec 7.2). paper.tex l.1037, l.1069-1076, l.1083.
- **dependencies**: `cross2025small` Lemma 7.4 (group-CSS iff
  `rank[X|Z]=rankX+rankZ`) [AXIOM, cited]; `khesin2026mirror` (mirror/2-coloring)
  [AXIOM, cited].
- **assumptions**: "We do not have a GF(2) reduction analogous to Step 2 for either
  gap and have not exhaustively brute-forced them" (paper.tex l.1075). Eliminating
  the gaps needs the full `6^n` enumeration, "computationally infeasible" at
  `n = 2*l*m >= 36, up to 360" (paper.tex l.1076).
- **status**: [AXIOM] + [HOLE]. Because of gaps (a)-(b) the 357 codes are described
  as "CSS-inequivalent within the tested local-Clifford families" NOT "genuinely
  non-CSS" (paper.tex l.1083). [HOLE]: expected type = "rule out (or exhibit) CSS
  reductions of any of the 357 via non-uniform `{SH,HSH}` on block 1, or via
  cross-class non-uniform patterns." Note: Cross-Vandeth Sec 7.2 itself remarks "no
  fast test for LC-CSS-equivalence is currently known" (paper.tex l.1037), so this
  gap is partly inherited from the state of the art. GF(4)-linearity partition of
  the 357 is named as a complementary classification not pursued [FUTURE]
  (paper.tex l.1086).

---

## Cross-cutting status note

- The two *proven* structural facts (`thm:ab_d2`: all `A=B` codes have `d=2`;
  `lem:crt_k`: `k=8l/3` HGP family) are theorems, recorded in `theorems.md`, and
  are NOT assumptions — they are exceptions to the otherwise-empirical envelope of
  A6.
- Distance values feeding A6/A7: MILP-exact only when HiGHS reports MIP gap = 0
  (supplemental.tex l.673); otherwise an incumbent **upper bound** (`d<=`).
  BP-OSD distances are stochastic UPPER bounds and overestimate up to 12x for
  `k/n>0.1` (paper.tex l.90); the `d/sqrt(n)` trust filter (<=1.3 trusted,
  >=2.0 discarded) is the in-loop guard. Treat every `<=` row as conditional.
- Every catalog parameter claim is conditional on the conjunction A1-A11.
