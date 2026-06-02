# Convention / Notation — arXiv:2606.02418

Source: arXiv:2606.02418 "Evolutionary Discovery of Bivariate Bicycle Codes with LLM-Guided Search" (Cruz-Benito, Cross, Kremer, Faro; IBM Research; PRX Quantum).
tex: `paper.tex` (1091 lines), `supplemental.tex` (715 lines). Default modality `LiteratureGrounded` unless a proof is present.

Each row is a TYPED entry: `symbol -> one-line meaning [modality] (tex anchor)`. Tex labels are preserved VERBATIM. Status markers per `_common/markers.md`.

## 1. Algebraic ground objects

| symbol | one-line meaning | modality | tex anchor |
|---|---|---|---|
| `l` (`\ell`) | first cyclic factor size; the variable `x` has order `l`, i.e. `x^l - 1` is a relation of `R`. | LiteratureGrounded | paper l.158 |
| `m` | second cyclic factor size; the variable `y` has order `m`, i.e. `y^m - 1` is a relation of `R`. | LiteratureGrounded | paper l.158 |
| `(l,m)` | a "lattice"; one choice of cyclic factor sizes. Lattice set used: `(12,6),(6,12),(12,12),(24,6),(15,12),(30,6),(16,9),(18,8)` (Stage 2). | LiteratureGrounded | paper l.249 |
| `R` | quotient polynomial ring `R = F_2[x,y]/(x^l-1, y^m-1)`; commutative over `F_2`. All polynomials `A,B,C,D` live here. | LiteratureGrounded | paper l.158 |
| `x`, `y` | the two commuting cyclic generators (orders `l`, `m`); a monomial `x^a y^b` is a cyclic shift on the `Z_l x Z_m` group. | LiteratureGrounded | paper l.71, l.168 |
| `F_2` (`\FF_2`) | the binary field GF(2); all matrix ranks, kernels and arithmetic are over `F_2`. | LiteratureGrounded | paper l.166 |
| `^T` / `A^top` | matrix transpose of the circulant; equivalently the ring involution `x -> x^{-1}, y -> y^{-1}` applied to the polynomial. | LiteratureGrounded | paper l.164 |
| circulant | an `lm x lm` matrix that is the regular representation of a ring element of `R`; `A`, `B` are circulants. Polynomial multiplication = matrix product. | LiteratureGrounded | paper l.164 |
| trinomial | a weight-3 polynomial (exactly 3 monomial terms); the BB search space for Campaigns 1-3. Yields weight-6 stabilizers. | LiteratureGrounded | paper l.158, l.165 |

## 2. Code-defining polynomials and matrices

| symbol | one-line meaning | modality | tex anchor |
|---|---|---|---|
| `A`, `B` | the two BB-defining polynomials in `R` (CSS case); circulants of size `lm x lm`. | LiteratureGrounded | paper l.158, l.164 |
| `C`, `D` | the two PBB perturbation polynomials in `R`; augment the X-block with Z-type support. `C=D=0` reduces PBB to CSS BB. | LiteratureGrounded | paper l.173, l.183 |
| `H_X` | CSS X-type parity-check matrix `H_X = (A | B)`. | LiteratureGrounded | paper l.161 (eq.) |
| `H_Z` | CSS Z-type parity-check matrix `H_Z = (B^T | A^T)`. | LiteratureGrounded | paper l.162 (eq.) |
| `H` (PBB) | non-CSS stabilizer matrix `H = [[A,B,C,D],[0,0,B^T,A^T]]`; block-1 row = mixed X(A,B)+Z(C,D), block-2 row = pure Z. | LiteratureGrounded | paper l.176 (eq.) |
| `H = (X | Z)` | standard symplectic representation: first `lm` columns = X-support, second `lm` columns = Z-support of a row/operator. | LiteratureGrounded | paper l.179 |
| `(a | b)` | symplectic vector of a Pauli on `n` qubits in `F_2^{2n}`; `a_i` = X-content, `b_i` = Z-content on qubit `i` (X-first convention). | LiteratureGrounded | supp l.678, l.690 |
| `e_i` | `i`-th standard basis vector of `F_2^{lm}` (used in the `A=B` distance-trap proof). | SymbolicDerivation | paper l.966 |
| `v_i` | weight-2 vector `v_i = e_i + e_{i+lm} = (e_i, e_i)` in the diagonal subspace `S` (`A=B` proof). | SymbolicDerivation | paper l.966 |

## 3. Code parameters

| symbol | one-line meaning | modality | tex anchor |
|---|---|---|---|
| `[[n,k,d]]` | DOUBLE-bracket = QUANTUM stabilizer code parameters (qubits, logical qubits, distance); macro `\code{#1}` renders `[[#1]]`. Single brackets `[n,k,d]` would be classical — this paper uses double throughout. | LiteratureGrounded | paper l.26 (macro), l.167 |
| `n` | number of physical qubits; `n = 2*l*m` for BB and PBB codes. | LiteratureGrounded | paper l.167 |
| `k` | number of logical qubits; `k = 2lm - 2*rank_{F2}(H_X)` (CSS). | SymbolicDerivation | paper l.167 |
| `d` | minimum weight of a nontrivial logical operator; for non-CSS PBB, measured in SYMPLECTIC weight. `d = min(d_X, d_Z)`. | LiteratureGrounded | paper l.167; supp l.670, l.680 |
| `d_X`, `d_Z` | X-type / Z-type minimum logical weights; for BB `d_X = d_Z` (involution exchanges `H_X, H_Z`). | SymbolicDerivation | supp l.670, l.674 |
| `<=d` (e.g. `[[360,12,<=24]]`) | distance is an incumbent MILP UPPER bound, not proven exact (MIP gap > 0). | LiteratureGrounded | supp l.75 |
| `FOM` | figure of merit `FOM = k d^2 / n`; benchmark for comparing BB codes. Gross code `[[144,12,12]]` has `FOM = 12`; rotated surface code `FOM = 1`. Motivated by BPT bound `kd^2 = O(n)`. | LiteratureGrounded | paper l.201-202 |
| `d/sqrt(n)` trust | trust filter on the distance estimate: `<= 1.3` fully trusted, `>= 2.0` discarded, linear interpolation between. Operates on (unreliable) BP-OSD estimates; Campaign 5 bypasses it. | LiteratureGrounded | paper l.369-371 |
| `k/n` | encoding rate; BP-OSD overestimates distance for high-rate codes (`k/n > 0.1`). | LiteratureGrounded | paper l.90; supp l.85 |
| `p`, `p_L` | physical error rate `p`; per-logical-qubit error rate `p_L = 1-(1-LER)^{1/k}`. | LiteratureGrounded | supp l.448 |
| `LER` | block logical error rate (code-capacity simulation). | LiteratureGrounded | supp l.420 |

## 4. CSS / commutativity conditions

| symbol | one-line meaning | modality | tex anchor |
|---|---|---|---|
| css-commute | CSS condition `H_X H_Z^T = AB + BA = 0` over `F_2`; follows automatically from commutativity of `R`. | SymbolicDerivation | paper l.166 |
| pbb-commute | PBB rows commute IFF `(A C^T + B D^T) mod 2` is symmetric over `F_2`; the only nontrivial condition (block-1/block-2 commutativity is automatic). Must be checked per 4-tuple. | SymbolicDerivation | paper l.180; supp l.690 |
| `S` (diagonal subspace) | `S := {(w,w) : w in F_2^{lm}}`; rowspace(`H_X`) lies in `S` when `A=B`. | SymbolicDerivation | paper l.965 |
| `N(S)` | normalizer of the stabilizer group; weight-2 operators landing in `N(S)` but not in the stabilizer are nontrivial logicals (`A=B` PBB argument). | SymbolicDerivation | paper l.977-979 |

## 5. Structural families / ansatz patterns

| symbol | one-line meaning | modality | tex anchor |
|---|---|---|---|
| univariate / UV / HGP | `A = f(y)`, `B = g(x)` (or vice versa); equals the hypergraph product (HGP) of two low-distance cyclic codes; ALL have `d in {2,4}`. | LiteratureGrounded | paper l.79; supp l.57, l.249 |
| `x/y`-swap / XY | polynomials mixing both cyclic variables, e.g. `A = x^a + y^b + y^c`; the family reaching `d=12` but limited to `k <= 24`. | LiteratureGrounded | paper l.80; supp l.57 |
| `A = B` / SD | identical-polynomial trap; always gives `d=2` (thm:ab_d2). NOTE: distinct from "self-dual" `C subset C^perp`; SD here = "same" not self-dual. | LiteratureGrounded | paper l.205-211; supp l.57 |
| `B = A^T` (antipodal self-dual) | DIFFERENT condition from `A=B`: antipodal self-duality (cross-ref liang2025selfdual); such codes can have `d` up to 16. Do NOT conflate with the `A=B` trap. | LiteratureGrounded | paper l.972 |
| mixed-monomial / MX | polynomial with a term `x^a y^b`, `a,b > 0` (both `x` and `y` present); Campaign 4 family; weight-6 (trinomial) or weight-8+ (4-6 terms). | LiteratureGrounded | paper l.76, l.443; supp l.57 |
| diagonal-mixed / DM | subfamily with `1 + x^a y^a + x^b y^b` (equal `x,y` exponents in each mixed term), weight-6. | LiteratureGrounded | paper l.443; supp l.57 |
| weight-6 / weight-8 | max stabilizer (check) weight = nonzero entries per row of `H_X`/`H_Z`; trinomials -> weight-6, 4-term -> weight-8. | LiteratureGrounded | paper l.165, l.543 |
| PBB | perturbed bivariate bicycle: non-CSS 4-tuple `(A,B,C,D)` construction; reduces to CSS when `C=D=0`. | LiteratureGrounded | paper l.85, l.170-183 |
| decomposable | code whose Tanner graph (`H_X + H_Z` combined) disconnects into independent sub-codes -> a direct sum; e.g. `[[288,24,12]] = [[144,12,12]] + [[144,12,12]]`. | SymbolicDerivation | paper l.80, l.426-427 |
| gross code | the reference `[[144,12,12]]` BB code of bravyi2024high; `FOM=12`, pseudo-threshold ~0.7%. | LiteratureGrounded | paper l.66 |

## 6. Verification: decoders and solvers

| symbol | one-line meaning | modality | tex anchor |
|---|---|---|---|
| BP-OSD | belief-propagation + ordered-statistics decoding (`ldpc` lib); produces stochastic distance UPPER bounds; overestimates up to 12x for high-rate codes; multi-decoder 150k-trial protocol. | LiteratureGrounded | paper l.90, l.307; supp l.54 |
| `d_BP` | BP-OSD distance estimate (an upper bound, often inflated). | LiteratureGrounded | supp l.121, l.262 |
| OSD0 (`OSD_0`) | OSD order-0 configuration; weakest OSD setting; found global min for only 31.8% of Campaigns 1-3 representations. | LiteratureGrounded | supp l.85-86 |
| OSD-CS10 (`OSD-CS_{10}`) | OSD combination-sweep order 10; outperforms `OSD_0`, especially at high rate (`k/n > 15%`); reaches up to 64.9% global-min hit rate. | LiteratureGrounded | supp l.85-86, l.122 |
| OSD-CS order 7 | OSD combination-sweep order 7, 20 BP iterations, product-sum — the code-capacity simulation decoder config. | LiteratureGrounded | paper l.635; supp l.329 |
| MILP | mixed-integer linear program for EXACT distance; `min sum x_i` s.t. logical constraints; solved by HiGHS via `scipy.optimize.milp`. | LiteratureGrounded | paper l.319; supp l.656-672 |
| MILP CSS obj | `eq:milp_obj` = `min sum_{i=1}^n x_i`; `eq:milp_commute` = `H_Z x = 0 (mod 2)`; `eq:milp_anticommute` = `<x, Zbar_j> = 1 (mod 2)`; `eq:milp_binary` = `x_i in {0,1}`. | SymbolicDerivation | supp l.663-666 |
| `Zbar_j` | `j`-th independent Z-logical operator (CSS MILP target — find min-weight X-logical anticommuting with it). | LiteratureGrounded | supp l.668 |
| `Lbar_j` (`\bar{L}_j`) | `j`-th independent logical Pauli (symplectic vector in `F_2^{2n}`) for the non-CSS MILP. | LiteratureGrounded | supp l.679 |
| mod-2 linearization | each `sum a_i x_i = b (mod 2)` replaced by `sum a_i x_i - 2s = b` with integer slack `s >= 0`. | SymbolicDerivation | supp l.669 |
| `w_i = a_i OR b_i` | symplectic-weight indicator; enforced by `w_i >= a_i`, `w_i >= b_i`, `w_i <= a_i + b_i`; non-CSS MILP uses `3n` binary vars (`a_i,b_i,w_i`), ~4x slower than CSS. | SymbolicDerivation | supp l.686-691 |
| row-flip `(s_Z | s_X)` | symplectic-flipped stabilizer row ordering so ordinary matrix-vector product computes symplectic inner products (X-first vector convention). | SymbolicDerivation | supp l.689-690 |
| MIP gap | optimality gap reported by HiGHS; `MIP gap = 0` => solution proven optimal (distance EXACT); `> 0` => incumbent is an upper bound only (`<=d`). | LiteratureGrounded | supp l.673 |
| `<.,.>_symp` | symplectic inner product of two `F_2^{2n}` vectors. | LiteratureGrounded | supp l.679 |
| HiGHS | the MILP solver (open-source) invoked through `scipy.optimize.milp`. | LiteratureGrounded | supp l.672 |

## 7. Equivalence / deduplication

| symbol | one-line meaning | modality | tex anchor |
|---|---|---|---|
| BLISS | canonical-labeling algorithm (via `python-igraph`) on a COLORED Tanner graph; declares two codes permutation-equivalent iff canonical forms match. Dedup: 225 CSS reps -> 97 distinct; 720 PBB tuples -> 368 distinct. | LiteratureGrounded | paper l.383, l.386, l.388 |
| colored Tanner graph | CSS: 3 vertex colors (qubits, X-checks, Z-checks). non-CSS: per-stabilizer X-support and Z-support vertices tied by an edge -> 3 colors (qubits, stabilizer-X-support, stabilizer-Z-support). | LiteratureGrounded | paper l.383, l.386 |
| distinct | colored Tanner graphs have non-isomorphic BLISS canonical forms; sound and complete for permutation equivalence under the coloring. | LiteratureGrounded | paper l.388 |
| LC / local Clifford | per-qubit single-qubit Clifford conjugation; LC-CSS equivalence test (App E) using 6 coset reps `{I,S,H,HS,SH,HSH}`. Result: 11/368 PBB are CSS-equivalent (10 Hadamard, 1 uniform-S `[[36,4,6]]`); 357 CSS-inequivalent. | LiteratureGrounded | paper l.185-193 |
| Hadamard equivalence | parity 2-coloring test: generators become pure-X/pure-Z under some single-qubit-`H` pattern `H_J` iff no `Y` support and constraint graph is bipartite (inspired by khesin2026mirror, proved directly). | LiteratureGrounded | paper l.189-190 |
| `H_J` | the per-qubit Hadamard pattern (weight `n/2`) that renders every stabilizer pure-X or pure-Z. | LiteratureGrounded | paper l.189-190 |

## 8. Search / evolution machinery

| symbol | one-line meaning | modality | tex anchor |
|---|---|---|---|
| ansatz / generator ansatz | an evolved Python program `G(l,m) -> {(A_i,B_i)}` (or 4-tuples `(A_i,B_i,C_i,D_i)`) producing candidate polynomial tuples for any lattice; NOT a single code (no a priori validity guarantee). | LiteratureGrounded | paper l.73, l.221 |
| `G(l,m)` | the generator-ansatz function evaluated at lattice `(l,m)`. | LiteratureGrounded | paper l.221, l.235 |
| MAP-Elites | quality-diversity archive (OpenEvolve); behavioral dims (Campaigns 1-3,5): (i) #lattices with a `k>=8` code, (ii) total count of such codes. Campaign 4 swaps dims to polynomial-term-count + monomial structure. | LiteratureGrounded | paper l.220, l.226, l.228 |
| island | a sub-population in the distributed MAP-Elites search; 4-6 islands with migration every 12-25 iterations. | LiteratureGrounded | paper l.226 |
| migration | periodic exchange of individuals between islands (every 12-25 iterations). | LiteratureGrounded | paper l.226 |
| code diff | a targeted LLM-proposed modification to the generator ansatz (exponent tweak, new strategy branch, control-flow change) — not a full rewrite. | LiteratureGrounded | paper l.224 |
| cascade Stage 1 | ~2s; `k`-only via `F_2` rank on small lattices `(6,6)`,`(12,6)`; discards ~30% of mutants with no `k>0` code. | LiteratureGrounded | paper l.247 |
| cascade Stage 2 | ~30-60s; BP-OSD distance estimate on 8 lattices `{(12,6),(6,12),(12,12),(24,6),(15,12),(30,6),(16,9),(18,8)}`. | LiteratureGrounded | paper l.249-250 |
| cascade Stage 3 | MILP exact distance; in-loop for Campaigns 4-5, post-hoc for Campaigns 1-3. | LiteratureGrounded | paper l.237-238, l.251 |
| Campaign 1-5 | C1 Flash (100 it, pop 100, 9 codes); C2 ensemble (251, 100, 0); C3 ensemble (500, 1000, 145); C4 ensemble (300, 750, 45 mixed-monomial wt8); C5 PBB (500, 200, 368). ~1650 iters total. | LiteratureGrounded | paper l.292-296 (Table) |

## 9. Theorems / cited results (proof targets)

| label | one-line meaning | modality / status | tex anchor |
|---|---|---|---|
| `thm:ab_d2` | "Distance trap": every BB code with `A=B` and `k>0` has `d=2` exactly. Proof via diagonal subspace `S`; extends to PBB. | ExactProof / [SOLID] | paper l.959-980 |
| `lem:crt_k` | "Univariate encoding dimension": `A(y)=1+y+y^2`, `B(x)=A(x^c)`, `c=l/3`, `3|l`, `3|m` => `k = 8l/3` (an HGP code). Verified for 1680 combos `lm<=250`. | ExactProof / [SOLID] | paper l.985-1024; paper l.421 |
| `eq:milp_obj` | the CSS MILP objective `min sum_{i=1}^n x_i`. | SymbolicDerivation | supp l.663 |
| `eq:milp_commute` / `eq:milp_anticommute` / `eq:milp_binary` | CSS MILP constraints (commute with `H_Z`; anticommute with `Zbar_j`; binary). | SymbolicDerivation | supp l.664-666 |
| tillich-zemor (HGP distance) | `d = min(d_1, d_2, d_1^T, d_2^T)`; univariate BB codes collapse to `d in {2,4}`. CITED, not reproduced. | LiteratureGrounded / [AXIOM] | paper l.79; supp l.250 |
| BPT bound | `k d^2 = O(n)` for 2D-local stabilizer codes; motivates the FOM. CITED. | LiteratureGrounded / [AXIOM] | paper l.201 |

## 10. Key disambiguations (load-bearing)

- `[[n,k,d]]` double brackets = quantum code. `\code{144,12,12}` macro renders `[[144,12,12]]`. (paper l.26)
- `A = B` (SD pattern, "identical polynomials") is the `d=2` distance trap (thm:ab_d2) and is NOT the antipodal self-duality `B = A^T` of liang2025selfdual (which can reach `d=16`). These are different conditions; do not conflate. (paper l.972)
- `^T` / `A^T` = the ring involution `x->x^{-1}, y->y^{-1}` = transpose of the circulant. (paper l.164)
- MILP `MIP gap = 0` => `d` exact; otherwise `d` printed as `<=d` (incumbent upper bound). (supp l.673)
- BP-OSD distances are UPPER bounds only; "trusted" via `d/sqrt(n)`, never treated as exact. (paper l.369; supp l.54)
</content>
</invoke>
