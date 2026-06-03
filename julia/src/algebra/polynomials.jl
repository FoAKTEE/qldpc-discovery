# Ring R = F2[x,y]/(x^l - 1, y^m - 1): parse polynomial strings and build circulants.
# Port of qcode_discovery/algebra/polynomials.py.

"""Parse a polynomial string (e.g. \"y+y^2+x^3\", \"1+x+y\", \"x^9y^5+x^2y^4\") into a list of
monomials `(a, b)` meaning x^a y^b, with exponents reduced mod (l, m). `1` is the (0,0) monomial."""
function parse_terms(s::AbstractString, l::Int, m::Int)
    terms = Tuple{Int,Int}[]
    for raw in split(replace(String(s), " " => ""), '+')
        isempty(raw) && continue
        a = 0
        b = 0
        mx = match(r"x(?:\^(\d+))?", raw)
        if mx !== nothing
            a = mx.captures[1] === nothing ? 1 : parse(Int, mx.captures[1])
        end
        my = match(r"y(?:\^(\d+))?", raw)
        if my !== nothing
            b = my.captures[1] === nothing ? 1 : parse(Int, my.captures[1])
        end
        push!(terms, (mod(a, l), mod(b, m)))
    end
    return terms
end

"""The (lm × lm) bivariate circulant of a polynomial over R, with the index map
idx(i,j) = i*m + j. A monomial x^a y^b is the cyclic shift (i,j) -> ((i+a) mod l, (j+b) mod m);
the matrix is the mod-2 sum of the monomials' shift matrices."""
function circulant(terms, l::Int, m::Int)
    lm = l * m
    C = zeros(UInt8, lm, lm)
    for (a, b) in terms
        for i in 0:l-1, j in 0:m-1
            row = i * m + j + 1
            col = mod(i + a, l) * m + mod(j + b, m) + 1
            C[row, col] ⊻= 0x1   # XOR accumulate: repeated monomials cancel mod 2
        end
    end
    return C
end
