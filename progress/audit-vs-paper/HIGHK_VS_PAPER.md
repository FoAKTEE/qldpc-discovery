# High-k campaign vs paper (arXiv:2606.02418) — iter12

OBJECTIVE=k mode: univariate/CRT structural seeding (random params; lem:crt_k family, NOT catalog)
+ rate filter OFF + k-sorted frontier. ISD certifies the TRUE (low) distance, demoting the BP-OSD
garbage these ultra-degenerate codes produce. 249 certified cells, 115 EXACT.

## Result: the k-axis is RECOVERED (was capped at k=20; now k=24..160), at low distance

ISD demotes BP-OSD garbage to the true distance, e.g. [[360,160,156]] (BP-OSD d0=156) -> EXACT d=2.

| our high-k code | status | BP-OSD d0 | note |
|---|---|---|---|
| [[360,160,2]] | EXACT | 156 | pure-univariate => d=2 |
| [[342,152,2]] | EXACT | 146 | pure-univariate => d=2 |
| [[324,144,2]] | EXACT | 142 | pure-univariate => d=2 |
| [[306,136,2]] | EXACT | 130 | pure-univariate => d=2 |
| [[288,128,2]] | EXACT | 126 | pure-univariate => d=2 |
| [[270,120,2]] | EXACT | 114 | pure-univariate => d=2 |

## vs the paper's high-k catalog points (the 18 we previously missed entirely)

| paper code | our nearest (n,k) | our d | verdict |
|---|---|---|---|
| [[144,54,4]] | [[144,?]] | – | no nearby (n,k) |
| [[288,50,8]] | [[288,?]] | – | no nearby (n,k) |
| [[144,24,6]] | [[144,?]] | – | no nearby (n,k) |
| [[360,40,4]] | [[360,40]] | 2 | reach k≈40 but d=2E < paper 4 |
| [[288,24,12]] | [[288,24]] | 6 | reach k≈24 but d=6U < paper 12 |
| [[360,24,12]] | [[360,24]] | 10 | reach k≈24 but d=10U < paper 12 |
| [[144,32,4]] | [[144,32]] | 2 | reach k≈32 but d=2E < paper 4 |

## Findings (honest)

1. **k-axis recovered.** OBJECTIVE=k + univariate seeding produces k=24..160 at n<=360 (FOM-mode
   maxed at k=20 with ZERO cells k>=24). ISD certifies the true distance, demoting BP-OSD garbage
   (d0~156 -> d=2) — the ISD tool (iter11) is essential here.
2. **Pure univariate is d=2.** The simplest CRT family gives high k but trivial distance (d=2);
   only moderate k=24 reaches d=6-10 (UB). The paper's high-k codes (d=4-8, e.g. [[144,54,4]] d=4,
   [[288,50,8]] d=8) use RICHER structure (weight-8 cross-factored polynomials) than pure 3-term
   univariate. So we recover the right (n,k) but at LOWER d than the paper's high-k optima.
3. **Next lever:** higher-weight / factored high-k seeds (weight-4+ univariate variants, shared-
   factor products) to lift the high-k distance from 2 toward the paper's 4-8. Documented, not yet run.

_Source: progress/blind-search-8gpu/{frontier_highk.md, certified_highk.md} (249 cells, 115 EXACT)._
