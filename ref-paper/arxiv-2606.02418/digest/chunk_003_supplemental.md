# Chunk 003 — Supplemental Material digest (pipeline-0 source import)

Source: `arxiv-2606.02418/src/supplemental.tex` (715 lines) + included catalog files
`css_catalog_tables.tex` (292 lines), `pbb_catalog_tables.tex` (480 lines).
Paper: arXiv:2606.02418 "Evolutionary Discovery of Bivariate Bicycle Codes with LLM-Guided Search"
(Cruz-Benito, Cross, Kremer, Faro; IBM Research; PRX Quantum).

DISCIPLINE: every entry below is TYPED `(context, claim, evidence modality, dependencies, status marker)`.
Default modality `LiteratureGrounded` (this is source import; the SM reports results, it does not re-derive
them here). Cited-but-not-reproduced external results carry `[AXIOM]`. tex labels preserved VERBATIM.
Symbols are declared in chunk_001/002 (`R`, `H_X`, `H_Z`, `A,B,C,D`, `k`, `d`, `n`, `FOM`); reused here without re-declaration.

---

## SM-MILP-1 — CSS distance MILP (verbatim formulation)

- **context**: SM Sec. `sm:milp`, subsec "CSS distance formulation", supplemental.tex l.659--674.
  Following Bravyi et al. `bravyi2024high` = arXiv:2308.07915 (the MILP baseline this work extends).
- **claim**: minimum-weight X-type logical for the $j$-th logical qubit is the integer program
  (eq labels VERBATIM):

```
min       sum_{i=1}^{n} x_i                         (eq:milp_obj)
s.t.      H_Z x  ≡ 0  (mod 2)                        (eq:milp_commute)
          <x, Zbar_j> ≡ 1  (mod 2)                   (eq:milp_anticommute)
          x_i ∈ {0,1},  i = 1,...,n                  (eq:milp_binary)
```

  where `Zbar_j` is the $j$-th independent $Z$-logical operator.
  Mod-2 linearization (l.669): each row $\sum_i a_i x_i \equiv b \pmod 2$ becomes
  $\sum_i a_i x_i - 2 s = b$ with integer slack $s \in \mathbb{Z}_{\ge 0}$.
  $Z$-type distance computed by swapping $H_X \leftrightarrow H_Z$; code distance $d = \min(d_X, d_Z)$ (l.670).
- **evidence modality**: `SymbolicDerivation` (the integer program is the exact, stated definition of the
  distance computed; not a heuristic). Solver outcome is `ExactProof` only when MIP gap = 0 (see SM-MILP-3).
- **dependencies**: `bravyi2024high` `[AXIOM]` (MILP baseline / BB definition); HiGHS via `scipy.optimize.milp`.
- **assumptions**: BB CSS code so $d_X = d_Z$ (l.674): the polynomial involution $x\mapsto x^{-1}, y\mapsto y^{-1}$
  exchanges $H_X$ and $H_Z$; both computed as a consistency check.
- **status**: `[SOLID]`. This is the load-bearing exact-distance definition for all CSS rows in the catalog.

## SM-MILP-2 — non-CSS symplectic distance MILP (verbatim formulation)

- **context**: SM Sec. `sm:milp`, subsec "Non-CSS symplectic formulation", supplemental.tex l.676--691.
- **claim**: a Pauli on $n$ qubits has symplectic rep $(\mathbf a \mid \mathbf b) \in \mathbb F_2^{2n}$
  (X-first convention: $a_i$ = X-content, $b_i$ = Z-content on qubit $i$, l.690). Symplectic weight of
  $P = X^{\mathbf a} Z^{\mathbf b}$ is $|\{i : a_i \neq 0 \text{ or } b_i \neq 0\}|$ (l.680). MILP:

```
min       sum_{i=1}^{n} w_i
s.t.      H · (a | b)^T ≡ 0  (mod 2)
          <(a | b), Lbar_j>_symp ≡ 1  (mod 2)
          w_i ≥ a_i,  w_i ≥ b_i,  w_i ≤ a_i + b_i
          a_i, b_i, w_i ∈ {0,1}
```

  (NOTE: these four `align` lines carry NO `\label` in source — the eq:milp_* labels belong to the CSS block only.)
  $w_i = a_i \lor b_i$ enforced by the standard binary-OR linear encoding (convex hull of the four feasible
  $(a_i,b_i,w_i)\in\{0,1\}^3$ triples; tight at integer points) (l.689).
  $H \in \mathbb F_2^{m\times 2n}$ is the **symplectic-flipped** stabilizer matrix: each stabilizer
  $(s_X \mid s_Z)$ is stored in row order $(s_Z \mid s_X)$ so that $H\cdot(\mathbf a\mid\mathbf b)^T$ computes
  the column of symplectic inner products and $\equiv 0$ enforces pairwise commutation (l.689).
  Row-flip justification (l.690): symplectic inner product of $(s_X\mid s_Z)$ with $(\mathbf a\mid\mathbf b)$
  is $s_X\!\cdot\mathbf b + s_Z\!\cdot\mathbf a$ = ordinary dot product of flipped row $(s_Z\mid s_X)$ with $(\mathbf a\mid\mathbf b)$.
  `Lbar_j` from `qldpc` symplectic Gaussian elimination.
- **evidence modality**: `SymbolicDerivation`.
- **dependencies**: SM-MILP-1; PBB commute condition `pbb-commute` (chunk_002): for PBB this commutativity
  reduces to "$A C^\top + B D^\top$ symmetric over $\mathbb F_2$" (l.690, main text Sec. III B, `evaluation/pbb_code.py`).
- **assumptions**: X-first symplectic convention (Z-first references flip the row ordering, l.690).
- **cost note**: $3n$ binary vars ($a_i,b_i,w_i$) vs $n$ for the CSS X-distance MILP; ~4x longer per-logical
  solve time on matched codes (l.691). Constrains lattice selection for Campaign 5 (see SM-CAMP-5).
- **status**: `[SOLID]`.

## SM-MILP-3 — exactness / optimality gate and audit

- **context**: supplemental.tex l.672--673, 693--711 (subsec "Validation and optimality audits").
- **claim**: a solution is *exact* iff HiGHS reports MIP gap = 0 (proven optimal); otherwise the incumbent
  is a valid UPPER bound (l.673). MILP solves in seconds for low-$d$, minutes for $d=12$ (l.696).
  Validated on Bravyi baselines $\llbracket 72,12,6\rrbracket$ and $\llbracket 144,12,12\rrbracket$ — both
  confirmed exactly (MIP gap = 0 for every logical) (l.695).
  Headline audit (300 s/logical timeouts, l.701--707):
  | Code | logicals | total | result |
  |---|---|---|---|
  | $\llbracket144,12,12\rrbracket$ gross | 24 | 13 min | proven optimal, all |
  | $\llbracket288,24,12\rrbracket$ | 48 | 29 min | proven optimal, all |
  | $\llbracket288,16,12\rrbracket$ | 32 | 80 min | proven optimal, all |
  | $\llbracket360,16,{\le}14\rrbracket$ | 32 | — | wt-14 found for all; optimality proven for 7; remaining 25 incumbents at wt 14 or 16 → $d\le14$ established (l.705--706) |
  - $d=2$ codes (incl. all $A=B$): weight-2 feasible in <1 s; combined with $d\ge2$ from trinomial column-weight
    structure ⇒ $d=2$ exactly (l.698). $d\le4$ univariate: proven optimal within seconds (l.699).
  - Campaign 4: all 1188 fitness-passing codes MILP-verified (120--600 s/logical); top 39 re-verified
    (3000 s/logical, 72000 s total) (l.709--710).
  - Campaign 5: 149 PBB catalog entries deep-verified (timeouts up to 14400 s/logical, up to 60-worker pool
    on 64-core server) → 63 exact outcomes, 33 downward distance corrections (l.711).
- **evidence modality**: `ExactProof` for MIP-gap-0 rows; `LiteratureGrounded` upper bound for incumbent rows.
- **dependencies**: SM-MILP-1, SM-MILP-2.
- **status**: `[SOLID]`. The `[AXIOM]` here is `bravyi2024high` (baseline correctness) only.

---

## SM-CAMP — Campaign configuration table (C1--C5)

- **context**: SM Sec. `sm:campaigns`, supplemental.tex l.552--585 (+ main text Table I, cross-referenced).
- **claim** (one TYPED row per campaign; numbers VERBATIM from l.554--585):

| C | model | iters | pop / islands | LLM $ | wall-clock | catalog yield | verification highlight |
|---|---|---|---|---|---|---|---|
| C1 | Gemini 3 Flash Preview | 100 | 100 / 3 islands | ~$15 | 5 h | 9 codes full-verified | best score 327.0 @ iter 83, gen-depth 5; seed 4 strat/230 lines → 7 strat/292 lines (added univariate); 79/100 niches occupied |
| C2 | 3-model ensemble | 251 (early-stopped) | 100 | ~$25 | 9.5 h | 0 net new (seed incl. 5 C1 codes) | best score 348.6 (+6.6% vs C1); largest gain +39.3 @ iter 3; $\Sigma_k = 464$ (BELOW C1's 704) |
| C3 | 3-model ensemble | 500 | 1000 / 5 islands | ~$50 | 21 h | 145 unique codes not in C1 | best score 354.4 @ iter 462; saturates after ~225 iters (last ~275 iters: one +1.2% improvement) |
| C4 | Ansatz (mixed-monomial) | 300 | 750 (per ground truth) | ~$47 | 92 h | 45 distinct, structural families not in `bravyi2024high`; wt-8 | 24 parallel workers / 64-core; all 1188 fitness-passers MILP-verified; top 39 ext-budget; top 6 → 300k-trial BP-OSD; rediscovered gross code via 6 mixed-monomial reps; only 1 poly-pair overlap with C1--3 ($\llbracket288,24,12\rrbracket$ @ (12,12)) |
| C5 | PBB (4-tuples) | 500 (352 productive) | 200 | ~$100 | 11 h | 368 BLISS-unique non-CSS PBB | 18588 candidate 4-tuples across 7 lattices; 149 deep-verified MILP (timeouts ≤14400 s, ≤60-worker); 63 exact, 33 downward corrections; lattice set restricted to $m\le6$ because symplectic MILP ~4x slower (excludes CSS lattices (12,12),(15,12)) |

  Cost reconciliation (l.581--585): 5 campaigns sum to **~$237** LLM inference over **~140 h**
  wall-clock (Table I rows $5+9.5+21+92+11 = 138.5$ h); C4's 92 h itself absorbs ~20 h (72000 s) top-code
  re-verification. Headline **~$400** (abstract) = $237 + ablation arms (~$70: random $10^3$/$10^4$/lattice + GA/GA-G ×5 seeds) + exploratory/failed runs (~$90). The 149-entry C5 deep MILP audit is reported ON TOP of the ~140 h (separate machine).
  **MILP verification — not LLM inference — is the dominant compute cost** (l.585).
- **evidence modality**: `EmpiricalMeasurement` (campaign telemetry: scores, iteration counts, $).
- **dependencies**: `openevolve` MAP-Elites; `litellm` proxy; SM-MILP-1/2/3.
- **status**: `[SOLID]`.
- **cross-campaign finding** (l.610--617): C2 (ensemble, pop=100) $\Sigma_k=464 < $ C1's 704 despite more
  iters + model diversity → small-population ensemble mutation may be less focused. Only C3 (pop=1000,
  500 iters) matched C1's $\Sigma_k$. "Most parsimonious explanation: population size and iteration count are
  the primary drivers" — ensemble contribution NOT isolated.
  **[HOLE]** expected claim: controlled single-variable (model-config-only) experiment to isolate the
  ensemble contribution. expected evidence: `StatisticalInference` over matched-config runs. Author-stated
  as needed (l.617); not run. `[FUTURE]` (does not block this chunk).

---

## SM-CAT-CSS — CSS catalog structure (css_catalog_tables.tex)

- **context**: SM Sec. `sm:css_catalog`, supplemental.tex l.47--67; tables in css_catalog_tables.tex.
- **claim**: 3 longtables `tab:cat144`, `tab:cat288`, `tab:cat360` (labels VERBATIM). 225 CSS polynomial
  representations total → 97 distinct codes after BLISS Tanner-graph dedup (`junttila2007engineering`).
  Per-table dedup: $n=144$ 50→16; $n=288$ 98→49; $n=360$ 77→34 (99 total; the 97 "distinct codes" excludes
  2 Bravyi codes for which C4 found extra reps) (l.52).
  **Row schema** (12 columns, css_catalog_tables.tex l.16--18, identical across all 3 tables):
  `Cl. | (ℓ,m) | A(x,y) | B(x,y) | k | d | FOM | d_{OSD_0} | d_{CS/sp} | d_{CS/ms} | Pat. | Camp.`
  - `Cl.` = BLISS equivalence class label; rows sharing a label are different poly reps of the SAME code.
    cat360 uses primed labels ($'$) to denote Campaign 4 classes.
  - `d`, `FOM` use MILP exact distances (incumbent upper bounds for some C4 codes; for cat360 classes
    U,V the MILP incumbent exceeded the 300k-trial BP-OSD bound so `d` reports the tighter BP-OSD value, l.198).
  - 3 decoder columns = 150k-trial BP-OSD upper bounds; **bold** = matched $d_\text{MILP}$ (l.54).
    Decoders: $\text{OSD}_0$/sp, CS$_{10}$/sp, CS$_{10}$/ms (product-sum vs minimum-sum BP).
  - `Pat.` abbreviations (l.57): UV = univariate; XY = $x/y$-swap; SD = $A=B$ (identical polys; NOT
    $C\subseteq C^\perp$ self-duality); MX = mixed-monomial; DM = diagonal-mixed $1+x^ay^a+x^by^b$; O/Other.
  - `Camp.` (l.58): F = C1 (Flash), E = C2--3 (Ensemble), A = C4 (Ansatz); "E,A"/"F,A" = independent
    rediscovery by both.
  - **Check weight** (l.60--63): F/E produce trinomials only → weight-6 stabilizers; A codes have stabilizer
    weight = (#terms in $A$) + (#terms in $B$) (3+3=wt6, 4+4=wt8, 5+5=wt10). Term count visible in poly columns.
- **evidence modality**: `LiteratureGrounded` (catalog is reported data).
- **dependencies**: SM-MILP-1/3 (distances); BLISS dedup (chunk on Sec VI.A); `tillich2014quantum` `[AXIOM]` (UV distances).
- **status**: `[SOLID]`.
- **CSS catalog landmark rows** (verbatim from css_catalog_tables.tex; spot-check ledger, not exhaustive):
  - cat144 prior record: $\llbracket144,12,12\rrbracket$ FOM 12.0 `bravyi2024high`. Class J reaches FOM 12.0
    (multiple A-campaign reps, XY+MX, l.20--25). Class O: $\llbracket144,54,4\rrbracket$ FOM 6.0 (k=54,
    DM/MX, A) l.66--68 — highest-$k$ CSS. SD class G: $\llbracket144,32,2\rrbracket$ FOM 0.9 ($A=B$) l.44.
  - cat288 prior record: $\llbracket288,12,18\rrbracket$ FOM 13.5 `bravyi2024high`. Class A:
    $\llbracket288,24,12\rrbracket$ FOM 12.0 (decomposable = 2 gross codes), at (12,12) E,A and (24,6) F,A
    l.91--92. Class B: $\llbracket288,16,12\rrbracket$ FOM 8.0 (E) l.105 — highest-$k$ indecomposable wt6 @ d12.
    Class X: $\llbracket288,50,8\rrbracket$ FOM 11.1 (k=50, MX, A, (18,8)) l.93--94.
  - cat360 prior record: $\llbracket360,12,{\le}24\rrbracket$ FOM ≤19.2 `bravyi2024high` (class V is C4
    rediscovery, same poly pair, l.203). Class U$^\dagger$: $\llbracket360,8,30\rrbracket$ FOM 20.0
    (UNTRUSTED $d/\sqrt n>1.2$, l.201,211). $\llbracket360,16,{\le}14\rrbracket$ class A,
    $\llbracket360,20,{\le}14\rrbracket$ (the wt-8 C4 code in threshold tables) appear at FOM 8.7 (l.216--219).
    UV families: $1+y+y^2 / 1+x^5+x^{10}$ etc give $k=40$, $d\in\{2,4\}$ (classes H,O,P,Q,R,S,T).

## SM-CAT-PBB — non-CSS PBB catalog structure (pbb_catalog_tables.tex)

- **context**: SM Sec. `sm:pbb_catalog`, supplemental.tex l.70--78; tables in pbb_catalog_tables.tex.
- **claim**: 368 BLISS-unique non-CSS PBB codes from Campaign 5, sorted by FOM descending within each block
  length. Each code = 4-tuple $(A,B,C,D)\in R$; $C=D=0$ ⇒ reduces to CSS BB code (l.74).
  **7 lattices / 7 table labels** (VERBATIM; counts are #codes = #distinct, all BLISS-unique):
  | label | n | (ℓ,m) | #codes |
  |---|---|---|---|
  | `tab:pbb_cat36` | 36 | (3,6),(6,3) | 47 |
  | `tab:pbb_cat72` | 72 | (6,6) | 34 |
  | `tab:pbb_cat108` + `tab:pbb_cat108_b` | 108 | (9,6) | 107 (split: ranks 1--54 / 55--107) |
  | `tab:pbb_cat144` | 144 | (12,6) | 66 |
  | `tab:pbb_cat180` | 180 | (15,6) | 64 |
  | `tab:pbb_cat360` | 360 | (30,6) | 50 |
  (sum = 47+34+107+66+64+50 = 368. ✓)
  **Row schema** (9 columns, pbb_catalog_tables.tex l.9--11, identical across all 7 tables):
  `Cl. | (ℓ,m) | A(x,y) | B(x,y) | C(x,y) | D(x,y) | k | d | FOM`
  - NO decoder/Pat./Camp. columns (all are C5). `d` = MILP value; `≤` prefix = incumbent upper bound,
    else exact (all logicals proven optimal) (l.75, table captions).
- **evidence modality**: `LiteratureGrounded`.
- **dependencies**: SM-MILP-2/3; BLISS dedup; `pbb-commute` (chunk_002).
- **status**: `[SOLID]`.
- **PBB catalog landmark rows** (verbatim):
  - n=144 (12,6): class 9 & 6 & 1 & 13 → $\llbracket144,12,12\rrbracket$ FOM 12.0 EXACT (the headline mixed
    X/Z PBB matching the gross code FOM); several class reps at $\le12$ incumbent (pbb_cat144 l.265--273).
  - n=360 (30,6): class 7 → $\llbracket360,12,{\le}24\rrbracket$ FOM ≤19.2 (l.433) — this is the HIGHEST-FOM
    PBB at n=360 per SM Sec sm:utility / sm:threshold tables (NOTE: class 1 row shows $\llbracket360,10,{\le}40\rrbracket$
    FOM ≤44.4 (l.427), but it is an upper-bound-only FOM driven by an untrusted large $d$ incumbent; the
    threshold/utility discussion treats $\llbracket360,12,{\le}24\rrbracket$ as the practical headline).
    class 27 → $\llbracket360,60,6\rrbracket$ FOM 6.0 EXACT (k=60, l.453); class 35/36 → $\llbracket360,50,6\rrbracket$ FOM 5.0.
  - n=108 (9,6): class 7 etc → $\llbracket108,8,10\rrbracket$ FOM 7.4 (l.126); n=72 (6,6): class 13 etc →
    $\llbracket72,4,8\rrbracket$ FOM 3.6 and $\llbracket72,12,6\rrbracket$ FOM 6.0 (l.76--90).
  - **[HOLE]** FOM-ranking inconsistency at n=360: the SM `sm:pbb_catalog` (l.73) sorts by FOM descending and
    class 1 ($\le44.4$) ranks above class 7 ($\le19.2$), yet ground-truth/abstract names
    $\llbracket360,12,{\le}24\rrbracket$ as "highest PBB FOM ≤19.2". Resolution: the $\le44.4$ rows are
    incumbent-only with large untrusted $d$ (trust filter $d/\sqrt n$, main text Sec V D); when restricted to
    trusted/exact bounds the headline is ≤19.2. expected evidence to close: the trust-filter classification
    of pbb_cat360 rows 1--6 (the $\le40$/$\le32$/$\le30$ incumbents). `[FUTURE]` — does not block import.

---

## SM-VERIF — per-decoder and BP-OSD verification data (ledger)

### SM-VERIF-1 — per-decoder global-minimum rates (`tab:decoder_rates`)
- **context**: SM Sec. `sm:decoders`, supplemental.tex l.81--108.
- **claim**: fraction of C1--3 trinomial codes for which each decoder found the global min $d$, by rate $k/n$.
  Across all 154 C1--3 poly reps: $\text{OSD}_0$/sp 49 (31.8%), CS$_{10}$/sp 90 (58.4%), CS$_{10}$/ms 100
  (64.9%). Mean gap OSD$_0$-min vs global-min = 3.8 (median 4, max 18). Sole-discoverer counts: 14 / 37 / 45.
  Stratified ($<5\%$: 8 codes; 5--10%: 56; 10--15%: 64; $>15\%$: 26). CS$_{10}$ advantage largest at $k/n>15\%$.
- **evidence modality**: `StatisticalInference`.
- **dependencies**: `panteleev2021degenerate`, `roffe2020decoding` (BP-OSD) `[AXIOM]`.
- **status**: `[SOLID]`. Supports main-text recommendation (Sec VI E): always use multiple decoder configs.

### SM-VERIF-2 — BP-OSD overestimation / per-batch instability (`tab:per_batch_stats`, `tab:extended`)
- **context**: SM Sec. `sm:per_batch`, supplemental.tex l.111--210.
- **claim**: BP-OSD distances are stochastic UPPER bounds, severe overestimates for high-$k$ codes.
  Protocol: 150k trials = 3 decoders × 10 batches × 5000. Gross code returns $d=12$ in all 30 batches,
  zero variance (control). High-$k$ examples (second independent 150k run, l.137):
  | code | MILP $d$ | BP min/max range (overestimate factor) |
  |---|---|---|
  | $\llbracket360,40,2\rrbracket$ @ (15,12) | 2 | OSD$_0$ 18--34 |
  | $\llbracket288,32,4\rrbracket$ @ (24,6) | 4 | 18--44 (4.5--11×) |
  | $\llbracket144,24,6\rrbracket$ @ (12,6) | 6 | 8--20 |
  | $\llbracket288,24,12\rrbracket$ @ (12,12) | 12 | OSD$_0$ medians ~2.4× true; only 2/30 batches exact |
  Extended 1.5M-trial run (`tab:extended`, l.197--202): even at 10× depth BP-OSD overestimates persist —
  $\llbracket360,40\rrbracket$ $d_{1.5M}{=}6$ (MILP 2), $\llbracket288,32\rrbracket$ $d_{1.5M}{=}12$ (MILP 4),
  $\llbracket144,32\rrbracket$ $d_{1.5M}{=}2$ (MILP 2, exact). 10× depth got the bias DIRECTION right but still
  ~3× overestimate. Cautionary: $\llbracket144,32,2\rrbracket$ has 72 independent wt-2 logicals yet 29/30
  batches failed to find one (l.210).
- **evidence modality**: `NumericalSimulation` (BP-OSD); contrasted against `ExactProof` MILP.
- **dependencies**: SM-MILP-1/3; BP-OSD libs `[AXIOM]`.
- **status**: `[SOLID]`. Headline: million-trial BP-OSD cannot substitute for exact distance (l.207).
- **note**: `thm:ab_d2` (App D) is invoked here — the $\llbracket144,32,2\rrbracket$ / $\llbracket144,12,12\rrbracket$
  $A=B$ $d=2$ result is "proven exact" (l.206,209). Theorem itself is in chunk for App D; here it is a dependency.

### SM-VERIF-3 — distance tightening 60k→150k (`tab:decoder_comparison_full`)
- **context**: supplemental.tex l.213--240. C1 codes, $\Delta d$ = upper-bound reduction (e.g.
  $\llbracket288,24\rrbracket$ 20→12, $\Delta d=-8$). Confirms even 150k bounds are gross overestimates.
- **evidence modality**: `NumericalSimulation`. **status**: `[SOLID]`.

### SM-VERIF-4 — univariate families all have $d\in\{2,4\}$ (`tab:uv_families`)
- **context**: SM Sec. `sm:univariate`, supplemental.tex l.243--313.
- **claim**: of 154 C1--3 trinomial reps, 87 (57%) are univariate → 12 distinct codes after dedup. Multiple
  UV families hit $k=40$ (highest among trinomials; C4 mixed-monomial reaches $k=54$). MILP reveals EVERY
  univariate code has $d\in\{2,4\}$. By Tillich–Zémor $d=\min(d_1,d_2,d_1^\top,d_2^\top)$ `tillich2014quantum`;
  palindromic check polys ⇒ $H^\top=H$ ⇒ collapses to $\min(d_A,d_B)$; low-weight quotients force min small
  (2 or 4); odd weight of trinomial check polys forces all four component distances even ⇒ rules out $d=3$.
  FOM collapse: top row $\text{FOM}_\text{BP}=64.0 \to \text{FOM}_\text{MILP}=0.4$ (up to 12× overestimate).
- **evidence modality**: `SymbolicDerivation` (the $\{2,4\}$ argument) wrapping `ExactProof` MILP per-code data.
- **dependencies**: `tillich2014quantum` `[AXIOM]` (HGP distance = min of 4 component distances);
  `eberhardt2024pruning` (UV = HGP of low-distance cyclic codes); `lem:crt_k` (App C, $k=8\ell/3$) related.
- **status**: `[SOLID]`. NOTE label `lem:crt_k` and `thm:ab_d2` are App C/D theorem targets, cited but proven elsewhere.

### SM-VERIF-5 — code-capacity (threshold) simulation data
- **context**: SM Sec. `sm:threshold`, supplemental.tex l.316--504.
- **claim**: full numerical block-LER and per-logical-qubit ($p_L = 1-(1-\text{LER})^{1/k}$) data.
  - X-only CSS (`tab:threshold_full`, `tab:per_qubit_full`): 6 codes (5 wt6 BB + 1 wt8$^\dagger$
    $\llbracket360,20,{\le}14\rrbracket$, MILP incumbent $\le14$, BP-OSD 300k confirms $d=14$), 12 error rates,
    100k shots/point. All 6 achieve $p_L<p$ at every rate.
  - 2 extra CSS (`tab:threshold_full_extra`): $\llbracket288,50,8\rrbracket^\ddagger$ (wt8 cross-factored),
    $\llbracket144,8,12\rrbracket$.
  - X-only non-CSS PBB (`tab:threshold_noncss_full`, `tab:per_qubit_noncss_full`): 5 PBB codes + CSS gross
    baseline — $\llbracket144,12,12\rrbracket$ PBB, $\llbracket72,4,8\rrbracket$, $\llbracket108,8,10\rrbracket$,
    $\llbracket360,12,{\le}20\rrbracket$, $\llbracket360,12,{\le}24\rrbracket$. All 6 achieve $p_L<p$.
  - depolarizing (`tab:threshold_depolarizing_full`): SAME PBB codes, decoder-MISMATCHED (iid X/Z BP-OSD
    prior at marginal rate $2p/3$ on $2n$ cols of symplectic $[H_z\mid H_x]$, does NOT model the $X/Z$
    correlation $P(e_x{=}1,e_z{=}1)=p/3$ from $Y$ errors) — reported LERs are a LOWER bound on the optimal
    depolarizing threshold, not the optimal threshold (l.327--328, 478). Both $n=360$ PBB stay LER$<p$
    throughout; small crossover (lower-FOM ≤20 better at $p\le4\%$, higher-FOM ≤24 better at $p\ge5\%$).
  - Decoders: OSD-CS order 7, product-sum, 20 BP iterations (l.329). Wilson 95% CIs ≤0.06 pp for LER≤1%.
- **evidence modality**: `NumericalSimulation`.
- **dependencies**: BP-OSD libs `[AXIOM]`.
- **status**: `[SOLID]`.
- **[AXIOM]** the depolarizing threshold figures are decoder-mismatched and are a LOWER bound only —
  any "depolarizing threshold" claim downstream must remain conditional on the iid-prior mismatch caveat.

---

## SM-UTIL — utility stratification of the combined catalog
- **context**: SM Sec. `sm:utility`, supplemental.tex l.507--520.
- **claim**: 465 distinct codes total. Among 97 CSS: MILP $d$ spans 2 ($A=B$ + some UV) to 14. C1--3 trinomial
  portion: 13 $(n,k,d)$ triples with $d\ge6$; C4 mixed-monomial expands to 41 distinct triples $d\ge6$.
  CSS with FOM≥6.0: 5 triples at C1--3 lengths (incl. decomposable $\llbracket288,24,12\rrbracket$ FOM 12.0)
  + 29 C4-only = 34 distinct CSS triples at FOM≥6. All 368 PBB have $d\ge6$ by construction (C5 rejected
  $d\le4$ in-loop): 108 distinct FOM≥6.0, 53 FOM≥8.0, 25 FOM≥12.0. Most-practical ($d\ge8$ AND FOM≥6.0):
  50 distinct $(n,k,d)$ triples across both catalogs (30 CSS, 24 non-CSS, 4 shared) → main text Table V subset.
- **evidence modality**: `LiteratureGrounded` (aggregate counts over the verified catalog).
- **status**: `[SOLID]`.

## SM-NOV — novelty / comparison
- **context**: SM Sec. `sm:comparison`, supplemental.tex l.523--546.
- **claim**: published wt-6 BB inventory at $n\in\{144,288,360\}$ = one code each from `bravyi2024high`.
  wt-8 prior: `symons2025covering` $\llbracket144,14,14\rrbracket$ FOM 19.1 (covering graphs);
  `liang2025selfdual` $\llbracket144,6,14\rrbracket$ FOM 8.2 (self-dual). `liang2025generalized` enumerated
  wt-6 generalized toric $f=1+x+x^ay^b$ for $n\le400$, reports only $\llbracket288,12,18\rrbracket$ at 288;
  the $x/y$-swap codes do NOT fall in their canonical form. `lin2024abelian` 2BGA enumeration wt≤8 for
  $n\le100$ (complementary, different block lengths). Only 2 of 99 CSS classes match prior work (gross code
  $\llbracket144,12,12\rrbracket$ + $\llbracket360,12,{\le}24\rrbracket$, both `bravyi2024high`, rediscovered
  by C4). Remaining 97 classes claimed novel.
- **evidence modality**: `LiteratureGrounded`.
- **status**: `[SOLID]`.
- **[AXIOM]** novelty claim is conditional on a review of 25+ papers / 6 public repos through March 2026 and
  NO access to unpublished industrial search databases (l.538). Downstream "novel" claims stay conditional on this.
- wt-8 vs wt-6 cost (l.540--546): wt-8 ⇒ 8 CNOT layers/cycle vs 6 (+33% depth); full circuit-level comparison `[FUTURE]`.

## SM-ABL — ablation methodology (8 arms)
- **context**: SM Sec. `sm:ablation`, supplemental.tex l.620--653.
- **claim**: 8 arms on the same 8 Stage-2 lattices: (1) seed; (2) uniform random trinomials $10^3$/lattice
  (1 seed); (3) random $10^4$/lattice (5 seeds, 80000/seed); (4) GA tournament(5) + single-point poly
  crossover + exponent mutation + 10% elitism, pop 200, $10^4$ evals/lattice (5 seeds); (5) GA-G on the LLM
  ansatz, AST-level mutations (int literals/loop bounds/strategy blocks), tournament(5), strategy-block
  crossover, pop 100, 30 gens, ~2800 evals/seed (5 seeds, ~14000 total); (6--8) highest-fitness C1--3 ansätze.
  GA-G 6 AST operators: literal ±1/±2/random; loop-bound mod; strategy-block duplicate-with-perturb;
  block removal; template splice ($x/y$-swap, perturbation, univariate); block-order swap. GA-G CANNOT create
  new strategy branches — only shuffles/parameterizes existing structure; LLM can invent new patterns (l.642).
  Degenerate verification (l.644--653): exhaustive GA across 5 seeds × 8 lattices = 9832 unique codes; at
  every lattice where C1 found codes, every GA code exceeding per-lattice max{k} has $d\le2$ via explicit
  wt-2 logicals ($k/n=2/3$, all 11 cases: 6 @ (12,6), 1 @ (6,12), 1 @ (12,12), 3 @ (24,6); 1 has $A=B$).
  At (16,9),(18,8) (where all evolved ansätze fail) GA finds genuine $d\ge3$; MILP of top-10 (k=32--64) →
  $d=4$--6 (proven exact), FOM≤4.0 = 3× below the LLM's FOM 12.0. GA-G hits $k=n/2$ at 6/8 lattices every
  seed (8/8 over seed union), $d\le2$; low variance (±22 vs ±142 for exponent-tuple GA), converges to
  $k=n/2$ attractor within ~10 gens.
- **evidence modality**: `EmpiricalMeasurement` + `ExactProof` (MILP degenerate audit).
- **dependencies**: SM-MILP-1/3; `thm:ab_d2` (the $A=B$ $d=2$ case).
- **status**: `[SOLID]`.

---

## Open holes / gaps carried by this chunk

- `[HOLE]` (SM-CAMP) — controlled model-config-only experiment to isolate the ensemble contribution to
  search effectiveness (C2/C3 vs C1). Expected evidence: `StatisticalInference`. `[FUTURE]`, not blocking.
- `[HOLE]` (SM-CAT-PBB) — trust-filter classification of pbb_cat360 incumbent-only rows ($\le40/\le32/\le30$)
  to reconcile the "highest PBB FOM ≤19.2" claim with the catalog's FOM-descending sort. `[FUTURE]`.
- `[FUTURE]` (SM-NOV) — full circuit-level wt-8 vs wt-6 FOM-vs-depth comparison (+33% CNOT depth per cycle).
- `[AXIOM]` carried forward (conditional on these for any certified downstream claim):
  - `bravyi2024high` = arXiv:2308.07915 — MILP baseline + BB definition (MANDATORY escalation candidate).
  - `tillich2014quantum` — HGP distance = min of 4 component distances (UV $d\in\{2,4\}$ argument).
  - BP-OSD libs (`panteleev2021degenerate`, `roffe2020decoding`) — decoder correctness; all BP-OSD distances
    are stochastic UPPER bounds (SM-VERIF-2 quantifies up to 12× overestimate).
  - depolarizing-threshold figures (SM-VERIF-5) are decoder-mismatched LOWER bounds, not optimal thresholds.
- Theorem labels referenced but PROVEN in other chunks (App C/D), treated here as dependencies, NOT re-proven:
  `thm:ab_d2` ($A=B,k>0 \Rightarrow d=2$ exactly), `lem:crt_k` ($k=8\ell/3$ HGP), `css-commute`, `pbb-commute`.
