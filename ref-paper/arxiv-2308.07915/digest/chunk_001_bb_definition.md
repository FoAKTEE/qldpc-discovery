# Chunk 001 — BB Code Definition Digest (arXiv_v2.tex, Main results → Lemmas)

> Pipeline-0 (source-import) chunk digest. Every entry below is a TYPED ledger
> object (context · claim · modality · dependencies · status marker). Default
> modality `LiteratureGrounded` (evidence = tex section); proofs/derivations present
> in this chunk are marked separately. Tex labels and equations preserved VERBATIM.
> Cited-but-not-reproduced results are `[AXIOM]`. Open obligations are
> `[HOLE]`/`[FUTURE]`/`[BLOCKING]`. Risk tiers R0–R4 per `code_quality_policy.md`.
> This is the FOUNDATIONAL paper (`bravyi2024high`) that defines BB codes; the mission
> paper arXiv:2606.02418 builds on it (its `ax:bb-construction` is REPLACED-BY this paper).

---

## 0. Provenance

| Field | Value |
|---|---|
| Paper | arXiv:2308.07915 "High-threshold and low-overhead fault-tolerant quantum memory" |
| Authors | Bravyi, Cross, Gambetta, Maslov, Rall, Yoder (IBM) |
| Venue | Nature 627, 778–782 (2024) |
| Source file | `ref-paper/arxiv-2308.07915/src/arXiv_v2.tex` (1368 lines total) |
| Chunk range | lines 308–888 |
| Sections covered | `sec:results` "Main results" (l.308); `sec:codedefinition` "Bivariate Bicycle quantum LDPC codes" (l.508) incl. matrix/ring setup (l.510–522), BB definition eqs `AB`/`HXHZ` (l.524–544), parameter formula (l.546–554), notation Table (l.561–584), `tab:codes` (l.587–644), `lem:kd` (l.666–676 + proof l.677–749), monomial/`q(T,\alpha)` labeling (l.757), `lem:thickness` (l.775–780 + proof l.781–833), `lem:connected` (l.843–845 + proof l.846–853), toric-layout `\begin{dfn}` (l.857–859) + `lem:toric_layout` (l.863–869 + proof l.870–872), worked toric-layout examples (l.874–883). `\input{supplemental_v2.tex}` at l.886. |
| Forward refs (NOT in this chunk) | `sec:syndrome_circuit` (depth-7 CNOT), `sec:decoder` (BP-OSD), `sec:numerics`, `sec:logicals` (logical memory / load-store), `sec:conclusions` (l.888); figures `fig:2Dlayout`, `fig:wheel_extraction`, `fig:navigation` (images, not text). Distance computation method `landahl2011fault` (MILP) is cited not reproduced here. |

---

## 1. Verbatim named constructions / definitions / claims

Each labeled with section anchor + tex line(s). Equations quoted VERBATIM (tex
labels preserved). All matrix arithmetic is over `\FF_2` (mod 2) unless noted.

### D1 — Generator matrices `x`, `y` over the cyclic-group ring [`sec:codedefinition`, l.510–522]
- `I_\ell`, `S_\ell` = identity and cyclic shift matrix of size `\ell\times\ell`; "The `i`-th row of `S_\ell` has a single nonzero entry equal to one at the column `i+1 (mod \ell)`."
- `x = S_\ell \otimes I_m` and `y = I_\ell \otimes S_m` (l.520). Relations (l.522): "`xy=yx` and `x^\ell = y^m = I_{\ell m}`." (Equivalent to working in `R = \FF_2[x,y]/(x^\ell-1, y^m-1)` — the ring presentation arXiv:2606.02418 uses.)

### D2 — BB code definition: `A`, `B`, ring polynomials [`sec:codedefinition`, l.523–530, eq `AB`]
- VERBATIM (l.524–527): `A = A_1 + A_2 + A_3` and `B = B_1 + B_2 + B_3`, "where each matrix `A_i` and `B_j` is a power of `x` or `y`."
- "Thus, we also assume the `A_i` are distinct and the `B_j` are distinct to avoid cancellation of terms." (l.528) — so generically `A`, `B` are weight-3 trinomials.
- Worked example (l.529): `A = x^3 + y + y^2` and `B = y^3 + x + x^2`.
- "Note that `A` and `B` have exactly three non-zero entries in each row and each column. Furthermore, `AB = BA` since `xy = yx`." (l.530)

### D3 — Check matrices `H^X`, `H^Z` [`sec:codedefinition`, l.531–544, eq `HXHZ`]
- VERBATIM (l.535–538): code denoted `\qc`, length `n = 2\ell m`, with
  `H^X = [A | B]` and `H^Z = [B^T | A^T]`.
- "Both matrices `H^X` and `H^Z` have size `(n/2) \times n`." (l.541)
- Each row `v\in\FF_2^n` of `H^X` (resp. `H^Z`) defines `X(v)=\prod_j X_j^{v_j}` (resp. `Z(v)=\prod_j Z_j^{v_j}`) (l.542–543).
- CSS commutativity (l.544): "Any X-check and Z-check commute since they overlap on even number of qubits (note that `H^X (H^Z)^T = AB + BA = 0 (mod 2)`)."
- "the code `\qc` can be viewed as a special case of the Lifted Product construction [`panteleev2021quantum`] based on the abelian group `\ZZ_\ell \times \ZZ_m`." (l.555–557)

### D4 — Code parameters `[[n,k,d]]` [`sec:codedefinition`, l.546–554; restated as `lem:kd`]
- VERBATIM (l.547–552): `n = 2\ell m`, `k = 2\cdot\mathrm{dim}(\ker{A}\cap\ker{B})`, `d = \min\{|v| : v\in\ker{H^X}\setminus\rs{H^Z}\}`.
- `|v| = \sum_{i=1}^n v_i` = Hamming weight (l.554). Notation Table (l.561–584): `\rs{H}` row space, `\cs{H}` column space, `\ker{H}` nullspace, `\rk{H}=\dim(\rs{H})=\dim(\cs{H})`, over `\FF_2=\{0,1\}`.
- (Note: arXiv:2606.02418's `k = 2\ell m - 2\,\mathrm{rank}(H_X)` is the equivalent rank form; `lem:kd` proof l.680 gives `k = n - \rk{H^X} - \rk{H^Z}` then `\rk{H^X}=\rk{H^Z}` ⇒ same.)

### L1 — Lemma `lem:kd` (parameters + equal X/Z distance) [`sec:codedefinition`, l.666–676; PROOF l.677–749]
- STATEMENT (verbatim, l.668–675): the code `\qc` has parameters `[[n,k,d]]` with `n=2\ell m`, `k = 2\cdot\mathrm{dim}(\ker{A}\cap\ker{B})`, `d = \min\{|v| : v\in\ker{H^X}\setminus\rs{H^Z}\}`. "The code offers equal distance for `X`-type and `Z`-type errors."
- PROOF PRESENT (l.677–749). Key construction: self-inverse permutation `C_\ell` with `i`-th column nonzero at row `j=-i (mod \ell)`, `C = C_\ell\otimes C_m`; since `C_\ell S_\ell C_\ell = S_\ell^T`, `C_m S_m C_m = S_m^T` one gets (eq `ABC2`, l.687–688) `A^T = CAC` and `B^T = CBC`. Hence `H^Z = C H^X [[0,C],[C,0]]`, an invertible left/right multiplication ⇒ `\rk{H^X}=\rk{H^Z}`, giving `k = 2\dim(\ker A\cap\ker B)`.
- `d^X = d^Z`: cites `steane1996multiple`,`calderbank1996good` for `d=\min(d^X,d^Z)` with `d^X=\min\{|v|:v\in\ker H^Z\setminus\rs H^X\}`, `d^Z=\min\{|v|:v\in\ker H^X\setminus\rs H^Z\}`; then an explicit involution `e=(C\delta,C\gamma)`, `h=(C\beta,C\alpha)` maps a min-weight `X`-logical to a `Z`-logical of equal weight (l.713–748), so `d^Z\le d^X` and symmetrically `d^X\le d^Z`. Also noted (l.751–754): `d^X=d^Z` follows from the Lifted Product machinery of `panteleev2021quantum`.

### L2 — Lemma `lem:thickness` (Tanner graph thickness ≤ 2) [`sec:codedefinition`, l.775–780; PROOF l.781–833]
- STATEMENT (verbatim, l.777–779): "The Tanner graph `G` of the code `\qc` has thickness `\theta\le 2`. A decomposition of `G` into two planar layers can be computed in time `O(n)`. Each planar layer of `G` is a degree-3 graph."
- PROOF PRESENT (l.781–833, constructive, `O(n)`). Splits `G` into `G_A`, `G_B` with check matrices (verbatim l.785–790):
  - `G_A`: `H^X_A = [A_2+A_3 | B_3]`, `H^Z_A = [B_3^T | A_2^T+A_3^T]`.
  - `G_B`: `H^X_B = [A_1 | B_1+B_2]`, `H^Z_B = [B_1^T+B_2^T | A_1^T]`.
  Each is degree-3; each connected component is a planar "wheel graph" (two length-`p` cycles + `p` radial edges). Worked: for `[[144,12,12]]`, `A=x^3+y+y^2`, `A_2=y`, `A_3=y^2` ⇒ `A_3 A_2^T = y^2 y^{-1} = y` of order `m=6` (l.815–817). Commutativity of `A_i`,`B_j` makes the 4-cycles `(B_3,A_2,B_3^T,A_2^T)` and `(B_3^T,A_3,B_3,A_3^T)` close ⇒ well defined ⇒ planar.
- Empirical side-note (l.835–839): "BB codes reported in `\tab{codes}` have no weight-4 stabilizers" (relevant to BP decoder performance; cites `panteleev2021degenerate`).

### L3 — Lemma `lem:connected` (Tanner-graph connectivity criterion) [`sec:codedefinition`, l.843–845; PROOF l.846–853]
- STATEMENT (verbatim, l.844): "The Tanner graph of the code `\qc` is connected if and only if `S = {A_iA_j^T : i,j\in{1,2,3}} \cup {B_iB_j^T : i,j\in{1,2,3}}` generates the group `\mathcal{M}`. The number of connected components in the Tanner graph is `\ell m / |\langle S\rangle|`, and all components are graph isomorphic to one another."
- PROOF PRESENT (l.846–853). Uses length-2 paths `L`-qubit `\alpha \to A_iA_j^T\alpha` (through `X`-check) and `\to B_iB_j^T\alpha` (through `Z`-check); components are labeled by cosets of `\langle S\rangle`.
- Context (l.841): some `A,B` give a separable / disconnected code; e.g. any `\tab{codes}` code with even `\ell` and `x\to x^2` yields two components.

### DEF1 — Toric layout definition [`sec:codedefinition`, `\begin{dfn}` l.857–859]
- Terminology (l.855): undirected Cayley graph of finite abelian `\mathcal{G}` (identity `0`) generated by `S` has vertices `\mathcal{G}`, edges `(g,g+s)`; "the Cayley graph of `\ZZ_a\times\ZZ_b`" defaults to generators `{(1,0),(0,1)}`; order `\ord{g}` = smallest `k>0` with `g^k=1`.
- DEFINITION (verbatim, l.858): "Code `\qc` is said to have a toric layout if its Tanner graph has a spanning sub-graph isomorphic to the Cayley graph of `\ZZ_{2\mu}\times\ZZ_{2\lambda}` for some integers `\mu` and `\lambda`." Only connected-Tanner codes can have one (l.861).

### L4 — Lemma `lem:toric_layout` (sufficient condition for toric layout) [`sec:codedefinition`, l.863–869; PROOF l.870–872]
- STATEMENT (verbatim, l.864–868): "A code `\qc` has a toric layout if there exist `i,j,g,h\in{1,2,3}` such that (i) `\langle A_iA_j^T, B_gB_h^T\rangle = \mathcal{M}` and (ii) `\ord{A_iA_j^T}\,\ord{B_gB_h^T} = \ell m`."
- PROOF PRESENT (l.870–872, constructive). `\mu=\ord{A_iA_j^T}`, `\lambda=\ord{B_gB_h^T}`; associate `L`-qubit `\alpha=(A_iA_j^T)^a(B_gB_h^T)^b \to (2a,2b)`, `R`-qubit `\alpha A_j^T B_g \to (2a+1,2b+1)`, `X`-check `\alpha A_j^T \to (2a+1,2b)`, `Z`-check `\alpha B_g \to (2a,2b+1)` in `\mathcal{G}=\ZZ_{2\mu}\times\ZZ_{2\lambda}`; uniqueness from (ii) + pigeonhole.
- Application notes (l.874–883): All `\tab{codes}` codes have a toric layout with `\mu=m`, `\lambda=\ell`; most via `i=g=2`, `j=h=3`; exception `[[90,8,10]]` uses `i=2,g=1,j=h=3`. Counterexamples: `[[784,24,\le24]]` (`\ell,m=28,14`, `A=x^{26}+y^6+y^8`, `B=y^7+x^9+x^{20}`) is connected but has NO toric layout; `[[432,4,\le22]]` (`\ell,m=18,12`, `A=x+y^{11}+y^3`, `B=y^2+x^{15}+x`) needs `\mu,\lambda=36,6` (so `{\ord{},\ord{}} \ne {\ell,m}`).

### DLAB — Monomial / unified `q(T,\alpha)` labeling [`sec:codedefinition`, l.757]
- Data qubits partitioned `[n]=LR`, `|L|=|R|=n/2=\ell m`. Monomials `\mathcal{M}={1,y,\dots,y^{m-1},x,xy,\dots,x^{\ell-1}y^{m-1}}`; index `i\in\ZZ_{\ell m}` ↔ `x^{a_i}y^{i-ma_i}`, `a_i=\lfloor i/m\rfloor`.
- `L`-qubit `\alpha` is in `X`-checks `A_i^T\alpha` and `Z`-checks `B_i\alpha`; `R`-qubit `\beta` in `X`-checks `B_i^T\beta`, `Z`-checks `A_i\beta` (`i=1,2,3`). Unified label `q(T,\alpha)`, `T\in{L,R,X,Z}`. (Used heavily by arXiv:2606.02418 and the logical-operator/automorphism sections in the supplemental.)

---

## 2. The gross code and the code table (`tab:codes`) — VERBATIM [l.587–644]

Check matrices for every row: `H^X = [A|B]`, `H^Z = [B^T|A^T]`, with `x^\ell=y^m=1`,
`xy=yx`. Distance computed by MILP of Ref. `landahl2011fault` (l.636). `\le d` = upper
bound only. The **gross code `[[144,12,12]]`** is the landmark this knowledge base verifies.

| `[[n,k,d]]` | rate `r` | `\ell,m` | `A` | `B` |
|---|---|---|---|---|
| `[[72,12,6]]` | 1/12 | 6,6 | `x^3+y+y^2` | `y^3+x+x^2` |
| `[[90,8,10]]` | 1/23 | 15,3 | `x^9+y+y^2` | `1+x^2+x^7` |
| `[[108,8,10]]` | 1/27 | 9,6 | `x^3+y+y^2` | `y^3+x+x^2` |
| **`[[144,12,12]]` (gross)** | **1/24** | **12,6** | **`x^3+y+y^2`** | **`y^3+x+x^2`** |
| `[[288,12,18]]` | 1/48 | 12,12 | `x^3+y^2+y^7` | `y^3+x+x^2` |
| `[[360,12,\le24]]` | 1/60 | 30,6 | `x^9+y+y^2` | `y^3+x^{25}+x^{26}` |
| `[[756,16,\le34]]` | 1/95 | 21,18 | `x^3+y^{10}+y^{17}` | `y^5+x^3+x^{19}` |

Notes from `tab:codes`/`tab:codes_intro` text (l.354–423, 635–662):
- All codes: weight-6 checks, thickness-2 Tanner graph, depth-7 syndrome circuit. `[[n,k,d]]` needs `2n` physical qubits total (`n` data + `n` check ancillas); net rate `r=k/2n` rounded down to nearest inverse integer.
- `[[144,12,12]]` "may be the most promising for near-term demonstrations"; pseudo-threshold `p_0=0.0065`; `p_L(10^{-3})=2\times10^{-7}`. The distance-13 surface code has `r=1/338`.
- `[[360,12,\le24]]` improves on `[[882,24,\le24]]` (`panteleev2021degenerate`) if the upper bound is tight.
- "all codes shown in `\tab{codes_intro}` are new" (l.358).
- Commented-out (NOT in published table, retained in tex as comments): `[[98,6,12]]` (7,7), `[[270,24,10]]` (15,9), `[[360,32,10]]` (15,12), `[[450,40,10]]` (15,15), `[[432,12,\le24]]` (18,12), `[[784,24,\le24]]` (28,14), `[[378,10,\le26]]` (27,7). The `[[784,24,\le24]]` and `[[432,4,\le22]]` codes ARE used in the toric-layout discussion (l.877–883).

---

## 3. Candidate ledger entries (typed)

> Schema: id | claim | modality | evidence (tex) | dependencies | risk | status

| id | claim | modality | evidence | deps | risk | status |
|---|---|---|---|---|---|---|
| B01 | Ring relations `xy=yx`, `x^\ell=y^m=I` from `x=S_\ell\otimes I_m`, `y=I_\ell\otimes S_m` | SymbolicDerivation | l.520–522 | D1 | R0 | `[SOLID]` |
| B02 | BB definition: `A=\sum A_i`, `B=\sum B_j` (each a power of `x` or `y`, distinct) ⇒ weight-3 each | LiteratureGrounded (definition) | l.524–530, eq `AB` | D1,D2 | R0 | `[SOLID]` |
| B03 | `H^X=[A|B]`, `H^Z=[B^T|A^T]`, size `(n/2)\times n` | LiteratureGrounded (definition) | l.535–541, eq `HXHZ` | D2,D3 | R0 | `[SOLID]` |
| B04 | CSS commutativity `H^X(H^Z)^T = AB+BA = 0 (mod 2)` | SymbolicDerivation | l.544 | B03,B01 | R0 | `[SOLID]` (reproducible algebra; relies on `AB=BA`) |
| B05 | `n=2\ell m`, `k=2\dim(\ker A\cap\ker B)`, `d=\min\{|v|:v\in\ker H^X\setminus\rs H^Z\}` | SymbolicDerivation (via `lem:kd`) | l.546–552, l.668–675 | D4,L1 | R1 | `[SOLID]` (proof present, l.677–749) |
| B06 | `k = n - \rk H^X - \rk H^Z` and `\rk H^X=\rk H^Z` (so `k=2\ell m - 2\rk H^X`) | SymbolicDerivation | proof `lem:kd` l.680–701; uses `A^T=CAC`,`B^T=CBC` eq `ABC2` | B05 | R1 | `[SOLID]` — this is the rank form arXiv:2606.02418 uses |
| B07 | `d^X = d^Z` (equal X/Z distance) | ExactProof (in-chunk, constructive involution) | proof `lem:kd` l.703–748 | B05 | R1 | `[SOLID]` |
| B08 | Lemma `lem:kd` statement | ExactProof | l.666–749 (statement + full proof) | B05,B06,B07 | R1 | `[SOLID]` |
| B09 | Tanner-graph thickness `\theta\le2`, `O(n)` two-planar-layer decomposition, layers degree-3 | ExactProof (constructive wheel-graph decomposition) | `lem:thickness` l.775–833 | B03,L2 | R2 | `[SOLID]` (proof present) |
| B10 | Connectivity iff `S` generates `\mathcal{M}`; #components `=\ell m/|\langle S\rangle|`, all isomorphic | ExactProof (in-chunk) | `lem:connected` l.843–853 | DLAB,L3 | R2 | `[SOLID]` (proof present) |
| B11 | Toric-layout sufficient condition (`\langle A_iA_j^T,B_gB_h^T\rangle=\mathcal{M}` and order product `=\ell m`) | ExactProof (constructive Cayley-graph embedding) | `lem:toric_layout` l.863–872; DEF1 l.857–859 | L3,L4,DEF1 | R2 | `[SOLID]` (proof present; SUFFICIENT not necessary — see HOLE-2) |
| B12 | Gross code `[[144,12,12]]` = `(\ell,m)=(12,6)`, `A=x^3+y+y^2`, `B=y^3+x+x^2` | LiteratureGrounded (table) | `tab:codes` l.605; `tab:codes_intro` l.381 | B02,B03 | R0 | `[SOLID]` — verified landmark |
| B13 | 7 published BB codes `[[72,12,6]]…[[756,16,\le34]]` with `(A,B,\ell,m)` | LiteratureGrounded (table) | `tab:codes` l.597–622 | B12 | R1 | `[SOLID]` for exact-`d` rows; `[AXIOM]` for `\le d` rows (see HOLE-1) |
| B14 | Distances computed by MILP of `landahl2011fault` | LiteratureGrounded (cited) | l.636–637 | — | R2 | `[AXIOM]` — method cited, not reproduced here (this is the MILP baseline arXiv:2606.02418's `distance_milp.py` follows) |
| B15 | `\qc` is a special case of Lifted Product over `\ZZ_\ell\times\ZZ_m` | LiteratureGrounded (cited) | l.555–557; l.751–754 | `panteleev2021quantum` | R2 | `[AXIOM]` (cited construction) |
| B16 | BB codes in `\tab{codes}` empirically have no weight-4 stabilizers | EmpiricalMeasurement | l.835 | B13 | R1 | `[PRELIMINARY]` — "empirically observed", not proven |
| B17 | Some `(A,B)` yield disconnected (separable) codes; even `\ell` with `x\to x^2` ⇒ 2 components | SymbolicDerivation (instance of `lem:connected`) | l.841 | B10 | R1 | `[SOLID]` |
| B18 | Monomial labeling `\mathcal{M}` + unified `q(T,\alpha)`, `T\in{L,R,X,Z}` | LiteratureGrounded (definition) | l.757 | B03 | R0 | `[SOLID]` (load-bearing for supplemental logical-operator / automorphism sections) |

---

## 4. Open holes / gaps

- **HOLE-1 `[AXIOM]` / `[FUTURE]` (upper-bound distances).** Rows `[[360,12,\le24]]` and `[[756,16,\le34]]` of `tab:codes` (and the toric-layout examples `[[784,24,\le24]]`, `[[432,4,\le22]]`) report ONLY MILP upper bounds (`\le d`); the tex states "only an upper bound on the code distance is known at the time of this writing" (l.638). True distance is `[AXIOM]` pending an exact MILP/ILP certificate. Tex: l.617, l.621, l.638, l.879, l.883. Modality required to close: `NumericalSimulation` exact-MILP or `ExactProof`.
- **HOLE-2 `[FUTURE]` (toric layout is sufficient, not necessary).** `lem:toric_layout` (B11) gives a SUFFICIENT condition only ("A code `\qc` has a toric layout IF…", l.864). The tex explicitly exhibits a connected code (`[[784,24,\le24]]`) that does NOT satisfy the condition (l.876–882) but whether it lacks a toric layout entirely vs. fails only this particular sufficient test is not resolved in-chunk. A necessary-and-sufficient characterization is an open obligation. Does not block current claims.
- **HOLE-3 `[AXIOM]` (cited CSS / Lifted-Product machinery).** `lem:kd` imports `k=n-\rk H^X-\rk H^Z` and `d=\min(d^X,d^Z)` from `steane1996multiple`,`calderbank1996good` (l.678, l.703); the alternative `d^X=d^Z` proof cites `panteleev2021quantum` (l.751–754). These are treated as imported postulates; the in-chunk `lem:kd` proof of `d^X=d^Z` IS reproduced (B07), so the `[AXIOM]` is only on the CSS-parameter framework, not on the equal-distance result.
- **HOLE-4 `[FUTURE]` (MILP distance method not reproduced).** B14: the MILP distance computation is delegated to `landahl2011fault`. The mission paper arXiv:2606.02418's `distance_milp.py` claims to "follow Bravyi et al." for its CSS MILP — but the BB paper itself only cites Landahl–Anderson–Rice and gives no MILP formulation in this chunk. Reproducing/auditing the exact MILP formulation lives in `sec:decoder` (supplemental, NOT this chunk). `[BLOCKING]` for any claim that the 2606 MILP is provably equivalent to the 2308 method.
- **HOLE-5 `[FUTURE]` (sections not in chunk).** Syndrome circuit (depth-7 CNOT, `sec:syndrome_circuit`), BP-OSD decoder (`sec:decoder`), numerics (`sec:numerics`), logical operators via Tanner-graph automorphisms / ZX-duality / logical measurements (`sec:logicals`), and the proof of "Lemma 1" all live in `supplemental_v2.tex` (`\input` at l.886) and the post-l.888 conclusion — NOT this chunk. Forward-referenced claims (depth-7 circuit, logical operators) carry `[AXIOM]` until those chunks are imported.
- **HOLE-6 `[FUTURE]` (figure content).** `fig:2Dlayout`, `fig:wheel_extraction`, `fig:navigation` are PDFs; the wheel-graph / compass-diagram geometry underpinning the `lem:thickness` and `lem:toric_layout` proofs is described only in captions (l.336–343, l.763, l.771). Geometric claims rely on the figure being correct (`[UNSAFE]` to assert pixel-level layout from text alone); the algebraic content (orders, 4-cycles) IS in-text and verified.

---

## 5. Key landmark codes (timeline seed, this chunk)

| Code | `(\ell,m)` | `A` | `B` | `d` status | rate | Source line |
|---|---|---|---|---|---|---|
| `[[72,12,6]]` | 6,6 | `x^3+y+y^2` | `y^3+x+x^2` | exact (conjectured circuit-distance-preserving) | 1/12 | l.597, l.374 |
| `[[90,8,10]]` | 15,3 | `x^9+y+y^2` | `1+x^2+x^7` | exact | 1/23 | l.601, l.376 |
| `[[108,8,10]]` | 9,6 | `x^3+y+y^2` | `y^3+x+x^2` | exact | 1/27 | l.603, l.378 |
| **`[[144,12,12]]` (gross)** | 12,6 | `x^3+y+y^2` | `y^3+x+x^2` | exact | 1/24 | l.605, l.381 — **verified landmark; `bravyi2024high`** |
| `[[288,12,18]]` | 12,12 | `x^3+y^2+y^7` | `y^3+x+x^2` | exact (UB `\le18` "unlikely tight", l.423) | 1/48 | l.609, l.383 |
| `[[360,12,\le24]]` | 30,6 | `x^9+y+y^2` | `y^3+x^{25}+x^{26}` | upper bound | 1/60 | l.617 |
| `[[756,16,\le34]]` | 21,18 | `x^3+y^{10}+y^{17}` | `y^5+x^3+x^{19}` | upper bound | 1/95 | l.621 |
| `[[784,24,\le24]]` | 28,14 | `x^{26}+y^6+y^8` | `y^7+x^9+x^{20}` | upper bound | — | l.879 — connected, NO toric layout |
| `[[432,4,\le22]]` | 18,12 | `x+y^{11}+y^3` | `y^2+x^{15}+x` | upper bound | — | l.883 — toric layout needs `\mu,\lambda=36,6` |

Provenance / role: this paper IS `bravyi2024high`, the foundational BB-code paper. The
gross `[[144,12,12]]` is the landmark that arXiv:2606.02418 and this knowledge base
verify. The BB construction (`H^X=[A|B]`, `H^Z=[B^T|A^T]` over `R=\FF_2[x,y]/(x^\ell-1,y^m-1)`)
REPLACES the external axiom `ax:bb-construction` in `src/qcode_discovery/bb_codes.py`;
`k = 2\ell m - 2\rk H^X`, `n=2\ell m` (B06) is the rank form used downstream.
