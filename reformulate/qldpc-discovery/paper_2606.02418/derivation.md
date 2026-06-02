# Key Derivations — arXiv:2606.02418

Source: `ref-paper/arxiv-2606.02418/src/paper.tex` (1091 lines),
`ref-paper/arxiv-2606.02418/src/supplemental.tex` (715 lines).

Each entry is a TYPED ledger object: `context | claim | modality | dependencies | status`.
Default modality `LiteratureGrounded` (cited result, not reproduced here). Where the paper
gives a self-contained proof we record `ExactProof` / `SymbolicDerivation`. Cited-but-not-reproduced
dependencies are marked `[AXIOM]`. Tex labels (`eq:milp_*`, `thm:ab_d2`, `lem:crt_k`) are VERBATIM.

Common symbols (in `Gamma`): `R = F2[x,y]/(x^l-1, y^m-1)` (commutative ring over F2);
`l, m` lattice dims; `n = 2*l*m` physical qubits; `A,B,C,D in R` represented as `l*m x l*m`
circulant matrices; `A^T` = image under involution `x -> x^{-1}, y -> y^{-1}` (= transpose of
cyclic-shift rep); `e_i` standard basis vector; `code{n,k,d}` code parameters.

---

## D1. CSS bivariate bicycle construction and CSS condition

- **context** sec:bb (paper.tex l.154-167). BB code = CSS code over `R` from two weight-3
  trinomials `A, B in R`.
- **claim** Parity-check matrices (eq. paper.tex l.160-163):

  ```
  H_X = ( A  B ),    H_Z = ( B^T  A^T )
  ```

  where `A, B` are `l*m x l*m` circulants. The CSS orthogonality condition is

  ```
  H_X H_Z^T = A B + B A = 0   over F2.            (CSS condition, l.166)
  ```

  Trinomial restriction -> weight-6 stabilizers (matching bravyi2024high). Campaign 4 relaxes
  to 4-6 term polynomials (weight-8 to weight-12 stabilizers, incl. mixed monomials `x^a y^b`,
  `a,b>0`).
- **evidence** `H_X H_Z^T = A B^{TT} + B A^{TT}`; since `(.)^T` is a ring involution and `R`
  is commutative, `A B + B A = 0` in `R` (characteristic 2: `AB + BA = 2AB = 0` also when
  `AB = BA`, which holds by commutativity). The orthogonality follows directly from
  commutativity of `R` — no per-code check needed (contrast PBB, D3).
- **modality** SymbolicDerivation (algebra explicit in tex). dependencies: bravyi2024high (BB def).
  status: `[SOLID]`. Provenance: paper.tex l.158-167.

## D2. Logical dimension k = 2 l m - 2 rank(H_X)

- **context** sec:bb (paper.tex l.167).
- **claim** `code{n,k,d}` with

  ```
  n = 2 l m,
  k = 2 l m - 2 * rank_{F2}(H_X),
  d = min weight of a nontrivial logical operator.
  ```

- **evidence** Standard CSS dimension count `k = n - rank(H_X) - rank(H_Z)`. For BB the
  involution `x->x^{-1}, y->y^{-1}` exchanges `H_X <-> H_Z`, so `rank(H_X) = rank(H_Z)`, giving
  the factor `2`. Stated, not re-derived, in tex.
- **modality** LiteratureGrounded. dependencies: D1, CSS code theory. status: `[SOLID]`.
  Provenance: paper.tex l.167.

## D3. Perturbed bivariate bicycle (PBB) H matrix and commutativity condition

- **context** sec:pbb (paper.tex l.170-183). Non-CSS ansatz: BB pair augmented with
  perturbation polynomials `C, D in R`.
- **claim** Stabilizer matrix (eq. paper.tex l.175-177):

  ```
  H = ( A  B  C  D )
      ( 0  0  B^T A^T )
  ```

  Block row 1 = mixed stabilizers: X-support `(A,B)`, Z-support `(C,D)`. Block row 2 = pure Z.
  In symplectic form `H = (X | Z)`: first `l*m` cols X-support, second `l*m` cols Z-support.
  All rows commute IFF

  ```
  (A C^T + B D^T) mod 2  is symmetric over F2.    (pbb-commute, l.180)
  ```

  This is the only nontrivial commutativity condition; block1-block2 commutativity is automatic
  from BB ring commutativity. PBB reduces to CSS BB when `C = D = 0`.
- **evidence** The symplectic inner product of two stabilizer rows over the X/Z partition reduces
  to the symmetry of `A C^T + B D^T` (the X-support of block 1 paired with its own Z-support).
  Unlike CSS (where commutativity of `R` suffices, D1), this MUST be verified computationally per
  tuple; empirically ~10% of random weight-3 4-tuples at lattice (6,6) satisfy it.
- **modality** SymbolicDerivation (condition stated; full reduction in symplectic MILP D5,
  supplemental l.690). dependencies: D1, symplectic inner product. status: `[SOLID]`.
  Provenance: paper.tex l.174-183, l.190 cross-ref to symplectic reduction.

## D4. MILP CSS distance formulation (eq:milp_*)

- **context** sm:milp / "CSS distance formulation" (supplemental.tex l.659-674). Following
  bravyi2024high. Minimum-weight X-type logical for the j-th logical qubit.
- **claim** (labels VERBATIM):

  ```
  min   sum_{i=1}^{n} x_i                              (eq:milp_obj)
  s.t.  H_Z x  ==  0   (mod 2)                          (eq:milp_commute)
        < x, Zbar_j >  ==  1   (mod 2)                  (eq:milp_anticommute)
        x_i in {0,1},  i = 1..n                         (eq:milp_binary)
  ```

  where `Zbar_j` is the j-th independent Z-logical operator.
- **evidence** mod-2 constraints `eq:milp_commute`-`eq:milp_anticommute` are linearized with
  integer slack: for each row `sum_i a_i x_i == b (mod 2)`, introduce `s in Z_{>=0}` and replace
  with `sum_i a_i x_i - 2 s = b` (supplemental l.669). Z-type distance by swapping `H_X <-> H_Z`;
  `d = min(d_X, d_Z)` (l.670). Solved via HiGHS through `scipy.optimize.milp`. A solution is
  EXACT when HiGHS reports MIP gap = 0 (proven optimal); else incumbent = valid upper bound
  (l.673). For BB `d_X = d_Z` because the involution exchanges `H_X, H_Z` (l.674); both computed
  as a consistency check.
- **modality** SymbolicDerivation (exact integer program; exactness conditional on MIP gap = 0).
  dependencies: bravyi2024high (formulation), huangfu2018highs (HiGHS solver) `[AXIOM]`,
  virtanen2020scipy `[AXIOM]`. status: `[SOLID]` (exact when MIP gap = 0; otherwise upper bound).
  Provenance: supplemental.tex l.661-674.

## D5. Non-CSS symplectic MILP formulation

- **context** sm:milp / "Non-CSS symplectic formulation" (supplemental.tex l.676-691). Pauli on
  `n` qubits has symplectic rep `(a | b) in F2^{2n}`, `a_i, b_i` = X- and Z-content on qubit i.
  Logical `Lbar_j in F2^{2n}` from qldpc symplectic Gaussian elimination.
- **claim** symplectic weight of `P = X^a Z^b` is `|{ i : a_i != 0 or b_i != 0 }|`. MILP
  (supplemental.tex l.682-688):

  ```
  min   sum_{i=1}^{n} w_i
  s.t.  H . (a | b)^T  ==  0   (mod 2)
        < (a | b), Lbar_j >_symp  ==  1   (mod 2)
        w_i >= a_i,   w_i >= b_i,   w_i <= a_i + b_i
        a_i, b_i, w_i in {0,1}
  ```

- **evidence** `w_i = a_i OR b_i` is the standard linear OR encoding (`w_i>=a_i, w_i>=b_i,
  w_i<=a_i+b_i` = convex hull of the four feasible `(a_i,b_i,w_i)` triples; tight at integer
  points). `H in F2^{m x 2n}` is the symplectic-FLIPPED stabilizer matrix: each stabilizer
  `(s_X | s_Z)` stored in order `(s_Z | s_X)`, so the ordinary product `H . (a|b)^T` computes the
  symplectic inner products and `== 0` enforces pairwise commutation. X-first convention for
  `(a|b)`; symplectic IP of `(s_X|s_Z)` with `(a|b)` is `s_X . b + s_Z . a` = dot product of
  flipped row `(s_Z|s_X)` with `(a|b)`, dictating the row flip. For PBB this commutativity reduces
  to `A C^T + B D^T` symmetric over F2 (D3; supplemental l.690). Uses `3n` binary vars (one each
  for `a_i, b_i, w_i`) vs `n` for the CSS X-distance MILP; ~4x slower per logical on matched codes.
- **modality** SymbolicDerivation. dependencies: D3, D4, qldpc symplectic GE `[AXIOM]`.
  status: `[SOLID]`. Provenance: supplemental.tex l.678-691.

## D6. thm:ab_d2 — the A = B distance trap (d = 2 exactly)

- **context** app:ab_trap (paper.tex l.956-980). Theorem 1 ("Distance trap").
- **claim** `thm:ab_d2`: every BB code with `A = B` and `k > 0` has `d = 2` exactly.
- **evidence** (ExactProof, paper.tex l.964-969):
  1. For `A = B`, every X-stabilizer has the form `(A_r | A_r)`, so `rowspace(H_X)` is contained
     in the diagonal subspace `S := { (w, w) : w in F2^{l m} }`.
  2. The weight-2 vector `v_i := e_i + e_{i+l m} = (e_i, e_i)` lies in `S` and satisfies
     `H_Z v_i = A^T e_i + A^T e_i = 0`, so `v_i in ker(H_Z)`.
  3. `v_i` is an X-stabilizer IFF `e_i in rowspace(A)`; `k > 0` forces `rank(A) < l m`, so some
     `e_i` lies outside -> nontrivial weight-2 X-logical -> `d_X <= 2`.
  4. The same `v_i` satisfies `H_X v_i = 0` and is a Z-stabilizer IFF `e_i in colspace(A)`; again
     `rank(A) < l m` puts some `e_i` outside -> `d_Z <= 2`.
  5. Polynomials with `>= 2` terms force every column of `H_X, H_Z` to have weight `>= 2`, so
     `d >= 2`. Hence `d = 2`.
- **PBB extension** (paper.tex l.975-980): for PBB with `A = B`, the block-1 X-part is `[A | A]`,
  so the weight-2 Z-type operator `(0 | e_i + e_{i+l m})` has symplectic IP zero with every block-1
  stabilizer (X-part contributes `(A_r)_i + (A_r)_i = 0 mod 2`) and with every block-2 stabilizer
  (zero X-part). These `l m` operators lie in the normalizer `N(S)`. In the CSS case a counting
  argument shows `k/2` of them are nontrivial logicals. For PBB, perturbations `C, D` change the
  stabilizer group but preserve normalizer membership; whenever such an operator is not itself a
  stabilizer element (verified by MILP for all `A = B` PBB codes in the catalog) -> `d <= 2`;
  combined with `d >= 2`, gives `d = 2`.
- **modality** ExactProof (BB case); CSS-complete, PBB extension conditional on per-code MILP
  check (`[AXIOM]` for the catalog-wide MILP verification). Holds for any polynomial weight `>= 2`
  (l.973). Distinct from antipodal self-duality `B = A^T` of liang2025selfdual (which reaches
  `d` up to 16, l.972). dependencies: D1, D3. status: `[SOLID]`.
  Provenance: paper.tex l.959-980.

## D7. lem:crt_k — univariate encoding dimension k = 8 l / 3 (HGP equivalence)

- **context** app:crt (paper.tex l.985-1024). Theorem ("Univariate encoding dimension").
- **claim** `lem:crt_k`: let `l, m` be positive integers divisible by 3 and `c = l/3`. The BB code
  with `A(y) = 1 + y + y^2 in F2[y]/(y^m-1)` and `B(x) = A(x^c) in F2[x]/(x^l-1)` is a hypergraph
  product code encoding `k = 8 l / 3` logical qubits.
- **evidence** (ExactProof, paper.tex l.990-1023):
  - Circulants `H_A in F2^{m x m}`, `H_B in F2^{l x l}` for `A(y), B(x)`. BB checks (l.992-1002):

    ```
    H_X = ( I_l (x) H_A | H_B (x) I_m )
    H_Z = ( H_B^T (x) I_m | I_l (x) H_A^T )      ((x) = Kronecker product)
    ```

  - HGP checks `HGP(H_1, H_2)`, `H_1 in F2^{r1 x n1}`, `H_2 in F2^{r2 x n2}` (l.1004-1014):

    ```
    H_X^{HGP} = ( H_1 (x) I_{n2} | I_{r1} (x) H_2^T )
    H_Z^{HGP} = ( I_{n1} (x) H_2 | H_1^T (x) I_{r2} )
    ```

  - Choosing `H_1 = H_B`, `H_2 = H_A^T`, `r1 = n1 = l`, `r2 = n2 = m` gives an HGP code equivalent
    to the BB code with left/right qubit blocks swapped. Hence `BB(A,B) ~ HGP(H_B, H_A^T)`.
  - HGP dimension (tillich2014quantum): `HGP(H_1,H_2)` encodes `k = k_1 k_2 + k_1^T k_2^T`, where
    `k_i, k_i^T` are the dims of the codes from `H_i, H_i^T`.
  - Cyclic-code identity (macwilliams1977theory): for `N x N` circulant `H` from
    `f(z) in F2[z]/(z^N-1)`, `dim ker H = deg gcd(f, z^N - 1)` (eq. l.1016-1018). Transpose has
    the same kernel dim.
  - `(y-1) A(y) = y^3 - 1` and `y^3 - 1 | y^m - 1` when `3 | m`, so `A(y) | y^m - 1` ->
    `k_A = k_A^T = deg A = 2`. Likewise `(x^c - 1) B(x) = x^l - 1`, so `B(x) | x^l - 1` ->
    `k_B = k_B^T = deg B = 2c = 2 l / 3`.
  - Therefore (eq. l.1020-1023):

    ```
    k = k_1 k_2 + k_1^T k_2^T = k_B k_A^T + k_B^T k_A = 2 k_B k_A^T = 2 * (2l/3) * 2 = 8 l / 3.
    ```

- **modality** ExactProof (paper proof), conditional on two cited identities marked below.
  dependencies: D1; tillich2014quantum (HGP dim) `[AXIOM]`; macwilliams1977theory (cyclic kernel
  identity) `[AXIOM]`. status: `[SOLID]` (verified for 1680 combos `l m <= 250` per GROUND TRUTH).
  Provenance: paper.tex l.987-1024.

## D8. Tillich-Zemor distance minimum (univariate codes have d in {2,4})

- **context** sm:univariate (supplemental.tex l.249-250). MILP-exact computation reveals every
  univariate code has `d in {2, 4}`.
- **claim** (tillich-zemor) By the Tillich-Zemor formula

  ```
  d = min(d_1, d_2, d_1^T, d_2^T)
  ```

  the BB distance is bounded by the smallest distance among the four component cyclic codes
  `ker H_A, ker H_B, ker H_A^T, ker H_B^T`. For palindromic check polynomials (as here),
  `H^T = H`, so the four-way min collapses to `min(d_A, d_B)`.
- **evidence** Low-weight quotients `(y^m - 1)/A` or `(x^l - 1)/B` force this min to be small
  (typically 2 or 4); the ODD weight of trinomial check polynomials forces all four component
  distances to be even, ruling out `d = 3`. Consequence: univariate FOM collapse — top-ranked code
  drops `FOM_BP = 64.0 -> FOM_MILP = 0.4` (supplemental l.252).
- **modality** LiteratureGrounded. The distance formula itself is CITED (tillich2014quantum) ->
  treat as `[AXIOM]`. dependencies: D7 (HGP/univariate structure), tillich2014quantum `[AXIOM]`.
  status: `[SOLID]` (MILP-confirmed `d in {2,4}` for all univariate codes).
  Provenance: supplemental.tex l.249-250.

## D9. Figure of merit FOM = k d^2 / n

- **context** sec:fom (paper.tex l.198-203).
- **claim** `FOM = k d^2 / n`. Gross code `code{144,12,12}` has `FOM = 12 * 144 / 144 = 12`.
- **evidence** Motivated by the Bravyi-Poulin-Terhal (BPT) bound `k d^2 = O(n)` (bravyi2010tradeoffs)
  and standard in the BB literature (bravyi2024high, liang2025generalized). The BPT bound applies
  to geometrically 2D-local stabilizer codes, so for 2D-local qLDPC codes FOM is bounded above by a
  constant as `n` grows; for general qLDPC codes it is not (rotated surface code FOM = 1 vs gross
  code FOM = 12). Used as a benchmark for comparing BB codes against each other. Highest-FOM prior
  CSS BB: `FOM = 12.0` (`code{144,12,12}`) and `FOM <= 19.2` (`code{360,12,<=24}`, weight-6 CSS).
- **modality** LiteratureGrounded (definitional). dependencies: D2 (`k`), distance `d`,
  bravyi2010tradeoffs (BPT) `[AXIOM]`. status: `[SOLID]`. Provenance: paper.tex l.201-203.

---

## Open markers

- `[AXIOM]` tillich2014quantum (HGP dimension formula D7; Tillich-Zemor distance D8) — cited,
  not reproduced. Final univariate `d in {2,4}` and `k = 8l/3` results remain conditional on it.
- `[AXIOM]` macwilliams1977theory (cyclic-code kernel identity `dim ker H = deg gcd(f, z^N-1)`, D7).
- `[AXIOM]` bravyi2010tradeoffs (BPT bound `k d^2 = O(n)`, D9 motivation).
- `[AXIOM]` HiGHS / scipy.optimize.milp (D4, D5) — MILP exactness depends on the solver reporting
  MIP gap = 0; incumbent solutions are only upper bounds otherwise.
- `[AXIOM]` qldpc symplectic Gaussian elimination (D5) — source of logical reps `Lbar_j`.
- `[AXIOM]` (catalog-wide) MILP verification that each `A = B` PBB weight-2 normalizer operator is
  not a stabilizer element (D6 PBB extension) — `d <= 2` for PBB rests on this per-code check.
- `[FUTURE]` D6 PBB extension states `k/2` of the weight-2 operators are nontrivial CSS logicals
  via "a direct counting argument" that the tex does not write out; the BB (CSS) case is fully
  proven, the PBB exact count is deferred to per-code MILP.
