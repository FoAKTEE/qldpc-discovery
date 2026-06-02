# Theorem Logical-Dependency Plan — arXiv:2606.02418

Proof-target dependency graph for the reproduction of "Evolutionary Discovery of Bivariate Bicycle
Codes with LLM-Guided Search" (Cruz-Benito, Cross, Kremer, Faro). Each row is a TYPED ledger entry
per `_common/agentic_lean_contract.md`: it carries `label`, `statement`, `predecessors`,
`target_path`, `signature_sketch`, `modality`, `risk_tier`, `evidence_citation`, `status`.

Scope: the **theorems** (`thm:ab_d2`, `lem:crt_k`), the **commutativity conditions**
(`css-commute`, `pbb-commute`), the **cited distance axiom** (`tillich-zemor`), and the
**verification-correctness obligations** that the kernel's admission gates rely on
(`MILP-CSS-correct`, `MILP-symplectic-correct`, `BLISS-permutation-sound`,
`decomposability=>direct-sum`, `Hadamard-2coloring-sound`, `LC-rank-condition`).

Discipline:
- Default modality `LiteratureGrounded`; `ExactProof`/`SymbolicDerivation` only where the paper gives
  a complete proof we can elaborate; cited-but-not-reproduced results are `[AXIOM]`.
- Markers per `_common/markers.md`. Every loose end carries a marker.
- Tex labels (`thm:ab_d2`, `lem:crt_k`, `eq:milp_obj`, …) preserved VERBATIM.
- Provenance format: `P.l.NNN` = `paper.tex` line N; `S.l.NNN` = `supplemental.tex` line N
  (in `/data/haiyangw/claude/qldpc-discovery/ref-paper/arxiv-2606.02418/src/`).
- `target_path` is relative to `/data/haiyangw/claude/qldpc-discovery/`. Modules that already exist
  are marked `(exists)`; modules to be created are marked `(NEW)`.

Risk tiers (per `code_quality_policy.md` RISK TIERS, reinterpreted for a math-verification kernel):
- **R1** — isolated helper / direct numeric check of a complete elementary proof.
- **R2** — normal correctness obligation; multi-lens review (an encoding or reduction the whole
  pipeline trusts).
- **R3** — admission-gate-critical: a soundness claim the kernel uses to *admit* codes into the
  catalog (a bug here silently corrupts the 465-code count or a reported distance). Independent
  multi-agent + adversarial lens required.

---

## 1. Proof-target dependency table

| label | statement | predecessors | target_path | signature_sketch | modality | risk_tier | evidence_citation | status |
|---|---|---|---|---|---|---|---|---|
| `css-commute` | A BB code `H_X=(A\|B)`, `H_Z=(B^T\|A^T)` is a valid CSS code iff `H_X H_Z^T = AB + BA = 0` over F2; this holds automatically because `R = F2[x,y]/(x^l-1,y^m-1)` is commutative (circulants `A,B` commute). | (none — foundational; ring-commutativity axiom) | `src/qcode_discovery/bb_codes.py` (exists) | `BBCode._validate_css(self) -> None` (raises if `(A@B + B@A) % 2 != 0`) | `SymbolicDerivation` | R2 | P.l.160–167 (`sec:bb`) | `[SOLID]` (one-line algebra; numeric check is `assert ((A@B+B@A)%2==0)` for every catalog `(A,B)`) |
| `pbb-commute` | A PBB code `H=[[A,B,C,D],[0,0,B^T,A^T]]` has all stabilizer rows pairwise commuting iff `(A C^T + B D^T) mod 2` is symmetric over F2. Block-1↔block-2 commutation is automatic from BB ring commutativity; the symmetry of `A C^T + B D^T` is the only nontrivial condition and must be checked computationally per tuple (~10% of random weight-3 4-tuples at (6,6) satisfy it). | `css-commute` (specializes to it when `C=D=0`) | `src/qcode_discovery/pbb_codes.py` (exists) | `PBBCode.reduced_condition_symmetric(self) -> bool`; cross-checked by `PBBCode.symplectic_gram_zero(self) -> bool` | `SymbolicDerivation` | R2 | P.l.174–183 (`sec:pbb`); S.l.690 | `[SOLID]` (derivation given; numeric: `M = (A@C.T + B@D.T)%2; M==M.T`. Cross-check via full symplectic Gram = 0) |
| `tillich-zemor` | HGP code `HGP(H1,H2)` from classical codes with parameters `(k1,k1^T)`, `(k2,k2^T)` encodes `k = k1 k2 + k1^T k2^T` qubits; its distance is `d = min(d1, d2, d1^T, d2^T)`; univariate (single-variable) BB/HGP codes therefore have `d ∈ {2,4}`. | (none — CITED external result, treat as imported postulate) | `src/qcode_discovery/theorems.py` (exists; consumes the `k` half) | (no own impl; `verify_crt_k` *uses* the `k` formula) — optional `hgp_k_formula(k1, k1T, k2, k2T) -> int` | `LiteratureGrounded` | R1 (we only consume it) | P.l.1015 (`tillich2014quantum` cited in `lem:crt_k` proof); univariate `d∈{2,4}` P.l.378–419, S.l.244–259 | `[AXIOM]` (cited `tillich2014quantum`; not re-derived. All results depending on it stay conditional) |
| `lem:crt_k` | For `3\|l`, `3\|m`, `c=l/3`, the BB code `A(y)=1+y+y^2`, `B(x)=A(x^c)=1+x^c+x^{2c}` is `HGP(H_B, H_A^T)` and encodes `k = 8l/3` logical qubits (independent of `m`). Proof: `BB(A,B) ≅ HGP(H_B,H_A^T)` (block swap); `k = k_B k_A^T + k_B^T k_A = 2·(2l/3)·2 = 8l/3`, using the cyclic-code identity `dim ker H = deg gcd(f, z^N−1)` (`macwilliams1977theory`) ⇒ `k_A=k_A^T=deg A=2`, `k_B=k_B^T=deg B=2l/3`. | `tillich-zemor` (the `k = k1 k2 + k1^T k2^T` formula); `css-commute` (BB validity) | `src/qcode_discovery/theorems.py` (exists) | `verify_crt_k(l: int, m: int) -> dict` (returns `{l,m,n,k,expected,match}`; raises unless `3\|l and 3\|m`) | `SymbolicDerivation` (proof) + `NumericalSimulation` (the 1680-combo `lm<=250` sweep) | R2 | P.l.982–1024 (`app:crt`, `lem:crt_k`); verified-1680-combos asserted P.l.378–419 / S.l.244–259 | `[SOLID]` proof; numeric `k=8l/3` re-verifiable per lattice. Distance claim `d∈{2,4}` rides on `tillich-zemor` ⇒ `[AXIOM]`-conditional |
| `thm:ab_d2` | Every BB code with `A = B` and `k > 0` has `d = 2` exactly. Proof: rowspace(H_X)⊆ diagonal subspace `S={(w,w)}`; `v_i=(e_i,e_i)∈ker(H_Z)` and is an X-stab iff `e_i∈rowspace(A)`; `k>0 ⇒ rank(A)<lm` ⇒ some `e_i` outside ⇒ weight-2 X-logical ⇒ `d_X≤2` (symmetric arg ⇒ `d_Z≤2`); polynomial weight ≥2 ⇒ every column weight ≥2 ⇒ `d≥2`; hence `d=2`. Holds for any check weight ≥2. Extends to PBB: `l m` weight-2 Z-operators `(0\|e_i+e_{i+lm})` lie in `N(S)`; MILP confirms non-stabilizer ⇒ `d=2` for all `A=B` PBB catalog entries. | `css-commute` (BB validity, `k` formula); for the PBB extension also `pbb-commute` and `MILP-symplectic-correct` (the "not a stabilizer" check) | `src/qcode_discovery/theorems.py` (exists) | `verify_ab_d2(l: int, m: int, A) -> dict` (constructs `A=B` code, exhibits a concrete weight-2 X-logical, returns witness `e_i ∉ rowspace(A)`, `k`, `d_upper=2`) | `ExactProof` (CSS); `SymbolicDerivation` + `NumericalSimulation` (PBB extension via MILP) | R2 | P.l.955–981 (`app:ab_trap`, `thm:ab_d2`); BP-OSD failure context P.l.205–211, P.l.692; MILP `d=2` S.l.698 | `[SOLID]` (CSS proof elementary, witness constructible & checkable). PBB extension `[PRELIMINARY]` — "not a stabilizer" leans on `MILP-symplectic-correct` |
| `MILP-CSS-correct` | The binary program `min Σx_i` s.t. `H_Z x ≡ 0 (mod 2)`, `⟨x, Zbar_j⟩ ≡ 1 (mod 2)`, `x∈{0,1}` returns the minimum Hamming weight of an X-logical anticommuting with `Zbar_j`; mod-2 rows linearized by integer slack `Σ a_i x_i − 2s = b`, `s∈Z≥0`. Code distance `d=min(d_X,d_Z)` over all `2k` logicals; for BB `d_X=d_Z` (involution `x↦x^{-1},y↦y^{-1}`). A solution is **exact** iff HiGHS reports MIP gap = 0; otherwise a valid upper bound. | `css-commute` (defines `H_X,H_Z`, logical bases) | `src/qcode_discovery/distance_milp.py` (exists) | `css_distance_milp(code, time_limit=60.0, which="both", max_logicals=None) -> dict`; internal `_min_weight_logical(check, target, time_limit) -> (weight, optimal)` | `ExactProof` (encoding correctness) + `NumericalSimulation` (HiGHS solve; exact only at gap=0) | **R3** | S.l.659–674 (`sm:milp` CSS), `eq:milp_obj`/`eq:milp_commute`/`eq:milp_anticommute`/`eq:milp_binary` S.l.663–666; P.l.319–337 (`sec:milp`); validation `[[72,12,6]]`,`[[144,12,12]]` S.l.695 | `[SOLID]` encoding (slack linearization is standard & elementary); each reported **exact** distance carries its own `gap=0` certificate. Incumbent-only solves stay `[AXIOM]`-grade upper bounds. Admission-gate critical |
| `MILP-symplectic-correct` | Non-CSS distance MILP: `min Σ w_i` s.t. `H·(a\|b)^T ≡ 0 (mod 2)`, `⟨(a\|b), Lbar_j⟩_symp ≡ 1 (mod 2)`, `w_i = a_i OR b_i` encoded as `w_i≥a_i, w_i≥b_i, w_i≤a_i+b_i` (convex hull of the 4 feasible `(a_i,b_i,w_i)` triples, tight at integer points); `a_i,b_i,w_i∈{0,1}`. `H` is the symplectic-flipped matrix: stabilizer `(s_X\|s_Z)` stored as `(s_Z\|s_X)` so `H·(a\|b)^T` computes the symplectic inner products (X-first convention). `3n` binary vars; ~4× slower than CSS X-distance. | `pbb-commute` (defines `H`, symplectic structure); reuses the slack/gap machinery of `MILP-CSS-correct` | `src/qcode_discovery/distance_milp.py` (exists; symplectic path is `(NEW)` within it) | `symplectic_distance_milp(code, time_limit=60.0, max_logicals=None) -> dict` `(NEW)`; needs symplectic logical basis `Lbar_j` from `qldpc` GE (or local GF(2) symplectic GE) | `ExactProof` (OR-encoding + row-flip correctness) + `NumericalSimulation` (HiGHS) | **R3** | S.l.676–691 (`sm:milp` non-CSS); 3n vars / ~4× S.l.691; reduces to `pbb-commute` S.l.690; Tier-2 P.l.348–351 | `[PRELIMINARY]` — OR-hull and `(s_Z\|s_X)` row-flip are checkable by hand; blocked on a symplectic logical basis (needs `qldpc` GE or a local symplectic-GE `[HOLE]`). Admission-gate critical |
| `decomposability=>direct-sum` | If the combined Tanner graph of `H_X` and `H_Z` (qubits + all checks) is **disconnected**, the code is a direct sum of the sub-codes on each component: a logical supported on ≥2 components restricts to a logical on each (stabilizers on other components act trivially), so `[[n,k,d]] ≅ ⊕_c [[n_c,k_c,d_c]]`. Concretely `[[288,24,12]] ≅ [[144,12,12]] ⊕ [[144,12,12]]` (even/odd `x`-index cosets); BLISS confirms the `(12,12)` and `(24,6)` representations are the *same* direct sum. | `css-commute` (the `H_X,H_Z` whose Tanner graph is analyzed); `BLISS-permutation-sound` (only for the "same direct sum across lattices" corollary) | `src/qcode_discovery/tanner.py` (exists) | `qubit_components(HX, HZ) -> int`; `is_decomposable(code) -> bool` (= `qubit_components > 1`) | `ExactProof` (graph connectivity ⇒ direct-sum is a complete elementary argument) | R2 | P.l.426–434 (`sec:families`); pipeline-capability framing P.l.100, P.l.239 | `[SOLID]` — restriction argument is complete; connectivity is exact (union-find). The specific `[[288,24,12]]` split is numerically reproducible |
| `BLISS-permutation-sound` | Two codes are permutation-equivalent (qubit relabeling preserving X/Z-stabilizer roles) **iff** their colored-Tanner-graph BLISS canonical forms are identical. CSS coloring: qubits=c0, X-checks=c1, Z-checks=c2. Non-CSS coloring: qubits + per-stabilizer X-support vertex + per-stabilizer Z-support vertex (3 colors), with a tying edge per stabilizer linking its X- and Z-support vertices to forbid independent permutation of the two check classes. Sound & complete *for permutation equivalence under the respective coloring*; the 465 = 97 CSS + 368 PBB count is a conservative upper bound under any coarser equivalence. | `css-commute` (CSS Tanner graph); `pbb-commute` (non-CSS stabilizer X/Z supports) | `src/qcode_discovery/bliss_dedup.py` `(NEW)` | `colored_tanner_css(HX, HZ) -> igraph.Graph`; `colored_tanner_pbb(H, n) -> igraph.Graph`; `bliss_canonical(g) -> bytes`; `dedup_codes(codes) -> list[int]` (returns rep indices) | `ExactProof` (the iff is the definition of the equivalence; BLISS canonical form is exact) | **R3** | P.l.380–393 (`sec:results` dedup); 225→97 P.l.386, 720→368 P.l.386; conservative-upper-bound P.l.388–393; lib P.l.280–282 (`junttila2007engineering`) | `[HOLE]` — module is `(NEW)`; **blocked on `python-igraph`+BLISS** (`OBL-ENV-2`). Until installed, the 97/368/465 counts are `[AXIOM]` (cited, not reproduced). Admission-gate critical |
| `Hadamard-2coloring-sound` | A stabilizer code's supplied generators are simultaneously made pure-X or pure-Z by some single-qubit-Hadamard pattern `H_J` **iff** (a) no generator has Y support, AND (b) the parity constraint graph is bipartite (2-colorable). Constraints: on qubit `j∈supp(g_r)` with local type `t_{rj}∈{0,1}` and target type `c_r`, need `s_j = c_r ⊕ t_{rj}`; two generators on the same qubit force `c_{r1} ⊕ c_{r2} = t_{r1,j} ⊕ t_{r2,j}`. Decidable in linear time by union-find with parity. Sound & complete **at the level of the supplied generators** (a True result yields an explicit `H_J`; a False result rules out any `H_J` for those generators). Identifies 10 of the 210 no-Y PBB codes as Hadamard-CSS. | `pbb-commute` (the stabilizer generators / their X,Z supports) | `src/qcode_discovery/clifford_equiv.py` `(NEW)` | `hadamard_two_coloring(stab_xz) -> dict` (returns `{feasible: bool, H_pattern: np.ndarray\|None, y_obstruction: bool}`); reuses parity union-find pattern of `tanner._UnionFind` | `ExactProof` (the iff + linear-time decision are fully derived in App. E) | R2 | P.l.189–190 (`sec:pbb` summary); P.l.1042–1052 (`app:lc` Hadamard 2-coloring); inspired by `khesin2026mirror` P.l.1043; 10 codes P.l.1081 | `[PRELIMINARY]` — proof is complete & elementary; module `(NEW)`. Independent of `igraph`. Caveat: soundness is *generator-level*, not group-level (group-level deferred to `LC-rank-condition`) |
| `LC-rank-condition` | A stabilizer group `S` is CSS **iff** `rank[X\|Z] = rank X + rank Z` over GF(2) (Lemma 7.4 of `cross2025small`, attr. T. Yoder). Used to test LC-CSS-equivalence by: (1) enumerating the 36 uniform per-block assignments from the 6 Clifford coset reps `{I,S,H,HS,SH,HSH}` and applying the rank condition to each conjugated group; (2) solving the exact GF(2) affine system for non-uniform `{I,S}` and `{H,HS}` patterns (`w·row_g = 0` for `w` in the orthogonal complement of `rowspan([B^T\|A^T])`). Result: of 368 PBB codes, exactly 1 (`[[36,4,6]]`) is LC-CSS via uniform `S`; 10 more via non-uniform `H` (the `Hadamard-2coloring-sound` path); 357 CSS-inequivalent within tested LC families (documented coverage gaps (a),(b): non-uniform `{SH,HSH}` on block 1, and cross-class non-uniform patterns). | `pbb-commute` (stabilizer matrix `[X\|Z]`); `Hadamard-2coloring-sound` (covers the non-uniform `{I,H}` family, complementary to the `{I,S}`/`{H,HS}` affine systems); `tillich-zemor` not required | `src/qcode_discovery/clifford_equiv.py` `(NEW)` | `is_css_group(stab_xz) -> bool` (the rank test; already stubbed as `PBBCode.is_css_group`); `lc_css_equivalent(code) -> dict` (returns `{css: bool, pattern: str, family: str, gap_note: str}`) | `LiteratureGrounded` (Lemma 7.4 imported) + `ExactProof` (the GF(2) rank tests we run) | **R3** | P.l.189–193 (`sec:pbb`); P.l.1026–1086 (`app:lc`); Lemma 7.4 P.l.1036; 6 reps P.l.1040; 36 uniform + affine P.l.1054–1067; gaps P.l.1069–1076; 11/368 result P.l.1078–1083 | `[AXIOM]` for Lemma 7.4 (cited `cross2025small`, not re-proven) + `[HOLE]` for the enumeration module `(NEW)`. The 357 count is explicitly *not* "genuinely non-CSS" — coverage gaps (a),(b) remain `[FUTURE]` (no GF(2) reduction; `6^n` brute force infeasible at `n≥36`). Admission-gate critical for the CSS/non-CSS partition |

---

## 2. Predecessor edge list (machine-readable)

`label -> [predecessors]`. Predecessors are other rows in this table OR named axioms.
Axiom nodes (no incoming edges, imported postulates): `ring-commutative-F2`, `cross2025small-Lemma7.4`,
`tillich-zemor`. A topological order for the loop is given in §3.

```yaml
# theorem dependency DAG — arXiv:2606.02418
edges:
  ring-commutative-F2: []                         # AXIOM: R = F2[x,y]/(x^l-1,y^m-1) commutative
  tillich-zemor: []                               # AXIOM: cited tillich2014quantum (HGP k & d)
  cross2025small-Lemma7.4: []                     # AXIOM: cited cross2025small (CSS-group rank iff)

  css-commute: [ring-commutative-F2]
  pbb-commute: [css-commute]

  lem:crt_k: [tillich-zemor, css-commute]
  thm:ab_d2: [css-commute, pbb-commute, MILP-symplectic-correct]   # PBB-extension edges only

  MILP-CSS-correct: [css-commute]
  MILP-symplectic-correct: [pbb-commute, MILP-CSS-correct]         # reuses slack/gap machinery
  decomposability=>direct-sum: [css-commute, BLISS-permutation-sound]  # BLISS only for cross-lattice "same sum"
  BLISS-permutation-sound: [css-commute, pbb-commute]
  Hadamard-2coloring-sound: [pbb-commute]
  LC-rank-condition: [pbb-commute, Hadamard-2coloring-sound, cross2025small-Lemma7.4]
```

Notes on edge subtleties:
- `thm:ab_d2` CSS proof needs ONLY `css-commute`; the `MILP-symplectic-correct` edge applies solely
  to the PBB extension ("whenever any such operator is not itself a stabilizer element---as verified
  by MILP"). If only the CSS theorem is in scope, drop that edge.
- `decomposability=>direct-sum` is self-contained (graph connectivity ⇒ direct sum); the
  `BLISS-permutation-sound` edge is needed only for the corollary that the `(12,12)` and `(24,6)`
  representations are the *same* direct sum.
- `lem:crt_k`'s **k** claim depends on `tillich-zemor`'s k-formula; its **distance** corollary
  (`d∈{2,4}` for univariate) additionally inherits `tillich-zemor`'s distance axiom and stays
  conditional on that `[AXIOM]`.

---

## 3. Topological build order (for the elaboration loop)

1. `css-commute` — R2, exists (`bb_codes.py`). Numeric assert over the catalog. → unblocks everything.
2. `pbb-commute` — R2, exists (`pbb_codes.py`). → unblocks PBB chain.
3. `MILP-CSS-correct` — **R3**, exists (`distance_milp.py`). Validate on `[[72,12,6]]`, `[[144,12,12]]`.
4. `decomposability=>direct-sum` — R2, exists (`tanner.py`). Reproduce `[[288,24,12]]` split.
5. `lem:crt_k` — R2, exists (`theorems.py`). Sweep `lm<=250`, `3|l, 3|m`; assert `k=8l/3`.
6. `thm:ab_d2` (CSS) — R2, exists (`theorems.py`). Exhibit witness `e_i ∉ rowspace(A)`.
7. `MILP-symplectic-correct` — **R3**, `(NEW)` path in `distance_milp.py`. Needs symplectic logical basis.
8. `thm:ab_d2` (PBB extension) — depends on step 7.
9. `Hadamard-2coloring-sound` — R2, `(NEW)` `clifford_equiv.py`. No external lib; parity union-find.
10. `LC-rank-condition` — **R3**, `(NEW)` `clifford_equiv.py`. Reproduce the 1 + 10 + 357 partition.
11. `BLISS-permutation-sound` — **R3**, `(NEW)` `bliss_dedup.py`. **BLOCKED on `python-igraph`+BLISS**
    (`OBL-ENV-2`). Reproduce 225→97, 720→368, total 465.

`tillich-zemor` and `cross2025small-Lemma7.4` are never "built" — they are imported `[AXIOM]`s;
all dependents remain conditional on them.

---

## 4. Status roll-up

| status marker | rows |
|---|---|
| `[SOLID]` | `css-commute`, `pbb-commute`, `lem:crt_k` (k-claim), `thm:ab_d2` (CSS), `MILP-CSS-correct` (encoding), `decomposability=>direct-sum` |
| `[PRELIMINARY]` | `MILP-symplectic-correct` (needs symplectic logical basis), `thm:ab_d2` (PBB extension), `Hadamard-2coloring-sound` (module NEW) |
| `[AXIOM]` (imported, results stay conditional) | `tillich-zemor`, `cross2025small-Lemma7.4` (inside `LC-rank-condition`) |
| `[HOLE]` (module NEW / dependency missing) | `BLISS-permutation-sound` (needs `python-igraph`), `LC-rank-condition` (enumeration NEW) |
| `[FUTURE]` (deliberately deferred) | `LC-rank-condition` coverage gaps (a) non-uniform `{SH,HSH}` on block 1, (b) cross-class non-uniform patterns — no GF(2) reduction, `6^n` brute force infeasible at `n≥36` |

**Admission-gate-critical (R3) rows** — a bug here silently corrupts the catalog: `MILP-CSS-correct`,
`MILP-symplectic-correct`, `BLISS-permutation-sound`, `LC-rank-condition`. These require independent
multi-agent + adversarial review per `code_quality_policy.md`, and every "exact" distance must ship
its own `gap=0` certificate (never promote an incumbent upper bound to an exact theorem).
