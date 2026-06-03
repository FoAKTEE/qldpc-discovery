"""
QCodeDiscovery — a Julia rewrite of the qcode-discovery package (arXiv:2606.02418):
verified, catalog-blind discovery of bivariate-bicycle (BB) quantum LDPC codes.

This is a PURE-JULIA port: no C/C++ dependencies. The scientific kernel (GF(2) algebra,
BB construction, k, FOM, the two theorem witnesses, and exact minimum-distance certification)
is implemented from first principles. The exact distance replaces the HiGHS (C++) MILP via a
minimum-weight-logical search; the scalable solver and the BP-OSD decoder are staged (see README).
"""
module QCodeDiscovery

# Source is organized into logical subpackages (mirroring the Python layout); files are included
# in dependency order (everything lives in one flat module scope).
include("algebra/gf2.jl")           # GF(2) rank / RREF / null space
include("algebra/polynomials.jl")   # ring F2[x,y]/(xˡ−1,yᵐ−1) + circulants
include("codes/codes.jl")           # BB (CSS) construction, k, FOM
include("distance/distance.jl")          # enumeration distance
include("distance/distance_exact.jl")    # Brouwer–Zimmermann certified exact distance (HiGHS replacement)
include("distance/isd.jl")               # Lee–Brickell ISD: tight UPPER bound at large n (refutes overestimates)
include("codes/theorems.jl")        # thm:ab_d2, lem:crt_k witnesses
include("codes/pbb.jl")             # PBB (non-CSS) construction
include("structure/tanner.jl")      # Tanner-graph decomposability (union-find)
include("structure/dedup.jl")       # BLISS dedup -> pure-Julia individualization-refinement canonical form
include("structure/clifford.jl")    # LC-CSS equivalence (Hadamard 2-coloring + rank condition)
include("distance/bposd.jl")        # ldpc BP-OSD -> pure-Julia belief propagation + OSD
include("parallel/gpu.jl")          # data-parallel GF(2) (threads + CUDA.jl path, CPU fallback)
include("parallel/gpu_cuda.jl")     # GPU batched GF(2) rank (real CUDA kernel via ext/, A100-tested)
include("discovery/evaluation.jl")  # staged evaluation cascade (k -> distance -> FOM)
include("discovery/search.jl")      # blind search + MAP-Elites archive + GA
include("discovery/evolve.jl")      # generator-ansatz program evolution
include("discovery/validation.jl")  # post-hoc validation vs built-in landmark codes
include("distance/pbb_distance.jl") # PBB exact symplectic distance (BZ; replaces HiGHS)

# GF(2) algebra
export as_f2, rref, gf2_rank, nullspace_gf2, in_rowspace
# ring + construction
export parse_terms, circulant, BBCode, css_k, fom, stabilizer_weight, css_valid
# distance (pure-Julia exact)
export css_distance_enum, min_weight_logical, min_distance_bz
# distance (tight upper bound at large n via information-set decoding)
export min_distance_isd
# theorem witnesses
export verify_ab_d2, verify_crt_k
# PBB (non-CSS)
export PBBCode, pbb_k, pbb_is_pure_css, pbb_has_mixed_generator, pbb_is_css_group,
       pbb_reduced_condition_symmetric, pbb_symplectic_gram_zero
# structure
export qubit_components, is_decomposable, canonical_hash, dedup_bliss
# local-Clifford equivalence
export hadamard_two_coloring, is_css_group, uniform_clifford_lc_css, lc_css_classify, css_stabilizer
# BP-OSD (pure-Julia decoder) + logicals
export bposd_distance, css_logicals
# data-parallel GF(2) (threads / GPU)
export batched_rank, batched_css_k, cuda_available, cuda_batched_rank, cuda_ext_loaded
# discovery pipeline
export screen_k_css, evaluate_css, bbcode_from_terms, random_polynomial, mutate_polynomial,
       blind_search_css, GeneratorAnsatz, random_ansatz, mutate_ansatz, ansatz_fitness, evolve_ansaetze
# post-hoc validation
export landmark_codes, validate
# PBB exact symplectic distance
export symplectic_distance

end # module
