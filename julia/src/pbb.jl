# Perturbed bivariate-bicycle (PBB) non-CSS code construction.
# Port of qcode_discovery/codes/pbb_codes.py.
#
# A PBB code augments a BB pair (A, B) with perturbation polynomials (C, D).
# Symplectic stabilizer matrix S = [SX | SZ] (order X | Z) over n = 2lm qubits:
#     top rows: SX = (A | B),  SZ = (C | D)      # mixed X/Z generators
#     bot rows: SX = (0 | 0),  SZ = (B^T | A^T)  # pure-Z generators
# All rows commute iff (A C^T + B D^T) is symmetric over F(2); C = D = 0 recovers
# the CSS BB code. k = n - rank(S). Paper anchor: arXiv:2606.02418 sec III.B.
#
# Convention note: the core `circulant(terms, l, m)` is the transpose of Python's
# `poly_matrix` (verified). Python's PBBCode builds its blocks from `poly_matrix`,
# so here we recover the Python-oriented circulant as `pmat = permutedims(circulant(...))`
# to keep the validity boolean and k bit-identical to the source of truth.

"""Python-`poly_matrix`-oriented circulant of a polynomial string: the (lm × lm)
matrix matching `qcode_discovery.algebra.polynomials.poly_matrix`. This is the
transpose of the core `circulant`, so blocks line up with the Python PBBCode."""
_pbb_polymat(s::AbstractString, l::Int, m::Int) = permutedims(circulant(parse_terms(s, l, m), l, m))

"""A non-CSS perturbed bivariate-bicycle code [[2lm, k, d]] built from a 4-tuple of
polynomial strings (A, B, C, D). Holds parsed monomial supports, the block circulants
A, B, C, D, and the symplectic stabilizer matrix `S = [SX | SZ]` (order X | Z)."""
struct PBBCode
    l::Int
    m::Int
    A::Vector{Tuple{Int,Int}}
    B::Vector{Tuple{Int,Int}}
    C::Vector{Tuple{Int,Int}}
    D::Vector{Tuple{Int,Int}}
    Am::Matrix{UInt8}
    Bm::Matrix{UInt8}
    Cm::Matrix{UInt8}
    Dm::Matrix{UInt8}
    SX::Matrix{UInt8}
    SZ::Matrix{UInt8}
    S::Matrix{UInt8}
    n::Int
end

"""All PBB generators pairwise commute: S_X S_Z^T + S_Z S_X^T = 0 (mod 2)."""
function pbb_symplectic_gram_zero(SX::AbstractMatrix, SZ::AbstractMatrix)
    G = (Int.(SX) * permutedims(Int.(SZ)) .+ Int.(SZ) * permutedims(Int.(SX))) .% 2
    return all(iszero, G)
end

"""The non-trivial commutativity condition: A C^T + B D^T symmetric over F(2)."""
function pbb_reduced_condition_symmetric(Am, Bm, Cm, Dm)
    M = (Int.(Am) * permutedims(Int.(Cm)) .+ Int.(Bm) * permutedims(Int.(Dm))) .% 2
    return M == permutedims(M)
end

"""Construct a PBB code from polynomial strings `(A, B, C, D)` on the (l, m) lattice.
Throws an `ArgumentError` (mirroring Python's `ValueError`) if the generators do not
commute — i.e. the tuple is rejected when `A C^T + B D^T` is not symmetric over F(2)."""
function PBBCode(l::Int, m::Int, A::AbstractString, B::AbstractString,
                 C::AbstractString, D::AbstractString)
    At = parse_terms(A, l, m)
    Bt = parse_terms(B, l, m)
    Ct = parse_terms(C, l, m)
    Dt = parse_terms(D, l, m)
    Am = _pbb_polymat(A, l, m)
    Bm = _pbb_polymat(B, l, m)
    Cm = _pbb_polymat(C, l, m)
    Dm = _pbb_polymat(D, l, m)
    lm = l * m
    Zr = zeros(UInt8, lm, lm)
    SX = vcat(hcat(Am, Bm), hcat(Zr, Zr))
    SZ = vcat(hcat(Cm, Dm), hcat(permutedims(Bm), permutedims(Am)))   # (C|D) over (B^T|A^T)
    S = hcat(SX, SZ)                                                  # symplectic, order (X|Z)
    if !pbb_symplectic_gram_zero(SX, SZ)
        throw(ArgumentError("PBB generators do not commute (A C^T + B D^T not symmetric)"))
    end
    return PBBCode(l, m, At, Bt, Ct, Dt, Am, Bm, Cm, Dm, SX, SZ, S, 2 * lm)
end

"""Encoding dimension k = n - rank(S) over F(2) (number of independent generators)."""
pbb_k(c::PBBCode) = c.n - gf2_rank(c.S)

"""True iff C = D = 0 — the code reduces to a CSS BB code."""
pbb_is_pure_css(c::PBBCode) = isempty(c.C) && isempty(c.D)

"""True iff some generator has both X- and Z-support (non-CSS at the generator level)."""
function pbb_has_mixed_generator(c::PBBCode)
    @inbounds for i in 1:size(c.SX, 1)
        xany = any(!iszero, @view c.SX[i, :])
        zany = any(!iszero, @view c.SZ[i, :])
        xany && zany && return true
    end
    return false
end

"""Group-CSS rank condition (Lemma 7.4): rank[X|Z] == rank(X) + rank(Z)."""
pbb_is_css_group(c::PBBCode) = gf2_rank(c.S) == gf2_rank(c.SX) + gf2_rank(c.SZ)
