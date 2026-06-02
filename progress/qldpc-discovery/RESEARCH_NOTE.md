# RESEARCH_NOTE — qldpc-discovery (canonical macro state)

> Canonical typed-ledger view for the BBC auto-discovery reproduction mission.
> Extend in place (note_discipline). Every scientific claim carries context,
> modality, evidence, assumptions, dependencies, status, holes.

## Mission + phase

**Holy grail:** reproduce arXiv:2606.02418 *"Evolutionary Discovery of Bivariate
Bicycle Codes with LLM-Guided Search"* (Cruz-Benito, Cross, Kremer, Faro; IBM) as
a runnable **codebase + pipeline + discovery timeline**. The paper evolves
*generator ansätze* (Python programs emitting polynomial tuples) under MAP-Elites
LLM-guided program synthesis, screens candidates through a staged cascade
(k via GF(2) rank → BP-OSD → MILP), then certifies survivors (MILP exact
distance, BLISS Tanner-graph dedup, decomposability, local-Clifford CSS-equivalence).

**Phase:** `BOOTSTRAP` (window 1 of a multi-window ralph task). Deliver a verified
scientific kernel + decomposition + scaffolded evolutionary loop; the ralph loop
then runs the discovery campaigns. Branch: `bbc`. Commit per substage; no push.

**Invariant (agentic-lean):** the LLM proposes ansätze; the kernel (GF(2) rank,
MILP, exhaustive enumeration, BLISS, LC checks) admits. No code parameter
[[n,k,d]] is "discovered" until its evidence modality + verifier status are recorded.

## Branch
`bbc` (off `main` @ 0e5a878). Commits local-only until the user requests a push.

## Repo audit — BEFORE (2026-06-02, window 1)

State at bootstrap (`git status`: untracked `.claude/`, `phys-agentic-loop/`, `progress/`):
- `phys-agentic-loop/` — methodology repo (Chandra): pipelines 0–6, `_common/`,
  `code_quality_policy.md`, `alignment.md` (PUA/MUSK), note/state templates.
  Generic and reusable; NOT BB-specific. Adapted (not forked) for this mission.
- `.claude/` — `inject_infra.sh` (SessionStart), `inject_alignment.sh`
  (UserPromptSubmit), `ralph_stop_guard.sh` (Stop), `settings.json`,
  `ralph-loop.local.md` (was the stale `classical-shadow` state; **rewritten**
  for the bbc mission, plugin-safe single-block format).
- `progress/prompt/bbc-initial.md` — the task spec.
- No prior Python, no codebase, no ref-paper. Greenfield for the discovery code.

**Reusable-script audit (before):** none present (greenfield). The reusable
surface is the phys-agentic-loop methodology itself (pipeline specs, templates,
markers, code-quality policy). Post-decomposition reusable-script audit → see
"Audit — AFTER".

## Sigma imports (typed ledger — Σ)

| ID | Source | Type | Status | Notes |
|---|---|---|---|---|
| `paper:2606.02418` | `ref-paper/arxiv-2606.02418/src/{paper,supplemental}.tex` | paper | `LiteratureGrounded` | holy-grail; 42pp; decomposed in `reformulate/qldpc-discovery/paper_2606.02418/` |
| `code:qcode-discovery` | github qiskit-community/qcode-discovery | code | `refuted-as-source` | cloned (sha 4a9520e) — EMPTY (README only); reproduce from paper text |
| `paper:2308.07915` | Bravyi et al. "High-threshold low-overhead FT memory" | paper | `LiteratureGrounded` | **foundational**; acquired + decomposed (`reformulate/.../paper_2308.07915/`) |
| `lib:scipy.optimize.milp` | HiGHS via scipy 1.17.1 | code | `SOLID` | available locally; MILP distance backend (matches paper) |
| `lib:numpy` | numpy 1.26.4 | code | `SOLID` | GF(2) linear algebra backend |

Installed via escalation (iter 9): `ldpc` 2.4.1 (BP-OSD), `python-igraph` 1.0.0 (BLISS).
Still absent (not needed): `qldpc`, `litellm`, `openevolve` — external-LLM-at-scale is `[FUTURE]`
(resource-gated; Claude Code served as the LLM mutation operator). Kernel is pure numpy/scipy (KISS).

## Pipeline component map (the codebase to build — typed ledger of claims)

| # | Component | Paper anchor | Modality target | Risk | Status |
|---|---|---|---|---|---|
| 1 | BB CSS construction `H_X=(A\|B), H_Z=(B^T\|A^T)` | §II.A | ExactProof (algebra) | R2 | `[SOLID]` `bb_codes` |
| 2 | PBB non-CSS construction + commutativity `AC^T+BD^T` symmetric | §III.B | ExactProof | R3 | `[SOLID]` `pbb_codes` |
| 3 | k via GF(2) rank `k=2ℓm-2 rank(H_X)` | §II.A | NumericalSimulation | R2 | `[SOLID]` `metrics` |
| 4 | CSS MILP distance (scipy/HiGHS) | §V.B, SM MILP | NumericalSimulation/ExactProof(gap=0) | R3 | `[SOLID]` `distance_milp` |
| 5 | non-CSS symplectic MILP distance | SM MILP | NumericalSimulation | R3 | `[SOLID]` (iter 2) |
| 6 | exhaustive weight-w enumeration (Tier 1) | §V.C | ExactProof(small) | R2 | `[SOLID]` `distance_enum` |
| 7 | BP-OSD distance bound + achievable-syndrome sampling | §V.A/C | StatisticalInference | R3 | `[SOLID]` `distance_bposd` (ldpc installed; coset bug fixed iter 15) |
| 8 | FOM = kd²/n | §II.C | DimensionalConsistency | R0 | `[SOLID]` `metrics.fom` |
| 9 | evaluation cascade (Stage1 k → Stage2 BP-OSD → Stage3 MILP) | §IV.B | — | R2 | `[SOLID]` `evaluation`+`search` |
| 10 | generator-ansatz program evolution (GA-G + Claude-LLM operator) | §IV.A | — | R2 | `[SOLID]` `evolve`/`search` (ext-LLM-at-scale `[FUTURE]`, resource-gated) |
| 11 | BLISS colored-Tanner-graph dedup | §VI.A | ExactProof(graph iso) | R2 | `[SOLID]` `dedup` (igraph installed) |
| 12 | decomposability (Tanner connectivity → direct sum) | §VI.A | ExactProof | R2 | `[SOLID]` `tanner` |
| 13 | LC-CSS equivalence (Hadamard 2-coloring + rank cond.) | App.E | ExactProof | R3 | `[SOLID]` `clifford_equiv` (to paper-parity; gaps (a),(b) are the paper's own) |

## Proof targets (theorem ledger — from the paper)

| Label | Claim | Modality | Evidence target | Status |
|---|---|---|---|---|
| `thm:ab_d2` (App.D) | every BB code with A=B, k>0 has d=2 exactly | ExactProof | `theorems.verify_ab_d2` + MILP | `[SOLID]` |
| `lem:crt_k` (App.C) | univariate A=1+y+y², B=A(x^{ℓ/3}) ⇒ k=8ℓ/3 (HGP) | ExactProof | `theorems.verify_crt_k` (ℓ=3,6,9,12) | `[SOLID]` |
| `tillich-zemor` | HGP distance d=min(d1,d2,d1^T,d2^T); dim k=k1k2+k1^Tk2^T | LiteratureGrounded | cite tillich2014quantum | `[AXIOM]` (imported; permanent) |
| `css-commute` | H_X H_Z^T = AB+BA = 0 over F2 (R commutative) | ExactProof | `bb_codes._validate_css` (numeric, all codes) | `[SOLID]` |
| `pbb-commute` | PBB rows commute iff AC^T+BD^T symmetric over F2 | ExactProof | `pbb_codes` Gram + reduced check | `[SOLID]` |

## Paper formalization progress (live snapshot — refresh ~every 5 iters)

**Window 1, iter 7 — full pipeline APPARATUS built (34 tests green).** Status:
- PROVEN: 1 BB-construction, 2 PBB-construction, 3 k-rank, 4 CSS-MILP, 5 symplectic-MILP,
  6 enumeration, 8 FOM, 9 evaluation-cascade, 10 blind-search (GA/MAP-Elites-lite), 12 decomposability.
- PARTIAL: 11 dedup (sound lattice-symmetry fallback; full BLISS/igraph [FUTURE]),
  13 LC-CSS (Hadamard 2-coloring + rank cond; uniform-S/{I,S}/{H,HS} enumeration [FUTURE]).
- [FUTURE]: 7 BP-OSD (needs `ldpc`). Theorems thm:ab_d2, lem:crt_k: [SOLID].

**Central theme achieved end-to-end:** blind discovery (no paper) → validate (held-out catalog),
both families — CSS [[72,12,6]] UB_CONSISTENT vs Bravyi; non-CSS [[36,2,6]] EXACT MATCH vs PBB catalog.
Highest-leverage next node: scale blind CSS search to **n=144** (target gross [[144,12,12]] vs catalog)
+ wire dedup into campaign post-processing for honest distinct-counts.

## Paper ingestion record (write-once)
- 2026-06-02: arXiv:2606.02418 e-print acquired (`PROVENANCE.md`), 42pp,
  decomposed into `reformulate/qldpc-discovery/paper_2606.02418/` + chunk digests.

## Open questions for human owner
- `[FUTURE]` BP-OSD (component 7) needs `ldpc` v2.2.0; install or keep MILP-only?
- `[FUTURE]` BLISS dedup (component 11) needs `python-igraph`; install or
  implement a networkx/naive canonical-form fallback?
- Escalation budget: how many cited dependency papers to decompose (bravyi2024high
  is mandatory; tillich2014quantum, cross2025small, khesin2026mirror optional)?

## Audit references
- `ref-paper/arxiv-2606.02418/` (tex source + PROVENANCE.md + chunk_index.md + digest/)
- `reformulate/qldpc-discovery/paper_2606.02418/` (decomposition)
- `ref-code/` (qcode-discovery clone; gitignored mirror) — file-dep in
  `reformulate/qldpc-discovery/paper_2606.02418/file_dependency_plan.md`

## Audit — AFTER decomposition (reusable scripts)

Post-decomposition reusable surface now in-tree (window 1):
- **Kernel modules (`src/qcode_discovery/`)** — reusable across every campaign and every
  future BB/PBB paper: `gf2` (F2 algebra), `polynomials` (ring R + circulants),
  `bb_codes`/`pbb_codes` (construction), `metrics` (k, logicals, FOM), `distance_milp`
  (CSS MILP), `distance_enum` (independent cross-check), `tanner` (decomposability),
  `theorems` (witness factory). These ARE the "scientific kernel" the loop reuses.
- **`scripts/code_quality_audit.py`** — reusable static diagnostic (self-evolution pt 4),
  run in every iter's VERIFY step; returns nonzero on CRITICAL/HIGH.
- **`tests/test_kernel.py`** — reusable regression harness; new components add tests here.
- **Reference-repo finding:** `qcode-discovery` is EMPTY (README only) → NO external code to
  reuse; the file-dependency graph is derived from the paper (`file_dependency_plan.md`).
- **Reusable across papers:** the kernel is paper-agnostic (any BB/PBB-style code over a
  group-algebra quotient ring). arXiv:2308.07915 (acquired) and future escalation papers
  plug into the same `BBCode`/`PBBCode` + distance/dedup verifiers.

Gaps to build (reuse-first, per `file_dependency_plan.md` / `bundle_dependency_plan.md`):
`symplectic_distance_milp` (extend `distance_milp`), `evaluation.py` (cascade),
`evolve.py` (MAP-Elites + ansatz), `bliss_dedup.py` (needs igraph; networkx fallback),
`clifford_equiv.py` (Hadamard 2-coloring + LC rank cond), `distance_bposd.py` (needs ldpc).

## Next Tactics

**DONE (iters 1–14):** decomposition (both papers) · kernel (all 13 components PROVEN; LC to
paper-parity) · blind discovery (CSS+PBB) → post-hoc validation (catalog matches both families) ·
3-stage cascade (BP-OSD+trust+MILP) · BLISS dedup (exact) · escalation install (ldpc+igraph) ·
README · all paper signature findings reproduced.

**Open (incremental):**
1. `[SOLID]` (iter 15, DONE) gross [[144,12,12]] d=12 kernel-verified (BP-OSD=12 + MILP weight-12).
2. `[FUTURE]` component 13 non-uniform `{SH,HSH}` / cross-class LC patterns — the paper's OWN
   admitted coverage gaps (a),(b); not a reproduction shortfall.
3. `[FUTURE]` wider blind campaigns → larger consolidated BLISS-deduped catalog at n=144–360.
4. `[FUTURE]` self-evolution window: repo-structure tidy + knowledge-base expansion ergonomics.
5. `[FUTURE]` decode `sec:decoder`/`sec:numerics` of Bravyi if circuit-level work is later needed.
