# Package extension: real GPU batched GF(2) rank on NVIDIA hardware via CUDA.jl.
#
# Loaded AUTOMATICALLY by Julia's extension mechanism iff CUDA.jl is present in the
# active project (see the [weakdeps]/[extensions] stanza for Project.toml in the report).
# The base package (julia/src/) loads and runs WITHOUT this file and without CUDA.
#
# It overloads the stub `QCodeDiscovery._cuda_rank_impl` (defined in src/gpu_cuda.jl) with
# a hand-written CUDA kernel: one GPU thread per matrix, bit-packed GF(2) Gaussian
# elimination on UInt64 words. NO C/C++ wrapping — CUDA.jl compiles this Julia kernel to
# PTX. The algorithm is identical to the CPU reference `_gf2_packed_rank!`.

module QCodeDiscoveryCUDAExt

using CUDA
import QCodeDiscovery: _cuda_rank_impl, _CUDA_EXT_LOADED

# --- device kernel: GF(2) rank of one matrix, bit-packed (row-major, nwords/row) -------
# Mirrors src/gpu_cuda.jl::_gf2_packed_rank! exactly, but with 0-based device indexing
# and no allocation. `words` is the single padded batch buffer; matrix `idx` lives at
# `offsets[idx]`, has `rows[idx]` rows of `nwords[idx]` UInt64 words each.
function _gf2_rank_kernel!(ranks, words, offsets, rows, nwords, nmats)
    idx = (blockIdx().x - 1) * blockDim().x + threadIdx().x
    if idx <= nmats
        off = offsets[idx]
        nr  = rows[idx]
        nw  = nwords[idx]
        rank = 0
        pr = 0                                  # 0-based current pivot row
        w = 0
        @inbounds while w < nw
            b = 0
            while b < 64
                mask = UInt64(1) << b
                piv = -1
                i = pr
                while i < nr
                    if (words[off + i * nw + w + 1] & mask) != 0
                        piv = i
                        break
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
                    rank += 1
                    pr += 1
                    if pr >= nr
                        ranks[idx] = rank
                        return nothing
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

# --- overload of the package hook: copy batch up, launch, copy ranks back --------------
function _cuda_rank_impl(words::Vector{UInt64}, offsets::Vector{Int},
                         rows::Vector{Int}, nwords::Vector{Int})
    nmats = length(offsets)
    d_words = CuArray(words)
    d_off   = CuArray(offsets)
    d_rows  = CuArray(rows)
    d_nw    = CuArray(nwords)
    d_ranks = CUDA.zeros(Int, nmats)

    threads = 256
    blocks  = cld(nmats, threads)
    @cuda threads = threads blocks = blocks _gf2_rank_kernel!(
        d_ranks, d_words, d_off, d_rows, d_nw, nmats)
    CUDA.synchronize()
    return Array(d_ranks)
end

function __init__()
    _CUDA_EXT_LOADED[] = true
    return
end

end # module
