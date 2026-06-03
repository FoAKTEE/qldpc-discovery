# POST-HOC validation: classify BLIND discoveries against known landmark codes.
# Pure-Julia port of qcode_discovery/discovery/validation.py (the landmark/validate path).
#
# This module is the Julia analogue of the ONLY Python module permitted to look at the
# held-out paper reference. Here we DO NOT bundle the paper catalog (.tex parsing) — per the
# task we use the built-in landmark codes ONLY (the Bravyi gross-code family, Sec V.B). It
# classifies each post-hoc discovery as POLY_MATCH / MATCH / UB_CONSISTENT / NOVEL_AT_N /
# PARAMS_NOT_IN_REF_AT_N exactly as the Python `validate(..., catalog_tex=None, kind="css")`.
#
# Paper anchor: arXiv:2606.02418 Sec V.B (post-hoc, held-out validation only).

"""
    landmark_codes() -> Vector{NamedTuple}

Paper-referenced CSS landmark/validation codes (Bravyi gross-code family, Sec V.B).
Each entry: (l, m, n, k, d, d_is_upper, A, B, pattern, source). Mirrors the Python
`landmark_codes()` list exactly (same two codes, same fields/values).
"""
function landmark_codes()
    return [
        (l = 12, m = 6, n = 144, k = 12, d = 12, d_is_upper = false,
         A = "y+y^2+x^3", B = "y^3+x+x^2", pattern = "gross",
         source = "landmark:bravyi2024high"),
        (l = 6, m = 6, n = 72, k = 12, d = 6, d_is_upper = false,
         A = "y+y^2+x^3", B = "y^3+x+x^2", pattern = "gross-family",
         source = "landmark:bravyi2024high(MILP-validation)"),
    ]
end

"""
    _normalize_terms(terms, l, m) -> Vector{Tuple{Int,Int}}

Reduce monomial exponents mod (l, m), cancel terms that appear an even number of times
(mod-2 ring arithmetic), then return the sorted, deduped survivors. Port of
`qcode_discovery.algebra.polynomials.normalize_terms`. NOTE: this is needed because the
existing Julia `parse_terms` reduces exponents mod (l,m) but does NOT cancel mod 2; the
polynomial-set match in Python compares the mod-2-reduced sets.
"""
function _normalize_terms(terms, l::Int, m::Int)
    counts = Dict{Tuple{Int,Int},Int}()
    for (a, b) in terms
        key = (mod(a, l), mod(b, m))
        counts[key] = get(counts, key, 0) + 1
    end
    survivors = [t for (t, c) in counts if isodd(c)]
    return sort(survivors)
end

"""
    _poly_set(expr, l, m) -> Union{Set{Tuple{Int,Int}}, Nothing}

The normalized monomial set of a polynomial, or `nothing` on parse failure. `expr` may be a
polynomial string (parsed with `parse_terms`) or an iterable of `(a,b)` tuples. Mirrors the
Python `_poly_set` (which returns a frozenset, or None on exception).
"""
function _poly_set(expr, l::Int, m::Int)
    try
        terms = expr isa AbstractString ? parse_terms(expr, l, m) :
                [(Int(t[1]), Int(t[2])) for t in expr]
        return Set(_normalize_terms(terms, l, m))
    catch
        return nothing
    end
end

"""
    validate(discoveries; kind=:css) -> NamedTuple

Classify each blind discovery against the built-in landmark codes (held-out reference).
`discoveries` is a vector of NamedTuples/Dicts with keys `n, k, l, m, A, B` and optionally
`d`, `exact`, `fom`. `kind` accepts `:css` only here (the `:pbb` path requires the paper
catalog, which is deliberately NOT bundled — see module docstring); any other kind errors.

Classification per discovery (identical precedence to Python `validate`):
  - `POLY_MATCH`             : same (l,m) and identical (A,B) polynomial sets as a reference.
  - `MATCH`                  : same (n,k), our exact d equals an exact reference d.
  - `UB_CONSISTENT`          : same (n,k), our (upper-bound) d <= a reference d.
  - `NOVEL_AT_N`             : no reference code at this n.
  - `PARAMS_NOT_IN_REF_AT_N` : reference codes exist at this n but none match (k/d).

Returns `(n_reference_codes, results, summary)` where `results` is a Vector{NamedTuple}
`(discovery, fom, exact, verdict, matched_ref)` and `summary` is a Dict{String,Int} of
verdict counts. Mirrors the Python report dict shape.
"""
function validate(discoveries; kind::Symbol = :css)
    if kind != :css
        throw(ArgumentError("kind=$kind unsupported in the Julia port: only :css " *
                            "(built-in landmarks) is available; the :pbb path needs the " *
                            "paper catalog, which is intentionally not bundled."))
    end
    reference = landmark_codes()
    ref_by_n = Dict{Int,Vector{eltype(reference)}}()
    for r in reference
        push!(get!(ref_by_n, r.n, eltype(reference)[]), r)
    end

    getf(disc, key, default = nothing) =
        disc isa NamedTuple ? get(disc, key, default) : get(disc, key, default)

    results = NamedTuple[]
    for disc in discoveries
        n = getf(disc, :n)
        k = getf(disc, :k)
        d = getf(disc, :d)
        d_exact = getf(disc, :exact, false) === true
        l = getf(disc, :l)
        mm = getf(disc, :m)
        refs = get(ref_by_n, n, eltype(reference)[])

        verdict = "NOVEL_AT_N"
        matched = nothing
        if isempty(refs)
            verdict = "NOVEL_AT_N"
        else
            disc_A = _poly_set(getf(disc, :A), l, mm)
            disc_B = _poly_set(getf(disc, :B), l, mm)
            for r in refs
                r.k != k && continue
                rA = _poly_set(r.A, r.l, r.m)
                rB = _poly_set(r.B, r.l, r.m)
                poly_hit = (disc_A !== nothing && rA !== nothing &&
                            Set([disc_A, disc_B]) == Set([rA, rB]))
                # Identical polynomials => the SAME code. POLY_MATCH regardless of our
                # d-estimate (an upper bound may overestimate the reference's true d).
                if poly_hit
                    verdict, matched = "POLY_MATCH", r
                    break
                end
                if d !== nothing && d == r.d && d_exact && !r.d_is_upper
                    verdict, matched = "MATCH", r
                    break
                end
                if d !== nothing && d <= r.d                 # our (possibly UB) d consistent
                    verdict, matched = "UB_CONSISTENT", r
                end
            end
            if matched === nothing && !isempty(refs)
                verdict = "PARAMS_NOT_IN_REF_AT_N"
            end
        end

        matched_ref = matched === nothing ? nothing :
            "[[$(matched.n),$(matched.k),$(matched.d)$(matched.d_is_upper ? "(<=)" : "")]] " *
            matched.source
        push!(results, (discovery = "[[$n,$k,$d]]", fom = getf(disc, :fom),
                        exact = d_exact, verdict = verdict, matched_ref = matched_ref))
    end

    summary = Dict{String,Int}()
    for r in results
        summary[r.verdict] = get(summary, r.verdict, 0) + 1
    end
    return (n_reference_codes = length(reference), results = results, summary = summary)
end
