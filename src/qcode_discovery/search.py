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

from .evaluation import screen_k_css, evaluate_css


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


def blind_search_css(lattices, *, n_random=400, generations=0, distance_budget=8,
                     weight=3, time_limit=3.0, max_logicals=None, seed=0, log=None) -> dict:
    """Run a blind CSS BB search over the given lattices [(l,m), ...].

    Phase 1: sample n_random naive trinomial pairs per lattice, Stage-1 screen k, take the
    top `distance_budget` by k, Stage-2 evaluate distance -> FOM, populate the archive.
    Phase 2 (optional): `generations` of FOM-hill-climbing GA mutating archive elites.
    Returns {archive_elites, n_evaluated, n_distance_evals}. NO paper data consulted.
    """
    rng = random.Random(seed)
    arch = Archive()
    n_eval = n_dist = 0
    say = log if log else (lambda *_: None)

    for (l, m) in lattices:
        # Phase 1: cheap k-screen of random trinomial pairs.
        screened = []
        for _ in range(n_random):
            A = random_polynomial(l, m, weight, rng)
            B = random_polynomial(l, m, weight, rng)
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
            res = evaluate_css(l, m, A, B, time_limit=time_limit, max_logicals=max_logicals)
            n_dist += 1
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
            res = evaluate_css(l, m, A, B, time_limit=time_limit, max_logicals=max_logicals)
            n_dist += 1
            if arch.consider(res):
                say(f"  gen{g+1} [{l},{m}] improved [[{res['n']},{res['k']},{res['d']}]] "
                    f"FOM={res['fom']:.2f} exact={res['exact']}")

    return {"archive_elites": arch.elites(), "n_evaluated": n_eval, "n_distance_evals": n_dist}
