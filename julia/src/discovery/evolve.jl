# Generator-ansatz program evolution (the paper's core representation).
# Pure-Julia port of qcode_discovery/discovery/evolve.py (GA-G non-LLM baseline).
#
# arXiv:2606.02418 evolves a GENERATOR ANSATZ — a program G(l,m) -> {(A_i,B_i)} that emits candidate
# codes for ANY lattice from an algebraic pattern (so one mutation like "use x^{l/3}" generalizes
# across all block lengths). This differs from search.jl, which mutates polynomial tuples directly.
# Here an ansatz is a set of parameterized algebraic STRATEGIES; mutation operators edit the program
# (GA-G, the runnable non-LLM baseline). The LLM mutation operator (the paper's headline) needs a
# funded API key + openevolve and is not runnable here.
#
# RNG: Julia's Random.MersenneTwister(seed) (seeded; naive — no paper data). Mutation PRESERVES
# polynomial weight per strategy (param edits / add / remove strategy; never change a monomial count).

import Random

# --------------------------------------------------------------------------------------------
# Safe exponent expressions over {l, m, ints, + - * ÷ %} (the LLM-proposed "custom" strategy).
# --------------------------------------------------------------------------------------------

"""Evaluate an exponent expression over {l, m, ints, + - * ÷ %} for the `:custom` strategy.
`expr` is an Int (returned as-is) or a closure (l, m) -> Int. This mirrors Python's `_safe_expr`,
which parses a restricted AST; in Julia we accept a typed closure so no `eval` of arbitrary code
is ever performed (catalog-blind and injection-safe)."""
_safe_expr(expr::Integer, l::Int, m::Int) = Int(expr)
_safe_expr(expr::Function, l::Int, m::Int) = Int(expr(l, m))

# --------------------------------------------------------------------------------------------
# The generator ansatz: a list of parameterized strategies emitting (A,B) for any (l,m).
# --------------------------------------------------------------------------------------------

"""A program: a list of parameterized algebraic strategies emitting (A,B) for any (l,m).
Each strategy is a Dict with :kind (a Symbol) and :params (a Dict)."""
mutable struct GeneratorAnsatz
    strategies::Vector{Dict{Symbol,Any}}
end
GeneratorAnsatz() = GeneratorAnsatz(Dict{Symbol,Any}[])

"""One strategy -> one (A_terms, B_terms). Exponents are scaled to the lattice (multi-lattice).
Mirrors Python `_emit` for kinds :xyswap, :univariate, :custom."""
function _emit(strategy::Dict{Symbol,Any}, l::Int, m::Int)
    k = strategy[:kind]
    p = strategy[:params]
    if k === :xyswap                       # A = x^a + y^b + y^c ; B = y^d + x^e + x^f
        A = [(mod(p[:a], l), 0), (0, mod(p[:b], m)), (0, mod(p[:c], m))]
        B = [(0, mod(p[:d], m)), (mod(p[:e], l), 0), (mod(p[:f], l), 0)]
    elseif k === :univariate               # A = 1 + y + y^2 ; B = 1 + x^j + x^{2j}, j scaled to l
        jraw = (p[:j_num] * l) ÷ p[:j_den]
        j = mod(max(1, jraw), l)
        j == 0 && (j = 1)
        A = [(0, 0), (0, mod(1, m)), (0, mod(2, m))]
        B = [(0, 0), (j, 0), (mod(2 * j, l), 0)]
    elseif k === :custom                   # A,B as monomials with exponents expr(l,m)
        A = [(mod(_safe_expr(a, l, m), l), mod(_safe_expr(b, l, m), m)) for (a, b) in p[:A]]
        B = [(mod(_safe_expr(a, l, m), l), mod(_safe_expr(b, l, m), m)) for (a, b) in p[:B]]
    else
        error("unknown strategy $k")
    end
    return sort(unique(A)), sort(unique(B))
end

"""Emit candidate (A_terms, B_terms) pairs for lattice (l,m) from each strategy (skipping any that
raise)."""
function generate(ansatz::GeneratorAnsatz, l::Int, m::Int)
    out = Tuple{Vector{Tuple{Int,Int}},Vector{Tuple{Int,Int}}}[]
    for s in ansatz.strategies
        try
            push!(out, _emit(s, l, m))
        catch
            continue
        end
    end
    return out
end

# --------------------------------------------------------------------------------------------
# Naive random ansatz + GA-G program mutation (weight-preserving).
# --------------------------------------------------------------------------------------------

"""A naive random ansatz (1-2 strategies) — NOT seeded from any paper code (blind)."""
function random_ansatz(rng::Random.AbstractRNG)
    params = Dict{Symbol,Any}(x => rand(rng, 1:6) for x in (:a, :b, :c, :d, :e, :f))
    strategies = Dict{Symbol,Any}[Dict(:kind => :xyswap, :params => params)]
    if rand(rng) < 0.5
        push!(strategies, Dict{Symbol,Any}(:kind => :univariate,
                                           :params => Dict{Symbol,Any}(:j_num => rand(rng, 1:2), :j_den => 3)))
    end
    return GeneratorAnsatz(strategies)
end

"""GA-G program mutation: perturb a strategy's exponent params, or add/remove a strategy.
WEIGHT-PRESERVING: it edits exponent values / adds / removes a strategy but never changes the
number of monomials a strategy emits (so each emitted polynomial keeps its weight). Mirrors
Python `mutate_ansatz`."""
function mutate_ansatz(ansatz::GeneratorAnsatz, rng::Random.AbstractRNG)
    strat = Dict{Symbol,Any}[Dict(:kind => s[:kind], :params => copy(s[:params]))
                             for s in ansatz.strategies]
    roll = rand(rng)
    if roll < 0.7 && !isempty(strat)                       # perturb a param
        s = strat[rand(rng, 1:length(strat))]
        keys_list = collect(keys(s[:params]))
        key = rand(rng, keys_list)
        s[:params][key] = max(1, s[:params][key] + rand(rng, (-1, 1)))
    elseif roll < 0.85                                     # add a strategy
        push!(strat, random_ansatz(rng).strategies[1])
    elseif length(strat) > 1                               # remove a strategy
        deleteat!(strat, rand(rng, 1:length(strat)))
    end
    return GeneratorAnsatz(strat)
end

# --------------------------------------------------------------------------------------------
# Fitness + GA-G evolution loop.
# --------------------------------------------------------------------------------------------

"""Total FOM of the codes an ansatz generates across `lattices` (the paper's combined score).
Uses the BP-OSD distance estimator with the trust filter (paper Campaigns 1-3 caveat: BP-OSD
overestimates d for high-k codes, so reported codes are UPPER BOUNDS — verify via exact Stage-3
before treating as discoveries). Returns (score, codes, n_lattices_with_code)."""
function ansatz_fitness(ansatz::GeneratorAnsatz, lattices; time_limit::Real=2.0,
                        distance_method::Symbol=:bposd, isd_iters::Int=600)
    codes = Any[]
    total = 0.0
    for (l, m) in lattices
        for (A, B) in generate(ansatz, l, m)
            r = evaluate_css(l, m, A, B; distance_method=distance_method, time_limit=time_limit, isd_iters=isd_iters)
            if r.d !== nothing && r.trusted
                push!(codes, r)
                total += r.fom
            end
        end
    end
    nl = length(Set((c.l, c.m) for c in codes))
    return (score=total, codes=codes, n_lattices_with_code=nl)
end

"""GA-G program evolution: evolve generator ANSAETZE (not tuples) by total cross-lattice FOM.
Blind (random seeds). Returns (best_ansatz, best). The fitness uses BP-OSD distance (UPPER bound)
— survivors MUST be passed through the exact Stage-3 (`evaluate_css(...; distance_method=:milp)`)
before being treated as discoveries, exactly as the paper added MILP-in-the-loop for Campaigns 4-5."""
function evolve_ansaetze(lattices; generations::Int=4, pop::Int=6, time_limit::Real=1.0,
                         seed::Int=0, log=nothing, distance_method::Symbol=:bposd, isd_iters::Int=600)
    rng = Random.MersenneTwister(seed)
    say = log === nothing ? (_...) -> nothing : log
    fit(a) = ansatz_fitness(a, lattices; time_limit=time_limit, distance_method=distance_method, isd_iters=isd_iters)
    population = Tuple{GeneratorAnsatz,Any}[]
    for _ in 1:pop
        a = random_ansatz(rng)
        push!(population, (a, fit(a)))
    end
    for g in 0:generations-1
        sort!(population; by=t -> t[2].score, rev=true)
        best = population[1]
        say("  gen$g: best score=$(round(best[2].score; digits=2)) over " *
            "$(best[2].n_lattices_with_code) lattices")
        survivors = population[1:max(1, pop ÷ 2)]
        children = Tuple{GeneratorAnsatz,Any}[]
        for (a, _) in survivors
            child = mutate_ansatz(a, rng)
            push!(children, (child, fit(child)))
        end
        population = vcat(survivors, children)
    end
    sort!(population; by=t -> t[2].score, rev=true)
    return (best_ansatz=population[1][1], best=population[1][2])
end
