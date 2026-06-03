# Regression: the Brouwer–Zimmermann / enumeration distance routines must run ALLOCATION-FREE in
# their hot loops. A prior version captured-and-reassigned locals (`best`, `enumerated`) inside a
# `do`-block closure, which Julia BOXES -> ~5 heap allocations PER COMBINATION. The `cap` bounded the
# number of combinations but NOT memory, so on high-κ codes (weight-8/9 [[144,k,·]] from the
# varying-weight blind search) the certifier churned billions of allocations and OOM-crashed the
# process UNCATCHABLY (a C-level abort that try/catch cannot intercept). These tests pin:
#   (1) no crash, (2) allocations << 1 per enumerated combination (the boxing produced ~5), (3) sane d.

using Test

# Captured crashers: high check-weight (8/9), high-k, n=144 codes that OOM-crashed certify.jl.
const _HARD_CSS = [
    (12, 6, "x^4*y^4+x^6*y^0+x^9*y^1+x^9*y^5+x^11*y^1", "x^1*y^3+x^5*y^1+x^5*y^3+x^7*y^1"),
    (12, 6, "x^2*y^5+x^4*y^0+x^8*y^5+x^9*y^4", "x^0*y^2+x^4*y^3+x^7*y^1+x^10*y^4+x^11*y^1"),
    (12, 6, "x^1*y^3+x^2*y^1+x^4*y^2+x^5*y^5", "x^2*y^1+x^4*y^2+x^10*y^5+x^11*y^4"),
]

@testset "BZ logical-distance allocation-free regression — distance_exact.jl" begin
    for (l, m, A, B) in _HARD_CSS
        c = BBCode(l, m, A, B)
        @test css_k(c) > 0
        cap = 1_000_000
        r = @timed min_distance_bz(c; cap=cap)         # must NOT crash / OOM
        res = r.value
        @test res.d > 0 && res.d <= c.n                # found a real logical, sane weight
        @test res.enumerated > 0
        # Hot loop allocation-free: far fewer than 0.5 heap allocs per enumerated combination
        # (the boxing bug produced ~5/combination); generous constant allows rref/packing setup.
        @test Base.gc_alloc_count(r.gcstats) < 0.5 * res.enumerated + 200_000
    end
end

@testset "Column enumeration allocation-free regression — distance.jl" begin
    # css_distance_enum enumerates weight-w error vectors; the old version allocated a matrix–vector
    # product PER combination. Run it where it sweeps ~1e6 combinations and pin a bound the per-combo
    # allocation would blow past.
    c = BBCode(6, 6, "x^1*y^2+x^3+y^4", "x^2+y^1+y^3")
    r = @timed css_distance_enum(c; max_weight=4)
    @test r.value.d == -1 || r.value.d > 0
    @test Base.gc_alloc_count(r.gcstats) < 3_000_000   # per-combination matvec alloc would exceed this
end

@testset "PBB symplectic-distance allocation-free + sane — pbb_distance.jl" begin
    # CSS-reduced PBB (C=D="" always commutes) of the known [[18,4,4]] code — cross-validates the
    # symplectic BZ path against the CSS distance AND exercises the allocation-free hot loop.
    c = PBBCode(3, 3, "1+x+y", "1+x^2+y^2", "", "")
    @test pbb_k(c) == 4
    r = @timed symplectic_distance(c; cap=2_000_000)   # must NOT crash / OOM
    @test r.value.d == 4 && r.value.certified          # matches the CSS [[18,4,4]] distance
    @test Base.gc_alloc_count(r.gcstats) < 0.5 * r.value.enumerated + 200_000
end
