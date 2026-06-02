# Data-parallel GF(2): batched rank + batched BB css_k screening. Pure Julia.
# Port of the data-parallel intent of qcode_discovery/algebra/gf2.py (rank/css_k),
# applied across MANY matrices/candidates at once. Two paths:
#   * CPU: Threads.@threads over the per-matrix kernels already in gf2.jl / codes.jl.
#   * GPU: an OPTIONAL CUDA.jl path, gated by a RUNTIME check so this file (and the
#     whole package) loads and runs with no CUDA installed. CUDA is NOT a dependency.
#
# Depends only on core functions in module scope: gf2_rank, BBCode, css_k.

# ---------------------------------------------------------------------------
# Runtime CUDA detection (no compile-time dependency on CUDA.jl)
# ---------------------------------------------------------------------------

"""
    cuda_available() -> Bool

Runtime probe for a usable CUDA.jl + GPU, WITHOUT making CUDA a package dependency.
Returns `false` (so callers fall back to the threaded CPU path) when CUDA.jl is not
installed, fails to load, or reports no functional device. Result is memoised.
"""
const _CUDA_STATE = Ref{Union{Nothing,Bool}}(nothing)
const _CUDA_MOD = Ref{Any}(nothing)

function cuda_available()
    _CUDA_STATE[] !== nothing && return _CUDA_STATE[]::Bool
    ok = false
    try
        # `Base.require` only succeeds if CUDA is an installed, resolvable package;
        # wrapped in try so a missing package never errors out of this call.
        cuda = Base.require(Base.PkgId(
            Base.UUID("052768ef-5323-5732-b1bb-66c8b64840ba"), "CUDA"))
        if Base.invokelatest(getfield(cuda, :functional))
            _CUDA_MOD[] = cuda
            ok = true
        end
    catch
        ok = false
    end
    _CUDA_STATE[] = ok
    return ok
end

# ---------------------------------------------------------------------------
# Batched GF(2) rank
# ---------------------------------------------------------------------------

"""
    batched_rank(mats::Vector{<:AbstractMatrix}; use_gpu=cuda_available()) -> Vector{Int}

Compute the GF(2) rank of every matrix in `mats` in parallel. Identical, element for
element, to `[gf2_rank(M) for M in mats]`, but distributes the work across
`Threads.nthreads()` threads (CPU path) or onto the GPU when CUDA.jl is available.

The GPU path bit-packs each matrix into `UInt64` words and runs a per-matrix
Gaussian elimination over GF(2); it is only taken when `use_gpu` is true (default:
a live CUDA device is detected at runtime). Otherwise the CPU-threaded path runs.
"""
function batched_rank(mats::Vector{<:AbstractMatrix}; use_gpu::Bool = cuda_available())
    if use_gpu && cuda_available()
        try
            return _batched_rank_gpu(mats)
        catch
            # Any GPU failure (OOM, driver, etc.) degrades gracefully to CPU.
        end
    end
    return _batched_rank_cpu(mats)
end

"""CPU-threaded batched GF(2) rank — one `gf2_rank` per matrix, spread over threads."""
function _batched_rank_cpu(mats::Vector{<:AbstractMatrix})
    out = Vector{Int}(undef, length(mats))
    Threads.@threads for i in eachindex(mats)
        out[i] = gf2_rank(mats[i])
    end
    return out
end

# --- GPU path -------------------------------------------------------------
# Bit-packed GF(2) Gaussian elimination, one CUDA thread per matrix. Self-contained
# (no ldpc / no C deps); only loaded/used when cuda_available() is true.

"""Pack a 0/1 matrix into one `UInt64` word per row (cols ≤ 64 per word block)."""
function _pack_rows(M::AbstractMatrix)
    R = as_f2(M)
    nrows, ncols = size(R)
    nwords = cld(ncols, 64)
    P = zeros(UInt64, nrows, nwords)
    @inbounds for i in 1:nrows, c in 1:ncols
        if R[i, c] == 0x1
            w = (c - 1) >> 6 + 1
            b = (c - 1) & 63
            P[i, w] |= (UInt64(1) << b)
        end
    end
    return P, nrows, nwords
end

"""GF(2) rank of a bit-packed (nrows × nwords) row block via in-place elimination."""
function _packed_rank!(P::AbstractMatrix{UInt64}, nrows::Int, nwords::Int)
    rank = 0
    pr = 1
    @inbounds for w in 1:nwords
        for b in 0:63
            mask = UInt64(1) << b
            piv = 0
            for i in pr:nrows
                if (P[i, w] & mask) != 0
                    piv = i
                    break
                end
            end
            piv == 0 && continue
            if piv != pr
                for ww in 1:nwords
                    P[pr, ww], P[piv, ww] = P[piv, ww], P[pr, ww]
                end
            end
            for i in 1:nrows
                if i != pr && (P[i, w] & mask) != 0
                    for ww in 1:nwords
                        P[i, ww] ⊻= P[pr, ww]
                    end
                end
            end
            rank += 1
            pr += 1
            pr > nrows && return rank
        end
    end
    return rank
end

# GPU code is NEVER referenced at include-time (no `using CUDA`, no CUDA macros in the
# compiled body). Instead the kernel + launcher are emitted as an `Expr` and `eval`'d
# into this module the first time a live CUDA device is detected. This keeps CUDA an
# OPTIONAL, runtime-only path: the package compiles and runs with no CUDA installed.
const _GPU_READY = Ref(false)

"""Bit-packed flatten of `mats` into a single padded UInt64 buffer (row-major / matrix)."""
function _flatten_packed(mats::Vector{<:AbstractMatrix})
    nmats = length(mats)
    packed = Vector{Tuple{Matrix{UInt64},Int,Int}}(undef, nmats)
    total = 0
    for i in 1:nmats
        P, nr, nw = _pack_rows(mats[i])
        packed[i] = (P, nr, nw)
        total += nr * nw
    end
    words = zeros(UInt64, total)
    offsets = zeros(Int, nmats)
    rows = zeros(Int, nmats)
    nwords = zeros(Int, nmats)
    pos = 0
    for i in 1:nmats
        P, nr, nw = packed[i]
        offsets[i] = pos; rows[i] = nr; nwords[i] = nw
        @inbounds for r in 0:nr-1, w in 0:nw-1
            words[pos + r * nw + w + 1] = P[r + 1, w + 1]
        end
        pos += nr * nw
    end
    return words, offsets, rows, nwords
end

"""Compile the CUDA kernel + launcher into this module (idempotent). Requires CUDA loaded."""
function _ensure_gpu_compiled()
    _GPU_READY[] && return
    cuda = _CUDA_MOD[]
    @eval Main begin end  # no-op guard for invokelatest world-age
    Core.eval(@__MODULE__, quote
        const CUDA = $cuda
        # One CUDA thread per matrix; in-place GF(2) elimination on the padded buffer.
        function _gf2_rank_kernel!(ranks, words, offsets, rows, nwords, nmats)
            idx = CUDA.threadIdx().x + (CUDA.blockIdx().x - 1) * CUDA.blockDim().x
            if idx <= nmats
                off = offsets[idx]; nr = rows[idx]; nw = nwords[idx]
                rank = 0; pr = 0; w = 0
                while w < nw
                    b = 0
                    while b < 64
                        mask = UInt64(1) << b
                        piv = -1; i = pr
                        while i < nr
                            if (words[off + i * nw + w + 1] & mask) != 0
                                piv = i; break
                            end
                            i += 1
                        end
                        if piv >= 0
                            if piv != pr
                                ww = 0
                                while ww < nw
                                    a = words[off + pr * nw + ww + 1]
                                    words[off + pr * nw + ww + 1] = words[off + piv * nw + ww + 1]
                                    words[off + piv * nw + ww + 1] = a
                                    ww += 1
                                end
                            end
                            i = 0
                            while i < nr
                                if i != pr && (words[off + i * nw + w + 1] & mask) != 0
                                    ww = 0
                                    while ww < nw
                                        words[off + i * nw + ww + 1] ⊻= words[off + pr * nw + ww + 1]
                                        ww += 1
                                    end
                                end
                                i += 1
                            end
                            rank += 1; pr += 1
                            if pr >= nr
                                ranks[idx] = rank; return nothing
                            end
                        end
                        b += 1
                    end
                    w += 1
                end
                ranks[idx] = rank
            end
            return nothing
        end

        function _launch_gpu_rank(words, offsets, rows, nwords)
            nmats = length(offsets)
            d_words = CUDA.CuArray(words)
            d_off = CUDA.CuArray(offsets)
            d_rows = CUDA.CuArray(rows)
            d_nw = CUDA.CuArray(nwords)
            d_ranks = CUDA.zeros(Int, nmats)
            threads = 256
            blocks = cld(nmats, threads)
            CUDA.@cuda threads = threads blocks = blocks _gf2_rank_kernel!(
                d_ranks, d_words, d_off, d_rows, d_nw, nmats)
            return Array(d_ranks)
        end
    end)
    _GPU_READY[] = true
    return
end

function _batched_rank_gpu(mats::Vector{<:AbstractMatrix})
    isempty(mats) && return Int[]
    _ensure_gpu_compiled()
    words, offsets, rows, nwords = _flatten_packed(mats)
    return Base.invokelatest(getfield(@__MODULE__, :_launch_gpu_rank),
        words, offsets, rows, nwords)
end

# ---------------------------------------------------------------------------
# Batched BB css_k screening
# ---------------------------------------------------------------------------

"""
    batched_css_k(cands; use_gpu=cuda_available()) -> Vector{Int}

Screen many bivariate-bicycle candidates in parallel, returning the encoding dimension
`k = n - rank(H_X) - rank(H_Z)` for each. Each candidate is `(l, m, A, B)` with `A`,`B`
polynomial strings (or a `BBCode`). Identical, element for element, to running
`css_k` one candidate at a time, but threaded across all candidates on the CPU
(and using the GPU batched-rank kernel for the two ranks when CUDA is available).
"""
function batched_css_k(cands; use_gpu::Bool = cuda_available())
    codes = Vector{BBCode}(undef, length(cands))
    Threads.@threads for i in eachindex(cands)
        codes[i] = _as_bbcode(cands[i])
    end
    if use_gpu && cuda_available()
        try
            # Build the 2N rank problems (H_X and H_Z for each code) and batch them.
            mats = Vector{Matrix{UInt8}}(undef, 2 * length(codes))
            @inbounds for i in eachindex(codes)
                mats[2i-1] = codes[i].HX
                mats[2i]   = codes[i].HZ
            end
            r = _batched_rank_gpu(mats)
            return [codes[i].n - r[2i-1] - r[2i] for i in eachindex(codes)]
        catch
            # Fall through to CPU path on any GPU failure.
        end
    end
    out = Vector{Int}(undef, length(codes))
    Threads.@threads for i in eachindex(codes)
        out[i] = css_k(codes[i])
    end
    return out
end

"""Coerce a candidate to a `BBCode`: pass a `BBCode` through, or build from `(l,m,A,B)`."""
_as_bbcode(c::BBCode) = c
function _as_bbcode(c::Tuple)
    l, m, A, B = c
    return BBCode(Int(l), Int(m), String(A), String(B))
end
