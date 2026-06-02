# QCodeDiscovery.jl

A **pure-Julia** rewrite of the qcode-discovery package (reproduction of arXiv:2606.02418 — blind
discovery of bivariate-bicycle quantum LDPC codes). **No C/C++ dependencies**: the scientific kernel
is implemented from first principles, and the external compiled libraries the Python version relied
on (HiGHS for MILP, `ldpc` for BP-OSD) are being replaced with native Julia algorithms.

## Status — this is an in-progress rewrite (honest)

| Component | Python (orig.) | Julia (here) |
|---|---|---|
| GF(2) algebra (rank, RREF, null space) | numpy | ✅ ported (`gf2.jl`) |
| Ring `F2[x,y]/(xˡ−1,yᵐ−1)` + circulants | numpy | ✅ ported (`polynomials.jl`) |
| BB (CSS) construction, k, FOM | numpy | ✅ ported (`codes.jl`) |
| Theorem witnesses `thm:ab_d2`, `lem:crt_k` | numpy | ✅ ported (`theorems.jl`) |
| **Exact distance** | **HiGHS MILP (C++)** | ✅ **pure-Julia min-weight-logical search** (`distance.jl`) — small/moderate codes |
| Scalable exact distance (e.g. d=12 @ n=144) | HiGHS branch&bound | ⏳ staged — pure-Julia B&B / information-set search |
| BP-OSD distance (fast upper bound) | `ldpc` (C++) | ⏳ staged — pure-Julia belief-propagation + OSD |
| PBB (non-CSS) construction | numpy | ⏳ staged |
| BLISS dedup / LC equivalence | igraph (C) | ⏳ staged (pure-Julia graph canonicalization) |
| Blind search / GA / cascade | — | ⏳ staged |

The ✅ rows are **cross-validated against the Python package** (identical results on every landmark:
gross k=12, the blindly-rediscovered [[144,12,12]] k=12, `lem:crt_k` k=8ℓ/3, `thm:ab_d2` d=2, and the
(3,3) code's exact d=4 — the pure-Julia distance matches the HiGHS MILP). 24 tests pass.

## Replacing the C/C++ dependencies (the hard part)

- **HiGHS MILP → pure Julia.** Exact distance is the smallest weight at which a nontrivial logical
  exists; `min_weight_logical` certifies this by increasing-weight search (a complete certificate up
  to `max_weight`), with no solver. This already reproduces the MILP exactly at small/moderate sizes.
  Certifying large codes (the gross code's d=12 at n=144) needs the staged branch-and-bound /
  information-set search — a real solver to write in Julia, not a HiGHS wrapper.
- **`ldpc` BP-OSD → pure Julia.** A native belief-propagation + ordered-statistics decoder is staged
  (the fast Stage-2 upper bound). It is an approximation oracle, so it is lower-risk to reimplement.

## Run

```bash
julia --project=julia julia/test/runtests.jl     # 24 tests
```
```julia
include("julia/src/QCodeDiscovery.jl"); using .QCodeDiscovery
gross = BBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2")   # the gross code
css_k(gross)                                       # 12
css_distance_enum(BBCode(3,3,"1+x+y","1+x^2+y^2")) # (d=4, dX=4, dZ=4, exhausted=true)
```

The Python package remains in the repository (`src/qcode_discovery/`) until this Julia port reaches
feature parity; it is the reference the Julia results are validated against.
