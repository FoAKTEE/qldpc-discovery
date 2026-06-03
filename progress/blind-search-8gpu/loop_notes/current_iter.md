# current_iter — iter 10: validate the broadened search in the paper's regime (n<=360)

## Anchor
iter9 broadened the pipeline (varying check weight, structured ansatz, GA refinement) + fixed the BZ
OOM. NEXT leverage step: actually RUN the broadened search in the paper's CSS regime and test (post-hoc)
whether closing the audit gaps recovers MORE of the paper's catalog than the fixed-weight-3 run.

## PLAN
Broadened blind run, CSS, NMAX=360 (paper's CSS lattices live here): WMIN=3 WMAX=5 (gap a),
ANSATZ=0.3 (gap b), GENS=2 (gap c), DEDUP=1, WALL=300s, -t 200,2. Then certify (safe certifier) and
compare post-hoc to the paper n=144/288/360 catalog. Blind discipline upheld: all seeds random/parametric.

## STATUS
Launching the broadened run (harness-tracked). ON COMPLETION -> certify -> compare to paper catalog ->
record whether varying-weight+ansatz+GA recovers weight-6 high-d codes (e.g. [[144,8,12]]) the
weight-3 run missed. completion_promise already satisfied by the original mission; this is validation.
