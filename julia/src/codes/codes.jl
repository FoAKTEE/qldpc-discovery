# Bivariate-bicycle (BB) CSS code construction + parameters.
# Port of qcode_discovery/codes/{bb_codes,metrics}.py.
#
# H_X = (A | B), H_Z = (B^T | A^T) over R = F2[x,y]/(x^l-1, y^m-1); n = 2lm.
# Circulants commute over GF(2), so H_X H_Z^T = AB + BA = 0 — a valid CSS code.

"""A BB CSS code, holding the parsed monomial supports and the parity-check matrices H_X, H_Z."""
struct BBCode
    l::Int
    m::Int
    A::Vector{Tuple{Int,Int}}
    B::Vector{Tuple{Int,Int}}
    HX::Matrix{UInt8}
    HZ::Matrix{UInt8}
    n::Int
end

"""Construct a BB code from polynomial strings `A`, `B` on the (l, m) lattice."""
function BBCode(l::Int, m::Int, A::AbstractString, B::AbstractString)
    At = parse_terms(A, l, m)
    Bt = parse_terms(B, l, m)
    Ac = circulant(At, l, m)
    Bc = circulant(Bt, l, m)
    HX = hcat(Ac, Bc)
    HZ = hcat(permutedims(Bc), permutedims(Ac))   # (B^T | A^T)
    return BBCode(l, m, At, Bt, HX, HZ, 2 * l * m)
end

"""Encoding dimension k = n - rank(H_X) - rank(H_Z) over F(2)."""
css_k(c::BBCode) = c.n - gf2_rank(c.HX) - gf2_rank(c.HZ)

"""Figure of merit FOM = k d^2 / n."""
fom(n::Integer, k::Integer, d::Integer) = k * d^2 / n

"""Stabilizer (check) weight — number of 1s in a parity-check row."""
stabilizer_weight(c::BBCode) = Int(sum(Int.(c.HX[1, :])))

"""True iff the code satisfies the CSS commutation H_X H_Z^T = 0 over F(2)."""
function css_valid(c::BBCode)
    P = (Int.(c.HX) * permutedims(Int.(c.HZ))) .% 2
    return all(iszero, P)
end
