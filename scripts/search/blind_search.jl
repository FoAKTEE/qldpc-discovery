#!/usr/bin/env julia
# Catalog-BLIND search for bivariate-bicycle (BB) quantum LDPC codes, CPU-only, massively parallel.
#
# Run (from the repo root, 200 cores):
#   JULIA_NUM_THREADS=200 julia --project=julia -t 200 scripts/search/blind_search.jl
#   env vars: NMAX (max n=2lm, default 1000)  WALL (seconds, default 600)  TRIALS (BP-OSD, default 120)
#
# BLIND DISCIPLINE: naive random weight-3 polynomial seeds; NO paper data, NO hardcoded codes, NO
# catalog. Each [[n,k,d]] is an HONEST result: d is a BP-OSD stochastic UPPER bound (the d/sqrt(n)
# trust filter drops the worst overestimates). Headline (high-d) codes need post-hoc exact
# certification (min_distance_bz / MILP) before being believed — they are NOT certified here.
#
# Pipeline per worker (one per thread): random (l,m) with 2lm<=NMAX -> random weight-3 (A,B) ->
# Stage-1 k via GF(2) rank (cheap; reject k=0 or k>KMAX) -> Stage-2 BP-OSD distance -> FOM=kd^2/n ->
# thread-local MAP-Elites archive keyed by (n,k). Archives merged at the end (best FOM per cell).

using QCodeDiscovery, Random, Printf

const NMAX    = parse(Int, get(ENV, "NMAX", "1000"))      # n = 2*l*m <= NMAX
const WALL    = parse(Float64, get(ENV, "WALL", "600"))   # wall-clock budget (s)
const TRIALS  = parse(Int, get(ENV, "TRIALS", "48"))      # BP-OSD trials
const MAXITER = parse(Int, get(ENV, "MAXITER", "40"))     # BP iterations cap (cost bound; OSD still bounds)
const WEIGHT = 3
const KMAX   = 300
const OUT    = get(ENV, "OUT", joinpath(@__DIR__, "frontier.md"))

const LATS = [(l, m) for l in 2:60 for m in 2:60 if 2 * l * m <= NMAX]

function worker(wid::Int, t0::Float64)
    rng = MersenneTwister(UInt32(2654435761) ⊻ UInt32(wid))
    arch = Dict{Tuple{Int,Int},NamedTuple}()
    ns = 0; nd = 0
    nlat = length(LATS)
    while time() - t0 < WALL
        l, m = LATS[rand(rng, 1:nlat)]
        ns += 1
        try
            A = random_polynomial(l, m, WEIGHT, rng)
            B = random_polynomial(l, m, WEIGHT, rng)
            c = bbcode_from_terms(l, m, A, B)
            k = css_k(c)
            (k <= 0 || k > KMAX) && continue
            r = bposd_distance(c; trials=TRIALS, seed=(ns * 131 + wid), max_iter=MAXITER)
            d = r.d_bound === nothing ? 0 : r.d_bound
            nd += 1
            d <= 0 && continue
            dsn = d / sqrt(c.n)
            dsn >= 2.0 && continue                   # trust filter: drop BP-OSD overestimates
            f = fom(c.n, k, d)
            key = (c.n, k)
            cur = get(arch, key, nothing)
            if cur === nothing || f > cur.fom
                arch[key] = (n=c.n, k=k, d=d, fom=f, l=l, m=m, dsn=dsn,
                             A=join(["x^$a*y^$b" for (a, b) in A], "+"),
                             B=join(["x^$a*y^$b" for (a, b) in B], "+"))
            end
        catch
            continue                                 # skip any degenerate candidate; never abort the run
        end
    end
    return (arch=arch, ns=ns, nd=nd)
end

function main()
    nthreads = Threads.nthreads()
    @printf("BLIND CPU search: threads=%d  NMAX=%d  |lattices|=%d  WALL=%.0fs  TRIALS=%d\n",
            nthreads, NMAX, length(LATS), WALL, TRIALS)
    flush(stdout)
    t0 = time()
    results = Vector{Any}(undef, nthreads)
    @sync for w in 1:nthreads
        Threads.@spawn results[w] = worker(w, t0)
    end
    merged = Dict{Tuple{Int,Int},NamedTuple}()
    tot_ns = 0; tot_nd = 0
    for r in results
        tot_ns += r.ns; tot_nd += r.nd
        for (key, v) in r.arch
            cur = get(merged, key, nothing)
            (cur === nothing || v.fom > cur.fom) && (merged[key] = v)
        end
    end
    el = time() - t0
    elites = sort(collect(values(merged)), by=x -> -x.fom)
    @printf("DONE: screened=%d  dist_evals=%d  cells=%d  elapsed=%.0fs  throughput=%.0f cand/s\n",
            tot_ns, tot_nd, length(merged), el, tot_ns / el)
    open(OUT, "w") do io
        println(io, "# Discovered frontier — BLIND CPU search (blind-zero), n<=$NMAX")
        println(io, "")
        println(io, "Catalog-blind; d = BP-OSD UPPER bound (NOT certified — high-d entries need MILP/BZ).")
        @printf(io, "screened=%d dist_evals=%d cells=%d elapsed=%.0fs threads=%d\n\n",
                tot_ns, tot_nd, length(merged), el, nthreads)
        println(io, "| [[n,k,d]] | FOM | (l,m) | d/sqrt(n) | A | B |")
        println(io, "|---|---|---|---|---|---|")
        for e in elites[1:min(40, length(elites))]
            @printf(io, "| [[%d,%d,%d]] | %.2f | (%d,%d) | %.2f | %s | %s |\n",
                    e.n, e.k, e.d, e.fom, e.l, e.m, e.dsn, e.A, e.B)
        end
    end
    println("top frontier (BP-OSD upper bounds — uncertified):")
    for e in elites[1:min(15, length(elites))]
        @printf("  [[%d,%d,%d]] FOM=%.2f (l=%d,m=%d) d/sqrt(n)=%.2f\n", e.n, e.k, e.d, e.fom, e.l, e.m, e.dsn)
    end
    println("wrote ", OUT)
end

main()
