#!/usr/bin/env julia
# QCodeDiscovery.jl quickstart — run with:
#   julia --project=julia -t auto julia/examples/quickstart.jl
#
# Shows the kernel (construct + verify), the pure-Julia exact distance solver (replaces the HiGHS C++
# MILP), and a tiny BLIND discovery. The catalog is NEVER read here; validation is a separate post-hoc
# step against built-in landmark codes.

include(joinpath(@__DIR__, "..", "src", "QCodeDiscovery.jl"))
using .QCodeDiscovery

# 1. Construct the gross code [[144,12,12]] and verify its encoding dimension.
gross = BBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2")
println("gross code: n=$(gross.n), k=$(css_k(gross)), stab weight=$(stabilizer_weight(gross)), FOM(d=12)=$(fom(144,12,12))")

# 2. A theorem witness: every A=B code has distance exactly 2 (thm:ab_d2).
w = verify_ab_d2(6, 6, "1+x+y")
println("thm:ab_d2 on a (6,6) A=B code: k=$(w.k), d=$(w.d)")

# 3. Certified exact distance via the pure-Julia Brouwer–Zimmermann solver (no C/C++ MILP).
r = min_distance_bz(BBCode(6, 6, "x^3+y+y^2", "y^3+x+x^2"))
println("[[72,12,6]]: BZ exact d=$(r.d) (certified=$(r.certified))")

# 4. A tiny BLIND discovery run (naive seeds, FOM fitness; NO paper knowledge).
println("\nblind discovery at (6,6) (catalog-blind):")
out = blind_search_css([(6, 6)]; n_random=200, distance_budget=4, generations=0,
                       distance_method=:bposd, seed=1)
for el in out.archive_elites[1:min(4, end)]
    println("  found [[$(el.n),$(el.k),$(el.d)]] FOM=$(round(el.fom, digits=2))")
end

# 5. Post-hoc validation against the paper's landmark codes (the held-out test set).
println("\npost-hoc validation:")
rep = validate(out.archive_elites; kind=:css)
println("  reference codes: $(rep.n_reference_codes); summary: $(rep.summary)")
