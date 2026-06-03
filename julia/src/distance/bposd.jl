# Pure-Julia belief-propagation + ordered-statistics decoding (OSD) for a STOCHASTIC UPPER
# BOUND on CSS distance — a from-scratch reimplementation of what the `ldpc` (C++) BpOsdDecoder
# did in qcode_discovery/distance/distance_bposd.py.  ABSOLUTELY NO C/C++; depends only on the
# pure-Julia GF(2) core (rref, nullspace_gf2, ...).
#
# Method (paper arXiv:2606.02418 sec V.A/C):  form H_eff = (H_check ; L) by stacking the logical
# generators below the checks, fix the stabilizer syndrome to zero, draw a random nontrivial
# logical coset λ, and decode the syndrome s = (0 | λ).  The decoded error e satisfies H_eff e = s
# (mod 2): zero syndrome on the checks (so e is in the code) AND the chosen logical pattern λ on the
# logical rows (so e is a nontrivial logical).  Its Hamming weight is a sample of a logical-operator
# weight; the MINIMUM over trials/configs is an UPPER BOUND on the distance (BP-OSD can overshoot —
# never promoted to exact).
#
# Decoder = belief propagation (sum-product OR normalized min-sum) on the Tanner graph of H_eff,
# initialised from a per-bit channel prior p (error_rate), followed by ordered-statistics decoding.
# When BP already yields a valid solution we still run OSD and keep the lighter of the two; OSD with
# a "combination sweep" of the least-reliable bits (osd_cs, order λ_osd) refines the base OSD-0
# solution exactly as the ldpc library's osd_cs mode does.

# ---------------------------------------------------------------------------------------------
# Logical-operator bases (port of qcode_discovery/codes/metrics.css_logicals).
# ---------------------------------------------------------------------------------------------

"""Subset of `candidates` rows that are independent modulo the row span of `span_basis`."""
function _independent_mod(span_basis::Matrix{UInt8}, candidates::Matrix{UInt8})
    width = size(candidates, 2) != 0 ? size(candidates, 2) : size(span_basis, 2)
    cur = copy(span_basis)
    r0 = size(cur, 1) == 0 ? 0 : gf2_rank(cur)
    chosen = Vector{UInt8}[]
    @inbounds for i in 1:size(candidates, 1)
        v = candidates[i, :]
        stacked = size(cur, 1) == 0 ? reshape(v, 1, :) : vcat(cur, reshape(v, 1, :))
        r1 = gf2_rank(stacked)
        if r1 > r0
            push!(chosen, copy(v))
            cur = stacked
            r0 = r1
        end
    end
    isempty(chosen) && return zeros(UInt8, 0, width)
    return permutedims(reduce(hcat, chosen))
end

"""A basis (independent rows) of the F(2) row space of `M`."""
function _row_reduce_basis(M::AbstractMatrix)
    size(M, 1) == 0 && return zeros(UInt8, 0, size(M, 2))
    R, pivots = rref(M)
    return R[1:length(pivots), :]
end

"""Return `(X_logicals, Z_logicals)` as bases of length-n logical-operator representatives.
Z-logicals lie in ker(H_X) modulo rowspace(H_Z); X-logicals in ker(H_Z) modulo rowspace(H_X)."""
function css_logicals(HX::Matrix{UInt8}, HZ::Matrix{UInt8})
    Z = _independent_mod(_row_reduce_basis(HZ), nullspace_gf2(HX))
    X = _independent_mod(_row_reduce_basis(HX), nullspace_gf2(HZ))
    return X, Z
end

# ---------------------------------------------------------------------------------------------
# Belief propagation on the Tanner graph of a binary parity-check matrix.
# ---------------------------------------------------------------------------------------------

"""Sparse Tanner graph: for each check the list of incident bit indices, and for each bit the
list of incident checks.  Built once per H_eff (shared across all trials)."""
struct TannerGraph
    m::Int                       # number of checks
    n::Int                       # number of bits
    check_bits::Vector{Vector{Int}}   # bits incident to each check
    bit_checks::Vector{Vector{Int}}   # checks incident to each bit
end

function TannerGraph(H::AbstractMatrix)
    m, n = size(H)
    check_bits = [Int[] for _ in 1:m]
    bit_checks = [Int[] for _ in 1:n]
    @inbounds for c in 1:m, b in 1:n
        if H[c, b] != 0
            push!(check_bits[c], b)
            push!(bit_checks[b], c)
        end
    end
    return TannerGraph(m, n, check_bits, bit_checks)
end

"""Belief propagation decoder.  `method` is `:product_sum` (sum-product / tanh rule) or
`:minimum_sum` (normalized min-sum, scaling factor α=0.625, the ldpc default).  Returns the
hard-decision bit vector `e` (UInt8) after at most `max_iter` iterations, stopping early once the
syndrome matches.  `prior_llr` is the per-bit channel log-likelihood-ratio log((1-p)/p).

Soft output (the per-bit posterior LLRs `llr`) is returned too so OSD can rank bit reliabilities."""
function _bp_decode(g::TannerGraph, syndrome::Vector{UInt8}, prior_llr::Float64;
                    method::Symbol, max_iter::Int, alpha::Float64=0.625)
    m, n = g.m, g.n
    # Edge messages, addressed per (check, position-in-check).
    msg_c2b = [zeros(Float64, length(g.check_bits[c])) for c in 1:m]   # check -> bit
    # bit -> check messages stored per (bit, position-in-bit)
    msg_b2c = [fill(prior_llr, length(g.bit_checks[b])) for b in 1:n]
    posterior = fill(prior_llr, n)
    hard = zeros(UInt8, n)

    # Position lookups: for check c, the index of bit b within g.check_bits[c]; and the position of
    # check c within g.bit_checks[b].  Precompute to avoid searches in the hot loop.
    pos_in_check = [Dict{Int,Int}() for _ in 1:m]
    pos_in_bit = [Dict{Int,Int}() for _ in 1:n]
    @inbounds for c in 1:m
        for (k, b) in enumerate(g.check_bits[c]); pos_in_check[c][b] = k; end
    end
    @inbounds for b in 1:n
        for (k, c) in enumerate(g.bit_checks[b]); pos_in_bit[b][c] = k; end
    end

    for _iter in 1:max_iter
        # ---- check update: c2b message excludes the target bit's incoming b2c ----
        @inbounds for c in 1:m
            bits = g.check_bits[c]
            deg = length(bits)
            sgn = syndrome[c] == 0 ? 1.0 : -1.0   # syndrome flips the overall sign
            if method === :product_sum
                # tanh product rule
                for (k, b) in enumerate(bits)
                    prod = sgn
                    for (k2, b2) in enumerate(bits)
                        k2 == k && continue
                        inc = msg_b2c[b2][pos_in_bit[b2][c]]
                        prod *= tanh(clamp(inc, -30.0, 30.0) / 2)
                    end
                    prod = clamp(prod, -1.0 + 1e-12, 1.0 - 1e-12)
                    msg_c2b[c][k] = 2 * atanh(prod)
                end
            else  # :minimum_sum  (normalized min-sum)
                for (k, b) in enumerate(bits)
                    s = sgn
                    minabs = Inf
                    for (k2, b2) in enumerate(bits)
                        k2 == k && continue
                        inc = msg_b2c[b2][pos_in_bit[b2][c]]
                        s *= sign(inc) == 0 ? 1.0 : sign(inc)
                        a = abs(inc)
                        a < minabs && (minabs = a)
                    end
                    deg == 1 && (minabs = 0.0)
                    msg_c2b[c][k] = alpha * s * minabs
                end
            end
        end
        # ---- bit update: posterior = prior + Σ incoming c2b ; b2c excludes the target check ----
        @inbounds for b in 1:n
            checks = g.bit_checks[b]
            total = prior_llr
            for (k, c) in enumerate(checks)
                total += msg_c2b[c][pos_in_check[c][b]]
            end
            posterior[b] = total
            for (k, c) in enumerate(checks)
                msg_b2c[b][k] = total - msg_c2b[c][pos_in_check[c][b]]
            end
            hard[b] = total < 0 ? 0x1 : 0x0
        end
        # ---- syndrome check: stop early on success ----
        ok = true
        @inbounds for c in 1:m
            acc = 0
            for b in g.check_bits[c]
                acc ⊻= Int(hard[b])
            end
            if (acc & 1) != Int(syndrome[c])
                ok = false
                break
            end
        end
        ok && return hard, posterior, true
    end
    return hard, posterior, false
end

# ---------------------------------------------------------------------------------------------
# Ordered-statistics decoding (OSD-0 + combination sweep), pure GF(2).
# ---------------------------------------------------------------------------------------------

"""GF(2) syndrome of a (UInt8) error against a dense check matrix `H`."""
function _syndrome(H::Matrix{UInt8}, e::Vector{UInt8})
    m, n = size(H)
    s = zeros(UInt8, m)
    @inbounds for c in 1:m
        acc = 0
        for b in 1:n
            H[c, b] != 0 && (acc ⊻= Int(e[b]))
        end
        s[c] = UInt8(acc & 1)
    end
    return s
end

"""Ordered-statistics decoding.  `H` is the (dense) check matrix, `syndrome` the target, `llr` the
soft per-bit posterior from BP (smaller |llr| / more negative = less reliable / likelier error).

OSD-0: order columns by reliability (most reliable first), Gaussian-eliminate to find a full-rank
information set among the top columns, force the remaining (least-reliable) bits to 0, and solve.
osd_cs (combination sweep, order λ): additionally try flipping small subsets of the λ least-reliable
non-basis bits, re-solving on the basis, and keep the lowest-weight valid error."""
function _osd(H::Matrix{UInt8}, syndrome::Vector{UInt8}, llr::Vector{Float64}; osd_order::Int)
    m, n = size(H)
    # Reliability: a bit is "likely 1" when llr<0.  Order columns from MOST reliable (large +llr)
    # to LEAST reliable so the information set is built from trustworthy positions.
    order = sortperm(llr; rev=true)            # descending llr = descending reliability of a 0

    # Gaussian elimination over GF(2) on the column-permuted matrix to find pivot columns.
    A = copy(H)
    rhs = copy(syndrome)
    pivot_col_of_row = fill(0, m)
    pivots = Int[]            # original column indices forming the information (basis) set
    row = 1
    @inbounds for oc in order
        row > m && break
        # find a row >= `row` with a 1 in column oc
        piv = 0
        for i in row:m
            if A[i, oc] != 0
                piv = i; break
            end
        end
        piv == 0 && continue
        if piv != row
            for j in 1:n
                A[row, j], A[piv, j] = A[piv, j], A[row, j]
            end
            rhs[row], rhs[piv] = rhs[piv], rhs[row]
        end
        for i in 1:m
            if i != row && A[i, oc] != 0
                for j in 1:n
                    A[i, j] ⊻= A[row, j]
                end
                rhs[i] ⊻= rhs[row]
            end
        end
        pivot_col_of_row[row] = oc
        push!(pivots, oc)
        row += 1
    end
    rank = row - 1

    # Non-basis columns, ordered LEAST reliable first (best candidates to switch on in the sweep).
    pivset = Set(pivots)
    nonbasis = [c for c in order if !(c in pivset)]
    reverse!(nonbasis)        # least reliable first

    # Solve for the basis bits given the (already reduced) system and a fixed assignment of the
    # non-basis bits `t` (a Dict col=>1 for switched-on bits).  Returns the full error vector or
    # `nothing` if inconsistent (a zero pivot row with nonzero residual).
    function solve(active::Vector{Int})
        e = zeros(UInt8, n)
        for c in active
            e[c] = 0x1
        end
        @inbounds for r in 1:rank
            acc = Int(rhs[r])
            for c in active
                A[r, c] != 0 && (acc ⊻= 1)
            end
            if (acc & 1) != 0
                e[pivot_col_of_row[r]] = 0x1
            end
        end
        # Validity: zero rows (rank+1..m) must have zero residual.
        @inbounds for r in (rank + 1):m
            acc = Int(rhs[r])
            for c in active
                A[r, c] != 0 && (acc ⊻= 1)
            end
            (acc & 1) != 0 && return nothing
        end
        return e
    end

    best = solve(Int[])             # OSD-0
    bestw = best === nothing ? typemax(Int) : Int(sum(best))

    # Combination sweep over the λ least-reliable non-basis bits: try singles and pairs.
    λ = min(osd_order, length(nonbasis))
    if λ > 0
        cand = nonbasis[1:λ]
        # singles
        for i in 1:λ
            e = solve([cand[i]])
            if e !== nothing
                w = Int(sum(e))
                if w < bestw; bestw = w; best = e; end
            end
        end
        # pairs (the "combination sweep" of osd_cs)
        for i in 1:λ-1, j in i+1:λ
            e = solve([cand[i], cand[j]])
            if e !== nothing
                w = Int(sum(e))
                if w < bestw; bestw = w; best = e; end
            end
        end
    end
    return best
end

# ---------------------------------------------------------------------------------------------
# Top level.
# ---------------------------------------------------------------------------------------------

# (bp_method, osd_method, osd_order) — the paper's multi-decoder protocol.
const _BPOSD_DEFAULT_CONFIGS = ((:product_sum, :osd_cs, 10), (:minimum_sum, :osd_cs, 10))

"""Decode one logical type.  `check` (m×n) stacked above `logicals` (k×n) = H_eff; fix the check
syndrome to 0 and a random nontrivial logical pattern λ on the logical rows; BP+OSD; record the
minimum decoded weight over `trials × configs`.  Returns the best (min) weight, or `nothing`
when k=0 / no valid solution was ever found."""
function _bposd_one_type(check::Matrix{UInt8}, logicals::Matrix{UInt8}, n::Int,
                         trials::Int, configs, seed::Int)
    m, k = size(check, 1), size(logicals, 1)
    k == 0 && return nothing
    Heff = vcat(check, logicals)
    g = TannerGraph(Heff)
    p = 0.05
    prior_llr = log((1 - p) / p)
    rng = _LCG(seed)               # match Python's random.Random sequence shape (independent RNG)
    best = nothing
    for (bp_method, _osd_method, osd_order) in configs
        for _ in 1:trials
            lam = UInt8[_lcg_bit(rng) for _ in 1:k]
            any(!iszero, lam) || continue
            s = vcat(zeros(UInt8, m), lam)
            hard, posterior, converged = _bp_decode(g, s, prior_llr;
                                                     method=bp_method, max_iter=n)
            e = _osd(Heff, s, posterior; osd_order=osd_order)
            # also consider the raw BP solution when it already satisfied the syndrome
            cand = Vector{UInt8}[]
            e !== nothing && push!(cand, e)
            converged && push!(cand, hard)
            for ev in cand
                _syndrome(Heff, ev) == s || continue
                w = Int(sum(ev))
                best = best === nothing ? w : min(best, w)
            end
        end
    end
    return best
end

# A tiny independent RNG so the Julia run is deterministic given `seed` (the *values* of λ need not
# match Python bit-for-bit — both sample uniformly random nontrivial cosets; the distance bound is a
# minimum over the orbit and is robust to the particular λ ordering for a reliable low-rate code).
mutable struct _LCG
    state::UInt64
end
function _lcg_next(r::_LCG)
    r.state = (6364136223846793005 * r.state + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
    return r.state
end
_lcg_bit(r::_LCG) = UInt8((_lcg_next(r) >> 33) & 0x1)

"""BP-OSD stochastic UPPER bound on the CSS distance d = min(d_X, d_Z).

Returns a NamedTuple `(d_bound, d_X, d_Z)`.  Stochastic — an UPPER bound only (the BP+OSD decoder
can overestimate; it is never promoted to exact).  Pure Julia; no C/C++.

Coset method (paper V.C): the min-weight X-logical x satisfies H_Z x = 0 and must ANTICOMMUTE with a
dual (Z) logical to be nontrivial, so H_eff = (H_Z ; L_Z); symmetrically the Z-distance stacks L_X."""
function bposd_distance(code::BBCode; trials::Int=200, configs=_BPOSD_DEFAULT_CONFIGS, seed::Int=0)
    X, Z = css_logicals(code.HX, code.HZ)
    dX = _bposd_one_type(code.HZ, Z, code.n, trials, configs, seed)        # X-logicals via H_Z + L_Z
    dZ = _bposd_one_type(code.HX, X, code.n, trials, configs, seed + 1)    # Z-logicals via H_X + L_X
    cand = Int[v for v in (dX, dZ) if v !== nothing]
    d_bound = isempty(cand) ? nothing : minimum(cand)
    return (d_bound=d_bound, d_X=dX, d_Z=dZ)
end
