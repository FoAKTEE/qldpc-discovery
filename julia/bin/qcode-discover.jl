#!/usr/bin/env julia
# qcode-discover — CLI for catalog-blind BB code discovery (pure Julia).
#
#   julia --project=julia -t auto julia/bin/qcode-discover.jl [--lattices 6x6,12x6]
#         [--n-random 400] [--budget 8] [--gens 0] [--method bposd|milp] [--seed 0] [--validate]
#
# Discovery is catalog-blind; --validate runs the post-hoc comparison vs built-in landmark codes.

include(joinpath(@__DIR__, "..", "src", "QCodeDiscovery.jl"))
using .QCodeDiscovery

function getarg(flag, default)
    i = findfirst(==(flag), ARGS)
    i === nothing || i == length(ARGS) ? default : ARGS[i + 1]
end
has(flag) = flag in ARGS

lattices = [Tuple(parse.(Int, split(p, "x"))) for p in split(getarg("--lattices", "6x6,12x6"), ",")]
nrand    = parse(Int, getarg("--n-random", "400"))
budget   = parse(Int, getarg("--budget", "8"))
gens     = parse(Int, getarg("--gens", "0"))
method   = Symbol(getarg("--method", "bposd"))
seed     = parse(Int, getarg("--seed", "0"))

println("blind discovery (catalog-blind): lattices=$lattices n_random=$nrand budget=$budget gens=$gens method=$method seed=$seed")
out = blind_search_css(lattices; n_random=nrand, distance_budget=budget, generations=gens,
                       distance_method=method, seed=seed)
println("evaluated $(out.n_evaluated); $(length(out.archive_elites)) archive elites (FOM-ranked):")
for el in out.archive_elites
    println("  [[$(el.n),$(el.k),$(el.d)]] FOM=$(round(el.fom, digits=2)) exact=$(el.exact)")
end

if has("--validate")
    println("\npost-hoc validation vs landmark codes:")
    rep = validate(out.archive_elites; kind=:css)
    for r in rep.results
        println("  $(r.discovery)  $(r.verdict)  $(something(r.matched_ref, ""))")
    end
    println("summary: $(rep.summary)")
end
