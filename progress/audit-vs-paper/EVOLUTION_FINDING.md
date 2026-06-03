# Evolutionary ansatz search (paper's core method) — iter18 finding

The package implements the paper's non-LLM evolutionary baseline (`evolve_ansaetze`: evolve a population
of generator ansatze toward total FOM via mutate_ansatz). Exercised it (blind, pure-Julia).

## Finding: evolution functions, but BP-OSD fitness chases OVERESTIMATES
A minimal run (lattice (12,6), gen=3, pop=4) evolved to "score 109.6", best code [[144,32,22]] FOM=107.6.
But that is a BLATANT BP-OSD overestimate — it is the univariate k=32 code whose TRUE distance is ~2
(established in the high-k campaign). The evolution optimized the BP-OSD fitness PROXY and climbed toward
an artifact, not a real high-distance code.

## This unifies the whole audit arc
This is EXACTLY why the paper moved to MILP-EXACT distance IN THE LOOP (Campaign 4): BP-OSD overestimates
mislead the search, so the fitness must be a trustworthy distance. Our evolution reproduces the failure
mode. The concrete fix is now available: wire the iter11 ISD tool (tight upper bound that refutes
overestimates) into `evaluate_css`/`ansatz_fitness` as the fitness distance, so evolution optimizes a
trustworthy value. (Also: evolve_ansaetze is single-threaded and timed out at 4 lattices — it needs
parallelization for bounded-time runs at scale.)

## Scoped next improvement (within constraints; high value)
ISD-based fitness for the discovery cascade + evolutionary loop, + parallelize evolve_ansaetze. This is
the single change most likely to make blind evolutionary search productive (the paper's method, done
right) — deferred as a substantial, well-scoped step rather than run ad hoc at the tail of this arc.

## iter20: parallelized + validated at scale — blind ISD-evolution produces HONEST codes
Parallelized evolve_ansaetze (fitness evals threaded; RNG generation stays sequential). Ran the
ISD-fitness evolution at scale (8 paper CSS lattices, gen=8, pop=12, -t 32) in ~2.5 min. Score climbed
26 -> 40 -> 55 across generations. Top TRUSTWORTHY (ISD-tight) codes discovered blind:
[[360,4,24]] FOM=6.4, [[360,8,16]] FOM=5.7, [[288,4,20]] FOM=5.6, [[144,4,14]] FOM=5.4 — all wt=6, all
HONEST distances (no [[144,32,22]]-style artifacts). [[360,4,24]] FOM=6.4 MATCHES the paper's catalog
value exactly. The paper's evolutionary method, done right in pure Julia (trustworthy ISD fitness +
parallelized), now produces honest blind discoveries. To approach the paper's higher-FOM codes
([[360,8,30]] FOM20), feed the evolution varying-weight / factored ansatze + more generations — a scaling
run, no longer blocked by tooling or the overestimate failure mode.

## iter22: sustained evolutionary run (driver scripts/search/evolve_search.jl) — at scale
Ran the evolutionary driver (gen=14, pop=16, ISD fitness, 8 paper CSS lattices, -t 48, ~5 min, no
timeout) -> best score 95.9, 46 ISD-trustworthy codes (progress/blind-search-8gpu/evolved_frontier.tsv).
Blind evolution now explores the paper's weight-6/8 high-k regime with HONEST distances: [[288,90,4]] wt8,
[[288,50,4]] wt8, [[288,48,4]] wt8 — the EXACT (n,k,weight) of the paper's [[288,50,8]]/[[288,48,8]], but
at d=4 vs the paper's d=8. So the evolutionary method (the paper's own approach), run blind in pure Julia,
reaches the right STRUCTURE but not the specific d=8 polynomials — the cross-axis finding now demonstrated
by the method itself. Top FOM 5.0; the paper's FOM-20 needs longer evolution / the specific catalog polys.

## iter25: long evolution (gen=30, ~13min) — promising high-k codes + ISD-iters convergence check
Sustained run (gen=30, pop=20, ISD fitness, 8 paper lattices, -t 24): best score 155.4, 48 codes
(evolved_frontier_long.tsv). Headline: [[360,80,8]] FOM=14.2 wt=12, [[360,80,6]] FOM=8.0, [[288,4,22]]
FOM=6.7 — [[360,80,8]] would EXCEED the paper's high-k codes ([[288,50,8]] FOM 11.1) IF genuine.

SKEPTICAL CHECK (does ISD-fitness exploit undertraining at high k?): on a pure-univariate k=80 code at
n=360, ISD-d is STABLE at d=2 across 300/1500/6000 iters — ISD converges FAST for high-k, so it is NOT
badly undertrained at k=80. This SUPPORTS the evolved [[360,80,8]] d=8 being a genuine ISD upper bound
(the weight-12 factored structure can legitimately have higher distance than the weight-3 univariate's
d=2). HONEST CAVEAT: it is still an ISD UPPER bound, and this run did not record the specific code's
polynomials, so it is not yet INDEPENDENTLY re-certified (high-iter ISD / exact BZ). Fixed: evolve_search.jl
now records A,B so future headline codes are verifiable. Status of [[360,80,8]] FOM=14.2: PROMISING /
PRELIMINARY, pending independent re-certification — NOT a confirmed beat.
