---
active: true
iteration: 11
session_id: ""
max_iterations: 300
completion_promise: "QLDPC_BBC_DISCOVERY_PIPELINE_COMPLETE"
started_at: "2026-06-02T08:00:00Z"
role: Ralph-loop local state for qldpc-discovery (BBC auto-discovery reproduction)
scope: .claude/ralph-loop.local.md — surfaced on SessionStart by inject_infra.sh, gated on Stop by ralph_stop_guard.sh (native) and the ralph-loop plugin stop-hook (plugin-safe single-block format)
mission_paper: "arXiv:2606.02418 — Evolutionary Discovery of Bivariate Bicycle Codes with LLM-Guided Search"
branch: bbc
pua_flavor: "musk"
discipline:
  - ../phys-agentic-loop/alignment.md (binding operational rules; MUSK mode always on)
  - ../phys-agentic-loop/code_quality_policy.md (R0-R4 risk tiers, KISS/DRY/AHA, FINDING SCHEMA, anti-patterns — BOUND INTO THIS PIPELINE)
  - ../phys-agentic-loop/_common/agentic_lean_contract.md (typed-ledger admission gates)
  - ../phys-agentic-loop/_common/progress_principles.md (promise-tag rule, per-substage commit cadence)
  - ../phys-agentic-loop/_common/markers.md (HYPOTHESIS/PRELIMINARY/SOLID/BLOCKING/FUTURE/HOLE/AXIOM/NONCOMPUTABLE)
  - ../phys-agentic-loop/_common/note_discipline.md (extend-in-place; bidirectional criterion)
  - ../phys-agentic-loop/pipelines/0-source-import/spec.md (import gate; code-quality discipline binding)
  - ../phys-agentic-loop/pipelines/6-escalation/spec.md (cross-paper / external-code acquisition)
multi_window_task:
  active: true
  window_count: 1
  max_windows: 10
  closing: false
  task_description: "Reproduce the arXiv:2606.02418 BB-code auto-discovery pipeline as a runnable codebase + discovery timeline."
  task_started_at_iter: 1
self_prompting_policy:
  policy: "user directive 2026-06-02 (bbc-initial.md)"
  rule: |
    Self-prompting of the phys-agentic-loop is OFF during this long
    multi-iteration run. Self-evolution / self-correction of `.claude` and
    `phys-agentic-loop` fires only every 5-10 1M-context windows (a
    self-evolution window), NOT every iter. Intermediate windows
    (closing=false) are LIGHTWEIGHT per multi_window_tolerance: no
    enforce-reading, no methodology re-injection; only `pytest`/verifier PASS
    is the hard gate. Full discipline returns on the FINAL window (closing=true).
escalation_policy:
  policy: "user directive 2026-06-02 (bbc-initial.md SELF-EVOLUTION) — INJECTED TO INFRA"
  rule: |
    You are ALLOWED and ENCOURAGED to search for useful papers and code and
    download them: tex -> ref-paper/arxiv-<id>/src/ (rule 8), repos ->
    ref-code/<owner>-<repo>/ (read-only mirror, gitignored). Then run
    pipeline-0 decomposition (chunk_index + digest + theorem/file dependency
    rows in reformulate/qldpc-discovery/paper_<id>/). Fire escalation
    (pipelines/6-escalation) whenever an ingredient (construction, distance
    method, equivalence test, decoder) is missing or an external_axioms entry
    goes [ACTIVE]. Record the trigger in the iter loop note BEFORE acquiring.
blind_discovery_policy:
  policy: "user directive 2026-06-02 (CENTRAL THEME) — BINDING"
  rule: |
    Discovery must run BLIND: the auto-discovery pipeline rediscovers codes WITHOUT any
    knowledge extracted from the paper. Run the blind search FIRST; only AFTER do we
    double-check against the paper.
    - KERNEL (construction, k via rank, MILP/enum distance, FOM, dedup, LC) = the verifier
      apparatus; deriving it from the paper's METHOD is allowed.
    - SEARCH (seed ansatz, evolution/GA/random) must NOT seed from the paper's discovered
      polynomials, must NOT hardcode any reported [[n,k,d]], must NOT import the catalog
      tables (css_catalog_tables.tex / pbb_catalog_tables.tex). Seeds are naive/generic.
    - `src/qcode_discovery/evaluation.py` + `search.py`/`evolve.py` are catalog-blind.
      A separate `validation.py` reads the catalog ONLY post-hoc to compare discovered vs
      reported (overlap, novelty, did-we-find-the-gross-code).
    - Every discovered [[n,k,d]] is logged to results/discovery_timeline.md with verifier
      status BEFORE any paper comparison. The catalog is a HELD-OUT TEST SET.
self_evolution_policy:
  policy: "user directive 2026-06-02 (bbc-initial.md SELF-EVOLUTION)"
  rule: |
    Every 5-10 windows, run ONE self-evolution window that may: (1) refine
    self-prompting; (2) optimize the phys-agentic-loop workflow; (3) restructure
    folders/files so same-kind files live together (no mixed types) and the
    knowledge base is easy to expand; (4) extend the python code-quality
    diagnostics (scripts/code_quality_audit.py) used to filter/diagnose code.
tracking_files:
  canonical: "progress/qldpc-discovery/RESEARCH_NOTE.md"
  per_iter: "progress/qldpc-discovery/loop_notes/current_iter.md"
  medium: "progress/qldpc-discovery/medium_term.md"
  agentic_state: "progress/qldpc-discovery/agentic_lean_state.md"
  external_axioms: "progress/qldpc-discovery/external_axioms.md"
  timeline: "results/discovery_timeline.md"
  theorem_plan: "reformulate/qldpc-discovery/paper_2606.02418/theorem_dependency_plan.md"
  file_plan: "reformulate/qldpc-discovery/paper_2606.02418/file_dependency_plan.md"
  chunk_index: "ref-paper/arxiv-2606.02418/chunk_index.md"
---

# Ralph loop — qldpc-discovery (BBC auto-discovery reproduction)

**Holy grail (arXiv:2606.02418):** reproduce, as a runnable codebase + pipeline,
the LLM-guided evolutionary discovery of bivariate-bicycle (BB) and perturbed-BB
(PBB) quantum LDPC codes, plus a timeline of discovered code results. The LLM
proposes; the scientific kernel (GF(2) rank, MILP distance, BLISS, LC checks)
admits. Branch: `bbc`. Commit per substage; do NOT push.

Canonical state: `progress/qldpc-discovery/RESEARCH_NOTE.md` (read its
"Next Tactics" + "Paper formalization progress" at the start of EVERY iter).

## Each iteration (7-step loop; PLAN/EDIT/VERIFY/COMMIT/UPDATE/ESCALATE/DO-NOT-STOP)

1. **PLAN** — Read RESEARCH_NOTE.md + `theorem_dependency_plan.md` +
   `file_dependency_plan.md`. Pick the SINGLE highest-leverage open
   `[HOLE]`/`[BLOCKING]`/`[PRELIMINARY]` node. State it as
   `Gamma |- ?hole : Evidence <modality> <claim>` and cite the paper anchor
   (section / theorem label / pipeline component) it implements. Classify the
   risk tier (R0-R4) per `code_quality_policy.md`.

2. **EDIT** — Implement that ONE node as a tactic output (candidate step,
   subgoals, evidence object, verifier command). Prefer one module under
   `src/qcode_discovery/`. Try-to-implement discipline: no stub without a
   `[FUTURE iter N+]` marker citing the specific obstacle. Apply KISS/DRY/AHA;
   docstring carries paper anchor + risk tier (<= 8 lines, no iter-number rot).

3. **VERIFY** — Run `python -m pytest -q` (and any node-specific check), tee to
   `progress/qldpc-discovery/loop_notes/current_iter.md`. The verifier output
   MUST include a `code_quality_policy_pass:` line listing each new declaration's
   risk tier + status (PROVEN / PARTIAL / PLACEHOLDER). REJECT the iter (no
   commit) on a red build or an undocumented stub. No untyped scientific claim:
   every result carries context, claim, modality, verifier status.

4. **COMMIT (no push)** — Commit on branch `bbc` (verify with
   `git rev-parse --abbrev-ref HEAD`). Paste the verifier output in the commit
   body. NEVER push to origin unless the user explicitly asks.

5. **UPDATE** — Edit RESEARCH_NOTE.md (move admitted nodes to [SOLID], refresh
   "Next Tactics"), overwrite `loop_notes/current_iter.md`, refresh
   `medium_term.md` on its cadence, append discovered codes to
   `results/discovery_timeline.md`, sync `agentic_lean_state.md`.

6. **ESCALATE** — If a node has not advanced for 3 iters OR 30 min, OR an
   ingredient is missing: fire `pipelines/6-escalation` (download paper/code ->
   ref-paper/ or ref-code/, decompose) per escalation_policy, OR spawn an Agent
   (general-purpose) with `alignment.md` + `agentic_lean_contract.md` +
   `code_quality_policy.md` injected for a 30-min deep-research report on the
   obstacle; implement its recommendation next iter.

7. **DO NOT STOP.** Output the completion promise ONLY when ALL hold:
   - `src/qcode_discovery/` reproduces the pipeline end-to-end: BB+PBB
     construction, k via GF(2) rank, CSS MILP distance + symplectic non-CSS
     MILP + exhaustive enumeration, FOM, the staged evaluation cascade, a
     working MAP-Elites/program-evolution search loop, BLISS Tanner-graph
     deduplication, decomposability detection, and the LC-CSS equivalence check.
   - `python -m pytest -q` is green and reproduces verified landmarks: gross
     code [[144,12,12]] k=12; [[72,12,6]] k=12; A=B => d=2 (Thm `thm:ab_d2`);
     univariate k=8l/3 (Thm `lem:crt_k`); >=1 MILP-exact distance match.
   - `results/discovery_timeline.md` records the discovery campaigns with
     verified [[n,k,d]] parameters and modality/status per code.
   - `theorem_dependency_plan.md` and `file_dependency_plan.md` are [SOLID].
   - No certified-claim `[HOLE]` or `[BLOCKING]` remains in RESEARCH_NOTE.md.

Completion promise (output ONLY when unequivocally TRUE):
<promise>QLDPC_BBC_DISCOVERY_PIPELINE_COMPLETE</promise>
