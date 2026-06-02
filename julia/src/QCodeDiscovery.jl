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

# GF(2) algebra
export as_f2, rref, gf2_rank, nullspace_gf2, in_rowspace
# ring + construction
export parse_terms, circulant, BBCode, css_k, fom, stabilizer_weight, css_valid
# distance (pure-Julia exact)
export css_distance_enum, min_weight_logical, min_distance_bz
# theorem witnesses
export verify_ab_d2, verify_crt_k

end # module
