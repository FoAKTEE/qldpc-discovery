# Pure-Julia EXACT minimum distance via Brouwer–Zimmermann codeword enumeration with a
# certified lower bound — replaces the HiGHS (C++) MILP for the certification role.
#
# d_X = min weight of c ∈ ker(H_Z) that is NOT a Z-stabilizer (c ∉ rowspace(H_X)); d_Z symmetric.
# We enumerate codewords by increasing "information weight" w on a systematic (RREF) generator:
# a codeword's restriction to the pivot (information) columns equals the row-combination indicator,
# so weight ≥ w. After enumerating all info-weight ≤ w codewords, any UNFOUND codeword has weight
# ≥ w+1 — a sound lower bound. When (w+1) ≥ (lightest logical found), the result is CERTIFIED.
#
# Membership test (no per-word rank): c ∉ rowspace(H_X) ⟺ U·c ≠ 0 over F(2), where U = ker(H_X),
# since rowspace(H_X) = (ker H_X)^⊥ over GF(2). Bit-packed (UInt64) for speed.
#
# Reach: for BB codes dim ker = (n+k)/2 > n/2, so only ONE disjoint information set fits; this
# certifies up to moderate distance (e.g. [[72,12,6]] d=6). The gross code's d=12 at n=144 needs the
# overlapping-information-set BZ or an industrial MIP — STAGED (returns an upper bound, certified=false).

const _W = UInt64
_nwords(n::Int) = (n + 63) >> 6

function _pack(row, nwords::Int)
    w = zeros(_W, nwords)
    @inbounds for i in eachindex(row)
        if row[i] != 0
            w[((i - 1) >> 6) + 1] |= (_W(1) << ((i - 1) & 63))
        end
    end
    return w
end

_packweight(w) = sum(count_ones, w)

function _dot2(a::Vector{_W}, b::Vector{_W})       # GF(2) inner product of packed vectors
    s = 0
    @inbounds for i in eachindex(a)
        s += count_ones(a[i] & b[i])
    end
    return s & 1
end

function _is_logical(c::Vector{_W}, U::Vector{Vector{_W}})   # c ∉ rowspace(H_X) ⟺ some U·c = 1
    @inbounds for u in U
        _dot2(c, u) == 1 && return true
    end
    return false
end

"""Allocation-free scan of every weight-`w` combination of the `κ` packed generator `rows`, updating
the best logical weight; honors the per-call combination budget `cap`. Returns `(best, enumerated,
capped)`. This is an EXTRACTED FUNCTION, not a closure: the hot loop must not capture-and-reassign
outer locals (`best`/`enumerated`), which Julia boxes into heap cells — that made the loop allocate
~5 heap objects per combination and OOM-crashed the process (uncatchably) on high-κ codes. Plain
locals here keep it at zero allocations per combination, so `cap` bounds work AND memory."""
function _bz_scan_weight!(acc::Vector{_W}, rows::Vector{Vector{_W}}, Upacked::Vector{Vector{_W}},
                          κ::Int, w::Int, best::Int, cap::Int, nw::Int)
    enumerated = 0
    combo = collect(1:w)
    while true
        enumerated += 1
        fill!(acc, zero(_W))
        @inbounds for r in combo
            rr = rows[r]
            for t in 1:nw
                acc[t] ⊻= rr[t]
            end
        end
        wt = _packweight(acc)
        if wt < best && _is_logical(acc, Upacked)
            best = wt
        end
        enumerated >= cap && return (best, enumerated, true)
        i = w
        @inbounds while i >= 1 && combo[i] == κ - w + i
            i -= 1
        end
        i == 0 && return (best, enumerated, false)
        @inbounds combo[i] += 1
        @inbounds for j in i+1:w
            combo[j] = combo[j-1] + 1
        end
    end
end

"""Minimum-weight logical of one sector (codewords = rowspace(`G`), nontrivial iff U·c ≠ 0), by
Brouwer–Zimmermann enumeration. Returns `(d, certified, enumerated)`. Stops (uncertified) at `cap`
total combinations (split across the increasing-weight passes)."""
function _bz_min_logical(G::Matrix{UInt8}, U::Matrix{UInt8}; cap::Int=50_000_000)
    Gr, pivots = rref(G)                 # systematic form; pivot columns are the information set
    κ = length(pivots)
    n = size(G, 2)
    nw = _nwords(n)
    rows = Vector{_W}[_pack(view(Gr, i, :), nw) for i in 1:κ]
    Upacked = Vector{_W}[_pack(view(U, i, :), nw) for i in 1:size(U, 1)]
    best = n + 1
    enumerated = 0
    acc = zeros(_W, nw)
    w = 1
    while w <= κ
        w >= best && return (d=best, certified=true, enumerated=enumerated)   # lower bound w ≥ best
        remaining = cap - enumerated
        remaining <= 0 && return (d=best, certified=false, enumerated=enumerated)
        best, e, capped = _bz_scan_weight!(acc, rows, Upacked, κ, w, best, remaining, nw)
        enumerated += e
        capped && return (d=best, certified=false, enumerated=enumerated)
        (w + 1) >= best && return (d=best, certified=true, enumerated=enumerated)
        w += 1
    end
    return (d=best, certified=true, enumerated=enumerated)   # enumerated the whole code
end

"""Exact CSS distance via Brouwer–Zimmermann (pure Julia; replaces the HiGHS MILP). Returns
`(d, dX, dZ, certified, enumerated)`. `certified=true` is a proof; `false` means `d` is an upper
bound reached before the enumeration `cap` (then a bigger `cap` or the staged solver is needed)."""
function min_distance_bz(c::BBCode; cap::Int=50_000_000)
    nullHZ = nullspace_gf2(c.HZ)
    nullHX = nullspace_gf2(c.HX)
    rx = _bz_min_logical(nullHZ, nullHX; cap=cap)   # X-logicals: ker(H_Z) \ rowspace(H_X)
    rz = _bz_min_logical(nullHX, nullHZ; cap=cap)   # Z-logicals: ker(H_X) \ rowspace(H_Z)
    return (d=min(rx.d, rz.d), dX=rx.d, dZ=rz.d,
            certified=(rx.certified && rz.certified),
            enumerated=rx.enumerated + rz.enumerated)
end
