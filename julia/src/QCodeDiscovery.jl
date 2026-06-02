"""
QCodeDiscovery — a Julia rewrite of the qcode-discovery package (arXiv:2606.02418):
verified, catalog-blind discovery of bivariate-bicycle (BB) quantum LDPC codes.

This is a PURE-JULIA port: no C/C++ dependencies. The scientific kernel (GF(2) algebra,
BB construction, k, FOM, the two theorem witnesses, and exact minimum-distance certification)
is implemented from first principles. The exact distance replaces the HiGHS (C++) MILP via a
minimum-weight-logical search; the scalable solver and the BP-OSD decoder are staged (see README).
"""
module QCodeDiscovery

include("gf2.jl")
include("polynomials.jl")
include("codes.jl")
include("distance.jl")
include("distance_exact.jl")
include("theorems.jl")
# migrated subsystems (wave 1) — pure Julia, no C/C++ (cross-validated vs the Python package)
include("pbb.jl")          # PBB (non-CSS) construction + symplectic structure
include("tanner.jl")       # Tanner-graph decomposability (union-find)
include("dedup.jl")        # BLISS dedup -> pure-Julia individualization-refinement canonical form
include("clifford.jl")     # LC-CSS equivalence (Hadamard 2-coloring + rank condition)
include("bposd.jl")        # ldpc BP-OSD -> pure-Julia belief propagation + OSD
include("gpu.jl")          # data-parallel GF(2) (threads + CUDA.jl path, CPU fallback)

# GF(2) algebra
export as_f2, rref, gf2_rank, nullspace_gf2, in_rowspace
# ring + construction
export parse_terms, circulant, BBCode, css_k, fom, stabilizer_weight, css_valid
# distance (pure-Julia exact)
export css_distance_enum, min_weight_logical, min_distance_bz
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
export batched_rank, batched_css_k, cuda_available

end # module
