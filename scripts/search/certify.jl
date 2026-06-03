#!/usr/bin/env julia
# CERTIFIER — re-evaluate the blind-scan frontier with HIGH-EFFORT / EXACT distance.
# Per code, parallel across cores:
#   CSS cells:
#     (1) MULTI-SEED high-effort BP-OSD (SEEDS independent restarts, many trials, large max_iter) —
#         take the MIN bound; the thorough pass finds low-weight logicals the cheap scan missed, so
#         BP-OSD OVERESTIMATES collapse. The (d0 - d) "spread" column flags still-loose UBs.
#     (2) EXACT certification, in order of feasibility:
#         - enumeration `css_distance_enum` for low-distance codes (d<=ENUM_MAXW, n<=ENUM_NMAX) — EXACT
#           if the small-weight space is exhausted (cheap even for large n when d is small);
#         - else Brouwer–Zimmermann `min_distance_bz` for n<=BZ_NMAX — EXACT certificate (gap=0).
#   PBB cells (fam=pbb): exact symplectic Brouwer–Zimmermann `symplectic_distance` (re-run at high cap).
# Output: a certified frontier showing d0 (scan bound) -> d (certified/tightened) + EXACT/UB status.
# Honest: large CSS codes get a tightened UPPER bound (status=UB); small ones / low-d / all PBB EXACT.
#
# Run (after the scan):  julia --project=julia -t 200 scripts/search/certify.jl
#   env: IN (frontier .tsv), OUT (certified .md), HITRIALS (300), HIMAXITER (120), SEEDS (3),
#        ENUM_NMAX (360), ENUM_MAXW (8), BZ_NMAX (200), BZCAP (20000000), PBB_CAP (20000000)

using QCodeDiscovery, Printf

const IN        = get(ENV, "IN",  joinpath(@__DIR__, "frontier.md.tsv"))
const OUT       = get(ENV, "OUT", joinpath(@__DIR__, "certified.md"))
const HITRIALS  = parse(Int, get(ENV, "HITRIALS", "300"))
const HIMAXITER = parse(Int, get(ENV, "HIMAXITER", "120"))
const SEEDS     = parse(Int, get(ENV, "SEEDS", "1"))
const ISD_ITERS = parse(Int, get(ENV, "ISD_ITERS", "1200"))   # Lee–Brickell info-set decoding iterations
const ISD_PMAX  = parse(Int, get(ENV, "ISD_PMAX", "2"))
const ENUM_NMAX = parse(Int, get(ENV, "ENUM_NMAX", "360"))
const ENUM_MAXW = parse(Int, get(ENV, "ENUM_MAXW", "8"))
const ENUM_BUDGET = parse(Float64, get(ENV, "ENUM_BUDGET", "5e7"))  # max C(n,1..w) before skipping enum
const BZ_NMAX   = parse(Int, get(ENV, "BZ_NMAX", "200"))
const BZCAP     = parse(Int, get(ENV, "BZCAP", "20000000"))
const PBB_CAP   = parse(Int, get(ENV, "PBB_CAP", "20000000"))

struct Cand
    n::Int; k::Int; d0::Int; l::Int; m::Int; A::String; B::String; fam::String; C::String; D::String
end

function load(path)
    cands = Cand[]
    for (i, ln) in enumerate(eachline(path))
        i == 1 && continue                       # header
        f = split(ln, '\t')
        length(f) < 8 && continue
        fam = length(f) >= 10 ? String(f[10]) : "css"
        C   = length(f) >= 11 ? String(f[11]) : ""
        D   = length(f) >= 12 ? String(f[12]) : ""
        push!(cands, Cand(parse(Int, f[1]), parse(Int, f[2]), parse(Int, f[3]),
                          parse(Int, f[5]), parse(Int, f[6]), String(f[7]), String(f[8]), fam, C, D))
    end
    return cands
end

# total combinations C(n,1)+...+C(n,w) — gate the (expensive) column enumeration to a tractable budget.
_enum_combos(n::Int, w::Int) = sum(Float64(binomial(big(n), j)) for j in 1:w)

# CSS: tighten the UPPER bound (ISD + BP-OSD), then try to certify EXACT (Brouwer–Zimmermann / enum).
function certify_css(c::Cand)
    code = BBCode(c.l, c.m, c.A, c.B)
    ub = c.d0
    # Lee–Brickell ISD: finds low-weight logicals BP-OSD misses -> the strongest UPPER-bound tightener,
    # and the only thing that meaningfully demotes large-n overestimates (where exact BZ is infeasible).
    isd = min_distance_isd(code; iters=ISD_ITERS, pmax=ISD_PMAX, seed=99)
    isd.d > 0 && (ub = min(ub, isd.d))
    for s in 1:SEEDS                                       # BP-OSD cross-check
        r = bposd_distance(code; trials=HITRIALS, max_iter=min(code.n, HIMAXITER), seed=12345 + 1009 * s)
        r.d_bound === nothing || (ub = min(ub, r.d_bound))
    end
    # (2a) Brouwer–Zimmermann over the logical generators (allocation-free, cap-bounded): finds light
    #      real logicals (tightening the UB — this is what demotes BP-OSD overestimates) and CERTIFIES
    #      where the increasing-weight enumeration completes.
    if code.n <= BZ_NMAX
        bz = min_distance_bz(code; cap=BZCAP)
        bz.d > 0 && (ub = min(ub, bz.d))
        bz.certified && bz.d > 0 && return (d=bz.d, status="EXACT")
    end
    # (2b) direct small-weight enumeration is EXACT when exhausted — only when actually tractable
    #      (C(n,1..ub) <= ENUM_BUDGET); else skip (BZ already supplied the tightened UB).
    if code.n <= ENUM_NMAX && 1 <= ub <= ENUM_MAXW && _enum_combos(code.n, ub) <= ENUM_BUDGET
        e = css_distance_enum(code; max_weight=ub)
        e.exhausted && return (d=e.d, status="EXACT")
    end
    return (d=ub, status="UB")
end

# PBB: exact symplectic Brouwer–Zimmermann (re-run at a high cap).
function certify_pbb(c::Cand)
    code = PBBCode(c.l, c.m, c.A, c.B, c.C, c.D)
    r = symplectic_distance(code; cap=PBB_CAP)
    d = (r.d === nothing || r.d <= 0) ? c.d0 : r.d
    return (d=d, status=r.certified ? "EXACT" : "UB")
end

function certify_one(c::Cand)
    res = c.fam == "pbb" ? certify_pbb(c) : certify_css(c)
    d = res.status == "UB" ? min(res.d, c.d0) : res.d      # a UB is never reported worse than the scan
    return (n=c.n, k=c.k, d0=c.d0, d=d, spread=c.d0 - d, status=res.status,
            fam=c.fam, l=c.l, m=c.m, A=c.A, B=c.B, C=c.C, D=c.D)
end

function main()
    cands = load(IN)
    @printf("certifying %d frontier codes (SEEDS=%d HITRIALS=%d HIMAXITER=%d ENUM<=%d@n<=%d BZ_NMAX=%d) on %d threads\n",
            length(cands), SEEDS, HITRIALS, HIMAXITER, ENUM_MAXW, ENUM_NMAX, BZ_NMAX, Threads.nthreads()); flush(stdout)
    res = Vector{Any}(undef, length(cands))
    Threads.@threads for i in eachindex(cands)
        try
            res[i] = certify_one(cands[i])
        catch
            c = cands[i]
            res[i] = (n=c.n, k=c.k, d0=c.d0, d=c.d0, spread=0, status="ERR",
                      fam=c.fam, l=c.l, m=c.m, A=c.A, B=c.B, C=c.C, D=c.D)
        end
    end
    out = [r for r in res if r !== nothing]
    fomc(r) = r.k * r.d^2 / r.n
    elites = sort(out, by=r -> -fomc(r))
    open(OUT, "w") do io
        println(io, "# CERTIFIED frontier — blind-zero (post-scan certification)")
        println(io, "")
        println(io, "d = EXACT (enumeration / Brouwer–Zimmermann gap=0, or exact PBB symplectic) or UB (tightened multi-seed BP-OSD).")
        println(io, "d0 = original cheap-scan bound; spread = d0 - d (large spread => the scan bound was a loose overestimate).")
        @printf(io, "certified %d codes (%d EXACT, %d tightened-UB, %d err)\n\n",
                length(out), count(r -> r.status == "EXACT", out),
                count(r -> r.status == "UB", out), count(r -> r.status == "ERR", out))
        println(io, "| [[n,k,d]] | status | d0 | spread | FOM | k/n | fam | (l,m) | A | B | C | D |")
        println(io, "|---|---|---|---|---|---|---|---|---|---|---|---|")
        for r in elites
            @printf(io, "| [[%d,%d,%d]] | %s | %d | %d | %.2f | %.3f | %s | (%d,%d) | %s | %s | %s | %s |\n",
                    r.n, r.k, r.d, r.status, r.d0, r.spread, fomc(r), r.k / r.n, r.fam, r.l, r.m, r.A, r.B, r.C, r.D)
        end
    end
    @printf("DONE: %d certified (%d EXACT); wrote %s\n",
            length(out), count(r -> r.status == "EXACT", out), OUT)
    println("top certified:")
    for r in elites[1:min(15, length(elites))]
        @printf("  [[%d,%d,%d]] %s %s  (scan d0=%d, spread=%d)  FOM=%.2f\n",
                r.n, r.k, r.d, r.status, r.fam, r.d0, r.spread, fomc(r))
    end
end

main()
