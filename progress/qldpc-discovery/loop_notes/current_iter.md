# current_iter — window 1 (bootstrap)

**Overwritten every iteration.** Window-scoped (multi_window_task, closing=false).

## (a) Paper anchor
arXiv:2606.02418 whole pipeline. This window builds the scientific KERNEL that admits
discoveries (components 1,2,3,4,6,8,12) + the two theorems (thm:ab_d2 App.D, lem:crt_k App.C).

## (b) What shipped this iter
- Infra: bbc `ralph-loop.local.md` (plugin-safe), code_quality_policy bound, escalation injected. Commit A `b205f8a`.
- phys-agentic-loop: plugin-safe template note. Commit `8e4c418` (agentic-lean branch).
- Decomposition (workflow wf_fce0b721-205): 3 chunk digests + 8 elaboration artifacts +
  theorem/file/logic/bundle dependency plans + chunk_index (Substage B).
- Kernel codebase + 18-test suite + code-quality audit + discovery timeline. Commit D `79e77f8`.
- Escalation: arXiv:2308.07915 (Bravyi BB foundation) acquired to ref-paper/.

## (c) Next-5 roadmap (non-duplication checked)
1. symplectic-weight MILP for non-CSS distance (component 5) — extends `distance_milp`; unlocks PBB d. NEW.
2. evaluation cascade (component 9): k→BP-OSD/MILP→FOM→trust filter `d/√n`. NEW.
3. MAP-Elites + generator-ansatz evolution (component 10): minimal in-tree GA-on-ansatz (no openevolve dep). NEW.
4. [[288,16,12]] d=12 MILP optimality audit (re-verify headline code, log to timeline). NEW.
5. decompose arXiv:2308.07915 (pipeline-0) for BB-foundation knowledge base. NEW.

## (d) Simplification flag
no (bootstrap window; first simplification cycle due ~window 5–10).

## (e) Token-utilization
Multi-window bootstrap window; heavy implementation (kernel + decomposition workflow + escalation). ≥0.90 target met.

## (f) Verifier output
```
$ python -m pytest -q
..................                                       [100%]   18 passed in 3.27s
$ python scripts/code_quality_audit.py
code_quality_audit: 10 files, 34 findings (CRITICAL=0 HIGH=0 MEDIUM=0 LOW=34)
code_quality_policy_pass: PASS (0 blocking finding(s))
```
code_quality_policy_pass: components 1,2,3,4,6,8,12 PROVEN; 5,7,9,10,11,13 [FUTURE] (scaffolded).
