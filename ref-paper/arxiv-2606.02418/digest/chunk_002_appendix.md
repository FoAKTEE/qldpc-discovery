# chunk_002_appendix — Appendices A–F (paper.tex 791–1088)

Pipeline-0 source-import digest of arXiv:2606.02418 "Evolutionary Discovery of Bivariate
Bicycle Codes with LLM-Guided Search" (Cruz-Benito, Cross, Kremer, Faro; IBM Research; PRX Quantum).
SOURCE: `src/paper.tex` lines 791–1088 (`\appendix` through `\bibliography`).
Sibling chunk: `chunk_001_*` (main text, not present at write time).

Scope of these appendices:
- App A `app:threshold` (l.793–847): code-capacity simulation tables (data only).
- App B `app:ablation` (l.849–905): ablation study tables (data only).
- App C `app:mutations` (l.907–954): representative LLM mutation diffs (qualitative).
- App D `app:ab_trap` (l.956–980): **Theorem `thm:ab_d2`** + proof (verbatim below).
- App E `app:crt` (l.982–1024): **Theorem `lem:crt_k`** + proof (verbatim below).
- App F `app:lc` (l.1026–1088): Local Clifford (LC) equivalence of PBB codes (procedure below).

DISCIPLINE: each imported claim is a TYPED entry (context, claim, modality, dependencies, status).
Default modality `LiteratureGrounded`; the two theorems carry full in-paper proofs → `ExactProof`.
Cited-but-not-reproduced results marked `[AXIOM]`. Tex labels preserved VERBATIM.

---

## 1. Theorem `thm:ab_d2` (App D, l.959–970) — verbatim

> **Theorem (Distance trap).** `\label{thm:ab_d2}`
> Every BB code with $A = B$ and $k > 0$ has $d = 2$ exactly.

**Proof (verbatim, l.964–970):**

> For $A = B$, every $X$-stabilizer has the form $(A_r \mid A_r)$, so $\mathrm{rowspace}(H_X)$
> is contained in the diagonal subspace $S := \{(\mathbf{w},\mathbf{w}) : \mathbf{w} \in \FF_2^{\ell m}\}$.
> The weight-2 vector $\mathbf{v}_i := \mathbf{e}_i + \mathbf{e}_{i+\ell m} = (\mathbf{e}_i, \mathbf{e}_i)$
> lies in $S$ and satisfies $H_Z \mathbf{v}_i = A^\top \mathbf{e}_i + A^\top \mathbf{e}_i = \mathbf{0}$,
> so $\mathbf{v}_i \in \ker(H_Z)$.
> It is an $X$-stabilizer iff $\mathbf{e}_i \in \mathrm{rowspace}(A)$, but $k > 0$ forces
> $\mathrm{rank}(A) < \ell m$, so some $\mathbf{e}_i$ lies outside, yielding a nontrivial weight-2
> $X$-logical and $d_X \leq 2$.
> The same vector also satisfies $H_X \mathbf{v}_i = \mathbf{0}$ and is a $Z$-stabilizer iff
> $\mathbf{e}_i \in \mathrm{colspace}(A)$; again $\mathrm{rank}(A) < \ell m$ forces some $\mathbf{e}_i$
> outside, giving $d_Z \leq 2$.
> Polynomials with $\geq 2$ terms force every column of $H_X, H_Z$ to have weight $\geq 2$,
> so $d \geq 2$, hence $d = 2$.

**Remarks (l.972–973):**
- This condition ($A = B$, identical polynomials) is *distinct* from antipodal self-duality
  $B = A^\top$ studied in `liang2025selfdual`, where self-dual BB codes with $B = A^\top$ can have
  $d$ as high as 16.
- The theorem holds regardless of check weight (any polynomial weight $\geq 2$).

**Extension to PBB codes (paragraph, l.975–980, verbatim claim):**

> The same argument applies to PBB codes with $A = B$: the X-part of the first stabilizer block
> is $[A \mid A]$, so the weight-2 Z-type operator $(0|\mathbf{e}_i + \mathbf{e}_{i+\ell m})$ has
> symplectic inner product zero with every block-1 stabilizer (since the X-part contributes
> $(A_r)_i + (A_r)_i = 0 \bmod 2$) and with every block-2 stabilizer (which has zero X-part).
> These $\ell m$ weight-2 operators lie in the normalizer $N(S)$.
> In the CSS case, a direct counting argument shows that $k/2$ of them are nontrivial logicals
> (Theorem `thm:ab_d2`).
> For PBB codes, the additional Z-content from perturbation polynomials $C$ and $D$ changes the
> stabilizer group, but the normalizer membership of these weight-2 operators is preserved;
> whenever any such operator is not itself a stabilizer element—as verified by MILP for all $A = B$
> PBB codes in the catalog—$d \leq 2$. Combined with $d \geq 2$ (from polynomial weight $\geq 2$),
> this gives $d = 2$.

**Proof-structure annotation (for elaboration; not in tex):**
1. $\mathrm{rowspace}(H_X) \subseteq S$ (diagonal subspace) because $A=B$ ⇒ each row is $(A_r\mid A_r)$.
2. $\mathbf{v}_i=(\mathbf{e}_i,\mathbf{e}_i)\in\ker(H_Z)$: $H_Z\mathbf{v}_i = A^\top\mathbf{e}_i + A^\top\mathbf{e}_i = 0$.
   (Here $H_Z=(B^\top\mid A^\top)=(A^\top\mid A^\top)$ under $A=B$.)
3. $\mathbf{v}_i$ is X-stabilizer iff $\mathbf{e}_i\in\mathrm{rowspace}(A)$; $k>0\Rightarrow\mathrm{rank}(A)<\ell m$
   ⇒ ∃ $\mathbf{e}_i\notin\mathrm{rowspace}(A)$ ⇒ nontrivial weight-2 X-logical ⇒ $d_X\le 2$.
4. Symmetric argument on $\mathrm{colspace}(A)$ ⇒ $d_Z\le 2$.
5. Lower bound: each polynomial has $\ge 2$ terms ⇒ every column weight $\ge 2$ ⇒ $d\ge 2$.
6. Hence $d=2$.

---

## 2. Theorem `lem:crt_k` (App E, l.985–1024) — verbatim

> **Theorem (Univariate encoding dimension).** `\label{lem:crt_k}`
> Let $\ell$ and $m$ be positive integers divisible by 3 and let $c = \ell/3$.
> The BB code defined by $A(y) = 1{+}y{+}y^2 \in \FF_2[y]/(y^m{-}1)$ and
> $B(x) = A(x^c) \in \FF_2[x]/(x^\ell{-}1)$ is a hypergraph product code that encodes
> $k = 8\ell/3$ logical qubits.

**Proof (verbatim, l.990–1024):**

> Let $H_A\in {\mathbb F}_2^{m\times m}$ and $H_B\in {\mathbb F}_2^{\ell\times\ell}$ be the circulant
> matrices associated with $A(y)$ and $B(x)$, respectively. The check matrices of the bivariate
> bicycle code are
> $$H_X = \left(\,I_\ell\otimes H_A \ \middle|\ H_B\otimes I_m\,\right)$$
> and
> $$H_Z = \left(\,H_B^T\otimes I_m \ \middle|\ I_\ell\otimes H_A^T\,\right).$$
> The hypergraph product code $HGP(H_1,H_2)$ with $H_1\in {\mathbb F}_2^{r_1\times n_1}$ and
> $H_2\in {\mathbb F}_2^{r_2\times n_2}$ has check matrices
> $$H_X^{HGP} = \left(\,H_1\otimes I_{n_2} \ \middle|\ I_{r_1}\otimes H_2^T\,\right)$$
> and
> $$H_Z^{HGP} = \left(\,I_{n_1}\otimes H_2 \ \middle|\ H_1^T\otimes I_{r_2}\,\right).$$
> Choosing $H_1=H_B$ and $H_2=H_A^T$ with $r_1=n_1=\ell$ and $r_2=n_2=m$ produces a HGP code that
> is equivalent to the BB code with the left and right blocks of qubits swapped. Therefore
> $BB(A,B)$ is equivalent to $HGP(H_B,H_A^T)$. For binary parity check matrices $H_1$, $H_2$ of
> classical codes encoding $k_1$, $k_2$ bits, respectively, and whose transposes are classical codes
> encoding $k_1^T$, $k_2^T$ bits, the hypergraph product code $HGP(H_1,H_2)$ encodes
> $k_1k_2+k_1^Tk_2^T$ qubits \cite{tillich2014quantum}. For an $N$ by $N$ circulant matrix $H$
> corresponding to the polynomial $f(z)\in {\mathbb F}_2[z]/(z^N-1)$, a standard cyclic-code
> identity~\cite{macwilliams1977theory} gives
> $$\mathrm{dim}\ \mathrm{ker}\ H = \mathrm{deg}\ \mathrm{gcd}(f, z^N-1).$$
> The transpose of a square matrix $H$ has the same kernel dimension as $H$. Now, $(y-1)A(y)=y^3-1$
> and $y^3-1$ divides $y^m-1$ whenever $m$ is divisible by 3, so $A(y)$ divides $y^m-1$. Therefore,
> $k_A=k_A^T=\mathrm{deg}\ A=2$. Likewise, $(x^c-1)B(x)=x^\ell-1$, so $B(x)$ divides $x^\ell-1$ and we
> find $k_B=k_B^T=\mathrm{deg}\ B=2c=2\ell/3$. Putting this together, we conclude that
> $$k = k_1k_2+k_1^Tk_2^T = k_Bk_A^T + k_B^Tk_A = 2k_Bk_A^T = 2\cdot \frac{2\ell}{3}\cdot 2 = 8\ell/3.$$

**Proof-structure annotation (for elaboration; not in tex):**
1. Write BB check matrices $H_X=(I_\ell\otimes H_A\mid H_B\otimes I_m)$, $H_Z=(H_B^\top\otimes I_m\mid I_\ell\otimes H_A^\top)$.
2. Identify with HGP template under $H_1=H_B$, $H_2=H_A^\top$, $r_1=n_1=\ell$, $r_2=n_2=m$ ⇒
   $BB(A,B)\cong HGP(H_B,H_A^\top)$ (qubit-block swap).
3. HGP dimension formula `tillich2014quantum`: $k=k_1k_2+k_1^Tk_2^T$ — **CITED [AXIOM]**.
4. Circulant kernel identity `macwilliams1977theory`: $\dim\ker H=\deg\gcd(f,z^N-1)$ — **CITED [AXIOM]**.
5. $(y-1)A(y)=y^3-1\mid y^m-1$ (since $3\mid m$) ⇒ $A\mid y^m-1$ ⇒ $k_A=k_A^T=\deg A=2$.
6. $(x^c-1)B(x)=x^\ell-1$ ⇒ $B\mid x^\ell-1$ ⇒ $k_B=k_B^T=\deg B=2c=2\ell/3$.
7. $k=k_Bk_A^T+k_B^Tk_A=2k_Bk_A^T=2\cdot(2\ell/3)\cdot 2=8\ell/3$.

NOTE: ground-truth seed records `lem:crt_k` numerically verified for 1680 combos with $\ell m\le 250$
(verification is reported in main text, not in this appendix range).

---

## 3. LC-CSS equivalence of PBB codes (App F `app:lc`, l.1026–1088)

**Motivating question (l.1029):** are the 368 non-CSS PBB codes merely CSS codes in disguise, i.e.
equivalent to a CSS code via per-qubit single-qubit Clifford conjugation (local Clifford / LC equivalence)?

**Block convention (l.1031):** block 1 = first $\ell m$ qubits (columns of $A$ in $H$);
block 2 = second $\ell m$ qubits (columns of $B$). A per-qubit Clifford assignment is a tuple of
$2\ell m$ single-qubit Cliffords; "uniform per block" = constant on each block index set.

### 3.1 Group-CSS rank condition (Lemma 7.4) — l.1033–1037

- For each PBB code, apply a product of single-qubit Cliffords to the stabilizer generators, then test
  whether the resulting stabilizer group $\mathcal{S}$ is CSS (sense of `calderbank1996good`, `steane1996multiple`).
- **Rank test:** $\mathcal{S}$ is CSS iff
  $$\operatorname{rank}[X \mid Z] = \operatorname{rank} X + \operatorname{rank} Z \quad\text{over } \mathrm{GF}(2).$$
  This is **Lemma 7.4 of `cross2025small`** (attributed there to T. Yoder); the paper refers to that
  source for the proof → **CITED [AXIOM]** (not reproduced here).
- Cross & Vandeth (`cross2025small` §7.2) remark **no fast test for LC-CSS-equivalence is currently
  known**; this is why the procedure enumerates Clifford patterns explicitly and admits residual gaps.

### 3.2 Reduction to 6 Clifford representatives — l.1039–1040

- Single-qubit Clifford group: 24 elements, but only **6 cosets modulo the single-qubit Pauli group**.
- Pauli conjugation flips signs of generators without changing X-/Z-supports; whether the stabilizer
  *group* is CSS depends only on the symplectic subspace it spans, not signs ⇒ suffices to check one
  representative per coset.
- Representatives used: $\{I, S, H, HS, SH, HSH\}$ (same reduction as `cross2025small` §7.2).

### 3.3 Hadamard 2-coloring (decides $\{I,H\}$ non-uniform, at generator level) — l.1042–1052

A parity 2-coloring deciding whether the supplied generators can be made CSS by a per-qubit $H$ pattern
$H_J$ ($J\subseteq\{1,\dots,n\}$). (Similar 2-coloring used by `khesin2026mirror` in the mirror-code
setting; derived here directly for general stabilizer codes.)

- Represent each Pauli factor on qubit $j$ as $(x_j,z_j)\in\FF_2^2$: $I=(0,0)$, $X=(1,0)$, $Z=(0,1)$, $Y=(1,1)$.
  Conjugation by $H$ swaps coordinates $(x_j,z_j)\mapsto(z_j,x_j)$ and sends $Y\to -Y$ (symplectic rep of $Y$ invariant).
- Let $s_j=\mathbb{1}[j\in J]$; let $c_r\in\{0,1\}$ encode desired post-conjugation type of generator $g_r$
  ($c_r=1$ pure-$X$, $c_r=0$ pure-$Z$).
- **Y obstruction:** if any $g_r$ has $Y$ at qubit $j$, both coordinates set; conjugation by any $H_J$ leaves $g_r$ mixed.
- **No-Y parity 2-coloring:** on $j\in\mathrm{supp}(g_r)$ local Pauli is X or Z; let $t_{rj}\in\{0,1\}$ denote which.
  Post-conjugation X-bit at $(r,j)$ is $t_{rj}\oplus s_j$; demanding $=c_r$ on every $j\in\mathrm{supp}(g_r)$ gives
  $s_j=c_r\oplus t_{rj}$.
- For two generators on the same qubit $j$, RHS must agree: $c_{r_1}\oplus c_{r_2}=t_{r_1,j}\oplus t_{r_2,j}$
  (equal Pauli types force equal colors; opposite types force different colors).
- **Solvable in linear time by union-find with parity** (a 2-coloring problem).
- **Soundness/completeness scope:** sound and complete *at the level of the supplied generators* — True
  exhibits an explicit $H_J$ making each generator pure-X or pure-Z (a fortiori group CSS); False rules out
  any $H_J$ achieving this *for the supplied generators*. The strictly broader question (group CSS under a
  different row-reduced generating set after some $H_J$) is decoupled from this 2-coloring and handled
  partially by the rank machinery and the $\{I,S\}/\{H,HS\}$ enumeration; residual gaps itemized below.

### 3.4 Verification procedure (two parts) — l.1054–1067

The procedure replaces the exponential $6^n$ Clifford enumeration (which would otherwise be needed to
decide LC-CSS via direct Lemma 7.4 on every conjugated group) by polynomial-time tests over three
structured Clifford families, plus a constant-cost 36-assignment enumeration:

- **Step 1 — Uniform per-block assignments (l.1059–1060):**
  For each of the $6\times 6 = 36$ uniform per-block assignments (one of $\{I,S,H,HS,SH,HSH\}$ on all of
  block 1, another on all of block 2), directly transform the stabilizer matrix and check the rank
  condition (§3.1).

- **Step 2 — Non-uniform $\{I,S\}$ and $\{H,HS\}$ assignments (l.1062–1066):**
  Within $\{I,S\}$, each qubit $j$ receives $S^{s_j}$, $s_j\in\{0,1\}$ ⇒ pattern
  $(\mathbf{s}_1,\mathbf{s}_2)\in\FF_2^{2\ell m}$. The group-CSS condition is **affine-linear** in this
  pattern over $\mathrm{GF}(2)$: for each vector $w$ in the orthogonal complement of
  $L=\mathrm{rowspan}([B^\top\mid A^\top])$ and each stabilizer row $g$, the constraint
  $w\cdot\mathrm{row}_g=0$ yields one affine equation in $(\mathbf{s}_1,\mathbf{s}_2)$. Solve the system
  exactly via $\mathrm{GF}(2)$ rank comparison; confirm it is either infeasible or admits a uniform
  solution. The $\{H,HS\}$ macro-class yields the **identical** constraint system.

Family→method map (l.1055): Hadamard 2-coloring covers non-uniform $\{I,H\}$; Step-2 affine GF(2) systems
cover non-uniform $\{I,S\}$ and $\{H,HS\}$; Step-1 covers the 36 uniform per-block assignments.

### 3.5 Coverage and gaps — l.1069–1076

Covered: Step 1 = all 6 macro-classes per block under **uniform** assignments; Step 2 = **non-uniform**
within $\{I,S\}$ and within $\{H,HS\}$; Hadamard 2-coloring = **non-uniform** within $\{I,H\}$.

Two classes of LC patterns lie **outside** combined coverage:
- **(a)** Non-uniform patterns within $\{SH,HSH\}$ on block 1. (On block 2, whose rows have zero X-part,
  $SH$ and $HSH$ act identically on pure-Z input, so block-2 non-uniformity within this class collapses to
  a uniform choice already handled by Step 1.)
- **(b)** Non-uniform patterns whose per-qubit Cliffords are not all from a single covered family
  $\{I,S\}$, $\{H,HS\}$, or $\{I,H\}$ — e.g. $S$ on some qubits and $H$ on others, or any pattern using
  $SH$/$HSH$ alongside other Cliffords.

No GF(2) reduction analogous to Step 2 exists for either gap, and they were not exhaustively brute-forced.
The gaps could in principle be eliminated by direct $6^n$ enumeration + Lemma 7.4, but at scale
($n=2\ell m\ge 36$, up to 360) this is computationally infeasible.

### 3.6 Results — l.1078–1087

- Exactly **one** code — the $[[36,4,6]]$ code ($\FOM=4.0$) — passes the uniform check with the $S$-gate
  on both blocks ($s_1=s_2=1$); LC-equivalent to CSS via uniform $S$.
- Remaining 367 fail every uniform and non-uniform $\{I,S\}/\{H,HS\}$ assignment.
- Hadamard 2-coloring (non-uniform $\{I,H\}$, which Step 2 does not capture) identifies **10 additional**
  codes as Hadamard-equivalent to CSS; explicit per-qubit $H$ pattern of weight $n/2$ renders every
  stabilizer pure-X or pure-Z, verified by direct construction.
- **Total: 11 of 368 PBB codes are CSS-equivalent under the tested LC families (10 via non-uniform $H$,
  1 via uniform $S$).**
- Remaining **357** admit no CSS reduction within tested families; gaps (a)–(b) mean reductions via
  non-uniform $\{SH,HSH\}$ on block 1 or cross-class non-uniform patterns cannot be ruled out ⇒ described
  as **"CSS-inequivalent within the tested local-Clifford families"** rather than "genuinely non-CSS".
- Future work (l.1085): integrate LC-CSS check into the evolutionary loop to penalize/discard disguised-CSS codes.
- Complementary classification not pursued: **GF(4)-linearity** — an LC-invariant decided by testing
  whether $R^{\otimes n}$ ($R=HS$) sends the stabilizer group to itself (`cross2025small` Lemma 7.5,
  Cor. 7.6). Cross–Vandeth Lemma 7.7 exhibits a non-CSS GF(4)-linear group LC-equivalent to a CSS one ⇒
  GF(4)-linearity is a **complement**, not a substitute, for the LC-CSS test.
- Verification script: `evaluation/clifford_equivalence.py` (supplementary material).

---

## 4. Appendices A–C (data/qualitative — summarized, not load-bearing for proofs)

- **App A `app:threshold` (l.793–847):** code-capacity simulation. $X$-only model: independent $X$ at rate
  $p$; BP-OSD (OSD-CS order 7, product-sum, 20 BP iterations). Block LER over 100,000 trials;
  $p_L=1-(1-\text{LER})^{1/k}$; Wilson 95% CI $\le 0.06$ pp for LER $\le 1\%$. `tab:threshold_css`
  (8 CSS codes, bit-flip) and `tab:threshold_noncss` (5 PBB + gross-code baseline, $X$-only +
  depolarizing). Depolarizing decoder caveat in footnote `fn:depolarizing-decoder` (iid X/Z prior is
  mismatched; results are decoder-dependent lower bounds). PBB $[[144,12,12]]$ outperforms CSS counterpart
  at $p\ge 6\%$ under $X$-only; identical under depolarizing with the iid prior.
- **App B `app:ablation` (l.849–905):** ablation. Exact $\FF_2$ rank; $\Sigma_k=\sum_{\ell,m}\max\{k\}$.
  Multi-seed arms: mean ± std over 5 seeds. GA-G = GA on the LLM ansatz representation with AST-level
  mutations. `tab:ablation_k` (k-only summary) and `tab:ablation_per_lattice` (per-lattice max k). Key
  finding: both GAs exceed Campaign 1 on $\Sigma_k$ but via low-distance ($d\le 2$) codes; LLM's
  highest-FOM $d\ge 6$ codes reach $\FOM=12.0$ vs $\le 4.0$ for either GA. GA-G reaches $k=n/2$ at every
  lattice (all $d\le 2$).
- **App C `app:mutations` (l.907–954):** three Campaign-1 LLM mutation diffs (Gemini 3 Flash, gen depth 5):
  Mut1 expanded search range + coprimality heuristic (`fig:mut1`, +22%); Mut2 "Pure-Axis"/decoupled
  univariate strategy — independent convergence on univariate/HGP codes from fitness signal alone
  (`fig:mut2`, +40%); Mut3 over-specialization reducing coverage (`fig:mut3`, −4%).

---

## 5. Candidate ledger entries

Schema per `_common/agentic_lean_contract.md`: id, name, type, context, claim, modality, evidence,
dependencies, assumptions, status, provenance.

### LEDGER-002-01 — Theorem `thm:ab_d2` (A = B distance trap)

- **id:** `chunk002.thm_ab_d2`
- **name:** `thm:ab_d2` (Distance trap)
- **type:** Theorem
- **context:** BB CSS code over $R=\FF_2[x,y]/(x^\ell-1,y^m-1)$; $H_X=(A\mid B)$, $H_Z=(B^\top\mid A^\top)$;
  $A,B$ circulant $\ell m\times\ell m$; CSS condition $AB+BA=0$.
- **claim:** Every BB code with $A=B$ and $k>0$ has $d=2$ exactly.
- **modality:** **ExactProof** (full proof reproduced from tex l.964–970).
- **evidence:** Proof: $\mathrm{rowspace}(H_X)\subseteq$ diagonal subspace $S$; weight-2 $\mathbf{v}_i=(\mathbf{e}_i,\mathbf{e}_i)\in\ker H_Z\cap\ker H_X$;
  $k>0\Rightarrow\mathrm{rank}(A)<\ell m$ ⇒ some $\mathbf{e}_i$ outside rowspace/colspace ⇒ weight-2 X-/Z-logical ⇒ $d_X,d_Z\le 2$;
  column weight $\ge 2$ ⇒ $d\ge 2$; hence $d=2$.
- **dependencies:** BB construction (`bravyi2024high`, MANDATORY); definitions of $H_X,H_Z,k$ (main text / `chunk_001`); standard linear algebra over $\FF_2$.
- **assumptions:** $A=B$ identical circulant; $k>0$; every defining polynomial has $\ge 2$ terms (col weight $\ge 2$).
- **status:** `checked`.
- **provenance:** `src/paper.tex` l.959–970 (statement+proof), l.972–973 (remarks).

### LEDGER-002-02 — Theorem `thm:ab_d2` PBB extension

- **id:** `chunk002.thm_ab_d2_pbb`
- **name:** `thm:ab_d2` extension to PBB codes
- **type:** Corollary/Extension
- **context:** PBB non-CSS code, 4-tuple $(A,B,C,D)$; $H=[[A,B,C,D],[0,0,B^\top,A^\top]]$; $A=B$.
- **claim:** PBB codes with $A=B$ also have $d=2$ (whenever any weight-2 normalizer operator is not a stabilizer element).
- **modality:** **ExactProof** for normalizer-membership argument; the "not-a-stabilizer-element" condition is verified per-code by **MILP (`NumericalSimulation`/exact MILP)** for all $A=B$ PBB codes in the catalog.
- **evidence:** X-part of block-1 is $[A\mid A]$ ⇒ weight-2 Z-operator $(0\mid\mathbf{e}_i+\mathbf{e}_{i+\ell m})$ has symplectic inner product 0 with all block-1 and block-2 stabilizers ⇒ lies in normalizer $N(S)$; $d\le 2$ when not itself a stabilizer (MILP-verified); $d\ge 2$ from polynomial weight; hence $d=2$.
- **dependencies:** LEDGER-002-01; PBB commutation rule $AC^\top+BD^\top$ symmetric (main text); MILP symplectic non-CSS distance routine (SM).
- **assumptions:** $A=B$; MILP confirms the weight-2 operator is non-stabilizer for each catalog code (per-code, not a closed-form proof).
- **status:** `conditional` (general $d\le 2$ depends on per-code MILP check; not a fully closed-form theorem for arbitrary $C,D$). See [HOLE-002-A].
- **provenance:** `src/paper.tex` l.975–980.

### LEDGER-002-03 — Theorem `lem:crt_k` (univariate encoding dimension)

- **id:** `chunk002.lem_crt_k`
- **name:** `lem:crt_k` (Univariate encoding dimension)
- **type:** Theorem
- **context:** $\ell,m$ divisible by 3; $c=\ell/3$; $A(y)=1+y+y^2\in\FF_2[y]/(y^m-1)$, $B(x)=A(x^c)\in\FF_2[x]/(x^\ell-1)$.
- **claim:** $BB(A,B)$ is a hypergraph product code encoding $k=8\ell/3$ logical qubits.
- **modality:** **ExactProof** (full proof reproduced from tex l.990–1024), **conditional on two CITED lemmas** (see assumptions).
- **evidence:** $BB(A,B)\cong HGP(H_B,H_A^\top)$ (qubit-block swap); HGP dim $k=k_1k_2+k_1^Tk_2^T$; circulant kernel $\dim\ker H=\deg\gcd(f,z^N-1)$; $(y-1)A=y^3-1\mid y^m-1$ ⇒ $k_A=k_A^T=2$; $(x^c-1)B=x^\ell-1$ ⇒ $k_B=k_B^T=2\ell/3$; $k=2k_Bk_A^T=8\ell/3$.
- **dependencies:** HGP distance/dimension theory (`tillich2014quantum`) **[AXIOM]**; cyclic-code kernel identity (`macwilliams1977theory`) **[AXIOM]**; BB↔HGP equivalence.
- **assumptions:** $3\mid\ell$ and $3\mid m$; $A(y)=1+y+y^2$ fixed trinomial; `tillich2014quantum` HGP dimension formula and `macwilliams1977theory` kernel identity accepted as imported.
- **status:** `conditional` (rests on two CITED [AXIOM] results; the in-paper algebra is exact). Numerically corroborated for 1680 combos $\ell m\le 250$ (main text).
- **provenance:** `src/paper.tex` l.985–1024.

### LEDGER-002-04 — Lemma 7.4 group-CSS rank condition (imported)

- **id:** `chunk002.lemma74_rank`
- **name:** Lemma 7.4 (`cross2025small`, attr. T. Yoder)
- **type:** Lemma (imported, used as test predicate)
- **context:** Stabilizer group $\mathcal{S}$ with binary symplectic representation $[X\mid Z]$ over GF(2).
- **claim:** $\mathcal{S}$ is CSS iff $\operatorname{rank}[X\mid Z]=\operatorname{rank}X+\operatorname{rank}Z$ over GF(2).
- **modality:** `LiteratureGrounded` (proof not reproduced; paper refers to `cross2025small`).
- **evidence:** Cited Lemma 7.4 of `cross2025small`.
- **dependencies:** CSS definition (`calderbank1996good`, `steane1996multiple`).
- **assumptions:** correctness of `cross2025small` Lemma 7.4.
- **status:** `[AXIOM]` — cited-but-not-reproduced; LC-CSS results downstream remain conditional on it.
- **provenance:** `src/paper.tex` l.1036.

### LEDGER-002-05 — LC-CSS classification result (11/368)

- **id:** `chunk002.lc_css_result`
- **name:** LC-CSS equivalence classification of PBB catalog
- **type:** Empirical/computational result
- **context:** 368 distinct non-CSS PBB codes; per-qubit single-qubit Clifford conjugation; representatives $\{I,S,H,HS,SH,HSH\}$.
- **claim:** Exactly 11/368 PBB codes are CSS-equivalent within the tested LC families (10 via non-uniform $H$ Hadamard 2-coloring; 1 — the $[[36,4,6]]$, FOM 4.0 — via uniform $S$ on both blocks). The remaining 357 are CSS-inequivalent within the tested LC families.
- **modality:** `NumericalSimulation`/exact GF(2) computation (Step-1 36 uniform assignments via rank test; Step-2 affine GF(2) solve for non-uniform $\{I,S\}$/$\{H,HS\}$; Hadamard 2-coloring union-find for non-uniform $\{I,H\}$).
- **evidence:** rank condition (LEDGER-002-04) + 36 uniform per-block enumeration + affine GF(2) systems + parity union-find 2-coloring; explicit weight-$n/2$ $H$ pattern verified by direct construction for the 10 Hadamard cases.
- **dependencies:** LEDGER-002-04 (Lemma 7.4) [AXIOM]; PBB construction; `evaluation/clifford_equivalence.py`.
- **assumptions:** coverage limited to families $\{I,S\}$, $\{H,HS\}$, $\{I,H\}$ (uniform) + 36 uniform per-block; gaps (a)–(b) not searched.
- **status:** `empirical` (computational; the 357 figure is "within tested families", NOT a proof of non-CSS-ness). See [HOLE-002-B].
- **provenance:** `src/paper.tex` l.1029–1087; script `evaluation/clifford_equivalence.py`.

---

## 6. Open holes

- **[HOLE-002-A] (PBB $A=B$ distance, l.979):** general $d\le 2$ for PBB with $A=B$ is established only
  via per-code MILP that the weight-2 normalizer operator is non-stabilizer — there is **no closed-form
  proof** that this holds for all $(A,C,D)$ with $A=B$. Expected obligation: a counting/rank argument over
  the perturbed stabilizer group (analogous to the CSS $k/2$ counting) that shows at least one weight-2
  normalizer operator is always a nontrivial logical. Evidence type needed: `ExactProof` or
  `Counterexample`. Owner: pipeline-1 elaboration.

- **[HOLE-002-B] (LC-CSS coverage gaps, l.1069–1076):** the 357 "CSS-inequivalent" codes are only
  inequivalent *within the tested LC families*. Gaps: (a) non-uniform $\{SH,HSH\}$ on block 1; (b)
  cross-class non-uniform patterns. No GF(2) reduction is known for either, and $6^n$ brute force is
  infeasible at $n$ up to 360. Expected obligation: either a polynomial-time GF(2) reduction covering
  $\{SH,HSH\}$ block-1 non-uniformity / cross-class patterns, or a bounded enumeration certifying no
  reduction exists. Evidence type needed: `SymbolicDerivation` (reduction) or `NumericalSimulation`
  (bounded enumeration). Owner: pipeline-1 elaboration / future campaign. [FUTURE]

- **[AXIOM] tillich2014quantum** (HGP dimension/distance) — load-bearing for `lem:crt_k`; not reproduced.
- **[AXIOM] macwilliams1977theory** (circulant kernel identity) — load-bearing for `lem:crt_k`; not reproduced.
- **[AXIOM] cross2025small Lemma 7.4** (group-CSS rank condition) — load-bearing for LC-CSS procedure.
- **[FUTURE] GF(4)-linearity classification** (l.1086): partition the 357 CSS-inequivalent codes into
  GF(4)-linear / non-GF(4)-linear via `cross2025small` Lemma 7.5 / Cor. 7.6; not pursued in this paper.

---

## 7. Preserved tex labels (verbatim)

`thm:ab_d2`, `lem:crt_k`, `app:threshold`, `app:ablation`, `app:mutations`, `app:ab_trap`, `app:crt`,
`app:lc`, `sec:pbb`, `sec:code_capacity`, `sec:ablation`, `tab:threshold_css`, `tab:threshold_noncss`,
`tab:ablation_k`, `tab:ablation_per_lattice`, `fig:mut1`, `fig:mut2`, `fig:mut3`, `fn:depolarizing-decoder`.
