# Architecture

The package separates three concerns: a **verifier kernel** (admits codes), a **catalog-blind
discovery** pipeline (proposes codes), and **post-hoc validation** (compares to the held-out paper).

```
ansatz G(l,m) ─▶ Stage 1: k via GF(2) rank ─▶ Stage 2: BP-OSD distance + d/√n trust filter
                                                          │ (fast, upper bounds)
   MAP-Elites-lite archive (binned by k) ◀───────────────┘
        │
        ▼ Stage 3: MILP exact distance (certify; catches BP-OSD overestimates)
   post-campaign: BLISS Tanner dedup ─▶ decomposability ─▶ LC-CSS equivalence
        │
        ▼ results/runs/*.json   ──(post-hoc)──▶  validation vs landmarks / paper catalog
```

## Subpackages (`src/`)

| Subpackage | Modules | Role |
|---|---|---|
| `algebra` | `gf2`, `polynomials` | GF(2) rank/nullspace; the ring R=F2[x,y]/(xˡ−1,yᵐ−1), circulants |
| `codes` | `bb_codes`, `pbb_codes`, `metrics`, `theorems` | BB (CSS) & PBB (non-CSS) construction; k, logicals, FOM; thm:ab_d2, lem:crt_k witnesses |
| `distance` | `distance_milp`, `distance_enum`, `distance_bposd` | CSS + symplectic MILP (HiGHS); exhaustive enumeration; BP-OSD upper bound (ldpc) |
| `structure` | `tanner`, `dedup`, `clifford_equiv` | decomposability (direct-sum); lattice-symmetry + exact BLISS dedup (igraph); LC-CSS (Hadamard 2-coloring + rank cond.) |
| `discovery` | `evaluation`, `search`, `evolve`, `validation` | catalog-blind cascade; GA search; generator-ansatz program evolution; post-hoc catalog validation |
| `cli` | `cli` | `qcode-discover` / `qcode-validate` / `qcode-audit` entry points |

## The 13 reproduced pipeline components (arXiv:2606.02418)

1 BB CSS construction · 2 PBB non-CSS construction · 3 k via GF(2) rank · 4 CSS MILP distance ·
5 symplectic MILP distance · 6 exhaustive enumeration · 7 BP-OSD distance bound · 8 FOM ·
9 staged evaluation cascade · 10 generator-ansatz program evolution (GA-G + Claude-LLM operator) ·
11 BLISS Tanner-graph dedup · 12 decomposability/direct-sum detection · 13 LC-CSS equivalence.

All verified (tests/); component 13 matches the paper's own coverage (residual non-uniform Clifford
gaps are the paper's admitted gaps). The external-LLM-at-scale mutation operator is `[FUTURE]`
(resource-gated); Claude Code served as the LLM operator in the guided runs.

## Design invariants

- **The kernel admits, not the LLM.** A discovered `[[n,k,d]]` carries an evidence modality + verifier
  status (exact MILP gap=0 / enumeration / BP-OSD upper bound).
- **Blind discovery.** `discovery/{evaluation,search,evolve}` import only the kernel; they never read
  the catalog. `discovery/validation` is the sole catalog reader, post-hoc.
- **Honest distances.** BP-OSD is a stochastic upper bound (it can overestimate ~12× for high-rate
  codes — reproduced); MILP gap=0 certifies; incumbents are reported as upper bounds.
