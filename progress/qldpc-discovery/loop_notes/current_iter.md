# current_iter — window 1, iters 2-11 (blind discovery loop)

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
