# Blind-Zero Findings: Bivariate Bicycle (BB) CSS Codes

**Discovered cold.** Everything below was found from the mathematics and an
own-built search only. No reference paper, catalog, or list of known codes was
consulted; no specific known BB code or `[[n,k,d]]` result was recalled from
memory. The reference PDFs present in the repo were deliberately **not opened**.

## Setup (as implemented in `src/qcode/`)

- Ring `R = F2[x,y]/(x^l-1, y^m-1)`; monomial `x^a y^b -> kron(S_l^a, S_m^b)`,
  `S_n` = `n x n` cyclic shift. A polynomial is the mod-2 sum of its monomials.
- `H_X = [A | B]`, `H_Z = [B^T | A^T]`; `H_X H_Z^T = 0 (mod 2)` holds because the
  monomial matrices commute (verified for 200 random codes, all four lattices).
- `n = 2 l m`; `k = n - rank_F2(H_X) - rank_F2(H_Z)`.
- Distance `d` = min Hamming weight of a nontrivial logical (min over X- and
  Z-type). `FOM = k d^2 / n`.

## How distance is verified (two independent methods, cross-checked)

1. **Exact low-weight enumeration** (`distance_lowweight` scalar reference and
   `distance_lowweight_vec` vectorised). Enumerates *all* weight-`w` supports for
   `w = 1, 2, ...` and tests `H_perp x = 0` plus anticommutation with a dual
   logical. Because it scans from `w=1` upward, the first hit IS the exact
   distance; if nothing is found up to `w_max`, then `d > w_max` is a **proven
   lower bound**.
2. **Exact MILP** (`distance_milp`, HiGHS via `scipy.optimize.milp`). For each
   dual-logical representative `j`, minimise `sum(x)` s.t. `H_perp x = 0 (mod 2)`
   (integer slacks) and `<dual_j, x> = 1 (mod 2)`; the min over `j` is the exact
   type distance. Solver `status==0` (gap closed) certifies exactness; otherwise
   the incumbent is an **upper bound**.

Cross-checks (pasted run output is in the section "Verification log" below):
- `n=18`: coset-enum == low-weight == MILP (all exact) on 15/15 nontrivial codes.
- low-weight scalar == low-weight vectorised: 15/15 at `n=18` (`w<=8`), agree at
  `n=72` (`w<=4`).
- `n=72`: low-weight == MILP (gap 0) on the codes checked.

## Verification log (pasted run output)

### Kernel cross-checks

GF(2) primitives vs an independent bit-vector implementation, and BB/CSS:
```
rank check: trials=200 mismatches= 0
nullspace check: trials=200 problems= 0
shift matrix: permutation, S^n=I, shift-by-a all OK
monomial multiplication respects ring relations OK
all monomials commute OK
CSS commutation H_X H_Z^T=0 for 200 random codes: True
```

Three distance methods agree at n=18 (coset-enum == low-weight == MILP, all
MILP gap=0):
```
=== n=18: coset-enum vs low-weight vs MILP ===
  checked=15 all-three-agree=15
```

Scalar low-weight reference == vectorised low-weight enumeration:
```
=== equivalence: scalar distance_lowweight vs distance_lowweight_vec ===
  n=18 wmax=8: checked=15 mismatches=0
  n=72 wmax=4 equivalence checked
```

At n=72, exact low-weight enumeration == exact MILP (gap=0):
```
=== n=72 fast: only codes with low-weight d<=7, compare to MILP ===
  k=4 low(exact)=4 milp=4 exact=True agree=True
  k=8 low(exact)=4 milp=4 exact=True agree=True
```

MILP exactness at n=72 (incumbent-sharing + enum-derived lower-bound cut),
certified gap=0:
```
=== n=72 (incumbent-sharing+floor) ===
  k=4 d=8 exact=True (7.4s)
  k=4 d=6 exact=True (15.9s)
  k=8 d=6 exact=True (2.6s)
```

One n=144 code independently re-certified exact (both X and Z types, gap=0):
```
re-certifying [[144,8,6]] A=[[0,0],[1,0],[5,4]] B=[[5,2],[6,4],[10,4]]
css ok: True k= 8
MILP d=6 certified_exact=True (11.8s)
per-type: (6, True) (6, True)
```

### Test suite (pytest)

```
$ PYTHONPATH=src python3 -m pytest tests/ -q
.............                                                            [100%]
13 passed in 70.23s (0:01:10)
```

The 13 tests cover: GF(2) rank/nullspace/row-space vs independent implementations;
shift-matrix period and monomial ring multiplication; CSS commutation; the k
formula and logical-rep counts; agreement of all three distance methods at n=18;
scalar-vs-vectorised low-weight equivalence; MILP weight-floor soundness; MILP ==
enumeration at n=72; and the search returning nontrivial codes plus the A=B trap
having d=2.

### Honest limitation on n=144

At n=144 the MILP does **not** close the optimality gap within a practical time
budget; those distances are reported as **upper bounds** (tag `milp-upper`),
paired with a **proven lower bound** from exhaustive enumeration (`enum-LB>W`
means an exhaustive scan found no logical of weight <= W, so d > W). n=72 and
n=108 distances are MILP-certified exact (gap=0) unless explicitly tagged
`milp-upper`.

## Best codes found

All polynomials are lists of monomial exponent pairs `(a, b)` meaning `x^a y^b`.
FOM = k d^2 / n.

### Best CERTIFIED codes (distance proven exact, MILP gap = 0)

The highest-FOM codes are at the (l,m) = (6,6), n = 72 lattice. Distinct
[[72,8,6]] codes (FOM = 4.000) recur across the search; three representatives,
each re-certified by MILP with gap = 0 (and a proven lower bound d > 4 from
exhaustive enumeration):

```
[[72,8,6]] FOM=4.000  MILP exact(gap=0) d=6; enum certifies d>4; 2.2s
    A=[(2, 2), (3, 4), (4, 3)]  B=[(0, 0), (2, 1), (5, 2)]
[[72,8,6]] FOM=4.000  MILP exact(gap=0) d=6; enum certifies d>4; 3.2s
    A=[(1, 1), (4, 5), (5, 4)]  B=[(1, 3), (2, 3), (4, 4)]
[[72,8,6]] FOM=4.000  MILP exact(gap=0) d=6; enum certifies d>4; 2.6s
    A=[(2, 4), (3, 1), (5, 0)]  B=[(2, 5), (3, 3), (5, 0)]
```

A second strong certified family is [[72,4,8]] (FOM = 3.556): a higher distance
(d = 8) at lower k = 4. Two representatives (MILP gap = 0, enum proves d > 4):

```
[[72,4,8]] FOM=3.556  MILP exact(gap=0) d=8; enum certifies d>4; 10.3s
    A=[(2, 3), (3, 2), (5, 4)]  B=[(1, 3), (2, 1), (2, 5)]
[[72,4,8]] FOM=3.556  MILP exact(gap=0) d=8; enum certifies d>4; 9.0s
    A=[(2, 2), (3, 1), (4, 1)]  B=[(0, 1), (1, 2), (5, 2)]
```

A k=12 code at the same lattice does better than all of these and is the best
n=72 code found: **[[72,12,6]] FOM = 6.000**, distance proven EXACT three
independent ways (this code lives in `results/_search3_66.json`; it had not been
promoted into this table by the earlier pass):

```
[[72,12,6]] FOM=6.000  A=[(1, 2), (2, 2), (3, 5)]  B=[(0, 0), (0, 5), (3, 1)]
  (1) exhaustive low-weight enumeration: NO logical of weight <= 5  =>  d > 5
  (2) MILP minimisation closed the gap: d = 6 (gap=0, both X and Z types)
  (3) capped-MILP infeasibility certifies d >= 6, and an explicit weight-6
      witness (both types) proves d <= 6     =>  d = 6 EXACT
```

| [[n,k,d]] | FOM | lattice (l,m) | distance verification |
|---|---|---|---|
| [[72,12,6]] | 6.000 | (6,6) | EXACT: enum d>5 + MILP gap=0 + infeas d>=6 + weight-6 witness |
| [[72,8,6]] | 4.000 | (6,6) | MILP gap=0 (exact); enum proves d>4 |
| [[72,4,8]] | 3.556 | (6,6) | MILP gap=0 (exact); enum proves d>4 |
| [[72,8,4]] | 1.778 | (6,6) | exhaustive enumeration (d=4, exact) |
| [[72,4,4]] | 0.889 | (6,6) | exhaustive enumeration (d=4, exact) |

**Highest FOM achieved at n=72 (certified exact): 6.000, the [[72,12,6]] code.**

### n = 144 (12,6) and (6,12): the high-distance push, done RIGOROUSLY

The earlier pass reported large n=144 FOM values (5.4–9.0) tagged `milp-upper`.
**Those came from LOOSE MILP incumbents and are NOT credible** — when HiGHS
cannot find a light logical inside the budget, the open-minimisation incumbent it
returns can sit far above the true distance. They are discarded as distance
estimates. This pass replaced them with a rigorous instrument.

**Method (honest by construction).** The randomized upper bound
(`distance_ub_random`) is useless for *ranking* at n=144: on random codes it
returns 46–48 (it simply fails to sample a light logical), which says nothing
about the true distance. The reliable tool is the **capped-MILP feasibility
query** (`exp_certlb._type_geq_T`): for a target `T` it either

- returns an explicit logical of weight `<= T-1` (a PROVEN upper bound: the true
  `d < T`), or
- proves every dual sub-problem infeasible at the cap `sum(x) <= T-1` (a PROVEN
  lower bound: `d >= T`).

HiGHS resolves these tight feasibility instances far faster than the open
minimisation, and the answer is rigorous either way. We climb a ladder of `T` to
BRACKET each code's distance: `cert_lb <= d <= witness_weight`
(`exp_n144.bracket_distance`).

**Result — a genuine, EXACT high-distance n=144 code:**

```
[[144,12,8]]  FOM = 5.333   lattice (l,m)=(6,12)   d = 8 EXACT
    A=[(0, 0), (1, 3), (2, 3)]   B=[(0, 0), (1, 4), (2, 11)]
  d >= 8 : every weight-<=7 sub-problem (all 12 dual reps x BOTH X and Z types)
           is MILP-INFEASIBLE  (98.7 s)
  d <= 8 : explicit weight-8 logical witnesses found for BOTH types  (1.8 s)
  => d = 8 exactly.  CSS commutation and k=12 = 144 - 66 - 66 re-verified.
```

This is the highest EXACT distance reached at n=144 in the whole search, and it
beats the only previously-exact n=144 code (`[[144,8,6]]`, FOM 2.000) on every
axis (higher k AND higher d AND FOM 5.333 vs 2.000).

**Distance distribution at n=144 (k=12 survivors, diagonal family).** Across the
screened k=12 codes the certified/bracketed distances cluster tightly:

```
 d = 4   (several)         FOM_lb = 1.333
 d = 6   (several)         FOM_lb = 3.000
 d >= 7  (a few; upper bound not resolved inside the 200 s search budget)
 d = 8   (>=1, EXACT)      FOM    = 5.333
```

Two additional k=12 codes were pushed by a dedicated certifier to a PROVEN
`d >= 8`, but no weight-<=8 witness was found inside the (generous) budget, so
their upper bound is OPEN — honest status `d >= 8` (could be 8 or larger):

```
[[144,12, d>=8]]  lattice (12,6)   A=[(0,0),(4,3),(11,3)]   B=[(0,0),(5,5),(10,1)]
  d >= 8 PROVEN (every weight-<=7 sub-problem, both X and Z, MILP-infeasible; 105 s)
  no weight-<=8 witness in 254 s  =>  d in [8, ?]   (NOT pinned)
[[144,12, d>=8]]  lattice (6,12)   A=[(0,0),(1,8),(2,1)]   B=[(0,0),(3,10),(3,11)]
  d >= 8 PROVEN (114 s);  no weight-<=8 witness in 245 s  =>  d in [8, ?]
```

We then probed these two at T=9 (prove `d>=9`, or witness a logical of weight
`<=8`).  BOTH are PROVEN `d >= 9`:

```
[[144,12, d>=9]]  lattice (12,6)  A=[(0,0),(4,3),(11,3)]  B=[(0,0),(5,5),(10,1)]
  d >= 9 PROVEN: every weight-<=8 sub-problem (all dual reps, BOTH types)
  MILP-INFEASIBLE  (270 s).   Upper bound still open.   =>  d in [9, ?].
[[144,12, d>=9]]  lattice (6,12)  A=[(0,0),(1,8),(2,1)]  B=[(0,0),(3,10),(3,11)]
  d >= 9 PROVEN  (260 s).   Upper bound still open.   =>  d in [9, ?].
```

Method cross-check: the SAME T=9 probe applied to the EXACT [[144,12,8]] code
immediately returned a weight-8 witness (`d <= 8`, 2 s) — exactly the right
answer — confirming the certifier is sound and that the two `d >= 9` results
above are genuine, not artefacts.

So the high end at n=144 is two codes with PROVEN `d >= 9` (a strictly stronger
lower bound than the EXACT d=8 code; their exact values are not pinned).  These
two were then probed at T=10 (`results/_probe_d10.json`): within the bounded
budget the T=10 infeasibility proof did NOT complete and no weight-9 witness was
returned, so `d >= 10` was neither proven nor refuted — the honest standing
result is **`d >= 9`** for both.  In no case was a code driven to a PROVEN
`d >= 10`, and certainly none to `d >= 12`.  The best fully-EXACT code remains
[[144,12,8]] (d=8 with explicit weight-8 witnesses).

**The ceiling.** The maximum fully-PINNED (exact) distance at n=144 is **d = 8**
(the [[144,12,8]], with explicit weight-8 witnesses). Two further codes are
PROVEN `d >= 9` (lower bound; exact value not pinned). Whether any of these
reaches `d >= 10` was probed directly (see the T=10 result below). Nothing in the
search (diagonal or free-family) was driven to a proven `d >= 12`.

Aggregate over all n=144 evaluations (76 unique codes,
`results/_n144_merged.json`), as a PROVEN lower bound `cert_lb`:

```
 cert_lb = 4 : 22 codes      cert_lb = 6 : 30 codes
 cert_lb = 7 : 22 codes      cert_lb = 8 :  2 codes (one EXACT [[144,12,8]];
                                            one further pushed to PROVEN d>=9)
```

### n = 288 (12,12): attempted, does NOT scale within budget

The (12,12) lattice (n=288) was attempted with a modest budget. Honest outcome:
the search instrument does not scale here. Stage-A screening alone costs ~0.3 s
per code (the `w<=2` enumeration is C(288,2) supports times an n=288 matrix
product), so a few-thousand-sample screen is ~10 min, and the per-code MILP at
n=288 (constraints on 144x288 matrices) rarely resolves a useful target inside
any reasonable per-code cap. **No certified n=288 distance was obtained.** This
is reported as a plain negative: with this kernel and budget, n=288 is out of
reach for rigorous distance certification; the credible certified results stop at
n=144.

## Summary

- **Best n=72 code (CERTIFIED exact): [[72,12,6]], FOM = 6.000** — verified three
  independent ways (enum d>5, MILP gap=0, capped-MILP infeasibility + weight-6
  witness). This supersedes the earlier headline [[72,8,6]] (FOM 4.000).
- **Best n=144 code (CERTIFIED exact): [[144,12,8]], FOM = 5.333** — d=8 proven
  EXACT (weight-<=7 infeasible both types + explicit weight-8 witnesses both
  types). TWO further n=144 codes are PROVEN `d >= 9` (lower bound; exact value
  not pinned within budget).
- **n=288 (12,12):** attempted with a modest budget; see the section below for
  the honest outcome.
- Other certified codes (n=72): [[72,8,6]] (FOM 4.000), [[72,4,8]] (3.556),
  [[72,8,4]] (1.778), [[72,4,4]] (0.889), all gap=0 / enumeration-exact.
- The A=B degenerate family gives d=2 (verified) — the high-k trap; the search
  excludes it via the k cap and the d=2 screen.

### Structural note (corrects the earlier hypothesis)

The earlier pass hypothesised that strictly "all-three-diagonal" trinomials reach
the highest distance. The actual best n=72 code, [[72,12,6]], does NOT fit that:
its A is all-diagonal but its B = constant `1` + an axis-aligned term `y^5` + one
diagonal term `x^3 y`. The high-distance codes live in the BROADER family
(constant + two off-axis monomials per polynomial, "diag" here, which includes
the constant) — not the strictly off-axis-everywhere family. Both the diagonal
and the fully-free families were searched at n=144; the diagonal family is where
the d=8 codes were found.

### HONEST VERDICT: does blind structural search reach d>=10 / d>=12 at n=144?

**No.** Within the (substantial) search and certification budget here, blind
structural reasoning at n=144 reaches a maximum FULLY-PINNED distance of **d = 8**
(the EXACT [[144,12,8]]), and a maximum PROVEN LOWER BOUND of **d >= 9** (two
codes whose exact value was not pinned). The certified/bracketed distances of the
k=12 survivors cluster at 4, 6, 7, 8, 9 with a clear ceiling around 8-9. **No
code was driven to a proven d >= 10 within budget, and none reached d >= 12.**
This is a clear negative on the high-distance (d>=10-12) regime at this code size
with this construction and budget, and it is reported as such. The positive
companion
result is real and rigorous: d = 8 at n=144 with k = 12 (FOM 5.333) is
certified EXACT, a genuine improvement over the earlier only-exact n=144 result
([[144,8,6]], FOM 2.000). Reaching d>=10–12 at n=144, if possible at all for this
family, was not achieved blind here.

Every code above was discovered cold: no reference paper, catalog, or recalled
known BB code was used. The reference PDFs in the repo were never opened.
