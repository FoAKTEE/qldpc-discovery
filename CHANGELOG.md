# Changelog

## 0.1.0 — reproduction of arXiv:2606.02418 (bivariate bicycle code discovery)

### Kernel (verifier)
- GF(2) algebra; bivariate ring + circulant construction; BB (CSS) and PBB (non-CSS) codes.
- Encoding dimension `k` via GF(2) rank; logical-operator bases; FOM = k d²/n.
- Minimum distance: CSS MILP + symplectic (non-CSS) MILP via scipy/HiGHS; exhaustive enumeration;
  BP-OSD stochastic upper bound (optional `ldpc`).
- Tanner-graph decomposability (direct-sum detection); lattice-symmetry + exact BLISS dedup
  (optional `python-igraph`); local-Clifford CSS-equivalence (Hadamard 2-coloring + rank condition
  + uniform-Clifford enumeration).
- Numeric witnesses for `thm:ab_d2` (A=B ⇒ d=2) and `lem:crt_k` (univariate ⇒ k=8ℓ/3).

### Discovery (catalog-blind)
- Staged evaluation cascade (k → BP-OSD + d/√n trust filter → MILP) with FOM-ranked archive.
- GA search over polynomial tuples; generator-ansatz program evolution (GA-G + Claude-as-LLM operator;
  external-LLM-at-scale is `[FUTURE]`, resource-gated).
- Post-hoc validation against the paper catalog + landmark codes (the only catalog reader).

### Results
- Reproduced 4 signature findings: A=B d=2 trap, 12× BP-OSD overestimate, [[288,24,12]]=gross⊕gross,
  univariate d∈{2,4}.
- Blind→validated: Claude-guided rediscovery of [[144,12,12]] + [[288,16,12]] (POLY_MATCH); GA found
  [[72,12,6]] and non-CSS [[36,2,6]] (exact MATCH).
- Clean-room (`blind-zero`): paper-naive discovery reached only d≤8 at n=144 (certified [[144,12,8]]),
  not the d=12 flagships — honest evidence for the value of structured/LLM-guided search.

### Packaging
- `src/` layout reorganized into logical subpackages (algebra/codes/distance/structure/discovery).
- Stable public API via `qcode_discovery/__init__.py`; CLI (`qcode-discover`/`qcode-validate`/`qcode-audit`).
- pyproject with metadata, optional `[decoders]`/`[dev]` extras, console entry points.

Bugs fixed during development: BP-OSD coset-logical orientation (returned d=6 for the d=12 gross code);
`dedup_bb` signature omitted (l,m); WL-histogram dedup over-merged regular Tanner graphs (replaced).
