# Provenance — arXiv:2606.02418

Write-once acquisition record per `phys-agentic-loop/pipelines/6-escalation/spec.md` §A.4.

| Field | Value |
|---|---|
| arXiv ID | 2606.02418 |
| Title | Evolutionary Discovery of Bivariate Bicycle Codes with LLM-Guided Search |
| Authors | Juan Cruz-Benito, Andrew W. Cross, David Kremer, Ismael Faro (IBM Research) |
| Venue target | PRX Quantum (revtex4-2, `prxquantum`) |
| Acquired | 2026-06-02 (UTC) via `curl https://arxiv.org/e-print/2606.02418` |
| Pages (PDF) | 42 |
| Reference code | https://github.com/qiskit-community/qcode-discovery (cited as `cruzbenito2026qcode`) |

## Artifact hashes (sha256)

| File | sha256 | Status |
|---|---|---|
| `eprint.tar.gz` (e-print tarball) | `21a9d027c1266d7293132e2edce187cf249376eff65e25bd7db6ce16e6aa8e12` | gitignored (reproducible) |
| `paper.pdf` | `5fe79673abd2edfa866ae5a5e2c402cd20331f88dfc02d653575b331ad91c837` | gitignored (reproducible) |

## Extracted tex source (committed; read-only mirror — rule 8)

| File | Role | Lines |
|---|---|---|
| `src/paper.tex` | Main text (toplevel) | 1091 |
| `src/supplemental.tex` | Supplemental Material (toplevel) | 715 |
| `src/css_catalog_tables.tex` | CSS catalog: n=144/288/360 (225 reps → 97 distinct) | 480 |
| `src/pbb_catalog_tables.tex` | non-CSS PBB catalog (368 codes) | — |
| `src/references.bib` | bibliography | 748 |
| `src/figures/*.pdf` | 6 figures (pipeline, pareto, fitness, LER, tightening, per-batch) | — |

Compiler: `pdflatex`, TeXLive 2025 (per `src/00README.json`).

`ref-paper/` is a **read-only mirror**. All commentary/decomposition lives in
`reformulate/qldpc-discovery/paper_2606.02418/` and `progress/qldpc-discovery/`.
