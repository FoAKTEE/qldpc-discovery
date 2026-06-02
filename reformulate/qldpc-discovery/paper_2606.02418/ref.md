# ref.md — References used (semi-)directly by arXiv:2606.02418

Source paper: arXiv:2606.02418 "Evolutionary Discovery of Bivariate Bicycle Codes with
LLM-Guided Search" (Cruz-Benito, Cross, Kremer, Faro; IBM Research; PRX Quantum).
Bib source: `ref-paper/arxiv-2606.02418/src/references.bib`.

Scope: only references the reformulation uses **(semi-)directly** — i.e. cited at a
load-bearing point (construction, distance theory, decoder, equivalence, evolution
engine, or solver/library). Related-work-only citations (e.g. yoder2025tour,
voss2025multivariate, RL-discovery papers) are excluded by design.

Modality (typed-ledger): every entry below is `LiteratureGrounded` — these are imported
external results/tools, not reproduced here. CITED-but-not-reproduced theorems whose
correctness the paper *relies on* are additionally flagged `[AXIOM]`. Escalation priority
is MANDATORY when the cited result is on the critical path of a proof or method gate we
must reconstruct; optional when it contextualizes; none when purely a tool/citation hook.

Status marker legend (see `_common/markers.md`): `[AXIOM]` = imported postulate, results
stay conditional on it; `[SOLID]` = used as a stable tool/fact with no open obligation.

---

## (1) Construction / distance theory

### bravyi2024high — `[AXIOM]` — escalation: MANDATORY
- **type**: external-paper (Nature 627:778, 2024; arXiv:2308.07915).
- **claim**: BB CSS code definition (trinomials A,B over R=F2[x,y]/(x^l-1,y^m-1);
  H_X=(A|B), H_Z=(B^T|A^T)); the MILP minimum-weight-logical baseline formulation;
  the gross code [[144,12,12]] reference landmark.
- **role in paper**: defines the object class being searched; supplies the MILP distance
  formulation the paper reuses (SM); benchmark code in CSS/PBB catalog tables.
- **evidence**: LiteratureGrounded.
- **provenance / tex**: `supplemental.tex` l.151, l.344, l.427, l.487, l.529, l.535,
  l.573, l.661 (MILP); `paper.tex` l.116, l.127, l.165, l.309.
- **dependencies**: anchors css-commute, thm:ab_d2, lem:crt_k, eq:milp_obj.
- **escalation rationale**: BB definition + MILP baseline are on the critical path of
  every construction/verification claim. Ground-truth marks this MANDATORY.

### tillich2014quantum — `[AXIOM]` — escalation: MANDATORY
- **type**: external-paper (IEEE TIT 60(2):1193, 2014; arXiv:0903.0566).
- **claim**: hypergraph-product (HGP) construction; HGP minimum distance
  d = min(d_1, d_2, d_1^T, d_2^T); HGP dimension k = k_1 k_2 + k_1^T k_2^T.
- **role in paper**: BB(A,B) ~ HGP(H_B, H_A^T); the distance and dimension formulas are
  the engine of lem:crt_k (k = 8l/3) and the univariate d in {2,4} bound. Treated as
  CITED (tillich-zemor [AXIOM]) per ground truth.
- **evidence**: LiteratureGrounded.
- **provenance / tex**: `paper.tex` l.409 (distance formula), l.420 (dim formula),
  l.1015 (HGP equivalence + dim); `supplemental.tex` l.250.
- **dependencies**: lem:crt_k, App C, App D distance argument.
- **escalation rationale**: distance/dim formulas are load-bearing for the App C/D
  theorems; must be reconstructed or imported as axiom.

### panteleev2022quantum — escalation: optional
- **type**: external-paper (IEEE TIT 68(1):213, 2022; arXiv:2012.04068).
- **claim**: lifted-product qLDPC codes with almost-linear minimum distance.
- **role in paper**: BB codes characterized as abelian lifted-product codes over
  Z_l x Z_m; situates BB family in the qLDPC hierarchy.
- **evidence**: LiteratureGrounded.
- **provenance / tex**: `paper.tex` l.116.
- **dependencies**: contextual framing of the code family; not a proof input.

### macwilliams1977theory — `[AXIOM]` — escalation: optional
- **type**: textbook (North-Holland, 1977).
- **claim**: standard cyclic-code identity: for an NxN circulant H with polynomial
  f(z) in F2[z]/(z^N-1), dim ker H = deg gcd(f, z^N-1).
- **role in paper**: supplies the kernel-dimension identity used inside lem:crt_k
  (k_A = k_A^T = 2, k_B = k_B^T = 2l/3).
- **evidence**: LiteratureGrounded.
- **provenance / tex**: `paper.tex` l.1015 (App C).
- **dependencies**: lem:crt_k.

### kapshikar2022hardness — escalation: optional
- **type**: external-paper (IEEE TIT 69(10):6293, 2023; arXiv:2203.04262).
- **claim**: computing the minimum distance of a (quantum/CSS) stabilizer code is
  NP-hard in general.
- **role in paper**: motivates the use of MILP (exact-with-certificate) over polynomial
  heuristics for distance, and the staged verification cascade.
- **evidence**: LiteratureGrounded.
- **provenance / tex**: `paper.tex` l.126, l.323.
- **dependencies**: justifies eq:milp_obj method choice; not a proof input.

---

## (2) Decoders / distance bounding

### panteleev2021degenerate — escalation: optional
- **type**: external-paper (Quantum 5:585, 2021; arXiv:1904.02703).
- **claim**: BP-OSD decoder for degenerate qLDPC codes with good finite-length
  performance.
- **role in paper**: half of the BP-OSD pair used for Stage-2 distance UPPER bounds;
  OSD-CS order-7, product-sum, 20 BP iterations.
- **evidence**: LiteratureGrounded.
- **provenance / tex**: `paper.tex` l.127, l.165, l.309; `supplemental.tex` l.329.
- **dependencies**: Stage-2 cascade; trust filter d/sqrt(n).

### roffe2020decoding — escalation: optional
- **type**: external-paper (Phys. Rev. Research 2:043423, 2020).
- **claim**: decoding across the qLDPC landscape (BP-OSD methodology).
- **role in paper**: other half of the BP-OSD citation pair for Stage-2 distance
  estimation (stochastic upper bounds).
- **evidence**: LiteratureGrounded.
- **provenance / tex**: `paper.tex` l.127, l.309; `supplemental.tex` l.329.
- **dependencies**: Stage-2 cascade.

### ldpc_library — `[SOLID]` — escalation: none (tool)
- **type**: software (Roffe, `quantumgizmos/ldpc`, v2.2.0).
- **claim**: Python BP-OSD implementation exposing multiple BP variants / OSD methods.
- **role in paper**: the executable BP-OSD used in the pipeline; defaults max_iter=n, no
  damping, depolarizing rate 1e-3.
- **evidence**: LiteratureGrounded (tool).
- **provenance / tex**: `paper.tex` l.127, l.280, l.316.
- **dependencies**: Stage-2; LOCAL ENV note: ldpc MISSING locally (v2.2.0).

### webster2026distance — escalation: optional
- **type**: external-paper preprint (arXiv:2603.22532, 2026).
- **claim**: systematic benchmark of heuristic and exact distance-finding algorithms for
  quantum codes/circuits; BP-OSD fails to find correct distance for codes as small as
  [[48,5,10]] without enhanced sampling; DEM-permutation / random-stabilizer effects.
- **role in paper**: external corroboration of the paper's BP-OSD-overestimation finding
  and of the choice of exact MILP; concurrent benchmark.
- **evidence**: LiteratureGrounded.
- **provenance / tex**: `paper.tex` l.128, l.317, l.322, l.699.
- **dependencies**: validates Sec.V trust-filter / verification claims.

---

## (3) Equivalence / canonical labeling

### junttila2007engineering — `[SOLID]` — escalation: optional
- **type**: external-paper (ALENEX 2007) / algorithm (BLISS).
- **claim**: BLISS canonical-labeling algorithm for large sparse colored graphs.
- **role in paper**: the dedup engine — colored Tanner graph canonical form gives
  225 reps -> 97 distinct CSS, 720 -> 368 PBB (Sec.VI.A).
- **evidence**: LiteratureGrounded.
- **provenance / tex**: `paper.tex` l.96, l.280, l.381; `supplemental.tex` l.50.
- **dependencies**: dedup counts; the 465 = 97 + 368 total.

### cross2025small — `[AXIOM]` — escalation: MANDATORY
- **type**: external-paper preprint (arXiv:2501.17447, 2025).
- **claim**: Lemma 7.4 — a stabilizer code S is CSS iff rank[X|Z] = rank X + rank Z over
  GF(2) (attributed to T. Yoder); small binary stabilizer subsystem codes / Clifford
  reduction context.
- **role in paper**: the group-level CSS test used in the LC-CSS equivalence analysis
  (App E); 11/368 PBB codes found CSS-equivalent.
- **evidence**: LiteratureGrounded; proof referred to source (not reproduced).
- **provenance / tex**: `paper.tex` l.189, l.1036 (App E / App lc).
- **dependencies**: App E LC-CSS result (357 CSS-inequivalent).
- **escalation rationale**: Lemma 7.4 is the decision predicate of the App E result;
  proof imported as axiom -> MANDATORY to verify or cite-as-axiom.

### khesin2026mirror — escalation: optional
- **type**: external-paper preprint (arXiv:2603.05496, 2026).
- **claim**: mirror codes — non-CSS construction over abelian groups; weight-6
  parameters [[60,4,10]], [[85,8,9]]; a parity 2-coloring in the mirror setting.
- **role in paper**: (a) comparison family for PBB non-CSS codes ([[108,8,10]] FOM 7.4
  matches highest-FOM mirror code); (b) the App-E Hadamard 2-coloring is "inspired by"
  but proven independently here; (c) open problem on non-CSS syndrome-extraction
  circuits.
- **evidence**: LiteratureGrounded.
- **provenance / tex**: `paper.tex` l.121, l.189, l.605, l.625, l.740, l.1043.
- **dependencies**: App E 2-coloring (re-derived directly, so NOT an axiom dependency).

### babai2016graph — escalation: none
- **type**: external-paper (STOC 2016).
- **claim**: graph isomorphism is solvable in quasi-polynomial time.
- **role in paper**: complexity caveat on BLISS dedup — GI is quasi-poly worst case but
  BLISS is efficient in practice; also frames code-equivalence hardness.
- **evidence**: LiteratureGrounded.
- **provenance / tex**: `paper.tex` l.383, l.389.
- **dependencies**: contextual caveat on Sec.VI.A dedup; not load-bearing for a claim.

---

## (4) Program evolution / search

### romera2024funsearch — escalation: optional
- **type**: external-paper (Nature 625:468, 2024).
- **claim**: FunSearch — LLMs as mutation operators in evolutionary program search
  (cap-set, bin-packing discoveries).
- **role in paper**: the conceptual basis of the LLM-guided search method; "technical
  basis is FunSearch via OpenEvolve."
- **evidence**: LiteratureGrounded.
- **provenance / tex**: `paper.tex` l.74, l.142.
- **dependencies**: Sec.III-IV method framing.

### novikov2025alphaevolve — escalation: optional
- **type**: external-paper preprint (arXiv:2506.13131, 2025).
- **claim**: AlphaEvolve — extends FunSearch from single functions to multi-file
  codebases with LLM-guided cross-module mutations.
- **role in paper**: second conceptual inspiration for the evolution pipeline; motivates
  evolving a multi-component generator ansatz.
- **evidence**: LiteratureGrounded.
- **provenance / tex**: `paper.tex` l.74, l.143.
- **dependencies**: Sec.III-IV method framing.

### openevolve — `[SOLID]` — escalation: optional (engine)
- **type**: software (Sharma, `codelion/openevolve`, 2025).
- **claim**: open-source evolutionary coding agent implementing MAP-Elites for LLM-guided
  program synthesis.
- **role in paper**: the actual evolution engine driving all 5 campaigns (~1650 iters,
  ~2e5 candidates); MAP-Elites dims = (#lattices with k>=8 codes, total such codes).
- **evidence**: LiteratureGrounded (tool).
- **provenance / tex**: `paper.tex` l.74, l.144, l.220.
- **dependencies**: entire campaign methodology; LOCAL ENV: openevolve MISSING locally.

### mouret2015illuminating — escalation: none
- **type**: external preprint (arXiv:1504.04909, 2015).
- **claim**: MAP-Elites — illuminating search spaces by mapping elites (quality-diversity
  archive over behavior descriptors).
- **role in paper**: the search algorithm OpenEvolve implements; defines the elite-archive
  semantics of the campaign behavior dimensions.
- **evidence**: LiteratureGrounded.
- **provenance / tex**: `paper.tex` l.220.
- **dependencies**: MAP-Elites archive definition.

---

## (5) Solvers / libraries

### huangfu2018highs — `[SOLID]` — escalation: optional (solver)
- **type**: external-paper (Math. Prog. Comput. 10(1):119, 2018) / solver (HiGHS).
- **claim**: parallel dual revised simplex; the HiGHS MILP/LP solver backend.
- **role in paper**: solves eq:milp_obj (exact CSS + symplectic non-CSS distance MILP);
  exact when MIP gap = 0; accessed via scipy.optimize.milp.
- **evidence**: LiteratureGrounded (tool).
- **provenance / tex**: `paper.tex` l.280, l.327; `supplemental.tex` l.672.
- **dependencies**: Stage-3 MILP; LOCAL ENV: scipy.optimize.milp = HiGHS, present.

### virtanen2020scipy — `[SOLID]` — escalation: none (tool)
- **type**: external-paper (Nature Methods 17(3):261, 2020) / library (SciPy).
- **claim**: SciPy fundamental scientific-computing algorithms; `scipy.optimize.milp`
  HiGHS wrapper.
- **role in paper**: the Python entry point to HiGHS for all MILP distance computations.
- **evidence**: LiteratureGrounded (tool).
- **provenance / tex**: `paper.tex` l.280, l.327; `supplemental.tex` l.672.
- **dependencies**: Stage-3 MILP harness; LOCAL ENV: scipy 1.17.1 present.

### csardi2006igraph — `[SOLID]` — escalation: none (tool)
- **type**: external-paper (InterJournal Complex Systems 1695, 2006) / library
  (python-igraph).
- **claim**: igraph software package for complex-network research (carries the BLISS
  binding used for canonical labeling).
- **role in paper**: python-igraph + BLISS performs Tanner-graph canonical labeling for
  dedup (Sec.VI.A).
- **evidence**: LiteratureGrounded (tool).
- **provenance / tex**: `paper.tex` l.280.
- **dependencies**: dedup pipeline; LOCAL ENV: igraph MISSING locally.

### litellm — `[SOLID]` — escalation: none (tool)
- **type**: software (BerriAI, `BerriAI/litellm`, 2024).
- **claim**: unified proxy to call all LLM APIs in OpenAI format.
- **role in paper**: the proxy through which cloud LLMs were accessed during evolution
  (ensemble campaigns, Gemini 3 Flash).
- **evidence**: LiteratureGrounded (tool).
- **provenance / tex**: `paper.tex` l.282.
- **dependencies**: campaign LLM access; LOCAL ENV: litellm MISSING locally.

---

## Escalation summary (MANDATORY first)

| key | group | marker | escalation |
|---|---|---|---|
| bravyi2024high | construction | [AXIOM] | MANDATORY |
| tillich2014quantum | distance | [AXIOM] | MANDATORY |
| cross2025small | equivalence | [AXIOM] | MANDATORY |
| panteleev2022quantum | construction | — | optional |
| macwilliams1977theory | distance | [AXIOM] | optional |
| kapshikar2022hardness | distance | — | optional |
| panteleev2021degenerate | decoder | — | optional |
| roffe2020decoding | decoder | — | optional |
| webster2026distance | decoder | — | optional |
| junttila2007engineering | equivalence | [SOLID] | optional |
| khesin2026mirror | equivalence | — | optional |
| romera2024funsearch | evolution | — | optional |
| novikov2025alphaevolve | evolution | — | optional |
| openevolve | evolution | [SOLID] | optional |
| huangfu2018highs | solver | [SOLID] | optional |
| ldpc_library | decoder | [SOLID] | none |
| babai2016graph | equivalence | — | none |
| mouret2015illuminating | evolution | — | none |
| virtanen2020scipy | solver | [SOLID] | none |
| csardi2006igraph | solver | [SOLID] | none |
| litellm | solver | [SOLID] | none |

[FUTURE] If App C/D/E proofs are reconstructed natively, the three [AXIOM] entries
(bravyi2024high, tillich2014quantum, cross2025small) must be re-typed from
LiteratureGrounded toward ExactProof; until then all derived results stay conditional.
