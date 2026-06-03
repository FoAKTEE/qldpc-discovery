# Deduplication of CSS codes by colored-Tanner-graph permutation equivalence. Pure Julia.
# Port of qcode_discovery/structure/dedup.py :: bliss_canonical_hash.
#
# The paper (arXiv:2606.02418 sec VI.A) dedups codes by the canonical form of the colored
# Tanner graph via BLISS (python-igraph). We replace BLISS with a native
# individualization-refinement (IR) canonical-labeling engine — the same family of algorithm
# BLISS/nauty implement — so this file has NO C/C++ dependency.
#
# Graph model (identical to dedup.py):
#   vertices = qubits (color 0) ++ X-checks (color 1) ++ Z-checks (color 2)
#   edges    = check -> qubit whenever that check touches that qubit (undirected here)
# Two CSS codes are permutation-equivalent (a qubit relabeling preserving X/Z-check roles)
# iff their canonical hashes match. SOUND and COMPLETE for that equivalence — equal hash <=>
# isomorphic colored graph; different hash <=> provably inequivalent.

import SHA

# ---------------------------------------------------------------------------
# Colored graph: adjacency as sorted neighbor lists + an initial color per vertex.
# ---------------------------------------------------------------------------

"""Build the colored Tanner graph of a CSS code from `HX`, `HZ` (Matrix{UInt8}, 0/1 entries).

Returns `(adj, colors)` where `adj[v]` is the sorted neighbor list of vertex `v` (1-based) and
`colors[v]` is its initial color (0 = qubit, 1 = X-check, 2 = Z-check). Mirrors the vertex and
color layout of `dedup.py`."""
function _tanner_graph(HX::AbstractMatrix, HZ::AbstractMatrix)
    HXb = as_f2(HX)
    HZb = as_f2(HZ)
    rx, n = size(HXb)
    rz, nz = size(HZb)
    @assert n == nz "HX and HZ must have the same number of qubits (columns)"
    N = n + rx + rz
    colors = Vector{Int}(undef, N)
    @inbounds for v in 1:n
        colors[v] = 0
    end
    @inbounds for v in (n + 1):(n + rx)
        colors[v] = 1
    end
    @inbounds for v in (n + rx + 1):N
        colors[v] = 2
    end
    adj = [Int[] for _ in 1:N]
    @inbounds for c in 1:rx
        cv = n + c
        for q in 1:n
            if HXb[c, q] == 0x1
                push!(adj[cv], q)
                push!(adj[q], cv)
            end
        end
    end
    @inbounds for c in 1:rz
        cv = n + rx + c
        for q in 1:n
            if HZb[c, q] == 0x1
                push!(adj[cv], q)
                push!(adj[q], cv)
            end
        end
    end
    for v in 1:N
        sort!(adj[v])
    end
    return adj, colors
end

# ---------------------------------------------------------------------------
# Ordered partition (the "color" structure during refinement).
#
# A partition is an ordered list of cells; each cell is a Vector{Int} of vertices.
# `cellof[v]` gives the index of the cell containing v. The order of cells is the canonical
# color order; vertices within a cell are interchangeable until further refined.
# ---------------------------------------------------------------------------

"""Equitable refinement of an ordered partition (1-dimensional Weisfeiler-Leman / color
refinement). Splits each cell by the multiset of (target-cell -> count) edges, breaking ties by
the canonical order of cells. The result is the coarsest equitable partition refining the
input. Returns a new vector of cells (each a sorted Vector{Int})."""
function _refine(adj::Vector{Vector{Int}}, cells::Vector{Vector{Int}})
    cells = [copy(c) for c in cells]
    N = length(adj)
    cellof = Vector{Int}(undef, N)
    for (ci, cell) in enumerate(cells)
        for v in cell
            cellof[v] = ci
        end
    end
    changed = true
    while changed
        changed = false
        newcells = Vector{Vector{Int}}()
        for cell in cells
            if length(cell) == 1
                push!(newcells, cell)
                continue
            end
            # Signature of each vertex: counts of neighbors per current cell index.
            # Represented as a sorted vector of (cellindex, count) pairs for stable comparison.
            sigs = Dict{Int,Vector{Tuple{Int,Int}}}()
            for v in cell
                counts = Dict{Int,Int}()
                for w in adj[v]
                    cw = cellof[w]
                    counts[cw] = get(counts, cw, 0) + 1
                end
                sigs[v] = sort!([(k, val) for (k, val) in counts])
            end
            # Group vertices by identical signature, ordering groups by signature (lexicographic).
            distinct = unique(values(sigs))
            if length(distinct) == 1
                push!(newcells, cell)
                continue
            end
            changed = true
            order = sort(distinct)
            for sg in order
                group = sort!([v for v in cell if sigs[v] == sg])
                push!(newcells, group)
            end
        end
        if changed
            cells = newcells
            for (ci, cell) in enumerate(cells)
                for v in cell
                    cellof[v] = ci
                end
            end
        else
            cells = newcells
        end
    end
    return cells
end

"""Initial ordered partition from the vertex colors: one cell per color, in increasing color
order, vertices sorted within each cell."""
function _initial_partition(colors::Vector{Int})
    N = length(colors)
    cols = sort(unique(colors))
    cells = Vector{Vector{Int}}()
    for col in cols
        push!(cells, sort!([v for v in 1:N if colors[v] == col]))
    end
    return cells
end

# ---------------------------------------------------------------------------
# Individualization-refinement canonical labeling.
#
# Discrete partition (every cell a singleton) gives a vertex ordering; we want the lexicographically
# minimal certificate over all such orderings reachable by individualizing vertices in the first
# non-singleton cell and re-refining. We explore the full IR tree (with the equitable refinement
# pruning most branches) and keep the best (minimal) certificate. Exact / complete.
# ---------------------------------------------------------------------------

"""Certificate of a *discrete* ordered partition: the adjacency, rendered in the canonical vertex
order given by the partition. `pos[v]` = canonical position of vertex v (1..N). The certificate is
the (initial-color sequence, sorted canonical edge list) — exactly the `sig` of `dedup.py`."""
function _certificate(adj::Vector{Vector{Int}}, colors::Vector{Int}, cells::Vector{Vector{Int}})
    N = length(adj)
    pos = Vector{Int}(undef, N)
    for (i, cell) in enumerate(cells)
        # discrete: each cell is a singleton
        pos[cell[1]] = i
    end
    newcolors = Vector{Int}(undef, N)
    for v in 1:N
        newcolors[pos[v]] = colors[v]
    end
    edges = Vector{Tuple{Int,Int}}()
    for v in 1:N
        pv = pos[v]
        for w in adj[v]
            if v < w
                a, b = pv, pos[w]
                push!(edges, a < b ? (a, b) : (b, a))
            end
        end
    end
    sort!(edges)
    return (newcolors, edges)
end

"""Compare two certificates `(colors, edges)` lexicographically; returns true if `a < b`."""
function _cert_less(a, b)
    a[1] != b[1] && return a[1] < b[1]
    return a[2] < b[2]
end

"""Find the first non-singleton cell index (the target cell to individualize), or 0 if discrete."""
function _target_cell(cells::Vector{Vector{Int}})
    for (i, cell) in enumerate(cells)
        length(cell) > 1 && return i
    end
    return 0
end

"""Canonical certificate of the colored graph via individualization-refinement.

Explores the IR search tree: refine to an equitable partition; if discrete, record the
certificate; otherwise pick the first non-singleton cell and branch on individualizing each of
its vertices, recursing. The minimal certificate over all leaves is canonical and invariant under
color-respecting isomorphism (BLISS-style). Complete and sound."""
function _canonical_certificate(adj::Vector{Vector{Int}}, colors::Vector{Int})
    cells0 = _refine(adj, _initial_partition(colors))
    best = Ref{Any}(nothing)

    function descend(cells)
        ti = _target_cell(cells)
        if ti == 0
            cert = _certificate(adj, colors, cells)
            if best[] === nothing || _cert_less(cert, best[])
                best[] = cert
            end
            return
        end
        target = cells[ti]
        # Branch: individualize each vertex of the target cell (place it in its own cell, first).
        for v in target
            rest = sort!([u for u in target if u != v])
            newcells = Vector{Vector{Int}}()
            for (i, cell) in enumerate(cells)
                if i == ti
                    push!(newcells, [v])
                    push!(newcells, rest)
                else
                    push!(newcells, copy(cell))
                end
            end
            refined = _refine(adj, newcells)
            descend(refined)
        end
    end

    descend(cells0)
    return best[]
end

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

"""Exact colored-Tanner-graph canonical hash of a CSS code (pure-Julia replacement for the
paper's igraph/BLISS hash). `HX`, `HZ` are Matrix{UInt8} with 0/1 entries.

Two CSS codes are permutation-equivalent — a qubit relabeling that preserves the X-check and
Z-check roles — iff their `canonical_hash` values are equal. SOUND and COMPLETE for that
equivalence: equal hash <=> isomorphic colored Tanner graph, different hash <=> inequivalent.

Hash bytes need NOT match the Python igraph hash (different serialization), but the equal/unequal
PATTERN across codes is identical."""
function canonical_hash(HX::AbstractMatrix, HZ::AbstractMatrix)::String
    adj, colors = _tanner_graph(HX, HZ)
    cert = _canonical_certificate(adj, colors)
    newcolors, edges = cert
    # Serialize the certificate deterministically, then SHA-256 and truncate to 32 hex chars
    # (matching the digest length of dedup.py).
    io = IOBuffer()
    print(io, "colors:")
    for c in newcolors
        print(io, c, ",")
    end
    print(io, "|edges:")
    for (a, b) in edges
        print(io, "(", a, ",", b, ")")
    end
    s = String(take!(io))
    return bytes2hex(SHA.sha256(s))[1:32]
end

"""Canonical hash of a `BBCode` (convenience wrapper over its `HX`/`HZ`)."""
canonical_hash(c::BBCode)::String = canonical_hash(c.HX, c.HZ)

"""Group CSS codes (objects with `.HX`/`.HZ`) by exact permutation equivalence.

Returns a `NamedTuple` `(representatives, classes, n_distinct)`: `classes` maps each canonical
hash to the list of 1-based indices in that equivalence class; `representatives` is the sorted
list of the first index of each class; `n_distinct` is the exact distinct-code count. Mirrors
`dedup_bliss` in dedup.py."""
function dedup_bliss(codes)
    classes = Dict{String,Vector{Int}}()
    for (i, c) in enumerate(codes)
        h = canonical_hash(c.HX, c.HZ)
        push!(get!(classes, h, Int[]), i)
    end
    reps = sort!([minimum(idxs) for idxs in values(classes)])
    return (representatives = reps, classes = classes, n_distinct = length(classes))
end
