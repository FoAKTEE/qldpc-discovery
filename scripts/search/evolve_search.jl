#!/usr/bin/env julia
# Evolutionary generator-ansatz search — the paper's core method (GA-G program evolution, arXiv:2606.02418
# sec IV.A), done blind + pure-Julia. Evolves a population of GeneratorAnsatz programs toward total
# cross-lattice FOM, using a TRUSTWORTHY ISD distance fitness (refutes the BP-OSD overestimates that
# would otherwise make the search chase artifacts — the lesson behind the paper's MILP-in-loop).
#
# Run:  JULIA_PROJECT=julia julia --project=julia -t <N> scripts/search/evolve_search.jl
#   env: GENERATIONS (12)  POP (16)  TIME_LIMIT (0.5, per-code BP-OSD budget if method=:bposd)
#        SEED (7)  METHOD (isd | bposd)  ISD_ITERS (300)  OUT (evolved_frontier.tsv)
#        LATS ("l,m;l,m;..."; default = the paper's Stage-2 CSS lattices)
#
# BLIND: ansatze are random/parametric structural programs (xyswap / univariate / factored), NOT the
# paper's catalog polynomials. Distances are honest (ISD = tight UPPER bound). Parallel: fitness evals
# are threaded inside evolve_ansaetze.

using QCodeDiscovery, Printf

const GENERATIONS = parse(Int, get(ENV, "GENERATIONS", "12"))
const POP         = parse(Int, get(ENV, "POP", "16"))
const TIME_LIMIT  = parse(Float64, get(ENV, "TIME_LIMIT", "0.5"))
const SEED        = parse(Int, get(ENV, "SEED", "7"))
const METHOD      = Symbol(get(ENV, "METHOD", "isd"))
const ISD_ITERS   = parse(Int, get(ENV, "ISD_ITERS", "300"))
const OUT         = get(ENV, "OUT", joinpath(@__DIR__, "evolved_frontier.tsv"))

function _lats()
    s = get(ENV, "LATS", "")
    isempty(s) && return [(12, 6), (6, 12), (12, 12), (24, 6), (15, 12), (30, 6), (16, 9), (18, 8)]
    return [(parse(Int, p[1]), parse(Int, p[2])) for p in (split(x, ',') for x in split(s, ';'))]
end

function main()
    lats = _lats()
    @printf("EVOLUTIONARY ansatz search: threads=%d  gens=%d  pop=%d  method=%s  isd_iters=%d  |lattices|=%d\n",
            Threads.nthreads(), GENERATIONS, POP, METHOD, ISD_ITERS, length(lats)); flush(stdout)
    r = evolve_ansaetze(lats; generations=GENERATIONS, pop=POP, time_limit=TIME_LIMIT,
                        seed=SEED, distance_method=METHOD, isd_iters=ISD_ITERS, log=println)
    codes = sort(r.best.codes, by=c -> -c.fom)
    polystr(t) = isempty(t) ? "" : join(["x^$a*y^$b" for (a, b) in t], "+")
    open(OUT, "w") do io
        # record A,B polynomials so headline codes are INDEPENDENTLY VERIFIABLE (high-iter ISD / exact BZ);
        # the in-loop d is an ISD upper bound at ISD_ITERS — re-certify before treating as a discovery.
        println(io, "n\tk\td\tfom\twt\tl\tm\tA\tB")
        for c in codes
            @printf(io, "%d\t%d\t%d\t%.4f\t%d\t%d\t%d\t%s\t%s\n",
                    c.n, c.k, c.d, c.fom, c.stab_weight, c.l, c.m, polystr(c.A), polystr(c.B))
        end
    end
    @printf("DONE: best score=%.1f over %d lattices; %d codes (ISD-trustworthy) -> %s\n",
            r.best.score, r.best.n_lattices_with_code, length(codes), OUT)
    println("top evolved codes:")
    for c in codes[1:min(15, length(codes))]
        @printf("  [[%d,%d,%d]] FOM=%.1f wt=%d\n", c.n, c.k, c.d, c.fom, c.stab_weight)
    end
end

try
    main()
catch e
    println(stderr, "TOP-LEVEL ERROR: ", sprint(showerror, e)); Base.show_backtrace(stderr, catch_backtrace())
    flush(stderr); rethrow()
end
