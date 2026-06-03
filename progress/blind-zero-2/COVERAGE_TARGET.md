# blind-zero-2 — coverage target (the ONLY retained info)

This is a clean-room re-run. ALL prior info (discovered frontiers, certified codes, research notes,
audit reports, paper-vs-blind comparisons) was deleted. The package (`julia/`), its Python port
(`python/`), and the blind search drivers (`scripts/search/`) are kept as TOOLING — they seed only
naive random / parametric-structural polynomials and admit distances via kernels; they carry no
catalog data.

The one piece of paper-derived knowledge retained is the **claimed parameter-space extent** below,
used ONLY to size the search so coverage spans where the paper (arXiv:2606.02418) reports results.
No specific code, polynomial, or [[n,k,d]] value is retained or seeded — the search rediscovers from
zero. Comparison of discovered codes to specific paper codes is strictly POST-HOC, in the report.

## Claimed parameter space (coverage target)
- **Family:** bivariate-bicycle (BB) CSS codes `H_X=(A|B), H_Z=(B^T|A^T)` over F2[x,y]/(x^l-1,y^m-1),
  AND the perturbed/non-CSS PBB family (4-tuple (A,B,C,D), commuting).
- **Block length:** `n = 2·l·m ≤ 1000`  (i.e. `l·m ≤ 500`).
- **Rate / logical dim:** `k ≤ 300` — must cover the LOW-k high-distance regime AND the HIGH-k regime.
- **Distance:** `d ≤ 300` — must cover the HIGH-distance regime (sparse codes, large d).
- **Check weight:** column/stabilizer weight from `3` (sparse) up to `~8` (the paper varies weight to
  reach its high-distance/high-FOM records).
- **Objective:** figure of merit `FOM = k·d²/n`, and separately the high-k axis.

## Coverage plan (how the search spans the above)
- Lattices: ALL `(l,m)`, `2≤l,m≤60`, `2lm≤1000` — the full BB lattice set to n=1000 (driver default).
- Weights: `WMIN=3 .. WMAX=8` (varying check weight).
- Objectives: a FOM sweep (CSS), a high-k campaign (`OBJECTIVE=k`), and the non-CSS PBB family
  (`MODE=pbb`); plus an evolutionary FOM search with a trustworthy ISD distance fitness.
- Honesty: search-time CSS distances are BP-OSD UPPER bounds; every headline code is then CERTIFIED
  post-hoc (Lee–Brickell ISD tight upper bound to refute overestimates; Brouwer–Zimmermann exact
  where tractable). PBB distances are exact symplectic. The report states each code's verifier status.
