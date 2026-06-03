# PBB (non-CSS) family vs paper (arXiv:2606.02418) — iter17

The audit flagged PBB as 79% of the paper's catalog (368/465 codes). The blind-zero search now exercises
PBB (MODE=pbb): random weight-3 (A,B) + random perturbations (C,D), kept only if the generators commute
(A C^T + B D^T symmetric) and the EXACT symplectic distance certifies.

## Result (blind random PBB campaign, n<=360, PBB_EXACT_NMAX=180)
- 94712 screened -> only 63 reached distance eval (random (A,B,C,D) rarely commute: ~0.07% survive),
  yielding 12 EXACT non-CSS PBB codes, all small (n<=168) and low-distance (d=2-4):
  [[24,4,4]], [[24,2,4]], [[120,8,2]], [[168,4,2]], ...
- Paper PBB catalog: 32 distinct (n,k) points across n in {36,72,108,144,180,360}, headline
  [[360,10,40]] FOM=44.4, [[180,6,21]] FOM=14.7, [[144,12,12]] FOM=12. **(n,k) overlap with ours: 0.**

## Honest finding
The PBB CAPABILITY works (exact non-CSS codes produced + certified), but blind RANDOM PBB seeding is far
too sparse — almost all random 4-tuples fail to commute, and the rare survivors are trivial (d=2). It
does not reach the paper's STRUCTURED PBB optima. This mirrors the CSS story exactly:
- CSS high-distance: needed varying weight (random) — RECOVERED ([[360,8,30]]).
- CSS high-k: needed univariate/factored structure — k-axis recovered, d capped 4-5.
- PBB: needs commute-by-construction structured (A,B,C,D) — only the family is reached blind.

## Consistent conclusion across all three axes
Blind generic/random search recovers the code FAMILIES and the rate-distance frontier SHAPE, but the
paper's specific high-FOM optima (weight-7 d=30, high-k d=8-14, PBB FOM-44) require STRUCTURED
constructions that are effectively catalog-derived — beyond generic blind seeds. The genuinely open
levers (structured PBB seeding; MILP large-n exact cert) are research efforts requiring either
constraint relaxation (pure-Julia -> MILP) or catalog-informed seeding (relaxing blind discipline).

## iter32: commute-by-construction (C=A,D=B) — solves efficiency but yields trivial d=2 codes
Tested the documented "commute-by-construction" PBB lever: C=A, D=B makes A C^T + B D^T = A A^T + B B^T,
which is ALWAYS symmetric -> guaranteed commuting non-CSS PBB. Result: 400/400 built (100% commute rate,
vs 0.07% for random C,D) and all non-CSS — so it FULLY solves the commutation-efficiency problem. BUT all
codes are d=2 (best EXACT [[48,8,2]]): the "doubled" structure is too symmetric to carry distance.

CLOSING the PBB lever honestly: BOTH generic approaches yield trivial PBB — random (A,B,C,D) is too sparse
(0.07% commute, d=2 survivors) and commute-by-construction (C=A,D=B) is efficient but d=2. Non-trivial
commuting PBB (the paper's FOM-44 [[360,10,40]] etc.) requires solving the commutation symmetry condition
A C^T + B D^T = sym FOR GOOD (C,D) — exactly the hard structural problem the paper's evolutionary search
solved. Generic structured PBB seeding does not straightforwardly reach it. Consistent with the cross-axis
conclusion: blind/generic recovers the family; the paper's specific optima need targeted construction.
