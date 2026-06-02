# Chunk 001 — Main Body Digest (paper.tex, Intro → Discussion)

> Pipeline-0 (source-import) chunk digest. Every entry below is a TYPED ledger
> object. Default modality `LiteratureGrounded` (evidence = tex section); proofs/
> derivations present in this chunk are marked separately. Tex labels preserved
> VERBATIM. Cited-but-not-reproduced results are `[AXIOM]`. Open obligations are
> `[HOLE]`/`[FUTURE]`/`[BLOCKING]`. Risk tiers R0–R4 per `code_quality_policy.md`.

---

## 0. Provenance

| Field | Value |
|---|---|
| Paper | arXiv:2606.02418 "Evolutionary Discovery of Bivariate Bicycle Codes with LLM-Guided Search" |
| Authors | Cruz-Benito, Cross, Kremer, Faro (IBM Research; PRX Quantum) |
| Source file | `ref-paper/arxiv-2606.02418/src/paper.tex` (1091 lines total) |
| Chunk range | lines 60–770 |
| Sections covered | `sec:intro` (61), `sec:related` (108), `sec:prelim` (151) incl. `sec:bb` (155), `sec:pbb` (171), `sec:fom` (199), `sec:ab_trap` (206); `sec:method` (214) incl. `sec:framework` (218), `sec:cascade` (244), `sec:campaigns` (261); `sec:verification` (303) incl. `sec:bposd_limits` (307), `sec:milp` (320), `sec:noncss_pipeline` (339), `sec:trust` (367); `sec:results` (374) incl. `sec:families` (378), `sec:tradeoff` (534), `sec:comparison` (563), `sec:code_capacity` (633), `sec:bposd_findings` (671), `sec:ablation` (704); `sec:discussion` (724) |
| Forward refs (NOT in this chunk) | App.~`app:ab_trap`, `app:crt`, `app:lc`, `app:ablation`, `app:threshold`; SM tables; `lem:crt_k`, `thm:ab_d2` statements live in appendices |

---

## 1. Verbatim named constructions / definitions / claims

Each labeled with section anchor + tex line(s). Quotes are VERBATIM where the
artifact requires verification.

### D1 — CSS Bivariate Bicycle (BB) code [`sec:bb`, l.157–168]
- Ring: `R = \FF_2[x,y]/(x^\ell{-}1, y^m{-}1)`, two weight-3 polynomials (trinomials) `A, B \in R`.
- Parity checks (eq. l.160–163): `H_X = (A  B)`, `H_Z = (B^\top  A^\top)`. `A,B` are `\ell m \times \ell m` circulants; `A^\top` is image under involution `x \mapsto x^{-1}, y \mapsto y^{-1}`.
- CSS condition (l.166): "`H_X H_Z^\top = AB + BA = 0` over `\FF_2` follows from the commutativity of `R`."
- Parameters (l.167): `\code{n,k,d}` with `n = 2\ell m`, `k = 2\ell m - 2\,\mathrm{rank}_{\FF_2}(H_X)`, `d` = min weight of a nontrivial logical operator.
- Trinomial restriction → weight-6 stabilizers (Campaigns 1–3); Campaign 4 relaxes to 4–6-term polynomials (weight-8 to weight-12), incl. mixed monomials `x^a y^b` (`a,b>0`).

### D2 — Perturbed Bivariate Bicycle (PBB) non-CSS code [`sec:pbb`, l.171–197]
- Four polynomials `A,B,C,D \in R`; stabilizer matrix (eq. l.175–177): `H = [[A, B, C, D],[0,0,B^\top,A^\top]]`.
- Block-1 row: mixed X-support `(A,B)` + Z-support `(C,D)`; block-2 row: purely Z-type.
- Commutativity (l.180): "All rows commute if and only if `(AC^\top + BD^\top) \bmod 2` is symmetric over `\FF_2`" — the only nontrivial condition; block1↔block2 automatic from BB ring commutativity. MUST be verified computationally per tuple (unlike CSS).
- Empirical: ~10% of random weight-3 4-tuples at lattice `(6,6)` satisfy the constraint (l.181).
- Reduces to CSS BB when `C = D = 0` (l.183).
- Non-CSS validity (3 levels, l.186–193): (i) row-op check (`C=B^\top` and `D=A^\top` ⇒ CSS; no top-FOM code satisfies); (ii) Hadamard 2-coloring (App `app:lc`) — pure-X/Z iff no Y support AND parity 2-coloring graph bipartite; (iii) per-qubit Clifford via 36 uniform per-block + GF(2) affine for `{I,S}`,`{H,HS}`. Result: 158/368 have Y-support; of remaining 210, 10 Hadamard-CSS; +1 uniform-S `\code{36,4,6}` (FOM 4.0). Total 11/368 CSS-equiv, 357 CSS-inequivalent under tested LC.
- `A=B` trap extends (l.196): `\ell m` weight-2 Z-operators `(0|\mathbf{e}_i + \mathbf{e}_{i+\ell m})` commute with all stabilizers ⇒ `d=2` (MILP-confirmed for all `A=B` PBB).

### D3 — Figure of merit FOM [`sec:fom`, l.199–203]
- `\FOM = kd^2/n`, motivated by BPT bound `kd^2 = O(n)` [`bravyi2010tradeoffs`].
- Gross code `\code{144,12,12}` has FOM = 12; rotated surface code FOM = 1 (l.202). Used as relative benchmark, NOT an absolute upper bound for general (non-2D-local) qLDPC.
- Highest prior CSS BB: FOM 12.0 (`\code{144,12,12}`), FOM ≤ 19.2 (`\code{360,12,{\leq}24}`, weight-6 CSS) [`bravyi2024high`].

### D4 — `A=B` distance trap [`sec:ab_trap`, l.205–211]
- Claim: `A=B` always yields `d=2` (proof in App `app:ab_trap` → `thm:ab_d2`).
- Three pipeline detection mechanisms: (i) `d/\sqrt{n}` trust filter; (ii) MILP `d=2` in <1s; (iii) LLM diversification after low-fitness feedback.
- BP-OSD FAILED to detect `d=2` even at `1.5 \times 10^6` trials — reported `d \leq 14` for `\code{144,32,2}` despite `\ell m = 72` weight-2 X-operators in normalizer (`k/2 = 16` independent nontrivial logicals).

### C1 — HGP dimension result [`sec:families`, l.419–421; statement of `lem:crt_k`]
- For `A = 1{+}y{+}y^2`, `B = 1{+}x^c{+}x^{2c}` with `c = \ell/3`, `3 \mid \ell`, `3 \mid m`: BB code is `\mathrm{HGP}(H_B, H_A^\top)`, `k = 8\ell/3` (independent of `m`). Theorem `lem:crt_k` (App `app:crt`).
- Follows from HGP dimension formula `k = k_1 k_2 + k_1^\top k_2^\top` [`tillich2014quantum`] + divisibility `A(y) \mid y^m{-}1`, `B(x) \mid x^\ell{-}1`.
- Verified computationally for all 1,680 combos with `3|\ell, 3|m, \ell m \leq 250`.

### C2 — Tillich–Zémor distance for univariate/HGP [`sec:families`, l.408–412]
- `d = \min(d_1, d_2, d_1^\top, d_2^\top)` [`tillich2014quantum`] — BB distance bounded by smallest of four classical cyclic-code distances `\ker H_A, \ker H_B, \ker H_A^\top, \ker H_B^\top`. For palindromic check polys `H^\top = H` ⇒ collapses to `\min(d_A, d_B)`.
- Every univariate catalog code has `d \in \{2,4\}` (MILP, l.408). Subfamily `c=\ell/3`: `(x^\ell{-}1)/B = 1{+}x^c` weight-2 ⇒ `d=2`; remaining univariate ⇒ `d=4`. Odd-weight `f` with `f(1)=1` ⇒ all-even-weight cyclic code ⇒ catalog skips `d=3` entirely.

### C3 — `\code{288,24,12}` decomposability [`sec:families`, l.425–434]
- `A = x^6{+}y{+}y^2`, `B = y^3{+}x^2{+}x^4` at `(12,12)`; MILP exact `d=12` (48 logicals). Only even `x`-exponents ⇒ Tanner graph (`H_X + H_Z`) has two disconnected components (even/odd `x`-indices).
- Disconnection ⇒ direct sum (l.427): restriction of any logical to one component is itself a logical.
- Re-indexing `x \to x/2`: each component at `(6,12)`, `x \leftrightarrow y` swap of gross code `(12,6)`. Hence `\code{288,24,12} \cong \code{144,12,12} \oplus \code{144,12,12}` (l.430). No EC advantage; BLISS confirms same direct sum also at `(24,6)`.

### C4 — `\code{288,16,12}` (top indecomposable wt-6 d=12) [`sec:families`, l.436]
- `A = x^3{+}y{+}y^2`, `B = y^3{+}x{+}x^2`, all shifts ≤ 3. Highest-`k` indecomposable CSS code at `d=12` (since `\code{288,24,12}` decomposes). Only three distinct `x/y`-swap codes reach `d \geq 12`, all `k \leq 24`; indecomposable bound `k \leq 16`.

### C5 — Mixed-monomial / higher-weight codes [`sec:families`, l.440–450]
- 45 distinct Campaign-4 codes with `x^a y^b` (`a,b>0`). Subfamilies: diagonal-mixed (`x^a y^a`, wt-6), mixed-monomial augmentation (wt-8), multi-term pure (wt-8).
- Top: `\code{288,50,8}` (wt-8, exact `d=8`, FOM 11.1), `\code{360,20,{\leq}14}` (wt-8, FOM ≤ 10.9).
- High-`k` (`k=50–54`): factored product `A = (1{+}x^3)(1{+}y^3)` for `\code{144,54,4}`; same-variable factored ⇒ `d \leq 4`. Cross-factored exception `\code{288,50,8}`: `A=(1{+}x)(1{+}y^5)`, `B=(1{+}y)(1{+}x^5)` ⇒ `d=8`.

### C6 — Non-CSS PBB results [`sec:families`, l.452–493]
- Campaign 5: 18,588 candidate 4-tuples, 7 lattices ⇒ 368 distinct codes, 78 `(n,k,d)` sets: 251 exact rows + 117 upper-bound (110 TRUSTED + 7 PARTIAL with `d/\sqrt{n} \geq 1.5`).
- All 368 use trinomial bases (`|A|=|B|=3`); non-CSS character entirely from `C,D`. Optimal `|C|=|D|=2` (56% of codes, avg FOM 6.4); heavy `|C|+|D| \geq 6` caps `d \leq 8`.
- 25 codes match/exceed FOM 12.0: 14× `\code{144,12,12}` (FOM 12.0; 7 exact, 7 trusted), 4 TRUSTED UB at n=360/180, 7 PARTIAL UB.
- `\code{360,60,6}` exact: 60 logical qubits (`k/n = 1/6`), highest rate among non-CSS with `d \geq 6`.

---

## 2. The 13 pipeline components (with tex anchors)

| # | Component | Section / line | Spec |
|---|---|---|---|
| P1 | Code construction (BB + PBB) | `sec:bb` l.157–167; `sec:pbb` l.173–183 | `qldpc` v1.0.1; `H_X=(A B)`, `H_Z=(B^\top A^\top)`; PBB `H=[[A,B,C,D],[0,0,B^\top,A^\top]]`. |
| P2 | `k`-only `\FF_2` rank (Stage 1) | `sec:cascade` l.247 | ~2s on `(6,6)`,`(12,6)`; discards ~30% of mutants with no `k>0` code at both. Both have `3|\ell` (possible bias, l.248). |
| P3 | Evaluation cascade (3 stages) | `sec:cascade` l.244–258 | Stage1 k-only ~2s; Stage2 BP-OSD on 8 lattices ~30–60s; Stage3 MILP in-loop (C4–5) / post-hoc (C1–3). ~2e5 candidates evaluated, ~400 MILP-verified. |
| P4 | BP-OSD distance bounding (Stage 2) | `sec:bposd_limits` l.307–317 | `ldpc` v2.2.0; stochastic UPPER bounds `d_true \leq d_reported`. Multi-decoder: OSD0/SP-BP, OSD-CS10/SP-BP, OSD-CS10/MS-BP; 10×5000 = 150k trials/code; bound = global min over 30 batches. Defaults: `max_iter=n`, no damping, error-rate placeholder `1e-3`. |
| P5 | MILP CSS distance | `sec:milp` l.320–336 | HiGHS via `scipy`; minimize `\sum_j x_j` s.t. mod-2 commute/anticommute with slack vars; `2k` instances (k X-logicals + k Z-logicals); `d=min` over `2k`. Timeouts 120–600s (3000s C4 top, 14400s C5 deep). "Exact" only when all `2k` reach MIP gap=0. Validated on `\code{72,12,6}`,`\code{144,12,12}`. Audit: `\code{288,24,12}` (48 log, 29min), `\code{288,16,12}` (32 log, 80min), gross (24 log, 13min). |
| P6 | Adaptive non-CSS pipeline (3 tiers) | `sec:noncss_pipeline` l.339–364 | Tier1 exhaustive wt-`w` enum (`d\leq6` at `n\leq216`; `d\leq4` at `n>216`, ~89GB at n=360). Tier2 MILP symplectic (adaptive timeouts 15/30/60s). Tier3 BP-OSD with achievable-syndrome sampling. Final `d \leq min(d_enum,d_MILP,d_BPOSD)`. 149 PBB deep-MILP ⇒ 63 exact + 33 downward corrections (22% rate); largest `d=24\to16` at n=360. |
| P7 | Achievable-syndrome sampling | `sec:noncss_pipeline` l.353–360 | Per-channel achievable subspace = image of channel error space under `H_eff` map (GF(2) null-space projection on stabilizer matrix restricted to channel). On `\code{144,12,12}` PBB: Z-channel achievable subspace dim `k` within `2k` ⇒ ~half random cosets have no preimage. Fix restored ~0% → ~100% decode success. |
| P8 | Trust filter `d/\sqrt{n}` | `sec:trust` l.367–371 | `\leq 1.3` fully trusted; `\geq 2.0` discarded; linear interp between. CSS Campaigns 1–4 only. Known failure: `\code{360,40,2}` passed at `d_BP/\sqrt{n}=1.26` despite true `0.11`. Campaign 5 bypasses (rejects `d \leq 4`). |
| P9 | MAP-Elites evolution | `sec:framework` l.218–229 | OpenEvolve; target = generator ansatz `G(\ell,m) \to \{(A_i,B_i)\}` (or 4-tuples). 4–6 islands, migration 12–25 iters. Dims: (#lattices with `k\geq8` codes, total such codes). C4 uses term-count + monomial-structure dims. |
| P10 | BLISS Tanner-graph dedup | `sec:families` l.380–394 | `python-igraph` + BLISS canonical form. CSS coloring: qubits c0, X-checks c1, Z-checks c2. Non-CSS: per-stabilizer X-support + Z-support vertices (3 colors) + tying edge forbidding independent permutation. 225 reps → 97 distinct CSS (2.3:1, up to 14:1 univariate; 99 classes incl. 2 Bravyi rediscoveries). 720 → 368 PBB (1.96:1). Conservative UPPER bound on distinctness. |
| P11 | Decomposability (Tanner connectivity) | `sec:families` l.425–434 | Connectivity of `H_X + H_Z`; disconnected ⇒ direct sum. Caught `\code{288,24,12} = `gross⊕gross. Invisible to BP-OSD. |
| P12 | LC-CSS equivalence (PBB) | `sec:pbb` l.186–194; `sec:families` l.488 | 3 levels: row-op, Hadamard 2-coloring (App `app:lc`), per-qubit Clifford (36 uniform + GF(2) affine for `{I,S}`,`{H,HS}`). 11/368 CSS-equiv (10 Hadamard, 1 uniform-S `\code{36,4,6}`); 357 CSS-inequivalent. |
| P13 | Polynomial-level dedup (in-loop) | `sec:families` l.396–399 | Hash set of coefficient tuples for `(A,B)` / `(A,B,C,D)`, `O(1)` lookup. Fast; does NOT catch lattice-symmetry equivalences (deferred to P10). |

Supporting infra (l.280–282): `qldpc` v1.0.1, `ldpc` v2.2.0, HiGHS via `scipy`, `python-igraph`+BLISS, LiteLLM proxy. C1–3 on Apple M4 Max 36GB; C4–5 on 64-core 251GB RHEL 9.

---

## 3. Campaign configuration ledger [`sec:campaigns`, Table `tab:campaigns` l.284–300]

| Camp | Type | Models | Iters | Pop | Codes | Time | Cost |
|---|---|---|---|---|---|---|---|
| 1 | CSS | Gemini 3 Flash Preview | 100 | 100 | 9 | 5h | $15 |
| 2 | CSS | Ensemble (Opus 4.6 / GPT-5.2 / Gemini 3 Pro) | 251 | 100 | 0* | 9.5h | $25 |
| 3 | CSS | Ensemble | 500 | 1,000 | 145 | 21h | $50 |
| 4 | CSS (4–6 term) | Ensemble (Opus 4.6 / GPT-5.3-Codex / Gemini 3.1 Pro), T=1.0 | 300 | 750 | 45 | 92h | $47 |
| 5 | PBB | Ensemble, T=0.8 | 500 | 200 | 368 | 11h | $100 |

*Camp 2: retroactively found to overlap entirely with Camp 3 (negative result for small-pop ensemble; l.267–268).
- Totals: ~1,650 iters, ~140h, ~$237 tabulated; ~$400 total incl. ablation arms (~$70) + exploratory/failed runs (~$90) (l.286).
- Seed (C1–3): ~300 lines Python encoding `x/y`-swap, perturbations of known codes, self-similar scaling, small-exponent enumeration (l.264). Temperatures: C1–3,5 = 0.8; C4 = 1.0 (l.272, 274).
- C5 excluded `(12,12)`,`(15,12)` (highest-FOM CSS lattices) due to ~4× slower symplectic MILP (l.277). Seed = known CSS base pairs + random `C,D` (l.278).

---

## 4. Candidate ledger entries (typed)

> Schema: id | claim | modality | evidence (tex) | dependencies | risk | status

| id | claim | modality | evidence | deps | risk | status |
|---|---|---|---|---|---|---|
| L01 | CSS condition `AB+BA=0` over `\FF_2` (R commutative) | SymbolicDerivation | `sec:bb` l.166 | D1 | R0 | `[SOLID]` |
| L02 | PBB commutativity iff `(AC^\top+BD^\top)` symmetric over `\FF_2` | SymbolicDerivation | `sec:pbb` l.180 | D2 | R1 | `[SOLID]` (reproducible algebra) |
| L03 | `n=2\ell m`, `k=2\ell m - 2 rank_{\FF_2}(H_X)` | SymbolicDerivation | `sec:bb` l.167 | D1 | R0 | `[SOLID]` |
| L04 | All `A=B` BB codes have `d=2` exactly (`thm:ab_d2`) | ExactProof (App, not in chunk) | `sec:ab_trap` l.208; `sec:intro` l.81 | D4, `thm:ab_d2` | R1 | `[AXIOM]` here — proof in `app:ab_trap`, not reproduced in chunk |
| L05 | `k=8\ell/3` for `c=\ell/3` univariate subfamily (`lem:crt_k`) | SymbolicDerivation + NumericalSimulation | `sec:families` l.419–421 | C1, `lem:crt_k`, L11 | R1 | `[AXIOM]` here (statement only; proof in `app:crt`) + verified 1,680 combos |
| L06 | Univariate catalog codes all have `d \in \{2,4\}` | NumericalSimulation (MILP) | `sec:families` l.408–411 | C2, P5 | R2 | `[SOLID]` (MILP exact within catalog) |
| L07 | `\code{288,24,12}` = gross ⊕ gross (decomposable) | SymbolicDerivation + NumericalSimulation | `sec:families` l.426–434 | C3, P11 | R2 | `[SOLID]` |
| L08 | `\code{288,16,12}` `d=12` exact, all shifts ≤3, highest-`k` indecomposable wt-6 d=12 | NumericalSimulation (MILP exact, 32 log, 80min) | `sec:milp` l.330; `sec:families` l.436 | C4, P5 | R2 | `[SOLID]` |
| L09 | `\code{288,50,8}` wt-8 cross-factored, exact `d=8`, FOM 11.1 | NumericalSimulation (MILP) | `sec:families` l.444,449 | C5, P5 | R2 | `[SOLID]` |
| L10 | `\code{144,12,12}` PBB matches gross FOM 12.0 via mixed X/Z, exact | NumericalSimulation (MILP) | `sec:families` Table `tab:pbb_best` l.472; `sec:intro` l.86 | D2, P6 | R2 | `[SOLID]` |
| L11 | HGP dim formula `k = k_1 k_2 + k_1^\top k_2^\top` [`tillich2014quantum`] | LiteratureGrounded | `sec:families` l.420 | `tillich2014quantum` | R2 | `[AXIOM]` (cited) |
| L12 | Tillich–Zémor distance `d=min(d_1,d_2,d_1^\top,d_2^\top)` | LiteratureGrounded | `sec:families` l.409 | `tillich2014quantum` | R2 | `[AXIOM]` (cited) |
| L13 | BP-OSD overestimates `d` up to 12× for `k/n>0.1`; 147/154 reps tightened | StatisticalInference / EmpiricalMeasurement | `sec:bposd_findings` l.673–701; `sec:intro` l.90 | P4, P5 | R2 | `[SOLID]` |
| L14 | Naive random-syndrome BP-OSD → ~0% decode success on many PBB | EmpiricalMeasurement | `sec:noncss_pipeline` l.360; `sec:bposd_findings` l.697 | P6, P7 | R2 | `[SOLID]` |
| L15 | Rate–distance tradeoff: wt-6 `k>24` ⇒ `d\leq4`; indecomp `d=12` ⇒ `k\leq16`; wt-8 new (k,d) but no escape | EmpiricalMeasurement (catalog-wide MILP) | `sec:tradeoff` l.549–558; `sec:intro` l.78 | C2,C4,C5,L15-deps | R2 | `[PRELIMINARY]` — empirical within searched catalog; structural-constraint claim UNPROVEN (see HOLE-1) |
| L16 | 465 distinct codes = 97 CSS + 368 PBB; conservative upper bound | EmpiricalMeasurement (BLISS) | `sec:families` l.386,393 | P10 | R2 | `[SOLID]` (as upper bound) |
| L17 | 11/368 PBB CSS-equivalent under tested LC; 357 inequivalent | NumericalSimulation (GF(2) + exhaustive) | `sec:pbb` l.193; `sec:families` l.488 | P12, `app:lc` | R3 | `[PRELIMINARY]` — residual LC coverage gaps acknowledged (`app:lc`) |
| L18 | GA-G `\Sigma_k=1037` beats LLM `704` by 47% with 14k vs 213k evals, but only `d\leq2` | EmpiricalMeasurement | `sec:ablation` l.704–718 | P9 | R2 | `[SOLID]` (with caveats: no budget control, no distance feedback to GA) |
| L19 | `\code{288,12,18}` (Bravyi, FOM 13.5) > all our indecomposable codes at n=288 | LiteratureGrounded + EmpiricalMeasurement | `sec:comparison` l.622; Table `tab:useful` l.602 | `bravyi2024high` | R2 | `[SOLID]` |
| L20 | Non-CSS `\code{144,12,12}` PBB beats CSS gross under X-only at `p\geq6%`; tie under depolarizing (iid prior) | NumericalSimulation (100k shots) | `sec:code_capacity` l.662–665 | D2, footnote `fn:depolarizing-decoder` | R3 | `[PRELIMINARY]` — decoder-dependent (sub-optimal iid prior; see HOLE-3) |

---

## 5. Open holes / gaps

- **HOLE-1 `[HOLE]` (structural tradeoff).** Claim L15: is the rate–distance tradeoff a *structural constraint* of the BB construction or an artifact of incomplete search? Expected resolution: proof of an upper bound on `kd^2/n` for the BB family, OR a counterexample code escaping the envelope. Tex: `sec:tradeoff` l.550, l.560; `sec:intro` l.78 ("we do not prove this is a structural constraint"). Modality required: ExactProof or Counterexample. Owner: open research. `[BLOCKING]` for any claim that promotes L15 from `[PRELIMINARY]` to `[SOLID]` as a structural theorem.
- **HOLE-2 `[FUTURE]` (non-CSS escape).** Whether any non-CSS construction over `\FF_2[x,y]/(x^\ell{-}1,y^m{-}1)` can EXCEED the CSS envelope. C5 excluded `(12,12)`,`(15,12)` where highest-FOM CSS codes live; extending PBB there is the stated next step. Tex: `sec:intro` l.87; `sec:tradeoff` l.559; `sec:discussion` l.763. Deferred — does not block current catalog claims.
- **HOLE-3 `[HOLE]` (depolarizing decoder).** CSS-vs-PBB depolarizing comparison uses a MISMATCHED iid X/Z BP-OSD prior (`P(e_x=1,e_z=1)=p/3` vs iid `(2p/3)^2`); reported depolarizing values are a LOWER bound on threshold under an optimal correlated decoder (e.g. quaternary BP over GF(4)), not the optimal threshold. Tex: footnote `fn:depolarizing-decoder` l.635; l.665. Expected: correlation-aware decoder rerun. Affects L20.
- **HOLE-4 `[FUTURE]` (Stage-1 `3|\ell` bias).** Both screening lattices have `3|\ell`; may bias toward divisibility-by-3 structures; failure of all evolved ansätze at `(16,9)`,`(18,8)` may partly reflect this. Tex: `sec:cascade` l.248; `sec:ablation` l.713; `sec:discussion` l.743.
- **HOLE-5 `[FUTURE]` (LC residual coverage).** L17's 357 "CSS-inequivalent" holds only *under tested LC patterns*; `app:lc` documents residual coverage gaps (not all single-qubit Clifford patterns, no full-Clifford). Tex: `sec:pbb` l.193; `sec:families` l.394.
- **HOLE-6 `[FUTURE]` (C4 confounded ablation).** Campaign 4 simultaneously changed MAP-Elites dims AND polynomial scope (trinomial → 4–6-term); no controlled ablation isolates which produced the 45 new codes. Tex: `sec:campaigns` l.273.
- **HOLE-7 `[AXIOM]` (cited distance lemmas).** L11/L12 (`tillich2014quantum` HGP dim + distance) treated as imported postulates; downstream `k=8\ell/3` and univariate `d\in\{2,4\}` results remain conditional on them. Tex: `sec:families` l.409,420.
- **HOLE-8 `[FUTURE]` (theorem statements not in chunk).** `thm:ab_d2` and `lem:crt_k` full PROOFS are in App `app:ab_trap`/`app:crt` (lines >770, NOT in this chunk). L04/L05 carry `[AXIOM]` status until the appendix chunk is imported and the proofs reproduced. `[BLOCKING]` for elevating L04/L05 to ExactProof modality.
- **HOLE-9 `[FUTURE]` (circuit-level noise).** All FOM/threshold claims are combinatorial / code-capacity only; circuit-level fault-tolerant performance (the criterion Bravyi et al. optimized for) is unassessed. Tex: `sec:discussion` l.745, l.749.

---

## 6. Key landmark codes (timeline seed, this chunk)

| Code | Type | `d` status | FOM | Source line |
|---|---|---|---|---|
| `\code{288,16,12}` | CSS wt-6 XY | exact | 8.0 | l.520, l.436 — highest-`k` indecomposable wt-6 d=12 |
| `\code{288,24,12}` | CSS wt-6 XY | exact | 12.0 | l.516 — decomposable = gross⊕gross |
| `\code{288,50,8}` | CSS wt-8 MX | exact | 11.1 | l.517 — cross-factored |
| `\code{144,8,12}` | CSS wt-6 MX | exact | 8.0 | l.521 |
| `\code{144,54,4}` | CSS wt-8 MX | exact | 6.0 | l.525 — `k=54`, factored product |
| `\code{360,16,{\leq}14}` | CSS wt-6 XY | I (7/32 proven) | ≤8.7 | l.519 |
| `\code{360,20,{\leq}14}` | CSS wt-8 MX | I | ≤10.9 | l.518 |
| `\code{360,40,4}` | CSS UV | exact | 1.8 | l.526 — `k=8\ell/3` |
| `\code{360,40,2}` | CSS UV | exact | 0.4 | l.528 — 12× BP-OSD overestimate |
| `\code{144,32,2}` | CSS SD (`A=B`) | exact | 0.9 | l.527 — `A=B` trap |
| `\code{144,12,12}` PBB | non-CSS | exact | 12.0 | l.472, l.614 — mixed X/Z, matches gross FOM |
| `\code{360,12,{\leq}24}` PBB | non-CSS wt-8 | I | ≤19.2 | l.470, l.613 — highest PBB FOM |
| `\code{360,60,6}` PBB | non-CSS | exact | — | l.492 — highest rate `k/n=1/6`, `d\geq6` |
| `\code{108,8,10}` PBB | non-CSS | exact | 7.4 | l.475, l.615 |
| `\code{72,4,8}` PBB | non-CSS | — | — | l.647, l.666 |

Prior-art anchors (cited): gross `\code{144,12,12}` FOM 12 (`bravyi2024high`); `\code{288,12,18}` FOM 13.5 exact; `\code{360,12,{\leq}24}` FOM ≤19.2 wt-6 CSS; `\code{150,16,8}` (`wang2024coprime`, prior highest `k`); mirror `\code{60,4,10}` FOM 6.7 / `\code{85,8,9}` (`khesin2026mirror`); `\code{144,14,14}` FOM 19.1 (`symons2025covering`).
