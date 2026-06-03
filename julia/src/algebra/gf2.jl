# GF(2) linear algebra — rank, RREF, null space, row-space membership. Pure Julia.
# Port of qcode_discovery/algebra/gf2.py. Foundation for k, logicals, distance, theorems.

"""Coerce a matrix/vector to UInt8 entries reduced mod 2 (a fresh array)."""
as_f2(M) = UInt8.(mod.(M, 2))

"""Reduced row-echelon form over F(2). Returns `(R, pivot_columns)`. Does not mutate `M`."""
function rref(M::AbstractMatrix)
    R = as_f2(M)
    nrows, ncols = size(R)
    pivots = Int[]
    r = 1
    @inbounds for c in 1:ncols
        piv = 0
        for i in r:nrows
            if R[i, c] == 0x1
                piv = i
                break
            end
        end
        piv == 0 && continue
        if piv != r
            for c2 in 1:ncols
                R[r, c2], R[piv, c2] = R[piv, c2], R[r, c2]
            end
        end
        for i in 1:nrows
            if i != r && R[i, c] == 0x1
                for c2 in 1:ncols
                    R[i, c2] ⊻= R[r, c2]
                end
            end
        end
        push!(pivots, c)
        r += 1
        r > nrows && break
    end
    return R, pivots
end

"""F(2) rank."""
gf2_rank(M) = isempty(M) ? 0 : length(rref(M)[2])

"""Basis (one vector per row) of the right null space {x : M x = 0} over F(2)."""
function nullspace_gf2(M)
    R, pivots = rref(M)
    ncols = size(R, 2)
    pivset = Set(pivots)
    freecols = [c for c in 1:ncols if !(c in pivset)]
    basis = zeros(UInt8, length(freecols), ncols)
    for (k, f) in enumerate(freecols)
        basis[k, f] = 0x1
        for (rowi, pivc) in enumerate(pivots)
            if R[rowi, f] == 0x1
                basis[k, pivc] = 0x1
            end
        end
    end
    return basis
end

"""True iff vector `v` lies in the F(2) row space of `M`."""
function in_rowspace(M, v)
    isempty(M) && return !any(!iszero, v)
    vrow = reshape(as_f2(v), 1, :)
    return gf2_rank(M) == gf2_rank(vcat(as_f2(M), vrow))
end
