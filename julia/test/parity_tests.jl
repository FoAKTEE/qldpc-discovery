using Test, Random
# Parity tests for the wave-1 migrated subsystems (pbb, tanner, dedup, clifford, bposd, gpu).
# Landmark values were cross-validated against the Python qcode_discovery package (source of truth);
# these re-verify them in the INTEGRATED module, with extra cases for the from-scratch C/C++ replacements.

@testset "PBB (non-CSS) — pbb.jl" begin
    # commuting weight-3 4-tuple at (6,6): Python -> n=72, k=4, valid, mixed (non-CSS)
    c = PBBCode(6, 6, "x^4+xy^4+xy^2", "y^5+x^4+x^3y",
                "x^2y+xy^3+x^5y^5", "x^4y^4+x^4y^2+x")
    @test c.n == 72
    @test pbb_k(c) == 4
    @test pbb_has_mixed_generator(c) && !pbb_is_pure_css(c)
    # pure-CSS reduction (C=D="") -> a valid CSS code, not mixed
    p = PBBCode(6, 6, "x^4+xy^4+xy^2", "y^5+x^4+x^3y", "", "")
    @test pbb_is_pure_css(p) && !pbb_has_mixed_generator(p)
    # non-commuting tuple must be rejected (mirrors Python ValueError)
    @test_throws Exception PBBCode(6, 6, "1+x", "1+y", "x", "y^2")
end

@testset "Tanner decomposability — tanner.jl" begin
    gross = BBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2")
    @test qubit_components(gross.HX, gross.HZ) == 1 && !is_decomposable(gross)
    dec = BBCode(6, 6, "x^2+x^4", "y^2+y^4")            # Python: 4 components (decomposable)
    @test qubit_components(dec.HX, dec.HZ) == 4 && is_decomposable(dec)
end

@testset "BLISS dedup -> pure-Julia canonical form — dedup.jl" begin
    gross = BBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2")
    h = canonical_hash(gross.HX, gross.HZ)
    # invariant under qubit relabeling (column permutation), across several permutations
    for s in (1, 7, 42, 2024)
        Random.seed!(s)
        p = randperm(size(gross.HX, 2))
        @test canonical_hash(gross.HX[:, p], gross.HZ[:, p]) == h
    end
    # distinct from a different code (same n) AND a different-n code
    other144 = BBCode(12, 6, "1+x+y", "1+x^2+y^2")
    other72 = BBCode(6, 6, "x^3+y+y^2", "y^3+x+x^2")
    @test canonical_hash(other144.HX, other144.HZ) != h
    @test canonical_hash(other72.HX, other72.HZ) != h
    # the blindly-rediscovered [[144,12,12]] IS the gross code -> same canonical hash
    blind = BBCode(12, 6, "x^9y^5+x^10y^2+x^11y^2", "x^2y^4+x^2y^5+x^5")
    @test canonical_hash(blind.HX, blind.HZ) == h
end

@testset "LC-CSS equivalence — clifford.jl" begin
    gross = BBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2")
    SX, SZ = css_stabilizer(gross)
    @test lc_css_classify(SX, SZ, gross.l * gross.m).verdict == "CSS_GROUP"
    @test is_css_group(SX, SZ)
end

@testset "BP-OSD (pure-Julia decoder) — bposd.jl" begin
    gross = BBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2")
    r = bposd_distance(gross; trials=200, seed=0)        # Python ldpc: d_bound=12
    @test r.d_bound == 12 && r.d_X == 12                  # d_bound (the estimate) matches Python;
    # NB: per-sector bounds are stochastic UPPER bounds (d_Z may be looser at low trials) — honest.
end

@testset "Data-parallel GF(2) — gpu.jl" begin
    gross = BBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2")
    c72 = BBCode(6, 6, "x^3+y+y^2", "y^3+x+x^2")
    mats = [gross.HX, gross.HZ, c72.HX, c72.HZ]
    @test batched_rank(mats) == [gf2_rank(m) for m in mats]      # threaded == serial
    cands = [(12, 6, "y+y^2+x^3", "y^3+x+x^2"), (6, 6, "x^3+y+y^2", "y^3+x+x^2")]
    @test batched_css_k(cands) == [css_k(gross), css_k(c72)]     # == 12, 12
    # cuda_batched_rank falls back to the bit-identical CPU path when CUDA.jl isn't loaded
    @test cuda_batched_rank(mats) == [gf2_rank(m) for m in mats]
end

@testset "discovery cascade + blind search — evaluation/search.jl" begin
    e = evaluate_css(3, 3, "1+x+y", "1+x^2+y^2"; distance_method=:milp)   # == Python MILP
    @test e.k == 4 && e.d == 4 && e.exact && e.fom == 4 * 4^2 / 18
    # END-TO-END: a blind search runs in pure Julia and populates the archive
    out = blind_search_css([(6, 6)]; n_random=120, distance_budget=4, generations=0,
                           distance_method=:bposd, seed=1)
    @test out.n_evaluated == 120
    @test length(out.archive_elites) >= 1
    @test all(el -> el.k > 0 && el.fom > 0 && el.n == 72, out.archive_elites)
end

@testset "post-hoc validation — validation.jl" begin
    rep = validate([(n=144, k=12, d=12, exact=true, l=12, m=6,
                     A="y+y^2+x^3", B="y^3+x+x^2", fom=12.0)]; kind=:css)
    @test rep.results[1].verdict in ("MATCH", "POLY_MATCH")
    rep2 = validate([(n=72, k=12, d=6, exact=false, l=6, m=6,
                      A="1+x+y", B="1+x^2+y^2", fom=6.0)]; kind=:css)
    @test rep2.results[1].verdict in ("UB_CONSISTENT", "MATCH", "POLY_MATCH")
end

@testset "PBB symplectic exact distance — pbb_distance.jl" begin
    @test symplectic_distance(PBBCode(2, 3, "1+y", "1+y", "x", "xy")).d == 3     # Python MILP d=3
    r = symplectic_distance(PBBCode(2, 2, "1+x", "1+x", "x", "x"))
    @test r.d == 2 && r.certified                                                # Python MILP d=2
end
