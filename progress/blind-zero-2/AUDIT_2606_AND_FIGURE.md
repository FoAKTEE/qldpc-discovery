# Audit of arXiv:2606.02418 + exact reproduction of its "best codes" figure with our codes

*Branch `blind-zero-2`. Post-hoc comparison (blind discipline permits this — the search is finished).
Paper source read from the `bbc` branch (`ref-paper/arxiv-2606.02418/`); the figure template was read
visually (VLM) from the arXiv source tarball `figures/fig_pareto_frontier.pdf`.*

## 1. The paper (audit)
**"Evolutionary Discovery of Bivariate Bicycle Codes with LLM-Guided Search"**, Cruz-Benito, Cross,
Kremer, Faro (IBM Research, dated 2026-06-02).

- **Method:** LLM-guided evolutionary program synthesis (FunSearch/AlphaEvolve-style) — LLMs mutate Python
  programs that emit BB / perturbed-BB *ansätze*. MAP-Elites, a k-then-distance evaluation cascade, trust
  filtering, **MILP exact distance**, BLISS Tanner-graph dedup, decomposability + Clifford checks.
- **Scale:** 5 campaigns, ~1,650 evolutionary iterations, ~2×10⁵ candidates screened, ~140 h compute,
  ~US$400 LLM inference.
- **Catalog:** **465 distinct codes — 97 CSS (weight-6 and weight-8) + 368 non-CSS PBB**, encoding
  dimension up to **k=54**, block lengths n ≤ 360.
- **Headline best codes** (Table "useful", d≥8 & FOM≥6):
  | source | code | FOM | wt | type |
  |---|---|---|---|---|
  | Bravyi (prior) | `[[360,12,≤24]]` | ≤19.2 | 6 | CSS — highest published FOM |
  | Bravyi (prior) | `[[288,12,18]]` | 13.5 | 6 | CSS — highest exact wt-6 |
  | Bravyi (prior) | `[[144,12,12]]` | 12.0 | 6 | CSS — gross code |
  | **this work** | `[[288,50,8]]` | 11.1 | 8 | CSS — cross-factored |
  | **this work** | `[[288,16,12]]` | 8.0 | 6 | CSS |
  | **this work** | `[[144,8,12]]` | 8.0 | 6 | CSS |
  | **this work** | `[[360,12,≤24]]` | ≤19.2 | 8 | PBB — highest PBB FOM |
  | **this work** | `[[144,12,12]]` | 12.0 | 8 | PBB — non-CSS gross |
- **Higher k at each n** (Table "comparison"): k=54@144 (4.5× Bravyi), k=50@288 (4.2×), k=40@360 (3.3×).

### The paper's central finding — and it is the same as ours
> "**no discovered indecomposable code exceeds the prior highest FOM at its own block length**"; the
> apparent highest-k d=12 code `[[288,24,12]]` is a *direct sum of two gross codes* (decomposable);
> "high-k codes routinely have **d≤4**"; **BP-OSD overestimates distance for high-rate codes (k/n>0.1) by
> up to 12×**, so they introduce MILP ground truth — "distance claims for high-k BB codes require exact
> verification."

This is precisely the conclusion our blind-zero-2 search reached independently (`SYNTHESIS.md`): BP-OSD
inflates, high-k is degenerate, certification (not the scan) decides reality, no FOM record is beaten.
**We reproduced the paper's core methodological lesson from zero, blind.**

## 2. The reproduced figure
Paper Fig. (pareto) "Rate–distance landscape" is a **2×2 grid**: (a) CSS k-vs-d with Pareto frontier;
(b) CSS FOM=kd²/n vs n; (c) PBB k-vs-d; (d) PBB FOM vs n. Red `+` = Bravyi baselines; red dotted =
FOM=12 (gross code); gray dashed = Pareto frontier. We reproduce this layout exactly with **our** codes,
in two versions (`make_pareto_figure.py`):

- **`fig_pareto_reproduction_asfound.png`** — our 3,435 CSS + 6 PBB codes with **as-found** distances
  (BP-OSD scan upper bounds, CSS; exact symplectic, PBB). Honors "no matter correct or not": the CSS
  panels explode to **k up to 300, d up to 303, FOM up to ~25,700** — the BP-OSD "distance trap" the
  paper warns about, rendered visually. The Bravyi baselines and the entire real frontier are crushed
  into the bottom-left corner.
- **`fig_pareto_reproduction_certified.png`** — only the **154 codes we certified**, with certified
  (ISD-tightened / Brouwer–Zimmermann exact) distances; PBB exact. The honest landscape: **max FOM 24.4**
  (`[[336,8,32]]`, robust to ISD@10000), high-k collapsed to d=1–2 along the k-axis at small d.

The two figures side-by-side ARE the paper's thesis: the same code set looks record-breaking under the
scan decoder and ordinary under certification.

## 3. Reproduction fidelity (phys-agentic-loop EXACT-reproduction check, VLM-verified)
Element-by-element against the paper figure (read visually from `fig_pareto_frontier.pdf`):

| element | paper | our reproduction | match |
|---|---|---|---|
| panel grid | 2×2 (CSS top, PBB bottom) | 2×2 (CSS top, PBB bottom) | ✅ exact |
| (a)/(c) axes | k vs MILP distance d | k vs distance d (ours BP-OSD/ISD) | ✅ structure; label noted |
| (b)/(d) axes | FOM=kd²/n vs block length n | FOM=kd²/n vs n | ✅ exact |
| Bravyi baselines | red `+`, 4 labeled codes | red `P`-cross, same 4 labeled | ✅ |
| FOM=12 line | red dotted (panels b,d) | red dotted (panels b,d) | ✅ exact |
| Pareto frontier | gray dashed staircase (a,c) | gray dashed staircase (a,c) | ✅ exact |
| CSS legend | x/y-swap · constant-mono · mixed-mono | weight-6 · weight-8 · weight≥10 | ⚠ deviation (see below) |
| PBB legend | PBB exact (251) · PBB UB (117) | PBB exact (6) | data: we found only 6 PBB |
| axis ranges | fixed to paper's catalog | auto-scaled to OUR data | adapted (to show our codes) |

**Documented deviations** (justified, not errors): (i) the paper labels CSS markers by *ansatz family*
(x/y-swap, constant-monomial, mixed-monomial); our frontier records *stabilizer weight*, not the paper's
ansatz tags, so we categorize by weight — the same 3-way split the paper itself uses ("weight-6 and
weight-8"). (ii) Our distances are BP-OSD/ISD, not MILP (we have no MILP — pure-Julia constraint), so the
as-found panel necessarily shows the overestimates. (iii) We found only 6 PBB codes (random/structured
PBB seeding is sparse — `PBB_VS_PAPER` finding) vs the paper's 368, so panels (c)/(d) are sparse.

## 4. Our codes vs the paper's (post-hoc)
- **High-k axis:** we match the paper's qualitative result — our scan reaches k≈300, but certification
  collapses every high-k code to d=1–3 (`[[504,294,1]]`); the paper's honest high-k codes are d≤4. Same story.
- **High-distance sparse family:** our robust `[[336,8,32]]` (FOM 24.4, ISD@10000) sits *above* the
  paper's best CSS FOM, but it is an **ISD upper bound, not MILP-exact** — so, exactly as the paper states
  for its own codes, it is **not a certified record**. n=336 is also not one of the paper's block lengths.
- **EXACT-certified:** our evolve phase yielded EXACT codes to k=54 (`[[180,54,4]]`) — same high-rate /
  low-distance regime the paper documents (k=54 at d≤4).
- **PBB:** the paper populates 368 PBB codes via structured evolution; our blind random/commute-by-
  construction PBB is far too sparse (6 codes, d≤4) — a coverage gap we documented, not a contradiction.

## 5. Conclusion
The audit shows **strong agreement**: independently and blind, we reproduced the paper's families, its
rate–distance envelope shape, and — most importantly — its central methodological finding that BP-OSD
overestimates distance for high-rate BB codes and that exact verification is what separates real codes
from artifacts. The reproduced figure makes this visceral: our as-found landscape looks like it shatters
every record (FOM 25,700) precisely because it is uncertified; the certified landscape is honest and
record-free. Where the paper used MILP, we used ISD+Brouwer–Zimmermann; the lesson is identical.

**Artifacts:** `make_pareto_figure.py`, `fig_pareto_reproduction_asfound.png`,
`fig_pareto_reproduction_certified.png`, and this report.
