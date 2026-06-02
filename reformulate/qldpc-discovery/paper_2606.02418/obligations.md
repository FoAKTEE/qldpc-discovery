# Obligations — Reproduction of arXiv:2606.02418

Typed `[HOLE]` / `[BLOCKING]` / `[AXIOM]` obligations that the reproduction must discharge.
Each is a ledger entry per `_common/agentic_lean_contract.md`: `context`, `claim`, expected `type`,
required evidence `modality`, `dependencies`, `status` marker, and **what unblocks it**.

Marker vocabulary: see `_common/markers.md`. Default modality `LiteratureGrounded` unless a
proof/derivation is present. Cited-but-not-reproduced results are `[AXIOM]`; results the authors
explicitly state they did **not** prove remain `[HOLE]` with the gap surfaced.

Paper anchors are `paper.tex` / `supplemental.tex` line ranges in
`/data/haiyangw/claude/qldpc-discovery/ref-paper/arxiv-2606.02418/src/`. Tex labels (`thm:ab_d2`,
`lem:crt_k`, `eq:milp_obj`, `sec:tradeoff`, …) are preserved VERBATIM.

---

## 1. Environment / missing libraries (infrastructure HOLEs)

### OBL-ENV-1 — `ldpc` BP-OSD decoder absent
- **context**: Stage-2 cascade + all BP-OSD overestimation findings (`sec:bposd_limits` l.307–317;
  `sec:bposd_findings` l.671–700; SM `sm:decoders`, `sm:per_batch`, `sm:tightening`).
- **claim**: BP-OSD distance bounding and the 150k/1.5M-trial multi-decoder protocol
  (OSD$_0$ sum-product; OSD-CS$_{10}$ sum-product; OSD-CS$_{10}$ min-sum) can be re-run.
- **type**: ReproductionArtifact (executable). **modality**: `NumericalSimulation` (stochastic upper bounds).
- **dependencies**: `ldpc v2.2.0` (`ldpc_library`, l.127); `numpy`.
- **status**: `[BLOCKING]` for any BP-OSD vs MILP comparison; `[HOLE]` otherwise.
- **unblocks**: `pip install ldpc==2.2.0`. Owner: reproduction env setup. Until installed, all
  `d_BP` numbers in Table `tab:codes` (l.510), `tab:per_batch_stats`, `tab:extended`, `tab:uv_families`
  remain `[AXIOM]` (cited, not reproduced).

### OBL-ENV-2 — `python-igraph` + BLISS absent
- **context**: dedup `sec:results` l.380–393; counts 225→97 CSS, 720→368 PBB.
- **claim**: colored-Tanner-graph canonical labeling reproduces the distinct-code counts.
- **type**: ReproductionArtifact. **modality**: `NumericalSimulation` (exact canonical form, but
  soundness/completeness claim is separate — see OBL-BLISS-1).
- **dependencies**: `python-igraph` with BLISS backend (`junttila2007engineering`, l.381).
- **status**: `[BLOCKING]` for the 97 / 368 / 465 counts.
- **unblocks**: `pip install python-igraph`. Owner: env setup.

### OBL-ENV-3 — `openevolve` + `litellm` absent
- **context**: MAP-Elites LLM-guided search engine, 5 campaigns (`sec:framework` l.218–242;
  `sec:campaigns` l.261–287).
- **claim**: the evolutionary discovery loop itself is reproducible.
- **type**: ReproductionArtifact. **modality**: `EmpiricalMeasurement` (stochastic, LLM-dependent).
- **dependencies**: `openevolve`, `litellm` proxy, LLM API access (~$237, ~140 h — SM l.582).
- **status**: `[FUTURE]` — search reproduction is out of scope for verification; the *codes* are the
  deliverable, not the search trajectory. Re-derivation of discovered codes does NOT require this.
- **unblocks**: full pipeline install + budget. Deliberately deferred; verification of catalog codes
  proceeds via `qldpc` construction + MILP without the search engine.

### OBL-ENV-4 — `qldpc` construction library absent
- **context**: code construction + symplectic Gaussian elimination for logical reps
  (`qldpc v1.0.1`; SM l.679 references `qldpc`'s symplectic GE).
- **claim**: $H_X,H_Z$ (CSS) and $H$ (PBB) matrices and logical operator bases can be built from
  $(A,B)$ / $(A,B,C,D)$ tuples.
- **type**: ReproductionArtifact. **modality**: `SymbolicDerivation` (circulant algebra over F2).
- **dependencies**: `qldpc v1.0.1`, OR an independent F2 circulant builder (numpy + GF(2) rank).
- **status**: `[BLOCKING]` for everything downstream; `[HOLE]`.
- **unblocks**: `pip install qldpc==1.0.1`, OR implement the small cited construction directly
  (R = F2[x,y]/(x^l-1,y^m-1); H_X=(A|B), H_Z=(B^T|A^T); PBB H=[[A,B,C,D],[0,0,B^T,A^T]]).
  Latter is preferred per `code_quality_policy.md` (small cited declaration, no heavy dep) for the
  CSS k-only Stage-1 check; `qldpc` only strictly needed for its symplectic logical basis (OBL-MILP-2).

---

## 2. BP-OSD achievable-syndrome subspace (explicitly NOT proved general)

### OBL-ACHSYN-1 — achievable subspace is half-dimensional (k of 2k)
- **context**: non-CSS Tier-3 distance, `sec:noncss_pipeline` l.353–360.
- **claim**: for the `[[144,12,12]]` PBB code, the Z-channel achievable subspace has dimension $k$
  within the $2k$-dimensional logical space, so ~half of random cosets have no preimage; same for the
  Y-channel.
- **type**: structural lemma about im(H) under a per-channel error space.
- **modality**: `NumericalSimulation` (verified on the one code) — author states VERBATIM
  "the same holds for the Y-channel (**we have not proved this is general**)" (l.359).
- **dependencies**: GF(2) null-space projection on the channel-restricted stabilizer matrix (l.358);
  OBL-ENV-4 (logical basis).
- **status**: `[HOLE]` — the dimension-$k$ claim is `EmpiricalMeasurement` on one code, NOT a theorem.
  Must remain conditional; do NOT promote to a general structural result.
- **unblocks**: (a) reproduce the dimension count on `[[144,12,12]]` PBB to confirm $k$/$2k$ (turns
  `[HOLE]`→`[PRELIMINARY]`); (b) a general proof that for PBB codes the per-channel achievable subspace
  has dimension exactly $k$ would promote to `[SOLID]` + `ExactProof`. No such proof exists in the paper.

### OBL-ACHSYN-2 — achievable-syndrome sampling restores decode success
- **context**: l.360, l.697.
- **claim**: sampling only from the per-channel achievable subspace restored BP-OSD from ~0% to ~100%
  decode success on every PBB code tested.
- **type**: ReproductionArtifact + empirical claim. **modality**: `EmpiricalMeasurement`.
- **dependencies**: OBL-ENV-1 (`ldpc`), OBL-ACHSYN-1 (subspace computation), OBL-ENV-4.
- **status**: `[HOLE]` (also `[BLOCKING]` for any non-CSS BP-OSD bound).
- **unblocks**: implement the projection + sampling, rerun on the PBB catalog; the "every PBB code we
  tested" universal needs the test set enumerated (SM l.578: 149 deep-verified entries).

---

## 3. Rate–distance tradeoff (explicitly NOT proved structural)

### OBL-TRADEOFF-1 — weight-6 envelope is empirical, not structural
- **context**: `sec:tradeoff` l.533–560; intro l.78–80, l.102; conclusion l.761–763.
- **claim**: across the searched catalog, higher $k$ accompanies lower $d$ (weight-6: indecomposable
  $d=12$ ⇒ $k\le16$; $k>24$ ⇒ $d\le4$; weight-8 reaches $k=50,d=8$ but does not escape the envelope).
- **type**: structural conjecture about the BB construction.
- **modality**: `StatisticalInference` / `EmpiricalMeasurement` over an incomplete search —
  authors state VERBATIM "though **we do not prove this is a structural constraint** of the
  construction" (l.78) and "Whether this tradeoff is a structural constraint … or an artifact of our
  (incomplete) search remains open" (l.550).
- **dependencies**: full MILP-verified catalog (OBL-MILP-1).
- **status**: `[HOLE]` — must stay `Conjectural`. NEVER render as a theorem. The BPT bound
  $kd^2=O(n)$ (`bravyi2010tradeoffs`, l.201) and $d=O(\sqrt n)$ (`postema2025existence`, l.116, l.560)
  are the only *proved* asymptotic facts and are themselves `[AXIOM]` (cited).
- **unblocks**: a proof that the BB/PBB construction over $\FF_2[x,y]/(x^\ell-1,y^m-1)$ obeys the
  observed $(k,d)$ envelope. Open problem; not in paper. Reproduction only re-confirms the data points.

### OBL-TRADEOFF-2 — non-CSS PBB does not escape the CSS envelope (open)
- **context**: l.83–87, l.558–560, l.763.
- **claim**: PBB matches but does not exceed $\FOM=12.0$ at $n=144$; whether non-CSS over the same
  ring can escape remains open.
- **type**: open question. **modality**: `EmpiricalMeasurement` (Campaign 5 excluded (12,12),(15,12)
  lattices — caveat l.559, SM l.579).
- **dependencies**: OBL-MILP-2 (symplectic MILP), OBL-ENV-3 (search) to extend to excluded lattices.
- **status**: `[FUTURE]` — known gap, deliberately deferred (lattice coverage limited by ~4× MILP slowdown).
- **unblocks**: PBB evolution on (12,12)/(15,12); requires symplectic MILP at $m=12$ within budget.

---

## 4. Local-Clifford (LC) coverage gaps (`app:lc`)

### OBL-LC-1 — uncovered Clifford pattern classes (a) and (b)
- **context**: `app:lc` "Coverage and gaps" l.1069–1076; results l.1078–1083.
- **claim**: 11/368 PBB codes are CSS-equivalent (10 non-uniform $H$, 1 uniform-$S$ `[[36,4,6]]`);
  357 are "CSS-inequivalent **within the tested local-Clifford families**" — NOT "genuinely non-CSS".
- **type**: classification with explicit residual holes.
- **modality**: `ExactProof` *within tested families* (GF(2) affine systems + parity 2-coloring,
  both stated sound+complete at generator level, l.1051, l.1065); `[HOLE]` for the gaps.
- **gaps (VERBATIM)**: (a) non-uniform $\{SH,HSH\}$ on block 1; (b) cross-class non-uniform patterns
  (e.g. $S$ on some qubits, $H$ on others). Authors: "We do not have a GF(2) reduction … and have not
  exhaustively brute-forced them" (l.1075).
- **dependencies**: `cross2025small` Lemma 7.4 (rank condition, l.1036) — `[AXIOM]`;
  `khesin2026mirror` 2-coloring (l.1043) — `[AXIOM]`; OBL-ENV-4.
- **status**: `[HOLE]` for gaps (a),(b); the 11 positive reductions are `[PRELIMINARY]` (explicit
  per-qubit pattern, "verified by direct construction" l.1081) pending reproduction.
- **unblocks**: (i) reproduce the 36 uniform + GF(2) non-uniform tests on the 368 catalog
  (`evaluation/clifford_equivalence.py`, l.1087 — file not in our tree, must be re-derived);
  (ii) a GF(2) reduction for $\{SH,HSH\}$ / cross-class, OR full $6^n$ enumeration (infeasible at
  $n\ge36$, l.1076). Gap closure is genuinely open.

### OBL-LC-2 — group-CSS vs generator-CSS distinction
- **context**: l.1051–1052.
- **claim**: the parity 2-coloring is sound+complete only "at the level of the supplied generators";
  the broader question (group CSS under a row-reduced generating set after $H_J$) is decoupled.
- **type**: scope caveat. **modality**: `LiteratureGrounded`.
- **status**: `[HOLE]` — must record that a "False" 2-coloring result does NOT prove the *group* is
  non-CSS. Lemma 7.4 rank machinery covers a sub-class only.
- **unblocks**: only matters if reproduction claims "genuinely non-CSS"; the paper deliberately
  avoids that phrasing. Keep the conditional language verbatim.

### OBL-LC-3 — GF(4)-linearity classification not done
- **context**: l.1086.
- **claim**: GF(4)-linearity (`cross2025small` Lemma 7.5, Cor 7.6) would partition the 357 codes;
  not computed.
- **status**: `[FUTURE]` — explicitly "not pursued here". Deferred; does not block any current claim.
- **unblocks**: test $R^{\otimes n}$ ($R=HS$) on the 357 codes. Optional finer structure.

---

## 5. Escalation of cited dependency papers (treat as `[AXIOM]` until reproduced)

### OBL-AXIOM-BRAVYI — `bravyi2024high` (arXiv:2308.07915), MANDATORY
- **context**: BB definition (`sec:bb` l.158), MILP baseline (`eq:milp_obj` SM l.661 "Following
  Bravyi et al."), BP-OSD distance-bounding technique (l.354), baselines `[[72,12,6]]`,`[[144,12,12]]`,
  `[[360,12,≤24]]` (l.203, SM l.695).
- **claim**: the BB construction, the MILP CSS formulation, and the BP-OSD $H_{\mathrm{eff}}$ method
  are correctly imported.
- **modality**: `LiteratureGrounded` → must become `ExactProof`/`ReproductionArtifact` for the parts
  this paper *re-uses* (MILP formulation, gross-code baseline).
- **status**: `[AXIOM]` (cited). Escalate: the MILP formulation `eq:milp_obj`–`eq:milp_binary` is
  reproduced *in this paper's SM* (OBL-MILP-1), so it can be discharged from `[AXIOM]`→`checked`
  by re-validating on `[[72,12,6]]`/`[[144,12,12]]` (SM l.695). The BB *definition* stays `[AXIOM]`
  unless 2308.07915 is read.
- **unblocks**: read arXiv:2308.07915 §II (BB def) + the MIP appendix; re-run the two baselines to
  MIP gap=0. This is the single MANDATORY escalation.

### OBL-AXIOM-TILLICH — `tillich2014quantum` (HGP distance + dimension)
- **context**: dimension formula $k=k_1k_2+k_1^\top k_2^\top$ used in `lem:crt_k` proof (l.1015–1023,
  l.420); distance formula $d=\min(d_1,d_2,d_1^\top,d_2^\top)$ (l.409, SM l.250).
- **claim**: both formulae hold and are correctly applied.
- **modality**: `LiteratureGrounded`.
- **status**: `[AXIOM]` (cited, "treat as AXIOM"). The *dimension* half is load-bearing for
  `lem:crt_k` (k=8l/3); the *distance* half grounds the univariate $d\in\{2,4\}$ collapse.
- **unblocks**: read tillich2014quantum for the two formulae. `lem:crt_k`'s own algebra (gcd /
  divisibility, `macwilliams1977theory` cyclic identity l.1017) is `SymbolicDerivation` and IS
  reproducible (OBL-THM-2) — but it remains *conditional on* the cited dimension formula.

### OBL-AXIOM-CROSS — `cross2025small` Lemma 7.4 (+ §7.2 reduction, Lem 7.5/7.7)
- **context**: group-CSS rank test (l.1036), 6-coset reduction (l.1040), "no fast LC-CSS test known"
  (l.1037).
- **status**: `[AXIOM]`. Lemma 7.4 ("rank$[X|Z]$ = rank$X$+rank$Z$ ⇔ CSS", attributed to T. Yoder)
  is used as a black box.
- **unblocks**: read cross2025small §7. Needed to certify OBL-LC-1's positive results beyond
  reproduction of the script.

### OBL-AXIOM-DECODE — `roffe2020decoding`, `panteleev2021degenerate` (BP-OSD)
- **context**: l.127, l.309. **status**: `[AXIOM]` (decoder correctness). `[FUTURE]` to read; the
  decoder is used only as a stochastic upper-bound oracle, never as ground truth, so deep escalation
  is low priority.

---

## 6. Symplectic (non-CSS) MILP correctness

### OBL-MILP-1 — CSS MILP formulation reproduces baselines
- **context**: `sm:milp` `eq:milp_obj`–`eq:milp_binary` (SM l.661–674); validation l.693–707.
- **claim**: $\min\sum x_i$ s.t. $H_Z x\equiv0$, $\langle x,\bar Z_j\rangle\equiv1\pmod2$,
  $x\in\{0,1\}$; mod-2 linearized by integer slack $\sum a_i x_i-2s=b$ (l.669); $d=\min(d_X,d_Z)$,
  exact iff MIP gap=0.
- **type**: ReproductionArtifact + correctness argument.
- **modality**: `ExactProof` of the linearization (the slack encoding is exact for $\{0,1\}$ vars) +
  `NumericalSimulation` for the solve.
- **dependencies**: `scipy.optimize.milp` (HiGHS) — PRESENT locally (scipy 1.17.1); `numpy`; OBL-ENV-4.
- **status**: `[HOLE]` (reproducible now — highest-priority, no missing lib).
- **unblocks**: implement `eq:milp_obj` in scipy, validate on `[[72,12,6]]` & `[[144,12,12]]` to
  MIP gap=0 (SM l.695). Discharges OBL-AXIOM-BRAVYI's MILP half.

### OBL-MILP-2 — symplectic non-CSS MILP: OR-encoding + row-flip correctness
- **context**: `sm:milp` "Non-CSS symplectic formulation" (SM l.676–691).
- **claim**: $\min\sum w_i$, $w_i=a_i\lor b_i$ enforced by $w_i\ge a_i$, $w_i\ge b_i$, $w_i\le a_i+b_i$
  (convex hull of the four feasible $(a_i,b_i,w_i)$ triples, tight at integer points, l.689);
  commutation via row-flipped $H$ encoding each $(s_X|s_Z)$ as $(s_Z|s_X)$ so $H(a|b)^\top\equiv0$
  computes symplectic inner products (l.689–690); anticommute with $\bar L_j$; $3n$ binary vars; ~4× slower.
- **type**: correctness of the integer-program encoding (R3-tier: a subtle linearization).
- **modality**: `ExactProof` of OR-hull + row-flip identity (the SM gives the derivation:
  symplectic IP of $(s_X|s_Z)$ with $(a|b)$ = $s_X\cdot b+s_Z\cdot a$ = dot of flipped row, l.690) +
  `NumericalSimulation` for the solve.
- **dependencies**: OBL-ENV-4 (`qldpc` symplectic Gaussian elimination for $\bar L_j$, l.679 — the
  ONE place qldpc is hard to replace); `scipy.optimize.milp`; PBB commutation reduces to
  $A C^\top+B D^\top$ symmetric (l.690, ground truth).
- **status**: `[HOLE]`; `[BLOCKING]` for all 368 PBB distances.
- **unblocks**: (a) prove the OR-hull is tight at integer points (4-point check — trivial, do it);
  (b) prove/verify the row-flip identity on a tiny code by brute force vs. enumeration;
  (c) validate symplectic MILP against Tier-1 exhaustive enumeration on a small PBB code
  (`[[72,4,8]]` or `[[36,4,6]]`, $d\le6$, $n\le216$, l.345). Convention caveat (X-first vs Z-first,
  l.690) must be pinned to match `qldpc`'s output.

### OBL-MILP-3 — exactness semantics
- **context**: l.324, l.363, SM l.673, l.75.
- **claim**: a code's $d$ is "exact" only when ALL $2k$ logical MILP instances reach MIP gap=0;
  otherwise the reported $d\le d_{\mathrm{incumbent}}$ is a valid upper bound; final
  $d\le\min(d_{\mathrm{enum}},d_{\mathrm{MILP}},d_{\mathrm{BP\text{-}OSD}})$ (l.362).
- **type**: bookkeeping invariant. **modality**: `ExactProof` (definitional).
- **status**: `[HOLE]` — must be enforced in the reproduction's status tracking so no per-logical
  incumbent is mislabeled "exact". Trust tiers: *exact* (all $2k$ optimal) vs *trusted* (≥2 methods
  agree on the bound), l.363.
- **unblocks**: implement gap-tracking per logical. No new dependency.

---

## 7. BLISS soundness/completeness for permutation equivalence

### OBL-BLISS-1 — colored-Tanner-graph iso ⇔ permutation equivalence
- **context**: `sec:results` l.381–393.
- **claim**: two codes have identical BLISS canonical forms **iff** they are permutation-equivalent
  (qubit relabeling preserving X/Z stabilizer roles; X-checks and Z-checks permute among themselves);
  the relation is "sound and complete for permutation equivalence under the respective coloring" (l.388).
  Non-CSS variant: per-stabilizer X-support and Z-support vertices (3 colors) + a tying edge forbidding
  independent permutation of the two check-vertex classes (l.386).
- **type**: correctness of the equivalence-reduction (R3-tier: the soundness/completeness claim is
  load-bearing for the headline "465 distinct codes").
- **modality**: `ExactProof` (graph-iso reduction is the standard argument) + `NumericalSimulation`
  (BLISS canonical form). The completeness claim rests on the coloring exactly capturing the allowed
  automorphisms — must be verified, not assumed.
- **dependencies**: OBL-ENV-2 (`python-igraph`+BLISS); `junttila2007engineering` (`[AXIOM]`, BLISS
  correctness); `babai2016graph` (GI quasi-poly, l.382 — context only).
- **status**: `[HOLE]`; `[BLOCKING]` for the 97/368/465 counts.
- **unblocks**: (a) prove the coloring is faithful — that the colored-graph automorphism group equals
  the group of admissible code permutations (qubit perms × within-X-check perms × within-Z-check
  perms); for non-CSS, that the tying edge exactly forbids cross-class permutations (l.386). This is
  a short combinatorial argument; write it out, do not assume. (b) Reproduce 225→97 and 720→368.

### OBL-BLISS-2 — "465 distinct" is a conservative UPPER bound, not a count of inequivalent codes
- **context**: l.388–393.
- **claim**: under any *broader* equivalence (local Clifford, full Clifford), the count "cannot exceed
  465 and may be smaller" (l.393); full stabilizer-code equivalence has no known efficient solver and
  no canonical open-source tool (l.390, l.392).
- **type**: scope caveat. **modality**: `LiteratureGrounded` (`petrank1997code`, `babai2016graph` —
  `[AXIOM]`).
- **status**: `[HOLE]` — must record that "distinct" = colored-Tanner-graph-non-isomorphic ONLY.
  Do NOT report 465 as "465 inequivalent quantum codes". OBL-LC-1 already collapses ≥11 PBB into CSS.
- **unblocks**: nothing to *prove*; this is a reporting-discipline obligation. Keep the conditional
  "conservative upper bound" framing verbatim. Owner: reporting stage.

---

## 8. Theorems reproducible without missing libs (SymbolicDerivation HOLEs)

### OBL-THM-1 — `thm:ab_d2` (A=B distance trap), `app:ab_trap` l.957–980
- **claim**: every BB code with $A=B$, $k>0$ has $d=2$ exactly; extends to PBB.
- **modality**: `ExactProof` (the proof is fully given: diagonal-subspace + rank$(A)<\ell m$ argument
  l.964–969). Reproducible by F2 linear algebra (numpy GF(2) rank), no `ldpc`/`qldpc` needed for CSS.
- **dependencies**: F2 rank of $A$; column-weight $\ge2$ lower bound. PBB extension needs MILP to
  confirm the weight-2 operator is not a stabilizer (l.979 — `qldpc`+scipy).
- **status**: `[HOLE]` (CSS case `[PRELIMINARY]` — proof present, reproduce on `[[144,32,2]]`,
  SM l.692). Distinct from $B=A^\top$ self-dual (`liang2025selfdual`, l.972) — do not conflate.
- **unblocks**: re-derive on a catalog $A=B$ code; confirm 72 weight-2 logicals on `[[144,32,2]]`.

### OBL-THM-2 — `lem:crt_k` (k=8l/3), `app:crt` l.985–1024
- **claim**: $A=1+y+y^2$, $B(x)=A(x^c)$, $c=\ell/3$, $3|\ell,3|m$ ⇒ $k=8\ell/3$ (HGP code).
- **modality**: `SymbolicDerivation` (gcd/divisibility algebra) **conditional on**
  OBL-AXIOM-TILLICH (HGP dimension formula) and `macwilliams1977theory` cyclic identity (l.1017).
- **status**: `[HOLE]` — algebra reproducible (sympy 1.12 present); verified for 1680 combos
  $\ell m\le250$ in paper. Remains conditional on the two cited identities (`[AXIOM]`).
- **unblocks**: re-derive $k_A=k_A^\top=2$, $k_B=k_B^\top=2\ell/3$ via gcd; spot-check k=8l/3 on
  (12,6)→k=32, (15,12)→k=40 by F2 rank (independent of the formula).

---

## Summary of blocking dependencies

| Obligation set | `[BLOCKING]` on missing lib | Reproducible NOW (local env) |
|---|---|---|
| MILP CSS (OBL-MILP-1, -3) | no (scipy/HiGHS present) | yes |
| `thm:ab_d2`, `lem:crt_k` (OBL-THM-1/2) | no (numpy/sympy present) | yes (CSS) |
| BP-OSD (OBL-ENV-1, ACHSYN) | **`ldpc`** | no |
| BLISS dedup (OBL-ENV-2, BLISS) | **`python-igraph`** | no |
| symplectic MILP (OBL-MILP-2) | **`qldpc`** (logical basis only) | partial |
| search loop (OBL-ENV-3) | **`openevolve`+`litellm`** | no (`[FUTURE]`) |

Mandatory escalation: **OBL-AXIOM-BRAVYI** (arXiv:2308.07915). Open (no proof exists):
**OBL-TRADEOFF-1** (structural), **OBL-ACHSYN-1** (general subspace dim), **OBL-LC-1** gaps (a),(b).
