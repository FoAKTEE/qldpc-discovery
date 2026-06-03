# qldpc-discovery

> Verified, **catalog-blind** discovery of bivariate-bicycle (BB) quantum LDPC codes — a reproduction
> of *"Evolutionary Discovery of Bivariate Bicycle Codes with LLM-Guided Search"*
> ([arXiv:2606.02418](https://arxiv.org/abs/2606.02418), Cruz-Benito, Cross, Kremer, Faro; IBM).

The LLM/search proposes generator ansätze; a **scientific kernel admits** them. Discovery runs blind
to the paper; the catalog is consulted only post-hoc, as a held-out test set.

## Two parallel implementations — pick one

| | [`python/`](python/) | [`julia/`](julia/) |
|---|---|---|
| Role | original reference implementation | pure-Julia + GPU port |
| Dependencies | `numpy`, `scipy`, optional `ldpc` + `python-igraph` (C/C++) | **pure Julia, no C/C++** (optional `CUDA.jl`) |
| Exact distance | HiGHS MILP | certified Brouwer–Zimmermann solver |
| BP-OSD decoder | `ldpc` (C++) | native belief-propagation + OSD |
| Graph dedup | `igraph` BLISS (C) | individualization-refinement canonical form |
| Parallel / GPU | — | `Threads` + a CUDA kernel (A100-verified) |
| Tests | 54 (pytest) | 55 (`Pkg.test`) |

Both implement the same pipeline — construction, `k`, exact/BP-OSD distance, FOM, Tanner
decomposability, dedup, local-Clifford equivalence, the staged blind-discovery cascade, and post-hoc
validation — and the Julia port is cross-validated against the Python reference on every landmark.

```bash
# Python
cd python && pip install ".[decoders]" && qcode-discover --type css --stage3-verify

# Julia
julia --project=julia -e 'using Pkg; Pkg.instantiate()'
julia --project=julia -t auto julia/bin/qcode-discover.jl --lattices 6x6,12x6
```

See [`python/README.md`](python/README.md) and [`julia/README.md`](julia/README.md) for details,
and [`julia/examples/demo.ipynb`](julia/examples/demo.ipynb) for a runnable walkthrough.

## Results

- Reproduced all 13 paper pipeline components and four signature findings (the A=B `d=2` trap, the
  **12× BP-OSD overestimate**, `[[288,24,12]] = gross ⊕ gross`, and the univariate `d ∈ {2,4}` collapse).
- Blind → validated: a guided search rediscovered the gross `[[144,12,12]]` and `[[288,16,12]]`; a
  knowledge-free GA found `[[72,12,6]]` and the non-CSS `[[36,2,6]]`.

## Citation & license

Reproduces Cruz-Benito, Cross, Kremer, Faro, arXiv:2606.02418. Foundational BB codes: Bravyi et al.,
*High-threshold and low-overhead fault-tolerant quantum memory*, Nature 627 (2024),
[arXiv:2308.07915](https://arxiv.org/abs/2308.07915). Licensed under [LICENSE](LICENSE) (LGPL-2.1).
