# Chunk Index — arXiv:2308.07915

> Pipeline-0 (source-import) chunking plan for the FOUNDATIONAL Bivariate Bicycle (BB)
> code paper. Each chunk is decomposed into a digest of TYPED ledger entries
> (context · claim · modality · dependencies · status marker). Default modality
> `LiteratureGrounded` (evidence = the cited tex section) unless an in-paper proof
> upgrades it to `ExactProof`/`SymbolicDerivation`. Cited-but-not-reproduced external
> results are `[AXIOM]`. Tex labels and equations are preserved VERBATIM in the digests.
> This paper (`bravyi2024high`) is the source whose `ax:bb-construction` REPLACES the
> external axiom of the mission paper arXiv:2606.02418.

## Paper

| Field | Value |
|---|---|
| arXiv ID | 2308.07915 (v2) |
| Title | High-threshold and low-overhead fault-tolerant quantum memory |
| Authors | Bravyi, Cross, Gambetta, Maslov, Rall, Yoder (IBM) |
| Venue | Nature 627, 778–782 (2024) |
| Source (read-only mirror) | `src/arXiv_v2.tex` (1368 lines), `src/supplemental_v2.tex` (1341 lines) |
| Role in Σ | `LiteratureGrounded` — BB definition + MILP-distance baseline + circuit-level FT memory |

## Chunks

| Chunk | Source file | Line range | Sections (tex labels) | Named objects | Digest path | Status |
|---|---|---|---|---|---|---|
| chunk_001 | `src/arXiv_v2.tex` | l.308–888 | `sec:results` (Main results, l.308); `sec:codedefinition` (BB definition, l.508); notation Table (l.561); `tab:codes` examples incl. gross code (l.587–644); `lem:kd` (l.666); monomial `q(T,α)` labeling (l.757); `lem:thickness` (l.775); `lem:connected` (l.843); toric-layout `\begin{dfn}` (l.857) + `lem:toric_layout` (l.863); `sec:conclusions` boundary at l.888 | `x=S_ℓ⊗I_m`, `y=I_ℓ⊗S_m`; BB code `\qc`; `A=A_1+A_2+A_3`, `B=B_1+B_2+B_3` (eq `AB`); `H^X=[A|B]`, `H^Z=[B^T|A^T]` (eq `HXHZ`); params `n=2ℓm`, `k=2·dim(ker A ∩ ker B)`, `d=min{|v|:v∈ker H^X∖rs H^Z}`; gross `[[144,12,12]]` (ℓ,m)=(12,6), `A=x^3+y+y^2`, `B=y^3+x+x^2`; `tab:codes` family ([[72,12,6]], [[90,8,10]], [[108,8,10]], [[288,12,18]], [[360,12,≤24]], [[756,16,≤34]]); involution `C=C_ℓ⊗C_m` (eq `ABC2`: `A^T=CAC`, `B^T=CBC`); wheel-graph thickness-2 decomposition; Cayley/toric layout `Z_{2μ}×Z_{2λ}` | `digest/chunk_001_bb_definition.md` | DONE |
| chunk_002 | `src/supplemental_v2.tex` | l.963–1350 (logicals) + l.43–200 (syndrome circuit) | `sec:logicals` (l.963); `ssec:logical_pauli_operators` (l.997); `ssec:automorphisms` (l.1124); `ssec:ZX_duality` (l.1226); `ssec:logical_measurements` (l.1293); `sec:syndrome_circuit` (l.43) | Logical Pauli blocks (primed/unprimed): `\bar X_α=X(αf,0)`, `\bar Z_α=Z(αh^T,αg^T)`, `\bar X'_α=X(αg,αh)`, `\bar Z'_α=Z(0,αf^T)` (eq `eq:logicalpaulis`); solving `Bf=0`, `gB+hA=0` (⇔ `PB+QA=0`); anticommutation lemma `X(P,Q)`/`Z(P̄,Q̄)` ⇔ `1∈PP̄^T+QQ̄^T` (proof present); `tab:f_polys` minimum-weight `f,g,h` for [[144,12,12]] (60 qubits/layer); automorphism gates (depth-4 CNOT, shifts `A_jA_k^T`, `B_jB_k^T` generating `\calM`); ZX-duality block swap (`breuckmann2022foldtransversal`); Cohen-Pastawski-style logical-`X`/`Z` measurement ancilla (`cohen2022lowoverhead`); depth-8 SC `tab:syndromecircuit` (rounds use `A_1,A_2,A_3,B_1,B_2,B_3` and transposes), depth-7 effective CNOT depth | `digest/chunk_002_logicals.md` | DONE |

## Coverage notes

- chunk_001 covers the BB DEFINITION + structural lemmas reproduced by our kernel
  (`bb_codes.py`, `metrics.py`). The proof of `lem:kd` (`rank H^X = rank H^Z` via the
  involution `C`, and `d^X=d^Z`) is PRESENT in this chunk (modality `ExactProof` in the
  digest).
- chunk_002 covers logical-operator structure (informs `metrics.css_logicals` /
  LC-equivalence layer) and the syndrome-extraction circuit. The depth-7 CNOT figure is
  a circuit-construction claim that our kernel does NOT reproduce (no circuit simulator) →
  remains `[AXIOM]` downstream; see `relation_to_2606.md`.
- NOT chunked (deliberately deferred, `[FUTURE]`): `sec:decoder` (BP-OSD, supplemental
  l.396), `sec:numerics` (l.885), and the figures (`fig:2Dlayout`, `fig:wheel_extraction`,
  `fig:navigation`, image-only). These are not on the import path that arXiv:2606.02418
  depends on for the BB construction + distance baseline.
