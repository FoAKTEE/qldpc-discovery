#!/usr/bin/env julia
# Catalog-BLIND search for bivariate-bicycle (BB) quantum LDPC codes, CPU-only, massively parallel,
# with CONTINUOUS checkpointing (frontier.md is rewritten every CHECKPOINT seconds during the run).
#
# Run (from the repo root, 200 cores):
#   JULIA_PROJECT=julia julia --project=julia -t 200,2 scripts/search/blind_search.jl
#   (the ",2" gives interactive threads so the checkpoint monitor isn't starved by the workers)
#   env: NMAX (max n=2lm, default 1000)  WALL (s, default 600)  TRIALS (BP-OSD, 32)  MAXITER (BP cap, 30)
#        CHECKPOINT (frontier write interval s, 20)  OUT (frontier path)
#
# BLIND DISCIPLINE: naive random weight-3 seeds; NO paper data / hardcoded codes / catalog. d is a
# BP-OSD stochastic UPPER bound (d/sqrt(n) trust filter drops the worst overestimates); headline
# high-d codes need post-hoc exact certification (min_distance_bz) — NOT certified here.
#
# Per-worker pipeline: random (l,m), 2lm<=NMAX -> random weight-3 (A,B) -> Stage-1 k via GF(2) rank
# (reject k=0 / k>KMAX) -> Stage-2 BP-OSD distance -> FOM=kd^2/n. Improvements update ONE shared
# MAP-Elites archive (keyed by (n,k)) under a lock; a monitor task snapshots + writes frontier.md
# every CHECKPOINT seconds so intermediate results stream out continuously.

using QCodeDiscovery, Random, Printf

const NMAX       = parse(Int, get(ENV, "NMAX", "1000"))
const WALL       = parse(Float64, get(ENV, "WALL", "600"))
const TRIALS     = parse(Int, get(ENV, "TRIALS", "32"))
const MAXITER    = parse(Int, get(ENV, "MAXITER", "30"))
const CHECKPOINT = parse(Float64, get(ENV, "CHECKPOINT", "20"))
const WEIGHT     = 3
const KMAX       = 300
const OUT        = get(ENV, "OUT", joinpath(@__DIR__, "frontier.md"))
const LATS       = [(l, m) for l in 2:60 for m in 2:60 if 2 * l * m <= NMAX]

# ---- shared MAP-Elites archive (best FOM per (n,k)) + progress counters -------------------------
const GARCH     = Dict{Tuple{Int,Int},NamedTuple}()
const GLOCK     = ReentrantLock()
const SCREENED  = Threads.Atomic{Int}(0)
const DISTEVALS = Threads.Atomic{Int}(0)

function write_frontier(elapsed::Float64)
    lock(GLOCK); snap = collect(values(GARCH)); unlock(GLOCK)     # snapshot under lock
    elites = sort(snap, by=x -> -x.fom)
    open(OUT, "w") do io
        println(io, "# Discovered frontier — BLIND CPU search (blind-zero), n<=$NMAX  [LIVE: rewritten every $(CHECKPOINT)s]")
        println(io, "")
        println(io, "Catalog-blind; d = BP-OSD UPPER bound (NOT certified — high-d entries need MILP/BZ).")
        @printf(io, "screened=%d  dist_evals=%d  cells=%d  elapsed=%.0fs  (run wall budget=%.0fs)\n\n",
                SCREENED[], DISTEVALS[], length(elites), elapsed, WALL)
        println(io, "| [[n,k,d]] | FOM | k/n | d/sqrt(n) | (l,m) | A | B |")
        println(io, "|---|---|---|---|---|---|---|")
        for e in elites[1:min(40, length(elites))]
            @printf(io, "| [[%d,%d,%d]] | %.2f | %.3f | %.2f | (%d,%d) | %s | %s |\n",
                    e.n, e.k, e.d, e.fom, e.k / e.n, e.dsn, e.l, e.m, e.A, e.B)
        end
    end
    # machine-readable sidecar (ALL cells) for the certifier
    open(OUT * ".tsv", "w") do io
        println(io, "n\tk\td_bposd\tfom\tl\tm\tA\tB")
        for e in elites
            @printf(io, "%d\t%d\t%d\t%.4f\t%d\t%d\t%s\t%s\n", e.n, e.k, e.d, e.fom, e.l, e.m, e.A, e.B)
        end
    end
    return elites
end

function worker(wid::Int, t0::Float64)
    rng = MersenneTwister(UInt32(2654435761) ⊻ UInt32(wid))
    nlat = length(LATS)
    while time() - t0 < WALL
        l, m = LATS[rand(rng, 1:nlat)]
        Threads.atomic_add!(SCREENED, 1)
        try
            A = random_polynomial(l, m, WEIGHT, rng)
            B = random_polynomial(l, m, WEIGHT, rng)
            c = bbcode_from_terms(l, m, A, B)
            k = css_k(c)
            (k <= 0 || k > KMAX) && continue
            r = bposd_distance(c; trials=TRIALS, seed=(SCREENED[] * 131 + wid), max_iter=MAXITER)
            d = r.d_bound === nothing ? 0 : r.d_bound
            Threads.atomic_add!(DISTEVALS, 1)
            d <= 0 && continue
            dsn = d / sqrt(c.n)
            # RATE-AWARE trust filter: BP-OSD OVERESTIMATES d more at high rate (paper's signature
            # finding, up to ~12x for k/n>0.1). Real high-rate codes obey the rate-distance tradeoff
            # (low d/sqrt(n)); a high d/sqrt(n) at high rate is almost surely an overestimate. So cap
            # d/sqrt(n) tighter as k/n rises. (Heuristic SCREEN only — the certifier is authoritative.)
            rate = k / c.n
            cap = rate <= 0.06 ? 1.8 : (rate <= 0.12 ? 1.4 : 1.1)
            dsn >= cap && continue
            f = fom(c.n, k, d)
            key = (c.n, k)
            lock(GLOCK)
            try
                cur = get(GARCH, key, nothing)
                if cur === nothing || f > cur.fom
                    GARCH[key] = (n=c.n, k=k, d=d, fom=f, l=l, m=m, dsn=dsn,
                                  A=join(["x^$a*y^$b" for (a, b) in A], "+"),
                                  B=join(["x^$a*y^$b" for (a, b) in B], "+"))
                end
            finally
                unlock(GLOCK)
            end
        catch
            continue                                    # defense-in-depth (root cause already fixed)
        end
    end
end

function monitor(t0::Float64, done::Threads.Atomic{Bool})
    while !done[]
        for _ in 1:Int(ceil(CHECKPOINT))                # poll `done` ~every 1s, write every CHECKPOINT
            sleep(1.0); done[] && break
        end
        el = time() - t0
        elites = write_frontier(el)
        @printf("[t=%4.0fs] screened=%d dist_evals=%d cells=%d  topFOM=%.1f  top=%s\n",
                el, SCREENED[], DISTEVALS[], length(elites),
                isempty(elites) ? 0.0 : elites[1].fom,
                isempty(elites) ? "-" : "[[$(elites[1].n),$(elites[1].k),$(elites[1].d)]]")
        flush(stdout)
    end
end

function main()
    nthreads = Threads.nthreads()
    @printf("BLIND CPU search: threads=%d  NMAX=%d  |lattices|=%d  WALL=%.0fs  TRIALS=%d  MAXITER=%d  CHECKPOINT=%.0fs\n",
            nthreads, NMAX, length(LATS), WALL, TRIALS, MAXITER, CHECKPOINT)
    println("LIVE frontier -> ", OUT)
    flush(stdout)
    t0 = time()
    done = Threads.Atomic{Bool}(false)
    # Monitor runs on the :interactive threadpool so it is NOT starved by the CPU-bound workers that
    # saturate the default pool — this is what makes the checkpoints fire DURING the run (run julia
    # with `-t <workers>,2` so an interactive thread exists; falls back to default pool otherwise).
    mon = Threads.@spawn :interactive monitor(t0, done)
    @sync for w in 1:nthreads
        Threads.@spawn worker(w, t0)
    end
    done[] = true
    wait(mon)
    elites = write_frontier(time() - t0)               # authoritative final write
    @printf("DONE: screened=%d  dist_evals=%d  cells=%d  elapsed=%.0fs  throughput=%.0f cand/s\n",
            SCREENED[], DISTEVALS[], length(elites), time() - t0, SCREENED[] / (time() - t0))
    println("top frontier (BP-OSD upper bounds — uncertified):")
    for e in elites[1:min(15, length(elites))]
        @printf("  [[%d,%d,%d]] FOM=%.2f (l=%d,m=%d) d/sqrt(n)=%.2f\n", e.n, e.k, e.d, e.fom, e.l, e.m, e.dsn)
    end
    println("wrote ", OUT)
end

try
    main()
catch e
    println(stderr, "TOP-LEVEL ERROR: ", sprint(showerror, e))
    Base.show_backtrace(stderr, catch_backtrace())
    flush(stderr); flush(stdout)
    rethrow()
end
