# Bundle Dependency Plan — arXiv:2606.02418

"Evolutionary Discovery of Bivariate Bicycle Codes with LLM-Guided Search"
(Cruz-Benito, Cross, Kremer, Faro; IBM Research; PRX Quantum).

Groups the 13 pipeline components (`PC-01..PC-13`, `ledger_seed.md`) and the theorem
set (`TH-01..TH-04`, `TH-AXIOM-TZ`, `CL-01..CL-03`) into **9 implementation bundles**
`B0..B8` with an explicit build DAG. This is the implementation-ordering view that sits
between `core.md` (typed IR), `ledger_seed.md` (per-component ledger), and `obligations.md`
(per-`[HOLE]` discharge plan). Component → ledger ID cross-references are kept verbatim so
the three files stay joinable.

Each bundle records: **members** (modules + ledger IDs), **depends-on** (other bundles),
**external libs** (AVAILABLE / MISSING), **exit criteria** (what closes the bundle), and a
**status marker** (`_common/markers.md`).

Conventions, schema, and discipline as in `core.md` / `ledger_seed.md`. Provenance: `P.l.NNN`
= `paper.tex` line; `S.l.NNN` = `supplemental.tex` line. Tex labels preserved VERBATIM.
Local env: numpy 1.26.4, scipy 1.17.1 (`scipy.optimize.milp` = HiGHS), sympy 1.12 present.
MISSING: qldpc v1.0.1, ldpc v2.2.0, python-igraph+BLISS, openevolve, litellm.

---

## Build DAG (topological order)

```
                         B0  gf2 / polynomials  (foundation, no deps)
                          |
              +-----------+-----------+
              |                       |
             B1  construction        B8  theorems  (numeric witnesses)
          (bb_codes, pbb_codes)       ^   ^   ^
              |                       |   |   |
        +-----+-----+-----------------+   |   |
        |     |     |                     |   |
       B2    B3 ----+---------------------+   |
    metrics  distance kernel                  |
       |     (MILP CSS/symplectic, enum)      |
       |     |   ^                            |
       |     |   | (B4 feeds B3 only as a    |
       |     |   |  ranking pre-filter)      |
       |    B4  decoders [FUTURE]            |
       |    (BP-OSD)                          |
       |     |                                |
       +--+--+----------------+               |
          |                   |               |
         B6  evaluation       B5  equivalence/structure
         cascade              (tanner, decomposability, BLISS, LC)
          |                   |
          +---------+---------+
                    |
                   B7  evolutionary search  [FUTURE]
                   (MAP-Elites + generator ansatz)
```

DAG edges (depends-on): `B0←{}`; `B1←B0`; `B2←B0,B1`; `B3←B0,B1`; `B4←B1` (FUTURE);
`B5←B0,B1`; `B6←B2,B3,B4`; `B7←B6,B5` (FUTURE); `B8←B0,B1,B3` (with two `[AXIOM]`-conditional
leaves resting on B-external cited papers). No cycles. **B4→B3**: BP-OSD (B4) supplies only a
ranking/upper-bound input consumed inside the cascade (B6) and as a pre-filter for B3's exact
solve; it does NOT block B3 — the exact distance kernel stands alone on scipy/HiGHS.

Critical path to first verified landmark (gross code [[144,12,12]], `lem:crt_k`, `thm:ab_d2`):
**B0 → B1 → {B2, B3, B8}**. This subgraph is fully buildable on the local env (numpy/scipy/sympy,
no MISSING lib). Everything past it (B4 BP-OSD, B5 BLISS dedup, B7 search) needs an external
install or is deliberately deferred.

---

## B0 — GF(2) algebra primitives

- **members**:
  - module `gf2` — F2 linear algebra: rank, kernel/null-space, RREF, solve, matrix product mod 2.
  - module `polynomials` — ring `R = F2[x,y]/(x^l-1, y^m-1)`; trinomial/4-6-term polynomials;
    polynomial↔circulant map; involution `A^T` via `x->x^-1, y->y^-1`; gcd over F2[z]/(z^N-1).
  - ledger: substrate for `PC-02` (F2 rank), `TH-03 css-commute`, `TH-04 pbb-commute`,
    `clm.crt_k` gcd algebra; ground-truth ring `ctx.ring`, `ctx.circ`, `ctx.field`.
- **depends-on**: none (foundation).
- **external libs**: numpy (AVAILABLE), sympy (AVAILABLE, for gcd over F2[z]); NO MISSING lib.
- **exit criteria**:
  - `rank_F2`, `nullspace_F2`, `matmul_mod2` re-verified against a known small case
    (e.g. recompute `rank_F2(H_X)` for gross code => k=12).
  - circulant builder round-trips a trinomial to its `(l*m)x(l*m)` matrix and back; involution
    `A^T` matches the cyclic-shift transpose (`P.l.164` VERBATIM definition).
  - `gcd(f, z^N - 1)` degree matches `macwilliams1977theory` cyclic-kernel identity on a
    spot case (feeds B8/`lem:crt_k`).
- **status marker**: `[HOLE]` — expected evidence `ExactProof` (exact F2 linear algebra),
  re-verifiable numerically. No blocker; highest-priority foundation. Owner: pipeline-1.
- **provenance**: `P.l.158-167` (ring, circulant, involution, k-formula).

## B1 — Code construction (BB + PBB + commutativity)

- **members**:
  - module `bb_codes` — CSS BB: `H_X=(A|B)`, `H_Z=(B^T|A^T)`; `n=2*l*m`; `mdl.css` (`M1`).
  - module `pbb_codes` — non-CSS PBB: `H=[[A,B,C,D],[0,0,B^T,A^T]]`; symplectic `(X|Z)` layout;
    reduces to CSS when `C=D=0`; `mdl.pbb` (`M2`).
  - commutativity guards: `TH-03 css-commute` (`AB+BA=0` over F2, automatic from `R` commutative)
    and `TH-04 pbb-commute` (rows commute IFF `(A C^T + B D^T) mod 2` symmetric over F2 — must be
    checked per-tuple; ~10% of random weight-3 4-tuples at (6,6) pass). `clm.css_commute`,
    `clm.pbb_commute`.
- **depends-on**: B0.
- **external libs**: numpy (AVAILABLE). `qldpc v1.0.1` (MISSING) is the reference builder, but the
  construction is a small cited declaration reproducible in pure numpy (`code_quality_policy` KISS —
  do NOT pull the heavy dep just to build `H_X/H_Z/H`). qldpc is only strictly needed for its
  symplectic logical basis, which is isolated to B3 (`OBL-MILP-2`).
- **exit criteria**:
  - `bb_codes` reproduces gross-code shape and `H_X H_Z^T = 0` over F2 (`css-commute` numeric check).
  - `pbb_codes` builds `H` for a known PBB tuple; `pbb-commute` predicate agrees with direct
    symplectic commutation of all stabilizer rows on a tiny code (e.g. (6,6)).
  - `C=D=0` reduction returns exactly the CSS BB matrices (`P.l.183`).
- **status marker**: `[HOLE]` — `bb_codes` is R2, `pbb_codes` R3 (subtle non-CSS symplectic layout
  + the only-nontrivial commutativity reduction). Evidence `ExactProof` (algebra) + numeric witness.
  Depends on mandatory escalation `sig.bravyi` (arXiv:2308.07915) for the BB definition `[AXIOM]`.
- **provenance**: `P.l.158-183`; `S.l.690` (PBB commutativity / row-flip).

## B2 — Parameters (metrics: k, FOM)

- **members**:
  - module `metrics` — `k = 2*l*m - 2*rank_F2(H_X)` (`PC-02`, EXACT, zero stochasticity; also the
    deterministic ablation metric Σ_k); `FOM = k*d^2/n` (`PC-13`, `ctx.fom`); surface FOM=1, gross
    FOM=12. BPT motivation `kd^2=O(n)` (`bravyi2010tradeoffs`) cited, not re-derived.
- **depends-on**: B0 (rank), B1 (`H_X`); FOM additionally consumes a `d` from B3.
- **external libs**: numpy (AVAILABLE); NO MISSING lib. qldpc reference only.
- **exit criteria**:
  - `k` recomputed from F2 rank equals catalog k for ≥3 landmarks (gross [[144,12,12]] k=12,
    (12,6) univariate k=32, (15,12) univariate k=40 via direct rank — independent of `lem:crt_k`).
  - `FOM` reproduces 12.0 for the gross code; surface-code FOM=1 sanity check.
- **status marker**: `[HOLE]` — `k` is `checked` (`ExactProof`); FOM is `checked` as a defined
  metric (`DimensionalConsistency`). R2 / R0. No blocker.
- **provenance**: `P.l.166-167` (k), `P.l.198-203` (FOM).

## B3 — Distance kernel (exact)

- **members**:
  - module `distance_milp` — CSS MILP (`PC-04`, `clm.milp_css`): per logical j,
    `min Σ x_i` `eq:milp_obj` s.t. `H_Z x ≡ 0` `eq:milp_commute`, `<x,Zbar_j> ≡ 1` `eq:milp_anticommute`,
    `x_i ∈ {0,1}` `eq:milp_binary`; mod-2 linearized via integer slack `Σ a_i x_i - 2s = b`;
    `d = min(d_X,d_Z)`, for BB `d_X=d_Z` by the involution. EXACT iff all 2k MIP gaps = 0; else
    valid upper-bound incumbent. (labels VERBATIM)
  - module `distance_symplectic` — non-CSS PBB MILP (`PC-05`, `clm.milp_pbb`): `min Σ w_i` with
    `w_i = a_i OR b_i` (`w_i>=a_i, w_i>=b_i, w_i<=a_i+b_i`, convex hull tight at integer points),
    `H(a|b)^T ≡ 0` on the symplectic-flipped row order `(s_Z|s_X)`, symplectic anticommute with
    `Lbar_j`; 3n binary vars, ~4x slower. X-first convention.
  - module `enumerate_weight` — Tier-1 exhaustive weight-w syndrome-lookup enumeration (`PC-06`):
    exact within band (d<=6 at n<=216; d<=4 at n>216, ~89GB at n=360).
  - distance-status convention `CL-03` (`clm.cascade` exactness semantics, `OBL-MILP-3`): "exact"
    = all 2k MIP gaps 0; else incumbent upper bound `d <= d_incumbent`, lower bound `d >= d_LB`.
- **depends-on**: B0 (F2 algebra for the constraint rows), B1 (`H_X/H_Z/H`). `distance_symplectic`
  additionally needs a symplectic logical basis `Lbar_j` (the ONE place qldpc is hard to replace).
- **external libs**: `scipy.optimize.milp` = HiGHS (AVAILABLE, scipy 1.17.1) — CSS MILP fully
  runnable now. `qldpc v1.0.1` (MISSING) needed ONLY for `Lbar_j` symplectic Gaussian elimination
  in the non-CSS path → `distance_symplectic` is partial until qldpc installed or `Lbar_j` is
  re-derived in B0/B1.
- **exit criteria**:
  - CSS MILP validated on `bravyi2024high` baselines [[72,12,6]] and [[144,12,12]] to MIP gap=0 for
    every logical (`S.l.693-695`) — discharges the MILP half of `OBL-AXIOM-BRAVYI`.
  - per-logical gap tracking enforced so no incumbent is mislabeled "exact" (`OBL-MILP-3`).
  - OR-hull tightness (4-point check) and the row-flip identity `s_X·b + s_Z·a` proven for the
    symplectic encoding (`S.l.689-690`); symplectic MILP cross-checked vs Tier-1 enumeration on a
    small PBB code ([[36,4,6]] or [[72,4,8]], d<=6, n<=216).
  - landmark distances reproduced exactly: [[144,12,12]] d=12, [[288,16,12]] d=12, [[288,24,12]] d=12.
- **status marker**: `[HOLE]` for CSS (R3, reproducible NOW — top priority verifier);
  `[FUTURE]`/partial for symplectic (R3, blocked on qldpc `Lbar_j`); Tier-1 enum `[FUTURE]` beyond
  memory bound at large n. Evidence: `ExactProof`/`NumericalSimulation` (gap=0) | `ControlledApproximation`
  (incumbent). This bundle is the scientific kernel's admission authority.
- **provenance**: `P.l.319-364`; `S.l.659-691`, `S.l.693-711`; eq labels `S.l.663-666`.

## B4 — Decoders (BP-OSD)  [FUTURE]

- **members**:
  - module `bposd` — in-loop Stage-2 BP-OSD (`PC-03`, `clm.cascade`): stochastic UPPER bound
    `d_true <= d_reported`; ranking signal only, NEVER ground truth.
  - multi-decoder post-hoc protocol (`PC-12`, `clm.bposd_overest`): 3 configs (OSD_0/SP-BP,
    OSD-CS_10/SP-BP, OSD-CS_10/min-sum-BP) × 10×5000 = 150k trials, verified bound = global min over
    30 batches; extended 1.5e6.
  - non-CSS Tier-3 achievable-syndrome sampling (`PC-07`, `clm.achievable_sampling`): per-channel
    GF(2) null-space projection restores decode success ~0%→~100%.
  - overestimation finding `CL-02` (`clm.bposd_overest`): up to 12x overestimate for k/n>0.1.
- **depends-on**: B1 (`H_X/H_Z/H`). Feeds B3 (pre-filter) and B6 (cascade Stage-2), but does NOT
  block them — exact distance comes from B3.
- **external libs**: `ldpc v2.2.0` (MISSING) — BP-OSD decoder. `[BLOCKING]` for any BP-OSD number.
- **exit criteria** (deferred):
  - reproduce a BP-OSD upper bound vs MILP ground truth on one high-rate code (e.g. [[360,40,2]]:
    d_BP<=24 @150k vs MILP true d=2) confirming the overestimation `CL-02`.
  - achievable-subspace dimension count on [[144,12,12]] PBB (Z/Y channels) — note the dimension-k
    claim is `[HOLE]`: observed per-instance, "we have not proved this is general" (`P.l.359`).
- **status marker**: `[FUTURE]` — needs `ldpc` install; verification of catalog *codes* proceeds via
  B3 (MILP) without BP-OSD. Evidence `StatisticalInference` (upper bound) / `EmpiricalMeasurement`
  (overestimation, achievable-subspace). Carries open `[HOLE]` `OBL-ACHSYN-1` (general subspace dim).
- **provenance**: `P.l.249-251, 306-317, 353-360, 670-701`.

## B5 — Equivalence / structure

- **members**:
  - module `tanner` — colored bipartite Tanner graph (`mdl.tanner`, `M3`): CSS qubit c0 / X-check c1
    / Z-check c2; non-CSS per-stabilizer X-support + Z-support vertices (3 colors) with a tying edge.
  - module `bliss_dedup` — BLISS canonical labeling (`PC-09`, `clm.dedup_lc`): permutation-equiv
    IFF canonical forms match; 225→97 CSS (2.3:1, up to 14:1 univariate), 720→368 PBB (1.96:1);
    465 distinct = 97 + 368 is a CONSERVATIVE upper bound (`OBL-BLISS-2`).
  - module `decompose` — Tanner-connectivity direct-sum detection (`PC-10`): disconnected (H_X+H_Z)
    => direct sum; [[288,24,12]] ≅ [[144,12,12]] ⊕ [[144,12,12]], no EC advantage.
  - module `lc_css` — LC-CSS equivalence for PBB (`PC-11`, App E): group-CSS IFF
    `rank[X|Z]=rankX+rankZ` (Lemma 7.4 `cross2025small` `[AXIOM]`); 6 coset reps {I,S,H,HS,SH,HSH};
    Hadamard 2-coloring (parity union-find), affine GF(2) for {I,S}/{H,HS}, 36 uniform per-block.
    11/368 CSS-equiv (10 Hadamard, 1 uniform-S [[36,4,6]]); 357 CSS-inequivalent WITHIN tested families.
- **depends-on**: B0 (GF(2) rank for `lc_css`), B1 (`H_X/H_Z/H` define the graphs).
- **external libs**: `python-igraph` + BLISS (MISSING) — `[BLOCKING]` for the 97/368/465 counts.
  `lc_css` GF(2) rank/affine + parity 2-coloring are pure numpy (AVAILABLE). `decompose`
  connectivity is pure numpy/graph traversal (AVAILABLE).
- **exit criteria**:
  - prove the coloring is faithful (colored-graph automorphism group = admissible code permutations;
    non-CSS tying edge forbids cross-class permutation) — short combinatorial argument, write it out
    (`OBL-BLISS-1`); reproduce 225→97 and 720→368.
  - `decompose` flags [[288,24,12]] as decomposable and confirms the two gross-code summands;
    runnable now (no MISSING lib).
  - `lc_css` reproduces the 11 positive reductions (10 Hadamard, 1 uniform-S) and the 357 count;
    record residual gaps (a) non-uniform {SH,HSH} on block 1, (b) cross-class — left as `[HOLE]`.
- **status marker**: `[FUTURE]` for `bliss_dedup` (needs igraph); `[HOLE]` for `decompose` and
  `lc_css` (runnable now). `lc_css` is `conditional` on Lemma 7.4 `[AXIOM]` and carries `[HOLE]`
  coverage gaps (357 holds only "within tested LC families"). R2 / R3. Evidence
  `SymbolicDerivation`/`ExactProof` (canonical form, rank, 2-coloring) + `NumericalSimulation` (p_L match).
- **provenance**: `P.l.185-194, 380-394, 426-434, 1026-1087`.

## B6 — Evaluation cascade

- **members**:
  - module `cascade` (`V3`, `clm.cascade`): Stage-1 (~2s) k-only F2 rank on (6,6),(12,6), discards
    ~30% of mutants; Stage-2 (~30-60s) BP-OSD distance on 8 lattices {(12,6),(6,12),(12,12),(24,6),
    (15,12),(30,6),(16,9),(18,8)}, top-10 by k-diversity get 1000 OSD_0, FOM>=6 get +3×500;
    Stage-3 MILP exact (in-loop C4-5, post-hoc C1-3).
  - module `trust_filter` (`PC-08`): `d/sqrt(n) <= 1.3` trusted, `>= 2.0` discarded, linear between;
    KNOWN-IMPERFECT (operates on the same unreliable BP-OSD it should catch). Counterexample
    [[360,40,2]] passed at d_BP/sqrt(n)=1.26 vs true 0.11. C5 bypasses it.
- **depends-on**: B2 (k, FOM gating), B3 (Stage-3 MILP — the admission authority), B4 (Stage-2 BP-OSD
  ranking — FUTURE; cascade is partial without it but Stage-1/Stage-3 still run).
- **external libs**: numpy + scipy (AVAILABLE) for Stage-1/Stage-3; `ldpc` (MISSING) for Stage-2.
- **exit criteria**:
  - Stage-1 reproduces the ~30% discard rate on a sampled mutant population (or documents the
    population it was measured on).
  - end-to-end: a candidate tuple flows Stage-1 (k>0) → Stage-3 (exact d via B3) and emits a typed
    catalog row with the `CL-03` exactness label. Stage-2 stubbed/skipped until B4.
  - `trust_filter` reproduces the [[360,40,2]] counterexample (admit it as a documented failure mode,
    NOT a reliable filter).
- **status marker**: `[FUTURE]` (full cascade needs B4 BP-OSD); `[HOLE]` for the Stage-1+Stage-3
  MILP-only path (runnable now). `trust_filter` is `approximate` (refuted as reliable; soft heuristic
  only). The agentic-lean invariant lives here: "the LLM proposes; the kernel admits."
- **provenance**: `P.l.246-258, 366-371`.

## B7 — Evolutionary search (MAP-Elites + ansatz)  [FUTURE]

- **members**:
  - module `search` (`PC-01`, `mdl.mapelites`, `M4`): evolve a generator ANSATZ `G(l,m) -> {(A_i,B_i)}`
    (4-tuples for PBB) — a Python program, not an individual code; LLM proposes targeted code diffs;
    4-6 islands, migration every 12-25 iters; MAP-Elites dims = (#lattices with k>=8 codes, total such
    codes); C4 dims = (term count, monomial structure). 5 campaigns, ~1650 iters, ~2e5 candidates,
    ~140h, ~US$400.
  - carries NO admission authority — every candidate is admitted only by B6→B3.
- **depends-on**: B6 (the cascade is the fitness/admission gate), B5 (dedup/structure for the archive
  behavioral dims and the distinct-code bookkeeping).
- **external libs**: `openevolve` + `litellm` + LLM API access (all MISSING). `[FUTURE]`.
- **exit criteria** (deferred — out of scope for verification; the *codes* are the deliverable, not the
  search trajectory, `OBL-ENV-3`):
  - re-deriving the discovered codes does NOT require this bundle — it requires only B1 (construct) +
    B3 (verify). A scaffolded loop is the deliverable; the ralph loop then runs the campaigns.
- **status marker**: `[FUTURE]` — deliberately deferred; needs the full LLM/search install + budget.
  Evidence `EmpiricalMeasurement` (stochastic, LLM-dependent). The loop is the proposal mechanism, not
  a verifier; no formal guarantee of output validity.
- **provenance**: `P.l.217-300`; libs `P.l.280-282`.

## B8 — Theorems (numeric witnesses)

- **members**:
  - `TH-01 thm:ab_d2` (`clm.ab_d2`, App D): every BB code with `A=B`, `k>0` has `d=2` exactly.
    Proof present (diagonal-subspace + `rank(A)<lm` argument); CSS case reproducible by F2 rank
    (B0) — no MISSING lib. PBB extension `clm.ab_d2_pbb` needs B3 MILP to confirm the weight-2
    operator is not a stabilizer (`[HOLE]`: general "every A=B PBB has d=2" only certified per-catalog).
  - `TH-02 lem:crt_k` (`clm.crt_k`, App C): `A=1+y+y^2`, `B=A(x^c)`, `c=l/3`, `3|l,3|m` => `k=8l/3`.
    Proof = gcd/divisibility algebra (B0 + sympy), CONDITIONAL on `TH-AXIOM-TZ` HGP-dim formula
    `[AXIOM]` and `macwilliams1977theory` cyclic identity `[AXIOM]`.
  - `TH-03 css-commute`, `TH-04 pbb-commute` — algebraic commutation identities (built/tested in B1).
  - `TH-AXIOM-TZ` `tillich2014quantum` (`clm.tz_distance`): HGP distance `d=min(d1,d2,d1^T,d2^T)`;
    univariate BB codes all have `d ∈ {2,4}`. Imported postulate `[AXIOM]` — final univariate-distance
    claims remain conditional on it.
  - `CL-01` rate-distance tradeoff (`clm` conjectural): wt6 k>24 => d<=4; wt8 reaches k=50 d=8.
    OPEN whether structural or search artifact (`OBL-TRADEOFF-1`) — NEVER render as a theorem.
- **depends-on**: B0 (F2 rank / gcd for the witnesses), B1 (`A=B` construction, `H_X`),
  B3 (MILP `d=2` corroboration for `thm:ab_d2`; PBB extension; univariate `d∈{2,4}`).
- **external libs**: numpy + sympy + scipy (AVAILABLE). `TH-AXIOM-TZ` rests on the cited
  `tillich2014quantum` (treat as `[AXIOM]`); `lem:crt_k` k-value also independently checkable by
  direct F2 rank (B0) without the formula. `bravyi2024high` `[AXIOM]` underpins the BB definition.
- **exit criteria**:
  - `thm:ab_d2`: F2-rank witness on a catalog A=B code (e.g. [[144,32,2]], 16 independent weight-2
    logicals, `S.l.692`) reproduces d=2; MILP (B3) corroborates in <1s.
  - `lem:crt_k`: re-derive `k_A=k_A^T=2`, `k_B=k_B^T=2l/3` via gcd; spot-check `k=8l/3` by direct
    F2 rank on (12,6)=>k=32 and (15,12)=>k=40 (independent of the HGP formula).
  - `css-commute`/`pbb-commute` numeric identity checks (shared with B1 exit).
  - `CL-01` recorded as `Conjectural`; only the finite searched data points are re-confirmed.
- **status marker**: `thm:ab_d2` `[PRELIMINARY]`→`checked` on CSS witness (PBB extension `[HOLE]`);
  `lem:crt_k` `[SOLID]` conditional on `[AXIOM]`s, numerically corroborated (1680 combos lm<=250);
  `css-commute`/`pbb-commute` `checked`; `TH-AXIOM-TZ` `[AXIOM]`; `CL-01` `Conjectural` `[HOLE]`/`[FUTURE]`.
  Evidence `ExactProof`/`SymbolicDerivation` + `NumericalSimulation` witnesses.
- **provenance**: `P.l.408-411, 533-560, 956-980, 982-1024`; labels `thm:ab_d2`, `lem:crt_k` VERBATIM.

---

## Bundle status summary

| Bundle | Members (modules) | Depends-on | External lib | Runnable now? | Status |
|---|---|---|---|---|---|
| B0 | gf2, polynomials | — | numpy, sympy (AVAIL) | YES | `[HOLE]` |
| B1 | bb_codes, pbb_codes (+commute) | B0 | numpy (AVAIL); qldpc ref | YES | `[HOLE]` |
| B2 | metrics (k, FOM) | B0, B1 | numpy (AVAIL) | YES | `[HOLE]` |
| B3 | distance_milp, distance_symplectic, enumerate_weight | B0, B1 | scipy/HiGHS (AVAIL); **qldpc MISSING** (Lbar_j) | CSS YES / symplectic partial | `[HOLE]` (CSS) / `[FUTURE]` (symp) |
| B4 | bposd (in-loop, multi-decoder, achievable) | B1 (→B3,B6) | **ldpc MISSING** | NO | `[FUTURE]` |
| B5 | tanner, bliss_dedup, decompose, lc_css | B0, B1 | **igraph+BLISS MISSING** (BLISS only) | dedup NO / decompose+lc_css YES | `[FUTURE]` (BLISS) / `[HOLE]` (rest) |
| B6 | cascade, trust_filter | B2, B3, B4 | scipy (AVAIL); ldpc for Stage-2 | Stage1+3 YES / full NO | `[FUTURE]` (full) / `[HOLE]` (MILP-only) |
| B7 | search (MAP-Elites + ansatz) | B6, B5 | **openevolve+litellm MISSING** | NO | `[FUTURE]` |
| B8 | thm:ab_d2, lem:crt_k, css/pbb-commute, TH-AXIOM-TZ, CL-01 | B0, B1, B3 | numpy/sympy/scipy (AVAIL); tillich/bravyi `[AXIOM]` | YES (conditional) | mixed (see B8) |

**Buildable-now subgraph** (no MISSING lib): B0, B1, B2, B3-CSS, B5-{decompose,lc_css}, B6-MILP-path,
B8. **Blocked subgraph**: B3-symplectic + B8-PBB-extension (qldpc `Lbar_j`), B4 (ldpc),
B5-BLISS (igraph), B6-full (ldpc), B7 (openevolve+litellm).

**Mandatory escalation**: `sig.bravyi` arXiv:2308.07915 (BB definition + MILP baseline) underpins
B1 and B3 — single mandatory dependency-paper read.

**Open `[HOLE]`/`[FUTURE]` carried by bundles** (cross-ref `obligations.md`): B3/B8 PBB A=B-trap
generality (`OBL-THM-1`, `OBL-MILP-2`); B4 achievable-subspace general dimension (`OBL-ACHSYN-1`);
B5 LC coverage gaps (a),(b) (`OBL-LC-1`) + BLISS faithfulness proof (`OBL-BLISS-1`); B6 trust-filter
refuted-as-reliable (`PC-08` counterexample); B8 rate-distance tradeoff structural-vs-artifact
(`OBL-TRADEOFF-1`, Conjectural). `[AXIOM]`s: `tillich2014quantum`, `cross2025small` Lemma 7.4,
`macwilliams1977theory`, `bravyi2024high`.
