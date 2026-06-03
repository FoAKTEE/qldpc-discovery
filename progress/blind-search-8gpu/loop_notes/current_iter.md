# current_iter — 8-GPU blind search, iter 2 (overwrite-mode)

## Anchor
User report: nvidia-smi shows all GPUs 0%. Investigate + debug why the GPUs aren't used.

## Diagnosis (evidence, tool-verified)
- CUDA.functional()=true, 8 devices visible, cuda_batched_rank runs on-device (mem allocates, ranks correct).
- ROOT CAUSE: the batched GF(2) rank GPU kernel (ext/QCodeDiscoveryCUDAExt.jl) is ONE-THREAD-PER-MATRIX
  (serial elimination per thread) -> near-zero A100 occupancy.
- Benchmark (4000 random 144x288 GF(2) matrices, rank):
    CPU batched_rank (256 threads): 300 ms/call
    GPU cuda_batched_rank:          1361 ms/call   (~0% util)
    => GPU is 0.22x CPU (~4.5x SLOWER) and effectively idle. ranks match (correct).
- Secondary: the search's heavy cost is BP-OSD distance (CPU); GPU only screens. So GPUs help only if
  (a) the screen kernel beats CPU AND screening volume is massive, or (b) distance also moves to GPU.

## Fix (in flight)
- Workflow wz2v59x93 (ultracode): rewrite the kernel for HIGH OCCUPANCY (block/warp per matrix,
  cooperative bit-packed elimination) to beat the 256-core CPU at real util; shard across all 8 GPUs;
  rework scripts/search/gpu_blind_search.jl to screen at massive scale on 8 GPUs + CPU distance on
  survivors. Honesty clause: if GPU still can't beat 256-core CPU for this workload, report
  cpu-is-better + recommend moving BP-OSD distance to GPU instead.

## Verifier
GPU-vs-CPU bench: 1361ms vs 300ms (0.22x), util ~0% — reproduced. CUDA functional=true, 8 devices.
code_quality_policy_pass: R1 (root-cause diagnosis, tool-verified) — PROVEN. Fix pending workflow.
