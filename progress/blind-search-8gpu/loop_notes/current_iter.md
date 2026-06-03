# current_iter — iter 10: broadened-search validation (DONE) + a 2nd package-discipline fix

## Anchor
Validate iter9's pipeline broadening: run the broadened search in the paper's regime (n<=360) and test
post-hoc whether varying weight + ansatz + GA recovers paper catalog codes the fixed-weight-3 run missed.

## EDIT/FIX (package_debug_policy, 2nd this session)
The broadened run surfaced a 2nd bug: with DEDUP=1, write_frontier ran canonical_hash (BLISS, measured
0.1-1.3s/code) over ALL cells EVERY checkpoint -> monitor stalled -> NO frontier ever written (looked
hung). Root-caused (timed canonical_hash) + fixed: distinct_count now uses a cheap representation-level
signature (microseconds); rigorous BLISS dedup deferred to a post-hoc step. Committed 54d7dca, ported
to main a2b9f3e.

## VERIFY (broadened run + certification)
Run: CSS n<=360, WMIN3 WMAX5, ANSATZ0.3, GENS2, DEDUP1, -t128,2, WALL240 -> 177085 screened, 530 cells,
distinct=530, weight diversity 6/7/8/9/10 (was uniformly 6). Certifier (light: SEEDS1 HITRIALS100 BZ_NMAX160)
-> 530 certified, 99 EXACT, ZERO crashes (at-scale proof of the BZ allocation-free fix — 530 high-weight
n<=360 codes, exactly the class that OOM-crashed before iter9).

## RESULT (progress/audit-vs-paper/BROADENED_VS_PAPER.md)
Paper CSS catalog coverage: 10/28 (n,k) points present; reached paper d (UB) at 6. KEY WINS the weight-3
run could NOT reach: [[360,8,30]] d=32 UB (paper FOM-20 weight-7 code), [[144,8,12]] d=12 (weight-6 MX),
[[288,8,20]], [[288,16,12]], [[288,14,12]]. GAPS: (a) all 18 missing are HIGH-k (k=24-54) codes — our
rate filter + FOM bias suppresses them -> needs a separate high-k campaign; (b) large-n d are uncertified
BP-OSD UBs (e.g. [[288,12,16]] ours d=30 vs paper-exact 16 = overestimate; needs MILP we lack). No
certified beat on the paper's own n.

## STATUS
iter10 COMPLETE: broadening validated (weight axis closes the high-d gap; high-k axis + large-n exact
certification remain open + documented). Committing artifacts. Honest: this is a validation, not new
SOTA. The user's explicit request (audit + pipeline changes) was delivered in iter9.
