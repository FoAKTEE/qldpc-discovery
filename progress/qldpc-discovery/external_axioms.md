# External axioms registry — qldpc-discovery

Cited results relied on but not (yet) reproduced in-tree. State machine:
`[CANDIDATE-INLINE]` (could inline a proof) → `[ACTIVE]` (must draw from external ref →
fire escalation) → `[REPLACED-BY-EXTERNAL-AXIOM]` (acquired ref now supplies it).
Final certified results remain conditional on any `[AXIOM]` still open (markers.md).

| ID | Statement | Used by | Source | State |
|---|---|---|---|---|
| `ax:tillich-zemor` | HGP(H1,H2) has dim k=k1k2+k1^T k2^T and distance d=min(d1,d2,d1^T,d2^T) | `lem:crt_k` (k=8ℓ/3); univariate d∈{2,4} | tillich2014quantum | `[CANDIDATE-INLINE]` — dim part re-derived numerically in `theorems.verify_crt_k`; distance bound still axiom |
| `ax:macwilliams-cyclic` | dim ker H = deg gcd(f, z^N−1) for circulant H of f | `lem:crt_k` proof | macwilliams1977theory | `[CANDIDATE-INLINE]` — consistent with our GF(2) rank |
| `ax:rank-css-condition` | stabilizer group is CSS iff rank[X\|Z]=rankX+rankZ over GF(2) (Lemma 7.4) | `pbb_codes.is_css_group`, LC layer (App.E) | cross2025small (Yoder) | `[ACTIVE]` — implemented as a test; the lemma's proof is external → escalation candidate cross2025small |
| `ax:bpt-bound` | kd²=O(n) for geometrically 2D-local stabilizer codes | FOM motivation (§II.C) | bravyi2010tradeoffs | `[CANDIDATE-INLINE]` — benchmark only, not load-bearing |
| `ax:bb-construction` | BB H_X=(A\|B),H_Z=(B^T\|A^T) is a valid CSS code; gross [[144,12,12]] | whole pipeline | bravyi2024high = arXiv:2308.07915 (ACQUIRED + DECOMPOSED) | `[REPLACED-BY-EXTERNAL-AXIOM]` — decomposed in reformulate/.../paper_2308.07915/; construction + n,k re-verified in `bb_codes`/`metrics`. `[HOLE]`: gross d=12 not yet MILP-re-run (LiteratureGrounded) |
| `ax:milp-distance-method` | min-distance via MILP (min-weight logical anticommuting with each dual logical) is correct | `distance_milp` | landahl2011fault / bravyi2024high SM | `[ACTIVE]` — method provenance imported; our ENCODING verified vs exhaustive enumeration (two-method agreement), per-instance HiGHS gap=0 proves each solve but not the method |
| `ax:graph-iso-quasipoly` | colored-graph isomorphism (BLISS) decides permutation equivalence | component 11 BLISS dedup | babai2016graph, junttila2007engineering | `[FUTURE]` — needs igraph/BLISS; networkx canonical-form fallback planned |
| `ax:konig-line-coloring` | weight-w check graph 6-edge-colors → 6 CNOT rounds/type | hardware-feasibility note | König | `[FUTURE]` — not on the discovery critical path |
