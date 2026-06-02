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
| `code:qcode-discovery` | github qiskit-community/qcode-discovery | code | `[HOLE] clone` | reference impl; clone → `ref-code/`, extract file-dep graph |
| `paper:2308.07915` | Bravyi et al. "High-threshold low-overhead FT memory" | paper | `[HOLE] escalate` | **foundational** BB-code definition + MILP-distance baseline |
| `lib:scipy.optimize.milp` | HiGHS via scipy 1.17.1 | code | `SOLID` | available locally; MILP distance backend (matches paper) |
| `lib:numpy` | numpy 1.26.4 | code | `SOLID` | GF(2) linear algebra backend |

Absent locally (escalation/[FUTURE]): `qldpc` v1.0.1, `ldpc` v2.2.0 (BP-OSD),
`python-igraph`+BLISS, `litellm`, `openevolve`. The kernel layer is implemented
in pure numpy/scipy to avoid heavy deps for the load-bearing verifiers (KISS).

## Pipeline component map (the codebase to build — typed ledger of claims)

| # | Component | Paper anchor | Modality target | Risk | Status |
|---|---|---|---|---|---|
| 1 | BB CSS construction `H_X=(A\|B), H_Z=(B^T\|A^T)` | §II.A | ExactProof (algebra) | R2 | `[HOLE]` |
| 2 | PBB non-CSS construction + commutativity `AC^T+BD^T` symmetric | §III.B | ExactProof | R3 | `[HOLE]` |
| 3 | k via GF(2) rank `k=2ℓm-2 rank(H_X)` | §II.A | NumericalSimulation | R2 | `[HOLE]` |
| 4 | CSS MILP distance (scipy/HiGHS) | §V.B, SM MILP | NumericalSimulation/ExactProof(gap=0) | R3 | `[HOLE]` |
| 5 | non-CSS symplectic MILP distance | SM MILP | NumericalSimulation | R3 | `[FUTURE]` |
| 6 | exhaustive weight-w enumeration (Tier 1) | §V.C | ExactProof(small) | R2 | `[FUTURE]` |
| 7 | BP-OSD distance bound + achievable-syndrome sampling | §V.A/C | StatisticalInference | R3 | `[FUTURE]` (needs `ldpc`) |
| 8 | FOM = kd²/n | §II.C | DimensionalConsistency | R0 | `[HOLE]` |
| 9 | evaluation cascade (Stage1 k → Stage2 BP-OSD → Stage3 MILP) | §IV.B | — | R2 | `[FUTURE]` |
| 10 | MAP-Elites generator-ansatz evolution loop | §IV.A | — | R2 | `[FUTURE]` |
| 11 | BLISS colored-Tanner-graph dedup | §VI.A | ExactProof(graph iso) | R2 | `[FUTURE]` (needs igraph/BLISS) |
| 12 | decomposability (Tanner connectivity → direct sum) | §VI.A | ExactProof | R2 | `[FUTURE]` |
| 13 | LC-CSS equivalence (Hadamard 2-coloring + rank cond.) | App.E | ExactProof | R3 | `[FUTURE]` |

## Proof targets (theorem ledger — from the paper)

| Label | Claim | Modality | Evidence target | Status |
|---|---|---|---|---|
| `thm:ab_d2` (App.D) | every BB code with A=B, k>0 has d=2 exactly | ExactProof | proof in paper + `tests/` numeric witness | `[HOLE]` |
| `lem:crt_k` (App.C) | univariate A=1+y+y², B=A(x^{ℓ/3}) ⇒ k=8ℓ/3 (HGP) | ExactProof | proof + `tests/` rank witness over ℓ,m | `[HOLE]` |
| `tillich-zemor` | HGP distance d=min(d1,d2,d1^T,d2^T); dim k=k1k2+k1^Tk2^T | LiteratureGrounded | cite tillich2014quantum (escalate) | `[AXIOM]` |
| `css-commute` | H_X H_Z^T = AB+BA = 0 over F2 (R commutative) | ExactProof | algebra + numeric | `[HOLE]` |
| `pbb-commute` | PBB rows commute iff AC^T+BD^T symmetric over F2 | ExactProof | algebra + numeric | `[HOLE]` |

## Paper formalization progress (live snapshot — refresh ~every 5 iters)

Window 1 (bootstrap): paper acquired + decomposed; kernel layer (components
1,3,4,8 + theorems thm:ab_d2, lem:crt_k) targeted for first verified landmark.
Highest-leverage open node: **component 1+3+4** — without BB construction +
k-rank + CSS MILP distance there is no kernel to admit any discovery.

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

## Audit — AFTER (reusable scripts) — filled at end of window 1
_(see "Reusable scripts" section appended after decomposition + codebase scaffold)_

## Next Tactics
1. `[HOLE]` Decompose paper → chunk_index + digests + theorem/file dependency plans.
2. `[HOLE]` Clone qcode-discovery → ref-code/; extract file-dependency graph.
3. `[HOLE]` Implement kernel: `gf2.py`, `bb_codes.py`, `metrics.py`, `distance_milp.py`.
4. `[HOLE]` Verify landmarks: gross code k=12; thm:ab_d2 d=2; lem:crt_k k=8ℓ/3.
5. `[HOLE]` Seed `results/discovery_timeline.md` from catalogs.
