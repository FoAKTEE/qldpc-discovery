# current_iter — Julia+GPU migration, iter 1 (overwrite-mode)

## Anchor
Re-established management infra (.claude ralph loop + phys-agentic-loop) on main; launched the
FULL JULIA + GPU migration mission. Ultracode ON → Workflows drive the substantive ports.

## Done this iter
- Restored .claude/ (hooks, stop guard, inject scripts) on main; rewrote ralph-loop.local.md for the
  Julia+GPU mission (active:true, promise QLDPC_JULIA_GPU_MIGRATION_COMPLETE).
- Created progress/julia-migration/{RESEARCH_NOTE,port_plan,loop_notes}.
- Julia core already ported + verified (prior commits): GF2, ring, BB, theorems, enumeration distance,
  and the Brouwer–Zimmermann certified exact solver (HiGHS replacement) — [[72,12,6]] d=6 certified.

## Next
Run the migration Workflow: port PBB, BLISS dedup, BP-OSD, Tanner, LC, evaluation/search to Julia,
each cross-validated against Python; design the GPU layer + scalable solver.

## Verifier
julia/test/runtests.jl -> 28 pass (5 testsets).
