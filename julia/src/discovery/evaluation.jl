# Staged evaluation cascade — the BLIND fitness function for code discovery.
# Pure-Julia port of qcode_discovery/discovery/evaluation.py.
#
# Catalog-blind by construction: this module uses ONLY the kernel verifiers (BB construction,
# k via GF(2) rank, exact distance, FOM). It NEVER reads the paper catalog or any reported
# [[n,k,d]]. A candidate's fitness is computed from first principles, exactly as the paper does:
#   Stage 1 (cheap):   k via GF(2) rank — reject k = 0.
#   Stage 2 (costly):  distance via exact BZ (replaces the C++ MILP) or BP-OSD upper bound.
#   FOM = k d^2 / n;  d/sqrt(n) reported for the trust heuristic.
# Paper anchor: arXiv:2606.02418 sec IV.B (cascade), sec II.C (FOM), sec V.D (trust).
#
# NOTE ON DISTANCE METHODS (faithful to Python `distance_method`):
#   :milp / :exact  -> Python "milp": EXACT distance. The Python package uses the HiGHS (C++) MILP
#                      `css_distance_milp`; ABSOLUTELY NO C/C++ here, so we substitute the pure-Julia
#                      Brouwer–Zimmermann certifier `min_distance_bz` (codes.jl/distance_exact.jl),
#                      which returns the SAME exact distance with a certificate (`exact=certified`).
#   :bposd          -> Python "bposd": STOCHASTIC UPPER bound via the pure-Julia BP-OSD decoder.
#   :enum           -> Python "enum": exhaustive small-weight enumeration `css_distance_enum`.

# --------------------------------------------------------------------------------------------
# Term-list BB construction. The discovery pipeline carries polynomials as term lists
# Vector{Tuple{Int,Int}} (the (a,b) monomial supports), NOT strings. We build a BBCode directly
# from term lists here WITHOUT redefining the string `BBCode` constructor in codes.jl.
# --------------------------------------------------------------------------------------------

"""Normalize a term list: reduce exponents mod (l,m), drop monomials that cancel mod 2, sort/dedup.
Mirrors qcode_discovery.algebra.polynomials.normalize_terms."""
function normalize_terms(terms, l::Int, m::Int)
    counts = Dict{Tuple{Int,Int},Int}()
    for (a, b) in terms
        key = (mod(a, l), mod(b, m))
        counts[key] = get(counts, key, 0) + 1
    end
    out = Tuple{Int,Int}[t for (t, c) in counts if isodd(c)]
    return sort(out)
end

"""Build a BBCode from polynomial TERM LISTS `A`, `B` (each a Vector{Tuple{Int,Int}} of (a,b)
monomials x^a y^b). Same matrices as the string constructor; this is the form the search uses."""
function bbcode_from_terms(l::Int, m::Int, A, B)
    At = normalize_terms(A, l, m)
    Bt = normalize_terms(B, l, m)
    Ac = circulant(At, l, m)
    Bc = circulant(Bt, l, m)
    HX = hcat(Ac, Bc)
    HZ = hcat(permutedims(Bc), permutedims(Ac))   # (B^T | A^T)
    return BBCode(l, m, At, Bt, HX, HZ, 2 * l * m)
end

"""Coerce A/B (either a polynomial string or a term list) into a BBCode on lattice (l,m)."""
_to_bbcode(l::Int, m::Int, A::AbstractString, B::AbstractString) = BBCode(l, m, A, B)
_to_bbcode(l::Int, m::Int, A, B) = bbcode_from_terms(l, m, A, B)

# --------------------------------------------------------------------------------------------
# Stage 1 — cheap k screen.
# --------------------------------------------------------------------------------------------

"""Stage 1: encoding dimension k of the CSS BB code (GF(2) rank). 0 => discard."""
function screen_k_css(l::Int, m::Int, A, B)
    code = _to_bbcode(l, m, A, B)
    return css_k(code)
end

# --------------------------------------------------------------------------------------------
# Stage 2 — full evaluation.
# --------------------------------------------------------------------------------------------

"""Full blind evaluation of a CSS BB candidate. Returns a NamedTuple with the cascade outcome:

    (l, m, n, k, d, exact, fom, d_over_sqrt_n, A, B, stab_weight, stage, trusted)

`distance_method`:
  :milp / :exact -> EXACT distance via pure-Julia Brouwer–Zimmermann (`exact` = certified).
  :bposd         -> STOCHASTIC UPPER bound via pure-Julia BP-OSD (`exact` = false).
  :enum          -> exhaustive small-weight enumeration (`exact` = exhausted within max_weight).

`time_limit` mirrors Python: for :bposd it sets trials = round(time_limit*100) (min 100), matching
Python `trials=int(time_limit*100) or 100`. No paper knowledge used; (A,B) is the only input."""
function evaluate_css(l::Int, m::Int, A, B; distance_method::Symbol=:milp, time_limit::Real=3.0,
                      enum_max_weight::Int=6, cap::Int=50_000_000, isd_iters::Int=800)
    code = _to_bbcode(l, m, A, B)
    k = css_k(code)
    d = nothing
    exact = false
    fomv = 0.0
    dsn = nothing
    trusted = false
    stage = 1
    if k > 0
        stage = 2
        if distance_method === :enum
            dres = css_distance_enum(code; max_weight=enum_max_weight)
            d = dres.d > 0 ? dres.d : nothing
            exact = dres.exhausted
        elseif distance_method === :bposd
            trials = max(round(Int, time_limit * 100), 100)
            dres = bposd_distance(code; trials=trials)
            d = dres.d_bound
            exact = false
        elseif distance_method === :isd
            # Lee–Brickell ISD: TIGHT upper bound that REFUTES BP-OSD overestimates -> a trustworthy
            # search fitness (BP-OSD fitness chases artifacts; see EVOLUTION_FINDING.md / the paper's
            # MILP-in-loop). Not a lower-bound certificate (exact=false).
            # SCALE iters with k: at FIXED iters, ISD UNDERTRAINS for high-k codes (large codeword space)
            # and overestimates d, which an FOM-maximizing search EXPLOITS (iter26: [[360,80,8]] FOM=14.2
            # was a fixed-300-iter artifact, retracted to d=2 by enough iters). Scaling ~linearly in k
            # keeps the fitness trustworthy. CAPPED (iter29) so ultra-high-k evals don't dominate wall-time
            # and stall the (barriered) evolution — the cap still covers the interesting k range; ISD finds
            # the trivial weight-2 logicals of ultra-high-k codes well within it.
            # ultra-high-rate codes (k/n>0.25) are the trivial UV family (d=2, found in a few iters); use
            # CHEAP base iters for them and reserve the (capped) k-scaling for the interesting k/n<=0.25
            # regime where the paper's high-k codes (e.g. [[288,50,8]] rate 0.17) live (iter30 perf fix).
            eff_iters = (k > code.n ÷ 4) ? isd_iters : min(isd_iters * max(1, cld(k, 8)), isd_iters * 10)
            dres = min_distance_isd(code; iters=eff_iters, pmax=2)
            d = dres.d > 0 ? dres.d : nothing
            exact = false
        else   # :milp or :exact  -> pure-Julia exact certifier (replaces HiGHS C++ MILP)
            dres = min_distance_bz(code; cap=cap)
            d = dres.d > 0 ? dres.d : nothing
            exact = dres.certified
        end
        if d !== nothing && d > 0
            fomv = fom(code.n, k, d)
            dsn = d / sqrt(code.n)
            trusted = dsn < 2.0          # paper's trust filter (Sec V.D): >= 2.0 discarded
        end
    end
    return (l=l, m=m, n=code.n, k=k, A=code.A, B=code.B, stab_weight=stabilizer_weight(code),
            d=d, exact=exact, fom=fomv, d_over_sqrt_n=dsn, stage=stage, trusted=trusted)
end
