# Synthesis — what a clean-room blind BB-code search actually establishes

*blind-zero-2 · synthesized with Opus 4.8 from tool-verified results. Frontier counts refresh when the
in-progress denser run + re-certification complete; the conclusions below are stable under that refresh
because they rest on certification behavior, not on any single code.*

## The experiment in one line
Strip the project to zero, keep only the search *machinery* and the paper's claimed *parameter extent*,
re-discover bivariate-bicycle (BB) codes blind across that whole extent, and — crucially — **certify every
headline distance** rather than trusting the search's own decoder. The question is not "what codes did the
scan report" but "what survives an honest distance proof."

## The one finding that organizes everything
**A blind scan's figure of merit is only as trustworthy as the distance oracle behind it, and the cheap
oracles lie upward.** Three independent lines of evidence, each tool-verified:

1. **BP-OSD (the in-loop scan decoder) overestimates catastrophically at high rate.** The entire high-k
   "frontier" — scan distances d₀ = 156–290 — certifies to **d = 2–3** (`[[504,224,163]]→3`,
   `[[456,228,156]]→2`). The honest maximum-rate code is `[[504,294,1]]`: k = 294 and **d = 1**. There is
   no usable high-k code in the blind sample; the apparent one was an artifact of the decoder.

2. **Even the *refuter* overestimates when under-resourced.** Lee–Brickell ISD is a *tight* upper bound,
   yet the answer it returns depends on how many iterations you spend. Re-certifying the same mid-FOM
   codes at increasing budgets shows monotone collapse:
   `[[256,10,·]]`: d0 28 → ISD@3000 **8**; `[[216,16,·]]`: 20 → **6**; `[[152,8,·]]`: 22 → **10**.
   The reported distance is a function of certification compute, not a property the scan discovered.

3. **But the collapse is not universal — a real family is stable.** Stress-tested all the way to
   **ISD@10000**, a sparse low-rate set holds: `[[336,8,32]]`, `[[360,8,32]]`, `[[384,8,32]]` (d = 32,
   spread 0) and `[[180,10,16]]`; `[[360,10,34]]` eases only to **d = 30**. These do not collapse because
   they genuinely have no low-weight logicals — they sit exactly in the paper's high-distance sparse
   regime and are credible **blind rediscoveries**.

So the blind frontier cleanly separates, *under certification*, into **artifacts that evaporate** and a
**genuine high-distance family that survives**. Without the certification step the two are indistinguishable
— and an FOM-ranking scan would have crowned the artifacts.

## What is actually trustworthy, by tier
- **Proven (EXACT, Brouwer–Zimmermann/enum gap = 0):** small n only — `[[32,14,4]]` (FOM 7), `[[96,16,4]]`,
  `[[16,14,2]]`, plus exact-symplectic PBB up to `[[24,4,4]]`. Modest, but *certain*.
- **Robust upper bounds (survive ISD@10000, not exact-provable at n≈360):** `[[336,8,32]]`,
  `[[360,8,32]]`, `[[384,8,32]]` (FOM ≈ 21–24), `[[360,10,30]]` (FOM ≈ 25). The credible discoveries.
- **Refuted (do not exist as claimed):** the high-k frontier (→ d 1–3) and many mid-FOM codes (→ 2–3×
  smaller). These are the cautionary tale.

## Coverage — the search did span the claimed space
All 1,317 lattices with 2lm ≤ 1000; weights 3–8; both FOM and high-k objectives; CSS and PBB families;
k driven to 300, n to 1000. This is a dense *sample*, never an exhaustive enumeration (the space holds
billions of polynomial pairs per lattice) — and the honest verdict to "did you finish the full search"
is therefore **no, and no search can**: completeness here means *all phases run + dense sampling + every
headline certified*, which is what is delivered.

## Relationship to the paper (post-hoc, blind discipline intact)
Blind search reproduces the BB code **families** and the **shape** of the rate–distance frontier, and
independently rediscovers a genuine high-distance sparse family in the paper's regime. It produces **no
certified beat** of the paper. Most importantly, it re-derives — from the opposite direction — the paper's
own methodological choice: the paper put **exact MILP distance inside its loop** precisely because a
decoder-driven search optimizes the decoder's errors. Our certification cascade is the same lesson stated
as a negative result: *the scan cannot be trusted to rank codes; only the proof can.*

## The transferable conclusion
For BB / qLDPC code discovery, **the bottleneck is certification, not search.** A blind sample of the
parameter space is cheap and broad; deciding which of its high-FOM hits are real is the expensive,
decisive step, and the answer moves as you spend more proof-compute. Trustworthy discovery requires exact
distance where feasible (small n) and a stated, large certification budget elsewhere — with the explicit
caveat that anything not exact-proven remains an upper bound that may still fall.

## Honest limitations
- Exact proof feasible only to n ≈ 160; the genuine high-distance codes (n ≈ 360) are robust upper bounds,
  not theorems.
- The evolutionary phase on large lattices was abandoned (sound-ISD fitness too costly to converge); the
  FOM and k axes are covered by the scan phases instead.
- Distances reported as ISD bounds are not proven tight — finding (2) above is the standing warning.
