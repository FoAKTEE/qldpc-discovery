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
