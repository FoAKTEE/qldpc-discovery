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
