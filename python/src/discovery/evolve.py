"""Generator-ansatz program evolution (the paper's core representation).

arXiv:2606.02418 evolves a GENERATOR ANSATZ -- a program G(l,m) -> {(A_i,B_i)} that emits
candidate codes for ANY lattice from an algebraic pattern (so one mutation like "use x^{l/3}"
generalizes across all block lengths). This differs from `search.py`, which mutates polynomial
tuples directly. Here an ansatz is a set of parameterized algebraic STRATEGIES; mutation operators
edit the program (GA-G, the paper's non-LLM baseline, runnable now). The LLM mutation operator
(the paper's headline) is an interface gated on API credentials + openevolve/litellm. R2.
"""
from __future__ import annotations

import ast
import operator as _op
import random
from dataclasses import dataclass, field

from .evaluation import evaluate_css

_SAFE_OPS = {ast.Add: _op.add, ast.Sub: _op.sub, ast.Mult: _op.mul,
             ast.FloorDiv: _op.floordiv, ast.Mod: _op.mod, ast.USub: _op.neg}


def _safe_expr(expr, l: int, m: int) -> int:
    """Evaluate an exponent expression over {l, m, ints, + - * // %} safely (no arbitrary code).

    Lets the LLM mutation operator propose lattice-scaling patterns like 'l//3', '2*m//3'."""
    if isinstance(expr, int):
        return expr
    node = ast.parse(str(expr), mode="eval").body

    def ev(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, int):
            return n.value
        if isinstance(n, ast.Name) and n.id in ("l", "m"):
            return {"l": l, "m": m}[n.id]
        if isinstance(n, ast.BinOp) and type(n.op) in _SAFE_OPS:
            return _SAFE_OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _SAFE_OPS:
            return _SAFE_OPS[type(n.op)](ev(n.operand))
        raise ValueError(f"unsafe exponent expr: {ast.dump(n)}")
    return ev(node)


@dataclass
class GeneratorAnsatz:
    """A program: a list of parameterized algebraic strategies emitting (A,B) for any (l,m)."""
    strategies: list = field(default_factory=list)

    def generate(self, l: int, m: int) -> list:
        """Emit candidate (A_terms, B_terms) pairs for lattice (l,m) from each strategy."""
        out = []
        for s in self.strategies:
            try:
                out.append(_emit(s, l, m))
            except Exception:
                continue
        return out


def _emit(strategy: dict, l: int, m: int):
    """One strategy -> one (A_terms, B_terms). Exponents are scaled to the lattice (multi-lattice)."""
    k, p = strategy["kind"], strategy["params"]
    if k == "xyswap":                      # A = x^a + y^b + y^c ; B = y^d + x^e + x^f
        A = [(p["a"] % l, 0), (0, p["b"] % m), (0, p["c"] % m)]
        B = [(0, p["d"] % m), (p["e"] % l, 0), (p["f"] % l, 0)]
    elif k == "univariate":                # A = 1 + y + y^2 ; B = 1 + x^j + x^{2j}, j scaled to l
        j = max(1, (p["j_num"] * l) // p["j_den"]) % l or 1
        A = [(0, 0), (0, 1 % m), (0, 2 % m)]
        B = [(0, 0), (j, 0), ((2 * j) % l, 0)]
    elif k == "custom":                    # LLM-proposed: A,B as monomials with exponents expr(l,m)
        A = [(_safe_expr(a, l, m) % l, _safe_expr(b, l, m) % m) for (a, b) in p["A"]]
        B = [(_safe_expr(a, l, m) % l, _safe_expr(b, l, m) % m) for (a, b) in p["B"]]
    else:
        raise ValueError(f"unknown strategy {k}")
    return sorted(set(A)), sorted(set(B))


def random_ansatz(rng: random.Random) -> GeneratorAnsatz:
    """A naive random ansatz (1-2 strategies) — NOT seeded from any paper code (blind)."""
    strategies = [{"kind": "xyswap",
                   "params": {x: rng.randrange(1, 7) for x in "abcdef"}}]
    if rng.random() < 0.5:
        strategies.append({"kind": "univariate",
                           "params": {"j_num": rng.randrange(1, 3), "j_den": 3}})
    return GeneratorAnsatz(strategies)


def mutate_ansatz(ansatz: GeneratorAnsatz, rng: random.Random) -> GeneratorAnsatz:
    """GA-G program mutation: perturb a strategy's exponent params, or add/remove a strategy."""
    strat = [dict(kind=s["kind"], params=dict(s["params"])) for s in ansatz.strategies]
    roll = rng.random()
    if roll < 0.7 and strat:                                   # perturb a param
        s = strat[rng.randrange(len(strat))]
        key = rng.choice(list(s["params"]))
        s["params"][key] = max(1, s["params"][key] + rng.choice((-1, 1)))
    elif roll < 0.85:                                          # add a strategy
        strat.append(random_ansatz(rng).strategies[0])
    elif len(strat) > 1:                                       # remove a strategy
        strat.pop(rng.randrange(len(strat)))
    return GeneratorAnsatz(strat)


def ansatz_fitness(ansatz: GeneratorAnsatz, lattices, time_limit=2.0, max_logicals=6) -> dict:
    """Total FOM of the codes an ansatz generates across lattices (the paper's combined score)."""
    codes, total = [], 0.0
    for (l, m) in lattices:
        for (A, B) in ansatz.generate(l, m):
            r = evaluate_css(l, m, A, B, distance_method="bposd", time_limit=time_limit,
                             max_logicals=max_logicals)
            if r.get("d") and r.get("trusted"):
                codes.append(r)
                total += r["fom"]
    return {"score": total, "codes": codes, "n_lattices_with_code": len({(c["l"], c["m"]) for c in codes})}


def evolve_ansaetze(lattices, *, generations=4, pop=6, time_limit=1.0, max_logicals=6,
                    seed=0, log=None) -> dict:
    """GA-G program evolution: evolve generator ANSATZE (not tuples) by total cross-lattice FOM.

    Blind (random seeds). Returns the best ansatz + its generated codes. The LLM mutation operator
    is the paper's method; swap it in via `mutate=` once credentials are available (see llm_mutation).

    CAVEAT (faithful to the paper's Campaigns 1-3): the fitness here uses BP-OSD distance, which
    OVERESTIMATES d for high-k codes, so the FOM signal is inflated (a high-k code can post a huge
    FOM from an overestimated d). The reported codes are BP-OSD UPPER BOUNDS, not certified — they
    MUST be passed through Stage-3 MILP (`search.verify_elites_milp`) before being treated as
    discoveries, exactly as the paper added MILP-in-the-loop for Campaigns 4-5.
    """
    rng = random.Random(seed)
    say = log if log else (lambda *_: None)
    population = [(a := random_ansatz(rng), ansatz_fitness(a, lattices, time_limit, max_logicals))
                  for _ in range(pop)]
    for g in range(generations):
        population.sort(key=lambda t: t[1]["score"], reverse=True)
        best = population[0]
        say(f"  gen{g}: best score={best[1]['score']:.2f} over {best[1]['n_lattices_with_code']} lattices")
        survivors = population[: max(1, pop // 2)]
        children = []
        for (a, _) in survivors:
            child = mutate_ansatz(a, rng)
            children.append((child, ansatz_fitness(child, lattices, time_limit, max_logicals)))
        population = survivors + children
    population.sort(key=lambda t: t[1]["score"], reverse=True)
    return {"best_ansatz": population[0][0], "best": population[0][1]}


def llm_mutation(ansatz: GeneratorAnsatz, feedback: str, model: str = "gpt-5.2"):
    """LLM mutation operator (the paper's headline). [FUTURE: needs litellm + funded API key].

    The paper drives mutation by prompting an LLM with the ansatz program + domain knowledge +
    evaluation feedback, parsing the returned code diff. Obstacle: requires litellm + a funded API
    key (the paper spent ~US$400) + openevolve; not runnable here without credentials. GA-G
    (`mutate_ansatz`) is the runnable non-LLM baseline. R2.
    """
    raise NotImplementedError(
        "[FUTURE iter N+] LLM-guided mutation needs litellm + a funded API key (openevolve). "
        "Provide credentials to run the paper's headline LLM-guided campaigns; GA-G is the baseline.")
