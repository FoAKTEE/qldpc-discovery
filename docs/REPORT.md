# Reproducing LLM-Guided Evolutionary Discovery of Bivariate Bicycle Codes

**Final report** (phys-agentic-loop pipeline-5, rendered from the typed ledger:
`progress/qldpc-discovery/RESEARCH_NOTE.md` + `results/discovery_timeline.md`). Branch `bbc`.

## Abstract

We reproduce arXiv:2606.02418 (Cruz-Benito, Cross, Kremer, Faro; IBM) — LLM-guided evolutionary
discovery of bivariate-bicycle (BB) and perturbed-BB (PBB) quantum LDPC codes — as a runnable,
verified codebase. Working from the paper's *method only*, we built a scientific kernel (the
verifier) and a catalog-**blind** discovery pipeline, then validated discoveries against the paper
as a held-out test set. The blind search rediscovered the gross code [[144,12,12]] and the
[[288,16,12]] code (both exact polynomial matches), using Claude Code itself as the LLM mutation
operator; a knowledge-free genetic-algorithm baseline independently found [[72,12,6]] and the
non-CSS [[36,2,6]] (exact catalog match). All four of the paper's signature findings are reproduced.

## Method reproduced

- **Construction** (§II–III): BB CSS codes `H_X=(A|B), H_Z=(B^T|A^T)` over `R=F2[x,y]/(xˡ−1,yᵐ−1)`;
  PBB non-CSS codes (4-tuples, commutativity `AC^T+BD^T` symmetric). `bb_codes.py`, `pbb_codes.py`.
- **Kernel / admission gates**: k via GF(2) rank; CSS + symplectic MILP distance (scipy/HiGHS);
  exhaustive enumeration; BP-OSD upper bound (ldpc); FOM=kd²/n; Tanner-graph decomposability;
  exact BLISS dedup (igraph); local-Clifford CSS-equivalence (Hadamard 2-coloring + rank condition
  + uniform-Clifford enumeration). `metrics/distance_*/tanner/dedup/clifford_equiv`.
- **Discovery** (§IV): the paper's 3-stage cascade — Stage-1 k-screen → Stage-2 BP-OSD + d/√n trust
  filter → Stage-3 MILP certification — over generator-ansatz program evolution (`evolve.py`,
  `search.py`). The LLM mutation operator is **Claude Code** (no external API).
- **Validation**: post-hoc only, `validation.py`, the sole module that reads the paper catalog.

## Verified results (closed-loop; `tests/`, 49 passing)

| Claim | Evidence | Status |
|---|---|---|
| gross [[144,12,12]] k=12, **d=12** | rank + (BP-OSD=12, low-rate-reliable) + MILP weight-12 | checked / trusted |
| [[72,12,6]] k=12 | rank | checked |
| `thm:ab_d2`: A=B ⇒ d=2 | constructive weight-2 witness + MILP | ExactProof |
| `lem:crt_k`: univariate ⇒ k=8ℓ/3 | rank witness (ℓ=3,6,9,12) | ExactProof |
| univariate distance collapse d∈{2,4} | MILP (§VI.A) | NumericalSimulation |
| 12× BP-OSD overestimate ([[144,32,2]] true d=2 → BP-OSD 24) | thm + MILP + BP-OSD | reproduced |
| [[288,24,12]] = gross ⊕ gross | Tanner connectivity + BLISS | ExactProof |
| MILP ↔ enumeration; symplectic-MILP ↔ CSS-MILP | two-method agreement | checked |

## Blind discovery → held-out validation

**Claude-guided (LLM operator = Claude Code), catalog-blind, reasoning from FOM feedback only:**
g0 naive (0 codes) → g1 x/y-swap → [[72,12,6]] → g2 exponent-scan → **[[144,12,12]]** (POLY_MATCH,
gross code) → g3 same pattern at (12,12) → **[[288,16,12]]** (POLY_MATCH). The kernel caught BP-OSD
overestimating the latter's distance (28 vs true 12) — exactly the paper's verification lesson.

**GA baseline (knowledge-free):** [[72,12,6]] (UB_CONSISTENT vs Bravyi), [[144,16,6]]/[[144,24,4]]
(UB_CONSISTENT vs catalog), non-CSS **[[36,2,6]]** (exact MATCH vs PBB catalog).

The catalog was never consulted during discovery — only afterward, as a held-out test set.

## Honest limitations

- **External-LLM campaigns at scale** (litellm + funded API + openevolve, ~US$400 in the paper) are
  `[FUTURE]`, user-resource-gated. Claude Code served as the LLM operator here; the GA-G program
  baseline is the runnable non-LLM arm.
- **MILP exactness at n≥288** (e.g. certifying [[288,16,12]] d=12) needs ~tens of minutes/code; we
  report BP-OSD/MILP upper bounds + polynomial matches there. Small codes are MILP-exact.
- **LC coverage gaps (a),(b)** (non-uniform {SH,HSH} / cross-class Cliffords) are the *paper's own*
  admitted gaps, not a reproduction shortfall.

## Reproduce

```bash
python -m pytest -q                                                   # verify the kernel
PYTHONPATH=src python scripts/run_blind_discovery.py --type css --distance-method bposd --stage3-verify
PYTHONPATH=src python scripts/validate_against_paper.py --type css    # post-hoc, held-out catalog
```
See `README.md` (overview) and `EXTENDING.md` (add a paper / component). Knowledge base:
`ref-paper/`, `reformulate/qldpc-discovery/`, `progress/qldpc-discovery/`.
