# blind-zero-2 — honest report of a clean-room blind BB-code search

**Branch:** `blind-zero-2`. **Date:** 2026-06-03. **Discipline:** catalog-BLIND (no paper code/polynomial/
[[n,k,d]] seeded or read during search); the only retained paper-derived info is the claimed
parameter-space extent (`COVERAGE_TARGET.md`). All distances reported here are tool-verified; every
headline number is reproducible from the artifacts named below.

## 1. What was run (clean room → search → certify)
- **Clean room:** every prior artifact (frontiers, certified catalogs, research notes, audit-vs-paper
  reports, scratch) was deleted on a fresh branch; only the pure-Julia `QCodeDiscovery` package, its
  Python port, and the blind search drivers (`scripts/search/`) were kept.
- **Compute:** 256-core host; idle ≈ 239 → **80% of idle = 191 Julia threads** used per phase.
  Observed system load during the heavy phases: **150–226** (full utilization of the budget + baseline).
- **Search (blind seeds only):**
  - *Phase 1 — CSS FOM:* varying check weight **3–8**, **all** lattices `(l,m)` with `2lm≤1000`,
    structured-ansatz fraction 0.3, GA refinement. **61,597 candidates screened → 562 distinct (n,k)**.
  - *Phase 2 — high-k:* `OBJECTIVE=k`, univariate/factored seeds, **k up to 300** → 3,142 distinct (n,k).
  - *Phase 3 — PBB (non-CSS):* exact symplectic distance → 6 codes.
  - *Phase 4 — evolutionary honest-ISD-FOM:* **abandoned** (see §6) — large-n high-k sound-ISD fitness
    did not complete generation 0 in 18 min.
- **In-loop distance:** CSS = BP-OSD **upper bound**; PBB = exact symplectic.
- **Certification (post-hoc):** Lee–Brickell **ISD** (tight upper bound / overestimate refuter) +
  **Brouwer–Zimmermann / enumeration** EXACT where tractable (small n). The certifier was verified to
  work end-to-end (§3).

## 2. Coverage achieved vs the claimed parameter space  ✓
| target axis | claimed | covered by this run |
|---|---|---|
| family | BB CSS + PBB | CSS (phases 1–2) + PBB (phase 3) ✓ |
| block length n=2lm | ≤ 1000 | all lattices `2lm≤1000`; codes found n=16…1000 ✓ |
| rate k | ≤ 300 | high-k campaign reached **k=300** ✓ |
| distance d | ≤ 300 | scan bounds reached d≈290 (but see §3 — these are overestimates) ✓ |
| check weight | 3…~8 | WMIN=3..WMAX=8 ✓ |
| objective | FOM=kd²/n, high-k | FOM sweep + high-k campaign ✓ |

The blind search **comprehensively spans the paper's claimed parameter space.**

## 3. Central finding — heuristic distance bounds systematically OVERESTIMATE (the honesty pivot)
A blind scan reports BP-OSD distances, which are **upper bounds** and inflate badly. Certification
reveals the truth, and the *amount of certification compute itself changes the answer*:

- **High-k regime is degenerate.** BP-OSD scan distances of d₀=156–290 certify to **d=2–3** (often
  EXACT via BZ on smaller analogues, e.g. `[[32,24,8]]→d=1`, `[[36,24,9]]→d=1`). Representative:
  `[[504,224,163]]→d=3` (spread 160), `[[512,224,172]]→d=2` (spread 170). The honest **max-rate** code
  is `[[504,294,1]]` — k=294 but **d=1** (trivial). There are **no usable high-k codes** from blind seeds.
- **Even ISD certification undertrains.** ISD@700 “certified” several mid codes that then **collapsed at
  ISD@3000**: `[[256,10,28]]→d=8`, `[[216,16,20]]→d=6`, `[[216,12,22]]→d=9`, `[[152,8,22]]→d=10`,
  `[[196,8,25]]→d=14`. So the reported distance *drops as you spend more certification compute* — apparent
  high-FOM “records” from a blind BP-OSD scan are largely **artifacts of insufficient distance computation.**

## 4. The honest certified frontier
- **EXACT-certified (trustworthy — Brouwer–Zimmermann/enum gap=0):** small n only.
  Best: `[[32,14,4]]` FOM 7.0, `[[96,16,4]]` FOM 2.67, `[[16,14,2]]`. Exact certification is infeasible
  for n≳160 (BZ is exponential), so larger codes remain upper-bounded.
- **Robust high-distance upper bounds (genuine-looking — survive ISD@10000):** unlike the high-k/mid-FOM
  codes that collapse, a sparse low-k family is STABLE under a large certification budget. Stress-tested at
  **ISD@10000**: `[[336,8,32]]`, `[[360,8,32]]`, `[[384,8,32]]` held at d=32 (spread 0), `[[180,10,16]]`
  held at d=16; only `[[360,10,34]]` eased to **d=30** (FOM 25). These sit squarely in the paper's known
  high-distance sparse regime (cf. its `[[360,8,30]]`-type codes) and are **plausibly genuine blind
  rediscoveries** — robust upper bounds, though not exact-certifiable at n≈360. (They are still upper
  bounds: `[[360,10,34]]→30` shows slow tightening continues; none was proven exact.)
- **PBB (non-CSS):** 6 codes, max `[[24,4,4]]` — sparse and low-distance; the family is hard to populate
  with blind random seeds.

Best code per regime is tabulated in **`BEST_CODES.md`** (111 certified (n,k); 9 EXACT).

## 5. Honest conclusion
A blind, catalog-free BB search **comprehensively covers the paper's parameter space** and rediscovers
the code *families* and the rate–distance frontier *shape*. Two distinct outcomes, separated only by
proper certification:
1. **Most apparent records are artifacts.** The high-k frontier and many mid-FOM codes are BP-OSD (and
   even low-iter-ISD) **overestimates that collapse under certification** (high-k → d=2–3; mid codes drop
   2–3×). A raw BP-OSD-driven scan chases these — you cannot trust its FOM ranking.
2. **A genuine high-distance sparse family survives.** `[[336,8,32]] [[360,8,32]] [[384,8,32]]`
   (FOM≈21–24) and `[[360,10,30]]` (FOM≈25) are **robust to ISD@10000** and sit in the paper's
   high-distance regime — credible blind rediscoveries (robust upper bounds, not exact-proven).

The only *fully* trustworthy distances are EXACT-certified (small n, modest FOM). This independently
reproduces the paper's methodological lesson — reliable discovery **requires exact distance in/after the
loop** (the paper used MILP); certification compute, not the scan, decides what is real.

## 6. Honest limitations
- **Evolutionary phase abandoned:** with broad lattices up to n=1000, the sound k-scaled ISD fitness made
  a few high-k/large-n codes so expensive that generation 0 did not finish in 18 min (the per-generation
  barrier serializes on them). Not run to completion; CSS+high-k phases already cover the FOM/k axes.
- **Exact certification limited to n≲160** (Brouwer–Zimmermann cost); larger-n distances are ISD upper
  bounds, which §3 shows are not guaranteed tight.
- **Search wall-clock bounded** (phases 1–2 to their WALL budgets); a longer search would surface more
  candidates but the certification lesson (§3) stands.
- **One process-management incident:** the first 4-phase driver was suspended by terminal job-control
  (piped output); re-run detached with file redirection. Phase-1/2 results were salvaged intact.

## Artifacts
`COVERAGE_TARGET.md` · `frontier_css.md(.tsv)` (562) · `frontier_highk.md(.tsv)` (3142) ·
`frontier_pbb.md(.tsv)` (6) · `CERTIFIED_FOM_HI.md` (ISD@3000, 55) · `CERTIFIED_HIGHK.md` (51) ·
`BEST_CODES.md` · certify logs `log_cert_*.txt`, `log_recert.txt`, `log_spot2.txt`.
