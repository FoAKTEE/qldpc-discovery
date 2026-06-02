using Test
include("../src/QCodeDiscovery.jl")
using .QCodeDiscovery

# Landmark values are cross-validated against the Python qcode_discovery package (source of truth):
# the pure-Julia port reproduces construction, k, the theorem witnesses, and exact distance exactly.

@testset "GF(2) algebra" begin
    @test gf2_rank([1 0; 0 1]) == 2
    @test gf2_rank([1 1; 1 1]) == 1
    @test gf2_rank([1 1 0; 0 1 1; 1 0 1]) == 2          # the three rows sum to 0 mod 2
    @test gf2_rank(zeros(Int, 3, 3)) == 0
    M = UInt8[1 1 0 1; 0 1 1 0]
    ns = nullspace_gf2(M)
    @test size(ns, 1) == size(M, 2) - gf2_rank(M)        # rank-nullity
    for r in 1:size(ns, 1)
        @test all(iszero, (Int.(M) * Int.(ns[r, :])) .% 2)
    end
    @test in_rowspace([1 1 0; 0 1 1], [1 0 1])
    @test !in_rowspace([1 1 0; 0 1 1], [1 0 0])
end

@testset "BB construction + k (landmarks)" begin
    gross = BBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2")
    @test gross.n == 144
    @test css_valid(gross)
    @test css_k(gross) == 12                              # gross code [[144,12,12]]
    @test stabilizer_weight(gross) == 6

    # the [[144,12,12]] rediscovered blind this session — the Julia port must agree it is k=12
    blind = BBCode(12, 6, "x^9y^5+x^10y^2+x^11y^2", "x^2y^4+x^2y^5+x^5")
    @test css_valid(blind)
    @test css_k(blind) == 12
end

@testset "theorem witnesses" begin
    w = verify_ab_d2(6, 6, "1+x+y")                       # thm:ab_d2 — A=B ⇒ d=2
    @test w.k == 8
    @test w.d == 2
    @test w.claim_d2

    @test verify_crt_k(6, 6).match && verify_crt_k(6, 6).k == 16   # lem:crt_k — k = 8l/3
    @test verify_crt_k(9, 9).match && verify_crt_k(9, 9).k == 24
end

@testset "exact distance (pure Julia; replaces HiGHS MILP)" begin
    c = BBCode(3, 3, "1+x+y", "1+x^2+y^2")
    @test css_k(c) == 4
    r = css_distance_enum(c; max_weight=6)
    @test r.dX == r.dZ == 4                               # matches the Python MILP (d=4)
    @test r.d == 4 && r.exhausted
    @test fom(c.n, 4, r.d) == 4 * 4^2 / 18
end
