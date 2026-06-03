using Test
# Regression test for the _independent_mod / css_logicals heap-corruption crash.
#
# History: the catalog-blind search (-t 200, thousands of candidates) aborted abruptly — exit 1,
# NO Julia exception, top-level try/catch never firing, --check-bounds=yes no help.  Root-caused
# to QCodeDiscovery._independent_mod (called by css_logicals -> bposd_distance) on rare degenerate
# high-nullity BB codes: it rebuilt a growing stacked matrix and recomputed gf2_rank FROM SCRATCH on
# every candidate row, churning hundreds of large short-lived UInt8 matrices through the allocator
# in a tight loop and intermittently corrupting the heap (SIGSEGV/SIGABRT).  The crash was
# layout/timing sensitive (masked under gdb and MALLOC_CHECK_=3) — a genuine memory fault, not a
# logic/bounds error.  Fixed by the one-pass incremental-basis implementation in distance/bposd.jl.
#
# The (l,m,A,B) below are EXACT candidates captured (with stage logging) from runs that crashed.
# Case 1 ((14,35), the densest crasher) reproduced the abort essentially every run in isolation;
# this test reduces it (and four siblings) repeatedly and asserts a correct, finite result.

@testset "BP-OSD _independent_mod degenerate-code crash regression — bposd.jl" begin
    # (l, m, A, B, expected k).  A/B in x^a*y^b string form (matches the (a,b) supports captured).
    cases = [
        (14, 35, "x^2*y^25+x^3*y^29+x^6*y^9", "y^0+x^4*y^24+x^10*y^15", 6),
        ( 9, 53, "x^2*y^7+x^6*y^42+x^7*y^4",  "x^4*y^42+x^5*y^10+x^6*y^30", 4),
        ( 7, 58, "y^49+x^4*y^14+x^6*y^47",    "x*y^57+x^2*y^2+x^6",         6),
        (15, 32, "x^3*y^4+x^8*y^13+x^13*y^12","x^4*y^15+x^6*y^31+x^14*y^3", 4),
        ( 7, 52, "x^3*y^26+x^4*y^47+x^6*y^4", "x*y^38+x^5*y^29+x^6*y^43",   6),
    ]

    for (l, m, A, B, kexp) in cases
        c = BBCode(l, m, A, B)
        @test css_k(c) == kexp

        # css_logicals: the routine that used to crash.  X- and Z-logical bases must each have
        # exactly k rows of length n (a full set of logical-operator representatives).
        X, Z = css_logicals(c.HX, c.HZ)
        @test size(X) == (kexp, c.n)
        @test size(Z) == (kexp, c.n)
        # Z-logicals lie in ker(H_X); X-logicals in ker(H_Z) (mod 2).
        @test all(iszero, (Int.(c.HX) * permutedims(Int.(Z))) .% 2)
        @test all(iszero, (Int.(c.HZ) * permutedims(Int.(X))) .% 2)

        # Full BP-OSD pipeline must run to completion and return a sane positive upper bound.
        # Repeat to exercise the (formerly) allocation-churning path many times in one process.
        local r
        for _ in 1:5
            r = bposd_distance(c; trials=8, seed=151130, max_iter=10)
        end
        @test r.d_bound !== nothing
        @test r.d_bound > 0 && r.d_bound <= c.n
    end
end
