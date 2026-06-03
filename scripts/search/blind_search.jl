#!/usr/bin/env julia
# Catalog-BLIND search for bivariate-bicycle (BB) + perturbed-BB (PBB) quantum LDPC codes, CPU-only,
# massively parallel, with CONTINUOUS checkpointing (frontier.md rewritten every CHECKPOINT seconds).
#
# Run (from the repo root, 200 cores):
#   JULIA_PROJECT=julia julia --project=julia -t 200,2 scripts/search/blind_search.jl
#   (the ",2" gives interactive threads so the checkpoint monitor isn't starved by the workers)
#
# Env (ALL default to the original fixed weight-3 CSS-only random scan, so the prior run reproduces):
#   NMAX (max n=2lm, 1000)  WALL (s, 600)  TRIALS (BP-OSD, 32)  MAXITER (BP cap, 30)
#   CHECKPOINT (frontier write interval s, 20)  OUT (frontier path)  KMAX (300)
#   --- audit-driven reach/strength flags (gap labels per progress/audit-vs-paper/AUDIT.md) ---
#   WMIN,WMAX  (check-weight range per trial; default 3,3 == fixed weight-3)              [gap a]
#   ANSATZ     (fraction [0,1] of CSS trials seeded from a generic structured ansatz, 0) [gap b]
#   GENS       (GA local-search refinement rounds over elites AFTER the scan, 0=off)      [gap c]
#   MODE       (css | pbb | both; default css — pbb adds non-CSS 4-tuple (A,B,C,D))       [gap d]
#   DEDUP      (1 => track canonical-hash distinct count; default 0)                      [gap e]
#   FIXLM      ("l,m" => concentrate all workers on ONE lattice, deep mode; default off)  [gap g]
#   PBB_EXACT_NMAX (144), PBB_CAP (2_000_000): exact symplectic distance gate for PBB.
#
# BLIND DISCIPLINE (BINDING): seeds are NAIVE — uniform-random monomials, or structured ANSATZ with
# RANDOM parameters (x/y-swap / univariate / custom forms, NOT the paper's polynomials), or PBB with
# RANDOM perturbations C,D. NO paper data / hardcoded codes / catalog is ever read. d is a BP-OSD
# stochastic UPPER bound (rate-aware d/sqrt(n) trust filter drops the worst overestimates); headline
# high-d codes need post-hoc exact certification (certify.jl) — NOT certified here.

using QCodeDiscovery, Random, Printf

const NMAX       = parse(Int, get(ENV, "NMAX", "1000"))
const WALL       = parse(Float64, get(ENV, "WALL", "600"))
const TRIALS     = parse(Int, get(ENV, "TRIALS", "32"))
const MAXITER    = parse(Int, get(ENV, "MAXITER", "30"))
const CHECKPOINT = parse(Float64, get(ENV, "CHECKPOINT", "20"))
const WMIN       = parse(Int, get(ENV, "WMIN", get(ENV, "WEIGHT", "3")))
const WMAX       = parse(Int, get(ENV, "WMAX", get(ENV, "WEIGHT", "3")))
const KMAX       = parse(Int, get(ENV, "KMAX", "300"))
const MODE       = Symbol(get(ENV, "MODE", "css"))            # :css | :pbb | :both
const OBJECTIVE  = Symbol(get(ENV, "OBJECTIVE", "fom"))       # :fom (FOM frontier) | :k (high-k campaign)
const ANSATZ     = parse(Float64, get(ENV, "ANSATZ", "0.0"))  # fraction of CSS trials from structured ansatz
const UNIVAR     = parse(Float64, get(ENV, "UNIVAR", OBJECTIVE === :k ? "0.8" : "0.0"))  # fraction of univariate (high-k) seeds
const DEDUP      = get(ENV, "DEDUP", "0") == "1"
const GENS       = parse(Int, get(ENV, "GENS", "0"))
const FIXLM      = get(ENV, "FIXLM", "")
const PBB_PERT_W = parse(Int, get(ENV, "PBB_PERT_W", "2"))    # max #terms in a PBB perturbation C/D
const PBB_EXACT_NMAX = parse(Int, get(ENV, "PBB_EXACT_NMAX", "144"))
const PBB_CAP    = parse(Int, get(ENV, "PBB_CAP", "2000000"))
const OUT        = get(ENV, "OUT", joinpath(@__DIR__, "frontier.md"))

function _lattices()
    if !isempty(FIXLM)
        p = split(FIXLM, ','); return [(parse(Int, p[1]), parse(Int, p[2]))]
    end
    return [(l, m) for l in 2:60 for m in 2:60 if 2 * l * m <= NMAX]
end
const LATS = _lattices()

# ---- shared MAP-Elites archive (best FOM per (n,k)) + progress counters -------------------------
const GARCH     = Dict{Tuple{Int,Int},NamedTuple}()
const GLOCK     = ReentrantLock()
const SCREENED  = Threads.Atomic{Int}(0)
const DISTEVALS = Threads.Atomic{Int}(0)

polystr(terms) = isempty(terms) ? "" : join(["x^$a*y^$b" for (a, b) in terms], "+")

# High-k structural seed families (RANDOM params; general algebraic priors, NOT the paper's catalog).
# univariate (UV) gives high k but d=2; factored / mixed lift the high-k distance to d~4-5 (verified).
function univariate_seed(l::Int, m::Int, rng)          # A=1+y^a+y^2a, B=1+x^j+x^2j (lem:crt_k; d=2)
    a = rand(rng, 1:max(1, m - 1)); j = rand(rng, 1:max(1, l - 1))
    return [(0, 0), (0, mod(a, m)), (0, mod(2a, m))], [(0, 0), (mod(j, l), 0), (mod(2j, l), 0)]
end
function factored_seed(l::Int, m::Int, rng)            # A=(1+y^a)(1+x^j), B=(1+y^2a)(1+x^2j) (high k, d~5)
    a = rand(rng, 1:max(1, m - 1)); j = rand(rng, 1:max(1, l - 1))
    A = [(0, 0), (mod(j, l), 0), (0, mod(a, m)), (mod(j, l), mod(a, m))]
    B = [(0, 0), (mod(2j, l), 0), (0, mod(2a, m)), (mod(2j, l), mod(2a, m))]
    return A, B
end
function mixed_seed(l::Int, m::Int, rng)               # univariate + a diagonal cross term (high k, d~4)
    a = rand(rng, 1:max(1, m - 1)); j = rand(rng, 1:max(1, l - 1))
    A = [(0, 0), (0, mod(a, m)), (mod(j, l), mod(a, m))]
    B = [(0, 0), (mod(j, l), 0), (mod(j, l), mod(a, m))]
    return A, B
end
# Pick a high-k family at random (univariate for raw k, factored/mixed for k with d>=4).
function highk_seed(l::Int, m::Int, rng)
    r = rand(rng)
    return r < 0.34 ? univariate_seed(l, m, rng) : (r < 0.67 ? factored_seed(l, m, rng) : mixed_seed(l, m, rng))
end

# rate-aware d/sqrt(n) trust cap: BP-OSD overestimates d MORE at high rate (paper's signature
# finding); a high d/sqrt(n) at high rate is almost surely an overestimate.
trust_cap(rate) = rate <= 0.06 ? 1.8 : (rate <= 0.12 ? 1.4 : 1.1)

# consider a candidate cell against the (n,k)-keyed archive (keep best FOM); returns true if stored.
function consider!(cell)
    key = (cell.n, cell.k)
    lock(GLOCK)
    try
        cur = get(GARCH, key, nothing)
        if cur === nothing || cell.fom > cur.fom
            GARCH[key] = cell
            return true
        end
    finally
        unlock(GLOCK)
    end
    return false
end

# Evaluate a CSS BB candidate from term lists -> cell NamedTuple, or nothing if rejected.
function eval_css(l, m, At, Bt, distseed)
    c = bbcode_from_terms(l, m, At, Bt)
    k = css_k(c)
    (k <= 0 || k > KMAX) && return nothing
    r = bposd_distance(c; trials=TRIALS, seed=distseed, max_iter=MAXITER)
    Threads.atomic_add!(DISTEVALS, 1)
    d = r.d_bound === nothing ? 0 : r.d_bound
    d <= 0 && return nothing
    dsn = d / sqrt(c.n)
    # FOM mode: drop high-rate BP-OSD overestimates. k mode (high-k campaign): keep all valid-k cells
    # (high-k codes are low d/sqrt(n) anyway; the rate filter must not hide the k-axis).
    OBJECTIVE !== :k && dsn >= trust_cap(k / c.n) && return nothing
    return (n=c.n, k=k, d=d, fom=fom(c.n, k, d), l=l, m=m, dsn=dsn,
            wt=stabilizer_weight(c), fam=:css,
            A=polystr(c.A), B=polystr(c.B), C="", D="",
            At=collect(c.A), Bt=collect(c.B), Ct=Tuple{Int,Int}[], Dt=Tuple{Int,Int}[])
end

# Evaluate a non-CSS PBB candidate (A,B,C,D term lists). Non-commuting tuples throw -> caught upstream.
# Distance is EXACT (symplectic Brouwer–Zimmermann) and only attempted for small n; else rejected.
function eval_pbb(l, m, At, Bt, Ct, Dt)
    (isempty(Ct) && isempty(Dt)) && return nothing        # C=D=0 is just CSS — handled by eval_css
    code = PBBCode(l, m, polystr(At), polystr(Bt), polystr(Ct), polystr(Dt))  # throws if non-commuting
    code.n > PBB_EXACT_NMAX && return nothing
    k = pbb_k(code)
    (k <= 0 || k > KMAX) && return nothing
    r = symplectic_distance(code; cap=PBB_CAP)
    Threads.atomic_add!(DISTEVALS, 1)
    (!r.certified || r.d <= 0) && return nothing          # only keep EXACT-certified PBB cells
    swt = Int(sum(Int.(code.SX[1, :])) + sum(Int.(code.SZ[1, :])))
    return (n=code.n, k=k, d=r.d, fom=fom(code.n, k, r.d), l=l, m=m, dsn=r.d / sqrt(code.n),
            wt=swt, fam=:pbb,
            A=polystr(code.A), B=polystr(code.B), C=polystr(code.C), D=polystr(code.D),
            At=collect(code.A), Bt=collect(code.B), Ct=collect(code.C), Dt=collect(code.D))
end

function worker(wid::Int, t0::Float64)
    rng = MersenneTwister(UInt32(2654435761) ⊻ UInt32(wid))
    nlat = length(LATS)
    while time() - t0 < WALL
        l, m = LATS[rand(rng, 1:nlat)]
        Threads.atomic_add!(SCREENED, 1)
        want_pbb = MODE === :pbb || (MODE === :both && rand(rng) < 0.5)
        try
            wA = rand(rng, WMIN:WMAX); wB = rand(rng, WMIN:WMAX)
            if want_pbb
                At = random_polynomial(l, m, wA, rng); Bt = random_polynomial(l, m, wB, rng)
                Ct = random_polynomial(l, m, rand(rng, 0:PBB_PERT_W), rng)
                Dt = random_polynomial(l, m, rand(rng, 0:PBB_PERT_W), rng)
                cell = eval_pbb(l, m, At, Bt, Ct, Dt)
            elseif UNIVAR > 0 && rand(rng) < UNIVAR
                # high-k structural seed (univariate | factored | mixed; random params) — the campaign's producer
                At, Bt = highk_seed(l, m, rng)
                cell = eval_css(l, m, At, Bt, SCREENED[] * 131 + wid)
            elseif ANSATZ > 0 && rand(rng) < ANSATZ
                # structured (generic-parameter) ansatz seed — encodes a STRUCTURAL prior, not catalog polys
                pairs = generate(random_ansatz(rng), l, m)
                isempty(pairs) && continue
                At, Bt = pairs[rand(rng, 1:length(pairs))]
                cell = eval_css(l, m, At, Bt, SCREENED[] * 131 + wid)
            else
                At = random_polynomial(l, m, wA, rng); Bt = random_polynomial(l, m, wB, rng)
                cell = eval_css(l, m, At, Bt, SCREENED[] * 131 + wid)
            end
            cell === nothing || consider!(cell)
        catch
            continue                                    # defense-in-depth (root cause already fixed)
        end
    end
end

# GA local-search refinement: mutate the (A,B) of each CSS elite, re-evaluate, consider. Blind:
# mutate_polynomial perturbs exponents only (weight-preserving), injecting no catalog knowledge.
function ga_refine!(gens::Int)
    gens <= 0 && return
    for g in 1:gens
        lock(GLOCK); seeds = collect(values(GARCH)); unlock(GLOCK)
        css = [e for e in seeds if e.fam === :css]
        isempty(css) && return
        Threads.@threads for idx in eachindex(css)
            e = css[idx]
            rng = MersenneTwister(UInt32(0x9E3779B1) ⊻ UInt32(g * 100003 + idx))
            try
                At = mutate_polynomial(e.At, e.l, e.m, rng)
                Bt = mutate_polynomial(e.Bt, e.l, e.m, rng)
                cell = eval_css(e.l, e.m, At, Bt, g * 1000 + idx)
                cell === nothing || consider!(cell)
            catch
                continue
            end
        end
        @printf("[GA gen %d/%d] cells=%d\n", g, gens, length(GARCH)); flush(stdout)
    end
end

# distinct-code count: CHEAP representation-level signature (l,m + normalized A,B,C,D term strings),
# microseconds per cell. The archive already keys by (n,k); this collapses identical representations.
# NOTE: rigorous symmetry/BLISS dedup (canonical_hash) is a POST-HOC certifier step, NOT run here —
# canonical_hash is 0.1-1.3s per code, far too slow to run over all cells on every checkpoint (doing so
# stalled the monitor so no frontier was ever written). This count is a fast lower bound on distinctness.
function distinct_count(snap)
    hs = Set{String}()
    for e in snap
        push!(hs, "$(e.l),$(e.m)|$(e.fam)|$(e.A)|$(e.B)|$(e.C)|$(e.D)")
    end
    return length(hs)
end

function write_frontier(elapsed::Float64)
    lock(GLOCK); snap = collect(values(GARCH)); unlock(GLOCK)     # snapshot under lock
    # FOM mode sorts by FOM; high-k campaign sorts by k (then FOM) so the high-rate codes surface.
    elites = OBJECTIVE === :k ? sort(snap, by=x -> (-x.k, -x.fom)) : sort(snap, by=x -> -x.fom)
    ndist = DEDUP ? distinct_count(snap) : length(elites)
    open(OUT, "w") do io
        println(io, "# Discovered frontier — BLIND CPU search (blind-zero), n<=$NMAX  [LIVE: rewritten every $(CHECKPOINT)s]")
        println(io, "")
        println(io, "Catalog-blind; d = BP-OSD UPPER bound for CSS / EXACT symplectic for PBB. CSS high-d entries need MILP/BZ.")
        @printf(io, "mode=%s  wt=%d..%d  ansatz=%.2f  gens=%d  dedup=%s  screened=%d  dist_evals=%d  cells=%d  distinct=%s  elapsed=%.0fs  (budget=%.0fs)\n\n",
                MODE, WMIN, WMAX, ANSATZ, GENS, DEDUP, SCREENED[], DISTEVALS[], length(elites),
                DEDUP ? string(ndist) : "n/a", elapsed, WALL)
        println(io, "| [[n,k,d]] | FOM | k/n | d/sqrt(n) | wt | fam | (l,m) | A | B |")
        println(io, "|---|---|---|---|---|---|---|---|---|")
        for e in elites[1:min(40, length(elites))]
            @printf(io, "| [[%d,%d,%d]] | %.2f | %.3f | %.2f | %d | %s | (%d,%d) | %s | %s |\n",
                    e.n, e.k, e.d, e.fom, e.k / e.n, e.dsn, e.wt, e.fam, e.l, e.m, e.A, e.B)
        end
    end
    # machine-readable sidecar (ALL cells) for the certifier.
    # COLUMNS (stable): n k d fom l m A B  | wt fam C D   (certify.jl reads 1..8 + fam/C/D)
    open(OUT * ".tsv", "w") do io
        println(io, "n\tk\td\tfom\tl\tm\tA\tB\twt\tfam\tC\tD")
        for e in elites
            @printf(io, "%d\t%d\t%d\t%.4f\t%d\t%d\t%s\t%s\t%d\t%s\t%s\t%s\n",
                    e.n, e.k, e.d, e.fom, e.l, e.m, e.A, e.B, e.wt, e.fam, e.C, e.D)
        end
    end
    return elites
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
    @printf("BLIND search: threads=%d  MODE=%s  NMAX=%d  |lattices|=%d  WALL=%.0fs  wt=%d..%d  ansatz=%.2f  gens=%d  dedup=%s  fixlm=%s\n",
            nthreads, MODE, NMAX, length(LATS), WALL, WMIN, WMAX, ANSATZ, GENS, DEDUP, isempty(FIXLM) ? "-" : FIXLM)
    println("LIVE frontier -> ", OUT)
    flush(stdout)
    t0 = time()
    done = Threads.Atomic{Bool}(false)
    # Monitor on the :interactive threadpool so the CPU-bound workers (default pool) don't starve it.
    mon = Threads.@spawn :interactive monitor(t0, done)
    @sync for w in 1:nthreads
        Threads.@spawn worker(w, t0)
    end
    ga_refine!(GENS)                                    # post-scan GA local search (no-op if GENS=0)
    done[] = true
    wait(mon)
    elites = write_frontier(time() - t0)               # authoritative final write
    @printf("DONE: screened=%d  dist_evals=%d  cells=%d  elapsed=%.0fs  throughput=%.0f cand/s\n",
            SCREENED[], DISTEVALS[], length(elites), time() - t0, SCREENED[] / max(1e-9, time() - t0))
    println("top frontier (CSS = BP-OSD upper bounds uncertified; PBB = exact symplectic):")
    for e in elites[1:min(15, length(elites))]
        @printf("  [[%d,%d,%d]] %s wt=%d FOM=%.2f (l=%d,m=%d) d/sqrt(n)=%.2f\n",
                e.n, e.k, e.d, e.fam, e.wt, e.fom, e.l, e.m, e.dsn)
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
