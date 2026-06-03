# RESEARCH NOTE — 8-GPU BLIND BB-CODE SEARCH (blind-zero, canonical)

**Mission.** From ZERO/scratch, run a catalog-BLIND search for BB quantum LDPC codes within
`[[n<=1000, k<=300, d<=300]]` using the pure-Julia `QCodeDiscovery` package, maximally parallel on
8x A100 GPUs + 256 CPU cores. Record + certify the discovered rate--distance frontier. Managed by the
ralph loop (.claude) + phys-agentic-loop methodology. Branch `blind-zero`; ultracode ON.

## Apparatus (all pure Julia, cross-validated vs the Python reference)
- GPU k-screen: batched GF(2) rank on all 8 A100s (CUDA extension), distributed per device.
- CPU distance: BP-OSD upper bound across 256 threads; MILP-BZ certified exact where feasible.
- Search: naive random weight-3 seeds (BLIND) -> k-screen -> distance -> MAP-Elites frontier by (n,k).

## Blind discipline (BINDING)
Naive seeds only; no paper data / no hardcoded codes / no catalog during search. Every [[n,k,d]] is
logged with modality (BP-OSD upper bound vs MILP-BZ certified) BEFORE any paper comparison; comparison
to the gross/Bravyi families is POST-HOC only.

## Status
- iter1: restored + audited + re-targeted `.claude` (was the finished Julia-migration mission) to this
  8-GPU blind-search mission; loop now manages it. Multi-GPU search driver being built + validated by a
  Workflow agent on the 8 A100s (scripts/search/gpu_blind_search.jl); frontier to be recorded on completion.

## Next tactics
1. Land + validate the multi-GPU driver (GPU rank == CPU on all 8 devices; all 8 used).
2. Run a substantial from-scratch blind search over BB codes n<=1000; record the frontier.
3. Certify the best frontier codes (min_distance_bz exact where feasible; else honest BP-OSD bound).
4. Post-hoc: compare the frontier to known BB codes (gross family etc.) — AFTER recording.

## Landmarks (post-hoc reference only; NOT used by the search)
gross [[144,12,12]] (k=12,d=12) · [[72,12,6]] · [[288,24,12]]=gross+gross.
