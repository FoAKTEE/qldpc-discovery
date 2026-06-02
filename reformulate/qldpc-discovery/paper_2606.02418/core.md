# core.md — Typed Core IR for arXiv:2606.02418

Paper: "Evolutionary Discovery of Bivariate Bicycle Codes with LLM-Guided Search"
(Cruz-Benito, Cross, Kremer, Faro; IBM Research; PRX Quantum).
Source tex: `ref-paper/arxiv-2606.02418/src/paper.tex` (1091 lines),
`.../supplemental.tex` (715 lines).

This file is the typed core intermediate representation. Every entry follows the
Accepted Object Schema of `_common/agentic_lean_contract.md`:
`id · name · type · context · claim · modality · evidence · dependencies · assumptions · status · provenance`.
Status vocabulary (markers.md): `[SOLID] [PRELIMINARY] [HYPOTHESIS]` and gap markers
`[AXIOM] [HOLE] [FUTURE] [BLOCKING]`. Tex labels are preserved VERBATIM.

DISCIPLINE NOTE: claims default to modality `LiteratureGrounded` (imported from the
paper, not re-derived here). Claims with an in-paper proof carry `ExactProof`. Claims
resting on cited-but-not-reproduced external results carry the `[AXIOM]` marker. No
result is invented; nothing in the paper's catalog tables is promoted to exact beyond
what the paper itself certifies.

---

## Sigma — imported declarations

| id | name | type | claim | modality | status | provenance |
|----|------|------|-------|----------|--------|------------|
| sig.paper | paper:2606.02418 | Paper | Primary source; BB/PBB evolutionary discovery, 465 distinct codes at n<=360 (97 CSS + 368 PBB). | LiteratureGrounded | [SOLID] | paper.tex l.34-56 (title/abstract) |
| sig.code | code:qcode-discovery | CodeRepo | github.com/qiskit-community/qcode-discovery, cited `cruzbenito2026qcode` as the data/code release. Repo is EMPTY (README only) as of 2026-06-02 sha 4a9520e — no artifact to import. | LiteratureGrounded | [BLOCKING] | paper.tex l.386 (`cruzbenito2026qcode`). Unblocks when repo populated; owner = upstream authors. Cannot reproduce code-level claims until then. |
| sig.bravyi | paper:2308.07915 | Paper | bravyi2024high: BB code definition, gross code [[144,12,12]], MILP distance baseline, per-channel BP-OSD bounding. MANDATORY dependency. | LiteratureGrounded | [AXIOM] | paper.tex l.65-66, l.158, l.661 — cited, not reproduced; escalation candidate |
| sig.scipy_milp | lib:scipy.optimize.milp | Library | HiGHS MILP solver wrapper; returns proven-optimal (MIP gap=0) or incumbent + bound. scipy 1.17.1 local. | LiteratureGrounded | [SOLID] | supplemental.tex l.672 |
| sig.numpy | lib:numpy | Library | F2 linear algebra primitive (rank, kernel) substrate for k-computation and GF(2) systems. numpy 1.26.4 local. | LiteratureGrounded | [SOLID] | paper.tex l.247 (Stage-1 F2 rank); env |
| sig.tillich | paper:tillich2014quantum | Paper | HGP dimension formula k=k1k2+k1^T k2^T and HGP distance d=min(d1,d2,d1^T,d2^T). | LiteratureGrounded | [AXIOM] | paper.tex l.409, l.420, supplemental.tex l.1015 — cited, not reproduced |
| sig.cross2025 | paper:cross2025small | Paper | Lemma 7.4 (group-CSS rank condition) + 6-coset Clifford reduction. | LiteratureGrounded | [AXIOM] | paper.tex l.189, l.1036, l.1040 |
| sig.macw | paper:macwilliams1977theory | Paper | Cyclic-code identity dim ker H = deg gcd(f, z^N - 1). | LiteratureGrounded | [AXIOM] | supplemental.tex l.1015 |
| sig.ldpc | lib:ldpc(v2.2.0) | Library | BP-OSD decoder; stochastic UPPER bounds only. MISSING locally. | LiteratureGrounded | [AXIOM] | paper.tex l.280, l.309 |
| sig.qldpc | lib:qldpc(v1.0.1) | Library | Code construction; symplectic Gaussian elimination for logical reps. MISSING locally. | LiteratureGrounded | [AXIOM] | paper.tex l.280, supplemental.tex l.679 |
| sig.bliss | lib:python-igraph+BLISS | Library | Colored-Tanner-graph canonical labeling for permutation-equivalence dedup. MISSING locally. | LiteratureGrounded | [AXIOM] | paper.tex l.280, l.381 |
| sig.openevolve | lib:openevolve | Library | MAP-Elites LLM-guided program synthesis (FunSearch lineage). MISSING locally. | LiteratureGrounded | [AXIOM] | paper.tex l.74, l.220 |

---

## Gamma — active context (symbols, ring, regime)

| id | name | type | declaration | status | provenance |
|----|------|------|-------------|--------|------------|
| ctx.ring | R | Ring | R = F2[x,y]/(x^l - 1, y^m - 1); commutative quotient ring over F2. | [SOLID] | paper.tex l.158 |
| ctx.lattice | (l,m) | LatticeParam | Cyclic lattice dimensions; l,m positive integers. n = 2*l*m physical qubits. | [SOLID] | paper.tex l.158, l.167 |
| ctx.poly | A,B,C,D | RingElement | Polynomials in R. BB: A,B trinomials (weight-3 => weight-6 stabilizers). C4: 4-6 term (weight-8..12). PBB adds C,D. | [SOLID] | paper.tex l.158, l.165, l.168, l.174 |
| ctx.circ | circulant | Map | A,B realize as (l*m)x(l*m) circulant matrices; A^T = involution x->x^-1, y->y^-1. | [SOLID] | paper.tex l.164 |
| ctx.field | F2 | Field | Binary field; all linear algebra (rank, kernel, commutation) is mod 2. | [SOLID] | paper.tex l.166-167 |
| ctx.regime | n<=360 | Regime | Block-length regime of the search/catalog; n in {36,...,360}. MILP tractable here. | [SOLID] | paper.tex l.52, supplemental.tex l.344 |
| ctx.fom | FOM | DerivedQuantity | FOM = k*d^2/n; BPT-motivated benchmark. Gross code FOM=12. | [SOLID] | paper.tex l.200-202 |

---

## Model structures

### M1 — CSS bivariate-bicycle (BB) code
- id: `mdl.css`
- type: ModelStructure (StabilizerCode, CSS)
- context: `ctx.ring`, `ctx.lattice`, `ctx.poly` (A,B trinomials), `ctx.circ`, `ctx.field`
- claim: H_X = (A | B), H_Z = (B^T | A^T), each block (l*m)x(l*m) circulant.
  Parameters [[n,k,d]] with n = 2*l*m, k = 2*l*m - 2*rank_{F2}(H_X), d = min weight of a
  nontrivial logical operator.
- modality: LiteratureGrounded
- evidence: paper.tex l.160-167 (eq H_X/H_Z, parameter formulas)
- dependencies: `ctx.ring`, `ctx.circ`, `sig.bravyi`
- assumptions: trinomial restriction for weight-6 (C1-C3); C4 relaxes to 4-6 terms.
- status: [SOLID]

### M2 — Perturbed bivariate-bicycle (PBB) non-CSS code
- id: `mdl.pbb`
- type: ModelStructure (StabilizerCode, non-CSS)
- context: `ctx.ring`, `ctx.lattice`, `ctx.poly` (A,B,C,D), `ctx.field`
- claim: 4-tuple (A,B,C,D) in R; stabilizer matrix
  H = [[A, B, C, D], [0, 0, B^T, A^T]]. Block-1 mixed (X-support A,B; Z-support C,D);
  block-2 pure-Z. Symplectic (X | Z): first l*m cols X-support, second l*m cols Z-support.
  Reduces to CSS BB when C = D = 0.
- modality: LiteratureGrounded
- evidence: paper.tex l.174-183 (eq H, block description)
- dependencies: `mdl.css`, `ctx.ring`
- assumptions: validity of resulting code not guaranteed a priori; commutativity must be
  verified per tuple (see `clm.pbb_commute`).
- status: [SOLID]

### M3 — Colored Tanner graph (permutation-equivalence object)
- id: `mdl.tanner`
- type: ModelStructure (Graph)
- context: a fixed BB or PBB code
- claim: colored bipartite graph. CSS: qubit vertices (color 0), X-check (color 1),
  Z-check (color 2), edges check->supported qubits. Non-CSS: per-stabilizer X-support
  and Z-support vertices (3 colors total: qubits, stab-X-supports, stab-Z-supports), with
  a tying edge between each stabilizer's X- and Z-support vertices forbidding independent
  permutation. Two codes are permutation-equivalent iff BLISS canonical forms coincide
  (sound and complete for permutation equivalence under the respective coloring).
  Decomposability: connectivity of (H_X + H_Z) Tanner graph; disconnected => direct sum.
- modality: LiteratureGrounded
- evidence: paper.tex l.381-388 (CSS coloring), l.386 (non-CSS coloring), l.426-427 (decomposability)
- dependencies: `sig.bliss`, `mdl.css`, `mdl.pbb`
- assumptions: BLISS canonical form exact in practice for these structured graphs (GI is
  quasi-polynomial in worst case).
- status: [SOLID]

### M4 — MAP-Elites archive (evolutionary search state)
- id: `mdl.mapelites`
- type: ModelStructure (SearchArchive)
- context: OpenEvolve evolutionary loop
- claim: evolutionary target is a generator ANSATZ G(l,m) -> {(A_i,B_i)} (or 4-tuples for
  PBB) — a Python program, not an individual code. LLM proposes targeted code diffs.
  Archive indexed along two behavioral dims: (i) #lattices yielding k>=8 codes,
  (ii) total count of such codes. 4-6 islands, migration every 12-25 iters. C4 uses
  alternate dims (polynomial term count + monomial structure).
- modality: LiteratureGrounded
- evidence: paper.tex l.220-228 (framework), l.228 (C4 dims)
- dependencies: `sig.openevolve`, `mdl.css`, `mdl.pbb`
- assumptions: ansatz outputs not guaranteed valid codes; admission is by the kernel
  (evaluation cascade), per the agentic-lean invariant "LLM proposes; kernel admits".
- status: [SOLID]

---

## Claim candidates

### C-CSS — CSS commutation condition `css-commute`
- id: `clm.css_commute`
- type: Claim (algebraic identity)
- context: `mdl.css`
- claim: CSS condition H_X H_Z^T = A B + B A = 0 over F2, which follows from commutativity
  of R.
- modality: SymbolicDerivation
- evidence: paper.tex l.166 ("follows from the commutativity of R")
- dependencies: `ctx.ring` (commutative), `mdl.css`
- assumptions: none beyond R commutative.
- status: [SOLID]

### C-PBB — PBB commutation condition `pbb-commute`
- id: `clm.pbb_commute`
- type: Claim (algebraic condition)
- context: `mdl.pbb`
- claim: All rows commute iff (A C^T + B D^T) mod 2 is symmetric over F2. This is the only
  nontrivial commutativity condition (block-1/block-2 commutativity automatic from BB ring
  commutativity). Unlike CSS, must be verified computationally per tuple. Empirically ~10%
  of random weight-3 4-tuples at lattice (6,6) satisfy it.
- modality: SymbolicDerivation (condition); EmpiricalMeasurement (~10% rate)
- evidence: paper.tex l.180-181; symplectic derivation supplemental.tex l.690
- dependencies: `mdl.pbb`, `ctx.ring`
- assumptions: standard symplectic representation, X-first convention.
- status: [SOLID]

### T1 — `thm:ab_d2` Distance trap (every BB code with A=B, k>0 has d=2)
- id: `clm.ab_d2`
- type: Theorem
- context: `mdl.css` with A = B
- claim (verbatim): "Every BB code with A = B and k > 0 has d = 2 exactly."
  Proof sketch: for A=B every X-stabilizer is (A_r | A_r), so rowspace(H_X) lies in the
  diagonal subspace S = {(w,w)}. v_i = e_i + e_{i+l*m} = (e_i, e_i) lies in S and
  H_Z v_i = 0, so v_i in ker(H_Z); it is an X-stabilizer iff e_i in rowspace(A), but k>0
  forces rank(A) < l*m so some e_i is outside => weight-2 X-logical => d_X <= 2 (symmetric
  argument gives d_Z <= 2). Column weight >= 2 (polynomials with >=2 terms) => d >= 2.
  Hence d = 2. Holds regardless of check weight (any polynomial weight >= 2).
- modality: ExactProof
- evidence: paper.tex l.959-973 (theorem + full proof, App. D `app:ab_trap`)
- dependencies: `mdl.css`, `clm.css_commute`
- assumptions: polynomial weight >= 2 (for the d >= 2 lower bound). Distinct from antipodal
  self-duality B = A^T (`liang2025selfdual`), which can reach d up to 16.
- status: [SOLID]

### T1-ext — PBB extension of the A=B trap
- id: `clm.ab_d2_pbb`
- type: Claim (theorem extension)
- context: `mdl.pbb` with A = B
- claim: if A=B in a PBB code, the l*m weight-2 Z-type operators (0 | e_i + e_{i+l*m})
  commute with all stabilizers (X-part [A|A] has identical column blocks), placing them in
  the normalizer. MILP confirms d = 2 for ALL A=B PBB codes in the catalog; combined with
  d >= 2 (polynomial weight >= 2), d = 2.
- modality: SymbolicDerivation (normalizer membership) + NumericalSimulation (MILP per-catalog d=2)
- evidence: paper.tex l.196, l.975-980 (App. D extension)
- dependencies: `clm.ab_d2`, `mdl.pbb`, `clm.milp_css`
- assumptions: normalizer membership preserved under C,D perturbation; "is some such
  operator not itself a stabilizer" verified by MILP per code, not proven in general.
- status: [PRELIMINARY] — general (not catalog-restricted) statement is a [HOLE]: expected
  claim = "every A=B PBB code has d=2"; the paper only certifies it per-catalog-entry via MILP.

### T2 — `lem:crt_k` Univariate encoding dimension
- id: `clm.crt_k`
- type: Theorem
- context: `mdl.css` univariate subfamily
- claim (verbatim setup): l, m divisible by 3, c = l/3, A(y) = 1+y+y^2 in
  F2[y]/(y^m - 1), B(x) = A(x^c) in F2[x]/(x^l - 1). Then the BB code is a hypergraph
  product code encoding k = 8l/3 logical qubits (independent of m).
  Proof: BB(A,B) ~ HGP(H_B, H_A^T); HGP dim k = k1 k2 + k1^T k2^T (`tillich2014quantum`);
  dim ker H = deg gcd(f, z^N - 1) (`macwilliams1977theory`); (y-1)A=y^3-1 | y^m-1 so
  k_A = k_A^T = deg A = 2; (x^c-1)B = x^l-1 so k_B = k_B^T = 2c = 2l/3; thus
  k = 2 k_B k_A^T = 2*(2l/3)*2 = 8l/3.
- modality: SymbolicDerivation (paper proof) — rests on imported HGP formula
- evidence: paper.tex l.419-421, l.985-1024 (theorem + proof, App. C `app:crt`)
- dependencies: `sig.tillich` [AXIOM], `sig.macw` [AXIOM], `mdl.css`
- assumptions: HGP dimension formula and cyclic-code kernel identity imported, not
  re-derived. Verified computationally for all 1680 combos with 3|l, 3|m, l*m <= 250.
- status: [SOLID] (conditional on `sig.tillich`, `sig.macw` axioms; numerically corroborated)

### T3 — `tillich-zemor` HGP distance / univariate collapse
- id: `clm.tz_distance`
- type: Claim (imported theorem + applied consequence)
- context: `mdl.css` univariate subfamily
- claim: HGP distance d = min(d1, d2, d1^T, d2^T) (`tillich2014quantum`). Applied: every
  univariate code in the catalog has d in {2,4}. For palindromic check polynomials H^T = H,
  so the four-way min collapses to min(d_A, d_B). Catalog skips d=3 entirely (odd-weight
  f with f(1)=1 forces even-weight cyclic codewords).
- modality: LiteratureGrounded (TZ formula) + NumericalSimulation (catalog d in {2,4}, MILP)
- evidence: paper.tex l.408-411
- dependencies: `sig.tillich` [AXIOM], `clm.milp_css`
- assumptions: TZ distance formula cited, NOT reproduced.
- status: [AXIOM] — the TZ distance formula itself is treated as an imported postulate;
  the catalog-level d in {2,4} consequence is [SOLID] within the searched catalog only.

### V1 — `eq:milp_obj`/`eq:milp_commute`/`eq:milp_anticommute`/`eq:milp_binary` CSS MILP
- id: `clm.milp_css`
- type: Method (exact distance computation, CSS)
- context: `mdl.css`
- claim (verbatim labels): for the j-th logical qubit,
  min sum_{i=1..n} x_i  `eq:milp_obj`
  s.t. H_Z x == 0 (mod 2)  `eq:milp_commute`
       <x, Zbar_j> == 1 (mod 2)  `eq:milp_anticommute`
       x_i in {0,1}  `eq:milp_binary`
  mod-2 rows linearized via integer slack: sum_i a_i x_i - 2s = b, s in Z_{>=0}.
  Z-distance by swapping H_X<->H_Z; d = min(d_X, d_Z). For BB d_X = d_Z (involution
  exchanges H_X,H_Z). 2k MILP instances per code. "Exact" iff HiGHS MIP gap = 0 for all
  2k logicals; else incumbent is a valid upper bound.
- modality: ExactProof (when MIP gap=0) / ControlledApproximation (incumbent upper bound)
- evidence: supplemental.tex l.661-674 (eq block), paper.tex l.324-337
- dependencies: `sig.scipy_milp`, `sig.bravyi`, `mdl.css`
- assumptions: HiGHS optimality certificate is trusted (gap=0 => exact).
- status: [SOLID]

### V2 — Non-CSS symplectic MILP
- id: `clm.milp_pbb`
- type: Method (exact distance computation, non-CSS)
- context: `mdl.pbb`
- claim: symplectic weight |{i : a_i != 0 OR b_i != 0}|. MILP:
  min sum w_i s.t. H (a|b)^T == 0 (mod 2); <(a|b), Lbar_j>_symp == 1 (mod 2);
  w_i = a_i OR b_i enforced by w_i >= a_i, w_i >= b_i, w_i <= a_i + b_i (convex hull, tight
  at integer points); a_i,b_i,w_i in {0,1}. H is the symplectic-flipped stabilizer matrix:
  each row (s_X | s_Z) stored as (s_Z | s_X). 3n binary vars (vs n for CSS X-distance);
  ~4x slower per logical. For PBB the commutativity reduces to A C^T + B D^T symmetric / F2.
- modality: ExactProof (MIP gap=0) / ControlledApproximation (incumbent)
- evidence: supplemental.tex l.676-691
- dependencies: `clm.milp_css`, `sig.qldpc` (logical reps), `mdl.pbb`, `clm.pbb_commute`
- assumptions: X-first symplectic convention; OR-linearization correctness (stated as convex
  hull of the four feasible triples).
- status: [SOLID]

### V3 — Evaluation cascade (Stage 1/2/3) + trust filter
- id: `clm.cascade`
- type: Method (staged validation)
- context: `mdl.mapelites`
- claim: Stage 1 (~2s) k-only F2 rank on lattices (6,6),(12,6); discards ~30% of mutants.
  Stage 2 (~30-60s) BP-OSD distance on 8 lattices {(12,6),(6,12),(12,12),(24,6),(15,12),
  (30,6),(16,9),(18,8)}, spanning n in {144,288,360}; top-10 by k diversity get 1000 OSD0
  trials, FOM>=6 get +3 batches of 500. Stage 3 MILP exact: in-loop for C4-C5 top codes,
  post-hoc for C1-C3. Trust filter on d/sqrt(n): <=1.3 fully trusted, >=2.0 discarded,
  linear interpolation between; C5 bypasses (uses verified distances, rejects d<=4).
- modality: LiteratureGrounded
- evidence: paper.tex l.247-258 (cascade), l.369-371 (trust filter)
- dependencies: `clm.milp_css`, `sig.ldpc`, `mdl.mapelites`
- assumptions: BP-OSD ranking adequate within loop (later shown unreliable — see V4).
- status: [SOLID]

### V4 — BP-OSD overestimation finding
- id: `clm.bposd_overest`
- type: Claim (empirical methodology finding)
- context: `sig.ldpc`, `clm.milp_css`
- claim: BP-OSD gives stochastic UPPER bounds only; systematically overestimates distance
  for high-rate codes (k/n > 0.1), up to 12x. Multi-decoder protocol (OSD0+SP-BP,
  OSD-CS10+SP-BP, OSD-CS10+min-sum-BP; 10 batches x 5000 = 150k trials; verified bound =
  global min). 147 of 154 trinomial representations had bounds tightened. Fails to detect
  d=2 for A=B codes even at 1.5e6 trials (reported d<=14 for [[144,32,2]]).
- modality: EmpiricalMeasurement / StatisticalInference
- evidence: paper.tex l.90, l.211, l.309-317; supplemental.tex l.117-258
- dependencies: `sig.ldpc`, `clm.milp_css`, `clm.ab_d2`
- assumptions: ldpc-library defaults (max_iter=n, no damping, p=1e-3 placeholder).
- status: [SOLID]

### V5 — Achievable-syndrome sampling (non-CSS BP-OSD fix)
- id: `clm.achievable_sampling`
- type: Method (non-CSS distance bounding)
- context: `mdl.pbb`
- claim: per-channel BP-OSD bounding (`bravyi2024high` H_eff = [H_check; L]) fails for
  non-CSS because achievable logical cosets form a strict subspace (Y-type logicals need
  mixed support; random binary vectors rarely lie in im(H)). Fix: compute achievable
  subspace per channel as GF(2) null-space projection of stabilizer matrix restricted to
  channel, sample only from it. Restored decode success from ~0% to ~100% on tested PBB.
  3-tier pipeline: Tier1 exhaustive weight-w enum (d<=6 at n<=216, d<=4 at n>216, ~89GB at
  n=360); Tier2 symplectic MILP (adaptive timeouts 15/30/60s); Tier3 BP-OSD achievable
  sampling. Final d <= min(d_enum, d_MILP, d_BPOSD).
- modality: SymbolicDerivation (subspace) + NumericalSimulation (decode-success restoration)
- evidence: paper.tex l.91, l.341-364
- dependencies: `sig.bravyi`, `clm.milp_pbb`, `mdl.pbb`
- assumptions: "~half of cosets unreachable" shown empirically on [[144,12,12]] PBB; "not
  proved general" (paper's words).
- status: [PRELIMINARY] — generality is a [HOLE]: expected claim = "achievable subspace has
  dimension k for all PBB Z/Y channels"; paper proves only per-instance.

### V6 — BLISS dedup + LC-CSS equivalence layer
- id: `clm.dedup_lc`
- type: Claim (equivalence accounting)
- context: `mdl.tanner`, `mdl.pbb`
- claim: 225 CSS polynomial representations -> 97 distinct codes (2.3:1, up to 14:1 for
  univariate). 720 tuple-distinct PBB -> 368 BLISS-unique (1.96:1). LC-CSS check
  (App. E `app:lc`): group-CSS iff rank[X|Z] = rank X + rank Z over GF(2) (Lemma 7.4
  `cross2025small`); 6 Clifford coset reps {I,S,H,HS,SH,HSH}; Hadamard 2-coloring
  (parity union-find, covers non-uniform {I,H}); affine GF(2) systems for {I,S} and {H,HS};
  36 uniform per-block assignments. Result: 11/368 CSS-equivalent (10 via non-uniform
  Hadamard, 1 = [[36,4,6]] via uniform S); 357 CSS-inequivalent within tested LC families.
  465 "distinct" = 97 CSS + 368 PBB is a CONSERVATIVE upper bound.
- modality: LiteratureGrounded (counts) + ExactProof (GF(2) rank/affine tests where run)
- evidence: paper.tex l.380-394 (dedup), l.189-194, l.1029-1087 (App. E)
- dependencies: `sig.bliss`, `sig.cross2025` [AXIOM], `mdl.tanner`, `mdl.pbb`
- assumptions: coverage gaps (a) non-uniform {SH,HSH} on block1, (b) cross-class non-uniform
  patterns — NOT brute-forced; 357 are "CSS-inequivalent within tested LC families", not
  "genuinely non-CSS".
- status: [SOLID] (with explicit [FUTURE] residual-coverage gaps from App. E `app:lc`)

---

## Open obligations (markers digest)

- [BLOCKING] `sig.code` qcode-discovery repo EMPTY (sha 4a9520e, 2026-06-02). No code-level
  artifact importable. Unblocks when upstream populates the repo; owner = paper authors.
  Blocks: any reproduction of `clm.cascade`, `clm.milp_css`, `clm.milp_pbb`,
  `clm.achievable_sampling`, `clm.dedup_lc` at executable level.
- [AXIOM] `sig.bravyi` (2308.07915) — BB definition + MILP baseline + per-channel BP-OSD;
  MANDATORY escalation candidate. All BB/PBB final claims remain conditional on it.
- [AXIOM] `sig.tillich`, `sig.macw`, `sig.cross2025` — imported theorems (HGP dim/distance,
  cyclic kernel identity, Lemma 7.4). `clm.crt_k`, `clm.tz_distance`, `clm.dedup_lc` rest
  on them.
- [HOLE] `clm.ab_d2_pbb` — general "every A=B PBB code has d=2" not proven; only per-catalog
  MILP. Expected: ExactProof or [AXIOM] on normalizer-non-stabilizer step.
- [HOLE] `clm.achievable_sampling` — general dimension claim for achievable subspace not
  proven; only per-instance ([[144,12,12]] PBB).
- [FUTURE] `clm.dedup_lc` — LC coverage gaps (a),(b); GF(4)-linearity classification
  (`cross2025small` Lem 7.5/Cor 7.6) not pursued.
- Local env MISSING: qldpc, ldpc, igraph, openevolve, litellm. scipy.optimize.milp and
  numpy present — only `clm.milp_css`/`clm.milp_pbb` substrate is locally runnable.

---
END core.md
