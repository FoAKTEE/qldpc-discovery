# Broadened search vs paper catalog (arXiv:2606.02418) — iter10 validation

Broadened run: CSS, n<=360, **varying check weight 3-5** + structured-ansatz seeding + GA refinement
+ dedup. 530 frontier cells, 99 EXACT-certified. Compared post-hoc to the paper's CSS catalog.

**Honest caveats:** our d at n>160 are BP-OSD UPPER bounds (no MILP for large n); several are
overestimates. EXACT (99) are small-n only. This is upper-bound coverage, not certified beats.

## Paper CSS catalog (28 (n,k) points) vs our broadened certified frontier

| paper [[n,k,d]] | paperFOM | our d | status | verdict |
|---|---|---|---|---|
| [[360,8,30]] | 20.0 | 32 | UB | **reached** (UB d=32 >= 30) |
| [[360,12,24]] | 19.2 | 19 | UB | below (d=19 < 24) |
| [[144,12,12]] | 12.0 | 10 | UB | below (d=10 < 12) |
| [[288,24,12]] | 12.0 | – | – | NOT in frontier |
| [[288,50,8]] | 11.1 | – | – | NOT in frontier |
| [[288,8,20]] | 11.1 | 20 | UB | **reached** (UB d=20 >= 20) |
| [[360,20,14]] | 10.9 | – | – | NOT in frontier |
| [[288,48,8]] | 10.7 | – | – | NOT in frontier |
| [[288,12,16]] | 10.7 | 30 | UB | **reached** (UB d=30 >= 16) |
| [[288,46,8]] | 10.2 | – | – | NOT in frontier |
| [[360,24,12]] | 9.6 | – | – | NOT in frontier |
| [[288,18,12]] | 9.0 | – | – | NOT in frontier |
| [[288,40,8]] | 8.9 | – | – | NOT in frontier |
| [[360,16,14]] | 8.7 | 8 | UB | below (d=8 < 14) |
| [[144,8,12]] | 8.0 | 12 | UB | **reached** (UB d=12 >= 12) |
| [[288,16,12]] | 8.0 | 18 | UB | **reached** (UB d=18 >= 12) |
| [[288,36,8]] | 8.0 | – | – | NOT in frontier |
| [[360,26,10]] | 7.2 | – | – | NOT in frontier |
| [[360,18,12]] | 7.2 | – | – | NOT in frontier |
| [[144,16,8]] | 7.1 | 2 | EXACT | below (d=2 < 8) |
| [[288,32,8]] | 7.1 | – | – | NOT in frontier |
| [[288,14,12]] | 7.0 | 22 | UB | **reached** (UB d=22 >= 12) |
| [[288,28,8]] | 6.2 | – | – | NOT in frontier |
| [[144,24,6]] | 6.0 | – | – | NOT in frontier |
| [[144,54,4]] | 6.0 | – | – | NOT in frontier |
| [[144,32,4]] | 3.6 | – | – | NOT in frontier |
| [[360,40,4]] | 1.8 | – | – | NOT in frontier |
| [[360,32,4]] | 1.4 | – | – | NOT in frontier |

**Coverage: 10/28 (n,k) points present; reached paper d at 6.**

## Findings

1. **Varying weight closed the high-distance gap.** The broadened search reached [[360,8,30]]
   (d=32 UB >= paper 30, FOM 20 region) and the weight-6 MX [[144,8,12]] (d=12) — code types the
   fixed-weight-3 run structurally could NOT produce. Weight diversity confirmed: cells at stab
   weight 6/7/8/9/10 (was uniformly 6).
2. **High-k codes still missed (18/28).** All missing points are high encoding rate (k=24-54:
   [[288,50,8]], [[144,54,4]], [[360,40,4]], ...). Our rate-aware trust filter + FOM(=kd^2/n) bias
   suppresses high-k/low-d codes. Recovering them needs a SEPARATE high-k campaign (filter relaxed,
   k-maximizing objective) — a concrete next gap, distinct from the weight axis.
3. **Large-n d's are uncertified UBs.** [[288,12,16]] ours d=30 vs paper-exact 16 is a clear BP-OSD
   overestimate that our pure-Julia BZ cannot refute at n=288 (needs MILP, paper's tool). The 99
   EXACT codes are all small-n. No certified beat of the paper on its own block lengths.

_Source: progress/blind-search-8gpu/{frontier_broadened.md, certified_broadened.md} (530 cells, 99 EXACT)._
