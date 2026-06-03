# AUDIT — Blind-Zero BB-Code Discovery vs. arXiv:2606.02418 Catalog and SOTA

## Executive summary

Our blind-zero pipeline (`scripts/search/blind_search.jl` + `scripts/search/certify.jl`) rediscovered the single most important shared point in the paper — the gross code **[[144,12,12]]**, FOM 12.0 — entirely **blind**, from uniform-random weight-3 seeds on the (12,6) lattice, with no catalog input. It also covers **[[288,12,16]]** (FOM 10.67, exact lattice + weight + FOM match) and the small-n regime **[[36,4,6]]** / **[[72,8,6]]** (both BZ-exact). Beyond those points, however, coverage is narrow and shallow. We miss the paper's headline records along three structural axes that are baked into our run code: (1) **check weight is hardcoded to 3** (weight-6 stabilizers only), so every weight-7/8/10 record is mathematically unreachable; (2) **seeds are pure uniform-random** with no structured ansatz, GA, or LLM refinement, so the thin XY / mixed-monomial subspaces where the high-distance records live are essentially never sampled; (3) **PBB / non-CSS is never searched**, putting 368 of the paper's 465 distinct codes (79%) out of scope. Where our headline FOMs appear to beat the paper (FOM 20–40), they sit at block lengths n ≫ 360 the paper never explored and are **unverified BP-OSD upper bounds** — none of our 39 exact-certified codes exceeds FOM 6.86 ([[56,6,8]]), and every one of the top-40-by-FOM codes is status UB, with several demoted 6–12 distance points by the post-hoc tightening pass. Net: a few genuine shared low/mid points (notably the blind gross-code rediscovery) plus broad uncertified exploration of larger n; **no certified beat of the paper on its own block lengths**. This document is honest about that gap and proposes blind-safe pipeline changes that broaden reach and strengthen certification **without injecting any catalog code**.

---

## 1. What the paper does

**arXiv:2606.02418** (Cruz-Benito / Cross / Kremer / Faro, IBM Research; PRX Quantum) is an LLM-guided **evolutionary** workflow (OpenEvolve / MAP-Elites, FunSearch/AlphaEvolve lineage). LLMs mutate Python **generator ansatze** `G(l,m) -> {(A,B)}` (or 4-tuples `(A,B,C,D)`) rather than individual codes, so a single mutation expresses an algebraic pattern (e.g. "use `x^(l/3)`") that generalizes across lattices. ~1,650 iterations, ~2×10⁵ candidates screened, ~140h compute, ~$400 LLM inference. **465 distinct codes at n ≤ 360: 97 CSS + 368 non-CSS PBB.**

**Catalog scope.** CSS lattices span n ∈ {144, 288, 360}; PBB lattices span n ∈ {36, 72, 108, 144, 180, 360} (all m ≤ 6). Stage-2 CSS lattice set: (12,6), (6,12), (12,12), (24,6), (15,12), (30,6), (16,9), (18,8). Reported as "N representations → M distinct" (CSS 225→97; per-n 50→16 @144, 98→49 @288, 77→34 @360; PBB 720→368).

**Varying check weight is a primary experimental axis.** Campaigns 1–3 (CSS): trinomials only (weight-3 A,B → weight-6 stabilizers). **Campaign 4 (CSS) explicitly relaxes to 4–6-term polynomials** → weight-8 to weight-12 stabilizers (stab weight = #terms(A)+#terms(B): 3+3=6, 4+4=8, 5+5=10), including mixed monomials x^a y^b (a,b>0). Campaign 5 (PBB): trinomial bases + (C,D) perturbations pushing type-1 mixed X/Z stabilizers to weight 8–10. The paper states "the landscape of code parameters depends on check weight."

**Patterns.** XY (x/y-swap; the *only* weight-6 trinomial family reaching d≥6), MX (mixed-monomial), UV (univariate/HGP, collapses to d∈{2,4}), SD (A=B distance trap, provably d=2), DM (diagonal-mixed), Other.

**Decoders & certification.** In-loop BP-OSD (OSD_0/sp) for ranking; post-hoc 150k-trial three-config protocol (OSD_0/sp, OSD-CS_10/sp, OSD-CS_10/ms — minimum-sum best, finds global min for 64.9% of reps) plus a 1.5M-trial stress test. Campaigns 4–5 add **exact MILP distance in the loop** after discovering BP-OSD overestimated by up to 12×. **EXACT** distance is via MILP (HiGHS/scipy), CSS and symplectic-PBB variants, reported EXACT only when all 2k logicals reach MIP gap=0; otherwise an "≤" incumbent upper bound. Two-level dedup: in-loop coefficient hash + post-campaign **BLISS** colored-Tanner-graph canonical labeling, plus a Tanner **decomposability** check (caught [[288,24,12]] = gross ⊕ gross) and an LC-CSS classifier for PBB.

**SOTA records (selected).** [[288,16,12]] (indecomposable weight-6 d=12, all shifts ≤3, MILP-exact), [[288,50,8]] (weight-8 cross-factored, k=50=4.2× Bravyi), [[144,54,4]] (weight-8 factored, highest k in CSS catalog), [[360,8,30]] (weight-7, FOM 20.0), [[144,8,12]] (weight-6 MX), [[144,12,12]] PBB (FOM 12.0, non-CSS route), [[360,12,≤24]] PBB (FOM 19.2, highest trusted non-CSS), [[360,60,6]] PBB (highest rate). **Important nuance:** no *indecomposable* code in the paper exceeds the prior highest FOM at its own block length — the paper wins on encoding dimension k (3.3–4.5×) and on filling intermediate (k,d) regimes, not on FOM-beating.

---

## 2. What our blind-zero pipeline does

The actual run is `scripts/search/blind_search.jl` (search) + `scripts/search/certify.jl` (post-hoc). Verified against the run code:

- **Family:** BB **CSS only**. Workers pick (l,m) uniformly from `LATS = {l,m ∈ 2..60, 2lm ≤ NMAX(=1000)}`, so n = 2·l·m up to ~990 — far beyond the paper's n ≤ 360.
- **Weight:** **hardcoded `const WEIGHT = 3`**; both A and B are `random_polynomial(l,m,3,rng)` every trial. Weight is never varied, mutated, or swept.
- **Seeds:** **pure uniform-random monomials** (Random.randperm over the full l×m lattice). No structured ansatz (xyswap/univariate/custom), no GA / `mutate_polynomial`, no generations, no LLM. It reimplements its own (n,k)-keyed archive inline rather than using the package's `Archive`/`consider!`.
- **In-loop distance:** BP-OSD only — `bposd_distance(c; trials=32, max_iter=30)`, **multi-config** (product_sum + minimum_sum, both osd_cs order 10), giving a stochastic **upper bound**. A rate-aware d/√n trust cap (1.8 / 1.4 / 1.1 by k/n) is a heuristic screen, not a certificate.
- **Post-hoc certification (`certify.jl`):** high-effort BP-OSD tightening (trials=300) for all, plus **BZ-exact (`min_distance_bz`) only for n ≤ 200**. Pure-Julia Brouwer–Zimmermann, no MILP.
- **Ported-but-unused capability:** `pbb.jl`, `pbb_distance.jl`, `clifford.jl` (LC-CSS), `dedup.jl` (canonical_hash/BLISS), `evolve.jl` (GeneratorAnsatz), `search.jl` (GA `blind_search_css`), `distance.jl` (`css_distance_enum`), `distance_exact.jl` are all exported but **never invoked** by the run.

**Results (`progress/blind-search-8gpu/certified.md`, authoritative):** 418 codes — **39 EXACT, 379 UB**. All 39 EXACT are small (n ≤ 192, d ≤ 8); highest-FOM EXACT is **[[56,6,8]] FOM 6.86**. The entire top-40-by-FOM list is UB.

---

## 3. Coverage: recovered / missed / suspect

### 3.1 Recovered (shared with the paper)

| Paper code | Our match | Notes |
|---|---|---|
| **[[144,12,12]]** FOM 12.0 | [[144,12,12]] **UB**, (12,6), weight-6 | **The blind rediscovery.** Params-match of the paper's headline gross code (class J) from uniform-random weight-3 seeds. Ours is a BP-OSD upper bound (d≤12), *not* MILP-exact like the paper's audited gross code, and is a single CSS rep with no dedup. We did not reach the non-CSS PBB version (we never search PBB). |
| **[[36,4,6]]** FOM 4.0 | [[36,4,6]] **EXACT**, (2,9) | Same (n,k,d) + FOM. Paper's is non-CSS PBB; ours is CSS BB — same parameter point, different family. Ours is BZ-exact. |
| **[[288,12,16]]** FOM 10.7 | [[288,12,16]] **UB**, (12,12), weight-6 | Clean params + lattice + weight + FOM match (10.67). UB (scan d0=28 demoted to 16, consistent with the paper's exact value). |
| **[[72,12,6]]** (n=72 best) | [[72,8,6]] **EXACT**, (3,12) | Partial: we cover the n=72 regime at lower k (k=8 exact), **not** the headline k=12 point. |

### 3.2 Missed (the important gaps)

**Most important miss — [[288,16,12]] (FOM 8, the indecomposable weight-6 record).** A=x³+y+y², B=y³+x+x² at (12,12), all shifts ≤3, MILP-exact. Our best at (288,16) is only **[[288,16,10]]** — two distance points short. Our random scan hit the right (l,m) and weight but never landed the specific structured XY trinomial pair; uniform-random seeding has near-zero probability of drawing it, and with no GA/ansatz/hill-climbing we cannot climb to it.

Other notable misses, by cause:

- **Weight policy (weight-3 pin) rules these out entirely:** [[360,8,30]] (FOM 20, weight-7), [[288,50,8]] (FOM 11.1, weight-8 cross-factored, k=50), [[144,54,4]] (k=54, weight-8 factored), [[360,20,14]] (FOM 10.9, weight-8). All of Campaign 4's higher-weight regime.
- **Structured-pattern misses within weight-6:** [[288,24,12]] (FOM 12; note the paper flags it **decomposable** = gross ⊕ gross), [[360,12,24]] (FOM 19.2 XY — we hit the right (n,k) but only **[[360,12,16]]**, an 8-point distance gap), [[144,8,12]] (FOM 8, weight-6 MX — we found [[144,12,12]] and [[144,16,14]] at (12,6) but not this MX point).
- **PBB family (never searched):** [[360,12,24]] PBB (FOM 19.2, highest trusted non-CSS), [[360,60,6]] (highest rate), [[180,6,≤21]] PBB (FOM 14.7), [[108,8,10]] PBB (FOM 7.4 — we *do* cover (108,8) with a better CSS [[108,8,12]], but not the PBB construction). All 368 PBB codes are structurally out of scope.

### 3.3 "Better"-looking and suspect overestimates (be skeptical)

Our top FOMs (20–40) are **all UB and all at n ≫ 360** — block lengths the paper never searched, so these are *coverage of larger n*, not head-to-head FOM beats:

- [[840,16,46]] FOM 40.30, [[336,20,26]] FOM 40.24, [[600,16,38]] FOM 38.51, [[780,16,42]] FOM 36.18 — all UB; n far beyond any BZ certification (BZ runs only n ≤ 200).
- [[144,16,14]] FOM 21.78 (UB, d0=16→14): a weight-6 [[144,16,14]] would *beat* the literature (cf. Symons [[144,14,14]] FOM 19.1, weight-8) — a red flag that the BP-OSD bound is optimistic. Demands MILP before being believed.
- **Large scan demotions** signal still-loose UBs: [[336,20,26]] (d0=32→26), [[528,16,28]] (40→28, 12-pt drop), [[896,12,40]] (52→40, 12-pt drop), [[780,16,42]] (50→42), [[288,8,22]] (30→22 — our "best" at 288, suspect for a block length the paper certified exactly to d≤20).

**General caveat:** the entire FOM 20–40 frontier rests on unverified BP-OSD upper bounds. The highest-FOM EXACT code is [[56,6,8]] (FOM 6.86). Under exact distance, true FOMs may drop and parts of the "frontier" may evaporate.

---

## 4. Methodology gaps (ranked)

| # | Capability | Paper has | We have | Severity | Impact |
|---|---|---|---|---|---|
| a | **Check-weight as an axis** | Weight varied per campaign; C4 relaxes to 4–6-term polys (wt 8–12) | `const WEIGHT=3` hardcoded for A and B | **Critical** | Locks us out of the entire weight-7/8/10 half of the catalog: [[360,8,30]], [[288,50,8]], [[144,54,4]], [[360,20,14]]. k=50–54 codes mathematically unreachable. |
| b | **Structured / algebraic seeds** | LLM-mutated ansatze encoding XY swap, UV, MX, factored products | Pure uniform-random monomials; no ansatz | **Critical** | High-d trinomials live in the thin XY (small-shift) subspace; random draws almost never land them (e.g. [[288,16,12]] needs all shifts ≤3). Likely *the* reason our n=144/288/360 results are modest. |
| c | **Evolutionary / LLM refinement** | 5 campaigns of LLM-guided evolution + a GA baseline | Single-shot random restart; generations=0, no mutate | **High** | No way to concentrate sampling or climb a lucky seed to the exact optimum (e.g. tuning shifts down). Forfeits the compounding that turns a near-hit into a record. |
| d | **PBB / non-CSS family** | Entire Campaign 5; 368 codes | `pbb.jl`/`pbb_distance.jl` ported but never invoked | **High** | 79% of the paper's distinct codes out of scope, incl. highest raw FOM ([[360,10,≤40]] 44.4) and [[144,12,12]] PBB. Missing **family**, not just a code. |
| e | **In-loop equivalence dedup / decomposability** | Coefficient hash + BLISS + Tanner decomposability + LC-CSS | None called (`dedup.jl` exported, unused) | **Medium** | Doesn't block discovery but undermines claim validity: a high-FOM find could be a trivial direct sum (as [[288,24,12]] was). Our "418 codes" is reps, not distinct, so not comparable to the paper's "465 distinct." |
| f | **Tight in-loop distance / multi-decoder** | 150k-trial multi-config + in-loop MILP (C4–5) | BP-OSD trials=32, max_iter=30; no in-loop exact | **High** | 32 trials is far below the paper's in-loop effort → loose UB; mis-ranks candidates and the trust cap can discard true high-d codes. (It *is* multi-config product_sum+minimum_sum, so less severe than a single-config gap.) |
| g | **Deep enumeration at fixed n** | Compute concentrated on {144,288,360} (50/98/77 reps) | Uniform lattice sampling up to n~990; ~3–7 codes each at 144/288/360 | **High** | Effort diluted across n the paper never claimed and where we cannot certify. The few samples at target sizes explain the modest, uncertified n=144/288/360 entries. |
| h | **Exact MILP/BZ certification** | MILP exact for CSS + symplectic PBB | BP-OSD UB only in-loop; BZ-exact only n ≤ 200 | **High** | Headline FOMs rest entirely on unverified UBs; documented 6–12-pt demotions show they're still loose. We cannot reproduce even [[144,12,12]]/[[288,16,12]] as EXACT — only as UBs. |

**Prioritized narrative.** (1) Weight-3 pin (a) is the single hardest structural blocker — fix first. (2) Unstructured random seeds (b) are the most likely reason our target-size results are modest. (3) These pair with the absence of any refinement (c): structure puts us in the right neighborhood, refinement climbs to the point. (4) Three reinforcing search-design gaps — broad-but-shallow n-scan (g), loose in-loop distance (f), thin certification (h) — mean even codes we *do* find at target sizes are reported as loose UBs. (5) PBB (d) is an entire unsearched family. (6) Dedup/decomposability (e) is validity, not discovery.

---

## 5. Pipeline changes (priority order)

All changes are gated behind environment flags defaulting to **current behavior**, so the existing run is reproduced exactly unless explicitly opted in.

### 5.1 Julia — `/data/haiyangw/claude/qldpc-discovery/scripts/search/blind_search.jl`

1. **GA / local-search refinement of elites** (`GENS`, default 0 = no change). After the timed random scan, snapshot top-N elites, mutate their stored (A,B) term lists with `mutate_polynomial(...)` (weight-preserving exponent perturbation), re-screen k, re-bound distance, and `consider` against the (n,k) cell for `GENS` rounds. *Blind-safe:* mutation injects no catalog knowledge. **Highest-impact reach improvement** (addresses gap c, pairs with b).

2. **Varying check-weight sampling** (`WMIN`/`WMAX`, default 3,3 = no change). Per trial draw `wA, wB ∈ WMIN:WMAX`, call `random_polynomial(l,m,wA,rng)` / `(...,wB,...)`; record realized `stabilizer_weight(c)` and add a `wt` column to frontier output. *Blind-safe:* `random_polynomial` already takes an arbitrary weight; only the driver pins it. (Addresses gap a.)

3. **Wire PBB non-CSS into the search** (`MODE`, default `css`; values css|pbb|both). For `:pbb`, draw weight-3 A,B + small perturbations C,D (weights from {0,1,2,3}, so C=D=0 reduces to CSS), wrap `PBBCode(l,m,A,B,C,D)` in try/catch (most random 4-tuples are non-commuting and throw), screen `pbb_k`, bound distance with `symplectic_distance` gated to small n (`PBB_EXACT_NMAX`, default 216) else k-only. Store a `noncss` flag + columns C,D. *Blind-safe:* C,D drawn uniformly (generic, **not** the paper's |C|=|D|=2 optimum); mirrors the existing Python `random_commuting_pbb`. (Addresses gap d.)

4. **In-loop canonical_hash equivalence dedup** (`DEDUP`, default 0 = off). Track canonical hashes of elites; report `n_distinct` alongside the rep count. *Blind-safe:* pure structural canonicalization. Opt-in because canonical_hash is O(IR-tree). (Addresses gap e.)

5. **Generic GeneratorAnsatz structured-pattern seeding** (`ANSATZ`, default 0 = off). A fraction of workers draw from `random_ansatz(rng)` + `mutate_ansatz` and emit (A,B) via `generate(ansatz,l,m)`. Strategies (xyswap/univariate/custom) use only **parametric** exponents (a..f drawn 1:6; j scaled as p·l//q; safe arithmetic over {l,m,ints}). *Blind-safe:* encodes structural priors (x/y-swap is the only weight-6 family reaching d≥6) **with random parameters, not the catalog's polynomials**. (Addresses gap b.)

6. **Deep-enumeration mode at fixed (l,m)** (`FIXLM`, default empty). Exhaustively/semi-exhaustively enumerate weight-w (A,B) pairs on a single lattice, sharded by a deterministic monomial-pair index stride, deduped by canonical_hash. *Blind-safe:* lexicographic enumeration order injects no catalog knowledge; pairs with the DEDUP change. (Addresses gap g.)

### 5.2 Julia — `/data/haiyangw/claude/qldpc-discovery/scripts/search/certify.jl`

7. **Enumeration-based exact certification + raised threshold** (`ENUM_NMAX` default 360, `ENUM_MAXW` default 8). For codes with `d0 ≤ ENUM_MAXW` and `n ≤ ENUM_NMAX`, run `css_distance_enum`; if exhausted, mark **EXACT**. Also parameterize `BZ_NMAX` (raise default 200 → e.g. 288 where feasible). *Blind-safe:* first-principles enumeration, no catalog. Closes the suspicious low-distance demoted codes honestly. (Addresses gap h.)

8. **Multi-seed high-effort BP-OSD + spread reporting**. Replace the single-seed `bposd_distance` with a loop over `SEEDS` (default 3), take the min d_bound, record `d_X`/`d_Z` and a `spread` = (initial d0) − (tightened d) column so demotion magnitude is machine-readable (large spread ⇒ still-suspect UB). *Blind-safe:* more decoder effort, no catalog lookup. (Addresses gap f.)

### 5.3 Python — `/data/haiyangw/claude/qldpc-discovery/python/src/discovery/search.py`

9. **Check-weight variation parity** in `blind_search_css`: add `weights=None`; when a sequence is passed draw `wA,wB` per seed and record `stab_weight`. Default unchanged. *Blind-safe:* mirrors Julia change a.

10. **In-loop dedup distinct count parity** in `blind_search_css`/`blind_search_pbb`: add `dedup=False`; when True track canonical hashes among elites and report `n_distinct`. *Blind-safe:* mirrors Julia change e; no catalog.

### 5.4 Scripts

None required — all wiring lives in `blind_search.jl` / `certify.jl`.

**Recommended order:** GENS → WMIN/WMAX → ENUM_NMAX cert → MODE=pbb → multi-seed BP-OSD+spread → DEDUP → ANSATZ → FIXLM, then the two Python parity changes.

---

## 6. Blind-discipline guardrails

Every change above **broadens reach or strengthens certification — none injects the catalog.** Concretely:

- **No paper polynomial is ever written into the search.** Weight sampling (WMIN/WMAX), GA mutation, ansatz seeding, and PBB perturbation all draw **random parameters**. The ansatz strategies encode *structural priors* the paper found productive (x/y-swap, univariate, factored forms) but with randomly-drawn exponents — they do **not** emit the catalog's specific (A,B) pairs. PBB C,D are drawn generically (any weight 0–3), explicitly **not** the paper's |C|=|D|=2 optimum.
- **Certification changes add proof, not knowledge.** Enumeration and Brouwer–Zimmermann are first-principles exact-distance algorithms; multi-seed BP-OSD is just more decoder effort. None consults the catalog.
- **Dedup/decomposability are structural truth-telling**, making our counts comparable to the paper's distinct framing and flagging trivial direct sums — again, no catalog input.
- **All flags default to current behavior**, so the existing blind run is bit-for-bit reproducible; opt-in only.

**Honesty statement.** Our high-FOM large-n codes (FOM 20–40 at n=336–990) are **BP-OSD upper bounds, not MILP-exact**, several demoted 6–12 distance points by tightening, at block lengths the paper never searched and our BZ cannot certify (n ≤ 200). We do **not** beat the paper on its own block lengths in any certified sense. Our one solid claim is the **blind rediscovery of the gross [[144,12,12]] (FOM 12.0)** from uniform-random weight-3 seeds — and even that is reported as a BP-OSD upper bound, not the paper's MILP-exact certificate. The changes above are the minimum needed to begin closing that gap while preserving blind discipline.

---

## Top blind-safe changes (workflow-ranked)

1. Add GENS-gated GA/local-search refinement of top elites in blind_search.jl (mutate_polynomial on discovered cells; default off)
2. Add WMIN/WMAX per-trial check-weight sampling in blind_search.jl to reach weight-7/8/10 (default 3,3 = unchanged)
3. Add enumeration-based exact certification (ENUM_NMAX/ENUM_MAXW) + raised BZ_NMAX in certify.jl to certify low-distance codes at larger n
4. Wire PBB non-CSS 4-tuple (A,B,C,D) search into blind_search.jl behind MODE=pbb with generic random C,D
5. Replace single-seed certify.jl BP-OSD with multi-seed minimization plus a spread column flagging still-loose UBs
6. Add ANSATZ-gated generic GeneratorAnsatz structured seeding (xyswap/univariate/factored) with random parameters
7. Add DEDUP-gated canonical_hash equivalence dedup reporting n_distinct in blind_search.jl
8. Add FIXLM deep-enumeration mode to saturate target lattices (12,6)/(12,12)/(30,6) instead of diluting effort to n~990

_Generated by the `audit-vs-paper` multi-agent workflow (10 agents); coverage + methodology + pipeline-change analysis cross-referenced against arXiv:2606.02418 catalog tables and our certified frontier._
