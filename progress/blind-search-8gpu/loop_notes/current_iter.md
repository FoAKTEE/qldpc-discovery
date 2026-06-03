# current_iter — iter 12: high-k campaign (user #1) + result

## Anchor
User #1 (after #2): recover the paper's high-k codes (k=24-54) the FOM-mode search missed (it maxed at
k=20, ZERO cells k>=24 — random BB polys are high-rank -> low k).

## EDIT (committed with the mode)
blind_search.jl OBJECTIVE=fom|k. :k mode = univariate/CRT seeding (UNIVAR=0.8; A=1+y^a+y^2a, B=1+x^j+x^2j,
RANDOM a,j — lem:crt_k family, NOT catalog), rate filter OFF, frontier sorted by k.

## VERIFY (campaign + ISD certify)
Campaign (OBJECTIVE=k, n<=360, WALL=90, cheap search d): 672411 screened, 249 cells, k=24..160 (FOM-mode
maxed at 20). ISD certification (iter11 tool): 249 certified, 115 EXACT. ISD demotes the BP-OSD garbage
these ultra-degenerate codes produce, e.g. [[360,160,156]] (BP-OSD d0=156) -> EXACT d=2.

## RESULT (progress/audit-vs-paper/HIGHK_VS_PAPER.md)
- k-AXIS RECOVERED: produces k=24..160 at n<=360 (was impossible in FOM mode). The ISD tool is essential
  (true d vs BP-OSD garbage).
- BUT pure univariate is d=2 at extreme k; only k=24 reaches d=6-10 (UB). The paper's high-k codes (d=4-8:
  [[144,54,4]], [[288,50,8]]) use RICHER weight-8 cross-factored structure than pure 3-term univariate.
  So we reach the right (n,k) but LOWER d than the paper's high-k optima.
- Next lever (documented, not run): higher-weight/factored high-k seeds to lift d from 2 toward 4-8.

## STATUS
Both user asks delivered: #2 (ISD large-n upper-bound refuter, iter11) + #1 (high-k campaign, iter12).
Honest: ISD refutes overestimates + the high-k axis is recovered (low d); full MILP-grade large-n exact
cert and the paper's d=4-8 high-k optima remain documented open levers. Committing artifacts + porting.
