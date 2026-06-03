# QCodeDiscovery.jl

> A **pure-Julia**, GPU-accelerated package for verified, catalog-blind discovery of bivariate-bicycle
> (BB) and perturbed-BB (PBB) quantum LDPC codes — a complete Julia migration of the Python
> reproduction of *"Evolutionary Discovery of Bivariate Bicycle Codes with LLM-Guided Search"*
> ([arXiv:2606.02418](https://arxiv.org/abs/2606.02418)).

`julia ≥ 1.9` · **no C/C++ dependencies** · optional `CUDA.jl` (GPU) · **55 tests passing**

The LLM/search proposes generator ansätze; a scientific kernel **admits** them. Discovery runs **blind**
to the paper; the catalog is consulted only post-hoc, as a held-out test set. Every result is
cross-validated against the reference Python package.

## No C/C++ — the compiled dependencies are reimplemented natively

| Python dependency (C/C++) | Pure-Julia replacement |
|---|---|
| HiGHS MILP (exact distance) | `min_distance_bz` — Brouwer–Zimmermann certified codeword enumeration |
| `ldpc` BP-OSD decoder | `bposd_distance` — native belief propagation (sum-product / min-sum) + OSD |
| `igraph` BLISS (graph canonicalization) | `canonical_hash` — individualization-refinement canonical form |

## Install

```julia
import Pkg; Pkg.develop(path="julia")     # or Pkg.add(url=...) once published
using QCodeDiscovery
```
GPU is **optional** (a package extension): `Pkg.add("CUDA")` activates the CUDA batched-GF(2) kernel;
without it, everything runs on CPU (multithreaded).

## Quickstart

```julia
using QCodeDiscovery

gross = BBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2")    # the gross code [[144,12,12]]
css_k(gross)                                        # 12
min_distance_bz(BBCode(6,6,"x^3+y+y^2","y^3+x+x^2"))   # certified d=6 (pure-Julia exact solver)

# blind discovery (catalog-blind), then post-hoc validation
out = blind_search_css([(6,6)]; n_random=400, distance_budget=8, distance_method=:bposd, seed=0)
validate(out.archive_elites; kind=:css)             # MATCH / POLY_MATCH / UB_CONSISTENT / NOVEL
```
See [`examples/quickstart.jl`](examples/quickstart.jl) and the CLI [`bin/qcode-discover.jl`](bin/qcode-discover.jl).

## Capabilities

- **Kernel** — GF(2) algebra; BB (CSS) & PBB (non-CSS) construction; `k` via GF(2) rank; FOM; the two
  paper theorem witnesses (`thm:ab_d2`, `lem:crt_k`).
- **Distance** — exact via Brouwer–Zimmermann (certified; e.g. `[[72,12,6]]` d=6 in 0.2 s) and
  enumeration; symplectic exact distance for PBB; BP-OSD stochastic upper bound.
- **Structure** — Tanner-graph decomposability; pure-Julia colored-graph canonical form (dedup);
  local-Clifford CSS-equivalence.
- **Discovery** — staged cascade (k → distance → FOM) over a MAP-Elites archive + GA; post-hoc
  validation vs built-in landmark codes.
- **Parallel / GPU** — `Threads.@threads` batched GF(2) across CPU cores; a real CUDA kernel
  (A100-verified, bit-identical to CPU) via the optional `CUDA` extension.

## Layout

```
julia/
  Project.toml                  package + [deps] + [weakdeps]/[extensions] for optional CUDA
  src/QCodeDiscovery.jl         module (includes the subpackages below, in dependency order)
    algebra/    gf2.jl · polynomials.jl
    codes/      codes.jl · pbb.jl · theorems.jl
    distance/   distance.jl · distance_exact.jl · bposd.jl · pbb_distance.jl
    structure/  tanner.jl · dedup.jl · clifford.jl
    discovery/  evaluation.jl · search.jl · evolve.jl · validation.jl
    parallel/   gpu.jl · gpu_cuda.jl
  ext/QCodeDiscoveryCUDAExt.jl  GPU kernel (loaded only when CUDA.jl is present)
  test/runtests.jl              55 tests (kernel + parity vs the Python reference)
  examples/quickstart.jl        runnable script
  examples/demo.ipynb           Jupyter (Julia kernel) usage demonstration
  bin/qcode-discover.jl         CLI
```

## Test

```bash
julia --project=julia -t auto julia/test/runtests.jl     # 55 tests
```

## Parity & honest status

Every module is cross-validated against the reference Python package (`../src/qcode_discovery/`):
gross k=12; the blindly-rediscovered `[[144,12,12]]` (same canonical hash as gross); `[[72,12,6]]` d=6;
`thm:ab_d2` d=2; `lem:crt_k` k=8ℓ/3; PBB commutation & symplectic d; dedup hash invariance; LC verdicts;
BP-OSD d_bound=12; GPU rank == CPU rank. **Staged:** certifying the gross code's d=12 *exactly* in
Julia (the BZ solver certifies moderate distances; large-d needs the overlapping-information-set
extension — BP-OSD already gives the d=12 upper bound), and `.tex` catalog parsing (built-in landmark
codes are used instead).

## License

See [LICENSE](LICENSE) (LGPL-2.1). Reproduces Cruz-Benito, Cross, Kremer, Faro, arXiv:2606.02418.
