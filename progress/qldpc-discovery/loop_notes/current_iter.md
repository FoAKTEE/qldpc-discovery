# current_iter — window 1, iter 20 (overwrite-mode; history in git + discovery_timeline.md)

## (a) Paper anchor
arXiv:2606.02418 §IV.A (generator-ansatz LLM-guided evolution). Central theme: discover BLIND, then
validate vs the held-out catalog. Latest: Claude Code AS the LLM mutation operator (user directive).

## (b) What shipped (iter 19-20)
- evolve.py: `_safe_expr` (safe exponent eval over l,m) + `custom` strategy → the (Claude) LLM operator
  can propose arbitrary lattice-scaling algebraic patterns. `scripts/run_claude_guided_search.py`.
- RAN Claude-guided blind search (Claude reasons from FOM feedback only, no catalog injection):
  g0 naive → 0 · g1 x/y-swap → [[72,12,6]] · g2 exp-scan → **[[144,12,12]]** (gross, POLY_MATCH) ·
  g3 same pattern @ (12,12) → **[[288,16,12]]** (POLY_MATCH; BP-OSD d=28 overestimate of true 12).
- validate() fix: identical polynomials ⇒ POLY_MATCH regardless of (BP-OSD) d-estimate.

## (c) Status
ALL 13 components PROVEN. Both papers decomposed. Blind→validate proven for: GA (both families,
knowledge-free) + Claude-guided LLM operator (TWO flagship codes POLY_MATCH). 4 paper signature
findings reproduced + the 12× BP-OSD overestimate. 49 tests green, audit PASS, 27 commits on bbc.

## (d) Verifier output
```
$ python -m pytest -q                       -> 49 passed
$ python scripts/code_quality_audit.py      -> PASS (0 blocking)
$ run_claude_guided_search g0..g3           -> [[144,12,12]] & [[288,16,12]] found blind
$ validate(...) both                        -> POLY_MATCH with held-out catalog
```
code_quality_policy_pass: PROVEN.

## (e) Next (incremental / gated)
- LLM operator at scale = Claude-guided search over more lattices/structures (more codes) — runnable.
- Real external-LLM campaigns (litellm + funded API + openevolve) = [FUTURE, user-resource-gated].
- Paper's own LC coverage gaps (a),(b) = not a reproduction shortfall.
Mission substantively complete; remaining is incremental.
