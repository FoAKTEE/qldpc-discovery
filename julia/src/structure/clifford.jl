# Local-Clifford CSS-equivalence checks for non-CSS (PBB) codes. Pure Julia.
# Port of qcode_discovery/structure/clifford_equiv.py (source of truth).
#
# Post-campaign verifier (arXiv:2606.02418 App. E): decide whether a non-CSS code is secretly
# CSS under single-qubit Cliffords. Two fully-derived, polynomial-time pieces:
#   - Hadamard 2-coloring (generator level): some per-qubit H pattern makes every supplied
#     generator pure-X or pure-Z  iff  no generator has Y support AND a parity constraint
#     graph is 2-colorable (decided by union-find with parity).
#   - the group-CSS rank condition (Lemma 7.4): rank[X|Z] == rankX + rankZ over F(2).
#
# A stabilizer is described by two binary matrices SX, SZ (each #generators x n): the X- and
# Z-support of each generator, in symplectic order (X | Z). Depends only on core gf2 functions.

"""Union-find with parity: tracks each node's bit relative to its component root.

Port of clifford_equiv._ParityUF. `parent`/`par` are 1-based vectors over `1:size`."""
mutable struct ParityUF
    parent::Vector{Int}
    par::Vector{Int}      # parity relative to parent
end
ParityUF(size::Int) = ParityUF(collect(1:size), zeros(Int, size))

"""Return `(root, parity_of_x_relative_to_root)`, with path compression (matches Python)."""
function uf_find(uf::ParityUF, x::Int)
    if uf.parent[x] == x
        return x, 0
    end
    root, p = uf_find(uf, uf.parent[x])
    uf.parent[x] = root
    uf.par[x] ⊻= p
    return root, uf.par[x]
end

"""Constrain bit(x) XOR bit(y) = parity. Return `false` on contradiction."""
function uf_union(uf::ParityUF, x::Int, y::Int, parity::Int)
    rx, px = uf_find(uf, x)
    ry, py = uf_find(uf, y)
    if rx == ry
        return (px ⊻ py) == parity
    end
    uf.parent[rx] = ry
    uf.par[rx] = px ⊻ py ⊻ parity
    return true
end

"""Decide if some single-qubit-Hadamard pattern makes every generator pure-X / pure-Z.

`SX`, `SZ`: (#generators x n) binary X- and Z-support of each generator. Returns a NamedTuple
`(feasible, y_obstruction, H_pattern)`. Constraint per (generator r, qubit j in support): with
local type t = SZ[r,j] (0=X, 1=Z) and unknown generator target c_r and unknown qubit-flip s_j,
s_j XOR c_r = t (App. E). Union-find with parity over (qubits + generators) decides it.
Mirrors clifford_equiv.hadamard_two_coloring."""
function hadamard_two_coloring(SX::AbstractMatrix, SZ::AbstractMatrix)
    X = as_f2(SX)
    Z = as_f2(SZ)
    R, n = size(X)
    # some generator has Y on some qubit (both X and Z support) -> obstruction
    if any((X .& Z) .!= 0x0)
        return (feasible = false, y_obstruction = true, H_pattern = nothing)
    end
    uf = ParityUF(n + R)                                  # nodes 1..n qubits, n+1..n+R generators
    @inbounds for r in 1:R
        for j in 1:n
            if (X[r, j] | Z[r, j]) == 0x1                 # qubit j is in support of generator r
                t = Int(Z[r, j])                          # 1 if Z on (r,j), 0 if X
                if !uf_union(uf, j, n + r, t)             # s_j XOR c_r = t
                    return (feasible = false, y_obstruction = false, H_pattern = nothing)
                end
            end
        end
    end
    # Recover an H pattern: each component's root := 0; qubit's bit is its parity-to-root.
    pattern = UInt8[uf_find(uf, j)[2] for j in 1:n]
    return (feasible = true, y_obstruction = false, H_pattern = pattern)
end

"""The 6 single-qubit-Clifford coset reps as 2x2 F(2) symplectic maps on (x, z)^T.

I, S:(x,z)->(x, x+z), H:(x,z)->(z,x), and the products HS, SH, HSH (App. E reduction to
6 reps mod the Pauli group). Mirrors clifford_equiv._clifford_symplectic_mats."""
function clifford_symplectic_mats()
    I = UInt8[1 0; 0 1]
    S = UInt8[1 0; 1 1]
    H = UInt8[0 1; 1 0]
    mul(P, Q) = UInt8.(mod.(Int.(P) * Int.(Q), 2))
    return [("I", I), ("S", S), ("H", H),
            ("HS", mul(H, S)), ("SH", mul(S, H)), ("HSH", mul(H, mul(S, H)))]
end

"""Transform a qubit block's (X, Z) supports by a single 2x2 symplectic Clifford map `M`.

Mirrors clifford_equiv._apply_block."""
function apply_block(Xb::AbstractMatrix, Zb::AbstractMatrix, M::AbstractMatrix)
    Xn = (M[1, 1] .* Int.(Xb) .+ M[1, 2] .* Int.(Zb)) .% 2
    Zn = (M[2, 1] .* Int.(Xb) .+ M[2, 2] .* Int.(Zb)) .% 2
    return UInt8.(Xn), UInt8.(Zn)
end

"""Group-CSS rank condition (Lemma 7.4): rank[X|Z] == rank X + rank Z over GF(2).

Mirrors clifford_equiv._is_css / pbb_codes.is_css_group."""
is_css_group(SX::AbstractMatrix, SZ::AbstractMatrix) =
    gf2_rank(hcat(as_f2(SX), as_f2(SZ))) == gf2_rank(SX) + gf2_rank(SZ)

"""App. E Step 1: does any of the 36 uniform per-block single-qubit Clifford assignments
render the stabilizer group CSS (by the rank condition)?

`SX`, `SZ` are (#gen x n) with n = 2*lm; columns split into two blocks of width `lm`.
Returns `(css::Bool, pattern)` where pattern is `(name1, name2)` or `nothing`.
Mirrors clifford_equiv.uniform_clifford_lc_css."""
function uniform_clifford_lc_css(SX::AbstractMatrix, SZ::AbstractMatrix, lm::Int)
    X = as_f2(SX)
    Z = as_f2(SZ)
    X1, X2 = X[:, 1:lm], X[:, lm+1:end]
    Z1, Z2 = Z[:, 1:lm], Z[:, lm+1:end]
    mats = clifford_symplectic_mats()
    for (n1, M1) in mats
        for (n2, M2) in mats
            x1, z1 = apply_block(X1, Z1, M1)
            x2, z2 = apply_block(X2, Z2, M2)
            if is_css_group(hcat(x1, x2), hcat(z1, z2))
                return (css = true, pattern = (n1, n2))
            end
        end
    end
    return (css = false, pattern = nothing)
end

"""Classify a stabilizer's CSS-equivalence under the tested single-qubit-Clifford families.

`SX`, `SZ` are (#generators x n) binary support matrices in symplectic order (X | Z); `lm`
is the per-block width (n = 2*lm), needed for the uniform-Clifford block split. Returns a
NamedTuple with field `verdict` (and supporting fields):
  - "CSS_GROUP"               : already CSS via the rank condition.
  - "UNIFORM_CLIFFORD_CSS"    : a uniform per-block Clifford assignment makes it CSS.
  - "HADAMARD_CSS"            : a per-qubit H pattern makes the generators CSS.
  - "CSS_INEQUIVALENT_TESTED" : none of the tested families; residual non-uniform {S}/{SH,HSH}
                                families are [FUTURE], so this means "within tested families".
Mirrors clifford_equiv.lc_css_classify."""
function lc_css_classify(SX::AbstractMatrix, SZ::AbstractMatrix, lm::Int)
    if is_css_group(SX, SZ)
        return (verdict = "CSS_GROUP", hadamard = nothing)
    end
    uni = uniform_clifford_lc_css(SX, SZ, lm)                 # App. E Step 1 (36 uniform assignments)
    if uni.css
        return (verdict = "UNIFORM_CLIFFORD_CSS", pattern = uni.pattern, hadamard = nothing)
    end
    had = hadamard_two_coloring(SX, SZ)                       # App. E non-uniform {I,H}
    if had.feasible
        return (verdict = "HADAMARD_CSS", hadamard = had, H_weight = Int(sum(had.H_pattern)))
    end
    return (verdict = "CSS_INEQUIVALENT_TESTED", hadamard = had)
end

"""Build the symplectic stabilizer `(SX, SZ, lm)` of a CSS code from its `H_X`, `H_Z`.

CSS generators are pure-X or pure-Z: X-checks contribute rows `[HX | 0]`, Z-checks `[0 | HZ]`.
Convenience wrapper so `lc_css_classify` can be exercised on a BBCode."""
function css_stabilizer(HX::AbstractMatrix, HZ::AbstractMatrix)
    n = size(HX, 2)
    @assert size(HZ, 2) == n "HX and HZ must have the same number of columns (qubits)"
    rx, rz = size(HX, 1), size(HZ, 1)
    SX = vcat(as_f2(HX), zeros(UInt8, rz, n))
    SZ = vcat(zeros(UInt8, rx, n), as_f2(HZ))
    return SX, SZ, n ÷ 2
end
css_stabilizer(c::BBCode) = css_stabilizer(c.HX, c.HZ)
