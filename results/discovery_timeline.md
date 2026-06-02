# Discovery timeline — BB / PBB quantum LDPC codes

> The chronological record of code-discovery results, each with its evidence modality
> and verifier status (agentic-lean: a [[n,k,d]] is "discovered" only once its evidence
> is admitted). `checked` = our kernel verified it this session; `LiteratureGrounded`
> = reported by arXiv:2606.02418, pending our re-verification by the ralph loop.
> Modalities per `phys-agentic-loop/_common/agentic_lean_contract.md`.

## Window 1 — 2026-06-02 — kernel bootstrap (verified by `tests/test_kernel.py`, 18 passed)

| Event | Code | Claim | Modality | Verifier | Status |
|---|---|---|---|---|---|
| construction + k | `[[144,12,12]]` gross (12,6) A=y+y²+x³ B=y³+x+x² | k=12 via GF(2) rank | NumericalSimulation | `metrics.css_k` | `checked` |
| construction + k | `[[72,12,6]]` (6,6) same polys | k=12 | NumericalSimulation | `metrics.css_k` | `checked` |
| theorem witness | A=B codes (`thm:ab_d2`) | d=2 exactly (k>0) | ExactProof (constructive) | `theorems.verify_ab_d2` + MILP | `checked` |
| theorem witness | univariate A=1+y+y², B=A(x^{ℓ/3}) (`lem:crt_k`) | k=8ℓ/3 | ExactProof | `theorems.verify_crt_k` (ℓ=3,6,9,12) | `checked` |
| distance (2 methods) | `[[18,4,2]]` (3,3) A=1+x+y B=1+x²+y² | d agrees MILP↔enum | NumericalSimulation ×2 | `distance_milp` + `distance_enum` | `checked` (trusted) |
| distance (MILP exact) | `[[72,2,2]]` (6,6) A=B=1+x+y | d=2 MIP gap=0 | NumericalSimulation (exact) | `distance_milp` | `checked` |
| structure | `[[288,24,12]]` (12,12) A=x⁶+y+y² B=y³+x²+x⁴ | decomposes → 2 Tanner components (= gross ⊕ gross) | ExactProof (graph) | `tanner.qubit_components` | `checked` |
| non-CSS construction | `[[144,12,12]]` PBB (12,6) +C=y+x³y, D=y³+x³y³ | valid non-CSS, k=12, mixed X/Z | NumericalSimulation | `pbb_codes.PBBCode` | `checked` |

## Reference catalog (arXiv:2606.02418 headline codes — `LiteratureGrounded`, to re-verify)

Full catalogs: `ref-paper/arxiv-2606.02418/src/{css,pbb}_catalog_tables.tex` (97 CSS + 368 PBB = 465 distinct).

| Code | (ℓ,m) | wt | FOM | d status | family | note |
|---|---|---|---|---|---|---|
| `[[288,16,12]]` | (12,12) | 6 | 8.0 | exact | XY | highest-k **indecomposable** wt-6 at d=12, all shifts ≤3 |
| `[[288,24,12]]` | (12,12) | 6 | 12.0 | exact | XY | **decomposable** = gross ⊕ gross (excluded) |
| `[[288,50,8]]` | (18,8) | 8 | 11.1 | exact | MX | cross-factored, k=50 |
| `[[144,8,12]]` | (12,6) | 6 | 8.0 | exact | MX | mixed-monomial |
| `[[144,54,4]]` | (12,6) | 8 | 6.0 | exact | MX | k=54 factored (prior wt-6 max was k=16) |
| `[[360,16,≤14]]` | (15,12) | 6 | ≤8.7 | incumbent | XY | |
| `[[360,20,≤14]]` | (30,6) | 8 | ≤10.9 | incumbent | MX | |
| `[[144,12,12]]` PBB | (12,6) | 8 | 12.0 | exact | PBB | non-CSS, matches gross FOM via mixed X/Z |
| `[[360,12,≤24]]` PBB | (30,6) | 8 | ≤19.2 | incumbent | PBB | highest trusted non-CSS FOM |
| `[[108,8,10]]` PBB | (9,6) | 8 | 7.4 | exact | PBB | |

Prior art: gross `[[144,12,12]]` FOM=12 (Bravyi 2024); prior wt-6 max k=16 (Wang 2024).
Empirical rate–distance tradeoff (`conjectural`, not proven structural): wt-6 k>24 ⇒ d≤4;
indecomposable d=12 ⇒ k≤16.

## Next discovery targets (ralph loop)
- Re-verify `[[288,16,12]]` d=12 exact via MILP (optimality audit, ~80 min/paper).
- Stand up the evaluation cascade + MAP-Elites ansatz evolution (components 9,10).
- Run a small CSS campaign at (6,6)/(12,6) and log newly found [[n,k,d]] here.
