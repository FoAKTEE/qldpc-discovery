# Package extension: HIGH-OCCUPANCY batched GF(2) rank on NVIDIA GPUs (pure Julia + CUDA.jl).
#
# Loaded AUTOMATICALLY by Julia's extension mechanism iff CUDA.jl is present in the active project
# (see [weakdeps]/[extensions] in Project.toml). The base package (julia/src/) loads + runs WITHOUT
# this file and without CUDA. Overloads the stub `QCodeDiscovery._cuda_rank_impl` (src/parallel/
# gpu_cuda.jl). CUDA.jl compiles these Julia kernels to PTX — NO C/C++ wrapping.
#
# DESIGN. The original kernel was ONE THREAD PER MATRIX (serial elimination per thread) -> a single
# 256-thread block cannot fill an A100's 108 SMs, so util was ~0% and it was ~4.5x slower than the
# 256-core CPU. FIX: cooperate within a matrix.
#   * WARP-PER-MATRIX (`_rank_kernel_warp!`, the fast path): 32 lanes cooperate on one matrix
#     (warp-synchronous: ballot pivot-search + shuffle broadcast + lane-strided elimination, pivot
#     row cached in shared mem); warps packed many-per-block -> thousands of warps saturate all SMs.
#   * BLOCK-PER-MATRIX (`_rank_kernel_block!`, fallback for wide matrices): a whole block cooperates.
# The GF(2) rank is invariant to pivot choice; result is bit-identical to CPU `gf2_rank`.

module QCodeDiscoveryCUDAExt

using CUDA
import QCodeDiscovery: _cuda_rank_impl, _CUDA_EXT_LOADED

const MAX_PIVOT_WORDS = 16        # 16 UInt64 words/row -> up to 1024 columns (n<=1000 => <=16)

# --- WARP-PER-MATRIX: 32 lanes cooperate; sh caches each warp's pivot row (warps_per_block*max_nw) -
function _rank_kernel_warp!(ranks, words, offsets, rows, nwords, nmats, max_nw)
    warps_per_block = blockDim().x >> 5
    lane = (threadIdx().x - 1) & 31
    warp_in_block = (threadIdx().x - 1) >> 5
    mat = (blockIdx().x - 1) * warps_per_block + warp_in_block + 1
    mat > nmats && return nothing
    @inbounds begin
        off = offsets[mat]; nr = rows[mat]; nw = nwords[mat]
        sh = CuDynamicSharedArray(UInt64, warps_per_block * max_nw)
        pbase = warp_in_block * max_nw
        rank = Int32(0); pr = Int32(0)
        fullmask = 0xffffffff % UInt32
        w = 0
        while w < nw
            b = 0
            while b < 64
                mask = UInt64(1) << b
                myrow = Int32(-1)
                i = pr + lane
                while i < nr
                    if (words[off + i * nw + w + 1] & mask) != 0
                        myrow = i % Int32; break
                    end
                    i += 32
                end
                found = vote_ballot_sync(fullmask, myrow >= 0)
                if found != 0
                    src = trailing_zeros(found)                 # lowest lane (smallest row) with a hit
                    piv = shfl_sync(fullmask, myrow, src + 1)
                    if piv != pr
                        ww = lane
                        while ww < nw
                            a1 = words[off + pr * nw + ww + 1]
                            a2 = words[off + piv * nw + ww + 1]
                            words[off + pr * nw + ww + 1] = a2
                            words[off + piv * nw + ww + 1] = a1
                            ww += 32
                        end
                    end
                    sync_warp(fullmask)
                    ww = lane
                    while ww < nw
                        sh[pbase + ww + 1] = words[off + pr * nw + ww + 1]
                        ww += 32
                    end
                    sync_warp(fullmask)
                    i = lane
                    while i < nr
                        if i != pr && (words[off + i * nw + w + 1] & mask) != 0
                            base = off + i * nw
                            ww2 = 0
                            while ww2 < nw
                                words[base + ww2 + 1] ⊻= sh[pbase + ww2 + 1]
                                ww2 += 1
                            end
                        end
                        i += 32
                    end
                    sync_warp(fullmask)
                    rank += Int32(1); pr += Int32(1)
                    if pr >= nr
                        lane == 0 && (ranks[mat] = Int(rank))
                        return nothing
                    end
                end
                b += 1
            end
            w += 1
        end
        lane == 0 && (ranks[mat] = Int(rank))
    end
    return nothing
end

# --- BLOCK-PER-MATRIX fallback (wide matrices): block cooperates; tree-reduce pivot search ---------
function _rank_kernel_block!(ranks, words, offsets, rows, nwords, nmats)
    mat = blockIdx().x
    mat > nmats && return nothing
    tid = threadIdx().x; nthr = blockDim().x
    @inbounds begin
        off = offsets[mat]; nr = rows[mat]; nw = nwords[mat]
        shp = CuDynamicSharedArray(UInt64, nw)
        red = CuDynamicSharedArray(Int32, nthr, nw * sizeof(UInt64))
        rank = Int32(0); pr = Int32(0)
        w = 0
        while w < nw
            b = 0
            while b < 64
                mask = UInt64(1) << b
                lm = nr; i = pr + (tid - 1)
                while i < nr
                    if (words[off + i * nw + w + 1] & mask) != 0
                        lm = i; break
                    end
                    i += nthr
                end
                red[tid] = lm % Int32
                sync_threads()
                s = nthr >> 1
                while s > 0
                    if tid <= s && red[tid + s] < red[tid]
                        red[tid] = red[tid + s]
                    end
                    sync_threads()
                    s >>= 1
                end
                piv = Int(red[1]); sync_threads()
                if piv < nr
                    if piv != pr
                        ww = tid - 1
                        while ww < nw
                            a1 = words[off + pr * nw + ww + 1]
                            a2 = words[off + piv * nw + ww + 1]
                            words[off + pr * nw + ww + 1] = a2
                            words[off + piv * nw + ww + 1] = a1
                            ww += nthr
                        end
                        sync_threads()
                    end
                    ww = tid - 1
                    while ww < nw
                        shp[ww + 1] = words[off + pr * nw + ww + 1]
                        ww += nthr
                    end
                    sync_threads()
                    i = tid - 1
                    while i < nr
                        if i != pr && (words[off + i * nw + w + 1] & mask) != 0
                            base = off + i * nw
                            ww2 = 0
                            while ww2 < nw
                                words[base + ww2 + 1] ⊻= shp[ww2 + 1]
                                ww2 += 1
                            end
                        end
                        i += nthr
                    end
                    sync_threads()
                    rank += Int32(1); pr += Int32(1)
                    if pr >= nr
                        tid == 1 && (ranks[mat] = Int(rank))
                        return nothing
                    end
                end
                b += 1
            end
            w += 1
        end
        tid == 1 && (ranks[mat] = Int(rank))
    end
    return nothing
end

# Overload the package hook: warp-per-matrix when rows fit MAX_PIVOT_WORDS, else block-per-matrix.
function _cuda_rank_impl(words::Vector{UInt64}, offsets::Vector{Int},
                         rows::Vector{Int}, nwords::Vector{Int})
    nmats = length(offsets)
    nmats == 0 && return Int[]
    max_nw = maximum(nwords)
    d_words = CuArray(words); d_off = CuArray(offsets)
    d_rows = CuArray(rows);   d_nw = CuArray(nwords)
    d_ranks = CUDA.zeros(Int, nmats)
    if max_nw <= MAX_PIVOT_WORDS
        wpb = 8                                   # 8 warps/block = 256 threads
        threads = wpb * 32
        blocks = cld(nmats, wpb)
        shmem = wpb * max_nw * sizeof(UInt64)
        @cuda threads = threads blocks = blocks shmem = shmem _rank_kernel_warp!(
            d_ranks, d_words, d_off, d_rows, d_nw, nmats, max_nw)
    else
        threads = min(256, max(32, nextpow(2, maximum(rows))))
        shmem = max_nw * sizeof(UInt64) + threads * sizeof(Int32)
        @cuda threads = threads blocks = nmats shmem = shmem _rank_kernel_block!(
            d_ranks, d_words, d_off, d_rows, d_nw, nmats)
    end
    CUDA.synchronize()
    return Array(d_ranks)
end

function __init__()
    _CUDA_EXT_LOADED[] = true
    return
end

end # module
