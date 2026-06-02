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

| [[n,k,d]] | FOM | lattice (l,m) | distance verification |
|---|---|---|---|
| [[72,8,6]] | 4.000 | (6,6) | MILP gap=0 (exact); enum proves d>4 |
| [[72,4,8]] | 3.556 | (6,6) | MILP gap=0 (exact); enum proves d>4 |
| [[72,8,4]] | 1.778 | (6,6) | exhaustive enumeration (d=4, exact) |
| [[72,4,4]] | 0.889 | (6,6) | exhaustive enumeration (d=4, exact) |

**Highest FOM achieved (certified): 4.000, the [[72,8,6]] code.**

### Larger lattices — explored; distances mostly UPPER BOUNDS (flagged)

All four requested lattices were searched: (6,6) n=72, (9,6) n=108, (12,6) and
(6,12) both n=144. At n = 108 and n = 144 the MILP usually does NOT close the
optimality gap within the per-code time budget. Two regimes:

- **One n=144 code was certified exact:** `[[144,8,6]] FOM=2.000` (MILP gap=0,
  enum proves d>3). This is a genuine exact larger-lattice result.
- **All other n=108 / n=144 distances are UPPER BOUNDS** (`milp-upper`), each
  paired with a proven lower bound `d>3` (n=144) or `d>4` (n=108) from
  exhaustive enumeration.

```
[[108,4,8]]  FOM=2.370  milp-upper(enum-LB>4)   # d<=8 (UB), d>4 (proven)
[[144,8,6]]  FOM=2.000  milp-exact(enum-LB>3)   # EXACT, gap=0
[[144,8,8]]  FOM=3.556  milp-upper(enum-LB>3)   # d<=8 (UB), d>3 (proven)
[[144,8,10]] FOM=5.556  milp-upper(enum-LB>3)   # d<=10 (UB, likely loose)
[[144,4,14]] FOM=5.444  milp-upper(enum-LB>3)   # d<=14 (UB, almost certainly loose)
[[144,4,16]] FOM=7.111  milp-upper(enum-LB>3)   # d<=16 (UB, loose incumbent)
[[144,4,18]] FOM=9.000  milp-upper(enum-LB>3)   # d<=18 (UB, loose incumbent)
```

**Caveat (stated plainly):** the large nominal FOM values for n=144 (5.4–9.0)
come from *loose* MILP incumbents — when HiGHS cannot find a low-weight logical
within the budget, the incumbent it returns can be far above the true distance.
These are NOT credible distance estimates and are NOT claimed as the best codes.
They are recorded only as honest upper bounds. The only quantities I stand
behind as exact are the gap=0 results.

## Summary

- **Highest FOM achieved that is CERTIFIED exact: 4.000 — the [[72,8,6]] code**
  (l,m)=(6,6). Multiple inequivalent polynomial pairs realise it.
- Other certified codes: [[72,4,8]] (FOM 3.556), [[144,8,6]] (FOM 2.000),
  [[72,8,4]] (1.778), [[72,4,4]] (0.889), all gap=0 or exhaustive-enumeration
  exact.
- Merged archive: 23 unique codes across the four lattices
  (`results/_archive.json`).
- The A=B degenerate family gives d=2 (verified) — the high-k trap; the search
  excludes it via the k cap and the d=2 screen.

Every code above was discovered cold: no reference paper, catalog, or recalled
known BB code was used. The reference PDFs in the repo were never opened.
