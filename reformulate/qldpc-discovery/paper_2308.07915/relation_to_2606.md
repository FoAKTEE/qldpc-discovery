# Dependency Note — arXiv:2606.02418 ← arXiv:2308.07915 (`bravyi2024high`)

> What the mission paper arXiv:2606.02418 IMPORTS from the foundational BB-code paper
> arXiv:2308.07915, mapped to the `src/qcode_discovery` module that reproduces it and to
> the `external_axioms` id it discharges. Each row is a TYPED entry
> (context · claim · modality · dependencies · status marker). Default modality
> `LiteratureGrounded`. Cited-but-not-reproduced results stay `[AXIOM]` — final results
> remain conditional on them. Tex labels preserved VERBATIM.

## 0. The axiom being discharged

In arXiv:2606.02418's ledger, the BB construction enters as the external axiom
`ax:bb-construction` (ledger id `sig.bravyi` / `OBL-AXIOM-BRAVYI`, ref `bravyi2024high`,
escalation MANDATORY). Acquiring arXiv:2308.07915 supplies the actual definition, so:

> `ax:bb-construction` = **REPLACED-BY-EXTERNAL-AXIOM** via arXiv:2308.07915
> (`sec:codedefinition`, l.508–557; `lem:kd`, l.666–749).

The axiom's modality stays `LiteratureGrounded` (we cite Bravyi et al. for the
*definition*); what our kernel additionally provides is INDEPENDENT VERIFICATION of the
concrete consequences (CSS condition, gross-code `k`), upgrading those specific claims
to reproducible evidence while the construction itself remains imported.

## 1. Dependency table

| # | Imported claim (from 2308.07915) | Tex anchor | Module reproducing it | external_axioms id | Status / modality |
|---|---|---|---|---|---|
| D1 | BB CSS construction: `H^X=[A\|B]`, `H^Z=[B^T\|A^T]` over `R=F2[x,y]/(x^ℓ-1,y^m-1)`, `A,B` weight-3 monomial sums; CSS condition `H^X(H^Z)^T = AB+BA = 0 (mod 2)` | `sec:codedefinition` eqs `AB` (l.524–530), `HXHZ` (l.535–544) | `bb_codes.py` (`BBCode.HX/HZ`, `_validate_css`) | `ax:bb-construction` = **REPLACED-BY** this paper | **VERIFIED** (kernel re-derives CSS=0 from commuting shift matrices) + `LiteratureGrounded` for the definition |
| D2 | gross code `[[144,12,12]]` at `(ℓ,m)=(12,6)`, `A=x^3+y+y^2`, `B=y^3+x+x^2`; weight-6 checks | `tab:codes` (l.605), worked example l.529 | `bb_codes.py` + `validation.py` (`landmark:bravyi2024high`) | (instance of `ax:bb-construction`) | **VERIFIED** (kernel: `n=144`, `k=12`, CSS holds, `stabilizer_weight=6`); `d=12` itself is `LiteratureGrounded` (distance not re-run here) |
| D3 | dimension `k = 2ℓm − 2·rank(H_X)` (= `2·dim(ker A ∩ ker B)`); `n = 2ℓm`; `rank H^X = rank H^Z` via involution `C=C_ℓ⊗C_m` (`A^T=CAC`, `B^T=CBC`, eq `ABC2`) | `lem:kd` (l.666–701), eq at l.547–552 | `metrics.py` (`css_k = n − rank(H_X) − rank(H_Z)`) | (consequence of `ax:bb-construction`) | **VERIFIED** (kernel `css_k` returns 12 for gross code); proof `ExactProof` in chunk_001 digest |
| D4 | MILP minimum-distance method: `d_X = min{|v|}` over min-weight `X`-logicals anticommuting with each `Z`-logical, solved as integer LP with mod-2 slacks ("Following Bravyi et al.", `landahl2011fault` MILP) | `tab:codes` caption (l.636–637, cites `landahl2011fault`); 2606 SM CSS MILP | `distance_milp.py` (`css_distance_milp`, `_min_weight_logical`) | (method imported from `bravyi2024high` SM) | **[AXIOM]** for METHOD PROVENANCE (we cite Bravyi/Landahl for the formulation); our solver runs are `ExactProof` (HiGHS MIP gap=0) on each *instance* but the method's correctness is `LiteratureGrounded` |
| D5 | logical operators via Tanner-graph automorphisms: polynomial logical Paulis `\bar X_α=X(αf,0)`, `\bar Z_α=Z(αh^T,αg^T)` etc. (eq `eq:logicalpaulis`) from `Bf=0`, `gB+hA=0`; automorphism shifts `A_jA_k^T`, `B_jB_k^T` generate `\calM` | `ssec:logical_pauli_operators` (l.997–1065); `ssec:automorphisms` (l.1124–1149) | `metrics.py` (`css_logicals` — basis of `ker H_X mod rs H_Z`); `clifford_equiv.py` (LC layer) | (consequence of `ax:bb-construction`) | **VERIFIED** for the logical-basis count (`css_logicals` returns `k` independent reps); the automorphism *gate* construction is `LiteratureGrounded` |
| D6 | depth-7 (≤8-round) syndrome-extraction circuit, weight-6 checks, thickness-2 Tanner graph | `sec:syndrome_circuit` (l.43–200, `tab:syndromecircuit`); thickness `lem:thickness` (l.775) | (not reproduced — no circuit simulator in kernel) | — | **[AXIOM]** (circuit-level claim; downstream results stay conditional on it) |

## 2. VERIFIED vs [AXIOM] summary

**Kernel-VERIFIED (reproducible evidence, not assertion):**
- BB construction CSS condition `H^X(H^Z)^T=0` — re-derived by `bb_codes.BBCode._validate_css`
  from the commuting shift matrices `x,y`; holds for the gross code (checked).
- gross code `[[144,12,12]]`: `n=144`, `k=12`, weight-6 stabilizers — re-computed by the
  kernel (`bb_codes.py` + `metrics.css_k`); `k=12` matches `lem:kd`.
- `k = 2ℓm − 2·rank(H_X)` dimension formula — `metrics.css_k` (rank form) returns the
  Bravyi value; proof of `rank H^X=rank H^Z` is `ExactProof` in the chunk_001 digest.
- logical-operator *count* `k` via `metrics.css_logicals` (basis of `ker H_X / rs H_Z`).

**Remains [AXIOM] (cited, not reproduced — final results conditional):**
- MILP-distance METHOD PROVENANCE (D4): the *formulation* is imported from
  `bravyi2024high` / `landahl2011fault`; our per-instance solver runs prove optimality
  (HiGHS MIP gap=0) but do not re-derive the method's correctness. The gross-code
  *distance* `d=12` is `LiteratureGrounded` (not re-run in this note).
- depth-7 syndrome circuit (D6): circuit-construction claim, no kernel reproduction.
- automorphism logical-*gate* construction (D5): the Clifford-gate-from-automorphism
  argument is `LiteratureGrounded` (only the logical-operator basis is verified).

## 3. Open holes

- `[HOLE]` (expected: `ExactProof`/`NumericalSimulation`) — verify the gross-code
  **distance** `d=12` against `distance_milp.css_distance_milp` to MIP gap=0, to upgrade
  D2's `d` from `LiteratureGrounded` to reproducible evidence. Currently only `n,k` and
  the CSS/weight properties are kernel-verified; the distance is imported.
