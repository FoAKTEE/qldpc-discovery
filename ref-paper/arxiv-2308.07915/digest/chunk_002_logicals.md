# chunk_002_logicals — Logical memory + syndrome circuit (supplemental_v2.tex 43–200, 963–1342)

Pipeline-0 source-import digest of arXiv:2308.07915 "High-threshold and low-overhead
fault-tolerant quantum memory" (Bravyi, Cross, Gambetta, Maslov, Rall, Yoder; IBM;
Nature 627, 778–782 (2024)). This is the FOUNDATIONAL Bivariate Bicycle (BB) code paper;
our mission paper arXiv:2606.02418 builds on it.
SOURCE: `src/supplemental_v2.tex` lines 43–200 (syndrome circuit) and 963–1342 (logical memory:
Logical Pauli Operators `ssec:logical_pauli_operators` l.997; Logical Gates via Automorphisms
`ssec:automorphisms` l.1124; ZX-duality `ssec:ZX_duality` l.1226; Logical Measurements
`ssec:logical_measurements` l.1293).

WHY THIS CHUNK EXISTS (downstream dependency): these results inform our logical-operator
computation (`metrics.css_logicals`) and the LC-equivalence layer. The polynomial construction of
logical Pauli operators (Eq. `eq:logicalpaulis`) is the canonical way to read off a basis of
$\bar X,\bar Z$ from the BB polynomials $A,B$; the automorphism action gives the symmetry group used
to canonicalize / compare logical operators; the ZX-duality is the involution relating the two
logical blocks.

DISCIPLINE: each imported claim is a TYPED entry (context, claim, modality, dependencies, status).
Default modality `LiteratureGrounded`. Claims with a complete in-paper derivation/proof carry
`SymbolicDerivation` or `ExactProof`. Cited-but-not-reproduced external results (refs
`breuckmann2022foldtransversal`, `cohen2022lowoverhead`, `tremblay2022constant`) are marked
`[AXIOM]` — final results stay conditional on them. Tex labels preserved VERBATIM. No SLOP CANNON.

## Notation carried from `sec:codedefinition` (arXiv_v2.tex l.508–557), used below verbatim
- $\mathcal{M}$: the monomial set / abelian group $\mathbb{Z}_\ell\times\mathbb{Z}_m$, $|\mathcal{M}|=\ell m$.
- $x=S_\ell\otimes I_m$, $y=I_\ell\otimes S_m$, $x^\ell=y^m=I_{\ell m}$, $xy=yx$.
- $A=A_1+A_2+A_3$, $B=B_1+B_2+B_3$ over $R=\mathbb{F}_2[x,y]/(x^\ell-1,y^m-1)$; each $A_i,B_j$ a monomial.
- Check matrices $H^X=[A\,|\,B]$, $H^Z=[B^T\,|\,A^T]$; $n=2\ell m$; $k=2\dim(\ker A\cap\ker B)$.
- Four qubit registers $q(X),q(L),q(R),q(Z)$ of size $n/2=\ell m$ each; $q(L,\alpha),q(X,\alpha),\dots$
  index a register element by $\alpha\in\mathcal{M}$.
- gross landmark: $[[144,12,12]]$ at $(\ell,m)=(12,6)$, $A=x^3+y+y^2$, $B=y^3+x+x^2$ (Table, l.605).

---

## 1. Logical memory overview (`sec:logicals` l.963–995)

**E1 — context.** BB LDPC codes have the features required for a quantum memory: fault-tolerant
initialization/measurement of individual logical qubits and teleportation-based data transfer in/out
of the code. The toolkit combines two prior techniques: (i) fault-tolerant unitaries needing only
syndrome-measurement connectivity, following `\cite{breuckmann2022foldtransversal}`; (ii) low-overhead
Tanner-graph extensions enabling measurement of a single logical operator while preserving the
thickness-2 implementability criterion, following `\cite{cohen2022lowoverhead}`.
- **modality** LiteratureGrounded. **dependencies** [AXIOM] `breuckmann2022foldtransversal`,
  [AXIOM] `cohen2022lowoverhead`. **status** empirical/conditional.

**E2 — claim (block structure, l.980, l.1000).** The logical qubits split into an "unprimed" and a
"primed" block of equal size, with identical (symmetrical) commutation structure. Each block carries
$|\mathcal{M}|=\ell m$ many $X$ operators and $\ell m$ many $Z$ operators; operators in the primed
block commute with operators in the unprimed block. Each block contains a set of operators defining
$k/2$ logical qubits.
- **modality** SymbolicDerivation (derived in E5–E7). **dependencies** E5, E6. **status** checked.

**E3 — claim (resource caveat, l.995, `\edit`).** Equipping the $[[144,12,12]]$ code with ancilla
systems able to measure $X$ and $Z$ requires $2\times30\times(2d-1)=1380$ additional qubits on top of
the original 288 — significant overhead that undercuts the code's compactness. The authors expect this
is reducible and leave optimization to future work.
- **modality** LiteratureGrounded (arithmetic on `cohen2022lowoverhead` construction). **status** empirical.
- `[FUTURE]` resource optimization of the ancilla-system scheme is explicitly deferred by the authors.

---

## 2. Logical Pauli Operators (`ssec:logical_pauli_operators` l.997–1122)

**Monomial Pauli notation (l.1002–1005, verbatim setup).**
$\mathbb{F}_2^{\mathcal{M}}$ = polynomials over $\mathbb{F}_2$ with monomials from $\mathcal{M}$,
i.e. the quotient ring $\mathbb{F}_2[x,y]$ with $x^\ell=y^m=1$. For $P,Q\in\mathbb{F}_2^{\mathcal{M}}$,
$X(P,Q)$ denotes Pauli $X$ on qubits $q(L,\alpha)$ for $\alpha\in P$ and $q(R,\beta)$ for $\beta\in Q$
(identity elsewhere); $Z(P,Q)$ analogously. The $X$-stabilizer at $q(X,\alpha)$ is $X(\alpha A,\alpha B)$;
the $Z$-stabilizer at $q(Z,\alpha)$ is $Z(\alpha B^T,\alpha A^T)$.

**E4 — claim (commutation Lemma, l.1007).** `\begin{lemma}` $X(P,Q)$ anticommutes with $Z(\bar P,\bar Q)$
**if and only if** $1\in P\bar P^T+Q\bar Q^T$. `\end{lemma}`
- **modality** ExactProof — full proof given (l.1010–1043): overlap on $q(L,\alpha)$ iff
  $p_\alpha\bar p_\alpha=1$, on $q(R,\alpha)$ iff $q_\alpha\bar q_\alpha=1$; anticommute iff
  $\sum_\alpha(p_\alpha\bar p_\alpha+q_\alpha\bar q_\alpha)$ is odd; the coefficient of the monomial
  $1$ in $P\bar P^T+Q\bar Q^T$ equals exactly that sum. **dependencies** monomial notation. **status** checked.

**E5 — claim (logical $\Leftrightarrow$ commute-with-stabilizer, l.1046).** WLOG a logical Pauli is
$X(P,Q)$ or $Z(Q^T,P^T)$. $X(P,Q)$ (and $Z(Q^T,P^T)$) commutes with every stabilizer iff $PB+QA=0$.
- **modality** SymbolicDerivation — derived via E4: commutation with $Z(\alpha B^T,\alpha A^T)$ requires
  $\alpha\notin PB+QA$ for all $\alpha$, i.e. $PB+QA$ vanishes. **dependencies** E4. **status** checked.

**E6 — claim (two-solution requirement, l.1048).** If $(P,Q)$ solves $PB+QA=0$ then so does
$(\alpha P,\alpha Q)$ for any $\alpha\in\mathcal{M}$, giving an orbit of $|\mathcal{M}|=\ell m$ operators
each for $X$ and $Z$. A single solution used for both $X(\alpha P,\alpha Q)$ and $Z(\beta Q^T,\beta P^T)$
yields only commuting operators (since $PQ+QP=0$), so **at least two** solutions to $PB+QA=0$ are needed
to obtain nontrivial commutation relations.
- **modality** SymbolicDerivation. **dependencies** E4, E5. **status** checked.

**E7 — claim (canonical logical basis, Eq. `eq:logicalpaulis` l.1050–1058) — VERBATIM.**
Choose $f,g,h\in\mathbb{F}_2^{\mathcal{M}}$ with $Bf=0$ and $gB+hA=0$ (so that the logical $X$ operator
has **no support on $q(R)$** — needed for the measurement construction in §5). This gives two solutions
$(P,Q)=(f,0)$ and $(P,Q)=(g,h)$ and the family, for all $\alpha\in\mathcal{M}$:

> $\bar X_\alpha := X(\alpha f,0)\qquad \bar Z_\alpha := Z(\alpha h^T,\alpha g^T)$
> $\bar X'_\alpha := X(\alpha g,\alpha h)\qquad \bar Z'_\alpha := Z(0,\alpha f^T)$

Commutation (l.1058): $\bar X_\alpha,\bar Z'_\beta$ always commute ($f0^T+0f^T=0$);
$\bar X'_\beta,\bar Z_\alpha$ always commute ($gh+hg=0$); $\bar X_\alpha,\bar Z_\beta$ and
$\bar X'_\alpha,\bar Z'_\beta$ form anticommuting pairs when $\alpha^T\beta\in fh$. Hence two independent
symmetrical blocks ("unprimed" $\bar X_\alpha,\bar Z_\beta$; "primed" $\bar X'_\alpha,\bar Z'_\beta$),
each defining $k/2$ qubits.
- **modality** SymbolicDerivation. **dependencies** E4, E5, E6. **status** checked.

**E8 — claim (constructive enumeration, l.1060).** $Bf=0$ and $gB+hA=0$ are null spaces of $B$ and of
$\begin{bmatrix}B\\A\end{bmatrix}$ respectively; both obtainable by Gaussian elimination. Gaussian
elimination also checks whether $\{\bar X_\alpha,\bar Z_\alpha,\bar X'_\alpha,\bar Z'_\alpha\}$ span all
$k$ qubits modulo stabilizers. Not all $f,g,h$ span all $k$, but valid choices are readily enumerated in
software; all codes in the main-text table admit several such choices.
- **modality** SymbolicDerivation / NumericalSimulation (software enumeration). **status** checked.
- **DOWNSTREAM HOOK**: this is the algorithm our `metrics.css_logicals` mirrors — null spaces of $B$ and
  $[B;A]$ over $\mathbb{F}_2$, then a span/independence check.

**E9 — claim (logical-qubit selection, l.1065).** Enumerate monomial sets $\{n_1,\dots,n_{k/2}\}$ and
$\{m_1,\dots,m_{k/2}\}$ with $n_i^T m_j\in fh$ exactly when $i=j$. Then $\bar X_{n_i},\bar Z_{m_i}$ (and
$\bar X'_{n_i},\bar Z'_{m_i}$) for $i=1\dots k/2$ form $k$ logical qubits ($\bar X_{n_i}$ anticommutes
with $\bar Z_{m_j}$ iff $i=j$). A brute-force search readily finds such $\{n_i\},\{m_i\}$.
- **modality** SymbolicDerivation / NumericalSimulation. **dependencies** E7. **status** checked.

**E10 — datum ($[[144,12,12]]$ minimum-weight $f,g,h$, Table `table:f_polys` l.1068–1121).**
For the gross code there is a choice of $f,g,h$ (monomials with coefficient 1, given pictorially as
$x^iy^j$ dot diagrams in the tex; not transcribable here as numerals) making $\bar X_\alpha=X(\alpha f,0)$
and $\bar Z_\alpha=Z(\alpha h^T,\alpha g^T)$ **minimum-weight** logical Paulis. With
$\{n_i\}=\{1,\,y,\,x^2y,\,x^2y^5,\,x^3y^2,\,x^4\}$ and $\{m_i\}=\{y,\,y^5,\,xy,\,1,\,x^4,\,x^5y^2\}$,
$\bar X_{n_i},\bar Z_{m_j}$ anticommute exactly when $i=j$. This choice yields an ancilla system with
60 qubits per layer (and $\mathcal{G}_{\bar X},\mathcal{G}_{\bar Z}$ with 30 qubits each — see §5).
- **modality** NumericalSimulation (specific verified instance). **status** checked.
- `[HOLE]` (expected: the explicit monomial lists for $f,g,h$). The tex encodes $f,g,h$ only as TikZ dot
  diagrams (l.1073–1115), not as polynomial text. Resolution requires reading the dot coordinates off
  Figure/Table `table:f_polys` or recomputing the null spaces of $B$ and $[B;A]$ for the gross code and
  selecting the minimum-weight representative. **Type**: three explicit elements of $\mathbb{F}_2^{\mathcal{M}}$.

---

## 3. Logical Gates from Automorphisms (`ssec:automorphisms` l.1124–1224)

**E11 — context (definition, l.1127).** An automorphism is a permutation of physical qubits equivalent
to a permutation of the checks (more generally mapping a check to a product of checks). Focus is on
permutations implementable by fault-tolerant circuits within the connectivity already required for
syndrome measurement.

**E12 — claim (admissible permutations, l.1132–1140).** $A,B$ each split into three monomials; each
monomial is a permutation (a vertex-disjoint perfect matching between a data and a check register), so
swaps along it parallelize. A single circuit swaps along $A$-edges ($q(L)\!\leftrightarrow\!q(X)$,
$q(R)\!\leftrightarrow\!q(Z)$) or along $B$-edges ($q(L)\!\leftrightarrow\!q(Z)$,
$q(R)\!\leftrightarrow\!q(X)$). One can route $q(L)\!\to_{A_j^T}\!q(X)\!\to_{A_k}\!q(L)$ and
simultaneously $q(R)\!\to_{A_{k'}}\!q(Z)\!\to_{A_{j'}^T}\!q(R)$, but consistency forces $A_j=A_{j'}$,
$A_k=A_{k'}$. With check registers initialized to $|0\rangle$ and reset between swaps, these circuits
have $\mathsf{CNOT}$ **depth four** and are fault tolerant (errors cannot propagate between physical qubits).
- **modality** SymbolicDerivation + LiteratureGrounded (fault-tolerance argument). **status** checked.

**E13 — claim (these permutations ARE automorphisms, l.1143).** After an `A`-type permutation built from
$A_j,A_k$: qubits permute as $q(L,\alpha)\!\leftrightarrow\!q(L,A_k^TA_j\alpha)$ and
$q(R,\alpha)\!\leftrightarrow\!q(R,A_k^TA_j\alpha)$, transforming Paulis by
$X(P,Q)\to X(A_jA_k^TP,\,A_jA_k^TQ)$. Stabilizers map $X(\alpha A,\alpha B)\to X(\alpha A_jA_k^TA,\,\alpha A_jA_k^TB)$,
i.e. checks are permuted by $\alpha\to\alpha A_jA_k^T$ (same for $Z$). It is an automorphism precisely
because $q(L)$ and $q(R)$ are transformed by the **same** $A_jA_k^T$. `B`-type permutations are
automorphisms by the same argument, permuting checks by $B_jB_k^T$.
- **modality** SymbolicDerivation. **dependencies** E12. **status** checked.

**E14 — claim (logical action = grid translation, l.1145–1147).** By `\lem{connected}` (main text),
shifts $A_jA_k^T$ and $B_jB_k^T$ generate the whole group $\mathcal{M}$ whenever the Tanner graph is
connected. An automorphism given by $s\in\mathcal{M}$ acts as $\bar X_{n_i}\to\bar X_{sn_i}$,
$\bar Z_{m_i}\to\bar Z_{sm_i}$ (and likewise on the primed operators) — a translation of the 2D grid of
logical operators within each block. Critical for addressing all logical qubits.
- **modality** SymbolicDerivation. **dependencies** E7, E13, [AXIOM] `\lem{connected}` (main text, l.843).
  **status** checked (conditional on connectivity).
- **DOWNSTREAM HOOK (LC-equivalence layer)**: this is the symmetry group ($\cong\mathcal{M}$, abelian)
  acting on logical operators; it is the natural group for canonicalizing/comparing logical-operator bases.

**E15 — claim (gate type, l.1149).** One operation per $s\in\mathcal{M}$; since $\mathcal{M}$ is abelian
the implemented subgroup of Clifford gates is abelian. Each $s\neq1$ is nontrivial. Because automorphisms
send $\bar X\to\bar X$ and $\bar Z\to\bar Z$, they are logical $\mathsf{CNOT}$ circuits up to a logical
Pauli correction. (Authors note these are not obviously useful for computation.)
- **modality** SymbolicDerivation. **status** checked.

**E16 — datum (explicit depth-4 circuits, Table `table:automorphisms` l.1151–1223).** The `A`-type and
`B`-type automorphism circuits are listed as $\mathsf{CNOT}$/$\mathsf{init}$ sequences over $\alpha\in\mathcal{M}$.
For $s=A_jA_k^T$ or $s=B_jB_k^T$ the logical action is
$\bar X_\alpha,\bar Z_\alpha,\bar X'_\alpha,\bar Z'_\alpha\to\bar X_{s\alpha},\bar Z_{s\alpha},\bar X'_{s\alpha},\bar Z'_{s\alpha}$.
- **modality** SymbolicDerivation. **status** checked.

---

## 4. ZX-duality / accessing the primed block (`ssec:ZX_duality` l.1226–1289)

**E17 — context (definition, l.1230).** A ZX-duality is a permutation of qubits that commutes with the
stabilizer except it turns $X$ checks into $Z$ checks and vice versa. Implementing the permutation and
then applying Hadamard to all data qubits always acts as a logical gate (`\cite{breuckmann2022foldtransversal}`).
The paper constructs one specific ZX-duality present in **all** BB LDPC codes; other ZX-dualities are
`[FUTURE]`.

**E18 — claim (the canonical ZX-duality, l.1233).** The permutation swapping $q(L,\alpha)$ with
$q(R,\alpha^T)$ for all $\alpha\in\mathcal{M}$ is a ZX-duality: a check $q(X,\beta)$ implementing
$X(\beta A,\beta B)$ becomes connected to $q(L,(\beta B)^T),q(R,(\beta A)^T)$, i.e. the check
$Z(\beta^T B^T,\beta^T A^T)$ — exactly the stabilizer of $q(Z,\beta^T)$. So it exchanges the
$q(X,\beta)$ and $q(Z,\beta^T)$ stabilizers.
- **modality** SymbolicDerivation. **status** checked.

**E19 — claim (logical action of duality+Hadamard, l.1235).** This operation swaps
$\bar X_\alpha=X(\alpha f,0)$ with $\bar Z'_{\alpha^T}=Z(0,\alpha^T f^T)$, and
$\bar Z_\alpha=Z(\alpha h^T,\alpha g^T)$ with $\bar X'_{\alpha^T}=X(\alpha^T g,\alpha^T h)$. Net effect:
swap primed $\leftrightarrow$ unprimed blocks, **transpose** the operator grid, and apply logical
Hadamard to all qubits. Consequence: since logical $X$ of every unprimed qubit is measurable (§5),
this lets one measure logical $Z$ of primed-block qubits.
- **modality** SymbolicDerivation. **dependencies** E7, E18, [AXIOM] `breuckmann2022foldtransversal`.
  **status** checked.
- **DOWNSTREAM HOOK (LC-equivalence layer)**: $\alpha\mapsto\alpha^T$ (group inverse / transpose) is the
  involution relating the two logical blocks and underlies the Hadamard-type LC symmetry of BB codes.

**E20 — claim (fault-tolerant implementation, l.1237–1270).** Implementation factors into (i) exchanging
$q(L)\leftrightarrow q(R)$ via a loop $q(L,\alpha)\to q(X,A_i^T\alpha)\to q(R,B_jA_i^T\alpha)\to q(Z,B_j\alpha)\to q(L,\alpha)$
(a circuit shaped like the automorphism circuits, leaving a residual shift $B_jA_i^T$ removable by another
automorphism); and (ii) the harder permutation $q(L,\alpha)\leftrightarrow q(L,\alpha^T)$ (and the parallel
one on $q(R)$). For (ii): decompose $\mathcal{M}$ via the classification of finite abelian groups; e.g.
$[[90,8,10]]$ with $x^{15}=y^3=1$ has $\mathcal{M}\cong\mathbb{Z}_3\times\mathbb{Z}_5\times\mathbb{Z}_3$,
generators $p,q,r$ with $x=pq$, $y=r$, and $\alpha\mapsto\alpha^T$ inverts each generator exponent. Each
generator-swap uses fault-tolerant nearest-neighbor exchanges (move data onto a blank qubit; never a bare
SWAP of two data qubits — Fig. `fig:duality_implementation` A/B), chained along the abelian decomposition.
- **modality** SymbolicDerivation + LiteratureGrounded. **dependencies** E18, [AXIOM] `breuckmann2022foldtransversal`.
  **status** checked.

**E21 — datum (per-code decompositions, Table `table:duality_implementations` l.1273–1289).** Reduced
abelian-group orders, required generator ratios, and swap-chain lengths:
- $[[72,12,6]]$: $p^2,q^3,r^2,s^3$; ratios $q,s$; chain 4.
- $[[90,8,10]]$: $p^3,q^5,r^3$; ratios $p,q,q^2,r$; chain 6.
- $[[108,8,10]]$: $p^9,q^2,r^3$; ratios $p,p^3,p^5,p^7,r$; chain 9.
- $[[144,12,12]]$: $p^4,q^3,r^2,s^3$; ratios $p,q,s$; chain 6.
- $[[288,12,18]]$: $p^4,q^3,r^4,s^3$; ratios $p,q,r,s$; chain 10.
- $[[360,12,\le24]]$: $p^2,q^3,r^5,s^2,t^3$; ratios $q,ps,psr^2,psr^3,t$; chain 11.
- **modality** NumericalSimulation. **status** checked.

**E22 — claim (cost / depth, l.1265, l.1270).** For $[[144,12,12]]$, $q(L,\alpha)\leftrightarrow q(L,\alpha^T)$
decomposes into a chain of length six; with $(2n-1)$ nearest-neighbor swaps for a length-$n$ chain and
$\mathsf{CNOT}$ depth 12 per swap circuit, the naive depth is $(2\cdot6-1)\cdot12=132$. Because the
intermediate per-generator permutations are not themselves ZX-dualities, error correction generally
cannot run during this operation — much more expensive than the automorphisms, but used sparingly and
likely optimizable.
- **modality** NumericalSimulation / LiteratureGrounded. **status** empirical.
- `[FUTURE]` direct (non-Tanner) ZX-duality implementation via extra qubits — likely sacrifices thickness-2.

---

## 5. Logical Measurements (`ssec:logical_measurements` l.1293–1342)

**E23 — claim (ancilla measurement of $\bar X_1,\bar Z_1$, l.1306–1308).** Using `\cite{cohen2022lowoverhead}`,
one extends the Tanner graph so the extended code contains the target logical operator as a stabilizer,
enabling its fault-tolerant measurement. For $\bar X_1=X(f,0)$: take the subgraph
$\mathcal{G}_{\bar X}=(V_{\bar X},C_{\bar X},E_{\bar X})$ of $q(L,f)$ plus the $q(Z,\alpha)$ checks
supported on it; for $\bar Z_1=Z(h^T,g^T)$: $q(L,h^T),q(R,g^T)$ plus relevant $q(X,\alpha)$. With enough
copies the extended code keeps the original distance. Measuring $\bar X_1,\bar Z_1$ suffices to measure
$\bar X,\bar Z$ of all logical qubits (combined with §3 automorphisms and §4 duality).
- **modality** LiteratureGrounded. **dependencies** E7 (the $f,g,h$ basis), [AXIOM] `cohen2022lowoverhead`.
  **status** conditional.

**E24 — claim (Cohen et al. construction, l.1316–1320, `\edit` self-contained restatement).** To measure
$\bar X$ supported on $V_{\bar X}$, let $C_{\bar X}$ be the $Z$-checks touching $V_{\bar X}$ and $E_{\bar X}$
the connecting edges. Build the ancilla system from `primal layers` isomorphic to $\mathcal{G}_{\bar X}$
and `dual layers` isomorphic to $\mathcal{G}_{\bar X}^T$ (swap the roles of vertices/checks). For parameter
$r$: the final Tanner graph is the BB code plus $r$ dual copies $\mathcal{G}_{\bar X}^T[j]$ ($1\le j\le r$)
and $r-1$ primal copies $\mathcal{G}_{\bar X}[j]$ ($2\le j\le r$), with $\mathcal{G}_{\bar X}[1]$ the
original; add connections pairing $v\!\leftrightarrow\!v^T$, $c\!\leftrightarrow\!c^T$ between
$\mathcal{G}_{\bar X}[j]$–$\mathcal{G}_{\bar X}^T[j]$ ($j\le r$) and $\mathcal{G}_{\bar X}^T[j]$–$\mathcal{G}_{\bar X}[j+1]$ ($j<r$).
`\cite{cohen2022lowoverhead}` shows the result has distance $d$ when $r=d$.
- **modality** LiteratureGrounded. **dependencies** [AXIOM] `cohen2022lowoverhead`. **status** conditional.

**E25 — datum / cost (l.1320).** For $[[144,12,12]]$ the Table `table:f_polys` choice gives
$\mathcal{G}_{\bar X},\mathcal{G}_{\bar Z}$ with 30 qubits each; to reach $d=12$ requires
$2\times30\times(2d-1)=1380$ additional qubits. Authors suspect more efficient variants exist (`[FUTURE]`).
- **modality** NumericalSimulation. **status** empirical.

**E26 — claim (thickness-2 / effective planarity, l.1310–1332).** The $X(f,0)$ ancilla system can connect
to another QEC code (e.g. a surface code), giving a joint $\bar X\bar X$ measurement; with a subsequent
$Z(h^T,g^T)$ measurement and Pauli corrections this realizes quantum teleportation. The construction is
made "effectively planar" — relying on $X(f,0)$ having **no support on $q(R)$** (the reason E7 chose
$Bf=0$) — so that one plane consists only of two-vertex components, leaving them free to connect to a
surface code within an overall thickness-2 embedding. $\mathcal{G}_{\bar Z}$ decomposes into "hairy rings"
in both `A` and `B` planes (no support on $q(Z)$); $\mathcal{G}_{\bar X}$ is connected pairs in the `A`
plane and rings in the `B` plane (no support on $q(X)$).
- **modality** SymbolicDerivation + LiteratureGrounded. **dependencies** E7, [AXIOM] `cohen2022lowoverhead`.
  **status** conditional.
- `[FUTURE]` using more/smaller ancilla systems, or adding connections to $X(g,h),Z(0,f^T)$, to remove the
  error-prone ZX-duality of §4 — unclear whether thickness-2 survives.

---

## 6. Syndrome-measurement circuit (`sec:syndrome_circuit` l.43–200, proof l.226–392)

**E27 — context (l.46–51).** The SM circuit uses $2n$ physical qubits ($n$ data + $n$ check). It is a
periodic sequence of syndrome cycles (SC); a single SC measures the syndromes of all $n$ check operators.
$\mathsf{CNOT}$s act only on Tanner-graph-adjacent pairs.

**E28 — claim (depth-7 SC, l.204).** The SC circuit has effectively $N_r=8$ rounds; ignoring single-qubit
init/measure it is a **depth-7 $\mathsf{CNOT}$ circuit**. Exploiting the symmetries of this explicit code
family reduces depth to 7 from the generic $14=2\cdot6+2$ of `\cite[Theorem 1]{tremblay2022constant}`.
Footnote: with $N_c$ cycles the total SM-circuit depth is $8N_c+1$.
- **modality** LiteratureGrounded + SymbolicDerivation. **dependencies** [AXIOM] `tremblay2022constant`.
  **status** checked.

**E29 — datum (register roles & check action, l.204–211).** Data split into $q(L),q(R)$ (size $n/2$);
check registers $q(X),q(Z)$ (size $n/2$). The $i$-th $X$-check acts on $q(L,A_p(i)),q(R,B_p(i))$, $p=1,2,3$;
the $i$-th $Z$-check on $q(L,B_p^T(i)),q(R,A_p^T(i))$, $p=1,2,3$. ($A_p(i)=j$ means $A_p$ has a 1 at row $i$,
column $j$.) $q(Z)$ qubits are always $\mathsf{CNOT}$ targets ($X$-errors propagate data$\to q(Z)$, read by
$Z$-basis measurement in Round 7); $q(X)$ qubits are always controls ($Z$-errors propagate data$\to q(X)$,
read by $X$-basis measurement in Round 8).
- **modality** SymbolicDerivation. **status** checked.

**E30 — datum (depth-8 SC table, Table `table:syndromecircuit` l.81–200) — the explicit circuit.** Per round
(over $i=1\dots n/2$), the unitary $\mathsf{CNOT}$ part in compact form $\mathsf{CNOT}_M(a,b)$ with
$\{1,2,3,4\}=\{q(X),q(L),q(R),q(Z)\}$ (Eq. `SCunitary_part`, l.256–267):
- Round 1: $\mathsf{CNOT}_{A_1}(3,4)$
- Round 2: $\mathsf{CNOT}_{A_2}(1,2),\ \mathsf{CNOT}_{A_3}(3,4)$
- Round 3: $\mathsf{CNOT}_{B_2}(1,3),\ \mathsf{CNOT}_{B_1}(2,4)$
- Round 4: $\mathsf{CNOT}_{B_1}(1,3),\ \mathsf{CNOT}_{B_2}(2,4)$
- Round 5: $\mathsf{CNOT}_{B_3}(1,3),\ \mathsf{CNOT}_{B_3}(2,4)$
- Round 6: $\mathsf{CNOT}_{A_1}(1,2),\ \mathsf{CNOT}_{A_2}(3,4)$
- Round 7: $\mathsf{CNOT}_{A_3}(1,2)$

(Rounds 1 and 8 additionally do the $\mathsf{init}_X q(X)$, $\mathsf{meas}_Z q(Z)$ / $\mathsf{meas}_X q(X)$,
$\mathsf{init}_Z q(Z)$ housekeeping; $q(Z)$ init at Round 8 feeds Round 1 of the next cycle.)
- **modality** SymbolicDerivation. **status** checked.

**E31 — claim (correctness, l.226–371).** `\begin{}` Tracking the stabilizer tableau (Aaronson–Gottesman),
the $X$-type tableau evolves $\bigl(\begin{smallmatrix}I&0&0&0\\0&A&B&0\end{smallmatrix}\bigr)
\xrightarrow{\text{SC}}\bigl(\begin{smallmatrix}I&A&B&0\\0&A&B&0\end{smallmatrix}\bigr)$, i.e. each weight-1
$X$ stabilizer on a $q(X)$ check qubit is mapped to its product with the corresponding row of $H^X=[A|B]$;
measuring it reveals that check's syndrome, while the code's check operators are unchanged. The round-by-round
derivation (l.270–369) closes via the identity $(A_1+A_3)B+A(B_1+B_2)=A_2B+AB_3$ (both sides sum to $AB$,
and $AB+AB=0$). $Z$-checks follow by Hadamard conjugation (controls$\leftrightarrow$targets). `\end{}`
- **modality** ExactProof — explicit tableau computation. **dependencies** E30, `aaronson2004improved`. **status** checked.

**E32 — claim (logical action is trivial, l.373–381).** For an $X$-logical $X(v)$, $v=(u,w)$ on registers 2,3
with $uB+wA=0$ (commutation with $Z$-checks), the SC circuit maps $(0\,u\,w\,0)$ to $(0\,u\,w\,t)$ with
$t=w(A_1+A_2+A_3)+u(B_1+B_2+B_3)=wA+uB=0$. So the circuit fixes logical $X$ operators (and, by symmetry,
logical $Z$). The SM circuit is therefore logically transparent.
- **modality** ExactProof. **dependencies** E5, E30. **status** checked.

**E33 — datum (non-uniqueness & circuit distance, l.387–391).** A computer search found 935 depth-7
alternatives to the unitary part (936 total) by reordering the $\mathsf{CNOT}_{A_i},\mathsf{CNOT}_{B_j}$ layers.
For $[[144,12,12]]$ all 936 variants give circuit-level distance $d_{\mathrm{circ}}\le10$; the chosen circuit
is conjectured to have $d_{\mathrm{circ}}=10$.
- **modality** NumericalSimulation + Conjectural. **status** empirical / `[HYPOTHESIS]` ($d_{\mathrm{circ}}=10$).

---

## External axioms referenced by this chunk (cited, not reproduced → `[AXIOM]`)
- `breuckmann2022foldtransversal` — fold-transversal gates; ZX-duality-as-logical-gate principle (E1, E17, E19, E20).
- `cohen2022lowoverhead` — low-overhead single-logical-operator measurement via Tanner-graph extension;
  distance-$d$-at-$r=d$ result (E1, E23, E24, E26).
- `tremblay2022constant` [Theorem 1] — generic depth-$(2w+2)$ syndrome-extraction bound, beaten to depth 7 here (E28).
- `\lem{connected}` (this paper, main text l.843) — connectivity ⇒ shifts generate $\mathcal{M}$ (E14).
- `aaronson2004improved` — stabilizer tableau formalism used in the SC correctness proof (E31).

## Open holes / deferred items (markers)
- `[HOLE]` E10: explicit polynomial text of $f,g,h$ for $[[144,12,12]]$ (tex gives only TikZ dot diagrams).
  Type: three elements of $\mathbb{F}_2^{\mathcal{M}}$; resolve by recomputing $\ker B$, $\ker[B;A]$ and
  selecting minimum-weight representatives.
- `[HYPOTHESIS]` E33: $d_{\mathrm{circ}}=10$ for the chosen $[[144,12,12]]$ SC circuit (numerics give $\le10$).
- `[FUTURE]` ancilla-system resource optimization (E3, E25); additional ZX-dualities (E17); direct
  ZX-duality implementation (E22); alternative measurement systems avoiding the ZX-duality (E26).
