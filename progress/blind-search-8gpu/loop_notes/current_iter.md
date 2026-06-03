# current_iter — 8-GPU blind search, iter 3 (overwrite-mode)

## Anchor
Directive: fix the GPU 0%-util bug, and make the fix TO THE JULIA PACKAGE (not scratch).

## EDIT (fix landed in the package)
- julia/ext/QCodeDiscoveryCUDAExt.jl: replaced the ONE-THREAD-PER-MATRIX kernel with a
  WARP-PER-MATRIX kernel (32 lanes cooperate: ballot pivot-search + shuffle broadcast + lane-strided
  elimination, pivot row cached in shared mem; warps packed 8/block -> saturate all SMs) + a
  block-per-matrix fallback for wide matrices (>16 words/row). Dispatch in _cuda_rank_impl.
- julia/src/parallel/gpu_cuda.jl: threaded _gf2_flatten_batch (host bit-packing was single-threaded).

## VERIFY (tool-verified, TRF-R)
- Correctness: cuda_batched_rank == CPU gf2_rank, 0 mismatches @ 72x144,144x288,288x576,500x1000 + real BB.
- End-to-end (4000x 144x288): GPU 283 ms vs CPU(256t) 312 ms = 1.1x  [was 0.22x with old kernel] — GPUs now BEAT CPU.
- Kernel isolated: 98% A100 util, ~10.5 ms (device transfer+kernel+back).
- Package tests (CPU path, no CUDA): julia/test/runtests.jl -> PASS (exit 0).

## FINDING (typed) — why nvidia-smi still reads ~0% during the search
- claim: batched GF(2)-rank SCREENING is intrinsically GPU-light; GPU can't be saturated by it.
- evidence (modality=Measurement): cuda_batched_rank wall time breakdown = host-pack 325 ms vs
  GPU(transfer+kernel+back) 10.5 ms => GPU busy only 3.1% of wall time. And in the search, the
  EXPENSIVE step is BP-OSD distance on CPU (~45-80 s/round) >> the GPU screen (~3 s).
- status: [SOLID]. The kernel bug is FIXED (util when running = 98%, end-to-end 1.1x), but the GPUs
  will keep reading ~0% during the search because there isn't enough GPU work in screening.
- consequence: to actually saturate 8 A100s, the BP-OSD DISTANCE (belief propagation) must run on GPU.
  That is the real "use the GPUs" fix (next iteration) — plus build packed circulant rows directly
  (skip the dense UInt8 intermediate) to cut host-pack.

## code_quality_policy_pass
R2 (GPU kernel rewrite + threaded host pack, cross-validated vs CPU) -> PROVEN (kernel fix).
GPU-saturation via GPU BP-OSD distance -> [FUTURE] (next iteration).
