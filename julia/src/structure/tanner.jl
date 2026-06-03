# Tanner-graph structure: connectivity and decomposability (direct-sum detection).
# Port of qcode_discovery/structure/tanner.py.
#
# A code whose combined (H_X, H_Z) Tanner graph disconnects into independent
# components is a DIRECT SUM of sub-codes and offers no error-correction advantage
# over them. Union-find over the qubit set, pure Julia, no external graph dependency.

"""Disjoint-set with path halving; used to count Tanner-graph qubit components."""
mutable struct _UnionFind
    parent::Vector{Int}
end
_UnionFind(size::Int) = _UnionFind(collect(1:size))

"""Representative of `a`'s set (with path halving)."""
function _uf_find(uf::_UnionFind, a::Int)
    @inbounds while uf.parent[a] != a
        uf.parent[a] = uf.parent[uf.parent[a]]
        a = uf.parent[a]
    end
    return a
end

"""Merge the sets containing `a` and `b`."""
function _uf_union!(uf::_UnionFind, a::Int, b::Int)
    ra, rb = _uf_find(uf, a), _uf_find(uf, b)
    if ra != rb
        @inbounds uf.parent[ra] = rb
    end
    return nothing
end

"""
    qubit_components(HX, HZ)::Int

Number of connected components on the qubit set of the combined Tanner graph.
Qubits and check-vertices are nodes; an edge joins a check to each qubit in its
support. Two qubits are in the same component iff a path of shared checks links
them. Returns the count of distinct qubit components.
"""
function qubit_components(HX::AbstractMatrix, HZ::AbstractMatrix)
    HXf = as_f2(HX)
    HZf = as_f2(HZ)
    n = size(HXf, 2)
    checks = vcat(HXf, HZf)
    uf = _UnionFind(n)
    @inbounds for r in 1:size(checks, 1)
        support = findall(!iszero, @view checks[r, :])
        isempty(support) && continue
        first = support[1]
        for k in 2:length(support)
            _uf_union!(uf, first, support[k])
        end
    end
    roots = Set{Int}()
    for q in 1:n
        push!(roots, _uf_find(uf, q))
    end
    return length(roots)
end

"""
    is_decomposable(code)::Bool

True iff the code's Tanner graph splits into >= 2 qubit components (direct sum).
"""
is_decomposable(code) = qubit_components(code.HX, code.HZ) > 1
