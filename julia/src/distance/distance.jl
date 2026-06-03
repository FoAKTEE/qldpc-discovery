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
rowspace(`stab`). Returns -1 if none exists at weight ≤ max_weight (distance exceeds the budget)."""
function min_weight_logical(checks::AbstractMatrix, stab::AbstractMatrix; max_weight::Int=6)
    n = size(checks, 2)
    chk = Int.(checks)
    found = Ref(-1)
    v = zeros(Int, n)
    for w in 1:max_weight
        hit = _each_combination(n, w) do combo
            fill!(v, 0)
            @inbounds for idx in combo
                v[idx] = 1
            end
            in_ker = all(iszero, (chk * v) .% 2)
            in_ker && !in_rowspace(stab, v)
        end
        if hit
            found[] = w
            break
        end
    end
    return found[]
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
