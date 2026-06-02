# qldpc-discovery

Reproduction of **arXiv:2606.02418** — *"Evolutionary Discovery of Bivariate Bicycle Codes
with LLM-Guided Search"* (Cruz-Benito, Cross, Kremer, Faro; IBM) — as a runnable **codebase +
pipeline + discovery timeline** for the autonomous discovery of bivariate-bicycle (BB) and
perturbed-BB (PBB) quantum LDPC codes.

## Central principle — blind discovery, paper second

The auto-discovery pipeline **rediscovers codes without using any answer extracted from the
paper**: no catalog polynomials, no reported `[[n,k,d]]` as input. Only the *apparatus* (code
construction, k via GF(2) rank, MILP/BP-OSD distance, FOM — the verifier) comes from the method.
The search runs blind; the paper catalog is a **held-out test set** consulted only by a separate
post-hoc validator. *The LLM/search proposes; the scientific kernel admits.*

## Pipeline architecture (matches the paper)

```
ansatz G(l,m) ─▶ Stage 1: k via GF(2) rank ─▶ Stage 2: BP-OSD distance + d/√n trust filter
                                                          │ (fast, upper bounds)
   MAP-Elites-lite archive (binned by k) ◀───────────────┘
        │
        ▼ Stage 3: MILP exact distance (certify; catches BP-OSD overestimates)
   post-campaign: BLISS Tanner-graph dedup ─▶ decomposability ─▶ LC-CSS equivalence
        │
        ▼ results/discovery_timeline.md   ──(post-hoc)──▶  validation vs paper catalog
```

## Layout

| Path | Contents |
|---|---|
| `src/qcode_discovery/` | the kernel + discovery + validation modules (pure numpy/scipy core) |
| `tests/test_*.py` | verification suite (`python -m pytest -q`) |
| `scripts/run_blind_discovery.py` | run a blind campaign (`--type css\|pbb`, `--distance-method bposd`, `--stage3-verify`) |
| `scripts/validate_against_paper.py` | **post-hoc** validation vs the held-out catalog (`--type css\|pbb`) |
| `scripts/code_quality_audit.py` | static code-quality diagnostic (R0–R4 policy) |
| `results/` | `discovery_timeline.md`, blind-run JSON, validation reports |
| `ref-paper/arxiv-2606.02418/` | paper tex mirror + `chunk_index` + digests (PROVENANCE recorded) |
| `reformulate/qldpc-discovery/paper_2606.02418/` | decomposition: theorem + file logical-dependency DAGs |
| `progress/qldpc-discovery/` | RESEARCH_NOTE, loop notes, typed ledger, external axioms |
| `phys-agentic-loop/` | methodology infra (separate repo); ralph loop, code-quality policy, pipelines |

## Modules (`src/qcode_discovery/`)

`gf2` (F2 algebra) · `polynomials` (ring R=F2[x,y]/(xˡ−1,yᵐ−1)) · `bb_codes` (CSS) ·
`pbb_codes` (non-CSS + commutativity) · `metrics` (k, FOM, logicals) ·
`distance_milp` (CSS + symplectic, scipy/HiGHS) · `distance_enum` (exhaustive cross-check) ·
`distance_bposd` (BP-OSD upper bound; needs `ldpc`) · `tanner` (decomposability) ·
`dedup` (lattice-symmetry + exact BLISS; needs `igraph`) · `clifford_equiv` (LC-CSS Hadamard 2-coloring) ·
`evaluation` (catalog-blind cascade) · `search` (blind GA/MAP-Elites) · `validation` (post-hoc, catalog) ·
`theorems` (numeric witnesses for `thm:ab_d2`, `lem:crt_k`).

## Quickstart

```bash
python -m pytest -q                                  # verify the kernel (landmarks below)
PYTHONPATH=src python scripts/run_blind_discovery.py --type css --distance-method bposd --stage3-verify
PYTHONPATH=src python scripts/validate_against_paper.py --type css
```

Dependencies: `numpy`, `scipy` (required). Optional `decoders` extra: `ldpc` (BP-OSD, component 7)
and `python-igraph` (exact BLISS dedup, component 11) — `pip install --user ldpc python-igraph`.

## Verified landmarks (closed-loop, in `tests/`)

- gross `[[144,12,12]]` k=12; `[[72,12,6]]` k=12 (GF(2) rank).
- **`thm:ab_d2`**: every A=B code has d=2 (constructive witness + MILP).
- **`lem:crt_k`**: univariate A=1+y+y², B=A(xˡ́³) ⇒ k=8ℓ/3.
- MILP ↔ exhaustive-enumeration distance agreement; symplectic-MILP ↔ CSS-MILP consistency.
- `[[288,24,12]]` = gross ⊕ gross (Tanner decomposability + BLISS).
- **BP-OSD 12× overestimate** on the A=B `[[144,32,2]]` (true d=2) — the paper's key methodological finding.

## Blind-discovery results (vs held-out catalog)

The blind search rediscovers, *cold*, codes that match the paper: CSS `[[72,12,6]]` (UB_CONSISTENT
w/ Bravyi, reproduced across seeds), `[[144,16,6]]` / `[[144,24,4]]` (UB_CONSISTENT w/ catalog at
n=144), and non-CSS `[[36,2,6]]` (**exact MATCH** w/ the PBB catalog). See `results/discovery_timeline.md`.

## Methodology

Built under the phys-agentic-loop "Agentic Lean" discipline (typed ledger; the kernel admits, not
the LLM) on the `bbc` branch via a ralph loop. Per-substage commits; code-quality policy enforced.
