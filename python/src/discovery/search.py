"""Blind generator-ansatz search over BB codes (catalog-blind, FOM-driven).

Reproduces the paper's search FRAMEWORK without its answers (blind_discovery_policy):
seeds are NAIVE random polynomials — never the paper's discovered (A,B). The only signal
is the kernel fitness (FOM = k d^2 / n via the evaluation cascade). A MAP-Elites-lite
archive bins candidates by k so the search illuminates the rate--distance frontier itself
(the paper's central empirical finding), rather than being told it. The GA mutates exponents
of elites — this is the paper's acknowledged non-LLM baseline (Sec. VI.F GA / GA-G arms),
which needs no openevolve/LLM. Paper anchor: arXiv:2606.02418 sec IV.A. R2.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from .evaluation import screen_k_css, evaluate_css, evaluate_pbb
from ..codes.pbb_codes import PBBCode


def random_polynomial(l: int, m: int, weight: int, rng: random.Random) -> list[tuple[int, int]]:
    """A naive random polynomial: `weight` distinct monomials x^a y^b, a in Z_l, b in Z_m.

    No paper structure injected — uniform over the monomial lattice (blind seed).
    """
    all_mons = [(a, b) for a in range(l) for b in range(m)]
    return sorted(rng.sample(all_mons, weight))


def mutate_polynomial(terms, l: int, m: int, rng: random.Random) -> list[tuple[int, int]]:
    """Mutate one monomial of a polynomial: shift an exponent or resample a term (blind operator)."""
    terms = list(terms)
    i = rng.randrange(len(terms))
    a, b = terms[i]
    op = rng.random()
    if op < 0.5:                                   # shift one exponent by +/-1
        if rng.random() < 0.5:
            a = (a + rng.choice((-1, 1))) % l
        else:
            b = (b + rng.choice((-1, 1))) % m
    else:                                          # resample the monomial entirely
        a, b = rng.randrange(l), rng.randrange(m)
    cand = set(terms)
    cand.discard(terms[i])
    cand.add((a, b))
    out = sorted(cand)
    return out if len(out) == len(terms) else terms  # reject collision (keep weight)


@dataclass
class Archive:
    """MAP-Elites-lite: best-FOM elite per (lattice, k) bin. Illuminates the k vs d frontier."""
    cells: dict = field(default_factory=dict)

    def consider(self, result: dict) -> bool:
        """Insert result if it beats the current FOM elite of its (l,m,k) cell. Returns True if it did."""
        if not result.get("d") or result["fom"] <= 0:
            return False
        key = (result["l"], result["m"], result["k"])
        cur = self.cells.get(key)
        if cur is None or result["fom"] > cur["fom"]:
            self.cells[key] = result
            return True
        return False

    def elites(self):
        """All cell elites, sorted by FOM descending (the discovered rate--distance frontier)."""
        return sorted(self.cells.values(), key=lambda r: r["fom"], reverse=True)


def verify_elites_milp(elites, time_limit=10.0, max_logicals=None, log=None):
    """Stage-3: recompute EXACT MILP distance for each archive elite (tightens BP-OSD bounds).

    Returns the elites with d/exact/fom updated from MILP. Mirrors the paper's post-hoc MILP
    verification of the codes that survive the BP-OSD-driven evolutionary loop.
    """
    from ..codes.bb_codes import BBCode
    from ..distance.distance_milp import css_distance_milp
    from ..codes.metrics import fom
    say = log if log else (lambda *_: None)
    out = []
    for e in elites:
        code = BBCode(e["l"], e["m"], e["A"], e["B"])
        d = css_distance_milp(code, time_limit=time_limit, max_logicals=max_logicals)
        ev = dict(e)
        if d["d"] is not None:
            ev["d"], ev["exact"] = d["d"], d["exact"]
            ev["fom"] = fom(code.n, ev["k"], d["d"])
            say(f"  Stage-3 MILP [[{code.n},{ev['k']},{d['d']}]] exact={d['exact']} FOM={ev['fom']:.2f}")
        out.append(ev)
    out.sort(key=lambda r: r["fom"], reverse=True)
    return out


def _elite_canonical_hash(elite: dict) -> str:
    """Structural canonical hash of a CSS BB elite (for in-loop distinct-code counting).

    Pure structural canonicalization — no catalog input (blind-safe). Prefers the exact
    colored-Tanner-graph BLISS hash over the code's H_X/H_Z; falls back to the lattice-symmetry
    polynomial signature when python-igraph is absent. Codes that are permutation-equivalent
    (BLISS) — or, in the fallback, lattice-symmetry equivalent — share a hash.
    """
    from ..structure.dedup import bliss_canonical_hash, canonical_poly_signature
    from ..codes.bb_codes import BBCode
    code = BBCode(elite["l"], elite["m"], elite["A"], elite["B"])
    try:
        return bliss_canonical_hash(code.HX, code.HZ)
    except ImportError:                                 # python-igraph not installed
        sig = canonical_poly_signature(code.l, code.m, code.A_terms, code.B_terms)
        return repr((code.l, code.m, sig))


def blind_search_css(lattices, *, n_random=400, generations=0, distance_budget=8,
                     weight=3, weights=None, dedup=False, time_limit=3.0, max_logicals=None,
                     seed=0, log=None, distance_method="milp", trust_high=2.0) -> dict:
    """Run a blind CSS BB search over the given lattices [(l,m), ...].

    Phase 1: sample n_random naive trinomial pairs per lattice, Stage-1 screen k, take the
    top `distance_budget` by k, Stage-2 evaluate distance -> FOM, populate the archive.
    Phase 2 (optional): `generations` of FOM-hill-climbing GA mutating archive elites.

    `weights`: when None (default) every A,B is the fixed `weight` (today's behavior); when a
    (wmin, wmax) sequence, draw wA, wB uniformly from range(wmin, wmax+1) per seed (blind-safe
    check-weight variation — only widens reach, injects no catalog poly) and record the realized
    `stab_weight` (= |A|+|B|) on each elite. `dedup`: when True (default False), canonicalize each
    elite's Tanner graph and add `n_distinct` (the structural distinct-code count) to the summary.
    Returns {archive_elites, evaluated, n_evaluated, n_distance_evals} (+ n_distinct if dedup).
    NO paper data consulted.
    """
    rng = random.Random(seed)
    arch = Archive()
    n_eval = n_dist = 0
    evaluated: list[dict] = []                          # every distance-evaluated representation
    say = log if log else (lambda *_: None)
    wlo, whi = (weights[0], weights[1]) if weights is not None else (None, None)

    def _draw_weight() -> int:                          # per-seed weight (blind: uniform over range)
        return weight if weights is None else rng.randint(wlo, whi)

    for (l, m) in lattices:
        # Phase 1: cheap k-screen of random trinomial pairs.
        screened = []
        for _ in range(n_random):
            A = random_polynomial(l, m, _draw_weight(), rng)
            B = random_polynomial(l, m, _draw_weight(), rng)
            n_eval += 1
            k = screen_k_css(l, m, A, B)
            if k > 0:
                screened.append((k, A, B))
        # k-DIVERSE selection (not top-by-k): a spread across distinct k values, so low-k
        # high-distance codes are evaluated alongside high-k (often d=2 trap) codes. FOM decides.
        by_k: dict[int, list] = {}
        seen = set()
        for (k, A, B) in screened:
            sig = (tuple(map(tuple, A)), tuple(map(tuple, B)))
            if sig in seen:
                continue
            seen.add(sig)
            by_k.setdefault(k, []).append((A, B))
        selection = []
        ks = sorted(by_k)                              # round-robin one per k-value until budget filled
        ri = 0
        while len(selection) < distance_budget and any(by_k.values()):
            k = ks[ri % len(ks)]
            if by_k[k]:
                A, B = by_k[k].pop(0)
                selection.append((k, A, B))
            ri += 1
            if ri > len(ks) * (distance_budget + 2):
                break
        for (k, A, B) in selection:
            res = evaluate_css(l, m, A, B, distance_method=distance_method,
                               time_limit=time_limit, max_logicals=max_logicals)
            n_dist += 1
            # trust filter (only for BP-OSD upper bounds): discard d/sqrt(n) >= trust_high so
            # overestimated d=2 traps cannot fake a high FOM (paper Sec V.D).
            trusted = (distance_method != "bposd") or (res.get("d_over_sqrt_n") or 0) < trust_high
            if res.get("d") and trusted:
                evaluated.append(res)
                if arch.consider(res):
                    say(f"  [{l},{m}] discovered [[{res['n']},{res['k']},{res['d']}]] "
                        f"FOM={res['fom']:.2f} exact={res['exact']}")

    # Phase 2: GA hill-climbing on elites (FOM fitness).
    for g in range(generations):
        for elite in arch.elites()[:max(1, distance_budget // 2)]:
            l, m = elite["l"], elite["m"]
            A = mutate_polynomial(elite["A"], l, m, rng)
            B = mutate_polynomial(elite["B"], l, m, rng)
            if screen_k_css(l, m, A, B) == 0:
                continue
            res = evaluate_css(l, m, A, B, distance_method=distance_method,
                               time_limit=time_limit, max_logicals=max_logicals)
            n_dist += 1
            trusted = (distance_method != "bposd") or (res.get("d_over_sqrt_n") or 0) < trust_high
            if res.get("d") and trusted:
                evaluated.append(res)
                if arch.consider(res):
                    say(f"  gen{g+1} [{l},{m}] improved [[{res['n']},{res['k']},{res['d']}]] "
                        f"FOM={res['fom']:.2f} exact={res['exact']}")

    out = {"archive_elites": arch.elites(), "evaluated": evaluated,
           "n_evaluated": n_eval, "n_distance_evals": n_dist}
    if dedup:                                           # structural distinct-code count over elites
        out["n_distinct"] = len({_elite_canonical_hash(e) for e in out["archive_elites"]})
    return out


def random_commuting_pbb(l, m, rng, base_weight=3, pert_weights=(1, 2, 3), tries=40):
    """A naive random PBB 4-tuple (A,B,C,D) that satisfies the commutativity constraint.

    A,B are weight-`base_weight` (the BB-construction definition); C,D weights are drawn from
    `pert_weights` (generic perturbation — NOT the paper's discovered |C|=|D|=2 optimum).
    Returns (A,B,C,D) or None if no commuting tuple found in `tries` (most tuples don't commute).
    """
    for _ in range(tries):
        A = random_polynomial(l, m, base_weight, rng)
        B = random_polynomial(l, m, base_weight, rng)
        C = random_polynomial(l, m, rng.choice(pert_weights), rng)
        D = random_polynomial(l, m, rng.choice(pert_weights), rng)
        try:
            PBBCode(l, m, A, B, C, D)                 # raises unless A C^T + B D^T symmetric
            return A, B, C, D
        except ValueError:
            continue
    return None


def _pbb_elite_signature(elite: dict) -> tuple:
    """Structural signature of a PBB elite for distinct-code counting (blind-safe).

    The PBB symplectic stabilizer matrices have no CSS H_X/H_Z, so the BLISS colored-Tanner
    hash does not apply; we canonicalize the full (A,B,C,D) 4-tuple under the BB lattice-symmetry
    group (x->x^a, y->y^b, x<->y) instead. Pure structural canonicalization — no catalog input.
    SOUND for that group (a signature difference certifies distinctness; a conservative count).
    """
    from ..structure.dedup import _units
    l, m = elite["l"], elite["m"]
    polys = [{(i % l, j % m) for (i, j) in elite[key]} for key in ("A", "B", "C", "D")]
    best = None
    for a in _units(l):
        for b in _units(m):
            forms = [tuple(frozenset(((a * i) % l, (b * j) % m) for (i, j) in P) for P in polys)]
            if l == m:                                  # x<->y swap (only a symmetry when l=m)
                forms.append(tuple(frozenset((j, i) for (i, j) in P) for P in forms[0]))
            for form in forms:
                key = tuple(tuple(sorted(P)) for P in form)
                if best is None or key < best:
                    best = key
    return (l, m, best)


def blind_search_pbb(lattices, *, n_random=600, distance_budget=6, generations=0,
                     time_limit=4.0, max_logicals=None, seed=0, log=None, dedup=False) -> dict:
    """Blind non-CSS PBB search over the given lattices. Catalog-blind; FOM-driven.

    Phase 1: sample commuting 4-tuples, screen k, take a k-diverse set, symplectic-distance
    them -> FOM, archive. Phase 2: optional GA mutating elite (A,B,C,D). Returns archive + counts.

    `dedup`: when True (default False) add `n_distinct` to the summary — the count of elites
    distinct under the BB lattice-symmetry group applied to the (A,B,C,D) 4-tuple (see
    `_pbb_elite_signature`; PBB has no CSS H_X/H_Z, so the BLISS Tanner hash does not apply here).
    """
    rng = random.Random(seed)
    arch = Archive()
    n_eval = n_dist = n_commute = 0
    say = log if log else (lambda *_: None)

    for (l, m) in lattices:
        screened = []
        for _ in range(n_random):
            n_eval += 1
            tup = random_commuting_pbb(l, m, rng)
            if tup is None:
                continue
            n_commute += 1
            A, B, C, D = tup
            try:
                k = PBBCode(l, m, A, B, C, D).k
            except ValueError:
                continue
            if k > 0:
                screened.append((k, A, B, C, D))
        by_k: dict[int, list] = {}
        for (k, A, B, C, D) in screened:
            by_k.setdefault(k, []).append((A, B, C, D))
        selection, ks, ri = [], sorted(by_k), 0
        while len(selection) < distance_budget and any(by_k.values()):
            k = ks[ri % len(ks)]
            if by_k[k]:
                selection.append((k, *by_k[k].pop(0)))
            ri += 1
            if ri > len(ks) * (distance_budget + 2):
                break
        for (k, A, B, C, D) in selection:
            res = evaluate_pbb(l, m, A, B, C, D, time_limit=time_limit, max_logicals=max_logicals)
            n_dist += 1
            if res.get("valid") and arch.consider({**res, "A": A, "B": B, "C": C, "D": D}):
                say(f"  [{l},{m}] discovered non-CSS [[{res['n']},{res['k']},{res['d']}]] "
                    f"FOM={res['fom']:.2f} exact={res['exact']} mixed={res['non_css']}")

    out = {"archive_elites": arch.elites(), "n_evaluated": n_eval,
           "n_commuting": n_commute, "n_distance_evals": n_dist}
    if dedup:                                           # structural distinct-code count over elites
        out["n_distinct"] = len({_pbb_elite_signature(e) for e in out["archive_elites"]})
    return out
