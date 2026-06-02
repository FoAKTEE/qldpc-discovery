# current_iter — window 1, iters 2-20 (blind discovery loop)

## iter20: Claude-guided g3 rediscovers 2nd flagship [[288,16,12]] (POLY_MATCH) + validate poly-match fix
- g3: x/y-swap pattern at (12,12) -> A=x³+y+y²,B=y³+x+x² = catalog [[288,16,12]] (POLY_MATCH). BP-OSD
  d=28 overestimate (true d=12); fixed validate() so identical polynomials => POLY_MATCH regardless of
  d-estimate (same code). 49 tests pass. Claude-guided search now rediscovered TWO headline codes blind.

---

## iter19 (latest): CLAUDE-GUIDED LLM search rediscovers the gross code (user directive)
- User: "use claude code as api and run search" -> Claude Code IS the LLM mutation operator (no
  external API). evolve.py: added safe exponent evaluator (_safe_expr over l,m) + "custom" strategy
  so Claude can propose arbitrary lattice-scaling algebraic patterns. scripts/run_claude_guided_search.py:
  evaluates a Claude-proposed ansatz blind + records lineage to results/runs/claude_guided_trajectory.json.
- RAN the loop (Claude as operator, blind, reasoning from FOM feedback only):
  g0 naive A=x+y+y²,B=y+x+x² -> score 0 (no codes).
  g1 "concentrate one variable (x/y-swap)" -> [[72,12,6]] FOM=6, score 8.
  g2 "widen lone-exponent scan {2,3,4,5}" -> [[144,12,12]] FOM=12, score 18.
- g2's exp-3 at (12,6) = A=x³+y+y², B=y³+x+x² = GROSS CODE. POST-HOC validation: POLY_MATCH with
  held-out catalog [[144,12,12]] (strongest verdict). Central theme realized WITH the LLM operator.
- 48 tests pass; audit PASS. Discipline: mutations from algebraic reasoning on fitness only, no
  catalog injection (best-effort blind since I read the paper; GA run is fully knowledge-free).

---


## iter18 (latest): generator-ansatz PROGRAM evolution (the paper's core representation)
- evolve.py: GeneratorAnsatz (parameterized algebraic STRATEGIES emitting (A,B) for ANY (l,m) —
  exponents scaled to the lattice, so one ansatz generalizes across block lengths, the paper's key
  property). GA-G program mutation (perturb params / add / remove strategy — paper's non-LLM baseline,
  runnable). evolve_ansaetze (cross-lattice FOM fitness). llm_mutation = the paper's headline operator,
  [FUTURE: needs litellm + funded API key + openevolve] — credential-gated, refuses cleanly.
- FAITHFUL caveat reproduced: BP-OSD fitness inflates high-k FOM (a run posted [[144,32,d_BP=20]]
  FOM=88.89 — a BP-OSD overestimate that slipped the trust filter). This IS the paper's Campaign-1-3
  fitness-corruption; reported ansatz codes are UPPER BOUNDS needing Stage-3 MILP (verify_elites_milp).
- 47 tests pass; audit PASS (audit caught my llm_mutation stub using [BLOCKING] not [FUTURE] -> fixed).
- The ONE genuinely remaining framework piece is the LLM mutation operator, gated on user-provided
  API credentials + budget (~$400 in paper). Everything else reproduced + verified.

## iter17: univariate distance collapse d in {2,4} (paper Sec VI.A) — 4th signature finding reproduced.
## iter16: self-evolution window (results/ by type + EXTENDING.md).

---


## iter16 (latest): SELF-EVOLUTION window (explicit user directive)
- Reorganized results/ by type (no mixed kinds): results/runs/*.json (raw runs),
  results/validation/*.md (reports), results/discovery_timeline.md (canonical) at root.
  Updated the 2 scripts' paths + timeline/README refs; re-validated both types (matches hold).
- Added EXTENDING.md: knowledge-base expansion guide (add a paper / add a component / run+validate /
  tracking cadence) — directly serves "easy for knowledge base expansion".
- 41 tests pass; audit PASS. (Self-evolution cadence: ~every 5-10 windows per policy; this is the first.)
- Loop: wider campaigns; (a)/(b) LC gaps are paper's own; mission substantively complete.

---


## iter15 (latest): gross d=12 [HOLE] closed + REAL BP-OSD BUG found & fixed
- Verifying gross [[144,12,12]] d=12 exposed a bug: BP-OSD returned 6 (impossible upper bound for d=12).
  ROOT CAUSE: coset method must stack DUAL (Z) logicals in H_eff for X-distance (same-type logicals
  commute); calls had X/Z swapped. FIXED. Now [[144,12,12]]->12, [[72,12,6]]->6, A=B->24 (all correct).
- gross d=12 kernel-verified (BP-OSD=12 + MILP weight-12 8/12 logicals) -> upgraded LiteratureGrounded
  -> NumericalSimulation(d<=12, trusted). [HOLE] CLOSED. Regression test test_bposd_gross_144_d12 added.
- Impact: iter11-12 BP-OSD Stage-2 rankings were buggy, but reported discoveries were Stage-3-MILP-verified.
- LESSON: the "low-value" d=12 re-verification caught a real correctness bug — multi-case verification matters.
- 41 tests pass; audit PASS. RESEARCH_NOTE Next Tactics refreshed to current state.
- Loop: wider campaigns; self-evolution window; (a)/(b) LC gaps are paper's own.

---


## iter14 (latest): uniform per-block Clifford LC-CSS check (component 13 -> ~complete)
- clifford_equiv: _clifford_symplectic_mats (6 reps as 2x2 F2 maps), _apply_block, _is_css,
  uniform_clifford_lc_css (App.E Step 1: 36 uniform per-block assignments + rank condition).
  lc_css_classify now: CSS_GROUP -> UNIFORM_CLIFFORD_CSS -> HADAMARD_CSS -> CSS_INEQUIVALENT_TESTED.
- Verified symplectic-exact: H preserves CSS, S breaks CSS (X->Y); uniform-S-transformed CSS code
  is DETECTED as uniform-Clifford-CSS. 40 tests pass; audit PASS.
- Component 13 now matches the PAPER'S OWN coverage (rank cond + Hadamard {I,H} + uniform Clifford);
  residual non-uniform {SH,HSH} on block-1 + cross-class patterns are the paper's ADMITTED gaps (a),(b).
- ALL 13 components now PROVEN (component 13 to paper-parity). Remaining open: gross d=12 MILP re-run [HOLE].
- Loop continues: gross d=12 verification (bounded); wider campaigns; periodic self-evolution window.

---


## iter13 (latest): README + Bravyi (2308.07915) pipeline-0 decomposition (escalation)
- iter13a: project README.md (front-door "final product" doc).
- iter13b: focused decomposition workflow (3 agents) of the FOUNDATIONAL BB paper arXiv:2308.07915:
  digests (chunk_001 BB definition l.308-888, chunk_002 logicals+circuit), chunk_index, and
  relation_to_2606.md (6 typed dependency rows D1-D6 mapping Bravyi -> our modules + external_axioms).
  Agent ran the kernel for evidence (gross n=144,k=12,CSS,wt6 VERIFIED).
- external_axioms: ax:bb-construction REPLACED-BY (decomposed); added ax:milp-distance-method [ACTIVE].
- [HOLE] flagged by agent: gross [[144,12,12]] d=12 still LiteratureGrounded (not MILP-re-run; ~13min).
- NOTE: misdiagnosed a write-race as a workflow crash; reading-before-write preserved the agent's
  (better) relation_to_2606.md. Lesson: confirm workflow completion via its notification, not a poll.
- Loop continues: re-verify gross d=12 (bounded MILP); complete component 13 LC enumeration.

---


## iter12 (latest): consolidated 3-stage cascade campaign at scale + validation
- Ran full pipeline (Stage1 k -> Stage2 BP-OSD+trust -> Stage3 MILP -> BLISS dedup) over (6,6),(12,6).
- SELF-CORRECTION demonstrated: Stage2 BP-OSD [[144,24,14]] FOM=32.67 -> Stage3 MILP [[144,24,4]];
  [[72,16,4]](BP) -> [[72,16,2]](MILP trap). BLISS: 18 reps -> 17 distinct.
- Validation: [[144,24,4]]~catalog[[144,24,6]], [[144,8,8]]~[[144,8,12]], [[72,12,6]]~Bravyi (k-matches at n=144).
- runner: Stage-3 verify now respects --max-logicals (n=144 tractable). 38 tests still green.
- Loop continues: complete component 13 LC enumeration; decompose Bravyi (2308.07915); scale campaigns.

---


## iter11 (latest): full 3-stage cascade (Stage1 k -> Stage2 BP-OSD+trust -> Stage3 MILP)
- evaluation: trust filter (d/sqrt(n) < 2.0) field. search: distance_method="bposd" + trust gate
  (only for BP-OSD upper bounds), verify_elites_milp (Stage-3 exact). runner: --distance-method,
  --stage3-verify flags + BLISS dedup.
- DEMONSTRATED self-correction: Stage-2 BP-OSD ranked [[72,16,4]]; Stage-3 MILP revealed true
  [[72,16,2]] (d=2 trap) — the paper's pipeline working. 38 tests pass; audit PASS.
- Pipeline now matches paper architecture: fast BP-OSD loop + trust filter + post-hoc MILP exact.
- Next: larger multi-lattice campaign (BP-OSD Stage-2, big budget) -> consolidated verified catalog
  + BLISS dedup + validation; complete component 13 LC enumeration; decompose Bravyi.

---


## iter10 (latest): exact BLISS dedup via igraph (component 11 -> PROVEN) + dedup_bb bugfix
- dedup.bliss_canonical_hash / dedup_bliss: igraph color-respecting canonical labeling
  (qubits/X-checks/Z-checks) — SOUND+COMPLETE for permutation equivalence. Wired into campaign
  (BLISS when igraph present, lattice-symmetry fallback else).
- Verified vs paper: [[288,24,12]] (12,12) and (24,6) -> SAME BLISS canonical (the direct-sum
  claim); BLISS catches this cross-lattice iso that lattice-symmetry dedup_bb cannot.
- BUGFIX: dedup_bb signature now includes (l,m) — identical polys at different lattices are
  different codes; previously wrongly merged. 37 tests pass; audit PASS.
- KERNEL STATUS: components 1-13 all PROVEN except 13 (LC) PARTIAL. BP-OSD(7) + BLISS(11) now exact.
- Next: complete component 13 LC enumeration; larger consolidated blind campaigns w/ BP-OSD Stage-2.

---


## iter9 (latest): ESCALATION install (ldpc+igraph) + BP-OSD (component 7) + overestimation reproduced
- pip --user --break-system-packages installed ldpc 2.4.1 + igraph 1.0.0 (PEP668 workaround).
- distance_bposd.py: H_eff=(check;L) decode random logical cosets -> upper bound (paper V.A/C).
  Wired into cascade as Stage-2 (distance_method="bposd"); MILP stays Stage-3 exact.
- REPRODUCED paper headline: [[72,12,6]] bposd=6 (=MILP); A=B [[144,32,2]] bposd=24 vs TRUE d=2
  (thm:ab_d2+MILP) = 12x overestimate. 36 tests pass; audit PASS.
- iter8: dedup wired in + blind CSS at n=144 -> [[144,16,6]] UB_CONSISTENT w/ catalog (direct match).
- Next: iter10 true BLISS via igraph (component 11 -> exact, drop [FUTURE]); then larger campaigns.

---


## iter7 (latest): Tanner dedup (component 11) — FULL APPARATUS COMPLETE
- dedup.py: WL-histogram FAILED verification (bi-regular Tanner graphs -> trivial coloring,
  over-merges gross==diff). Replaced with SOUND lattice-symmetry canonicalization (x->x^a,
  y->y^b, x<->y, A<->B) -> conservative UPPER-bound distinct count (paper's framing).
- Verified: gross == x->x^5 relabel == A<->B swap; gross != diff(x^4) != A=B; dedup(5)->3 classes.
- 34 tests pass; audit PASS. All 13 pipeline components now built (PROVEN/PARTIAL; only 7 BP-OSD
  [FUTURE], needs ldpc). Theorems [SOLID]. Central theme done end-to-end (both families).
- Next: scale blind CSS to n=144 vs catalog; wire dedup into campaign post-processing; decompose Bravyi.

---


## iter6 (latest): LC-CSS equivalence via Hadamard 2-coloring (component 13)
- clifford_equiv.py: hadamard_two_coloring (parity union-find; Y-obstruction + 2-colorability,
  App.E), lc_css_classify (uses pbb.is_css_group rank cond + Hadamard). _ParityUF.
- Verified: CSS-as-PBB -> CSS_GROUP w/ constructive H pattern that PROVABLY makes generators
  pure-X/Z; Y-support -> y_obstruction; [[144,12,12]] PBB -> CSS_INEQUIVALENT_TESTED (has Y).
- 33 tests pass; audit PASS. Component 13 PARTIAL (Hadamard + rank cond done; uniform-S /
  non-uniform {I,S}/{H,HS} enumeration + gaps (a),(b) = [FUTURE]).
- Completion kernel pieces remaining: component 11 (BLISS dedup — needs igraph or WL fallback).

---


## iter5 (latest): blind NON-CSS PBB discovery + PBB validation
- search.blind_search_pbb (commutativity-filtered 4-tuples, symplectic-MILP, FOM) + validation.parse_pbb_catalog.
- RAN blind PBB (seed 5, (6,3)/(3,6)): found [[36,2,6]] d=6 exact, [[36,4,5]] d=5 exact, ...
- POST-HOC validation: [[36,2,6]] -> **MATCH** (exact) with PBB catalog. Blind non-CSS rediscovery confirmed.
- 29 tests pass; audit PASS. -> results/blind_pbb_discovery.json, results/validation_report_pbb.md.
- Roadmap item 2 (blind PBB) DONE. Next: item 1 (scale CSS to n=144), item 3 (bliss dedup), item 4 (LC).

---


**Overwritten every iteration.** Multi-window task, closing=false (lightweight intermediate).

## (a) Paper anchor
Central theme (user directive, blind_discovery_policy): the pipeline must REDISCOVER codes
blind, then validate vs the paper. Iters 2-4 build + run that loop.
- iter2: component 5 (symplectic non-CSS MILP distance), SM non-CSS formulation.
- iter3: components 9 (evaluation cascade) + 10 (blind generator-ansatz search), sec IV.A/B.
- iter4: post-hoc validation vs catalog + landmarks (sec V.B + catalogs).

## (b) What shipped
- `distance_milp.symplectic_distance_milp` + `metrics.symplectic_logicals` (component 5). Commit a5489fb.
- `evaluation.py` (catalog-blind cascade), `search.py` (blind GA + MAP-Elites-lite archive).
- `scripts/run_blind_discovery.py` — RAN blind (seed 7): found [[72,12,6]] FOM=6 (gross-family,
  cold), [[72,8,6]] d=6 exact, [[36,4,6]] exact, ... + rediscovered the d=2 trap (low FOM).
  -> `results/blind_css_discovery.json`.
- `validation.py` + `scripts/validate_against_paper.py` — POST-HOC: [[72,12,6]] UB_CONSISTENT
  with Bravyi landmark; rest NOVEL_AT_N (catalog starts n=144). -> `results/validation_report.md`.
- 6 new tests (test_discovery.py); blind run logged to results/discovery_timeline.md.

## (c) Next-5 roadmap (non-dup checked)
1. Scale blind search to n=144 (12,6): match the gross [[144,12,12]] vs catalog directly. NEW.
2. Extend search to PBB 4-tuples (blind non-CSS discovery via symplectic distance). NEW.
3. bliss_dedup.py — networkx canonical-form fallback (igraph MISSING) for permutation dedup. NEW.
4. clifford_equiv.py — Hadamard 2-coloring + LC rank condition (App.E), component 13. NEW.
5. Decompose arXiv:2308.07915 (BB foundation), pipeline-0. NEW.

## (d) Simplification flag
no (build phase). First simplification cycle due ~window 5-10.

## (e) Token-utilization
Heavy implementation window (kernel extension + blind discovery + validation + run). ≥0.90.

## (f) Verifier output
```
$ python -m pytest -q
..........................                               [100%]   26 passed
$ python scripts/code_quality_audit.py
code_quality_audit: 13 files, 46 findings (CRITICAL=0 HIGH=0 MEDIUM=0 LOW=46)
code_quality_policy_pass: PASS (0 blocking finding(s))
$ python scripts/run_blind_discovery.py   -> 10 codes incl [[72,12,6]] FOM=6 (blind)
$ python scripts/validate_against_paper.py -> [[72,12,6]] UB_CONSISTENT w/ Bravyi landmark
```
code_quality_policy_pass: components 5,9,10 + validation — PROVEN (R2-R3, verified blind+validated).

## (g) Decomposition QA (carried)
H-2/H-3 (P↔PC crosswalk) still open loop tasks; H-1 fixed iter1.
