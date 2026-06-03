# Information-set decoding (Lee–Brickell) for a TIGHT UPPER BOUND on CSS logical distance at large n.
#
# Motivation: BP-OSD (bposd.jl) OVERESTIMATES distance, and exact Brouwer–Zimmermann (distance_exact.jl)
# is infeasible for BB CSS logicals at large n/high d (dim ker H_Z = (n+k)/2 > n/2 ⇒ one information set
# ⇒ combinatorial wall — the paper used an industrial MILP here). ISD finds genuinely low-weight logicals
# far better than BP-OSD by repeatedly drawing a random information set, reducing to systematic form, and
# enumerating small row-combinations (Lee–Brickell). EVERY vector it evaluates is a real element of the
# codeword space and is checked to be a genuine logical, so a found logical of weight w is an
# UNCONDITIONAL proof that d ≤ w. This is an UPPER bound (refutes overestimates) — NOT a lower-bound
# certificate of equality. Reuses the packed-GF(2) helpers from distance_exact.jl.

import Random

# Min weight of a nontrivial logical (∈ rowspace(G), with U·c ≠ 0) found over `iters` random information
# sets, enumerating row-combinations of size 1..pmax in each. Allocation-light hot loop (acc reused).
function _isd_min_logical(G::Matrix{UInt8}, U::Matrix{UInt8}; iters::Int=2000, pmax::Int=2,
                          rng::Random.AbstractRNG=Random.GLOBAL_RNG)
    kc = size(G, 1)
    n = size(G, 2)
    kc == 0 && return n + 1
    nw = _nwords(n)
    Upacked = Vector{_W}[_pack(view(U, i, :), nw) for i in 1:size(U, 1)]
    best = n + 1
    acc = zeros(_W, nw)
    Gp = Matrix{UInt8}(undef, kc, n)
    tmp = zeros(UInt8, n)
    for _ in 1:iters
        perm = Random.randperm(rng, n)                      # random information set
        @inbounds for r in 1:kc, c in 1:n
            Gp[r, c] = G[r, perm[c]]
        end
        Gr, piv = rref(Gp)                                  # systematic form on the permuted columns
        length(piv) < kc && continue                        # degenerate draw — retry
        rows = Vector{Vector{_W}}(undef, kc)                # each Gr row, un-permuted to original cols
        @inbounds for r in 1:kc
            fill!(tmp, zero(UInt8))
            for c in 1:n
                tmp[perm[c]] = Gr[r, c]
            end
            rows[r] = _pack(tmp, nw)
        end
        @inbounds for i in 1:kc                              # p = 1
            w = _packweight(rows[i])
            if 0 < w < best && _is_logical(rows[i], Upacked)
                best = w
            end
        end
        if pmax >= 2                                         # p = 2 (Lee–Brickell)
            @inbounds for i in 1:kc-1, j in i+1:kc
                for t in 1:nw
                    acc[t] = rows[i][t] ⊻ rows[j][t]
                end
                w = _packweight(acc)
                if 0 < w < best && _is_logical(acc, Upacked)
                    best = w
                end
            end
        end
    end
    return best
end

"""Tight UPPER bound on CSS distance via Lee–Brickell information-set decoding (probabilistic). Returns
`(d, dX, dZ)`, each the minimum weight of a logical actually exhibited — so `true distance ≤ d` always
holds (a valid upper bound; NOT a certificate of equality). Finds low-weight logicals BP-OSD misses, so
the certifier uses it to refute overestimates where exact Brouwer–Zimmermann is infeasible (large n).
`iters` random information sets per sector; `pmax` is the max row-combination size (2 = Lee–Brickell)."""
function min_distance_isd(c::BBCode; iters::Int=2000, pmax::Int=2, seed::Int=0)
    rng = Random.MersenneTwister(UInt32(0x5DEECE66 ⊻ seed))
    nullHZ = nullspace_gf2(c.HZ)
    nullHX = nullspace_gf2(c.HX)
    dX = _isd_min_logical(nullHZ, nullHX; iters=iters, pmax=pmax, rng=rng)   # X-logicals ∈ ker(H_Z)
    dZ = _isd_min_logical(nullHX, nullHZ; iters=iters, pmax=pmax, rng=rng)   # Z-logicals ∈ ker(H_X)
    return (d=min(dX, dZ), dX=dX, dZ=dZ)
end
