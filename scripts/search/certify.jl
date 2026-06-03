#!/usr/bin/env julia
# CERTIFIER — re-evaluate the blind-scan frontier with HIGH-EFFORT distance to get true distances.
# Two passes per code, parallel across cores:
#   (1) high-effort BP-OSD (many trials, large max_iter) TIGHTENS the upper bound — the thorough pass
#       finds low-weight logicals the cheap scan missed, so BP-OSD OVERESTIMATES collapse to their
#       real (lower) value. This is what demotes "too good to be true" scan codes.
#   (2) min_distance_bz certifies EXACT (gap=0) where feasible (small n) — a true certificate.
# Output: a certified frontier showing d0 (scan upper bound) -> d (certified/tightened) so demotions
# are visible. Honest: large codes get a tightened UPPER bound (status=UB), small ones EXACT.
#
# Run (after the scan):  julia --project=julia -t 200 scripts/search/certify.jl
#   env: IN (frontier .tsv), OUT (certified .md), HITRIALS (300), HIMAXITER (120),
#        BZ_NMAX (200, only attempt exact BZ for n<=this), BZCAP (20000000)

using QCodeDiscovery, Printf

const IN        = get(ENV, "IN",  joinpath(@__DIR__, "frontier.md.tsv"))
const OUT       = get(ENV, "OUT", joinpath(@__DIR__, "certified.md"))
const HITRIALS  = parse(Int, get(ENV, "HITRIALS", "300"))
const HIMAXITER = parse(Int, get(ENV, "HIMAXITER", "120"))
const BZ_NMAX   = parse(Int, get(ENV, "BZ_NMAX", "200"))
const BZCAP     = parse(Int, get(ENV, "BZCAP", "20000000"))

struct Cand
    n::Int; k::Int; d0::Int; l::Int; m::Int; A::String; B::String
end

function load(path)
    cands = Cand[]
    for (i, ln) in enumerate(eachline(path))
        i == 1 && continue                       # header
        f = split(ln, '\t')
        length(f) < 8 && continue
        push!(cands, Cand(parse(Int, f[1]), parse(Int, f[2]), parse(Int, f[3]),
                          parse(Int, f[5]), parse(Int, f[6]), String(f[7]), String(f[8])))
    end
    return cands
end

function certify_one(c::Cand)
    code = BBCode(c.l, c.m, c.A, c.B)
    ub = bposd_distance(code; trials=HITRIALS, max_iter=min(code.n, HIMAXITER), seed=12345).d_bound
    ub = (ub === nothing) ? c.d0 : min(ub, c.d0)         # tighten: never worse than the scan bound
    if code.n <= BZ_NMAX
        bz = min_distance_bz(code; cap=BZCAP)
        if bz.certified
            return (n=c.n, k=c.k, d0=c.d0, d=bz.d, status="EXACT", l=c.l, m=c.m, A=c.A, B=c.B)
        end
    end
    return (n=c.n, k=c.k, d0=c.d0, d=ub, status="UB", l=c.l, m=c.m, A=c.A, B=c.B)
end

function main()
    cands = load(IN)
    @printf("certifying %d frontier codes (HITRIALS=%d HIMAXITER=%d BZ_NMAX=%d) on %d threads\n",
            length(cands), HITRIALS, HIMAXITER, BZ_NMAX, Threads.nthreads()); flush(stdout)
    res = Vector{Any}(undef, length(cands))
    Threads.@threads for i in eachindex(cands)
        try
            res[i] = certify_one(cands[i])
        catch
            c = cands[i]
            res[i] = (n=c.n, k=c.k, d0=c.d0, d=c.d0, status="ERR", l=c.l, m=c.m, A=c.A, B=c.B)
        end
    end
    out = [r for r in res if r !== nothing]
    fomc(r) = r.k * r.d^2 / r.n
    elites = sort(out, by=r -> -fomc(r))
    open(OUT, "w") do io
        println(io, "# CERTIFIED frontier — blind-zero (post-scan certification)")
        println(io, "")
        println(io, "d = EXACT (min_distance_bz gap=0, small codes) or UB (tightened high-effort BP-OSD).")
        println(io, "d0 = original cheap-scan BP-OSD bound; a large d0 -> d drop = a scan overestimate demoted.")
        @printf(io, "certified %d codes (%d EXACT, %d tightened-UB, %d err)\n\n",
                length(out), count(r -> r.status == "EXACT", out),
                count(r -> r.status == "UB", out), count(r -> r.status == "ERR", out))
        println(io, "| [[n,k,d]] | status | d0(scan) | FOM | k/n | (l,m) | A | B |")
        println(io, "|---|---|---|---|---|---|---|---|")
        for r in elites
            @printf(io, "| [[%d,%d,%d]] | %s | %d | %.2f | %.3f | (%d,%d) | %s | %s |\n",
                    r.n, r.k, r.d, r.status, r.d0, fomc(r), r.k / r.n, r.l, r.m, r.A, r.B)
        end
    end
    @printf("DONE: %d certified (%d EXACT); wrote %s\n",
            length(out), count(r -> r.status == "EXACT", out), OUT)
    println("top certified:")
    for r in elites[1:min(15, length(elites))]
        @printf("  [[%d,%d,%d]] %s  (scan d0=%d)  FOM=%.2f\n", r.n, r.k, r.d, r.status, r.d0, fomc(r))
    end
end

main()
