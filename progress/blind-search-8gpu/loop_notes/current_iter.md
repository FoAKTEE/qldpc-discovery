# current_iter — iter 14: attempted high-k d>=6; brute-force timed out -> d=5 stands; ARC CONCLUSION

## Anchor
Loop-driven continuation of the documented high-k distance lever (iter13 lifted d=2->5; try d>=6 toward
the paper's d=8 high-k codes, staying pure-Julia + blind).

## ATTEMPT + HONEST OUTCOME
iter14 experiment: richer weight-6 factored families ((1+y^a+y2a)(1+x^j), etc.) scanned for k>=24, d>=6
via ISD. TIMED OUT (250s, exit 143, no result) — ISD over weight-6 high-k codes (large k_code) at 400
iters x hundreds of (family,lattice,param) combos does not scale by brute force. Signal: pushing high-k
distance from d=5 -> d=8 has hit diminishing returns under generic structural search. The paper's d=8-14
high-k codes use SPECIFIC weight-8 cross-factored algebra; recovering them needs targeted construction
(or a smarter, cheaper search), not brute-force family scanning. The SOLID achieved result is iter13's
d=2 -> d=5 lift ([[294,78,5]], [[336,72,5]], [[288,48,5]]), committed (5af1843 / main 9607413).

## ARC CONCLUSION (iter9-14)
User's explicit request (audit + pipeline changes, iter9) DELIVERED + validated (iter10). Both prioritized
gaps DELIVERED: #2 ISD large-n upper-bound refuter (iter11), #1 high-k campaign (iter12) + d-lift (iter13).
Two package bugs root-caused+fixed+regression-tested+ported (BZ OOM, DEDUP stall). All committed on
blind-zero + main. Records: progress/audit-vs-paper/{AUDIT,BROADENED_VS_PAPER,HIGHK_VS_PAPER}.md.

## OPEN FRONTIER (handed to user — genuine research decisions, not mechanical)
1. MILP-grade large-n EXACT lower-bound cert (paper's HiGHS role) — needs relaxing pure-Julia (user's
   firm constraint) or a pure-Julia MILP build (Tulip+B&B; major, uncertain payoff).
2. Paper's d=8-14 high-k codes — need targeted weight-8 cross-factored construction; brute-force search
   doesn't reach them cheaply.

## STATUS
Pausing autonomous heavy-compute at this well-documented boundary. Everything requested is done +
committed; the two open levers require user direction (relax pure-Julia? / invest in targeted high-k
constructions?). Not setting active=false unilaterally — awaiting direction.
