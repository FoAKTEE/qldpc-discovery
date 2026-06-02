# Validation report (CSS) — blind discoveries vs arXiv:2606.02418 (post-hoc)

Reference codes: 227 (css catalog + landmarks). The catalog is a HELD-OUT TEST SET — never consulted during the blind search.

Blind seed: 7  ·  k-screened: 1500  ·  distance-evals: 28

| blind discovery | FOM | exact | verdict | matched paper code |
|---|---|---|---|---|
| [[72,12,6]] | 6.0 | False | UB_CONSISTENT | [[72,12,6]] landmark:bravyi2024high(MILP-validation) |
| [[36,4,6]] | 4.0 | True | NOVEL_AT_N | — |
| [[72,8,6]] | 4.0 | True | PARAMS_NOT_IN_REF_AT_N | — |
| [[36,8,4]] | 3.556 | True | NOVEL_AT_N | — |
| [[36,8,4]] | 3.556 | True | NOVEL_AT_N | — |
| [[72,4,8]] | 3.556 | False | PARAMS_NOT_IN_REF_AT_N | — |
| [[72,16,4]] | 3.556 | False | PARAMS_NOT_IN_REF_AT_N | — |
| [[36,4,4]] | 1.778 | True | NOVEL_AT_N | — |
| [[36,12,2]] | 1.333 | False | NOVEL_AT_N | — |
| [[72,24,2]] | 1.333 | False | PARAMS_NOT_IN_REF_AT_N | — |

## Summary

- **NOVEL_AT_N**: 5
- **PARAMS_NOT_IN_REF_AT_N**: 4
- **UB_CONSISTENT**: 1

Verdict key: MATCH = same (n,k,d) exact vs an exact reference; POLY_MATCH = identical (A,B) polynomial sets; UB_CONSISTENT = same (n,k), our d (upper bound) consistent with the reference d; NOVEL_AT_N = no reference code at this block length (the CSS catalog starts at n=144).
