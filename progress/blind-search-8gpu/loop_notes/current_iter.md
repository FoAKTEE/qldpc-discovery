# current_iter — iter 11: large-n exact-certification tool (ISD, user-requested #2)

## Anchor
User: "2 then 1, don't ask again" -> #2 large-n exact certification, then #1 high-k campaign.

## DESIGN (honest reconciliation)
For BB CSS LOGICAL distance, dim ker(H_Z) = (n+k)/2 > n/2 -> only ONE information set fits -> the
multi/overlapping-info-set BZ lower-bound improvement gives NOTHING (existing code comment confirms),
and combinatorial enumeration hits C(kc,d) ~ 1e20 at n=288/d=16. True exact cert there needs an
industrial MILP (paper's HiGHS) — precluded by the pure-Julia (no C/C++) constraint. So the honest,
achievable, verifiable pure-Julia win is a TIGHT UPPER BOUND via Lee-Brickell information-set decoding:
it finds low-weight logicals BP-OSD misses (refuting overestimates), and a found logical of weight w is
an unconditional proof d<=w (UPPER bound, NOT a lower-bound certificate).

## EDIT
- julia/src/distance/isd.jl (NEW): _isd_min_logical + min_distance_isd (Lee-Brickell; random info set ->
  systematic form -> enumerate row-combos size 1..pmax; reuses packed-GF(2) helpers). Exported.
- scripts/search/certify.jl: ISD is now the PRIMARY upper-bound tightener (ISD_ITERS=1200, ISD_PMAX=2),
  BP-OSD a cross-check (SEEDS default 1). BZ still the exact certifier where it completes.
- julia/test/runtests.jl: ISD testset (finds [[18,4,4]]=4, [[72,12,6]]=6, gross [[144,12,12]]=12, never below).

## VERIFY
runtests.jl all PASS (RUNTESTS_EXIT=0): ISD testset 4/4 (gross d=12 found in 2.1s — exact BZ CANNOT
certify this), alloc regressions 12/12+2/2+3/3, exact-distance landmarks preserved (enum 4/4, BZ 3/3).
DEMOTION DEMO: broadened [[288,12,30]] (BP-OSD d0=30 overestimate) -> ISD d=16 = the paper's exact
catalog value for (288,12). ISD found the true weight-16 logical BP-OSD missed. [SOLID]

## STATUS
#2 delivered (honest: tight UB / overestimate-refuter; exact cert stays BZ-where-feasible; MILP-grade
large-n lower-bound cert acknowledged as the pure-Julia limit). Committing + porting to main. NEXT: #1
high-k campaign (k-maximizing search mode to recover the paper's k=24-54 codes the rate filter suppresses).
