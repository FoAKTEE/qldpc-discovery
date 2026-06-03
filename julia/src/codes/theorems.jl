# Numeric witnesses for the two paper theorems. Port of qcode_discovery/codes/theorems.py.

"""thm:ab_d2 — every BB code with A = B and k > 0 has distance exactly 2.
Returns `(l, m, k, d, claim_d2)`; `claim_d2` is true iff k>0 and the (enumerated) distance is 2."""
function verify_ab_d2(l::Int, m::Int, A::AbstractString; max_weight::Int=2)
    c = BBCode(l, m, A, A)              # A = B
    k = css_k(c)
    d = css_distance_enum(c; max_weight=max_weight).d
    return (l=l, m=m, k=k, d=d, claim_d2=(k > 0 && d == 2))
end

"""lem:crt_k — for 3|l, 3|m, c=l/3, the code A(y)=1+y+y^2, B(x)=1+x^c+x^{2c} encodes k = 8l/3.
Returns `(l, m, n, k, expected, match)`."""
function verify_crt_k(l::Int, m::Int)
    (l % 3 == 0 && m % 3 == 0) || error("verify_crt_k requires 3|l and 3|m")
    cc = l ÷ 3
    A = "1+y+y^2"
    B = "1+x^$(cc)+x^$(2 * cc)"
    code = BBCode(l, m, A, B)
    k = css_k(code)
    expected = 8 * l ÷ 3
    return (l=l, m=m, n=code.n, k=k, expected=expected, match=(k == expected))
end
