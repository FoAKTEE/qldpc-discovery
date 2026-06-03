# Exact minimum distance — PURE JULIA, replacing the HiGHS (C/C++) MILP for the verification role.
#
# d_X = min weight of x with H_Z x = 0 (a Z-syndrome-free operator) that is NOT a Z-stabilizer
# (i.e. not in rowspace(H_X)); d_Z symmetric; d = min(d_X, d_Z). We search by increasing weight
# (a complete, exact certificate up to `max_weight`): the smallest weight at which a nontrivial
# logical exists IS the distance. This certifies small/moderate codes with no external solver.
#
# Scaling note: weight-w enumeration is C(n,w); exact certification of large codes (e.g. the gross
# code d=12 at n=144) needs the staged branch-and-bound / information-set search (see README).

"""Apply `f(combo)` to every w-subset (as a Vector{Int}) of 1:n; stop early if `f` returns true."""
function _each_combination(f, n::Int, w::Int)
    w == 0 && return f(Int[])
    combo = collect(1:w)
    while true
        f(combo) && return true
        i = w
        while i >= 1 && combo[i] == n - w + i
            i -= 1
        end
        i == 0 && return false
        combo[i] += 1
        for j in i+1:w
            combo[j] = combo[j-1] + 1
        end
    end
end

"""Minimum weight (1..max_weight) of a vector in ker(`checks`) over F(2) that is NOT in
rowspace(`stab`). Returns -1 if none exists at weight ≤ max_weight (distance exceeds the budget).

Allocation-free hot loop: the in-kernel test is the F(2) parity of each check row over the `w` set
columns (no per-combination matrix–vector product, which previously allocated a length-`size(checks,1)`
array on EVERY combination), and the combination walk is inlined (no capturing closure to box)."""
function min_weight_logical(checks::AbstractMatrix, stab::AbstractMatrix; max_weight::Int=6)
    n = size(checks, 2)
    nrc = size(checks, 1)
    chk = Int.(checks)
    v = zeros(Int, n)
    for w in 1:max_weight
        combo = collect(1:w)
        while true
            in_ker = true
            @inbounds for r in 1:nrc                 # row r in kernel ⟺ parity over set columns is even
                p = 0
                for idx in combo
                    p ⊻= chk[r, idx]
                end
                if (p & 1) != 0
                    in_ker = false
                    break
                end
            end
            if in_ker
                fill!(v, 0)
                @inbounds for idx in combo
                    v[idx] = 1
                end
                in_rowspace(stab, v) || return w     # nontrivial logical of weight w
            end
            i = w                                     # advance to the next w-combination (lexicographic)
            @inbounds while i >= 1 && combo[i] == n - w + i
                i -= 1
            end
            i == 0 && break
            @inbounds combo[i] += 1
            @inbounds for j in i+1:w
                combo[j] = combo[j-1] + 1
            end
        end
    end
    return -1
end

"""Exact CSS distance by minimum-weight logical search (pure Julia). Returns a NamedTuple
`(d, dX, dZ, exhausted)`; `exhausted=true` means d was certified within `max_weight`."""
function css_distance_enum(c::BBCode; max_weight::Int=6)
    dX = min_weight_logical(c.HZ, c.HX; max_weight=max_weight)   # X-logical ∈ ker(H_Z), ∉ rowspace(H_X)
    dZ = min_weight_logical(c.HX, c.HZ; max_weight=max_weight)
    vals = filter(>(0), [dX, dZ])
    d = isempty(vals) ? -1 : minimum(vals)
    return (d=d, dX=dX, dZ=dZ, exhausted=(d > 0 && d <= max_weight))
end
