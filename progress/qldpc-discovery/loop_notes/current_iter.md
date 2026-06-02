# current_iter — window 1, iters 2-4 (blind discovery loop)

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
