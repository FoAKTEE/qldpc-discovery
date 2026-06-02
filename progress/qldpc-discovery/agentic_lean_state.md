---
role: Agentic Lean state note (typed-ledger view) for qldpc-discovery
scope: ${AGENTIC_STATE}; updated at every ledger transition
discipline:
  - ../../phys-agentic-loop/alignment.md
  - ../../phys-agentic-loop/_common/agentic_lean_contract.md
  - ../../phys-agentic-loop/_common/markers.md
  - ../../phys-agentic-loop/_common/note_discipline.md
  - ../../phys-agentic-loop/_common/progress_principles.md
---

# qldpc-discovery — Agentic Lean State

Live typed-ledger view. The LLM proposes ansätze; the kernel (GF(2) rank, MILP,
enumeration, Tanner, LC) admits. Canonical macro state: `RESEARCH_NOTE.md`.

## Sigma Imports

| ID | Source | Type | Status | Notes |
|---|---|---|---|---|
| `paper:2606.02418` | ref-paper/arxiv-2606.02418/src | paper | `LiteratureGrounded` | holy grail; decomposed |
| `paper:2308.07915` | ref-paper/arxiv-2308.07915/src | paper | `LiteratureGrounded` | BB foundation; acquired, decomposition `[FUTURE]` |
| `code:qcode-discovery` | ref-code/ (empty @4a9520e) | code | `refuted-as-source` | reference repo EMPTY; reproduce from paper |
| `lib:numpy`, `lib:scipy.milp` | local | code | `checked` | GF(2) + MILP backends |

## Gamma Context

| Name | Type | Assumptions / regime |
|---|---|---|
| `(ℓ,m)` | lattice dims | n=2ℓm; campaigns use {(12,6),(6,12),(12,12),(24,6),(15,12),(30,6),(16,9),(18,8)} |
| `A,B,C,D` | polynomials in R=F2[x,y]/(x^ℓ−1,y^m−1) | trinomial (C1–3) or 4–6-term (C4); PBB 4-tuple (C5) |
| `F2` | field | all arithmetic mod 2 |

## Active Goals

| Goal | Expected evidence | Priority | Owner |
|---|---|---|---|
| `Γ ⊢ ?d : NumericalSimulation [[288,16,12]] d=12 exact` | MILP gap=0 all 32 logicals | `[BLOCKING]` next | loop |
| `Γ ⊢ ?cascade : evaluation cascade Stage1/2/3` | runnable evaluate(ansatz)→metrics | `[FUTURE]` | loop |
| `Γ ⊢ ?evolve : MAP-Elites ansatz evolution` | a campaign produces logged [[n,k,d]] | `[FUTURE]` | loop |

## Ledger (admitted this window)

| Claim | Modality | Evidence / verifier | Status |
|---|---|---|---|
| gross [[144,12,12]] k=12 | NumericalSimulation | `tests/test_kernel.py::test_gross_code_k12` | `[SOLID]` |
| thm:ab_d2: A=B ⇒ d=2 | ExactProof (constructive) | `theorems.verify_ab_d2` + MILP | `[SOLID]` |
| lem:crt_k: k=8ℓ/3 | ExactProof | `theorems.verify_crt_k` (ℓ=3,6,9,12) | `[SOLID]` |
| MILP↔enum distance agree | NumericalSimulation ×2 | `test_milp_enum_agree_small` | `[SOLID]` |
| [[288,24,12]] decomposable | ExactProof (graph) | `tanner.qubit_components`=2 | `[SOLID]` |
| PBB [[144,12,12]] non-CSS k=12 | NumericalSimulation | `test_pbb_144_12_12_noncss` | `[SOLID]` |

## Next Tactics

- `[HOLE]` symplectic-weight MILP for non-CSS distance (component 5) — `distance_milp` extension.
- `[HOLE]` evaluation cascade (component 9) wiring k→distance→FOM→trust filter.
- `[HOLE]` MAP-Elites + ansatz evolution (component 10); needs openevolve OR a minimal in-tree GA-on-ansatz.
- `[FUTURE]` BLISS dedup (component 11) — igraph or networkx canonical-form fallback.
- `[FUTURE]` decompose arXiv:2308.07915 (pipeline-0) for the BB-foundation knowledge base.

## Appendix — Abandoned tactics
(none yet)
