# Real GPU batched GF(2) rank via a Julia PACKAGE EXTENSION (CUDA.jl, OPTIONAL dep).
#
# WHAT / WHY
# ----------
# The Python source of truth is qcode_discovery/algebra/gf2.py::rank — a per-matrix
# F(2) Gaussian elimination. This file exposes a *batched* version of that exact
# computation that can run on an NVIDIA GPU, while keeping CUDA an OPTIONAL dependency:
#
#   * The hook `_cuda_rank_impl(mats)` is defined here as a STUB that errors. It is the
#     extension point. The package loads and runs with NO CUDA installed.
#   * The package extension `ext/QCodeDiscoveryCUDAExt.jl` (loaded automatically by Julia
#     ONLY when CUDA.jl is present in the active environment) overloads `_cuda_rank_impl`
#     with a real CUDA kernel — one GPU thread per matrix, bit-packed into UInt64 words.
#   * `cuda_batched_rank(mats)` is the public entry: it dispatches to the GPU overload if
#     the extension is loaded AND a device is functional, else falls back to CPU threads.
#
# ABSOLUTELY NO C/C++ deps: CUDA.jl is a pure-Julia + CUDA-runtime package; the GF(2)
# elimination kernel is written by hand in Julia and compiled to PTX by CUDA.jl. We do
# NOT wrap HiGHS / ldpc / igraph. The result is bit-identical, element for element, to
# `[gf2_rank(M) for M in mats]` (which itself matches gf2.py::rank).
#
# This file does NOT redefine any symbol from gpu.jl: it adds new names
# (`cuda_batched_rank`, `_cuda_rank_impl`, `_gf2_pack_words`, `_gf2_packed_rank!`,
# `cuda_ext_loaded`). It reuses `as_f2`, `gf2_rank` from module scope.

# ---------------------------------------------------------------------------
# Bit-packing: 0/1 matrix -> one flat UInt64 buffer, 64 columns per word, row-major.
# Shared by the CPU reference and the GPU kernel so both operate on identical layout.
# ---------------------------------------------------------------------------

"""
    _gf2_pack_words(M) -> (words::Vector{UInt64}, nrows::Int, nwords::Int)

Pack a 0/1 matrix into a flat row-major `UInt64` buffer: `nwords = cld(ncols, 64)` words
per row, column `c` living in bit `(c-1) & 63` of word `(c-1) >> 6`. Layout matches the
GPU kernel exactly so the packed CPU and GPU eliminations are bit-for-bit comparable.
"""
function _gf2_pack_words(M::AbstractMatrix)
    R = as_f2(M)
    nrows, ncols = size(R)
    nwords = cld(ncols, 64)
    words = zeros(UInt64, nrows * nwords)
    @inbounds for c in 1:ncols
        w = (c - 1) >> 6
        b = (c - 1) & 63
        bit = UInt64(1) << b
        for i in 1:nrows
            if R[i, c] == 0x1
                words[(i - 1) * nwords + w + 1] |= bit
            end
        end
    end
    return words, nrows, nwords
end

"""
    _gf2_packed_rank!(words, nrows, nwords) -> Int

GF(2) rank of one bit-packed (row-major, `nwords` words/row) matrix, in place. This is
the scalar kernel the GPU runs once per matrix; kept here so the CPU path and the GPU
path execute the SAME algorithm on the SAME packed layout (modulo parallelism).
"""
function _gf2_packed_rank!(words::AbstractVector{UInt64}, nrows::Int, nwords::Int)
    rank = 0
    pr = 0                       # 0-based current pivot row
    @inbounds for w in 0:nwords-1
        for b in 0:63
            mask = UInt64(1) << b
            piv = -1
            i = pr
            while i < nrows
                if (words[i * nwords + w + 1] & mask) != 0
                    piv = i; break
                end
                i += 1
            end
            piv < 0 && continue
            if piv != pr
                for ww in 0:nwords-1
                    a = words[pr * nwords + ww + 1]
                    words[pr * nwords + ww + 1] = words[piv * nwords + ww + 1]
                    words[piv * nwords + ww + 1] = a
                end
            end
            i = 0
            while i < nrows
                if i != pr && (words[i * nwords + w + 1] & mask) != 0
                    for ww in 0:nwords-1
                        words[i * nwords + ww + 1] ⊻= words[pr * nwords + ww + 1]
                    end
                end
                i += 1
            end
            rank += 1; pr += 1
            pr >= nrows && return rank
        end
    end
    return rank
end

# ---------------------------------------------------------------------------
# Flatten a batch into ONE padded UInt64 buffer + per-matrix offsets/shape.
# This is exactly the device-friendly layout the GPU kernel consumes.
# ---------------------------------------------------------------------------

"""
    _gf2_flatten_batch(mats) -> (words, offsets, rows, nwords)

Concatenate the bit-packed words of every matrix into a single `Vector{UInt64}`, with
0-based per-matrix `offsets`, row counts `rows`, and words-per-row `nwords`. A single
contiguous buffer is what we copy to the device in one `CuArray` transfer.
"""
function _gf2_flatten_batch(mats::Vector{<:AbstractMatrix})
    nmats = length(mats)
    packs = Vector{Tuple{Vector{UInt64},Int,Int}}(undef, nmats)
    total = 0
    @inbounds for i in 1:nmats
        wds, nr, nw = _gf2_pack_words(mats[i])
        packs[i] = (wds, nr, nw)
        total += nr * nw
    end
    words   = Vector{UInt64}(undef, total)
    offsets = Vector{Int}(undef, nmats)
    rows    = Vector{Int}(undef, nmats)
    nwords  = Vector{Int}(undef, nmats)
    pos = 0
    @inbounds for i in 1:nmats
        wds, nr, nw = packs[i]
        offsets[i] = pos; rows[i] = nr; nwords[i] = nw
        copyto!(words, pos + 1, wds, 1, length(wds))
        pos += nr * nw
    end
    return words, offsets, rows, nwords
end

# ---------------------------------------------------------------------------
# Extension hook + public entry.
# ---------------------------------------------------------------------------

"""
    cuda_ext_loaded() -> Bool

True once the `QCodeDiscoveryCUDAExt` package extension has loaded (i.e. CUDA.jl is in
the active environment). The extension's `__init__` flips `_CUDA_EXT_LOADED`; as a
timing-independent backstop we also check whether the extension has registered its
concrete `_cuda_rank_impl(::Vector{UInt64}, …)` method (the fallback here takes only
`AbstractVector`, so >1 method means the overload is present). Independent of whether a
device is actually *functional* — see `cuda_available()` for that runtime probe.
"""
const _CUDA_EXT_LOADED = Ref(false)
cuda_ext_loaded() = _CUDA_EXT_LOADED[] || (length(methods(_cuda_rank_impl)) > 1)

"""
    _cuda_rank_impl(words, offsets, rows, nwords) -> Vector{Int}

Extension hook: real GPU implementation lives in `ext/QCodeDiscoveryCUDAExt.jl`, which
adds a MORE-SPECIFIC method `_cuda_rank_impl(::Vector{UInt64}, ::Vector{Int}, ...)` when
CUDA.jl is loaded. This generic `AbstractVector` fallback is what exists without the
extension: it errors (and `cuda_batched_rank` never reaches it — it checks
`cuda_ext_loaded()` first). The signatures differ deliberately so the extension *adds*
a method instead of *overwriting* one (overwriting is illegal during precompilation).
"""
function _cuda_rank_impl(::AbstractVector, ::AbstractVector, ::AbstractVector, ::AbstractVector)
    error("CUDA extension not loaded: add CUDA.jl to the environment to enable the GPU path")
end

"""
    cuda_batched_rank(mats::Vector{<:AbstractMatrix}; force_cpu=false) -> Vector{Int}

GF(2) rank of every matrix in `mats`, computed on the GPU when the CUDA extension is
loaded and a device is functional, else on CPU threads. Bit-identical, element for
element, to `[gf2_rank(M) for M in mats]` (the pure-Julia port of gf2.py::rank).

The GPU path bit-packs the whole batch into one UInt64 buffer, transfers it once, runs
one GPU thread per matrix, and copies the rank vector back. No C/C++ libraries are
wrapped: the elimination kernel is hand-written Julia compiled to PTX by CUDA.jl.
"""
function cuda_batched_rank(mats::Vector{<:AbstractMatrix}; force_cpu::Bool = false)
    isempty(mats) && return Int[]
    # Take the GPU path whenever a device is functional. The dispatch to the extension's
    # `_cuda_rank_impl` is done via `invokelatest` to dodge world-age issues (the method
    # is registered lazily by the extension after this function was compiled), and any
    # failure — extension not loaded (MethodError), OOM, driver — degrades to CPU. This
    # is correctness-safe: the CPU fallback is bit-identical to the GPU result.
    if !force_cpu && cuda_available()
        try
            words, offsets, rows, nwords = _gf2_flatten_batch(mats)
            return Base.invokelatest(_cuda_rank_impl, words, offsets, rows, nwords)::Vector{Int}
        catch err
            err isa MethodError || @warn "GPU batched_rank failed; falling back to CPU" exception=err
        end
    end
    return _cuda_batched_rank_cpu(mats)
end

"""CPU reference for `cuda_batched_rank`: the packed kernel run per matrix, over threads.
Used both as the fallback and (in tests) as the ground truth the GPU must match."""
function _cuda_batched_rank_cpu(mats::Vector{<:AbstractMatrix})
    out = Vector{Int}(undef, length(mats))
    Threads.@threads for i in eachindex(mats)
        wds, nr, nw = _gf2_pack_words(mats[i])
        out[i] = _gf2_packed_rank!(wds, nr, nw)
    end
    return out
end
