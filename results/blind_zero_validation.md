# Blind-zero validation — clean-room findings vs the held-out paper (post-hoc)

The `blind-zero` branch was stripped to a clean room and a **paper-naive agent** discovered BB codes
from scratch (its kernel + search, no catalog/known-codes). This file compares its findings to
arXiv:2606.02418 (the held-out test set) — written by the orchestrator, who *has* read the paper;
the validation is post-hoc, the discovery was blind.

## What the blind agent found (cold, MILP/enum-certified)

| code | FOM | distance status |
|---|---|---|
| `[[72,8,6]]` | 4.00 | MILP gap=0 (exact) — its best |
| `[[72,4,8]]` | 3.56 | exact |
| `[[144,8,6]]` | 2.00 | exact (both X/Z) |
| `[[72,8,4]]`, `[[72,4,4]]` | 1.78 / 0.89 | exact (enumeration) |

It also produced loose n=144 incumbents (e.g. `[[144,4,18]]`) and **correctly refused to claim them**
— independently rediscovering the distance-overestimation caution (the same lesson the paper makes
about BP-OSD), with no paper input.

## Validation verdict vs the paper's headline codes

| paper code | role | blind agent find it? |
|---|---|---|
| `[[144,12,12]]` (gross) | flagship | **NO** |
| `[[288,16,12]]` | "most practically relevant" | **NO** |
| `[[72,12,6]]` (k=12) | Bravyi MILP-validation code | **NO** (found k=8 / k=4 at n=72, not k=12,d=6) |
| `[[144,8,12]]` (mixed-monomial) | Campaign-4 | NO (found `[[144,8,6]]`, d=6 ≠ 12) |

**None of the paper's headline codes were rediscovered by the genuinely-blind agent.** It found
*valid, certified, but modest* BB codes (FOM ≤ 4, d ≤ 8 at small n).

## The honest scientific conclusion

This clean-room result is the most important finding of the whole project, and it **vindicates the
user's instinct to test from zero**:

1. **Blind random + hill-climb finds real but modest codes** — it never reached the flagship
   `[[144,12,12]]`/`[[288,16,12]]` (d=12 at n=144/288). Those live in a thin, structured region
   (the "x/y-swap" trinomials) that uniform/local search hits with vanishing probability.
2. **The earlier `bbc` "Claude-guided" run reached the flagships only because the orchestrator had
   read the paper** and steered toward the x/y-swap pattern + exponent scans. That was *best-effort
   blind*, not airtight — exactly the contamination this experiment isolates.
3. Therefore the paper's genuine contribution is real: **the LLM's structural pattern-proposals
   (or equivalent prior knowledge) are what make the flagship codes discoverable** — not brute search.
   A truly paper-naive searcher does not stumble onto them at this compute budget.

## Caveat (disclosed, then fixed)

The clean-room was not initially airtight: the paper PDFs/tarballs were *gitignored*, so `git rm`
(which only removes tracked files) left them physically present. The blind agent stated it
**deliberately did not open them**, and its results corroborate genuine blindness (it produced no
flagship code and was appropriately skeptical of unverified high-FOM codes — a contaminated agent
would have "found" the gross code immediately). The binaries have now been removed; an airtight
re-run would delete all paper artifacts (tracked and untracked) before spawning the agent.

## Status

Blind discovery: kernel built + verified from scratch (13 tests pass); best certified `[[72,8,6]]`
FOM 4.0; **zero** held-out-catalog headline matches — an honest, instructive negative result on
brute-force blind search, and positive evidence for the value of structured (LLM-guided) search.
