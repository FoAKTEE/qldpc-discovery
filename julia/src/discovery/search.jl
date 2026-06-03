# Blind generator-ansatz search over BB codes (catalog-blind, FOM-driven).
# Pure-Julia port of qcode_discovery/discovery/search.py.
#
# Reproduces the paper's search FRAMEWORK without its answers: seeds are NAIVE random polynomials
# (never the paper's discovered (A,B)). The only signal is the kernel fitness (FOM = k d^2 / n via
# the evaluation cascade). A MAP-Elites-lite archive bins candidates by (l,m,k) keeping the best
# FOM, so the search illuminates the rate--distance frontier rather than being told it. The GA
# mutates exponents of elites — the paper's non-LLM baseline. Paper anchor: arXiv:2606.02418 sec IV.A.
#
# RNG NOTE: Python uses `random.Random(seed)` (Mersenne Twister, .sample/.randrange/.random/.choice).
# Here we use Julia's `Random.MersenneTwister(seed)`. Both are seeded MT but the EXACT sampled
# sequences differ (different stream algorithms), so a blind search is cross-validated STRUCTURALLY
# (it runs and returns a valid frontier), not bit-for-bit — exactly as the spec requires.

import Random

# --------------------------------------------------------------------------------------------
# Naive random / mutation operators on polynomial term lists (blind seeds).
# --------------------------------------------------------------------------------------------

"""A naive random polynomial: `weight` distinct monomials x^a y^b, a in Z_l, b in Z_m.
No paper structure injected — uniform over the monomial lattice (blind seed)."""
function random_polynomial(l::Int, m::Int, weight::Int, rng::Random.AbstractRNG)
    all_mons = [(a, b) for a in 0:l-1 for b in 0:m-1]
    weight >= length(all_mons) && return sort(all_mons)
    chosen = Random.randperm(rng, length(all_mons))[1:weight]
    return sort([all_mons[i] for i in chosen])
end

"""Mutate one monomial of a polynomial: shift an exponent by ±1, or resample the term entirely
(blind operator). Weight is preserved: a collision (the new monomial already present) is rejected
by returning the original term list, matching Python's `mutate_polynomial`."""
function mutate_polynomial(terms, l::Int, m::Int, rng::Random.AbstractRNG)
    terms = collect(terms)
    isempty(terms) && return terms
    i = rand(rng, 1:length(terms))
    a, b = terms[i]
    if rand(rng) < 0.5                                    # shift one exponent by ±1
        if rand(rng) < 0.5
            a = mod(a + rand(rng, (-1, 1)), l)
        else
            b = mod(b + rand(rng, (-1, 1)), m)
        end
    else                                                  # resample the monomial entirely
        a, b = rand(rng, 0:l-1), rand(rng, 0:m-1)
    end
    cand = Set(terms)
    delete!(cand, terms[i])
    push!(cand, (a, b))
    out = sort(collect(cand))
    return length(out) == length(terms) ? out : collect(terms)   # reject collision (keep weight)
end

# --------------------------------------------------------------------------------------------
# MAP-Elites-lite archive: best-FOM elite per (l,m,k) bin.
# --------------------------------------------------------------------------------------------

"""MAP-Elites-lite archive: keeps the best-FOM elite per (l, m, k) bin. Illuminates the k vs d
frontier. `cells` maps (l,m,k) -> the evaluation NamedTuple of the current elite."""
mutable struct Archive
    cells::Dict{Tuple{Int,Int,Int},Any}
end
Archive() = Archive(Dict{Tuple{Int,Int,Int},Any}())

"""Insert `result` if it beats the current FOM elite of its (l,m,k) cell. Returns true if it did."""
function consider!(arch::Archive, result)
    (result.d === nothing || result.fom <= 0) && return false
    key = (result.l, result.m, result.k)
    cur = get(arch.cells, key, nothing)
    if cur === nothing || result.fom > cur.fom
        arch.cells[key] = result
        return true
    end
    return false
end

"""All cell elites, sorted by FOM descending (the discovered rate--distance frontier)."""
elites(arch::Archive) = sort(collect(values(arch.cells)); by=r -> r.fom, rev=true)

# --------------------------------------------------------------------------------------------
# The blind CSS BB search.
# --------------------------------------------------------------------------------------------

"""Run a blind CSS BB search over the given `lattices` :: Vector of (l, m) tuples.

Phase 1: sample `n_random` naive weight-`weight` polynomial pairs per lattice, Stage-1 screen k,
take a k-DIVERSE selection of up to `distance_budget` survivors (round-robin across distinct k
values), Stage-2 evaluate distance -> FOM, populate the archive.
Phase 2 (optional): `generations` of FOM-hill-climbing GA mutating archive elites.

Returns a NamedTuple `(archive_elites, evaluated, n_evaluated, n_distance_evals)`.
A BP-OSD trust filter (paper Sec V.D) discards d/sqrt(n) >= `trust_high` upper bounds so an
overestimated d=2 trap cannot fake a high FOM. NO paper data consulted."""
function blind_search_css(lattices; n_random::Int=400, generations::Int=0, distance_budget::Int=8,
                          weight::Int=3, time_limit::Real=3.0, seed::Int=0,
                          distance_method::Symbol=:milp, trust_high::Real=2.0, log=nothing)
    rng = Random.MersenneTwister(seed)
    arch = Archive()
    n_eval = 0
    n_dist = 0
    evaluated = Any[]
    say = log === nothing ? (_...) -> nothing : log

    for (l, m) in lattices
        # Phase 1: cheap k-screen of random polynomial pairs.
        screened = Tuple{Int,Vector{Tuple{Int,Int}},Vector{Tuple{Int,Int}}}[]
        for _ in 1:n_random
            A = random_polynomial(l, m, weight, rng)
            B = random_polynomial(l, m, weight, rng)
            n_eval += 1
            k = screen_k_css(l, m, A, B)
            k > 0 && push!(screened, (k, A, B))
        end
        # k-DIVERSE selection (not top-by-k): spread across distinct k so low-k high-distance codes
        # are evaluated alongside high-k (often d=2 trap) codes. FOM decides.
        by_k = Dict{Int,Vector{Tuple{Vector{Tuple{Int,Int}},Vector{Tuple{Int,Int}}}}}()
        seen = Set{Tuple{Vector{Tuple{Int,Int}},Vector{Tuple{Int,Int}}}}()
        for (k, A, B) in screened
            sig = (A, B)
            sig in seen && continue
            push!(seen, sig)
            push!(get!(by_k, k, Vector{Tuple{Vector{Tuple{Int,Int}},Vector{Tuple{Int,Int}}}}()), (A, B))
        end
        selection = Tuple{Int,Vector{Tuple{Int,Int}},Vector{Tuple{Int,Int}}}[]
        ks = sort(collect(keys(by_k)))                    # round-robin one per k-value until budget filled
        if !isempty(ks)
            ri = 0
            while length(selection) < distance_budget && any(!isempty, values(by_k))
                k = ks[(ri % length(ks)) + 1]
                if !isempty(by_k[k])
                    A, B = popfirst!(by_k[k])
                    push!(selection, (k, A, B))
                end
                ri += 1
                ri > length(ks) * (distance_budget + 2) && break
            end
        end
        for (k, A, B) in selection
            res = evaluate_css(l, m, A, B; distance_method=distance_method, time_limit=time_limit)
            n_dist += 1
            # trust filter (only for BP-OSD upper bounds): discard d/sqrt(n) >= trust_high.
            trusted = (distance_method !== :bposd) ||
                      ((res.d_over_sqrt_n === nothing ? 0.0 : res.d_over_sqrt_n) < trust_high)
            if res.d !== nothing && trusted
                push!(evaluated, res)
                if consider!(arch, res)
                    say("  [$l,$m] discovered [[$(res.n),$(res.k),$(res.d)]] " *
                        "FOM=$(round(res.fom; digits=2)) exact=$(res.exact)")
                end
            end
        end
    end

    # Phase 2: GA hill-climbing on elites (FOM fitness).
    for g in 1:generations
        for elite in elites(arch)[1:min(end, max(1, distance_budget ÷ 2))]
            l, m = elite.l, elite.m
            A = mutate_polynomial(elite.A, l, m, rng)
            B = mutate_polynomial(elite.B, l, m, rng)
            screen_k_css(l, m, A, B) == 0 && continue
            res = evaluate_css(l, m, A, B; distance_method=distance_method, time_limit=time_limit)
            n_dist += 1
            trusted = (distance_method !== :bposd) ||
                      ((res.d_over_sqrt_n === nothing ? 0.0 : res.d_over_sqrt_n) < trust_high)
            if res.d !== nothing && trusted
                push!(evaluated, res)
                if consider!(arch, res)
                    say("  gen$g [$l,$m] improved [[$(res.n),$(res.k),$(res.d)]] " *
                        "FOM=$(round(res.fom; digits=2)) exact=$(res.exact)")
                end
            end
        end
    end

    return (archive_elites=elites(arch), evaluated=evaluated,
            n_evaluated=n_eval, n_distance_evals=n_dist)
end
