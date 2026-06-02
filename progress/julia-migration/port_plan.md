# Julia + GPU migration — port plan (canonical decomposition)

Migrate every Python subsystem (`src/qcode_discovery/`) to pure Julia (`julia/`), reimplementing the
C/C++ external deps, GPU-parallel. Python is the source of truth; each Julia module ships a parity
test matching Python on a landmark. Status: ✅ done+verified · 🟡 partial/staged · 🔴 [HOLE] not started.

| # | Subsystem | Python ref | Julia target | C/C++ dep removed | Parity landmark | Status |
|---|---|---|---|---|---|---|
| 1 | GF(2) algebra | algebra/gf2.py | gf2.jl | — | rank/nullspace identities | ✅ |
| 2 | ring + circulants | algebra/polynomials.py | polynomials.jl | — | parse + circulant | ✅ |
| 3 | BB (CSS) construction, k, FOM | codes/{bb_codes,metrics}.py | codes.jl | — | gross k=12; blind k=12 | ✅ |
| 4 | theorems thm:ab_d2, lem:crt_k | codes/theorems.py | theorems.jl | — | d=2; k=8l/3 | ✅ |
| 5 | exact distance (enumeration) | distance/distance_enum.py | distance.jl | — | (3,3) d=4 | ✅ |
| 6 | exact distance (certified, scalable) | distance/distance_milp.py (**HiGHS C++**) | distance_exact.jl | **HiGHS → pure-Julia BZ** | [[72,12,6]] d=6 certified | 🟡 (BZ done ≤ moderate d; gross d=12 needs overlapping-info-set BZ / pure-Julia MIP) |
| 7 | PBB (non-CSS) + symplectic distance | codes/pbb_codes.py, distance_milp (symplectic) | pbb.jl | HiGHS | PBB k, commutation; [[36,2,6]] | 🔴 |
| 8 | BP-OSD distance (fast UB) | distance/distance_bposd.py (**ldpc C++**) | bposd.jl | **ldpc → pure-Julia BP+OSD** | UB on gross/[[72,12,6]] | 🔴 |
| 9 | Tanner decomposability | structure/tanner.py | structure.jl | — | [[288,24,12]] = 2×[[144,12,12]] | 🔴 |
| 10 | BLISS dedup | structure/dedup.py (**igraph C**) | dedup.jl | **igraph → pure-Julia canonical form** | gross≡relabel hash; ≠ different | 🔴 |
| 11 | LC-CSS equivalence | structure/clifford_equiv.py | clifford.jl | — | CSS_GROUP / verdicts | 🔴 |
| 12 | evaluation cascade | discovery/evaluation.py | evaluation.jl | — | k→dist→FOM matches kernel | 🔴 |
| 13 | blind search / GA / MAP-Elites | discovery/search.py | search.jl | — | tiny blind run finds k>0 | 🔴 |
| 14 | generator-ansatz evolve | discovery/evolve.py | evolve.jl | — | mutation preserves weight | 🔴 |
| 15 | post-hoc validation | discovery/validation.py | validation.jl | — | landmark match verdicts | 🔴 |
| 16 | CLI | cli.py | bin/ + Comonicon/argparse | — | discover/validate/audit | 🔴 |
| G | **GPU + parallel** | (new) | gpu.jl (CUDA.jl) + threaded search | — | batched GF(2) rank == CPU; threaded speedup | 🔴 |

## C/C++ → pure-Julia strategy
- **HiGHS MILP** → Brouwer–Zimmermann codeword enumeration (done ≤ moderate d) + overlapping-info-set
  BZ / pure-Julia branch-and-bound for large d (the gross code d=12 @ n=144). No solver lib.
- **ldpc BP-OSD** → native min-sum/sum-product belief propagation + ordered-statistics post-processing
  (approximation oracle; lower-risk). GPU-batchable.
- **igraph BLISS** → pure-Julia colored-graph canonical form (individualization–refinement).

## GPU + parallel strategy
- CUDA.jl: batched GF(2) rank (k-screening of huge candidate sets) + batched BP decoding.
- Julia threads / Distributed: fan out the blind search candidate evaluations across cores/GPUs.
- CPU fallback mandatory (package loads + tests without CUDA.jl).
