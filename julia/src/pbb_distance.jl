# Pure-Julia EXACT non-CSS (symplectic) distance for PBB stabilizer codes.
# Port / generalization of `qcode_discovery.distance.distance_milp.symplectic_distance_milp`,
# but with NO MILP / HiGHS / scipy: a Brouwer–Zimmermann-style codeword enumeration with a
# certified symplectic lower bound, mirroring the CSS `min_distance_bz` in `distance_exact.jl`.
#
# A length-2n Pauli (a|b) (a = X-support, b = Z-support over n = 2lm qubits) is a LOGICAL iff
#   (1) it commutes with every stabilizer row of S = [SX | SZ]:  SZ·a + SX·b = 0  (mod 2),
#       i.e. (a|b) ∈ nullspace([SZ | SX]) — the symplectic normalizer N(S); and
#   (2) it is NOT itself a stabilizer:  (a|b) ∉ rowspace(S).
# The SYMPLECTIC WEIGHT of (a|b) is the number of qubits acted on nontrivially:
#       wsymp(a|b) = |{ i : a_i = 1  OR  b_i = 1 }|.
# The non-CSS distance is the minimum symplectic weight over all logicals — exactly what the
# Python `symplectic_distance_milp` computes (it just enumerates the 2k logical generators with
# a per-generator OR-linearized MILP; here we minimize over the whole normalizer quotient at once).
#
# ── Brouwer–Zimmermann lower bound for symplectic weight ────────────────────────────────────────
# Put a basis G of N(S) in RREF over F(2)^{2n}; its κ = 2k pivots are κ distinct COLUMNS. A codeword
# formed from a combination of w distinct generator rows restricts to the all-ones indicator on its w
# pivot columns, so it has HAMMING weight ≥ w over the 2n coordinates. Each qubit owns two columns
# (a_i at col i, b_i at col n+i); the worst case is that the w occupied columns pair up onto the same
# qubits, so the SYMPLECTIC weight is ≥ ⌈w/2⌉. Hence after enumerating all info-weight ≤ w codewords,
# any UNFOUND logical has symplectic weight ≥ ⌈(w+1)/2⌉ — a sound lower bound. When that bound reaches
# the lightest logical found so far, the answer is CERTIFIED. (Bit-packed UInt64 for speed.)
#
# Reach: dim N(S) = n + k > n for k>0, so a single information set covers the code; this certifies
# small/moderate non-CSS codes exactly. `cap` bounds the number of enumerated combinations; if hit,
# the returned `d` is an upper bound with certified=false (raise `cap` to push further).

"""Symplectic weight of a packed Pauli given as packed halves `(apk | bpk)` (each `nw` UInt64
words): the number of qubits where the X-half OR the Z-half is set."""
function _symp_weight(apk::Vector{_W}, bpk::Vector{_W})
    s = 0
    @inbounds for t in eachindex(apk)
        s += count_ones(apk[t] | bpk[t])
    end
    return s
end

"""Minimum symplectic weight of a nonzero element of `rowspace(G)` (the symplectic normalizer,
G a 2k×2n F(2) basis) that is NOT in `rowspace(S)` — i.e. a genuine logical — by Brouwer–Zimmermann
enumeration. `U2 = nullspace(S)` (over F(2)^{2n}) certifies non-membership: (a|b) ∉ rowspace(S) ⟺
U2·(a|b) ≠ 0. Returns `(d, certified, enumerated)`; stops (uncertified) at `cap` combinations."""
function _bz_min_symplectic(G::Matrix{UInt8}, U2::Matrix{UInt8}, n::Int; cap::Int=50_000_000)
    Gr, pivots = rref(G)                 # systematic form; pivot columns = the information set
    κ = length(pivots)
    twon = size(G, 2)                    # = 2n
    nw = _nwords(n)                       # words per HALF (n bits), not 2n
    # Split each RREF generator row into its X-half (cols 1:n) and Z-half (cols n+1:2n), packed.
    arows = [_pack(view(Gr, i, 1:n), nw)        for i in 1:κ]
    brows = [_pack(view(Gr, i, (n+1):twon), nw) for i in 1:κ]
    # Membership-certificate rows U2 likewise split into halves (length-2n vectors).
    Ua = [_pack(view(U2, i, 1:n), nw)        for i in 1:size(U2, 1)]
    Ub = [_pack(view(U2, i, (n+1):twon), nw) for i in 1:size(U2, 1)]
    best = n + 1
    enumerated = 0
    acca = zeros(_W, nw)
    accb = zeros(_W, nw)
    w = 1
    while w <= κ
        lb = (w + 1) >> 1                # ⌈w/2⌉ lower bound on symplectic weight at info-weight w
        lb >= best && return (d=best, certified=true, enumerated=enumerated)
        capped = _each_combination(κ, w) do combo
            enumerated += 1
            fill!(acca, zero(_W)); fill!(accb, zero(_W))
            @inbounds for r in combo
                ar = arows[r]; br = brows[r]
                for t in 1:nw
                    acca[t] ⊻= ar[t]
                    accb[t] ⊻= br[t]
                end
            end
            wt = _symp_weight(acca, accb)
            if wt < best && _is_symp_logical(acca, accb, Ua, Ub)
                best = wt
            end
            return enumerated >= cap
        end
        capped && return (d=best, certified=false, enumerated=enumerated)
        # After info-weight w, unfound logicals have symplectic weight ≥ ⌈(w+1)/2⌉.
        ((w + 2) >> 1) >= best && return (d=best, certified=true, enumerated=enumerated)
        w += 1
    end
    return (d=best, certified=true, enumerated=enumerated)   # enumerated the entire normalizer
end

"""True iff the packed Pauli `(apk|bpk)` is NOT in rowspace(S): some certificate row of
`U2 = nullspace(S)` has odd F(2) inner product with it, i.e. Σ Ua·a + Ub·b = 1 for some row."""
function _is_symp_logical(apk::Vector{_W}, bpk::Vector{_W}, Ua, Ub)
    @inbounds for i in eachindex(Ua)
        (_dot2(apk, Ua[i]) ⊻ _dot2(bpk, Ub[i])) == 1 && return true
    end
    return false
end

"""Exact non-CSS (symplectic) distance of a `PBBCode` — pure Julia, replacing the HiGHS MILP
`symplectic_distance_milp`. The distance is the minimum symplectic weight of a Pauli (a|b) that
commutes with every stabilizer (lies in the symplectic kernel of `S`) yet is NOT a stabilizer
(∉ rowspace(S)). Returns `(d, certified, enumerated, n_logicals)`: `certified=true` is a proof;
`false` means `d` is an upper bound reached before the enumeration `cap` (raise `cap` to push on)."""
function symplectic_distance(code::PBBCode; cap::Int=50_000_000)
    n = code.n
    S = code.S
    SX = @view S[:, 1:n]
    SZ = @view S[:, (n+1):2n]
    # Symplectic normalizer N(S): (a|b) with SZ·a + SX·b = 0  ⇔  [SZ | SX]·(a|b) = 0.
    Hflip = hcat(as_f2(SZ), as_f2(SX))
    Ggen = nullspace_gf2(Hflip)               # basis of N(S), rows are length-2n
    U2 = nullspace_gf2(S)                      # rowspace(S) = (ker S)^⊥ over F(2): membership certificate
    nlog = size(Ggen, 1) - gf2_rank(S)         # 2k = dim N(S) − dim stabilizer group
    r = _bz_min_symplectic(Ggen, U2, n; cap=cap)
    return (d=r.d, certified=r.certified, enumerated=r.enumerated, n_logicals=nlog)
end
