# qcode-discovery

> A verified, **catalog-blind** reproduction of *"Evolutionary Discovery of Bivariate Bicycle Codes
> with LLM-Guided Search"* ([arXiv:2606.02418](https://arxiv.org/abs/2606.02418), Cruz-Benito, Cross,
> Kremer, Faro; IBM) — built as a runnable Python package + discovery pipeline + results timeline.

`python · numpy · scipy` · optional `ldpc` + `python-igraph` · **54 tests passing** · code-quality audit: PASS · CI: GitHub Actions

The LLM/search proposes generator ansätze; a **scientific kernel admits** them. Discovery runs
**blind** to the paper; the catalog is consulted only *post-hoc*, as a held-out test set.

## Install

```bash
pip install -e .                 # core: numpy, scipy
pip install -e ".[decoders]"     # + ldpc (BP-OSD distance) + python-igraph (exact BLISS dedup)
```

## Quickstart

```python
from qcode_discovery import BBCode, css_k, css_distance_milp, blind_search_css, validate

gross = BBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2")     # the gross code [[144,12,12]]
print(gross.n, css_k(gross.HX, gross.HZ))            # 144 12
```
```bash
qcode-discover --type css --distance-method bposd --stage3-verify --lattices 6x6,12x6
qcode-validate --type css        # post-hoc, vs the held-out catalog
qcode-audit                      # static code-quality audit
```
See **[examples/quickstart.py](examples/quickstart.py)** and **[docs/usage.md](docs/usage.md)**.

## Features

- **Verifier kernel** — BB (CSS) & PBB (non-CSS) construction; k via GF(2) rank; minimum distance by
  CSS/symplectic MILP (HiGHS), exhaustive enumeration, and BP-OSD; FOM; Tanner decomposability;
  exact BLISS dedup; local-Clifford CSS-equivalence; numeric witnesses for two paper theorems.
- **Blind discovery** — a staged cascade (k → BP-OSD + trust filter → MILP) over GA / generator-ansatz
  program evolution, importing only the kernel (never the catalog).
- **Post-hoc validation** — compares blind discoveries to the paper catalog and landmark codes.

## Repository layout

```
src/qcode_discovery/   library: algebra · codes · distance · structure · discovery (+ cli)
tests/                 54-test suite (kernel · discovery · CLI)
scripts/               full-featured research drivers (run/validate/llm-search/audit)
docs/                  index, usage, architecture, REPORT, EXTENDING
examples/              runnable quickstart
results/               discovery_timeline.md · runs/ · validation/
ref-paper/ reformulate/ progress/   reproduction artifacts (acquisition, decomposition, typed ledger)
phys-agentic-loop/     methodology infra (separate repo)
```

## Results

- **Reproduced** all 13 paper pipeline components and four signature findings: the A=B `d=2` trap
  (proved + witnessed), the **12× BP-OSD distance overestimate** on high-rate codes, the
  `[[288,24,12]] = gross ⊕ gross` direct sum, and the univariate `d ∈ {2,4}` collapse.
- **Blind → validated** (held-out catalog): a Claude-as-LLM guided search rediscovered the gross
  `[[144,12,12]]` and `[[288,16,12]]` (polynomial matches); the knowledge-free GA found
  `[[72,12,6]]` and the non-CSS `[[36,2,6]]` (exact match).
- **Honest clean-room result** (`blind-zero` branch): a *paper-naive* agent, discovering from zero,
  reached only modest codes (best certified `[[144,12,8]]`, d=8) and did **not** find the d=12
  flagships — evidence that the paper's LLM-guided structural search (or prior knowledge) is what
  makes the flagship codes discoverable, not brute search. See [docs/REPORT.md](docs/REPORT.md).

## Citation

Reproduces Cruz-Benito, Cross, Kremer, Faro, *Evolutionary Discovery of Bivariate Bicycle Codes with
LLM-Guided Search*, [arXiv:2606.02418](https://arxiv.org/abs/2606.02418). Foundational BB codes:
Bravyi et al., *High-threshold and low-overhead fault-tolerant quantum memory*, Nature 627 (2024),
[arXiv:2308.07915](https://arxiv.org/abs/2308.07915).

## License

See [LICENSE](LICENSE).
